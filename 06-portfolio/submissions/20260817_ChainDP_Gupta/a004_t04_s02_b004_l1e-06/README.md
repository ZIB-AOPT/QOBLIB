# Submission for a004_t04_s02_b004_l1e-06

This directory contains the submission for the problem **a004_t04_s02_b004_l1e-06**.

| Field | Value 1 |
| --- | --- |
| Problem | a004_t04_s02_b004_l1e-06 |
| Submitter | Manan Gupta |
| Affiliation | The Harker School |
| Date | 2026-08-18 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-solvers/tree/main/portfolio |
| Best Objective Value | -42121 |
| Optimality Bound | -42121 |
| ====== |  |
| Modeling Approach | Reference binary quadratic model of bqp_u3_c10.zpl, reformulated as a chain over per-period unit-count portfolios |
| # Decision Variables | 140 |
| # Binary Variables | 140 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 2700 |
| Coefficients Type | Integer |
| Coefficients Range | -5105 - 105 |
| ====== |  |
| Workflow | Parse prices and covariances in exact rational arithmetic; round every objective coefficient exactly as Zimpl does; enumerate all feasible per-period portfolios under the budget and capital slack registers; solve the resulting chain by forward dynamic programming, the last period detaching because the reference model charges no rebalancing into it; recover the schedule by backpointers. |
| Algorithm Type | Deterministic |
| Paradigm | Classical |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M3 Pro (Mac15,6), 11 cores (5 performance + 6 efficiency), 18 GB unified memory, macOS 26.3, arm64. Runtimes are from a single-process rerun with no other load, so they are not inflated by contention. |
| ====== |  |
| Total Runtime | 0.018 |
| Time to Solution | 0.018 |
| CPU Runtime | 0.018 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Exact method, so the reported value is a proven optimum and the optimality bound equals the objective. The algorithm is not anytime, so the objective time series holds the single incumbent produced when the dynamic program returns. Variable and coefficient counts are for the reference binary model before presolve; the non-zero count expands each group-pair risk coefficient over the ub^2 copy-slot pairs. Verified with 06-portfolio/check. |
