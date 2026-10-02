# Submission for ITC2021_Early_14

This directory contains the submission for the problem **ITC2021_Early_14**.

| Field | Value 1 |
| --- | --- |
| Problem | ITC2021_Early_14 |
| Submitter | Kenji Kanamori |
| Affiliation | Independent Researcher |
| Date | 2026-09-11 |
| ====== |  |
| Reference | README.md in this submission package |
| Best Objective Value | 2569 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | RobinX match-slot encoding with D4 hierarchical 32-qubit shared-skeleton decomposition |
| # Decision Variables | 14440 |
| # Binary Variables | 14440 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | Integer |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | Parsing -> D4 shards -> Aer measurement -> Universal Joint -> Kenji R5 estimator -> consensus decoder -> validator |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Simulator |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Intel Core Ultra 5 225U CPU; 15.46 GiB RAM; Windows 11; CPU simulation |
| ====== |  |
| Total Runtime | 69.124672 |
| Time to Solution | 69.124672 |
| CPU Runtime | 69.124672 |
| GPU Runtime | N/A |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | 5/5 hard-feasible official RobinX validation; objectives 3139,2569,2571,3218,3028; best run 2 submitted; 38 shards; no classical repair |