# Submission for labs078

This directory contains the submission for the problem **labs078**.

## CSV Summary

| Field | Value |
|-------|-------|
| Problem | labs078 |
| Submitter | Maximilian Schicker |
| Date | 2024-12-29 02:15:18 |
|======||
| Reference | See Models Directory (integer) using Gurobi 11.0.0 |
|======||
| Best Objective Value | 755.0 |
| Optimality Bound | 0.0 |
|======||
| Modeling Approach | Integer Program |
| # Decision Variables | 3157 |
| # Binary Variables | 3080 |
| # Integer Variables | 77 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 0 |
| Coefficients Type | Integer |
| Coefficients Range | 0.0 - 0.0, 4.0 - 4.0, 1.0 - 4.0 |
|======||
| Workflow | Generate LP files using ZIMPL, solve using Gurobi |
| Algorithm Type | Deterministic |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 0 |
| Success Threshold | 0.0001 |
|======||
| Hardware Specifications | linux64, gurobi_cl: AMD EPYC 7542 32-Core Processor, instruction set [SSE2\|AVX\|AVX2] |
|======||
| Total Runtime | 7200.07 |
| CPU Runtime | 6942.42 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
|======||
| Remarks | CPU Runtime is Gurobi Work Measure, Success Threshold is the MIP Gap tolerance, variable counts are after presolve, Coefficient Range is (Min - Max) for (Linear, Quadratic, Quadratic Linear) coefficients |