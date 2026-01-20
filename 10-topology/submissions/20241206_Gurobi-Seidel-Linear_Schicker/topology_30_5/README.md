# Submission for topology_30_5

This directory contains the submission for the problem **topology_30_5**.

## CSV Summary

| Field | Value |
|-------|-------|
| Problem | topology_30_5 |
| Submitter | Maximilian Schicker |
| Date | 06. Dec. 2024 |
|======||
| Reference | See Models Directory (Seidel-Linear) using Gurobi 11.0.0 |
|======||
| Best Objective Value | 3.0 |
| Optimality Bound | 3.0 |
|======||
| Modeling Approach | Binary Linear Program |
| # Decision Variables | 76126 |
| # Binary Variables | 76125 |
| # Integer Variables | 1 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 374970 |
| Coefficients Type | Integer |
| Coefficients Range | 1.0 - 1.0, N/A - N/A, N/A - N/A |
|======||
| Workflow | Generate LP files using ZIMPL, solve using Gurobi |
| Algorithm Type | Deterministic |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0.0001 |
|======||
| Hardware Specifications | Intel(R) Xeon(R) Gold 6342 CPU @ 2.80GHz, instruction set [SSE2\|AVX\|AVX2\|AVX512] |
|======||
| Total Runtime | 1009.57 |
| CPU Runtime | 1654.73 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
|======||
| Remarks | CPU Runtime is Gurobi Work Measure, Success Threshold is the MIP Gap tolerance, variable counts are after presolve, Coefficient Range is (Min - Max) for (Linear, Quadratic, Quadratic Linear) coefficients |