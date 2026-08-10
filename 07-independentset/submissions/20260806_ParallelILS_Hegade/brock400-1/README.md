# Submission for brock400-1

This directory contains the submission for the problem **brock400-1**.

| Field | Value 1 |
| --- | --- |
| Problem | brock400-1 |
| Submitter | Narendra N. Hegade |
| Affiliation | Kipu Quantum |
| Date | 2026-08-06 |
| ====== |  |
| Reference | [Andrade, Resende & Werneck, J. Heuristics 18:525-547 (2012)](https://doi.org/10.1007/s10732-012-9196-4) |
| Best Objective Value | 27 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | MIS QUBO (max sum x_v - 2 sum_{(u,v) in E} x_u x_v) |
| # Decision Variables | 400 |
| # Binary Variables | 400 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 20477 |
| Coefficients Type | integer |
| Coefficients Range | -1 to 2 |
| ====== |  |
| Workflow | Cooperative parallel iterated local search (classical, multi-core metaheuristic). |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | 10 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M5 Max (arm64, 48 GB RAM), 18 CPU cores; C++ solver, clang -O3 -march=native |
| ====== |  |
| Total Runtime | 10.0100 |
| Time to Solution | N/A |
| CPU Runtime | 10.0100 |
| GPU Runtime | 0.0 |
| QPU Runtime | 0.0 |
| Other HW Runtime | 0.0 |
| ====== |  |
| Remarks | Runtime is in seconds. |
