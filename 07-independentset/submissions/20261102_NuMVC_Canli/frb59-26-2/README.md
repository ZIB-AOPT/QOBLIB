# Submission for frb59-26-2

This directory contains the submission for the problem **frb59-26-2**.

| Field | Value 1 |
| --- | --- |
| Problem | frb59-26-2 |
| Submitter | Arhan Canli |
| Affiliation | Quantavane |
| Date | 2026-11-02 |
| Reference | https://github.com/ZIB-AOPT/QOBLIB/tree/main/07-independentset/submissions/20261102_NuMVC_Canli |
| Best Objective Value | 59 |
| Optimality Bound | 59 |
| Modeling Approach | Direct search (no MIP or QUBO model): minimum vertex cover local search, the stable set is the complement of the cover |
| # Decision Variables | 1534 |
| # Binary Variables | 1534 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| Workflow | Greedy vertex cover, then NuMVC local search (Cai et al. 2013): two-stage exchange, edge weighting with forgetting (gamma = n/2, rho = 0.3), configuration checking; every cover found is recorded and one vertex removed to look for a smaller one; the run ends at its time limit or at a known upper bound; stable set = complement of the best cover, re-checked by an independent program. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| Hardware Specifications | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run on a shared machine (nice 10) |
| Total Runtime | 1657.2 |
| Time to Solution | 1085.8 |
| CPU Runtime | 847.5 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| Remarks | Stable set of size 59 (previous best known 58); upper bound 59. 1 of 5 seeded runs reached 59 (seed 1: 59 at 1086 s, seed 2: best 58 in 1800 s, seed 3: best 58 in 1800 s, seed 4: best 58 in 1800 s, seed 5: best 58 in 1800 s). A run stops at its time limit or when the set reaches the upper bound. Total Runtime is the mean wall-clock time over all runs and CPU Runtime the mean process CPU time over the runs that recorded it (seed 1 ran before CPU timing was added); Time to Solution is the mean wall-clock time to reach 59 over the runs that reached it. |
