# Submission for es60fst03

This directory contains the submission for the problem **es60fst03**.

| Field | Value 1 |
| --- | --- |
| Problem | es60fst03 |
| Submitter | Narendra N. Hegade |
| Affiliation | Kipu Quantum |
| Date | 2026-07-16 |
| ====== |  |
| Reference |  |
| Best Objective Value | 55 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | MIS QUBO (max sum x_v - 2 sum_{(u,v) in E} x_u x_v) |
| # Decision Variables | 113 |
| # Binary Variables | 113 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 255 |
| Coefficients Type | integer |
| Coefficients Range | -1 to 2 |
| ====== |  |
| Workflow | Random sampling of bitstrings + greedy local search ((1,2)-swaps, restarts) |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | 10 |
| Success Threshold | 0.0 |
| ====== |  |
| Hardware Specifications | Apple M5 Max (arm64, 48 GB RAM), single CPU core; C++ solver, clang -O3 -march=native |
| ====== |  |
| Total Runtime | 0.507989 |
| Time to Solution | N/A |
| CPU Runtime | 0.507989 |
| GPU Runtime | 0.0 |
| QPU Runtime | 0.0 |
| Other HW Runtime | 0.0 |
| ====== |  |
| Remarks | Total Runtime in seconds. |
