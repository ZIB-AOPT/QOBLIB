# Submission for B100_100_6

This directory contains the submission for the problem **B100_100_6**.

| Field | Value 1 |
| --- | --- |
| Problem | B100_100_6 |
| Submitter | András Czégel |
| Affiliation | Bentax Plus |
| Date | 2026-10-20 |
| Reference | https://arxiv.org/abs/2610.25837 (article), https://github.com/tg90000/rcs-birkhoff (code) |
| Best Objective Value | 100 |
| Optimality Bound | 100 |
| Modeling Approach | Exact decomposition, weights with the precision of the data. Solution chain: weights from the frequency rule, placed by fixing by unique subset sums (sparse); Birkhoff algorithm with the zeroing rule, beam search over zeroing steps, SAT re-optimization of the tail, large neighborhood search (dense). Bound chain in the same run: degree, two-line bound, SAT certificates |
| # Decision Variables | 6334 |
| # Binary Variables | 6333 |
| # Integer Variables | 1 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 200 |
| Coefficients Type | Binary |
| Coefficients Range | 1 |
| Workflow | Parallel run (6 threads): solution chain and bound chain in one run, stopping when they meet; final solution found by: frequency rule and fixing by unique subset sums |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| Hardware Specifications | Apple MacBook Pro, M4 Pro (8 performance + 4 efficiency cores), 24 GB RAM |
| Total Runtime | 53.917 |
| Time to Solution | 0.062 |
| CPU Runtime | 323.501 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| Remarks | Exact decomposition (no tolerance), with weights of the precision of the data (integers at the given scale). Proofs of optimality by the degree or two-line bound hold for real weights too; proofs by SAT certificates (small dense instances) hold for weights of this precision. Runs: 60 s per instance; instances without a proof of optimality were run again with 600 s; the shorter decomposition is reported with the runtime of its run. Every optimality bound comes from the reported runs themselves. CPU runtime is an upper estimate (wall time x 6 threads). The planted decomposition in the instance file is never read. |
