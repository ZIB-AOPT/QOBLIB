# Submission for frb100-40

This directory contains the submission for the problem **frb100-40**.

| Field | Value 1 |
| --- | --- |
| Problem | frb100-40 |
| Submitter | Shivaram Subramanian |
| Affiliation | IBM Research |
| Date | 2026-09-08 |
| ====== |  |
| Reference | https://github.com/subshiva/quantum-mis |
| Best Objective Value | 95 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Binary linear: max sum x_v s.t. x_u + x_v <= 1 for (u,v) in E; LP relaxation with dynamically generated clique inequalities |
| # Decision Variables | 4000 |
| # Binary Variables | 4000 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 1149548 |
| Coefficients Type | integer |
| Coefficients Range | 1 / 1 |
| ====== |  |
| Workflow | Column-and-cut generation: (1) graph partitioning into blocks <= 100 nodes; (2) master LP (set packing) solved with CPLEX; (3) pricing via VQE/QAOA simulation (Qiskit Aer MPS backend) on blocks up to 100 qubits; (4) separation via clique cuts using same quantum pipeline; (5) primal heuristics: genetic algorithm + greedy augmentation |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Simulator |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Intel Core i7-13850HX (14 cores / 28 threads), 32 GB DDR5 RAM, Ubuntu 24.04 (WSL2) |
| ====== |  |
| Total Runtime | 6732.7 |
| Time to Solution | 6732.7 |
| CPU Runtime | 6732.7 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Runtime is in seconds. Single run. VQE (EfficientSU2 depth 4, SPSA optimizer) and analytical QAOA (depth <= 4) simulated via Qiskit Aer MPS backend on blocks up to 100 qubits. |
