# Submission for frb100-40

This directory contains the submission for the problem **frb100-40**.

| Field | Value 1 |
| --- | --- |
| Problem | frb100-40 |
| Submitter | Arhan Canli |
| Affiliation | Quantavane |
| Date | 2026-11-02 |
| Reference | https://github.com/ZIB-AOPT/QOBLIB/tree/main/07-independentset/submissions/20261102_NuMVC_Canli |
| Best Objective Value | 97 |
| Optimality Bound | 100 |
| Modeling Approach | Direct search (no MIP or QUBO model): minimum vertex cover local search, the stable set is the complement of the cover |
| # Decision Variables | 4000 |
| # Binary Variables | 4000 |
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
| # Successful Runs | 4 |
| Success Threshold | 0 |
| Hardware Specifications | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run on a shared machine (nice 10) |
| Total Runtime | 3600.0 |
| Time to Solution | 1677.6 |
| CPU Runtime | 1684.6 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| Remarks | Stable set of size 97 (previous best known 96); upper bound 100. 4 of 5 seeded runs reached 97 (seed 1: 97 at 2517 s, seed 2: 97 at 1811 s, seed 3: 97 at 850 s, seed 4: best 96 in 3600 s, seed 5: 97 at 1532 s). A run stops at its time limit or when the set reaches the upper bound. Total Runtime is the mean wall-clock time over all runs and CPU Runtime the mean process CPU time over the runs that recorded it (seed 1 ran before CPU timing was added); Time to Solution is the mean wall-clock time to reach 97 over the runs that reached it. |
