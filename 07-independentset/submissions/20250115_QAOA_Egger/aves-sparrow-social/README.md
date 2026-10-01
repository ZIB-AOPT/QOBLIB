# Submission for aves-sparrow-social

This directory contains the submission for the problem **aves-sparrow-social**.

| Field | Value 1 |
| --- | --- |
| Problem | aves-sparrow-social |
| Submitter | Daniel Egger |
| Affiliation | IBM Quantum |
| Date | 2025-01-15 |
| ====== |  |
| Reference | See https://github.com/eggerdj/independent_set_benchmarking |
| Best Objective Value | 13 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 52 |
| # Binary Variables | 52 |
| # Integer Variables | N/A |
| # Continuous Variables | N/A |
| # Non-Zero Coefficients | 506 |
| Coefficients Type | Continuous |
| Coefficients Range | <0-1> |
| ====== |  |
| Workflow | 	1) The parameters β and γ of the depth-one QAOA and the Lagrange multiplier are optimized classically. 2) Samples are drawn from the QPU. 3) Samples from the QPU are classically post-processed. Therefore each run can provide multiple solutions. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | ThinkPad laptop and IBM Quantum device ibm_fez. |
| ====== |  |
| Total Runtime | 252 |
| Time to Solution | N/A |
| CPU Runtime | 192 |
| GPU Runtime | N/A |
| QPU Runtime | 60 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | 	Runtime is in seconds and QPU runtime includes payload compilation and execution. |
