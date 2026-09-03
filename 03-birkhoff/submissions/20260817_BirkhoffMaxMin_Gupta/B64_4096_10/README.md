# Submission for B64_4096_10

This directory contains the submission for the problem **B64_4096_10**.

| Field | Value 1 |
| --- | --- |
| Problem | B64_4096_10 |
| Submitter | Manan Gupta |
| Affiliation | Independent Researcher |
| Date | 2026-08-17 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-birkhoff |
| Best Objective Value | 254 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Exact integer Birkhoff decomposition using bottleneck perfect matchings. |
| # Decision Variables | 16510 |
| # Binary Variables | 16256 |
| # Integer Variables | 254 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 128 |
| Coefficients Type | Binary and integer |
| Coefficients Range | 1 to 1000000 |
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
| Total Runtime | 9.059961 |
| Time to Solution | 9.059961 |
| CPU Runtime | 9.059961 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Exact reconstruction verified; no optimality claim is made. |
