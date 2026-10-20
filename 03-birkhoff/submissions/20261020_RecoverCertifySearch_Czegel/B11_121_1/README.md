# Submission for B11_121_1

This directory contains the submission for the problem **B11_121_1**.

| Field | Value 1 |
| --- | --- |
| Problem | B11_121_1 |
| Submitter | András Czégel |
| Affiliation | Bentax Plus |
| Date | 2026-10-20 |
| Reference | https://arxiv.org/abs/2610.25837 (article), https://github.com/tg90000/rcs-birkhoff (code) |
| Best Objective Value | 52 |
| Optimality Bound | 20 |
| Modeling Approach | Exact decomposition, weights with the precision of the data. Solution chain: weights from the frequency rule, placed by fixing by unique subset sums (sparse); Birkhoff algorithm with the zeroing rule, beam search over zeroing steps, SAT re-optimization of the tail, large neighborhood search (dense). Bound chain in the same run: degree, two-line bound, SAT certificates |
| # Decision Variables | 122 |
| # Binary Variables | 121 |
| # Integer Variables | 1 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 22 |
| Coefficients Type | Binary |
| Coefficients Range | 1 |
| Workflow | Parallel run (6 threads): solution chain and bound chain in one run, stopping when they meet; final solution found by: beam search over zeroing steps |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| Hardware Specifications | Apple MacBook Pro, M4 Pro (8 performance + 4 efficiency cores), 24 GB RAM |
| Total Runtime | 600.045 |
| Time to Solution | 297.130 |
| CPU Runtime | 3600.270 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| Remarks | Exact decomposition (no tolerance), with weights of the precision of the data (integers at the given scale). Proofs of optimality by the degree or two-line bound hold for real weights too; proofs by SAT certificates (small dense instances) hold for weights of this precision. Runs: 60 s per instance; instances without a proof of optimality were run again with 600 s; the shorter decomposition is reported with the runtime of its run. Every optimality bound comes from the reported runs themselves. CPU runtime is an upper estimate (wall time x 6 threads). The planted decomposition in the instance file is never read. |
