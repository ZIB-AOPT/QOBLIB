# Submission for frb45-21-3

This directory contains the submission for the problem **frb45-21-3**.

| Field | Value 1 |
| --- | --- |
| Problem | frb45-21-3 |
| Submitter | Tim Bode |
| Affiliation | Forschungszentrum Jülich |
| Date | 2026-08-13 |
| ====== |  |
| Reference | https://github.com/Quicopt/Benchmarks |
| Best Objective Value | 43 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 945 |
| # Binary Variables | 945 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 59190 |
| Coefficients Type | Integer |
| Coefficients Range | [-1, 1] |
| ====== |  |
| Workflow | Build the QUBO from the graph instance, solve with Quicopt v0.1. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 20 |
| # Feasible Runs | 20 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | AMD EPYC-Rome, 1 core (single-threaded), 503 GB RAM, Ubuntu 24.04 |
| ====== |  |
| Total Runtime | 1.389 |
| Time to Solution | N/A |
| CPU Runtime | 1.389 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | QUBO: maximize sum_i y_i - sum_{(i,j) in E} y_i y_j (penalty lambda = 1); objective is the best set over all runs, runtimes are means over all runs. |
