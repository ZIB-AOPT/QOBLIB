# Submission for hamming10-4

This directory contains the submission for the problem **hamming10-4**.

| Field | Value 1 |
| --- | --- |
| Problem | hamming10-4 |
| Submitter | Tim Bode |
| Affiliation | Forschungszentrum Jülich |
| Date | 2026-08-13 |
| ====== |  |
| Reference | https://github.com/Quicopt/Benchmarks |
| Best Objective Value | 40 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 1024 |
| # Binary Variables | 1024 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 90624 |
| Coefficients Type | Integer |
| Coefficients Range | [-1, 1] |
| ====== |  |
| Workflow | Build the QUBO from the graph instance, solve with Quicopt v0.1. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 20 |
| # Feasible Runs | 20 |
| # Successful Runs | 11 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | AMD EPYC-Rome, 1 core (single-threaded), 503 GB RAM, Ubuntu 24.04 |
| ====== |  |
| Total Runtime | 1.434 |
| Time to Solution | N/A |
| CPU Runtime | 1.434 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | QUBO: maximize sum_i y_i - sum_{(i,j) in E} y_i y_j (penalty lambda = 1); objective is the best set over all runs, runtimes are means over all runs. |
