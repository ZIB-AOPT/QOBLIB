# Submission for topology_30_6

This directory contains the submission for the problem **topology_30_6**.

| Field | Value 1 |
| --- | --- |
| Problem | topology_30_6 |
| Submitter | Marcin Kaminski |
| Affiliation | 4colors Research |
| Date | 2026-09-08 |
| ====== |  |
| Reference | See README.md in this submission directory (4colors Optimizer) |
| Best Objective Value | 2 |
| Optimality Bound | 2 |
| ====== |  |
| Modeling Approach | Direct graph representation; decision problem 'diameter <= k' |
| # Decision Variables | 435 |
| # Binary Variables | 435 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 435 |
| Coefficients Type | Binary |
| Coefficients Range | [0, 1] |
| ====== |  |
| Workflow | 4colors Optimizer: simulated annealing on a target-diameter objective, with exact all-pairs distance evaluation. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 8 |
| # Feasible Runs | 8 |
| # Successful Runs | 4 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Intel Core Ultra 9 275HX, 24 cores (8 performance + 16 efficiency), 93 GB RAM, Ubuntu 24.04 |
| ====== |  |
| Total Runtime | 121.268 |
| Time to Solution | 19.155 |
| CPU Runtime | 121.268 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Optimal by the counting (Moore) bound: a graph of maximum degree d and diameter k has at most 1 + d*sum_{i<k}(d-1)^i vertices. Classical result: no quantum resource was used. |
