# Submission for frb100-40

| Field | Value |
| --- | --- |
| Problem | frb100-40 |
| Submitter | Narendra N. Hegade |
| Affiliation | Kipu Quantum |
| Date | 2026-07-24 |
| Reference |  |
| Best Objective Value | 95 |
| Optimality Bound | N/A |
| Modeling Approach | MIS QUBO (max sum x_v - 2 sum_{(u,v) in E} x_u x_v) |
| # Decision Variables | 4000 |
| # Binary Variables | 4000 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 576774 |
| Coefficients Type | integer |
| Coefficients Range | -1 to 2 |
| Workflow | Parallel iterated local search for maximum independent set (swap-based moves: vertex insertion, (1,2)-swap, plateau (1,1)-swap). |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | 10 |
| Success Threshold | N/A |
| Hardware Specifications | Apple M5 Max (arm64, 48 GB RAM), 18 CPU cores; C++ solver, clang -O3 -march=native |
| Total Runtime | 10.0700 |
| Time to Solution | N/A |
| CPU Runtime | 10.0700 |
| GPU Runtime | 0.0 |
| QPU Runtime | 0.0 |
| Other HW Runtime | 0.0 |
| Remarks | Runtime is in seconds. |
