# Submission for mammalia-kangaroo-interactions

This directory contains the submission for the problem **aves-sparrow-social**.

## CSV Summary

| Field | Value |
|-------|-------|
| Problem | aves-sparrow-social |
| Submitter | Daniel Egger |
| Date | 15. Jan. 2025 |
|======||
| Reference | See https://github.com/eggerdj/independent_set_benchmarking |
|======||
| Best Objective Value | 4 |
| Optimality Bound | N/A |
|======||
| Modeling Approach | QUBO |
| # Decision Variables | 17 |
| # Binary Variables | 17 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 108 |
| Coefficients Type | contiuous |
| Coefficients Range | {0, 1} |
|======||
| Workflow | 1) The parameters β and γ of the depth-one QAOA and the Lagrange multiplier are optimized classically. 2) Samples are drawn from the QPU. 3) Samples from the QPU are classically post-processed. |
| Algorithm Type | Stochastic |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
|======||
| Hardware Specifications | ThinkPad laptop and IBM Quantum device ibm_fez |
|======||
| Total Runtime | 87 |
| CPU Runtime | 27 |
| GPU Runtime | N/A |
| QPU Runtime | 60 |
| Other HW Runtime | N/A |
|======||
| Remarks | Runtime is in seconds and QPU runtime includes payload compilation and execution. |