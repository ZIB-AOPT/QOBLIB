# Submission for es60fst03

This directory contains the submission for the problem **es60fst03**.

| Field | Value 1 |
| --- | --- |
| Problem | es60fst03 MIS |
| Submitter | Jeung Rac Lee (Qunova Computing, Inc.) |
| Date | 2026-07-08 |
| ====== |  |
| Reference |  |
| Best Objective Value | 55 |
| Optimality Bound | 55 |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 113 |
| # Binary Variables | 113 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 255 |
| Coefficients Type | Integer |
| Coefficients Range | [-1, 2] |
| ====== |  |
| Workflow | (1) The Independent Set problem is formulated as a binary optimization problem (QUBO);  (2) Initial solution is computed calssically from the matrix’s structure as the initial “current best”; (3) A parameterized quantum circuit is sampled, and each bitstring is decoded as a variable index (O(log n) qubits); (4) A candidate re-assignment for the sampled variables are computed classically, and accept if the global objective is improved; (5) Repeat step 3-4 while updating circuit parameters with classical optimizer until convergence or for predefined number of iterations; |
| Algorithm Type | Stochastic |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | N/A |
| ====== |  |
| Hardware Specifications | IBM ibm_marrakesh/ibm_miami QPU; Intel Core i9-14900K (24 cores / 32 threads; max 6.0 GHz); no GPU |
| ====== |  |
| Total Runtime | 575.84 |
| CPU Runtime | 120.41 |
| GPU Runtime | 0 |
| QPU Runtime | 455.43 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Ansatz: H init; RZZ+RXX+RYY full connectivity entanglement layer; Ry variational rotation; approximation ratio=1.0000 (55/55); mean set size over 5 runs = 55.0 |
