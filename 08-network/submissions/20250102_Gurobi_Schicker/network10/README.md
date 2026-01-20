# Submission for network10

This directory contains the submission for the problem **network10**.

## CSV Summary

| Field | Value |
|-------|-------|
| Problem | network10 |
| Submitter | Maximilian Schicker |
| Date | 06. Dec. 2024 |
|======||
| Reference | See Models Directory using Gurobi 11.0.0 |
|======||
| Best Objective Value | 210800.0 |
| Optimality Bound | 202750.0 |
|======||
| Modeling Approach | Integer Linear Program |
| # Decision Variables | 901 |
| # Binary Variables | 90 |
| # Integer Variables | 811 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 4230 |
| Coefficients Type | Integer |
| Coefficients Range | 1.0 - 1000000.0, N/A - N/A, N/A - N/A |
|======||
| Workflow | Generate LP files using ZIMPL, solve using Gurobi |
| Algorithm Type | Deterministic |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 0 |
| Success Threshold | 0.0001 |
|======||
| Hardware Specifications | AMD EPYC 7542 32-Core Processor, instruction set [SSE2\|AVX\|AVX2] |
|======||
| Total Runtime | 7200.03 |
| CPU Runtime | 10053.49 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
|======||
| Remarks | CPU Runtime is Gurobi Work Measure, Success Threshold is the MIP Gap tolerance, variable counts are after presolve, Coefficient Range is (Min - Max) for (Linear, Quadratic, Quadratic Linear) coefficients |