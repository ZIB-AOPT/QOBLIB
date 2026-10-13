# Submission for topology_35_5

This directory contains the submission for the problem **topology_35_5**.

| Field | Value 1 |
| --- | --- |
| Problem | topology_35_5 |
| Submitter | Marcin Kaminski |
| Affiliation | 4colors Research |
| Date | 2026-09-08 |
| ====== |  |
| Reference | See README.md in this submission directory (4colors Optimizer) |
| Best Objective Value | 3 |
| Optimality Bound | 3 |
| ====== |  |
| Modeling Approach | Direct graph representation; decision problem 'diameter <= k' |
| # Decision Variables | 595 |
| # Binary Variables | 595 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 595 |
| Coefficients Type | Binary |
| Coefficients Range | [0, 1] |
| ====== |  |
| Workflow | 4colors Optimizer: simulated annealing on a target-diameter objective, with exact all-pairs distance evaluation. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 8 |
| # Feasible Runs | 8 |
| # Successful Runs | 8 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Intel Core Ultra 9 275HX, 24 cores (8 performance + 16 efficiency), 93 GB RAM, Ubuntu 24.04 |
| ====== |  |
| Total Runtime | 0.174 |
| Time to Solution | 0.022 |
| CPU Runtime | 0.174 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Optimal by the counting (Moore) bound: a graph of maximum degree d and diameter k has at most 1 + d*sum_{i<k}(d-1)^i vertices. Classical result: no quantum resource was used. |
