# Submission for frb59-26-2

This directory contains the submission for the problem **frb59-26-2**.

| Field | Value 1 | Value 2 |
| --- | --- | --- |
| Problem | frb59-26-2 | frb59-26-2 |
| Submitter | Arhan Canli | Arhan Canli |
| Affiliation | Quantavane | Quantavane |
| Date | 2026-11-02 | 2026-11-02 |
| Reference | https://github.com/arhancanli/quantavane-qoblib | https://github.com/arhancanli/quantavane-qoblib |
| Best Objective Value | 58 | 59 |
| Optimality Bound | 59 | 59 |
| Modeling Approach | Direct search (no MIP or QUBO model): minimum vertex cover local search, the stable set is the complement of the cover | Direct search (no MIP or QUBO model): minimum vertex cover local search, the stable set is the complement of the cover |
| # Decision Variables | 1534 | 1534 |
| # Binary Variables | 1534 | 1534 |
| # Integer Variables | 0 | 0 |
| # Continuous Variables | 0 | 0 |
| # Non-Zero Coefficients | N/A | N/A |
| Coefficients Type | N/A | N/A |
| Coefficients Range | N/A | N/A |
| Workflow | Greedy clique cover (upper bound UB, computed in the run), greedy vertex cover, then NuMVC local search (Cai et al. 2013): two-stage exchange, edge weighting with forgetting (gamma = n/2, rho = 0.3), configuration checking; every cover found is recorded and one vertex removed to look for a smaller one; a run stops when the stable set reaches UB (proven optimal) or at its CPU budget; stable set = complement of the best cover, re-checked by an independent program. | Greedy clique cover (upper bound UB, computed in the run), greedy vertex cover, then NuMVC local search (Cai et al. 2013): two-stage exchange, edge weighting with forgetting (gamma = n/2, rho = 0.3), configuration checking; every cover found is recorded and one vertex removed to look for a smaller one; a run stops when the stable set reaches UB (proven optimal) or at its CPU budget; stable set = complement of the best cover, re-checked by an independent program. |
| Algorithm Type | Stochastic | Stochastic |
| Paradigm | Classical | Classical |
| # Runs | 5 | 5 |
| # Feasible Runs | 5 | 5 |
| # Successful Runs | 5 | 1 |
| Success Threshold | 0 | 0 |
| Hardware Specifications | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run at nice 10 on a machine shared with other jobs; all times are the process CPU time | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run at nice 10 on a machine shared with other jobs; all times are the process CPU time |
| Total Runtime | 30.00 | 775.74 |
| Time to Solution | 10.51 | 103.60 |
| CPU Runtime | 30.00 | 775.74 |
| GPU Runtime | N/A | N/A |
| QPU Runtime | N/A | N/A |
| Other HW Runtime | N/A | N/A |
| Remarks | Runs of 30 s CPU, seeds 1-5: Best stable set 58 over these 5 runs (listed best known 58: ours is equal to it). Optimality Bound 59 is the greedy clique-cover upper bound computed by the method. seed 1: 58, reached at 23.29 s, run ended at 30.00 s; seed 2: 58, reached at 6.75 s, run ended at 30.00 s; seed 3: 58, reached at 4.80 s, run ended at 30.00 s; seed 4: 58, reached at 1.78 s, run ended at 30.00 s; seed 5: 58, reached at 15.93 s, run ended at 30.00 s. All times are the single-threaded process's own CPU time (user + system), which excludes any time spent waiting for a core on the shared machine; Total Runtime and CPU Runtime are the mean time per run, Time to Solution the mean time at which each run first reached its own best. | Longer runs, seeds 1-5: Best stable set 59 over these 5 runs (listed best known 58: ours is above it). Optimality Bound 59 is the greedy clique-cover upper bound computed by the method (attained: proven optimal). seed 1 (current build, budget 3600 s CPU; rerun of the first seed-1 run, same seed and search): 59, reached at 488.48 s, run ended at 488.50 s (proven optimal: equals the upper bound); seed 2 (earlier build, limit 1800 s wall clock): 58, reached at 6.72 s, run ended at 830.00 s; seed 3 (earlier build, limit 1800 s wall clock): 58, reached at 5.07 s, run ended at 858.70 s; seed 4 (earlier build, limit 1800 s wall clock): 58, reached at 1.84 s, run ended at 830.30 s; seed 5 (earlier build, limit 1800 s wall clock): 58, reached at 15.91 s, run ended at 871.20 s. All times are the single-threaded process's own CPU time (user + system), which excludes any time spent waiting for a core on the shared machine; Total Runtime and CPU Runtime are the mean time per run, Time to Solution the mean time at which each run first reached its own best. |
