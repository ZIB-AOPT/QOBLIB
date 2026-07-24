# Submission for gen200_p0-9_44

This directory contains the submission for the problem **gen200_p0-9_44**.

| Field | Value 1 |
| --- | --- |
| Problem | gen200_p0-9_44 |
| Submitter | Narendra N. Hegade |
| Affiliation | Kipu Quantum |
| Date | 2026-07-16 |
| ====== |  |
| Reference |  |
| Best Objective Value | 44 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | MIS QUBO (max sum x_v - 2 sum_{(u,v) in E} x_u x_v) |
| # Decision Variables | 200 |
| # Binary Variables | 200 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 2190 |
| Coefficients Type | integer |
| Coefficients Range | -1 to 2 |
| ====== |  |
| Workflow | Random sampling of bitstrings + greedy local search ((1,2)-swaps, parallel restarts) |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | 10 |
| Success Threshold | 0.0 |
| ====== |  |
| Hardware Specifications | Apple M5 Max (arm64, 18 cores / 48 GB RAM), 8 cores for parallel restart streams; C++ solver, clang -O3 -march=native |
| ====== |  |
| Total Runtime | 0.515464 |
| Time to Solution | N/A |
| CPU Runtime | 0.515464 |
| GPU Runtime | 0.0 |
| QPU Runtime | 0.0 |
| Other HW Runtime | 0.0 |
| ====== |  |
| Remarks | Total Runtime in seconds. |
