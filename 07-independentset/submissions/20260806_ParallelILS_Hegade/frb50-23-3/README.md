# Submission for frb50-23-3

This directory contains the submission for the problem **frb50-23-3**.

| Field | Value 1 |
| --- | --- |
| Problem | frb50-23-3 |
| Submitter | Narendra N. Hegade |
| Affiliation | Kipu Quantum |
| Date | 2026-08-06 |
| ====== |  |
| Reference | [Andrade, Resende & Werneck, J. Heuristics 18:525-547 (2012)](https://doi.org/10.1007/s10732-012-9196-4) |
| Best Objective Value | 50 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | MIS QUBO (max sum x_v - 2 sum_{(u,v) in E} x_u x_v) |
| # Decision Variables | 1150 |
| # Binary Variables | 1150 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 82218 |
| Coefficients Type | integer |
| Coefficients Range | -1 to 2 |
| ====== |  |
| Workflow | Cooperative parallel iterated local search (classical, multi-core metaheuristic). |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | 9 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M5 Max (arm64, 48 GB RAM), 18 CPU cores; C++ solver, clang -O3 -march=native |
| ====== |  |
| Total Runtime | 120.0200 |
| Time to Solution | N/A |
| CPU Runtime | 120.0200 |
| GPU Runtime | 0.0 |
| QPU Runtime | 0.0 |
| Other HW Runtime | 0.0 |
| ====== |  |
| Remarks | Runtime is in seconds. |
