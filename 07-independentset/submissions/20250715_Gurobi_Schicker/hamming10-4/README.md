# Submission for hamming10-4

This directory contains the submission for the problem **hamming10-4**.

## CSV Summary

| Field | Value |
|-------|-------|
| Problem | hamming10-4 |
| Submitter | Maximilian Schicker |
| Date | 2025-07-15 18:02:47 |
|======||
| Reference | See Models Directory (BLP) using Gurobi 12.0.1 |
|======||
| Best Objective Value | 40.0 |
| Optimality Bound | 47.0 |
|======||
| Modeling Approach | Binary Linear Program |
| # Decision Variables | 1024 |
| # Binary Variables | 1024 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 179200 |
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
| Total Runtime | 7200.16 |
| CPU Runtime | 9297.71 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
|======||
| Remarks | CPU Runtime is Gurobi Work Measure, Success Threshold is the MIP Gap tolerance, variable counts are after presolve, Coefficient Range is (Min - Max) for (Linear, Quadratic, Quadratic Linear) coefficients |