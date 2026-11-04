# 4colors Optimizer - 04-steiner

Marcin Kaminski, 4colors Research. 2026-09-08. Apache-2.0.

149 solutions for the node-disjoint Steiner tree packing problem: 147 instances that had no
recorded value, and 2 below the recorded one. No optimality is claimed; `Optimality Bound` is `N/A`
throughout.

| | instances |
|---|---:|
| First value (no previous entry) | 147 |
| Below the recorded value | 2 |

## The two improvements

`stp_s070_l4_t6_h0_rs97531` improves from 375 to 374, reached once in 19 runs.

`stp_s030_l3_t5_h1_rs24098` improves from 476 to 475, reached in 10 of 45 runs. This row is currently recorded as `optimal` at
476, and the packing submitted here is accepted by `check_steiner` at 475, so the recorded value
merits review. The observation does not depend on this particular packing: any packing the checker
accepts at cost C yields a feasible point of the shipped rooted ILP with objective at most C,
because roots appear as `terms.dat` entries in all 190 instances, so each net's subgraph can be
oriented away from its own root.

Merging replaces `solutions/stp_s030_l3_t5_h1_rs24098.opt.sol` with a `.bst.sol` and records the row
as `best known`, since this submission asserts no bound of its own.

## Method

Negotiated-congestion routing, followed by rip-up and reroute, local search and multistart. The step
responsible for the improvements replaces the approximate per-net tree construction with an exact
one on a restricted subgraph, seeded with the approximate tree so the result can never be worse.

Runs are independent and differ only in seed; per-instance counts are in the summary CSVs.

## Verification

Every submitted packing was checked with `04-steiner/check` built from this tree.

## Environment

Intel Core Ultra 9 275HX, 24 cores (8 performance + 16 efficiency), 93 GB RAM, Ubuntu 24.04.
Single-threaded per run; g++ 13, `-O3 -march=native`.
No GPU, QPU, annealer or quantum simulator was used at any stage.

## Files

    README.md
    <instance>/<instance>_solution.sol
    <instance>/<instance>_summary.csv
