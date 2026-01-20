# Submission for frb59-26-2

This directory contains the submission for the problem **frb59-26-2**.

## CSV Summary

| Field | Value |
|-------|-------|
| Problem | frb59-26-2 |
| Submitter | Maximilian Schicker |
| Date | 2025-07-15 17:55:06 |
|======||
| Reference | See Models Directory (BLP) using Gurobi 12.0.1 |
|======||
| Best Objective Value | 56.0 |
| Optimality Bound | 59.0 |
|======||
| Modeling Approach | Binary Linear Program |
| # Decision Variables | 1534 |
| # Binary Variables | 1534 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 252326 |
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
| Total Runtime | 7200.83 |
| CPU Runtime | 5256.17 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
|======||
| Remarks | CPU Runtime is Gurobi Work Measure, Success Threshold is the MIP Gap tolerance, variable counts are after presolve, Coefficient Range is (Min - Max) for (Linear, Quadratic, Quadratic Linear) coefficients |