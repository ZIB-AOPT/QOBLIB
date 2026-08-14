# Submission for p_hat1500-1

This directory contains the submission for the problem **p_hat1500-1**.

| Field | Value 1 |
| --- | --- |
| Problem | p_hat1500-1 |
| Submitter | Tim Bode |
| Affiliation | Forschungszentrum Jülich |
| Date | 2026-08-13 |
| ====== |  |
| Reference | https://github.com/Quicopt/Benchmarks |
| Best Objective Value | 11 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 1500 |
| # Binary Variables | 1500 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 840827 |
| Coefficients Type | Integer |
| Coefficients Range | [-1, 1] |
| ====== |  |
| Workflow | Build the QUBO from the graph instance, solve with Quicopt v0.1. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 20 |
| # Feasible Runs | 20 |
| # Successful Runs | 20 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | AMD EPYC-Rome, 1 core (single-threaded), 503 GB RAM, Ubuntu 24.04 |
| ====== |  |
| Total Runtime | 3.498 |
| Time to Solution | N/A |
| CPU Runtime | 3.498 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | QUBO: maximize sum_i y_i - sum_{(i,j) in E} y_i y_j (penalty lambda = 1); objective is the best set over all runs, runtimes are means over all runs. |
