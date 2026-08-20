# Submission for a003_t02_orig_b003_l1e-04

This directory contains the submission for the problem **a003_t02_orig_b003_l1e-04**.

| Field | Value 1 |
| --- | --- |
| Problem | a003_t02_orig_b003_l1e-04 |
| Submitter | Manan Gupta |
| Affiliation | The Harker School |
| Date | 2026-08-18 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-solvers/tree/main/portfolio |
| Best Objective Value | -1995 |
| Optimality Bound | -1995 |
| ====== |  |
| Modeling Approach | Reference binary quadratic model of bqp_u3_c10.zpl, reformulated as a chain over per-period unit-count portfolios |
| # Decision Variables | 58 |
| # Binary Variables | 58 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 822 |
| Coefficients Type | Integer |
| Coefficients Range | -1630 - 1630 |
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
| Total Runtime | 0.0 |
| Time to Solution | 0.0 |
| CPU Runtime | 0.0 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Exact method, so the reported value is a proven optimum and the optimality bound equals the objective. The algorithm is not anytime, so the objective time series holds the single incumbent produced when the dynamic program returns. Variable and coefficient counts are for the reference binary model before presolve; the non-zero count expands each group-pair risk coefficient over the ub^2 copy-slot pairs. Verified with 06-portfolio/check. |
