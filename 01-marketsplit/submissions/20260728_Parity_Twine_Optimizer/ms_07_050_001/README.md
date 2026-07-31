# Submission for ms_07_050_001

This directory contains the submission for the problem **ms_07_050_001**.

| Field | Value 1 |
| --- | --- |
| Problem | ms_07_050_001 |
| Submitter | ParityQC Team |
| Affiliation | Parity Quantum Computing GmbH |
| Date | 2026-07-28 |
| ====== |  |
| Reference | https://parityqc.com/products/parity-twine-optimizer |
| Best Objective Value | 17.0 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 60 |
| # Binary Variables | 60 |
| # Integer Variables | N/A |
| # Continuous Variables | N/A |
| # Non-Zero Coefficients | 1831 |
| Coefficients Type | Integer |
| Coefficients Range | -386302.0 - 18940.0 |
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
| Total Runtime | 1525.9696000000001 |
| Time to Solution | 1525.9696000000001 |
| CPU Runtime | 1494.9696000000001 |
| GPU Runtime | N/A |
| QPU Runtime | 31.0 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | The Best Objective Value is the market split violation. Statistics for the Objective value across the runs: min: 17.0, median: 37.0, mean: 35.2, max: 62.0, std: 15.714961024450552.  |
