# 4colors Optimizer -- 08-network

Marcin Kaminski, 4colors Research. 2026-09-08. Apache-2.0.

Improved solutions for eleven of the fourteen open instances of the network design problem, by
between 0.65% and 5.03%. No optimality is claimed; `Optimality Bound` is `N/A` throughout.

| instance | previous | this submission | reduction |
|---|---:|---:|---:|
| `network13` | 304,116 | 302,152 | 0.65% |
| `network14` | 350,173 | 345,632 | 1.30% |
| `network15` | 383,000 | 371,385 | 3.03% |
| `network16` | 409,067 | 405,385 | 0.90% |
| `network17` | 460,182 | 441,926 | 3.97% |
| `network18` | 481,950 | 477,066 | 1.01% |
| `network19` | 514,625 | 496,910 | 3.44% |
| `network20` | 548,536 | 520,929 | 5.03% |
| `network21` | 593,000 | 575,271 | 2.99% |
| `network22` | 647,594 | 616,578 | 4.79% |
| `network23` | 686,453 | 656,030 | 4.43% |

## Method

The problem separates into a discrete choice of topology and a routing subproblem. The solver
searches over 2-regular digraphs, represented so that the degree conditions hold by construction
rather than as constraints, and scores each candidate by solving the associated min-congestion
linear program. Candidate generation is an iterated local search seeded from the reference
incumbent.

The final configuration is re-solved with integrality restored on the flow variables, so the
submitted routing is integral.

## Verification

Each submitted solution was checked with `08-network/check` built from this tree, and independently
with a second implementation of the objective written from the problem statement rather than from
the checker source.

## Environment

Intel Core Ultra 9 275HX, 24 cores (8 performance + 16 efficiency), 93 GB RAM, Ubuntu 24.04.
Single-threaded per run. Python 3.12, HiGHS 1.13.1 for the linear programs.
No GPU, QPU, annealer or quantum simulator was used at any stage.

## Files

    README.md
    <instance>/<instance>_solution.sol
    <instance>/<instance>_summary.csv
