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
"""Submission reader.

Walks each problem's ``submissions/`` tree and parses the canonical 30-column
``*_summary.csv`` files into per-instance submission rows, mapping the verbose
CSV headers to terse canonical keys. CSV is the only supported submission format.
"""

from __future__ import annotations

import sys
from pathlib import Path

from .classify import classify_submission
from .text import parse_date_str


# Canonical key -> accepted CSV header aliases.
COLUMN_MAP: dict[str, list[str]] = {
    "instance":          ["Problem", "Problem Identifier", "Instance"],
    "submitter":         ["Submitter"],
    "affiliation":       ["Affiliation"],
    "date":              ["Date"],
    "reference":         ["Reference"],
    "value":             ["Best Objective Value"],
    "optimality_bound":  ["Optimality Bound"],
    "modeling_approach": ["Modeling Approach", "Modelling Approach"],
    "n_vars":            ["# Decision Variables"],
    "n_binary":          ["# Binary Variables"],
    "n_integer":         ["# Integer Variables"],
    "n_continuous":      ["# Continuous Variables"],
    "n_nonzero":         ["# Non-Zero Coefficients"],
    "coefficients_type": ["Coefficients Type"],
    "workflow":          ["Workflow"],
    "algorithm_type":    ["Algorithm Type"],
    "paradigm":          ["Paradigm"],
    "n_runs":            ["# Runs"],
    "n_feasible":        ["# Feasible Runs"],
    "n_successful":      ["# Successful Runs"],
    "success_threshold": ["Success Threshold"],
    "hardware":          ["Hardware Specifications"],
    "runtime_total":     ["Total Runtime"],
    "time_to_solution":  ["Time to Solution"],
    "runtime_cpu":       ["CPU Runtime"],
    "runtime_gpu":       ["GPU Runtime"],
    "runtime_qpu":       ["QPU Runtime"],
    "runtime_other":     ["Other HW Runtime"],
    "remarks":           ["Remarks"],
}


def _resolve_instance(col_instance: str, path_instance: str | None, known: set[str] | None) -> str:
    """Pick the canonical instance name for a submission row.

    The ``Problem`` column is authoritative whenever it already names a real
    instance (the canonical case — true for ~all submissions). Otherwise fall
    back to the instance encoded in the file path
    (``<instance>/<instance>_summary.csv``); this rescues packages that put a
    human-readable label in the column (e.g. ``LABS (N = 6)``) instead of the
    instance id. A path like ``labs006-without_calibration`` (a run variant)
    resolves to its base instance ``labs006`` — the longest known instance it
    extends — so both runs attach to the real instance.
    """
    if known and col_instance and col_instance in known:
        return col_instance
    if path_instance and known:
        if path_instance in known:
            return path_instance
        base = max(
            (k for k in known
             if path_instance == k or path_instance.startswith(f"{k}-") or path_instance.startswith(f"{k}_")),
            key=len,
            default=None,
        )
        if base:
            return base
    return col_instance or (path_instance or "")


def read_csv_submissions_folder(submissions_dir: Path, known_instances: set[str] | None = None) -> dict:
    """
    Walk submissions_dir recursively.  Collects:
      • all *_summary.csv files anywhere in the tree
      • any *.csv files that are direct children of submissions_dir

    Returns {instance_name: [list_of_submission_dicts]}.
    Each dict has canonical keys matching the 30-column CSV standard plus
    '_source_dir' (the immediate subdirectory name, e.g. '20241222_Abs2_Schicker').

    ``known_instances`` (the problem's real instance names) lets a row whose
    ``Problem`` column is not a valid instance fall back to the instance encoded
    in its ``<instance>/<instance>_summary.csv`` path (see _resolve_instance).
    """
    import csv as csvmod

    def get_col(row: dict, canonical: str) -> str:
        for alias in COLUMN_MAP.get(canonical, [canonical]):
            if alias in row:
                return (row[alias] or "").strip()
        return ""

    result: dict = {}
    if not submissions_dir.is_dir():
        return result

    # Collect CSV files: direct children + all *_summary.csv anywhere in tree
    csv_files: set[Path] = set()
    for f in submissions_dir.iterdir():
        if f.is_file() and f.suffix.lower() == ".csv":
            csv_files.add(f)
    for f in submissions_dir.rglob("*_summary.csv"):
        if f.is_file():
            csv_files.add(f)

    for csv_file in sorted(csv_files):
        rel = csv_file.relative_to(submissions_dir)
        source_dir = rel.parts[0] if len(rel.parts) > 1 else csv_file.stem
        # Instance encoded in the canonical "<instance>_summary.csv" filename,
        # used when the row's "Problem" column does not name a real instance.
        path_instance = (
            csv_file.name[: -len("_summary.csv")] if csv_file.name.endswith("_summary.csv") else None
        )
        try:
            with open(csv_file, newline="", encoding="utf-8", errors="replace") as fh:
                reader = csvmod.DictReader(fh)
                for raw in reader:
                    row = {(k or "").strip(): (v or "").strip()
                           for k, v in raw.items() if k}
                    instance = _resolve_instance(get_col(row, "instance"), path_instance, known_instances)
                    if not instance:
                        continue
                    val_str = get_col(row, "value")
                    try:
                        value: float | None = float(val_str)
                    except (ValueError, TypeError):
                        value = None

                    sub: dict = {
                        "instance": instance,
                        "value": value,
                        "_source_dir": source_dir,
                        "_source_file": rel.as_posix(),
                    }
                    for key in COLUMN_MAP:
                        if key not in ("instance", "value"):
                            sub[key] = get_col(row, key)
                    sub["date"] = parse_date_str(sub.get("date", ""))
                    sub["category"] = classify_submission(sub)
                    result.setdefault(instance, []).append(sub)
        except Exception as exc:
            print(f"  Warning: skipping {csv_file}: {exc}", file=sys.stderr)

    return result
