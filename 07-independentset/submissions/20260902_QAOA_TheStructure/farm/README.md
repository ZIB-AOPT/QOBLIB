# Submission for farm

This directory contains the submission for the problem **farm**.

| Field | Value 1 |
| --- | --- |
| Problem | farm |
| Submitter | Max |
| Affiliation | The Structure |
| Date | 2026-09-01 |
| ====== |  |
| Reference | Farhi, E., Goldstone, J., & Gutmann, S. (2014). A Quantum Approximate Optimization Algorithm. arXiv:1411.4028. |
| Best Objective Value | 10 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 17 |
| # Binary Variables | 17 |
| # Integer Variables | N/A |
| # Continuous Variables | N/A |
| # Non-Zero Coefficients | 56 |
| Coefficients Type | Integer |
| Coefficients Range | [-2, 1] |
| ====== |  |
| Workflow | QAOA with COBYLA |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Simulator |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | 10 |
| Success Threshold | N/A |
| ====== |  |
| Hardware Specifications | AerSimulator |
| ====== |  |
| Total Runtime | AerSimulator s |
| Time to Solution | N/A |
| CPU Runtime | N/A |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | N/A |

| ====== | |
| QUBO Linear Penalty Coeff | 1 |
| QUBO Edge Constraint Coeff | -2 |

## Remarks

Objective formulated as maximization of the negated QUBO (canonical MIS formulation with linear penalty +1 per node, edge constraint -2 per violated edge, maximized).
