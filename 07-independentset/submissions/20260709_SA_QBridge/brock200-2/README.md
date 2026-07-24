# Submission for brock200-2

This directory contains the submission for the problem **brock200-2**.

| Field | Value 1 |
| --- | --- |
| Problem | brock200-2 |
| Submitter | Q-Bridge Team |
| Affiliation | Q-Bridge (South Korea) |
| Date | 9. Jul. 2026 |
| ====== |  |
| Reference | Proprietary engine (contact: liveplex@gmail.com); method summary in Remarks |
| Best Objective Value | 12 |
| Optimality Bound | 12 |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 200 |
| # Binary Variables | 200 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 10224 |
| Coefficients Type | Integer |
| Coefficients Range | {-1; 2} |
| ====== |  |
| Workflow | QUBO (-sum(x) + 2*sum_{(i,j) in E} x_i x_j); GPU-parallel simulated annealing (512 chains, reheat rounds, greedy-descent polish); deterministic repair of violated edges (remove higher-degree endpoint) as postprocessing. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M5 Max (arm64, 64GB), numpy CPU backend; identical algorithm runs on CuPy/RTX 5090 |
| ====== |  |
| Total Runtime | 21.6 |
| Time to Solution | 21.6 |
| CPU Runtime | 21.6 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Independent set sizes over seeds [42, 43, 44, 45, 46]: [12, 12, 12, 12, 12] (proven optimum 12). Feasibility guaranteed by deterministic repair postprocessing. Quantum-inspired GPU-parallel SA (flip moves on the penalty QUBO). |
