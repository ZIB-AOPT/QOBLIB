# Submission for ms_03_050_002

This directory contains the submission for the problem **ms_03_050_002**.

| Field | Value 1 |
| --- | --- |
| Problem | ms_03_050_002 |
| Submitter | Q-Bridge Team |
| Affiliation | Q-Bridge (South Korea) |
| Date | 9. Jul. 2026 |
| ====== |  |
| Reference | Proprietary engine (contact: liveplex@gmail.com); method summary in Remarks |
| Best Objective Value | 0.0 |
| Optimality Bound | 0.0 |
| ====== |  |
| Modeling Approach | Penalty QUBO |
| # Decision Variables | 20 |
| # Binary Variables | 20 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 210 |
| Coefficients Type | Integer |
| Coefficients Range | {-56477; 8790} |
| ====== |  |
| Workflow | Penalty QUBO sum_i (A_i.x - b_i)^2; first-order persistency preprocessing (roof-duality style variable fixing); GPU-parallel simulated annealing (512 chains, 20000 sweeps x 20 reheat rounds). |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M5 Max (arm64, 64GB), numpy CPU backend; identical algorithm runs on CuPy/RTX 5090 |
| ====== |  |
| Total Runtime | 4.4 |
| Time to Solution | 4.4 |
| CPU Runtime | 4.4 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Residual violations over seeds [42, 43, 44, 45, 46]: [0, 0, 0, 0, 0] (0 = exact solution, all Ax=b satisfied). Feasible run = exact solution. Quantum-inspired swap SA with persistency preprocessing (0 vars fixed). |
