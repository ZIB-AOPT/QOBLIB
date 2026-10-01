# Submission for a003_t02_s02_b003_l1e-05

This directory contains the submission for the problem **a003_t02_s02_b003_l1e-05**.

| Field | Value 1 |
| --- | --- |
| Problem | a003_t02_s02_b003_l1e-05 |
| Submitter | Marcin Kaminski |
| Affiliation | 4colors Research |
| Date | 2026-09-08 |
| ====== |  |
| Reference | See README.md in this submission directory (4colors Optimizer) |
| Best Objective Value | -5378 |
| Optimality Bound | -5378 |
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
| Algorithm Type | Deterministic |
| Paradigm | Classical |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | N/A |
| Success Threshold | N/A |
| ====== |  |
| Hardware Specifications | Intel Core Ultra 9 275HX, 24 cores (8 performance + 16 efficiency), 93 GB RAM, Ubuntu 24.04 |
| ====== |  |
| Total Runtime | 0.000 |
| Time to Solution | 0.000 |
| CPU Runtime | 0.000 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Objective evaluated at the checker defaults: capital C = 10 (cash 1e6, unit 1e5), ub = 3, cs1 = 4, cs2 = 7. Proven optimal; reproduction code accompanies this submission. Classical result: no quantum resource was used. |
