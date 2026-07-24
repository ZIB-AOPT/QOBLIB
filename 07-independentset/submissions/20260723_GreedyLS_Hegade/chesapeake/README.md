# Submission for chesapeake

This directory contains the submission for the problem **chesapeake**.

| Field | Value 1 |
| --- | --- |
| Problem | chesapeake |
| Submitter | Narendra N. Hegade |
| Affiliation | Kipu Quantum |
| Date | 2026-07-16 |
| ====== |  |
| Reference |  |
| Best Objective Value | 17 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | MIS QUBO (max sum x_v - 2 sum_{(u,v) in E} x_u x_v) |
| # Decision Variables | 39 |
| # Binary Variables | 39 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 209 |
| Coefficients Type | integer |
| Coefficients Range | -1 to 2 |
| ====== |  |
| Workflow | Random sampling of 4000 bitstrings + greedy local search |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | 10 |
| Success Threshold | 0.0 |
| ====== |  |
| Hardware Specifications | Apple M5 Max (arm64, 48 GB RAM), single CPU core; C++ solver, clang -O3 -march=native |
| ====== |  |
| Total Runtime | 0.007752 |
| Time to Solution | N/A |
| CPU Runtime | 0.007752 |
| GPU Runtime | 0.0 |
| QPU Runtime | 0.0 |
| Other HW Runtime | 0.0 |
| ====== |  |
| Remarks | Total Runtime in seconds. |
