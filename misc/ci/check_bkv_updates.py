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

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from site_builder import config
from site_builder.solutions import load_reference_map

ROOT_RE = re.compile(r"^([0-9]{2}-[^/]+/submissions/[^/]+)/")
SOLUTIONS_RE = re.compile(r"^([0-9]{2}-[^/]+)/solutions/")


def _git_changed_paths(base: str, head: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", base, head],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git diff failed (rc={result.returncode}): {result.stderr.strip()}")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _find_submission_roots(paths: list[str]) -> set[str]:
    roots: set[str] = set()
    for path in paths:
        m = ROOT_RE.match(path)
        if m:
            roots.add(m.group(1))
    return roots


def _parse_float(raw: str | None) -> float | None:
    if raw is None:
        return None
    text = raw.strip()
    if not text or text.upper() in {"N/A", "NA"}:
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def _is_feasible_row(row: dict[str, str]) -> bool:
    feasible = _parse_float(row.get("# Feasible Runs"))
    if feasible is None:
        return True
    return feasible > 0


def _iter_summary_rows(submission_root: Path):
    for summary_csv in sorted(submission_root.rglob("*_summary.csv")):
        if not summary_csv.is_file():
            continue
        with summary_csv.open(newline="", encoding="utf-8", errors="replace") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                yield summary_csv, row


def _load_reference_map(problem_dir: Path) -> dict[str, dict]:
    return load_reference_map(problem_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail when a PR submission reports a better objective value than the "
            "current reference best-known value without updating that problem's solutions/ directory."
        )
    )
    parser.add_argument("--base", required=True, help="Base commit SHA for the PR diff.")
    parser.add_argument("--head", required=True, help="Head commit SHA for the PR diff.")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help=(
            "Report best-known improvements informationally and always exit 0. "
            "Use this now that records are regenerated automatically on merge by "
            ".github/workflows/update-bkv.yml — a manual solutions/ update is no "
            "longer required in the PR."
        ),
    )
    args = parser.parse_args(argv)

    repo_root = Path(".").resolve()
    config.configure(root=repo_root)

    changed_paths = _git_changed_paths(args.base, args.head)
    submission_roots = sorted(_find_submission_roots(changed_paths))

    if not submission_roots:
        print("No changed submission roots found.")
        return 0

    changed_solution_problems = {
        match.group(1)
        for path in changed_paths
        for match in [SOLUTIONS_RE.match(path)]
        if match
    }

    violations: list[str] = []

    for root_rel in submission_roots:
        submission_root = repo_root / root_rel
        problem_dir = submission_root.parent.parent
        problem_name = problem_dir.name
        problem_id = problem_name.split("-", 1)[0]
        minimize = config.PROBLEM_META.get(problem_id, {}).get("minimize", True)

        ref_map = _load_reference_map(problem_dir)
        if not ref_map:
            continue

        improvements: list[tuple[str, float, float, str]] = []

        for summary_csv, row in _iter_summary_rows(submission_root):
            instance = (row.get("Problem") or "").strip()
            if not instance:
                continue

            ref_entry = ref_map.get(instance) or {}
            ref_value = ref_entry.get("value")
            if not isinstance(ref_value, (int, float)):
                continue

            sub_value = _parse_float(row.get("Best Objective Value"))
            if sub_value is None or not _is_feasible_row(row):
                continue

            better = sub_value < float(ref_value) if minimize else sub_value > float(ref_value)
            if better:
                improvements.append((instance, sub_value, float(ref_value), summary_csv.relative_to(repo_root).as_posix()))

        if not improvements:
            continue

        print(f"Detected better submission value(s) for {problem_name}:")
        for instance, sub_value, ref_value, source in improvements:
            direction = "<" if minimize else ">"
            print(f"  - {instance}: {sub_value} {direction} {ref_value} ({source})")

        if problem_name not in changed_solution_problems:
            violations.append(
                f"{problem_name}: submission improves current best-known value but PR does not modify `{problem_name}/solutions/`"
            )

    if violations:
        if args.warn_only:
            print(
                "\nNOTE: This PR improves the best-known value for the problem(s) below. "
                "The reference solutions/ files and BEST_KNOWN.md tables will be updated "
                "automatically on merge to main (.github/workflows/update-bkv.yml) — no "
                "manual solutions/ change is required in this PR:"
            )
            for violation in violations:
                print(f"  - {violation}")
            return 0
        print("\nERROR: Best-known-value improvements require solution-directory updates in the same PR:")
        for violation in violations:
            print(f"  - {violation}")
        return 1

    print("Best-known-value check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
