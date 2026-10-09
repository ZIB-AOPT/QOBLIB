# Submission for a400_t10_s02_b100_l1e-05

This directory contains the submission for the problem **a400_t10_s02_b100_l1e-05**.

| Field | Value 1 |
| --- | --- |
| Problem | a400_t10_s02_b100_l1e-05 |
| Submitter | Manan Gupta |
| Affiliation | The Harker School |
| Date | 2026-10-09 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-solvers/tree/main/portfolio |
| Best Objective Value | -2656259 |
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
| # Runs | 3 |
| # Feasible Runs | 3 |
| # Successful Runs | 2 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Cloud CPU instance: 16 vCPU slice of an AMD EPYC 9655 host, 755 GB RAM visible, Ubuntu 24.04, Python 3.12, no GPU. Runs executed one at a time within the instance, but the host is shared with other tenants and showed high load, so wall clock times are indicative only. |
| ====== |  |
| Total Runtime | 87.7 |
| Time to Solution | 87.7 |
| CPU Runtime | 87.7 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | No feasible solution was on record for this instance before this submission. Heuristic, so the optimality bound is N/A. Runtimes are the average over the seeds and include building the exact integer coefficients. Successful runs are those reaching this method's own best value. Verified with 06-portfolio/check. |
