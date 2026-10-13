#!/usr/bin/env python3
"""Regenerate the five selected frozen-XORSAT MIS instances and solutions."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path


GEN_DIR = Path(__file__).resolve().parent
REPO_ROOT = GEN_DIR.parents[2]
LICENSE_HEADER = """c This file is part of QOBLIB - Quantum Optimization Benchmarking Library
c Licensed under the Creative Commons Attribution 4.0 International License.
c You may obtain a copy of the License at
c
c     https://creativecommons.org/licenses/by/4.0/
c
c You are free to share and adapt the material for any purpose, even commercially,
c as long as you give appropriate credit and indicate if changes were made.

"""
CASES = [
    # instance id, family, size argument, optimum, seed
    ("frozen_xorsat_c3k3_compact_n700", "compact", 175, 175, 1),
    ("frozen_xorsat_c3k3_compact_n800", "compact", 200, 200, 1),
    ("frozen_xorsat_c3k3_compact_n1000", "compact", 250, 250, 1),
    ("frozen_xorsat_c3k3_compact_n1200", "compact", 300, 300, 1),
    ("frozen_xorsat_c3k3_regular_n1500", "regular", 250, 500, 1),
    ("frozen_xorsat_v2_qc_l75_s1", "v2_qc", 75, 225, 1),
    ("frozen_xorsat_v2_qc_l100_s4", "v2_qc", 100, 300, 4),
    ("frozen_xorsat_v2_qc_l125_s1", "v2_qc", 125, 375, 1),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--check", action="store_true", help="compare with existing files without writing")
    args = parser.parse_args()
    instance_dir = args.output_root / "07-independentset" / "instances"
    solution_dir = args.output_root / "07-independentset" / "solutions"
    if not args.check:
        instance_dir.mkdir(parents=True, exist_ok=True)
        solution_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="qoblib_xorsat_") as temp:
        temp_root = Path(temp)
        for instance_id, family, size_arg, optimum, seed in CASES:
            if family == "compact":
                script = GEN_DIR / "gen_xorsat_compact.py"
                command = [sys.executable, str(script), str(size_arg), "3", "3", str(seed), instance_id]
            elif family == "regular":
                script = GEN_DIR / "gen_xorsat_reg.py"
                command = [sys.executable, str(script), str(size_arg), "3", str(seed), instance_id]
            else:
                script = GEN_DIR / "gen_xorsat_qc_v2.py"
                command = [sys.executable, str(script), str(size_arg), str(seed), instance_id]
            subprocess.run(command, cwd=temp_root, check=True, stdout=subprocess.DEVNULL)
            generated = temp_root / "logs" / "xor_lab"
            graph = LICENSE_HEADER.encode() + (generated / f"{instance_id}.dimacs").read_bytes()
            solution_values = (generated / f"{instance_id}.sol").read_bytes().split()
            if len(solution_values) != optimum:
                raise ValueError(f"wrong planted solution size for {instance_id}")
            solution = b"\n".join(solution_values) + b"\n"
            targets = [
                (instance_dir / f"{instance_id}.gph", graph),
                (solution_dir / f"{instance_id}.opt.sol", solution),
            ]
            for target, payload in targets:
                if args.check:
                    if not target.is_file() or target.read_bytes() != payload:
                        raise SystemExit(f"MISMATCH: {target}")
                else:
                    target.write_bytes(payload)
            print(f"{instance_id}: {hashlib.sha256(graph).hexdigest()}")


if __name__ == "__main__":
    main()
