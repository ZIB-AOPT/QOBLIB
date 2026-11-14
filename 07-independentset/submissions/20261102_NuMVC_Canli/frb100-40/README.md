# Submission for frb100-40

This directory contains the submission for the problem **frb100-40**.

| Field | Value 1 | Value 2 |
| --- | --- | --- |
| Problem | frb100-40 | frb100-40 |
| Submitter | Arhan Canli | Arhan Canli |
| Affiliation | Quantavane | Quantavane |
| Date | 2026-11-02 | 2026-11-02 |
| Reference | https://github.com/arhancanli/quantavane-qoblib | https://github.com/arhancanli/quantavane-qoblib |
| Best Objective Value | 96 | 97 |
| Optimality Bound | 100 | 100 |
| Modeling Approach | Direct search (no MIP or QUBO model): minimum vertex cover local search, the stable set is the complement of the cover | Direct search (no MIP or QUBO model): minimum vertex cover local search, the stable set is the complement of the cover |
| # Decision Variables | 4000 | 4000 |
| # Binary Variables | 4000 | 4000 |
| # Integer Variables | 0 | 0 |
| # Continuous Variables | 0 | 0 |
| # Non-Zero Coefficients | N/A | N/A |
| Coefficients Type | N/A | N/A |
| Coefficients Range | N/A | N/A |
| Workflow | Greedy clique cover (upper bound UB, computed in the run), greedy vertex cover, then NuMVC local search (Cai et al. 2013): two-stage exchange, edge weighting with forgetting (gamma = n/2, rho = 0.3), configuration checking; every cover found is recorded and one vertex removed to look for a smaller one; a run stops when the stable set reaches UB (proven optimal) or at its CPU budget; stable set = complement of the best cover, re-checked by an independent program. | Greedy clique cover (upper bound UB, computed in the run), greedy vertex cover, then NuMVC local search (Cai et al. 2013): two-stage exchange, edge weighting with forgetting (gamma = n/2, rho = 0.3), configuration checking; every cover found is recorded and one vertex removed to look for a smaller one; a run stops when the stable set reaches UB (proven optimal) or at its CPU budget; stable set = complement of the best cover, re-checked by an independent program. |
| Algorithm Type | Stochastic | Stochastic |
| Paradigm | Classical | Classical |
| # Runs | 5 | 7 |
| # Feasible Runs | 5 | 7 |
| # Successful Runs | 2 | 5 |
| Success Threshold | 0 | 0 |
| Hardware Specifications | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run at nice 10 on a machine shared with other jobs; all times are the process CPU time | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run at nice 10 on a machine shared with other jobs; all times are the process CPU time |
| Total Runtime | 30.00 | 2066.59 |
| Time to Solution | 21.11 | 711.33 |
| CPU Runtime | 30.00 | 2066.59 |
| GPU Runtime | N/A | N/A |
| QPU Runtime | N/A | N/A |
| Other HW Runtime | N/A | N/A |
| Remarks | Runs of 30 s CPU, seeds 1-5: Best stable set 96 over these 5 runs (listed best known 96: ours is equal to it). Optimality Bound 100 is the greedy clique-cover upper bound computed by the method. seed 1: 96, reached at 25.08 s, run ended at 30.00 s; seed 2: 95, reached at 29.09 s, run ended at 30.00 s; seed 3: 95, reached at 22.14 s, run ended at 30.00 s; seed 4: 94, reached at 10.36 s, run ended at 30.00 s; seed 5: 96, reached at 18.90 s, run ended at 30.00 s. All times are the single-threaded process's own CPU time (user + system), which excludes any time spent waiting for a core on the shared machine; Total Runtime and CPU Runtime are the mean time per run, Time to Solution the mean time at which each run first reached its own best. | Longer runs, seeds 1-7: Best stable set 97 over these 7 runs (listed best known 96: ours is above it). Optimality Bound 100 is the greedy clique-cover upper bound computed by the method. seed 1 (current build, budget 1680 s CPU; rerun of the first seed-1 run, same seed and search): 97, reached at 1157.20 s, run ended at 1680.00 s; seed 2 (earlier build, limit 3600 s wall clock): 97, reached at 939.98 s, run ended at 1833.30 s; seed 3 (earlier build, limit 3600 s wall clock): 97, reached at 341.92 s, run ended at 1475.50 s; seed 4 (earlier build, limit 3600 s wall clock): 96, reached at 69.35 s, run ended at 1573.20 s; seed 5 (earlier build, limit 3600 s wall clock): 97, reached at 806.36 s, run ended at 1856.30 s; seed 6 (earlier build, limit 7200 s wall clock): 96, reached at 134.98 s, run ended at 3023.70 s; seed 7 (earlier build, limit 7200 s wall clock): 97, reached at 1529.54 s, run ended at 3024.10 s. All times are the single-threaded process's own CPU time (user + system), which excludes any time spent waiting for a core on the shared machine; Total Runtime and CPU Runtime are the mean time per run, Time to Solution the mean time at which each run first reached its own best. |
