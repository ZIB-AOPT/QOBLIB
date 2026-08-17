# Submission for B100_10000_3

This directory contains the submission for the problem **B100_10000_3**.

| Field | Value 1 |
| --- | --- |
| Problem | B100_10000_3 |
| Submitter | Manan Gupta |
| Affiliation | Independent Researcher |
| Date | 2026-08-17 |
| ====== |  |
| Reference | https://github.com/mnn31/QOBLIB/tree/a5a9c80dd18d5e0ab73dac5af8e42b8373c551f4/experiments/birkhoff |
| Best Objective Value | 424 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Exact integer Birkhoff decomposition using bottleneck perfect matchings. |
| # Decision Variables | 42824 |
| # Binary Variables | 42400 |
| # Integer Variables | 424 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 200 |
| Coefficients Type | Binary and integer |
| Coefficients Range | 1 to 10000000 |
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
| Total Runtime | 1.008742 |
| Time to Solution | 1.008742 |
| CPU Runtime | 1.008742 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Exact reconstruction verified; no optimality claim is made. |
