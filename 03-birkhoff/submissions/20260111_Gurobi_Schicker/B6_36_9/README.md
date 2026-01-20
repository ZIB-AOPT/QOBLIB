# Submission for B6_36_9

This directory contains the submission for the problem **B6_36_9**.

## CSV Summary

| Field | Value |
|-------|-------|
| Problem | B6_36_9 |
| Submitter | Maximilian Schicker |
| Date | 2026-01-10 18:48:52 |
|======||
| Reference | See Models Directory using Gurobi 12.0.1 |
|======||
| Best Objective Value | 22.0 |
| Optimality Bound | 13.0 |
|======||
| Modeling Approach | Binary Linear Program |
| # Decision Variables | 1440 |
| # Binary Variables | 720 |
| # Integer Variables | 720 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 6480 |
| Coefficients Type | Integer |
| Coefficients Range | 1.0 - 10000.0, N/A - N/A, N/A - N/A |
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
| CPU Runtime | 10734.81 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
|======||
| Remarks | CPU Runtime is Gurobi Work Measure, Success Threshold is the MIP Gap tolerance, variable counts are after presolve, Coefficient Range is (Min - Max) for (Linear, Quadratic, Quadratic Linear) coefficients |