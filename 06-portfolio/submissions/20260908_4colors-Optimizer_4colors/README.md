# 4colors Optimizer - 06-portfolio

Marcin Kaminski, 4colors Research. 2026-09-08. Apache-2.0.

232 solutions: 8 improvements on the a050 family, 96 first values that are also proven optimal, and
128 further first values that are heuristic.

| | instances |
|---|---:|
| Lower than the recorded value | 8 (a050) |
| First value, proven optimal | 96 (a003, a004, a005) |
| First value, heuristic | 128 (a200, a400) |
| **total** | **232** |

## Method

The reference model reduces exactly to a chain over periods with state given by the unit-count
vector. The shipped formulation carries three interchangeable unit copies per (asset, direction,
period), producing a symmetric block per group; working in counts removes the symmetry without
changing the feasible set. For the small budgets the chain is solved exactly by dynamic programming.
Where the budget puts the state space beyond exhaustive treatment, a local search in the same space
is used, warm-started from the reference solution.

## Optimality

Asserted on the 96 first values, where the dynamic program enumerates every feasible position plan
and therefore returns the global optimum of the reference model.

`portfolio_dp.cpp` is the implementation: standalone C++17, no external dependencies, sharing no code
with our heuristics.

    g++ -O2 -std=c++17 -o portfolio_dp portfolio_dp.cpp
    ./portfolio_dp <instance-dir> --budget B --lambda L [--out FILE]
    ./portfolio_dp <instance-dir> --lambda L --evaluate <solution>

It was validated three ways before the claim was made: its objective reproduces `check_portfolio`
on all 296 solutions produced; its optimum agrees with exhaustive enumeration over all plans on the
96 small instances; and the plans it emits are accepted by `check_portfolio` at the stated objective.

## Parameters

All objectives are evaluated at the checker defaults: capital C = 10 (cash 1e6, unit 1e5), ub = 3,
cs1 = 4, cs2 = 7. This is stated explicitly because `instances/manifest.json` records the budget and
lambda per instance but not the cash and unit values, so the same solution scores differently under
a different capital.

## Instance keys

Directory names, the `Problem` column and the solution filenames all use the canonical instance key
-- no `po_` prefix, lambda exponent zero-padded, e.g. `a050_t10_orig_b020_l1e-02`. That is the form
`misc/ci/update_bkv.py` derives from the CSV before it looks for the solution file.

## Verification

All 232 solutions were checked with `06-portfolio/check` built from this tree; each was accepted and
returned exactly the objective recorded in its summary CSV.

## Environment

Intel Core Ultra 9 275HX, 24 cores (8 performance + 16 efficiency), 93 GB RAM, Ubuntu 24.04.
Single-threaded per instance; g++ 13, `-O2 -std=c++17`.
No GPU, QPU, annealer or quantum simulator was used at any stage.

## Files

    README.md
    portfolio_dp.cpp      standalone exact dynamic program
    <instance>/README.md
    <instance>/<instance>_solution.sol
    <instance>/<instance>_summary.csv
