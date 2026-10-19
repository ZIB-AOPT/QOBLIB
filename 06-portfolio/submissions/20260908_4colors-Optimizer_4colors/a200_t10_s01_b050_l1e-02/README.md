# Submission for a200_t10_s01_b050_l1e-02

This directory contains the submission for the problem **a200_t10_s01_b050_l1e-02**.

| Field | Value 1 |
| --- | --- |
| Problem | a200_t10_s01_b050_l1e-02 |
| Submitter | Marcin Kaminski |
| Affiliation | 4colors Research |
| Date | 2026-09-08 |
| ====== |  |
| Reference | See README.md in this submission directory (4colors Optimizer) |
| Best Objective Value | -114070 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Exact chain over periods with the unit-count vector as state; equivalent to the reference model with its unit symmetry removed |
| # Decision Variables | N/A |
| # Binary Variables | N/A |
| # Integer Variables | N/A |
| # Continuous Variables | N/A |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | Integer |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | 4colors Optimizer: dynamic program over the count-space chain, exact where the state space is enumerable and a local search in the same space otherwise. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | N/A |
| Success Threshold | N/A |
| ====== |  |
| Hardware Specifications | Intel Core Ultra 9 275HX, 24 cores (8 performance + 16 efficiency), 93 GB RAM, Ubuntu 24.04 |
| ====== |  |
| Total Runtime | 15.314 |
| Time to Solution | 15.314 |
| CPU Runtime | 15.314 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Objective evaluated at the checker defaults: capital C = 10 (cash 1e6, unit 1e5), ub = 3, cs1 = 4, cs2 = 7. Classical result: no quantum resource was used. |
