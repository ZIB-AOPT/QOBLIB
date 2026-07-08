# Q-Bridge — Constraint-Preserving Swap Simulated Annealing (SwapSA)

Submission by the Q-Bridge Team (South Korea) — contact: liveplex@gmail.com

## Method
- Modeling: standard MIS QUBO, minimize `-sum(x) + 2 * sum_{(i,j) in E} x_i x_j`.
- Main solver: GPU-parallel simulated annealing (512 chains, geometric cooling,
  reheat rounds, greedy-descent polish). Quantum-inspired, classical hardware.
- Postprocessing: deterministic repair of any violated edge (remove the
  higher-degree endpoint) — feasibility of reported solutions is guaranteed.
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
