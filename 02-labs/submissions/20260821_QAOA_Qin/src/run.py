#!/usr/bin/env python3
"""CLI runner: solve LABS with QAOA, then generate the QOBLIB submission files.

Usage:
    python run.py --n 6,8 --runs 5
    python run.py --n 10 --runs 5 --p 2 --shots 4096 --maxiter 300
    python run.py --n 6,8 --runs 5 --outdir 02-labs/submissions/20260821_QAOA_Qin
"""

import argparse
import os
import time

from labsoa import solve, hubo_terms
from report import package_instance

CFG = {
    "submitter":   "Qin.Z",
    "affiliation": "N/A",
    "date":        "2026-08-21",
    "reference":   "https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm",
    "hardware":    "Intel(R) Xeon(R) CPU @ 2.20GHz | Ubuntu 22.04 | 12 GB",
    "workflow":    ("LABS cost function mapped to a HUBO (AQT closed form) as Pauli "
                    "Z-strings; QAOA with COBYLA parameter optimization on a local Aer "
                    "statevector simulator; best sampled bitstring per run."),
    "model":       "HUBO",
    "coeff_type":  "Integer",
    "coeff_range": "{1, 2}",
}


def main():
    ap = argparse.ArgumentParser(description="QAOA for QOBLIB 02-LABS")
    ap.add_argument("--n", required=True, help="comma-separated lengths, e.g. 6,8,10")
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--seeds", nargs="*", type=int, default=None)
    ap.add_argument("--p", type=int, default=1)
    ap.add_argument("--shots", type=int, default=2048)
    ap.add_argument("--maxiter", type=int, default=200)
    ap.add_argument("--outdir", default="02-labs/submissions/20260821_QAOA_Qin")
    args = ap.parse_args()

    seeds = args.seeds if args.seeds else list(range(args.runs))
    for n in [int(x) for x in args.n.split(",")]:
        inst = f"labs{n:03d}"
        results = []
        t_start = time.perf_counter()
        for i, seed in enumerate(seeds):
            E, bits, dt = solve(n, seed=seed, p=args.p, shots=args.shots,
                                maxiter=args.maxiter)
            results.append((E, bits, dt, seed))
            print(f"{inst} run {i+1}/{len(seeds)} (seed {seed}): E={E}  ({dt:.2f}s)")
        total = time.perf_counter() - t_start
        avg_time = total / len(seeds)              # CONTRIBUTING.md: report average runtime
        best_E = min(r[0] for r in results)
        meta = {
            "cfg": CFG, "best_E": best_E, "ncoef": len(hubo_terms(n)),
            "runs": len(seeds), "success": sum(1 for r in results if r[0] == best_E),
            "total": avg_time, "tts": min(r[2] for r in results if r[0] == best_E),
            "p": args.p,
            "remarks": (f"QAOA p={args.p}, {args.shots} shots/eval, "
                        f"COBYLA maxiter={args.maxiter}, seeds={seeds}. "
                        f"Runtimes are averages over the {len(seeds)} runs."),
        }
        inst_dir = os.path.join(args.outdir, inst)
        paths = package_instance(inst_dir, n, results, meta)
        print(f"  -> {inst}: best E={best_E}, wrote {len(paths)} solution(s) + summary + README")


if __name__ == "__main__":
    main()
