# Submission for XSH-n20-k4-37

This directory contains the submission for the problem **XSH-n20-k4-37**.

| Field | Value 1 | Value 2 |
| --- | --- | --- |
| Problem | XSH-n20-k4-37 | XSH-n20-k4-37 |
| Submitter | Vuong Kha Anh Son | Vuong Kha Anh Son |
| Affiliation | Independent Researcher | Independent Researcher |
| Date | 2026-10-17 | 2026-10-17 |
| ====== |  |  |
| Reference | Code: https://github.com/vkas0812-sys/qoblib-routing-exact-sqa | Code: https://github.com/vkas0812-sys/qoblib-routing-exact-sqa |
| Best Objective Value | 650 | 650 |
| Optimality Bound | 650 | N/A |
| ====== |  |  |
| Modeling Approach | Tight-Capacity Set Partitioning (Exact Cover over demand-tight subsets sum(d_i) = Q with Held-Karp TSP costs) | Tight-Capacity Subspace QUBO / Hypergraph Simulated Quantum Annealing (P=16 Trotter replicas) |
| # Decision Variables | 475 | 475 |
| # Binary Variables | 475 | 475 |
| # Integer Variables | 0 | 0 |
| # Continuous Variables | 0 | 0 |
| # Non-Zero Coefficients | 3307 | 3307 |
| Coefficients Type | integer | integer |
| Coefficients Range | 1 - 306 | 1 - 306 |
| ====== |  |  |
| Workflow | Pre-processing: parse CVRPLIB instance and compute EUC_2D rounded integer distance matrix; exploit 100% tight capacity (sum_{i=1}^n d_i = k*Q) via subset-sum DFS to enumerate all single-vehicle subsets S with sum_{i in S} d_i = Q and compute exact optimal route costs via bitwise Held-Karp dynamic programming. Main optimization: TC-Exact deterministic bitwise exact-cover search with lowest-set-bit (__builtin_ctz) symmetry breaking across the 4 vehicles and O(1) complement mask lookup for the 4th vehicle. Post-processing: reconstruct optimal customer sequences via Held-Karp parent pointers. | Pre-processing: project CVRP onto the demand-tight subspace (sum_{i in S} d_i = Q) and build the multi-scale 2-route and 3-route hypergraph transition neighborhoods. Main optimization: Simulated Quantum Annealing (Path-Integral Monte Carlo) with P=16 Trotter replicas, transverse field schedule Gamma(t) from 35.0 to 0.175 over 1000 sweeps at effective temperature T = 6.0, ferromagnetic Trotter coupling J_perp(t) = -0.5*T*ln(tanh(Gamma/(P*T))), and multi-scale 2-route, 3-route, and 4-route quantum tunneling moves. Post-processing: select lowest-energy Trotter replica. |
| Algorithm Type | Deterministic | Stochastic |
| Paradigm | Classical | Classical |
| # Runs | 1 | 5 |
| # Feasible Runs | 1 | 5 |
| # Successful Runs | 1 | 5 |
| Success Threshold | 0 | 0 |
| ====== |  |  |
| Hardware Specifications | Apple M4 (10 cores); 16 GB unified RAM; macOS; AppleClang 21.0.0 (-O3 -std=c++17), single-thread execution | Apple M4 (10 cores); 16 GB unified RAM; macOS; AppleClang 21.0.0 (-O3 -std=c++17), single-thread execution |
| ====== |  |  |
| Total Runtime | 0.001535 | 0.011312 |
| Time to Solution | 0.001498 | 0.010904 |
| CPU Runtime | 0.001535 | 0.011312 |
| GPU Runtime | 0 | 0 |
| QPU Runtime | 0 | 0 |
| Other HW Runtime | 0 | 0 |
| ====== |  |  |
| Remarks | TC-Exact enumerates all 475 capacity-tight single-vehicle subsets (sum(d_i) = 245) and all 2800 feasible 4-vehicle partitions, proving global optimality at Cost = 650 (second-best partition cost = 655, spectral gap = 5). | SQA-Subspace (P=16 Trotter slices, 5 independent runs of 1000 sweeps). Best objective across 5 runs = 650 (gap to proven optimal 650: 0.00%). Objective time series recorded in XSH-n20-k4-37_objective_time_series.json.gz. |
