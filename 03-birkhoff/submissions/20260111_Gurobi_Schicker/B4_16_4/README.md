# Submission for B4_16_4

This directory contains the submission for the problem **B4_16_4**.

## CSV Summary

| Field | Value |
|-------|-------|
| Problem | B4_16_4 |
| Submitter | Maximilian Schicker |
| Date | 2026-01-10 05:45:02 |
|======||
| Reference | See Models Directory using Gurobi 12.0.1 |
|======||
| Best Objective Value | 10.0 |
| Optimality Bound | 10.0 |
|======||
| Modeling Approach | Binary Linear Program |
| # Decision Variables | 45 |
| # Binary Variables | 21 |
| # Integer Variables | 24 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 168 |
| Coefficients Type | Integer |
| Coefficients Range | 1.0 - 10000.0, N/A - N/A, N/A - N/A |
|======||
| Workflow | Generate LP files using ZIMPL, solve using Gurobi |
| Algorithm Type | Deterministic |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0.0001 |
|======||
| Hardware Specifications | AMD EPYC 7542 32-Core Processor, instruction set [SSE2\|AVX\|AVX2] |
|======||
| Total Runtime | 0.06 |
| CPU Runtime | 0.01 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
|======||
| Remarks | CPU Runtime is Gurobi Work Measure, Success Threshold is the MIP Gap tolerance, variable counts are after presolve, Coefficient Range is (Min - Max) for (Linear, Quadratic, Quadratic Linear) coefficients |