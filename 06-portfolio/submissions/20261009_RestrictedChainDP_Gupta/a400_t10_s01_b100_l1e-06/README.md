# Submission for a400_t10_s01_b100_l1e-06

This directory contains the submission for the problem **a400_t10_s01_b100_l1e-06**.

| Field | Value 1 |
| --- | --- |
| Problem | a400_t10_s01_b100_l1e-06 |
| Submitter | Manan Gupta |
| Affiliation | The Harker School |
| Date | 2026-10-25 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-solvers/tree/main/portfolio |
| Best Objective Value | -3202287 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Reference binary quadratic model of bqp_u3_c10.zpl, searched as a chain over per period unit count portfolios |
| # Decision Variables | N/A |
| # Binary Variables | N/A |
| # Integer Variables | N/A |
| # Continuous Variables | N/A |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | Restricted state chain dynamic program. For each period, build a pool of good portfolios by exact integer local search (add, remove, swap and pair moves with exact incremental gains), exact subset enumeration over small groups of assets, and roundings of a Frank Wolfe relaxation, with neighbouring periods entering as separable rebalancing anchors. Run the exact chain dynamic program over the pools, then coordinate descent over periods with kicks and repeat. All coefficients are the exact integer coefficients of the reference model, so the checker agrees bit for bit. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 33 |
| # Feasible Runs | 33 |
| # Successful Runs | 4 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Cloud CPU container: 32 hardware threads of an AMD EPYC 9B45 host, 128 GB memory limit, Ubuntu 20.04, Python 3.12, no GPU. Eight single threaded runs executed concurrently in the container; the host is shared with other tenants and showed high load, so wall clock times are indicative only. |
| ====== |  |
| Total Runtime | 170.3 |
| Time to Solution | 170.3 |
| CPU Runtime | 170.3 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | This instance had no entry in the best known table before this submission. Re-run on 2026-10-25 with 33 seeds and a larger search budget (more restarts, kicks and neighbourhood iterations than the 2026-10-09 rows); the best seed is reported. Heuristic, so the optimality bound is N/A. Runtimes are the average over the seeds and include building the exact integer coefficients. Successful runs are those reaching this method's own best value. Verified with 06-portfolio/check. |
