#!/usr/bin/env python3
"""
For the 20250822_Abs2_Schicker submission: run the checker on every solution,
set '# Feasible Runs' to 0 in the CSV for every run that the checker rejects,
and regenerate each leaf README.md from the updated CSV.

Usage (from 06-portfolio/):
    python fix_abs2_feasibility.py [--dry-run]
"""

import csv as csvmod
import io
import subprocess
import sys
import re
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv
CHECKER = Path(__file__).parent / "check" / "target" / "release" / "check_portfolio"
INSTANCES = Path(__file__).parent / "instances"
SUB_ROOT = Path(__file__).parent / "submissions" / "20250822_Abs2_Schicker"

# Column index (0-based) for # Feasible Runs in the 30-col CSV standard
COL_N_FEASIBLE = 19   # column 20 is 1-based → index 19


def check_solution(inst_dir: Path, sol: Path) -> bool:
    """Return True if the checker exits 0 (feasible)."""
    result = subprocess.run(
        [str(CHECKER), str(inst_dir), str(sol)],
        capture_output=True,
    )
    return result.returncode == 0


def update_csv(csv_path: Path, feasible: bool) -> bool:
    """Set # Feasible Runs column to 0 or 1 as appropriate. Returns True if changed."""
    text = csv_path.read_text(encoding="utf-8")
    reader = csvmod.reader(io.StringIO(text))
    rows = list(reader)
    if len(rows) < 2:
        return False
    header = rows[0]
    try:
        idx = header.index("# Feasible Runs")
    except ValueError:
        return False
    data = rows[1]
    new_val = "1" if feasible else "0"
    if data[idx].strip() == new_val:
        return False
    data[idx] = new_val
    if not DRY_RUN:
        out = io.StringIO()
        writer = csvmod.writer(out, lineterminator="\n")
        writer.writerows(rows)
        csv_path.write_text(out.getvalue(), encoding="utf-8")
    return True


def generate_readme(inst_name: str) -> None:
    """Re-run check_submission.py --generate-readme for one leaf instance."""
    script = Path(__file__).parent.parent / "misc" / "ci" / "check_submission.py"
    subprocess.run(
        [sys.executable, str(script), "--generate-readme",
         "--instance-pattern", inst_name, str(SUB_ROOT)],
        capture_output=True,
    )


def main():
    if not CHECKER.exists():
        print(f"ERROR: checker not found at {CHECKER}. Run `cargo build --release` first.")
        sys.exit(1)

    changed_csv = 0
    changed_readme = 0

    for leaf_dir in sorted(SUB_ROOT.rglob("*/po_*_l*")):
        if not leaf_dir.is_dir():
            continue
        inst_name = leaf_dir.name  # e.g. po_a010_t10_orig_b004_l0

        # Find the solution file
        sols = list(leaf_dir.glob(f"{inst_name}_solution.sol"))
        if not sols:
            continue
        sol = sols[0]

        # Derive the instance dir from the solution header
        text = sol.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^instance\s+(\S+)", text, re.MULTILINE)
        if not m:
            continue
        base_inst = m.group(1)  # e.g. po_a010_t10_orig
        inst_dir = INSTANCES / base_inst
        if not inst_dir.is_dir():
            print(f"  WARN: instance dir not found: {inst_dir}")
            continue

        feasible = check_solution(inst_dir, sol)

        # Update the CSV
        csv = leaf_dir / f"{inst_name}_summary.csv"
        if not csv.exists():
            continue
        updated = update_csv(csv, feasible)
        status = "INFEASIBLE" if not feasible else "feasible"
        marker = " [CSV updated]" if updated else ""
        print(f"  {inst_name}: {status}{marker}")
        if updated:
            changed_csv += 1

        # Regenerate the README from the updated CSV
        if updated and not DRY_RUN:
            generate_readme(inst_name)
            changed_readme += 1

    print(f"\nDone. CSVs updated: {changed_csv}, READMEs regenerated: {changed_readme}")


if __name__ == "__main__":
    main()
