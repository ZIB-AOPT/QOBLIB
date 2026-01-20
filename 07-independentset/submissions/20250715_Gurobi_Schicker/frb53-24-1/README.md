# Submission for frb53-24-1

This directory contains the submission for the problem **frb53-24-1**.

## CSV Summary

| Field | Value |
|-------|-------|
| Problem | frb53-24-1 |
| Submitter | Maximilian Schicker |
| Date | 2025-07-15 17:49:06 |
|======||
| Reference | See Models Directory (BLP) using Gurobi 12.0.1 |
|======||
| Best Objective Value | 50.0 |
| Optimality Bound | 53.0 |
|======||
| Modeling Approach | Binary Linear Program |
| # Decision Variables | 1272 |
| # Binary Variables | 1272 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 188454 |
| Coefficients Type | Integer |
| Coefficients Range | 1.0 - 1.0, N/A - N/A, N/A - N/A |
|======||
| Workflow | Generate LP files using ZIMPL, solve using Gurobi |
| Algorithm Type | Deterministic |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 0 |
| Success Threshold | 0.0001 |
|======||
| Hardware Specifications | linux64, gurobi_cl: Intel(R) Xeon(R) Gold 6338 CPU @ 2.00GHz, instruction set [SSE2\|AVX\|AVX2\|AVX512] |
|======||
| Total Runtime | 7200.14 |
| CPU Runtime | 5941.22 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
|======||
| Remarks | CPU Runtime is Gurobi Work Measure, Success Threshold is the MIP Gap tolerance, variable counts are after presolve, Coefficient Range is (Min - Max) for (Linear, Quadratic, Quadratic Linear) coefficients |