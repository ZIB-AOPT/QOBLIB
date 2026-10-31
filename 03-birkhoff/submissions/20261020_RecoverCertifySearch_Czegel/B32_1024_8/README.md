# Submission for B32_1024_8

This directory contains the submission for the problem **B32_1024_8**.

| Field | Value 1 |
| --- | --- |
| Problem | B32_1024_8 |
| Submitter | András Czégel |
| Affiliation | Bentax Plus |
| Date | 2026-10-20 |
| Reference | https://arxiv.org/abs/2610.25837 (article), https://github.com/tg90000/rcs-birkhoff (code) |
| Best Objective Value | 151 |
| Optimality Bound | 53 |
| Modeling Approach | Exact decomposition, weights with the precision of the data. Solution chain: weights from the frequency rule, placed by fixing by unique subset sums (sparse); Birkhoff algorithm with the zeroing rule, beam search over zeroing steps, SAT re-optimization of the tail, large neighborhood search (dense). Bound chain in the same run: degree, two-line bound, SAT certificates |
| # Decision Variables | 1025 |
| # Binary Variables | 1024 |
| # Integer Variables | 1 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 64 |
| Coefficients Type | Binary |
| Coefficients Range | 1 |
| Workflow | Parallel run (6 threads): solution chain and bound chain in one run, stopping when they meet; final solution found by: large neighborhood search |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 2 |
| Success Threshold | 0 |
| Hardware Specifications | Apple MacBook Pro, M4 Pro (8 performance + 4 efficiency cores), 24 GB RAM |
| Total Runtime | 168.013 |
| Time to Solution | 64.296 |
| CPU Runtime | 972.320 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| Remarks | Exact decomposition (no tolerance), with weights of the precision of the data (integers at the given scale). Proofs of optimality by the degree or two-line bound hold for real weights too; proofs by SAT certificates (small dense instances) hold for weights of this precision. 5 independent runs with the seeds 0, 1, 2, 3, 4. A run: 60 s per instance; without a proof of optimality, a second round of 600 s; the result of the run is the shorter decomposition of the two rounds, with the runtime and time to solution of its round. Best Objective Value: the shortest decomposition over the runs. Optimality Bound: the largest lower bound over the runs. Total Runtime and Time to Solution: means over the 5 runs; the time to solution of a run is the time at which it found its own final decomposition. CPU Runtime: the measured CPU time of all threads, mean over the runs with the seeds 1 to 4 (the CPU time of the run with seed 0 was not measured). The objective time series has one entry per run. Length over the runs (seeds 0 to 4): 152, 151, 152, 152, 151; mean 151.6, median 152, std 0.55. Total runtime [s]: 60.0123, 600.0144, 60.0041, 60.0181, 60.0166; median 60.017, std 241.496. Time to solution [s]: 2.6641, 244.8397, 8.4312, 6.3864, 59.1611; median 8.431, std 103.556. The planted decomposition in the instance file is never read. |
