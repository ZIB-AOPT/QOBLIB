# Submission for frb59-26-2

This directory contains the submission for the problem **frb59-26-2**.

| Field | Value 1 |
| --- | --- |
| Problem | frb59-26-2 |
| Submitter | Tim Bode |
| Affiliation | Forschungszentrum Jülich |
| Date | 2026-08-13 |
| ====== |  |
| Reference | https://github.com/Quicopt/Benchmarks |
| Best Objective Value | 55 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 1534 |
| # Binary Variables | 1534 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 127697 |
| Coefficients Type | Integer |
| Coefficients Range | [-1, 1] |
| ====== |  |
| Workflow | Build the QUBO from the graph instance, solve with Quicopt v0.1. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 20 |
| # Feasible Runs | 20 |
| # Successful Runs | 2 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | AMD EPYC-Rome, 1 core (single-threaded), 503 GB RAM, Ubuntu 24.04 |
| ====== |  |
| Total Runtime | 3.313 |
| Time to Solution | N/A |
| CPU Runtime | 3.313 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | QUBO: maximize sum_i y_i - sum_{(i,j) in E} y_i y_j (penalty lambda = 1); objective is the best set over all runs, runtimes are means over all runs. |
