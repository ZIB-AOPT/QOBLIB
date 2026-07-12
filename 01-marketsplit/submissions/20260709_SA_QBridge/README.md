# Q-Bridge — GPU-Parallel SA with Persistency Preprocessing

Submission by the Q-Bridge Team (South Korea) — contact: liveplex@gmail.com

## Method
- Modeling: penalty QUBO `sum_i (A_i . x - b_i)^2`; objective 0 = exact
  solution (all Ax = b satisfied).
- Preprocessing: first-order persistency (roof-duality style) variable fixing.
- Main solver: GPU-parallel simulated annealing (512 chains, 20000 sweeps x 20
  reheat rounds). Quantum-inspired, classical hardware.
- Stochastic protocol: 5 seeded runs per instance (seeds 42-46), residual
  violations reported unfiltered.

## Results (5 runs each, 60 s budget per run)
| Instance | Exact runs (violation 0) | Mean runtime |
|---|---|---|
| ms_03_050_002 | 5/5 | 4.4 s |
| ms_03_050_005 | 5/5 | 4.3 s |
| ms_03_100_001 | 5/5 | 4.3 s |
| ms_03_100_012 | 5/5 | 4.3 s |

## Hardware
Apple M5 Max (arm64, 64 GB), numpy CPU backend (identical algorithm runs on
CuPy / NVIDIA RTX 5090).

## Code availability
Proprietary engine — algorithm summarized above; review under NDA on request.

## Objective trajectory & TTS (added 2026-07-13, review follow-up)
Each instance directory now includes `<instance>_objective_time_series.json`
(list of 5 runs; each run a list of {Time, Incumbent} points recorded whenever
the incumbent improved). Incumbent is the penalty-QUBO objective sum_i (A_i.x - b_i)^2 (0 = exact solution).
No optimality cutoff is used — the schedule always runs to completion; the
"Time to Solution" column is computed post-hoc from the trajectory as the first
time the final incumbent was reached (mean over the 5 runs).
