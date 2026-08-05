# Submission for aves-sparrow-social

This directory contains the submission for the problem **aves-sparrow-social**.

| Field | Value 1 |
| --- | --- |
| Problem | aves-sparrow-social |
| Submitter | ParityQC Team |
| Affiliation | Parity Quantum Computing GmbH |
| Date | 2026-07-30 |
| ====== |  |
| Reference | https://parityqc.com/products/parity-twine-optimizer |
| Best Objective Value | 13 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO with penalty (n / d) * log(d) where n is the number of nodes and d the average degree of the graph. |
| # Decision Variables | 53 |
| # Binary Variables | 53 |
| # Integer Variables | N/A |
| # Continuous Variables | N/A |
| # Non-Zero Coefficients | 507 |
| Coefficients Type | float |
| Coefficients Range | -1.0 - 8.788805588461589 |
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
| Total Runtime | 725.8394 |
| Time to Solution | 725.8394 |
| CPU Runtime | 695.4394 |
| GPU Runtime | N/A |
| QPU Runtime | 30.4 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | The Best Objective Value is the size of the maximal independent set found.Statistics for the Objective value across the runs: max: 13, median: 13.0, mean: 13.0, min: 13, std: 0.0. Times are in seconds. |
