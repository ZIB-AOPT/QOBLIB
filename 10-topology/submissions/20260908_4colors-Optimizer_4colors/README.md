# 4colors Optimizer -- 10-topology

Marcin Kaminski, 4colors Research. 2026-09-08. Apache-2.0.

Solutions for three open instances of the Order/Degree problem. `topology_30_6` and `topology_35_5`
are optimal; `topology_50_4` is an improvement with no optimality claim.

| instance | previous | this submission | `Optimality Bound` |
|---|---:|---:|---|
| `topology_30_6` | 3 | 2 | 2 |
| `topology_35_5` | 4 | 3 | 3 |
| `topology_50_4` | 5 | 4 | N/A |

## Method

Integer diameter is a plateau objective, so it is not minimized directly. The solver fixes a target
diameter `k` and minimizes a distance-excess objective over degree-preserving moves, under simulated
annealing followed by a deterministic polish. All-pairs distances are computed exactly at every
evaluation, so the diameter of any candidate is never an estimate.

Each run fixes a target diameter and is given 120 s. Measured over 8 seeds, one core per run:
`topology_35_5` and `topology_50_4` reach their target on 8 seeds out of 8 with a median time to
solution of about 0.02 s; `topology_30_6` reaches diameter 2 on 4 seeds out of 8, with a median of
19 s and a best of 0.33 s. The per-instance run counts and timings in the summary CSVs are these
measurements.

## Optimality

A graph of maximum degree `d` and diameter `k` has at most `1 + d * sum_{i<k} (d-1)^i` vertices,
since a breadth-first tree rooted anywhere branches at most `d` ways at the root and `d-1` ways
thereafter. An instance `(n, d)` therefore has diameter at least the smallest `k` for which that
expression reaches `n`.

- `topology_30_6`: at `k = 1` the bound gives 7 < 30, so diameter 2 is optimal.
- `topology_35_5`: at `k = 2` the bound gives 26 < 35, so diameter 3 is optimal.
- `topology_50_4`: at `k = 3` the bound gives 53 >= 50 and does not settle the instance.

`moore_bound.py` in this directory regenerates the bound for every instance in the class directly
from `10-topology/solutions/README.md`:

    python3 moore_bound.py 10-topology

It needs the Python standard library only.

## Verification

Every submitted graph was checked with `10-topology/check` built from this tree, and independently
with a second implementation that recomputes exact all-pairs distances and the degree sequence. That
implementation was validated first by reproducing the recorded diameter of each shipped reference
graph.

## Environment

Intel Core Ultra 9 275HX, 24 cores (8 performance + 16 efficiency), 93 GB RAM, Ubuntu 24.04.
Single-threaded per run; gcc 13, `-O3 -march=native`. Python 3.12 for `moore_bound.py`.
No GPU, QPU, annealer or quantum simulator was used at any stage.

## Files

    README.md                       this file
    moore_bound.py                  regenerates the counting bound for the class
    <instance>/<instance>_solution.gph
    <instance>/<instance>_summary.csv
