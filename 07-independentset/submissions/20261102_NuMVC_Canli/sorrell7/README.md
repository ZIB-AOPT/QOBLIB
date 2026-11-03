# Submission for sorrell7

This directory contains the submission for the problem **sorrell7**.

| Field | Value 1 |
| --- | --- |
| Problem | sorrell7 |
| Submitter | Arhan Canli |
| Affiliation | Quantavane |
| Date | 2026-11-02 |
| Reference | https://github.com/arhancanli/quantavane-qoblib |
| Best Objective Value | 198 |
| Optimality Bound | 366 |
| Modeling Approach | Direct search (no MIP or QUBO model): minimum vertex cover local search, the stable set is the complement of the cover |
| # Decision Variables | 2048 |
| # Binary Variables | 2048 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| Workflow | Greedy clique cover (upper bound UB, computed in the run), greedy vertex cover, then NuMVC local search (Cai et al. 2013): two-stage exchange, edge weighting with forgetting (gamma = n/2, rho = 0.3), configuration checking; every cover found is recorded and one vertex removed to look for a smaller one; a run stops when the stable set reaches UB (proven optimal) or at its CPU budget; stable set = complement of the best cover, re-checked by an independent program. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| Hardware Specifications | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run at nice 10 on a machine shared with other jobs; all times are the process CPU time |
| Total Runtime | 30.00 |
| Time to Solution | 4.61 |
| CPU Runtime | 30.00 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| Remarks | Runs of 30 s CPU, seeds 1-5: Best stable set 198 over these 5 runs (listed best known 198: ours is equal to it). Optimality Bound 366 is the greedy clique-cover upper bound computed by the method. seed 1: 198, reached at 12.25 s, run ended at 30.00 s; seed 2: 198, reached at 6.85 s, run ended at 30.00 s; seed 3: 198, reached at 1.18 s, run ended at 30.00 s; seed 4: 198, reached at 1.30 s, run ended at 30.00 s; seed 5: 198, reached at 1.47 s, run ended at 30.00 s. All times are the single-threaded process's own CPU time (user + system), which excludes any time spent waiting for a core on the shared machine; Total Runtime and CPU Runtime are the mean time per run, Time to Solution the mean time at which each run first reached its own best. |
