# Submission for ms_04_200_030

This directory contains the submission for the problem **ms_04_200_030**.

| Field | Value 1 |
| --- | --- |
| Problem | ms_04_200_030 |
| Submitter | ParityQC Team |
| Affiliation | Parity Quantum Computing GmbH |
| Date | 2026-07-28 |
| ====== |  |
| Reference | https://parityqc.com/products/parity-twine-optimizer |
| Best Objective Value | 3.0 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 30 |
| # Binary Variables | 30 |
| # Integer Variables | N/A |
| # Continuous Variables | N/A |
| # Non-Zero Coefficients | 465 |
| Coefficients Type | Integer |
| Coefficients Range | N/A - N/A |
| ====== |  |
| Workflow | Solved using Parity Twine Optimizer (version: 0.1.8). 1) The parameters β and γ of the depth-one QAOA are optimized classically. 2) Samples are drawn from the QPU. 3) Samples from the QPU are classically post-processed. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware |
| # Runs | 5 |
| # Feasible Runs | 0 |
| # Successful Runs | 0 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Classical: MacBook Pro (Apple M3) 8 GB RAM 8 cores, Quantum: ibm_boston with 100000 shots. |
| ====== |  |
| Total Runtime | 337.1682 |
| Time to Solution | 337.1682 |
| CPU Runtime | 308.1682 |
| GPU Runtime | N/A |
| QPU Runtime | 29.0 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | The Best Objective Value is the market split violation. Statistics for the Objective value across the runs: min: 3.0, median: 4.0, mean: 6.6, max: 18.0, std: 5.71314274283428.  |
