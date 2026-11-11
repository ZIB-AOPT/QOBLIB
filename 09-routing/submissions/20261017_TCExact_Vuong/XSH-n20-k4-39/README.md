# Submission for XSH-n20-k4-39

This directory contains the submission for the problem **XSH-n20-k4-39**.

| Field | Value 1 |
| --- | --- |
| Problem | XSH-n20-k4-39 |
| Submitter | Vuong Kha Anh Son |
| Affiliation | Independent Researcher |
| Date | 2026-10-17 |
| ====== |  |
| Reference | Code: https://github.com/vkas0812-sys/qoblib-routing-exact-sqa |
| Best Objective Value | 717 |
| Optimality Bound | 717 |
| ====== |  |
| Modeling Approach | Tight-Capacity Set Partitioning (Exact Cover over demand-tight subsets sum(d_i) = Q with Held-Karp TSP costs) |
| # Decision Variables | 595 |
| # Binary Variables | 595 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 4400 |
| Coefficients Type | integer |
| Coefficients Range | 1 - 317 |
| ====== |  |
| Workflow | Pre-processing: parse CVRPLIB instance and compute EUC_2D rounded integer distance matrix; exploit 100% tight capacity (sum_{i=1}^n d_i = k*Q) via subset-sum DFS to enumerate all single-vehicle subsets S with sum_{i in S} d_i = Q and compute exact optimal route costs via bitwise Held-Karp dynamic programming. Main optimization: TC-Exact deterministic bitwise exact-cover search with lowest-set-bit (__builtin_ctz) symmetry breaking across the 4 vehicles and O(1) complement mask lookup for the 4th vehicle. Post-processing: reconstruct optimal customer sequences via Held-Karp parent pointers. |
| Algorithm Type | Deterministic |
| Paradigm | Classical |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M4 (10 cores); 16 GB unified RAM; macOS; AppleClang 21.0.0 (-O3 -std=c++17), single-thread execution |
| ====== |  |
| Total Runtime | 0.003448 |
| Time to Solution | 0.003435 |
| CPU Runtime | 0.003448 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | TC-Exact enumerates all 595 capacity-tight single-vehicle subsets (sum(d_i) = 234) and all 2885 feasible 4-vehicle partitions, proving global optimality at Cost = 717 (second-best partition cost = 718, spectral gap = 1). |
