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
"""Reference-solution / best-known-value (BKV) readers.

Maps the repository's ``solutions/`` folders to ``{instance: {value, status,
source_file}}``. Handles per-instance ``.sol`` files (with the objective stored
inline or in a comment), aggregate ``record.csv`` / ``solutions.json`` files,
and the Birkhoff ``qbench_*.json`` solution bundles.
"""

from __future__ import annotations

import gzip
import json
import lzma
import re
from pathlib import Path

from . import config
from .text import normalize_portfolio_lambda


STATUS_PRIORITY = {
    "open": 0,
    "best_known": 1,
    "solved": 2,
    "optimal": 3,
}


# A labelled objective anywhere in a file (incl. comment lines). The separator may
# be ':' / '=' or just whitespace (e.g. routing's "Cost 583").
OBJECTIVE_LABEL_RE = re.compile(
    r"\b(?:energy|objective(?:\s+value)?|value|obj|bkv|cost|merit)\b\s*[=:]?\s*"
    r"([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)",
    re.IGNORECASE,
)


def _read_text(path: Path, max_bytes: int | None = None) -> str | None:
    """Read a solution file as text, transparently decompressing ``.xz`` / ``.gz``.

    ``max_bytes`` bounds how much is read (the objective always lives in the header
    for the formats we parse, so topology's large ``.gph.xz`` graphs need only a
    small prefix).
    """
    try:
        name = path.name.lower()
        if name.endswith(".xz"):
            opener = lambda: lzma.open(path, "rt", encoding="utf-8", errors="replace")
        elif name.endswith(".gz"):
            opener = lambda: gzip.open(path, "rt", encoding="utf-8", errors="replace")
        else:
            opener = lambda: open(path, "rt", encoding="utf-8", errors="replace")
        with opener() as fh:
            return fh.read(max_bytes) if max_bytes else fh.read()
    except Exception:
        return None


def _labelled_value(text: str) -> float | None:
    """First labelled objective (``# Objective value = …``) found in ``text``."""
    for line in text.splitlines():
        m = OBJECTIVE_LABEL_RE.search(line)
        if m:
            return float(m.group(1))
    return None


def _independentset_size(text: str) -> float | None:
    """Objective of a Maximum-Independent-Set solution = size of the chosen set.

    Handles both storage formats: a Gurobi ``.mst`` vector (``x#7 1`` lines → count
    the ones) and a bare *nodelist* (one vertex index per line → count the lines).
    """
    ones = 0
    nodes = 0
    is_vector = False
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.lower().startswith("c "):
            continue
        parts = s.split()
        if len(parts) == 2 and parts[1] in ("0", "1"):
            is_vector = True
            if parts[1] == "1":
                ones += 1
        elif len(parts) == 1 and re.fullmatch(r"[-+]?\d+", parts[0]):
            nodes += 1
    if is_vector:
        return float(ones)
    return float(nodes) if nodes else None


def read_objective(path: Path, problem_id: str | None = None) -> float | None:
    """Read the objective value from a solution file, format-aware per problem.

    Many solution files store the solution *vector* (one spin/bit/vertex per line)
    with the objective in a comment (e.g. LABS ``# Energy: 898``, network
    ``# Objective value = …``). We therefore look for a labelled objective FIRST
    (including in comments) and only fall back to a bare number when the file is
    literally a single value — never the first element of a solution vector.

    Problem-specific formats where the objective is not a labelled number:
      * 10-topology: the diameter lives in a ``c … Diameter N`` comment.
      * 07-independentset: nodelist / ``.mst`` files encode the set, whose *size*
        is the objective (see :func:`_independentset_size`).
    """
    pid = (problem_id or "")[:2]

    if pid == "10":
        text = _read_text(path, max_bytes=65536)
        if not text:
            return None
        m = re.search(r"diameter\s+([-+]?\d+(?:\.\d+)?)", text, re.IGNORECASE)
        return float(m.group(1)) if m else None

    text = _read_text(path)
    if not text:
        return None
    text = text.strip()
    if not text:
        return None

    # Try JSON
    if text.startswith("{"):
        try:
            d = json.loads(text)
            for key in ("value", "objective", "obj", "best", "bkv", "energy"):
                if key in d:
                    return float(d[key])
        except json.JSONDecodeError:
            pass

    # A labelled objective anywhere in the file (incl. comment lines).
    labelled = _labelled_value(text)
    if labelled is not None:
        return labelled

    # Maximum independent set: objective = size of the encoded set. Handled here
    # (before the bare-number fallback) so a nodelist's first vertex index is never
    # mistaken for the objective.
    if pid == "07":
        return _independentset_size(text)

    # Fall back to a bare number ONLY when the first data line is a lone value
    # (otherwise it is a solution vector and the first token is not the objective).
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) == 1:
            try:
                return float(parts[0])
            except ValueError:
                return None
        return None  # first data line is a vector → no inline objective
    return None


def read_bkv_from_sol_file(path: Path) -> float | None:
    """Backwards-compatible objective reader for problems whose format is generic."""
    return read_objective(path, None)


def normalise_solution_stem(path: Path) -> tuple[str, str]:
    """Map repository solution filenames back to their instance name and status."""
    parts = path.name.split(".")
    status = "open"

    while parts and parts[-1] in {"xz", "gz", "bz2"}:
        parts.pop()
    while parts and parts[-1] in {"sol", "txt", "json", "gph", "xml", "mst"}:
        parts.pop()
    if parts and parts[-1] in {"opt", "bst", "solved"}:
        marker = parts.pop()
        status = {
            "opt": "optimal",
            "bst": "best_known",
            "solved": "solved",
        }[marker]

    return ".".join(parts), status


def merge_solution_entry(
    result: dict[str, dict],
    inst: str,
    value: float | None,
    status: str,
    source_file: str | None = None,
) -> None:
    if not inst:
        return

    current = result.get(inst)
    current_priority = STATUS_PRIORITY.get(current.get("status", "open"), 0) if current else -1
    new_priority = STATUS_PRIORITY.get(status, 0)

    if current is None or new_priority > current_priority:
        merged = {"status": status}
        if value is not None:
            merged["value"] = value
        elif current and "value" in current:
            merged["value"] = current["value"]
        if source_file:
            merged["source_file"] = source_file
        elif current and "source_file" in current:
            merged["source_file"] = current["source_file"]
        result[inst] = merged
        return

    if value is not None and "value" not in current:
        current["value"] = value
    if source_file and "source_file" not in current:
        current["source_file"] = source_file


# Per-instance solution extensions whose objective we can read (after stripping
# any ``.xz`` / ``.gz`` compression).
READABLE_SOLUTION_EXTS = {"sol", "txt", "json", "gph", "mst"}


def _solution_ext(path: Path) -> str:
    """Final solution extension of ``path`` after stripping compression suffixes."""
    parts = path.name.split(".")
    while parts and parts[-1].lower() in {"xz", "gz", "bz2"}:
        parts.pop()
    return parts[-1].lower() if len(parts) > 1 else ""


def read_solutions_folder(solutions_dir: Path, problem_id: str | None = None) -> dict[str, dict]:
    """
    Returns {instance_stem: {"value": float, "status": "optimal"|"open"|"best_known"}}.
    Handles:
      - One .sol file per instance (filename matches instance stem).
      - A record.csv / solutions.csv with columns: instance, value, status.
      - A record.json / solutions.json.

    ``problem_id`` selects the format-aware objective reader (see
    :func:`read_objective`) for problems whose objective is not a labelled number
    (e.g. 07-independentset nodelists, 10-topology diameters).
    """
    result: dict[str, dict] = {}
    if not solutions_dir.is_dir():
        return result

    # CSV-style aggregate file
    for csv_name in ("record.csv", "solutions.csv", "best_known.csv"):
        csv_path = solutions_dir / csv_name
        if csv_path.exists():
            import csv
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    inst = row.get("instance") or row.get("name") or ""
                    val_str = row.get("value") or row.get("obj") or row.get("objective") or ""
                    status = (row.get("status") or "open").strip().lower()
                    try:
                        result[inst.strip()] = {
                            "value": float(val_str),
                            "status": status,
                            "source_file": config.rel_to_root(csv_path),
                        }
                    except ValueError:
                        pass
            if result:
                return result  # prefer aggregate file

    # JSON aggregate file
    for json_name in ("record.json", "solutions.json", "best_known.json"):
        json_path = solutions_dir / json_name
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text())
                if isinstance(data, dict):
                    for inst, entry in data.items():
                        if isinstance(entry, dict):
                            val = entry.get("value") or entry.get("obj")
                            status = entry.get("status", "open")
                        else:
                            val, status = entry, "open"
                        try:
                            result[inst] = {
                                "value": float(val),
                                "status": status,
                                "source_file": config.rel_to_root(json_path),
                            }
                        except (TypeError, ValueError):
                            pass
                return result
            except Exception:
                pass

    # Per-instance solution files
    for sol_file in sorted(solutions_dir.rglob("*")):
        if not sol_file.is_file() or sol_file.name.startswith(".") or sol_file.name == "README.md":
            continue

        inst, status = normalise_solution_stem(sol_file)
        value = None
        if _solution_ext(sol_file) in READABLE_SOLUTION_EXTS:
            value = read_objective(sol_file, problem_id)
        merge_solution_entry(
            result,
            inst,
            value,
            status,
            source_file=config.rel_to_root(sol_file),
        )

    return result


# ---------------------------------------------------------------------------
# Birkhoff (03) exactness gate.
#
# The 03 objective is the *minimum number of permutation matrices whose convex
# combination equals the target doubly-stochastic matrix exactly*. An approximate
# decomposition trivially wins on that count — you can always use fewer matrices
# if you tolerate reconstruction error — so an approximate result is not comparable
# to an exact one and must not be credited a best-known value, awarded attribution
# on the leaderboard, or counted as "reached the optimum".
#
# A submission's self-reported ``# Feasible Runs``/objective cannot be trusted for
# this: an approximate run legitimately reports a feasible, low objective. So we
# reconstruct the target from the shipped solution file and require *entrywise*
# agreement to within floating-point slack (``|target − reconstructed| ≤
# BIRKHOFF_ENTRY_REL_TOL · scale``). This admits legitimate floating-point
# decompositions (entries landing at e.g. 1940.0000000000002, residual ~1e-34)
# while rejecting genuine approximations (residual ~1e-6). It is deliberately
# stricter than the per-problem Rust checker's *approximate* mode
# (``--tolerance > 0``, aggregate normalised Frobenius²), which exists to accept
# approximations and is therefore the wrong criterion for attribution.
BIRKHOFF_CONVEXITY_REL_TOL = 1e-6
BIRKHOFF_ENTRY_REL_TOL = 1e-9

# Cache parsed instance bundles: every 03 submission of a given (n, density) reads
# the same qbench_*.json, so parse each at most once per build.
_birkhoff_instance_cache: dict[Path, dict] = {}


def birkhoff_instance_file(problem_dir: Path, inst: str) -> Path | None:
    """Resolve the qbench instance file backing a Birkhoff instance name.

    Mirrors check_submission._build_auto_checker_cmd: ``B{n}_{k}_{idx}`` maps to
    ``qbench_{n:02d}_dense.json`` when ``k == n²`` and ``…_sparse.json`` otherwise.
    """
    m = re.match(r"B(\d+)_(\d+)_\d+", inst, re.IGNORECASE)
    if not m:
        return None
    n, k = int(m.group(1)), int(m.group(2))
    density = "dense" if k == n * n else "sparse"
    f = problem_dir / "instances" / f"qbench_{n:02d}_{density}.json"
    return f if f.exists() else None


def find_birkhoff_submission_solution(problem_dir: Path, source_dir: str, instance: str) -> Path | None:
    """Locate the solution file a submission provides for ``instance``.

    Prefers a single ``<instance>_solution.<ext>``; otherwise the lowest-numbered
    ``solutions/<instance>_solution_<N>.<ext>``. Shared with update_bkv so the BKV
    generator and the site builder agree on which file to verify.
    """
    base = problem_dir / "submissions" / source_dir
    if not base.is_dir():
        return None
    singles = [
        p for p in sorted(base.rglob(f"{instance}_solution.*"))
        if p.is_file() and "/solutions/" not in p.as_posix()
    ]
    if singles:
        return singles[0]
    numbered = sorted(p for p in base.rglob(f"{instance}_solution_*") if p.is_file())
    return numbered[0] if numbered else None


def birkhoff_solution_is_exact(problem_dir: Path, inst: str, sol_path: Path) -> bool:
    """True iff the shipped Birkhoff solution reconstructs the target exactly.

    "Exact" means entrywise agreement up to floating-point slack (see the section
    note above). Returns False on any structural problem (missing/mismatched
    instance, non-permutation, non-convex weights, dimension mismatch) — an
    unverifiable solution is not eligible to define a best-known value.
    """
    inst_file = birkhoff_instance_file(problem_dir, inst)
    if inst_file is None:
        return False
    inst_data = _birkhoff_instance_cache.get(inst_file)
    if inst_data is None:
        try:
            inst_data = json.loads(inst_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False
        _birkhoff_instance_cache[inst_file] = inst_data
    try:
        sol_data = json.loads(sol_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False

    entry = next(
        (v for v in inst_data.values() if isinstance(v, dict) and v.get("id") == inst),
        None,
    )
    if entry is None:
        return False
    sol = next(
        (v for v in sol_data.values() if isinstance(v, dict) and v.get("id") == inst),
        None,
    )
    if sol is None and len(sol_data) == 1:
        only = next(iter(sol_data.values()))
        sol = only if isinstance(only, dict) else None
    if sol is None:
        return False

    try:
        n = int(entry["n"])
        scale = float(entry["scale"])
        target = list(entry["scaled_doubly_stochastic_matrix"])
        weights = [float(w) for w in sol["weights"]]
        perms = list(sol["permutations"])
    except (KeyError, TypeError, ValueError):
        return False

    if len(target) != n * n or len(perms) != len(weights) * n:
        return False
    if abs(sum(weights) - scale) > BIRKHOFF_CONVEXITY_REL_TOL * scale:
        return False

    reconstructed = [0.0] * (n * n)
    for i, w in enumerate(weights):
        perm = perms[i * n:(i + 1) * n]
        if sorted(perm) != list(range(1, n + 1)):  # not a permutation of 1..n
            return False
        for row in range(n):
            reconstructed[row * n + (perm[row] - 1)] += w

    tol = BIRKHOFF_ENTRY_REL_TOL * scale
    return all(abs(target[i] - reconstructed[i]) <= tol for i in range(n * n))


def load_birkhoff_solution_map(problem_dir: Path) -> dict[str, dict]:
    result: dict[str, dict] = {}
    solutions_dir = problem_dir / 'solutions'
    for sol_file in sorted(solutions_dir.glob('qbench_*.json')):
        try:
            data = json.loads(sol_file.read_text(encoding='utf-8'))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        for key, entry in data.items():
            if not isinstance(entry, dict):
                continue
            inst_id = entry.get('id')
            if not inst_id:
                continue
            status = 'optimal' if entry.get('optimal') else 'best_known'
            merged = {
                'status': status,
                'source_file': config.rel_to_root(sol_file),
            }
            if 'k' in entry:
                merged['value'] = float(entry['k'])
            result[inst_id] = merged
    return result


def load_portfolio_solution_map(problem_dir: Path) -> dict[str, dict]:
    """Reference map for 06-portfolio.

    Reference solutions live under ``solutions/<instance-dir>/*.{opt,bst}.sol``,
    one file per (instance, budget, lambda) key. The instance directory name is
    the base instance (e.g. ``po_a010_t10_orig``); the full sub-instance key is
    the solution filename stem (e.g. ``po_a010_t10_orig_b004_l1e-4``).

    Keys are canonicalised (``po_`` prefix dropped, λ suffix normalised via
    :func:`normalize_portfolio_lambda`) so they match the instance-source and
    model keys the rest of the builder joins on — the regenerated solution files
    use a compact λ tag (``_l1e-4``) while the instance grid feeds decimals
    (``_l0.0001``); without normalisation the reference values never attach.
    """
    result: dict[str, dict] = {}
    solutions_dir = problem_dir / "solutions"
    for sol_file in sorted(solutions_dir.rglob("*.sol")):
        if not sol_file.is_file():
            continue
        inst, status = normalise_solution_stem(sol_file)
        inst = normalize_portfolio_lambda(inst.removeprefix("po_"))
        value = read_objective(sol_file, "06")
        if value is None:
            continue
        current = result.get(inst)
        if (current is None or value < current["value"]
                or STATUS_PRIORITY.get(status, 0) > STATUS_PRIORITY.get(current["status"], 0)):
            result[inst] = {
                "value": value,
                "status": status,
                "source_file": config.rel_to_root(sol_file),
            }
    return result


def load_reference_map(problem_dir: Path) -> dict[str, dict]:
    """Reference (best-known baseline) map for one problem, dispatched by format.

    Most problems keep one solution file per instance (:func:`read_solutions_folder`);
    03-birkhoff stores aggregate ``qbench_*.json`` bundles and 06-portfolio stores
    ``.tar.gz`` families, each with a dedicated reader.
    """
    problem_id = problem_dir.name.split("-", 1)[0]
    if problem_id == "03":
        return load_birkhoff_solution_map(problem_dir)
    if problem_id == "06":
        return load_portfolio_solution_map(problem_dir)
    return read_solutions_folder(problem_dir / "solutions", problem_id)
