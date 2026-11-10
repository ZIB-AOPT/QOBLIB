# 4colors Optimizer - 03-birkhoff

Marcin Kaminski, 4colors Research. 2026-09-08. Apache-2.0.

284 solutions for the minimum Birkhoff decomposition problem: 269 lower than the recorded value and
15 first values. Optimality is asserted on 18 of them.

| | instances | reduction |
|---|---:|---:|
| Lower than the recorded value | 269 | 9,771 |
| - dense | 130 | 2,310 |
| - sparse | 139 | 7,461 |
| First value (no previous entry) | 15 | - |
| total | 284 | 9,771 |

## Method

Four components run under a per-instance time budget: a greedy bottleneck construction; a
minimum-support integer program over an enumerated pool of candidate permutations; a
large-neighborhood search whose subproblems are small enough that every legal column can be
enumerated, so each move is exact; and a structural refinement that uses the fact that every row of
the matrix induces a partition of the same weight multiset. All arithmetic is on the scaled
integers, so every decomposition reconstructs its matrix exactly.

Runs are independent and differ only in seed; the submitted value is always the value of the
submitted file. Per-instance counts are in the summary CSVs.

## Optimality

Asserted on 18 instances, all with n <= 9. `PROOF.md` gives the argument and `birkhoff_proof.py`
reproduces it using the Python standard library alone. In outline: every term of a valid
decomposition is a perfect matching of the support, so the admissible columns are finite and can be
listed in full; optimality of an incumbent of size k is then the single question "is there a
combination of at most k-1 of them?", and INFEASIBLE is the certificate.

Two independent checks accompany it: the column count is cross-checked against Ryser's permanent
formula in exact integer arithmetic, and at n = 3 the result is replicated by exhaustive enumeration
over every subset in exact rational arithmetic with no solver involved. `birkhoff_proof.py` also
exports the feasibility model as a plain `.lp` file, so the certificate can be reproduced with any
MILP solver rather than taken on trust.

## Verification

All 284 solutions were checked with `03-birkhoff/check` built from this tree, and independently with
a verifier in exact integer arithmetic that recomputes the reconstruction and the convexity
condition. The two agree on every instance. Weights are emitted as integers scaled by the instance
scale, so no floating-point tolerance is involved.

## Environment

Intel Core Ultra 9 275HX, 24 cores (8 performance + 16 efficiency), 93 GB RAM, Ubuntu 24.04.
Single-threaded per run. Python 3.12, NumPy 2.x; Gurobi 12 and HiGHS 1.13.1 for the integer
programs. No GPU, QPU, annealer or quantum simulator was used at any stage.

## Files

    README.md
    PROOF.md              the optimality argument and the two checks
    birkhoff_proof.py     enumeration, Ryser cross-check, .lp export, exact n = 3 replication
    <instance>/README.md
    <instance>/<instance>_solution.json
    <instance>/<instance>_summary.csv
