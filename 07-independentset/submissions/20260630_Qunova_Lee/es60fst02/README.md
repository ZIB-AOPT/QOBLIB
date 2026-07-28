# Submission for es60fst02

This directory contains the submission for the problem **es60fst02**.

| Field | Value 1 |
| --- | --- |
| Problem | es60fst02 MIS |
| Submitter | Jeung Rac Lee |
| Affiliation | Qunova Computing, Inc. |
| Date | 2026-07-18 |
| ====== |  |
| Reference |  |
| Best Objective Value | 86 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 186 |
| # Binary Variables | 186 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 466 |
| Coefficients Type | Integer |
| Coefficients Range | [-1, 2] |
| ====== |  |
| Workflow | (1) The Independent Set problem is formulated as a binary optimization problem (QUBO);  (2) Initial solution is computed classically from the matrix’s structure as the initial “current best”; (3) A parameterized quantum circuit is sampled, and each bitstring is decoded as a variable index (O(log n) qubits); (4) A candidate re-assignment for the sampled variables are computed classically, and accept if the global objective is improved; (5) Repeat step 3-4 while updating circuit parameters with classical optimizer until convergence or for predefined number of iterations; |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 0 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | IBM ibm_fez/ibm_miami QPU; Intel Core i9-14900K (24 cores / 32 threads; max 6.0 GHz); no GPU |
| ====== |  |
| Total Runtime | 892.46 |
| Time to Solution | N/A |
| CPU Runtime | 122.14 |
| GPU Runtime | 0 |
| QPU Runtime | 770.32 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Ansatz: H init; RZZ+RXX+RYY full connectivity entanglement layer; Ry variational rotation; approximation ratio=0.9773 (86/88); mean set size over 5 runs = 84.2; # Successful Runs counts runs reaching the best-known optimal objective (from the repository solutions); Success Threshold epsilon=0. |
