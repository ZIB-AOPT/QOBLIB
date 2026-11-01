# Submission for B7_49_6

This directory contains the submission for the problem **B7_49_6**.

| Field | Value 1 |
| --- | --- |
| Problem | B7_49_6 |
| Submitter | András Czégel |
| Affiliation | Bentax Plus |
| Date | 2026-10-20 |
| Reference | https://arxiv.org/abs/2610.25837 (article), https://github.com/tg90000/rcs-birkhoff (code) |
| Best Objective Value | 25 |
| Optimality Bound | 13 |
| Modeling Approach | Exact decomposition, weights with the precision of the data. Solution chain: weights from the frequency rule, placed by fixing by unique subset sums (sparse); Birkhoff algorithm with the zeroing rule, beam search over zeroing steps, SAT re-optimization of the tail, large neighborhood search (dense). Bound chain in the same run: degree, two-line bound, SAT certificates |
| # Decision Variables | 50 |
| # Binary Variables | 49 |
| # Integer Variables | 1 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 14 |
| Coefficients Type | Binary |
| Coefficients Range | 1 |
| Workflow | Parallel run (6 threads): solution chain and bound chain in one run, stopping when they meet; final solution found by: beam search over zeroing steps |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| Hardware Specifications | Apple MacBook Pro, M4 Pro (8 performance + 4 efficiency cores), 24 GB RAM |
| Total Runtime | 660.091 |
| Time to Solution | 237.824 |
| CPU Runtime | 3245.224 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| Remarks | Exact decomposition (no tolerance), with weights of the precision of the data (integers at the given scale). The Optimality Bound holds for real weights (degree or two-line bound); its certificate is B7_49_6_certificate.json. For weights with the precision of the data, a SAT certificate of the runs proves the lower bound 15. This bound does not hold for real weights and is not used as Optimality Bound; no proof file is included. 5 independent runs with the seeds 0, 1, 2, 3, 4. A run: 60 s per instance; without a proof of optimality, a second round of 600 s that starts from scratch; the result of the run is the shorter decomposition of the two rounds. Best Objective Value: the shortest decomposition over the runs. Optimality Bound: the largest lower bound over the runs that holds for real weights. Total Runtime: the time of the whole run (both rounds). Time to Solution: the time from the start of the run until it first found a decomposition of its final length (the second round counts from the end of the first). Both are means over the 5 runs. CPU Runtime: the measured CPU time of all threads in both rounds, mean over the runs with the seeds 1 to 4 (the CPU time of the run with seed 0 was not measured). The objective time series has one element per run: the incumbent of the run over both rounds, the second round shifted by the runtime of the first. Length over the runs (seeds 0 to 4): 25, 25, 25, 25, 25; mean 25.0, median 25, std 0.00. Total runtime [s]: 660.0955, 660.0882, 660.0670, 660.1089, 660.0963; median 660.096, std 0.015. Time to solution [s]: 214.9413, 360.3541, 210.0767, 205.6156, 198.1309; median 210.077, std 68.775. The planted decomposition in the instance file is never read. |
