# Submission for B64_4096_9

This directory contains the submission for the problem **B64_4096_9**.

| Field | Value 1 |
| --- | --- |
| Problem | B64_4096_9 |
| Submitter | András Czégel |
| Affiliation | Bentax Plus |
| Date | 2026-10-20 |
| Reference | https://arxiv.org/abs/2610.25837 (article), https://github.com/tg90000/rcs-birkhoff (code) |
| Best Objective Value | 242 |
| Optimality Bound | 97 |
| Modeling Approach | Exact decomposition, weights with the precision of the data. Solution chain: weights from the frequency rule, placed by fixing by unique subset sums (sparse); Birkhoff algorithm with the zeroing rule, beam search over zeroing steps, SAT re-optimization of the tail, large neighborhood search (dense). Bound chain in the same run: degree, two-line bound, SAT certificates |
| # Decision Variables | 4097 |
| # Binary Variables | 4096 |
| # Integer Variables | 1 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 128 |
| Coefficients Type | Binary |
| Coefficients Range | 1 |
| Workflow | Parallel run (6 threads): solution chain and bound chain in one run, stopping when they meet; final solution found by: large neighborhood search |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| Hardware Specifications | Apple MacBook Pro, M4 Pro (8 performance + 4 efficiency cores), 24 GB RAM |
| Total Runtime | 384.019 |
| Time to Solution | 107.700 |
| CPU Runtime | 1580.713 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| Remarks | Exact decomposition (no tolerance), with weights of the precision of the data (integers at the given scale). Proofs of optimality by the degree or two-line bound hold for real weights too; proofs by SAT certificates (small dense instances) hold for weights of this precision. 5 independent runs with the seeds 0, 1, 2, 3, 4. A run: 60 s per instance; without a proof of optimality, a second round of 600 s; the result of the run is the shorter decomposition of the two rounds, with the runtime and time to solution of its round. Best Objective Value: the shortest decomposition over the runs. Optimality Bound: the largest lower bound over the runs. Total Runtime and Time to Solution: means over the 5 runs; the time to solution of a run is the time at which it found its own final decomposition. CPU Runtime: the measured CPU time of all threads, mean over the runs with the seeds 1 to 4 (the CPU time of the run with seed 0 was not measured). The objective time series has one entry per run. Length over the runs (seeds 0 to 4): 243, 243, 242, 244, 243; mean 243.0, median 243, std 0.71. Total runtime [s]: 600.0167, 600.0197, 600.0187, 60.0273, 60.0149; median 600.017, std 295.769. Time to solution [s]: 288.4662, 115.0413, 66.6244, 9.0372, 59.3320; median 66.624, std 107.809. The planted decomposition in the instance file is never read. |
