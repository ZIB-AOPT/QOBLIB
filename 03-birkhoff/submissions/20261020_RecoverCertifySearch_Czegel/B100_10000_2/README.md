# Submission for B100_10000_2

This directory contains the submission for the problem **B100_10000_2**.

| Field | Value 1 |
| --- | --- |
| Problem | B100_10000_2 |
| Submitter | András Czégel |
| Affiliation | Bentax Plus |
| Date | 2026-10-20 |
| Reference | https://arxiv.org/abs/2610.25837 (article), https://github.com/tg90000/rcs-birkhoff (code) |
| Best Objective Value | 406 |
| Optimality Bound | 151 |
| Modeling Approach | Exact decomposition, weights with the precision of the data. Solution chain: weights from the frequency rule, placed by fixing by unique subset sums (sparse); Birkhoff algorithm with the zeroing rule, beam search over zeroing steps, SAT re-optimization of the tail, large neighborhood search (dense). Bound chain in the same run: degree, two-line bound, SAT certificates |
| # Decision Variables | 10001 |
| # Binary Variables | 10000 |
| # Integer Variables | 1 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 200 |
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
| Total Runtime | 168.120 |
| Time to Solution | 80.954 |
| CPU Runtime | 960.559 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| Remarks | Exact decomposition (no tolerance), with weights of the precision of the data (integers at the given scale). Proofs of optimality by the degree or two-line bound hold for real weights too; proofs by SAT certificates (small dense instances) hold for weights of this precision. 5 independent runs with the seeds 0, 1, 2, 3, 4. A run: 60 s per instance; without a proof of optimality, a second round of 600 s; the result of the run is the shorter decomposition of the two rounds, with the runtime and time to solution of its round. Best Objective Value: the shortest decomposition over the runs. Optimality Bound: the largest lower bound over the runs. Total Runtime and Time to Solution: means over the 5 runs; the time to solution of a run is the time at which it found its own final decomposition. CPU Runtime: the measured CPU time of all threads, mean over the runs with the seeds 1 to 4 (the CPU time of the run with seed 0 was not measured). The objective time series has one entry per run. Length over the runs (seeds 0 to 4): 406, 406, 407, 407, 407; mean 406.6, median 407, std 0.55. Total runtime [s]: 60.1634, 60.1864, 60.0663, 600.1149, 60.0703; median 60.163, std 241.492. Time to solution [s]: 16.1604, 13.3330, 30.5322, 305.6019, 39.1413; median 30.532, std 126.024. The planted decomposition in the instance file is never read. |
