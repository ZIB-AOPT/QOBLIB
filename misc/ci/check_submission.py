#!/usr/bin/env python3
# This file is part of QOBLIB - Quantum Optimization Benchmarking Library
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python3
"""
validate_submission.py

Validate a benchmarking-library submission layout and contents.

Instance directories are discovered recursively: an instance directory is any
directory containing a "<instance>_summary.csv" file. It may sit directly under
the submission root or be nested inside arbitrary grouping subfolders, e.g.
  SUBMISSION_ROOT/<group>/<instance>/<instance>_summary.csv
Both flat and nested layouts are accepted.

Checks for each instance directory:
  - Required files:
      <instance>_summary.csv
      <instance>_solution.<ext>
        OR a "solutions/" directory with files named <instance>_solution_<N>.<ext> (N=1.., consecutive)
    Optional files:
      <instance>_objective_time_series.json
      README.md  (can be auto-generated to pretty-print the CSV)

  - CSV header exactly matches the required columns (order-sensitive).
  - CSV must have at least one data row. By default, we verify `Problem` == <instance>.
  - Basic type checks for some numeric/count columns.
  - Objective time series JSON structure: list of runs; each run is a list of objects with keys Time and Incumbent.
  - Automatically runs the per-problem solution checker (if available) for each solution.
    Pass --no-check to disable this.
  - (Optional) run a solution checker for each solution via a user-provided command template.

Usage:
  python validate_submission.py SUBMISSION_ROOT
    [--all]                              # validate every submission under a repo / problem-class / submissions dir
    [--no-check]                         # disable automatic per-problem solution checker
    [--instance-pattern 'glob*']         # only check matching instance dir names
    [--generate-readme]                  # (re)create README.md from CSV pretty table
    [--strict-problem-match]             # require CSV Problem column == instance dir name
    [--verbose]
    [--quiet]

Exit code is nonzero if any instance fails validation.

Automatic per-problem checkers (built via `cargo build --release` in <problem>/check/):
  01-marketsplit : check_marketsplit  <instance>.dat <solution>
  02-labs        : check_labs         <N> <solution>
  03-birkhoff    : check_birkhoff     <instance>.json <solution>
  04-steiner     : check_steiner      --arcs arcs.dat --terms terms.dat --sol <solution>
  07-independent : check_stableset    <instance>.gph <solution>
  08-network     : check_network      <size> demand.txt <solution>
  09-routing     : check_cvrp         <instance>.vrp <solution>
  10-topology    : check_topology     <nodes> <degree> <diameter> <solution>
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Iterable
import subprocess
import fnmatch
import gzip
import os

REQUIRED_COLUMNS: List[str] = [
    "Problem","Submitter","Affiliation","Date","Reference","Best Objective Value","Optimality Bound","Modeling Approach",
    "# Decision Variables","# Binary Variables","# Integer Variables","# Continuous Variables",
    "# Non-Zero Coefficients","Coefficients Type","Coefficients Range","Workflow","Algorithm Type","Paradigm",
    "# Runs","# Feasible Runs","# Successful Runs","Success Threshold","Hardware Specifications",
    "Total Runtime","Time to Solution","CPU Runtime","GPU Runtime","QPU Runtime","Other HW Runtime","Remarks"
]

# Columns we try to parse as ints/floats (best-effort; empty allowed)
INT_COLUMNS = {
    "# Decision Variables","# Binary Variables","# Integer Variables","# Continuous Variables",
    "# Non-Zero Coefficients","# Runs","# Feasible Runs","# Successful Runs"
}
FLOAT_COLUMNS = {
    "Best Objective Value","Optimality Bound","Success Threshold",
    "Total Runtime","Time to Solution","CPU Runtime","GPU Runtime","QPU Runtime","Other HW Runtime"
}

# ---------------------------------------------------------------------------
# Per-problem checker exit-code contract (see misc/CHECKER_CONTRACT.md).
# The checker reports a *fact* about the solution file; this script applies the
# *policy* (what a submission is allowed to declare) on top of it.
# ---------------------------------------------------------------------------
EXIT_VALID        = 0    # valid file, feasible (and optimal where determinable)
EXIT_INVALID_FILE = 10   # solution file is malformed / unparseable / wrong shape
EXIT_SUBOPTIMAL   = 20   # valid, feasible file, but not optimal
EXIT_INFEASIBLE   = 21   # valid file, but the solution violates a constraint
EXIT_USAGE        = 2    # bad arguments / unreadable instance file (infra error)

EXIT_CODE_LABELS = {
    EXIT_VALID:        "VALID",
    EXIT_INVALID_FILE: "INVALID_FILE",
    EXIT_SUBOPTIMAL:   "SUBOPTIMAL",
    EXIT_INFEASIBLE:   "INFEASIBLE",
    EXIT_USAGE:        "USAGE",
}

OBJECTIVE_TS_BASENAME = "_objective_time_series.json"
SUMMARY_CSV_SUFFIX   = "_summary.csv"
SOLUTION_SINGLE_RE   = r"^{inst}_solution\.(?P<ext>[^./\\]+)$"
SOLUTION_DIR_NAME    = "solutions"
SOLUTION_MULTI_RE    = r"^{inst}_solution_(?P<idx>[0-9]+)\.(?P<ext>[^./\\]+)$"  # 0..N consecutive


@dataclass
class CheckerResult:
    solution_path: Path
    returncode: int
    stdout: str
    stderr: str


@dataclass
class InstanceReport:
    instance: str
    path: Path
    ok: bool = True
    messages: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    csv_rows: int = 0
    solutions: List[Path] = field(default_factory=list)
    checker_results: List[CheckerResult] = field(default_factory=list)

    def fail(self, msg: str) -> None:
        self.ok = False
        self.messages.append(f"ERROR: {msg}")

    def warn(self, msg: str) -> None:
        self.warnings.append(f"WARNING: {msg}")

    def info(self, msg: str) -> None:
        self.messages.append(f"INFO: {msg}")


def find_instance_dirs(root: Path, pattern: Optional[str]) -> List[Path]:
    """Locate the instance directories under a submission ``root``.

    An instance directory is any directory that contains a ``*_summary.csv``
    file. Such directories may sit directly under the submission root or be
    nested inside arbitrary grouping subfolders, e.g.
    ``<root>/<group>/<instance>/<instance>_summary.csv`` — both layouts are
    accepted. Directories named ``misc`` (at any depth) are skipped, and
    ``pattern`` filters on the instance directory name.
    """
    instance_dirs: List[Path] = []
    seen: set = set()
    for summary in sorted(root.rglob("*" + SUMMARY_CSV_SUFFIX)):
        if not summary.is_file():
            continue
        inst_dir = summary.parent
        # The root itself is never an instance directory; instances live in a
        # (possibly nested) subdirectory below it.
        if inst_dir == root or inst_dir in seen:
            continue
        rel_parts = [part.lower() for part in inst_dir.relative_to(root).parts]
        if "misc" in rel_parts:
            continue
        seen.add(inst_dir)
        instance_dirs.append(inst_dir)

    if pattern:
        instance_dirs = [p for p in instance_dirs if fnmatch.fnmatch(p.name, pattern)]
    return sorted(instance_dirs, key=lambda p: p.relative_to(root).as_posix().lower())


def validate_csv(instance: str, csv_path: Path, strict_problem_match: bool, report: InstanceReport) -> List[Dict[str, str]]:
    if not csv_path.exists():
        report.fail(f"Missing summary CSV: {csv_path.name}")
        return []

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        if header != REQUIRED_COLUMNS:
            report.fail(
                "CSV header mismatch.\n"
                f"  Expected ({len(REQUIRED_COLUMNS)}): {REQUIRED_COLUMNS}\n"
                f"  Found    ({len(header)}): {header}"
            )
            rows = list(reader)
            return rows

        rows: List[Dict[str,str]] = list(reader)
        if not rows:
            report.fail("CSV must contain at least one data row.")
            return rows

    report.csv_rows = len(rows)

    for i, row in enumerate(rows, start=1):
        if strict_problem_match:
            prob = row.get("Problem","").strip()
            if prob != instance:
                report.fail(f"Row {i}: 'Problem' column must equal instance name '{instance}', found '{prob}'.")

        # ---- FIX: allow "N/A" (case insensitive) ----
        def is_na(v: str) -> bool:
            return v.strip().upper() in {"N/A", "NA"}

        for col in INT_COLUMNS:
            val = (row.get(col) or "").strip()
            if val == "" or is_na(val):
                continue
            try:
                int(val.replace(",", ""))
            except Exception:
                report.fail(f"Row {i}: Column '{col}' should be an integer or 'N/A', found '{val}'.")

        for col in FLOAT_COLUMNS:
            val = (row.get(col) or "").strip()
            if val == "" or is_na(val):
                continue
            try:
                float(val.replace(",", ""))
            except Exception:
                report.fail(f"Row {i}: Column '{col}' should be a number or 'N/A', found '{val}'.")

        # Multiple authors must be given as a comma-separated list (wrapped in
        # double quotes in the raw CSV so it parses as a single field), and the
        # affiliations must be a comma-separated list in the same order, with
        # one entry per author (repeat shared affiliations).
        submitters = [s.strip() for s in (row.get("Submitter") or "").split(",") if s.strip()]
        affiliations = [a.strip() for a in (row.get("Affiliation") or "").split(",") if a.strip()]
        if len(submitters) > 1 and len(affiliations) != len(submitters):
            report.warn(
                f"Row {i}: {len(submitters)} author(s) in 'Submitter' but {len(affiliations)} "
                f"entry/entries in 'Affiliation'. Provide a comma-separated affiliation per author "
                f"in the same order (repeat shared affiliations)."
            )

    return rows



def collect_solutions(instance: str, inst_dir: Path, report: InstanceReport) -> List[Path]:
    # Pattern 1: single solution file
    single_pat = re.compile(SOLUTION_SINGLE_RE.format(inst=re.escape(instance)))
    singles = [p for p in inst_dir.iterdir() if p.is_file() and single_pat.match(p.name)]

    # Pattern 2: solutions directory with numbered files
    sol_dir = inst_dir / SOLUTION_DIR_NAME
    multi_pat = re.compile(SOLUTION_MULTI_RE.format(inst=re.escape(instance)))
    multis: List[Path] = []
    if sol_dir.is_dir():
        for p in sol_dir.iterdir():
            if p.is_file() and multi_pat.match(p.name):
                multis.append(p)
        multis.sort(key=lambda p: int(multi_pat.match(p.name).group("idx")))  # type: ignore

    if singles and sol_dir.exists():
        report.fail("Found both a single solution file AND a 'solutions/' directory. Choose one approach.")
        return []

    if not singles and not multis:
        report.fail(
            f"Missing solution: either a single '{instance}_solution.<ext>' file "
            f"or a '{SOLUTION_DIR_NAME}/' directory with '{instance}_solution_<N>.<ext>' files."
        )
        return []

    if singles:
        report.info(f"Found single solution file: {singles[0].name}")
        return singles

    # Validate consecutive numbering for multis
    idxs = []
    for p in multis:
        m = multi_pat.match(p.name)
        assert m is not None
        idxs.append(int(m.group("idx")))
    if idxs:
        expected = list(range(0, len(idxs)))
        if idxs != expected:
            report.fail(f"'solutions/' files must be consecutively numbered from 0: found indices {idxs}, expected {expected}.")
    report.info(f"Found {len(multis)} solutions in '{SOLUTION_DIR_NAME}/'.")
    return multis


def validate_objective_time_series(instance: str, inst_dir: Path, report: InstanceReport) -> None:
    # Accept either plain JSON or gzipped JSON
    ts_name_json = f"{instance}{OBJECTIVE_TS_BASENAME}"              # e.g. foo_objective_time_series.json
    ts_name_gz   = f"{instance}{OBJECTIVE_TS_BASENAME}.gz"           # e.g. foo_objective_time_series.json.gz
    ts_path = None
    if (inst_dir / ts_name_json).exists():
        ts_path = inst_dir / ts_name_json
    elif (inst_dir / ts_name_gz).exists():
        ts_path = inst_dir / ts_name_gz

    if not ts_path:
        report.info("Objective time series file not provided (optional).")
        return

    try:
        if ts_path.suffix == ".gz":
            opener = gzip.open
        else:
            opener = open

        with opener(ts_path, "rt", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            report.fail(f"{ts_path.name}: must be a list of runs.")
            return

        for r_i, run in enumerate(data, start=1):
            if not isinstance(run, list):
                report.fail(f"{ts_path.name}: run {r_i} must be a list.")
                continue
            for e_i, entry in enumerate(run, start=1):
                if not isinstance(entry, dict):
                    report.fail(f"{ts_path.name}: run {r_i} entry {e_i} must be an object.")
                    continue
                if "Time" not in entry or "Incumbent" not in entry:
                    report.fail(f"{ts_path.name}: run {r_i} entry {e_i} must contain 'Time' and 'Incumbent' keys.")

    except (json.JSONDecodeError, OSError) as e:
        report.fail(f"{ts_path.name}: invalid JSON: {e}")


def generate_readme_from_csv(instance: str, inst_dir: Path, rows: List[Dict[str,str]], report: InstanceReport) -> None:
    """Create/overwrite README.md with a transposed Markdown table from the CSV.

    The table layout will be:
        | Field | Row 1 | Row 2 | ... |
    where each CSV column becomes a table row and each CSV row becomes a column.
    Inserts empty table rows between selected field pairs for visual grouping.
    """
    readme_path = inst_dir / "README.md"

    if not rows:
        raise ValueError("No CSV rows provided to generate README.")
    # Preserve column order as found in the first row; if other rows introduce new keys, append them in first-seen order
    seen: List[str] = []
    for r in rows:
        for k in r.keys():
            if k not in seen:
                seen.append(k)
    header_fields = seen

    # Fields after which we insert an empty row (to create spacing)
    insert_after = {
        "Date",                    # between Date and Reference
        "Optimality Bound",        # between Optimality Bound and Modeling Approach
        "Coefficients Range",      # between Coefficients Range and Workflow
        "Success Threshold",       # between Success Threshold and Hardware Specifications
        "Hardware Specifications", # between Hardware Specifications and Total Runtime
        "Other HW Runtime",        # between Other HW Runtime and Remarks
    }

    # Build a new list of fields including blank sentinel rows where requested
    BLANK_SENTINEL = "__README_BLANK_ROW__"
    fields_with_blanks: List[str] = []
    for f in header_fields:
        fields_with_blanks.append(f)
        if f in insert_after:
            fields_with_blanks.append(BLANK_SENTINEL)

    # Header: "Field" plus one column per CSV row
    header_cells = ["Field"] + [f"Value {i}" for i in range(1, len(rows) + 1)]
    header = "| " + " | ".join(header_cells) + " |\n"
    sep = "| " + " | ".join("---" for _ in header_cells) + " |\n"

    # Build body: one Markdown table row per CSV column (and blank rows)
    body_lines: List[str] = []
    for col in fields_with_blanks:
        if col == BLANK_SENTINEL:
            # produce an entirely empty row (first "Field" cell empty)
            empty_cells = ["======"] + [""] * len(rows)
            body_lines.append("| " + " | ".join(empty_cells) + " |")
            continue

        cells = [col]
        for row in rows:
            val = row.get(col, "")
            v = "" if val is None else str(val)
            # Replace newlines with <br> to keep table formatting, escape vertical bars
            v = v.replace("\n", "<br>").replace("|", r"\|")
            cells.append(v)
        body_lines.append("| " + " | ".join(cells) + " |")

    md = (
        f"# Submission for {instance}\n\n"
        f"This directory contains the submission for the problem **{instance}**.\n\n"
        + header + sep + "\n".join(body_lines) + "\n"
    )
    readme_path.write_text(md, encoding="utf-8")
    report.info(f"README.md generated from CSV ({readme_path.name}).")


# ---------------------------------------------------------------------------
# Declared-claim helpers (policy inputs read from the summary CSV)
# ---------------------------------------------------------------------------

def _parse_count(value: Optional[str]) -> Optional[int]:
    """Parse a count column to an int, or None when blank / 'N/A'."""
    if value is None:
        return None
    v = value.strip().replace(",", "")
    if v == "" or v.upper() in {"N/A", "NA"}:
        return None
    try:
        return int(float(v))
    except ValueError:
        return None


def _parse_number(value: Optional[str]) -> Optional[float]:
    """Parse a numeric column to a float, or None when blank / 'N/A'."""
    if value is None:
        return None
    v = value.strip().replace(",", "")
    if v == "" or v.upper() in {"N/A", "NA"}:
        return None
    try:
        return float(v)
    except ValueError:
        return None


def feasibility_claimed(rows: List[Dict[str, str]]) -> bool:
    """Does the submission claim at least one feasible solution for this instance?

    Derived from the '# Feasible Runs' column. A blank / 'N/A' value is treated as
    "assumed feasible" (i.e. the claim stands) — feasibility enforcement is only
    waived when the submitter *explicitly* declares 0 feasible runs on every row.
    Mirrors misc/check_bkv_updates.py::_is_feasible_row.
    """
    if not rows:
        return True
    for row in rows:
        n = _parse_count(row.get("# Feasible Runs"))
        if n is None or n > 0:
            return True
    return False


def optimality_claimed(rows: List[Dict[str, str]]) -> bool:
    """Does the submission assert a *proven* optimum for this instance?

    A proven-optimum claim is expressed by the 'Optimality Bound' meeting the
    'Best Objective Value' (the bound certifies the reported objective is optimal).
    Optimality is opt-in: if the bound is blank / 'N/A' the submission makes no
    optimality claim, so a valid but non-optimal solution is accepted.

    Note: '# Successful Runs' is deliberately NOT used here. Per CONTRIBUTING.md it
    counts runs within the success threshold of the *algorithm's own best*, not the
    global optimum, so a good heuristic legitimately has '# Successful Runs' > 0 while
    remaining sub-optimal — using it would reject valid heuristic submissions.
    """
    for row in rows:
        obj = _parse_number(row.get("Best Objective Value"))
        bound = _parse_number(row.get("Optimality Bound"))
        if obj is not None and bound is not None and abs(obj - bound) <= 1e-9 * max(1.0, abs(obj)):
            return True
    return False


# ---------------------------------------------------------------------------
# Auto per-problem checker
# ---------------------------------------------------------------------------

def _detect_problem_and_roots(
    submission_root: Path,
) -> Tuple[Optional[str], Optional[Path], Optional[Path]]:
    """Detect (problem_dir_name, check_dir, qoblib_root) from the submission path.

    Expected layout: <qoblib_root>/<problem_dir>/submissions/<submission_name>/
    Returns (None, None, None) when the layout doesn't match or no check/ dir exists.
    """
    try:
        problem_dir = submission_root.resolve().parent.parent
        qoblib_root = problem_dir.parent
        check_dir = problem_dir / "check"
        if not check_dir.is_dir():
            return None, None, None
        return problem_dir.name, check_dir, qoblib_root
    except Exception:
        return None, None, None


def _ensure_checker_built(check_dir: Path, binary_name: str) -> Optional[Path]:
    """Return the path to the checker binary, building it with cargo if needed."""
    binary_path = check_dir / "target" / "release" / binary_name
    if binary_path.exists():
        return binary_path
    print(f"  Building checker '{binary_name}' in {check_dir} ...", file=sys.stderr)
    try:
        result = subprocess.run(
            ["cargo", "build", "--release"],
            cwd=str(check_dir),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and binary_path.exists():
            return binary_path
        print(
            f"  WARNING: cargo build failed (rc={result.returncode}):\n"
            + textwrap.indent(result.stderr[:600], "    "),
            file=sys.stderr,
        )
    except FileNotFoundError:
        print("  WARNING: 'cargo' not found; cannot build checker.", file=sys.stderr)
    return None


def _read_topology_diameter(solution_path: Path) -> int:
    """Read the diameter from the first 5 comment lines of a topology .gph file."""
    try:
        with solution_path.open(encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh):
                if i >= 5:
                    break
                m = re.search(r"(?i)^c[^\d]*(diameter)[^\d]*(\d+)", line)
                if m:
                    return int(m.group(2))
    except OSError:
        pass
    return 999999


def _build_auto_checker_cmd(
    problem_name: str,
    check_dir: Path,
    qoblib_root: Path,
    instance: str,
    solution: Path,
) -> Optional[List[str]]:
    """Construct a checker command list for the given problem/instance/solution.

    Returns None when no checker applies (unknown problem or build failure).
    """
    prob = problem_dir = problem_name  # alias for readability
    instances_dir = qoblib_root / problem_name / "instances"

    if prob.startswith("01-"):
        binary = _ensure_checker_built(check_dir, "check_marketsplit")
        if not binary:
            return None
        return [str(binary), str(instances_dir / f"{instance}.dat"), str(solution)]

    if prob.startswith("02-"):
        binary = _ensure_checker_built(check_dir, "check_labs")
        if not binary:
            return None
        m = re.search(r"(\d+)", instance)
        num = m.group(1) if m else "0"
        return [str(binary), num, str(solution)]

    if prob.startswith("03-"):
        binary = _ensure_checker_built(check_dir, "check_birkhoff")
        if not binary:
            return None
        # Instance name format: B{n}_{k}_{idx}
        # k == n  → sparse file qbench_{n:02d}_sparse.json
        # k == n² → dense  file qbench_{n:02d}_dense.json
        m = re.match(r"B(\d+)_(\d+)_\d+", instance, re.IGNORECASE)
        if not m:
            return None
        n, k = int(m.group(1)), int(m.group(2))
        density = "dense" if k == n * n else "sparse"
        instance_file = instances_dir / f"qbench_{n:02d}_{density}.json"
        if not instance_file.exists():
            return None
        return [str(binary), str(instance_file), str(solution)]

    if prob.startswith("04-"):
        binary = _ensure_checker_built(check_dir, "check_steiner")
        if not binary:
            return None
        arcs = instances_dir / instance / "arcs.dat"
        terms = instances_dir / instance / "terms.dat"
        return [str(binary), "--arcs", str(arcs), "--terms", str(terms), "--sol", str(solution)]

    if prob.startswith("07-"):
        binary = _ensure_checker_built(check_dir, "check_stableset")
        if not binary:
            return None
        return [str(binary), str(instances_dir / f"{instance}.gph"), str(solution)]

    if prob.startswith("08-"):
        binary = _ensure_checker_built(check_dir, "check_network")
        if not binary:
            return None
        m = re.search(r"network(\d+)", instance, re.IGNORECASE)
        size = str(int(m.group(1))) if m else "0"
        demand_file = instances_dir / "demand.txt"
        return [str(binary), size, str(demand_file), str(solution)]

    if prob.startswith("09-"):
        binary = _ensure_checker_built(check_dir, "check_cvrp")
        if not binary:
            return None
        return [str(binary), str(instances_dir / f"{instance}.vrp"), str(solution)]

    if prob.startswith("10-"):
        binary = _ensure_checker_built(check_dir, "check_topology")
        if not binary:
            return None
        m = re.search(r"topology_(\d+)_(\d+)", instance, re.IGNORECASE)
        if not m:
            return None
        nodes, degree = m.group(1), m.group(2)
        diameter = str(_read_topology_diameter(solution))
        return [str(binary), nodes, degree, diameter, str(solution)]

    return None


def run_auto_checker_on_solutions(
    problem_name: str,
    check_dir: Path,
    qoblib_root: Path,
    instance: str,
    solutions: List[Path],
    report: InstanceReport,
) -> None:
    """Run the auto-detected per-problem checker on each solution."""
    warned = False
    for sol in solutions:
        cmd = _build_auto_checker_cmd(problem_name, check_dir, qoblib_root, instance, sol)
        if cmd is None:
            if not warned:
                report.warn(f"No auto-checker available for problem '{problem_name}'.")
                warned = True
            continue
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )
            checker_result = CheckerResult(
                solution_path=sol,
                returncode=proc.returncode,
                stdout=proc.stdout.strip(),
                stderr=proc.stderr.strip(),
            )
            report.checker_results.append(checker_result)
            if proc.returncode == 0:
                report.info(f"Checker ran successfully for solution {sol.name}.")
        except Exception as e:
            report.fail(f"Auto-checker execution failed for {sol.name}: {e}")


def apply_checker_policy(
    results: List[CheckerResult],
    feas_claimed: bool,
    opt_claimed: bool,
    report: InstanceReport,
) -> None:
    """Turn raw checker exit codes into pass/fail decisions using the declared claims.

    See misc/CHECKER_CONTRACT.md for the full table. In short:
      * A malformed solution file (EXIT_INVALID_FILE) or infra error (EXIT_USAGE, or
        any unexpected non-zero code such as a raw panic) always fails — validity of
        the solution file is non-negotiable.
      * Infeasibility (EXIT_INFEASIBLE) fails only when the submission claims
        feasibility; a submission that declares 0 feasible runs is accepted as long
        as its file is well-formed.
      * Non-optimality (EXIT_SUBOPTIMAL) fails only when the submission claims
        optimality (# Successful Runs > 0).
    The feasibility/optimality checks are aggregated over all solution files of the
    instance: every file must be well-formed, and *at least one* file must satisfy a
    claimed property.
    """
    if not results:
        return

    feasible_files = []   # files that are at least feasible (valid + feasible)
    optimal_files = []     # files that are optimal (valid + feasible + optimal)
    hard_failure = False

    for cr in results:
        rc = cr.returncode
        name = cr.solution_path.name
        if rc == EXIT_VALID:
            feasible_files.append(name)
            optimal_files.append(name)
        elif rc == EXIT_SUBOPTIMAL:
            feasible_files.append(name)  # feasible, just not optimal
        elif rc == EXIT_INFEASIBLE:
            pass  # valid file, but infeasible
        elif rc == EXIT_INVALID_FILE:
            report.fail(f"Solution file '{name}' is invalid (malformed / unparseable) "
                        f"[checker exit {rc}].")
            hard_failure = True
        elif rc == EXIT_USAGE:
            report.fail(f"Checker could not process solution '{name}' "
                        f"(usage / instance error) [checker exit {rc}].")
            hard_failure = True
        else:
            report.fail(f"Checker for solution '{name}' returned unexpected exit code "
                        f"{rc}; treating the file as invalid.")
            hard_failure = True

    if hard_failure:
        return  # a malformed / unprocessable file already failed the instance

    # Feasibility: enforced only when the submission claims it.
    if feas_claimed:
        if not feasible_files:
            report.fail("Submission declares at least one feasible run "
                        "(# Feasible Runs > 0 or blank), but no submitted solution "
                        "file is feasible.")
        elif len(feasible_files) < len(results):
            report.warn(f"{len(results) - len(feasible_files)} of {len(results)} "
                        f"solution file(s) are infeasible, but at least one is "
                        f"feasible as claimed.")
    else:
        if feasible_files:
            report.info("Submission declares 0 feasible runs, yet a submitted "
                        "solution file is feasible — metadata may under-claim.")
        else:
            report.warn("Solution file(s) valid but infeasible; accepted because the "
                        "submission declares 0 feasible runs (# Feasible Runs = 0).")

    # Optimality: enforced only when the submission asserts a proven optimum
    # (Optimality Bound == Best Objective Value).
    if opt_claimed and not optimal_files:
        report.fail("Submission asserts a proven optimum (Optimality Bound equals Best "
                    "Objective Value), but no submitted solution file is optimal.")
    elif not opt_claimed and feasible_files and not optimal_files:
        report.info("Solution file(s) valid and feasible but not optimal; accepted "
                    "because the submission makes no optimality claim.")


def print_report(reports: List[InstanceReport], quiet: bool=False) -> None:
    total = len(reports)
    passed = sum(1 for r in reports if r.ok)
    failed = total - passed

    for r in reports:
        if quiet and r.ok:
            continue
        banner = f"[{r.instance}] {'OK' if r.ok else 'FAILED'}"
        print("=" * len(banner))
        print(banner)
        print("=" * len(banner))
        for msg in r.messages:
            print(msg)
        for w in r.warnings:
            print(w)
        # Surface per-solution checker detail only for failed instances (a passing
        # instance may legitimately contain infeasible/non-optimal files).
        if not r.ok:
            noteworthy = [cr for cr in r.checker_results if cr.returncode != EXIT_VALID]
            if noteworthy:
                print("Checker results:")
                for cr in noteworthy:
                    label = EXIT_CODE_LABELS.get(cr.returncode, f"exit {cr.returncode}")
                    print(f"  - {cr.solution_path.name}: {label} (rc={cr.returncode})")
                    if cr.stdout:
                        print(textwrap.indent(cr.stdout, prefix="      stdout: "))
                    if cr.stderr:
                        print(textwrap.indent(cr.stderr, prefix="      stderr: "))
        print()

    print(f"Summary: {passed}/{total} instances passed, {failed} failed.")
    if failed > 0:
        print("Overall: FAILED")
    else:
        print("Overall: OK")


def validate_instance(
    submission_root: Path,
    inst_dir: Path,
    args: argparse.Namespace,
) -> InstanceReport:
    instance = inst_dir.name
    report = InstanceReport(instance=instance, path=inst_dir)

    # 1) summary CSV
    csv_path = inst_dir / f"{instance}{SUMMARY_CSV_SUFFIX}"
    rows = validate_csv(instance, csv_path, args.strict_problem_match, report)

    # 2) solution(s)
    solutions = collect_solutions(instance, inst_dir, report)
    report.solutions = solutions

    # 3) objective time series (optional)
    validate_objective_time_series(instance, inst_dir, report)

    # 4) README.md (optional or generate)
    readme_path = inst_dir / "README.md"
    if args.generate_readme and rows:
        try:
            generate_readme_from_csv(instance, inst_dir, rows, report)
            report.info("README.md generated successfully.")
        except Exception as e:
            report.fail(f"Failed to generate README.md: {e}")
    else:
        if not readme_path.exists():
            report.info("README.md not present (optional).")

    # 5) Auto per-problem checker (default; disabled by --no-check)
    if not args.no_check and solutions:
        problem_name, check_dir, qoblib_root = _detect_problem_and_roots(submission_root)
        if problem_name and check_dir:
            auto_start = len(report.checker_results)
            run_auto_checker_on_solutions(
                problem_name, check_dir, qoblib_root, instance, solutions, report
            )
            # Interpret the checker exit codes against what the submission declares
            # in its summary CSV (see misc/CHECKER_CONTRACT.md). Solution-file
            # validity is always required; feasibility/optimality are enforced only
            # when the submission claims them.
            apply_checker_policy(
                report.checker_results[auto_start:],
                feas_claimed=feasibility_claimed(rows),
                opt_claimed=optimality_claimed(rows),
                report=report,
            )
        # If layout unrecognised, silently skip (no checker available)

    return report


def validate_one_submission(root: Path, args: argparse.Namespace) -> List[InstanceReport]:
    """Validate a single submission root, returning one report per instance dir."""
    instance_dirs = find_instance_dirs(root, args.instance_pattern)
    reports: List[InstanceReport] = []
    for inst_dir in instance_dirs:
        if args.verbose:
            print(f"Validating instance: {inst_dir.name}")
        reports.append(validate_instance(root, inst_dir, args))
    return reports


def discover_submission_roots(root: Path) -> List[Path]:
    """Find every submission directory reachable from `root`.

    Accepts being pointed at any of:
      - a repository root        -> scans <root>/*/submissions/*
      - a problem-class dir      -> scans <root>/submissions/*
      - a `submissions/` dir     -> scans <root>/*

    Each immediate subdirectory of a `submissions/` folder is treated as one
    submission root. Directories named "misc" are ignored.
    """
    if root.name == "submissions":
        submissions_dirs = [root]
    elif (root / "submissions").is_dir():
        submissions_dirs = [root / "submissions"]
    else:
        submissions_dirs = sorted(root.glob("*/submissions"))

    roots: List[Path] = []
    for submissions_dir in submissions_dirs:
        if not submissions_dir.is_dir():
            continue
        for d in sorted(submissions_dir.iterdir(), key=lambda p: p.name.lower()):
            if d.is_dir() and d.name.lower() != "misc":
                roots.append(d)
    return roots


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate benchmarking-library submission.")
    parser.add_argument("submission_root", type=Path, help="Path to submission root directory.")
    parser.add_argument("--all", action="store_true",
                        help="Treat the path as a repository root and validate every submission found "
                             "under <root>/*/submissions/*. Aggregates results across all submissions.")
    parser.add_argument("--no-check", action="store_true",
                        help="Disable the automatic per-problem solution checker.")
    parser.add_argument("--instance-pattern", type=str, default=None,
                        help="Only validate instance directories whose names match this glob (e.g., 'vrp_*').")
    parser.add_argument("--generate-readme", action="store_true",
                        help="Generate README.md per instance from the CSV (overwrites if exists).")
    parser.add_argument("--strict-problem-match", action="store_true",
                        help="Require 'Problem' column in CSV to equal the instance directory name.")
    parser.add_argument("--verbose", action="store_true", help="Verbose output.")
    parser.add_argument("--quiet", action="store_true", help="Only show failed instances in the summary.")
    args = parser.parse_args()

    root = args.submission_root
    if not root.exists() or not root.is_dir():
        print(f"ERROR: Path does not exist or is not a directory: {root}", file=sys.stderr)
        sys.exit(2)

    if args.all:
        submission_roots = discover_submission_roots(root)
        if not submission_roots:
            print(f"No submissions found under {root}/*/submissions/*.", file=sys.stderr)
            sys.exit(2)

        grand_pass = grand_total = 0
        empty_submissions: List[Path] = []
        failed_submissions: List[Path] = []
        for sroot in submission_roots:
            rel = sroot.relative_to(root)
            banner = f"# SUBMISSION: {rel}"
            print("\n" + "#" * len(banner))
            print(banner)
            print("#" * len(banner))
            reports = validate_one_submission(sroot, args)
            if not reports:
                print("WARNING: no instance subdirectories found in this submission.\n")
                empty_submissions.append(rel)
                continue
            print_report(reports, quiet=args.quiet)
            grand_total += len(reports)
            grand_pass += sum(1 for r in reports if r.ok)
            if not all(r.ok for r in reports):
                failed_submissions.append(rel)

        print("\n" + "=" * 70)
        print(f"GRAND TOTAL: {grand_pass}/{grand_total} instances passed "
              f"across {len(submission_roots)} submissions.")
        if empty_submissions:
            print(f"Submissions with no recognized instance dirs ({len(empty_submissions)}):")
            for rel in empty_submissions:
                print(f"  - {rel}")
        if failed_submissions:
            print(f"Submissions with failing instances ({len(failed_submissions)}):")
            for rel in failed_submissions:
                print(f"  - {rel}")
        ok = not failed_submissions and not empty_submissions
        print("Overall: OK" if ok else "Overall: FAILED")
        sys.exit(0 if ok else 1)

    reports = validate_one_submission(root, args)
    if not reports:
        print("No instance subdirectories found matching criteria.", file=sys.stderr)
        sys.exit(2)

    print_report(reports, quiet=args.quiet)

    # Nonzero exit on any failure
    sys.exit(0 if all(r.ok for r in reports) else 1)


if __name__ == "__main__":
    main()
