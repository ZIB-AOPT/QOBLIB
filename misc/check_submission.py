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
  - (Optional) run a solution checker for each solution via a user-provided command template.

Usage:
  python validate_submission.py SUBMISSION_ROOT
    [--checker-cmd '...{solution}...']   # command template with placeholders
    [--instance-pattern 'glob*']         # only check matching instance dir names
    [--fail-on-checker]                  # mark instance invalid if checker fails/returns nonzero
    [--generate-readme]                  # (re)create README.md from CSV pretty table
    [--strict-problem-match]             # require CSV Problem column == instance dir name
    [--verbose]
    [--quiet]
  Placeholders for --checker-cmd: {submission_root} {instance_dir} {instance} {solution}

Exit code is nonzero if any instance fails validation.
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

REQUIRED_COLUMNS: List[str] = [
    "Problem","Submitter","Date","Reference","Best Objective Value","Optimality Bound","Modeling Approach",
    "# Decision Variables","# Binary Variables","# Integer Variables","# Continuous Variables",
    "# Non-Zero Coefficients","Coefficients Type","Coefficients Range","Workflow","Algorithm Type",
    "# Runs","# Feasible Runs","# Successful Runs","Success Threshold","Hardware Specifications",
    "Total Runtime","CPU Runtime","GPU Runtime","QPU Runtime","Other HW Runtime","Remarks"
]

# Columns we try to parse as ints/floats (best-effort; empty allowed)
INT_COLUMNS = {
    "# Decision Variables","# Binary Variables","# Integer Variables","# Continuous Variables",
    "# Non-Zero Coefficients","# Runs","# Feasible Runs","# Successful Runs"
}
FLOAT_COLUMNS = {
    "Best Objective Value","Optimality Bound","Success Threshold",
    "Total Runtime","CPU Runtime","GPU Runtime","QPU Runtime","Other HW Runtime"
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
    dirs = [p for p in root.iterdir() if p.is_dir()]

    # Exclude any directory named "misc"
    dirs = [p for p in dirs if p.name.lower() != "misc"]

    if pattern:
        dirs = [p for p in dirs if fnmatch.fnmatch(p.name, pattern)]
    return sorted(dirs, key=lambda p: p.name.lower())


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


def run_checker_on_solutions(
    checker_cmd_tpl: str,
    submission_root: Path,
    instance_dir: Path,
    instance: str,
    solutions: List[Path],
    report: InstanceReport,
) -> None:
    for sol in solutions:
        cmd = checker_cmd_tpl.format(
            submission_root=str(submission_root),
            instance_dir=str(instance_dir),
            instance=instance,
            solution=str(sol),
        )
        # Shell execution so users can pass pipelines; but warn about shells
        try:
            proc = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
            report.checker_results.append(CheckerResult(
                solution_path=sol,
                returncode=proc.returncode,
                stdout=proc.stdout.strip(),
                stderr=proc.stderr.strip(),
            ))
        except Exception as e:
            report.fail(f"Checker execution failed for {sol.name}: {e}")


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
        if r.checker_results:
            print("Checker results:")
            for cr in r.checker_results:
                status = "OK" if cr.returncode == 0 else f"FAIL (rc={cr.returncode})"
                print(f"  - {cr.solution_path.name}: {status}")
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

    # 5) Run checker if requested
    if args.checker_cmd and solutions:
        run_checker_on_solutions(args.checker_cmd, submission_root, inst_dir, instance, solutions, report)
        if args.fail_on_checker:
            for cr in report.checker_results:
                if cr.returncode != 0:
                    report.fail(f"Checker failed for solution {cr.solution_path.name} with return code {cr.returncode}.")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate benchmarking-library submission.")
    parser.add_argument("submission_root", type=Path, help="Path to submission root directory.")
    parser.add_argument("--checker-cmd", type=str, default=None,
                        help=("Command template to run a solution checker for each solution. "
                              "Placeholders: {submission_root} {instance_dir} {instance} {solution}"))
    parser.add_argument("--fail-on-checker", action="store_true",
                        help="Mark instance invalid if checker returns nonzero.")
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
        print(f"ERROR: Submission root does not exist or is not a directory: {root}", file=sys.stderr)
        sys.exit(2)

    instance_dirs = find_instance_dirs(root, args.instance_pattern)
    if not instance_dirs:
        print("No instance subdirectories found matching criteria.", file=sys.stderr)
        sys.exit(2)

    reports: List[InstanceReport] = []
    for inst_dir in instance_dirs:
        if args.verbose:
            print(f"Validating instance: {inst_dir.name}")
        reports.append(validate_instance(root, inst_dir, args))

    print_report(reports, quiet=args.quiet)

    # Nonzero exit on any failure
    sys.exit(0 if all(r.ok for r in reports) else 1)


if __name__ == "__main__":
    main()
