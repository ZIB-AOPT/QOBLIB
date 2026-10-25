#!/usr/bin/env python3
"""Regenerate the selected adversarial Market Split instances for QOBLIB."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path


GEN_DIR = Path(__file__).resolve().parent
REPO_ROOT = GEN_DIR.parents[2]
LICENSE_HEADER = """# This file is part of QOBLIB - Quantum Optimization Benchmarking Library
# Licensed under the Creative Commons Attribution 4.0 International License.
# You may obtain a copy of the License at
#
#     https://creativecommons.org/licenses/by/4.0/
#
# You are free to share and adapt the material for any purpose, even commercially,
# as long as you give appropriate credit and indicate if changes were made.

"""

INSTANCES = [
    # id, generator, n, m, D, outer seed, extra arguments
    ("ms_05_18000_128_ortho_n81", "ortho", 81, 5, 18000, 128, ["--tf-iters", "4000"]),
    ("ms_05_18000_191_ortho_n81", "ortho", 81, 5, 18000, 191, ["--tf-iters", "4000"]),
    ("ms_05_20000_053_ortho_n81", "ortho", 81, 5, 20000, 53, ["--tf-iters", "4000"]),
    ("ms_05_20000_228_ortho_n81", "ortho", 81, 5, 20000, 228, ["--tf-iters", "4000"]),
    ("ms_05_20000_453_v5_n81", "v5", 81, 5, 20000, 453, []),
    ("ms_05_30000_058_v5_n84", "v5", 84, 5, 30000, 58, []),
    ("ms_07_03000_098_v5_n86", "v5", 86, 7, 3000, 98, []),
    ("ms_08_01000_019_v5_n88", "v5", 88, 8, 1000, 19, []),
    ("ms_06_10000_068_v5_n90", "v5", 90, 6, 10000, 68, []),
    ("ms_05_100000_043_v5_n90", "v5", 90, 5, 100000, 43, []),
]


def parse_generated(path: Path) -> tuple[list[list[int]], list[int], list[int]]:
    lines = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    m, n = map(int, lines[0].split())
    matrix = [list(map(int, lines[i].split())) for i in range(1, m + 1)]
    if any(len(row) != n for row in matrix) or lines[m + 1] != "b":
        raise ValueError(f"malformed generated instance: {path}")
    rhs = list(map(int, lines[m + 2].split()))
    if len(rhs) != m or lines[m + 3] != "x_star":
        raise ValueError(f"malformed generated right-hand side: {path}")
    solution = list(map(int, lines[m + 4].split()))
    if len(solution) != n or any(bit not in (0, 1) for bit in solution):
        raise ValueError(f"malformed planted solution: {path}")
    actual = [sum(a * x for a, x in zip(row, solution)) for row in matrix]
    if actual != rhs:
        raise ValueError(f"planted solution does not satisfy A x = b: {path}")
    if [sum(row) for row in matrix] != [2 * value for value in rhs]:
        raise ValueError(f"RHS is not exactly half of each row sum: {path}")
    return matrix, rhs, solution


def render_dat(matrix: list[list[int]], rhs: list[int]) -> bytes:
    m, n = len(matrix), len(matrix[0])
    body = [f"{m} {n}"]
    body.extend(" ".join(map(str, row + [b])) for row, b in zip(matrix, rhs))
    return (LICENSE_HEADER + "\n".join(body) + "\n").encode()


def render_solution(solution: list[int]) -> bytes:
    return (" ".join(map(str, solution)) + "\n").encode()


def generate_one(record, temp_root: Path) -> tuple[bytes, bytes]:
    instance_id, family, n, m, cap, seed, extra = record
    out = temp_root / instance_id
    script = GEN_DIR / f"generate_market_split_{family}.py"
    command = [
        sys.executable, str(script), "--n", str(n), "--m", str(m),
        "--D", str(cap), "--seed", str(seed), "--feas-samples", "0",
        "--outdir", str(out), *extra,
    ]
    if family != "ortho":
        command.extend(["--candidates", "1"])
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
    if family == "ortho":
        out = out / f"n{n}_m{m}_hi{cap}_seed{seed}"
    matrix, rhs, solution = parse_generated(out / "instance.txt")
    return render_dat(matrix, rhs), render_solution(solution)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--check", action="store_true", help="compare with existing files without writing")
    args = parser.parse_args()
    instance_dir = args.output_root / "01-marketsplit" / "instances"
    solution_dir = args.output_root / "01-marketsplit" / "solutions"
    if not args.check:
        instance_dir.mkdir(parents=True, exist_ok=True)
        solution_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="qoblib_marketsplit_") as temp:
        for record in INSTANCES:
            instance_id = record[0]
            dat, sol = generate_one(record, Path(temp))
            targets = [
                (instance_dir / f"{instance_id}.dat", dat),
                (solution_dir / f"{instance_id}.opt.sol", sol),
            ]
            for target, payload in targets:
                if args.check:
                    if not target.is_file() or target.read_bytes() != payload:
                        raise SystemExit(f"MISMATCH: {target}")
                else:
                    target.write_bytes(payload)
            print(f"{instance_id}: {hashlib.sha256(dat).hexdigest()}")


if __name__ == "__main__":
    main()
