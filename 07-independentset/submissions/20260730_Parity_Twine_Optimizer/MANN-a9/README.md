# Submission for MANN-a9

This directory contains the submission for the problem **MANN-a9**.

| Field | Value 1 |
| --- | --- |
| Problem | MANN-a9 |
| Submitter | ParityQC Team |
| Affiliation | Parity Quantum Computing GmbH |
| Date | 2026-07-30 |
| ====== |  |
| Reference | https://parityqc.com/products/parity-twine-optimizer |
| Best Objective Value | 3 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 46 |
| # Binary Variables | 46 |
| # Integer Variables | N/A |
| # Continuous Variables | N/A |
| # Non-Zero Coefficients | 918 |
| Coefficients Type | Integer |
| Coefficients Range | N/A - N/A |
| ====== |  |
| Workflow | Solved using Parity Twine Optimizer (version: 0.1.8). 1) The parameters β and γ of the depth-one QAOA are optimized classically. 2) Samples are drawn from the QPU. 3) Samples from the QPU are classically post-processed. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Classical: MacBook Pro (Apple M3) 8 GB RAM 8 cores, Quantum: ibm_fez with 100000 shots. |
| ====== |  |
| Total Runtime | 807.4136 |
| Time to Solution | 807.4136 |
| CPU Runtime | 777.4136 |
| GPU Runtime | N/A |
| QPU Runtime | 30.0 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | The Best Objective Value is the size of the maximal independent set found.Statistics for the Objective value across the runs: max: 3, median: 3.0, mean: 3.0, min: 3, std: 0.0. Times are in seconds. |
