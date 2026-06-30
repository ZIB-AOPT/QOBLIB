# Submission for es60fst01

This directory contains the submission for the problem **es60fst01**.

| Field | Value 1 |
| --- | --- |
| Problem | es60fst01 MIS |
| Submitter | Jeung Rac Lee (Qunova Computing, Inc.) |
| Date | 2026-06-30 |
| ====== |  |
| Reference |  |
| Best Objective Value | 58 |
| Optimality Bound | 60 |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 123 |
| # Binary Variables | 123 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 282 |
| Coefficients Type | Integer |
| Coefficients Range | [-1, 2] |
| ====== |  |
| Workflow | (1) The Independent Set problem is formulated as a binary optimization problem (QUBO);  (2) Initial solution is computed calssically from the matrix’s structure as the initial “current best”; (3) A parameterized quantum circuit is sampled, and each bitstring is decoded as a variable index (O(log n) qubits); (4) A candidate re-assignment for the sampled variables are computed classically, and accept if the global objective is improved; (5) Repeat step 3-4 while updating circuit parameters with classical optimizer until convergence or for predefined number of iterations; |
| Algorithm Type | Stochastic |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | N/A |
| ====== |  |
| Hardware Specifications | IBM ibm_marrakesh QPU; Intel Core i9-14900K (24 cores / 32 threads; max 6.0 GHz); no GPU |
| ====== |  |
| Total Runtime | 843.25 |
| CPU Runtime | 139.62 |
| GPU Runtime | 0 |
| QPU Runtime | 703.63 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Ansatz: H init; Heisenberg entanglement (RZZ+RXX+RYY) full connectivity; Ry variational rotation; approximation ratio=0.9667 (58/60) |
