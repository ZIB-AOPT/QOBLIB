# Q-Bridge — GPU-Parallel Simulated Annealing on the Penalty QUBO

Submission by the Q-Bridge Team (South Korea) — contact: liveplex@gmail.com

## Method
- Modeling: standard MIS QUBO, minimize `-sum(x) + 2 * sum_{(i,j) in E} x_i x_j`.
- Main solver: GPU-parallel simulated annealing (512 chains, geometric cooling,
  reheat rounds, greedy-descent polish). Quantum-inspired, classical hardware.
- Postprocessing: deterministic repair of any violated edge (remove the
  higher-degree endpoint) — feasibility of reported solutions is guaranteed.
  Note: constraints are handled via the penalty term during the anneal and are
  NOT enforced move-by-move; the repair step runs after the solve. (Our engine
  also has a constraint-preserving swap mode for assignment-structured problems
  with built-in exactly-one groups; that mode is not applicable to MIS and was
  not used here.)
- Stochastic protocol: 5 seeded runs per instance (seeds 42-46); per-run and
  aggregate statistics are reported unfiltered in each summary CSV.

## Results (5 runs each, 60 s budget per run)
| Instance | Proven optimum | Our best | Successful runs |
|---|---|---|---|
| chesapeake | 17 | 17 | 5/5 |
| aves-sparrow-social | 13 | 13 | 5/5 |
| C125-9 | 34 | 34 | 5/5 |
| brock200-2 | 12 | 12 | 5/5 |

## Hardware
Apple M5 Max (arm64, 64 GB), numpy CPU backend. The identical algorithm runs
on CuPy / NVIDIA RTX 5090; CPU numbers are reported here for reproducibility.

## Code availability
The engine is proprietary (commercial product). The algorithm is summarized
above and in the per-instance CSVs; we are happy to provide additional detail
or a review under NDA on request.

## Objective trajectory & TTS (added 2026-07-13, review follow-up)
Each instance directory now includes `<instance>_objective_time_series.json`
(list of 5 runs; each run a list of {Time, Incumbent} points recorded whenever
the incumbent improved). Incumbent is the penalty-QUBO objective (at feasible incumbents this equals minus the independent-set size, e.g. -34 for C125-9).
No optimality cutoff is used — the schedule always runs to completion; the
"Time to Solution" column is computed post-hoc from the trajectory as the first
time the final incumbent was reached (mean over the 5 runs).
