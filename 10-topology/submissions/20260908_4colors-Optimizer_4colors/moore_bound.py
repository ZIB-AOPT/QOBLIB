#!/usr/bin/env python3
# Marcin Kaminski, 4colors Research.
# SPDX-License-Identifier: Apache-2.0
"""Counting (Moore) lower bound on the diameter, for the Order/Degree problem.

A graph of maximum degree d and diameter k has at most

    M(d, k) = 1 + d * sum_{i<k} (d-1)^i

vertices: a breadth-first tree rooted at any vertex reaches at most d vertices at
depth 1 and at most (d-1) new vertices per vertex at every deeper level, and at
diameter k every vertex is within depth k of the root.  An instance (n, d) with
n > M(d, k) therefore admits no graph of diameter k, so its optimum is at least
the smallest k for which M(d, k) >= n.

The bound is combinatorial: it involves no solver, no search and no floating
point.  Where a recorded solution attains it, that solution is optimal.

    python3 moore_bound.py <path to 10-topology>

reads every instance and every recorded best-known value and prints the bound
against each, marking the rows where the two coincide.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def moore(d: int, k: int) -> int:
    """Largest order admitting maximum degree d and diameter k."""
    if k <= 0:
        return 1
    if d <= 1:
        return 2 if k >= 1 else 1
    return 1 + d * sum((d - 1) ** i for i in range(k))


def lower_bound(n: int, d: int) -> int:
    """Smallest diameter not excluded by the counting bound at order n."""
    k = 1
    while moore(d, k) < n:
        k += 1
    return k


def read_best_known(problem_dir: Path) -> dict[str, tuple[int, str]]:
    """Instance -> (best-known diameter, status) from solutions/README.md."""
    out: dict[str, tuple[int, str]] = {}
    readme = problem_dir / "solutions" / "README.md"
    for line in readme.read_text().splitlines():
        m = re.match(r"\|\s*(topology_\d+_\d+)\s*\|\s*(\d+)\s*\|\s*([a-z ]+?)\s*\|", line)
        if m:
            out[m.group(1)] = (int(m.group(2)), m.group(3).strip())
    return out


def main(argv: list[str]) -> int:
    problem_dir = Path(argv[1] if len(argv) > 1 else "10-topology")
    best = read_best_known(problem_dir)
    if not best:
        print(f"no best-known table found under {problem_dir}", file=sys.stderr)
        return 2

    rows = []
    for inst, (value, status) in best.items():
        n, d = (int(x) for x in inst.split("_")[1:3])
        rows.append((n, d, inst, value, status, lower_bound(n, d)))
    rows.sort()

    print(f"{'instance':22} {'n':>8} {'d':>3} {'best known':>10} {'bound':>6} {'status':>11}  verdict")
    tight = []
    for n, d, inst, value, status, lb in rows:
        verdict = ""
        if value == lb:
            verdict = "OPTIMAL -- attains the bound"
            if status != "optimal":
                verdict += " (recorded as best known)"
                tight.append(inst)
        else:
            verdict = f"gap {value - lb}"
        print(f"{inst:22} {n:>8} {d:>3} {value:>10} {lb:>6} {status:>11}  {verdict}")

    print()
    print(f"{len(rows)} instances; {sum(1 for r in rows if r[3] == r[5])} attain the bound.")
    if tight:
        print("Recorded as 'best known' while attaining the bound, hence optimal:")
        for inst in tight:
            print(f"  {inst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
