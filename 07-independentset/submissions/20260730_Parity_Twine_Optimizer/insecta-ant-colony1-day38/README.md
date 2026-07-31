# Submission for insecta-ant-colony1-day38

This directory contains the submission for the problem **insecta-ant-colony1-day38**.

| Field | Value 1 |
| --- | --- |
| Problem | insecta-ant-colony1-day38 |
| Submitter | ParityQC Team |
| Affiliation | Parity Quantum Computing GmbH |
| Date | 2026-07-30 |
| ====== |  |
| Reference | https://parityqc.com/products/parity-twine-optimizer |
| Best Objective Value | 6 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO with penalty (n / d) * log(d) where n is the number of nodes and d the average degree of the graph. |
| # Decision Variables | 57 |
| # Binary Variables | 57 |
| # Integer Variables | N/A |
| # Continuous Variables | N/A |
| # Non-Zero Coefficients | 1134 |
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
| Total Runtime | 887.9112 |
| Time to Solution | 887.9112 |
| CPU Runtime | 857.9112 |
| GPU Runtime | N/A |
| QPU Runtime | 30.0 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | The Best Objective Value is the size of the maximal independent set found.Statistics for the Objective value across the runs: max: 6, median: 6.0, mean: 6.0, min: 6, std: 0.0. Times are in seconds. |
