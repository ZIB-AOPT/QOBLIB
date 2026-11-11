# Submission for XSH-n20-k4-06

This directory contains the submission for the problem **XSH-n20-k4-06**.

| Field | Value 1 |
| --- | --- |
| Problem | XSH-n20-k4-06 |
| Submitter | Vuong Kha Anh Son |
| Affiliation | Independent Researcher |
| Date | 2026-10-17 |
| ====== |  |
| Reference | Code: https://github.com/vkas0812-sys/qoblib-routing-exact-sqa |
| Best Objective Value | 690 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Tight-Capacity Subspace QUBO / Hypergraph Simulated Quantum Annealing (P=16 Trotter replicas) |
| # Decision Variables | 536 |
| # Binary Variables | 536 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 3716 |
| Coefficients Type | integer |
| Coefficients Range | 1 - 251 |
| ====== |  |
| Workflow | Pre-processing: project CVRP onto the demand-tight subspace (sum_{i in S} d_i = Q) and build the multi-scale 2-route and 3-route hypergraph transition neighborhoods. Main optimization: Simulated Quantum Annealing (Path-Integral Monte Carlo) with P=16 Trotter replicas, transverse field schedule Gamma(t) from 35.0 to 0.175 over 1000 sweeps at effective temperature T = 6.0, ferromagnetic Trotter coupling J_perp(t) = -0.5*T*ln(tanh(Gamma/(P*T))), and multi-scale 2-route, 3-route, and 4-route quantum tunneling moves. Post-processing: select lowest-energy Trotter replica. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 4 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M4 (10 cores); 16 GB unified RAM; macOS; AppleClang 21.0.0 (-O3 -std=c++17), single-thread execution |
| ====== |  |
| Total Runtime | 0.019436 |
| Time to Solution | 0.019040 |
| CPU Runtime | 0.019436 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | SQA-Subspace (P=16 Trotter slices, 5 independent runs of 1000 sweeps). Best objective across 5 runs = 690 (gap to proven optimal 690: 0.00%). Objective time series recorded in XSH-n20-k4-06_objective_time_series.json.gz. |
