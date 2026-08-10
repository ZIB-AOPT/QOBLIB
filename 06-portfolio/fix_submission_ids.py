#!/usr/bin/env python3
"""
Fix portfolio submission instance IDs: add po_ prefix and normalise lambda tokens.

Changes made:
  - CSV Problem column: e.g. a010_t10_orig_b004_l0.0 → po_a010_t10_orig_b004_l0
  - Submission leaf directory names:  a010_t10_orig_b004_l0/ → po_a010_t10_orig_b004_l0/
  - Files inside leaf dirs:           a010_t10_orig_b004_l0_* → po_a010_t10_orig_b004_l0_*
  - Submission mid-level directories: a010_t10_orig_b004/ → po_a010_t10_orig_b004/

Lambda normalisation map (applied both to CSV fields and file/dir names):
  l0.0 → l0   l0.0001 → l1e-4   l0.0005 → l5e-4   l0.001 → l1e-3
  l0.01 → l1e-2   l1e-05 → l1e-5   l1e-06 → l1e-6   l5e-05 → l5e-5
"""
import re
import sys
from pathlib import Path

LAMBDA_MAP = {
    "l0.0": "l0",
    "l0.0001": "l1e-4",
    "l0.0005": "l5e-4",
    "l0.001": "l1e-3",
    "l0.01": "l1e-2",
    "l1e-05": "l1e-5",
    "l1e-06": "l1e-6",
    "l5e-05": "l5e-5",
}

# Match a lambda token anywhere in a string (as a full token between _ or end)
LAMBDA_RE = re.compile(r'(l(?:0\.0+\d*|\d+(?:\.\d+)?(?:[eE][-+]?\d+)?))')


def normalise_lambda(token: str) -> str:
    return LAMBDA_MAP.get(token, token)


def normalise_inst_id(inst_id: str) -> str:
    """Add po_ prefix (if missing) and normalise lambda token."""
    if not inst_id.startswith("po_"):
        inst_id = "po_" + inst_id
    # Replace the lambda suffix token
    inst_id = LAMBDA_RE.sub(lambda m: normalise_lambda(m.group(1)), inst_id)
    return inst_id


def fix_csv(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if len(lines) < 2:
        return False
    header = lines[0]
    data = lines[1]
    # First field is the Problem/instance column
    first_comma = data.index(",")
    old_id = data[:first_comma]
    new_id = normalise_inst_id(old_id)
    if new_id == old_id:
        return False
    new_data = new_id + data[first_comma:]
    path.write_text(header + new_data, encoding="utf-8")
    return True


def rename_tree(sub_dir: Path, dry_run: bool = False) -> int:
    """Rename files and directories inside a single submission directory."""
    count = 0
    # Bottom-up: rename files first, then dirs (innermost first)
    for path in sorted(sub_dir.rglob("*"), key=lambda p: -len(p.parts)):
        name = path.name
        new_name = normalise_inst_id(name) if (
            not name.startswith("po_") and re.match(r'a\d{3}_', name)
        ) else None
        if new_name and new_name != name:
            target = path.parent / new_name
            if not dry_run:
                path.rename(target)
            print(f"  rename: {path.relative_to(sub_dir)} -> {new_name}")
            count += 1
    return count


def main():
    root = Path(__file__).parent
    submissions_root = root / "submissions"
    dry_run = "--dry-run" in sys.argv

    for sub_dir in sorted(submissions_root.iterdir()):
        if not sub_dir.is_dir() or sub_dir.name.startswith("."):
            continue
        # Only process the two Schicker submissions
        if "Schicker" not in sub_dir.name:
            continue
        print(f"\n=== {sub_dir.name} ===")
        # 1. Fix CSVs first (before renaming so paths are still valid)
        csv_count = 0
        for csv in sorted(sub_dir.rglob("*_summary.csv")):
            if fix_csv(csv):
                csv_count += 1
        print(f"  Updated {csv_count} summary CSVs")
        # 2. Rename files and directories
        n = rename_tree(sub_dir, dry_run=dry_run)
        print(f"  Renamed {n} files/dirs")

    print("\nDone.")


if __name__ == "__main__":
    main()
