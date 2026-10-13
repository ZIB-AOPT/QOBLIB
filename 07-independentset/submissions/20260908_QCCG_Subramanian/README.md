# Quantum Column-and-Cut Generation (QCCG) for Maximum Independent Set

**Submitter:** Shivaram Subramanian -- IBM Research   **Date:** 2026-09-08

A quantum-simulator submission covering 12 `07-independentset` instances using
**quantum column-and-cut generation**, a hybrid framework where pricing and
separation subproblems are solved via simulated VQE and QAOA circuits.
Each instance is run once. All runtimes are wall-clock seconds.
Every reported solution is a verified independent set.

**Hardware:** Intel Core i7-13850HX (14 cores / 28 threads), 32 GB DDR5 RAM, Ubuntu 24.04 (WSL2)

## Algorithm

1. **Graph partitioning** into blocks of <= 100 nodes
2. **Master LP** -- set packing relaxation with dynamically generated
   clique inequalities, solved with CPLEX
3. **Pricing (Quantum)** -- MWIS subproblems solved via VQE circuit
   simulation (Qiskit Aer, MPS backend, EfficientSU2 ansatz, depth 4,
   SPSA optimizer) and analytical QAOA (depth p <= 4) with classical
   parameter optimization, on blocks up to 100 qubits
4. **Separation (Quantum)** -- clique cut generation via MWIS on the
   complement graph using the same quantum simulation pipeline
5. **Primal heuristics** -- genetic algorithm, exact neighborhood repair,
   greedy augmentation to obtain integer feasible solutions

## Results

| Instance | Nodes | IS Size | Runtime (s) |
| :------- | ----: | ------: | ----------: |
| C4000-5 | 4000 | 17 | 10677.1 |
| brock400-1 | 400 | 27 | 3484.3 |
| brock800-1 | 800 | 23 | 6429.9 |
| frb100-40 | 4000 | 95 | 6732.7 |
| frb45-21-3 | 945 | 44 | 1580.9 |
| frb50-23-3 | 1150 | 49 | 2166.5 |
| frb53-24-1 | 1272 | 52 | 1969.0 |
| frb59-26-2 | 1534 | 57 | 2160.6 |
| keller6 | 3361 | 59 | 6874.5 |
| socfb-trinity100 | 2613 | 499 | 9044.0 |
| sorrell4 | 2048 | 24 | 5496.0 |
| sorrell7 | 2048 | 198 | 6824.3 |

## Reference

https://github.com/subshiva/quantum-mis
