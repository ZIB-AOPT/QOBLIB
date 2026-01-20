# Submission for labs029

This directory contains the submission for the problem **labs029**.

## CSV Summary

| Field | Value |
|-------|-------|
| Problem | labs029 |
| Submitter | Maximilian Schicker |
| Date | 2024-12-28 17:58:41 |
|======||
| Reference | See Models Directory (integer) using Gurobi 11.0.0 |
|======||
| Best Objective Value | 62.0 |
| Optimality Bound | 62.0 |
|======||
| Modeling Approach | Integer Program |
| # Decision Variables | 462 |
| # Binary Variables | 434 |
| # Integer Variables | 28 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 0 |
| Coefficients Type | Integer |
| Coefficients Range | 0.0 - 0.0, 4.0 - 4.0, 1.0 - 4.0 |
|======||
| Workflow | Generate LP files using ZIMPL, solve using Gurobi |
| Algorithm Type | Deterministic |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0.0001 |
|======||
| Hardware Specifications | linux64, gurobi_cl: AMD EPYC 7542 32-Core Processor, instruction set [SSE2\|AVX\|AVX2] |
|======||
| Total Runtime | 484.7 |
| CPU Runtime | 502.57 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
|======||
| Remarks | CPU Runtime is Gurobi Work Measure, Success Threshold is the MIP Gap tolerance, variable counts are after presolve, Coefficient Range is (Min - Max) for (Linear, Quadratic, Quadratic Linear) coefficients |