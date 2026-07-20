# Submission for c-fat200-1

This directory contains the submission for the problem **c-fat200-1**.

| Field | Value 1 |
| --- | --- |
| Problem | c-fat200-1 MIS |
| Submitter | Jeung Rac Lee (Qunova Computing, Inc.) |
| Date | 2026-07-08 |
| ====== |  |
| Reference |  |
| Best Objective Value | 17 |
| Optimality Bound | 18 |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 200 |
| # Binary Variables | 200 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 1734 |
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
| Total Runtime | 59.58 |
| CPU Runtime | 7.58 |
| GPU Runtime | 0 |
| QPU Runtime | 52.00 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Ansatz: H init; RZZ+RXX+RYY full connectivity entanglement layer; Ry variational rotation; approximation ratio=0.9444 (17/18); mean set size over 5 runs = 16.0 |
