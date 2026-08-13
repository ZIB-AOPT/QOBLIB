# BF-DCQO submissions for Maximum Independent Set

**Submitter:** Narendra N. Hegade — Kipu Quantum   **Date:** 2026-07-30

Hybrid quantum-classical submissions for the `07-independentset` problem class, produced with the HSQC method (Kipu Quantum) built on bias-field digitized counterdiabatic quantum optimization (BF-DCQO) algorithm. All circuits were executed on an IBM Heron R3 quantum processor (`ibm_aachen`); classical pre- and post-processing ran on a single CPU core. Each instance reaches the best-known objective on every run. Every reported solution is a verified independent set.

## Results

| Instance | Nodes | Objective | Best-known | Successful runs | QPU runtime (s) | Backend |
| :--- | ---: | ---: | ---: | :---: | ---: | :--- |
| johnson16-2-4 | 120 | 15 | 15 | 5/5 | 2.739 | ibm_aachen (Heron R3) |
| C125-9 | 125 | 34 | 34 | 5/5 | 2.728 | ibm_aachen (Heron R3) |
| sloane_1dc_128 | 128 | 16 | 16 | 5/5 | 1.964 | ibm_aachen (Heron R3) |
| sloane_1zc_128 | 128 | 18 | 18 | 10/10 | 2.213 | ibm_aachen (Heron R3) |
| es60fst02 | 186 | 88 | 88 | 5/5 | 2.477 | ibm_aachen (Heron R3) |
| es60fst04 | 162 | 78 | 78 | 5/5 | 2.374 | ibm_aachen (Heron R3) |

Each per-instance folder contains `README.md`, `<instance>_summary.csv`, and `<instance>_solution.sol` (1-indexed vertices).

## References

1. A. Gomez Cadavid, A. Dalal, A. Simen, E. Solano, N. N. Hegade, [*Bias-field digitized counterdiabatic quantum optimization*](https://arxiv.org/abs/2405.13898), Phys. Rev. Research 7, L022010 (2024).
2. P. Chandarana, A. Gomez Cadavid, S. V. Romero, et al., [*Runtime Quantum Advantage with Digital Quantum Optimization*](https://arxiv.org/abs/2505.08663) (2025).
3. P. Chandarana, A. Gomez Cadavid, E. Solano, T. Koch, S. Woerner, N. N. Hegade, [*The Quest for Quantum Advantage in Combinatorial Optimization: End-to-end Benchmarking of Quantum Solvers vs. Multi-core Classical Solvers*](https://arxiv.org/abs/2603.13607) (2026).
