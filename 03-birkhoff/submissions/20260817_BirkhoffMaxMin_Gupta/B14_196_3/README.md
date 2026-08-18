# Submission for B14_196_3

This directory contains the submission for the problem **B14_196_3**.

| Field | Value 1 |
| --- | --- |
| Problem | B14_196_3 |
| Submitter | Manan Gupta |
| Affiliation | Independent Researcher |
| Date | 2026-08-17 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-birkhoff |
| Best Objective Value | 70 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Exact integer Birkhoff decomposition using bottleneck perfect matchings. |
| # Decision Variables | 1050 |
| # Binary Variables | 980 |
| # Integer Variables | 70 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 28 |
| Coefficients Type | Binary and integer |
| Coefficients Range | 1 to 100000 |
| ====== |  |
| Workflow | At each iteration, maximize the smallest residual selected by a perfect matching. Within that threshold, maximize eliminated entries and then minimize the matching residual sum. Subtract the selected minimum exactly. |
| Algorithm Type | Deterministic |
| Paradigm | Classical |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple MacBook Pro with Apple M3 Pro, 11 CPU cores, 18 GB unified memory |
| ====== |  |
| Total Runtime | 0.006784 |
| Time to Solution | 0.006784 |
| CPU Runtime | 0.006784 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Exact reconstruction verified; no optimality claim is made. |
