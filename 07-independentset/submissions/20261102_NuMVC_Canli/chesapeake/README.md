# Submission for chesapeake

This directory contains the submission for the problem **chesapeake**.

| Field | Value 1 |
| --- | --- |
| Problem | chesapeake |
| Submitter | Arhan Canli |
| Affiliation | Quantavane |
| Date | 2026-11-02 |
| Reference | https://github.com/arhancanli/quantavane-qoblib |
| Best Objective Value | 17 |
| Optimality Bound | 17 |
| Modeling Approach | Direct search (no MIP or QUBO model): minimum vertex cover local search, the stable set is the complement of the cover |
| # Decision Variables | 39 |
| # Binary Variables | 39 |
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
| Total Runtime | 0.00 |
| Time to Solution | 0.00 |
| CPU Runtime | 0.00 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| Remarks | Runs of 30 s CPU, seeds 1-5: Best stable set 17 over these 5 runs (listed best known 17: ours is equal to it). Optimality Bound 17 is the greedy clique-cover upper bound computed by the method (attained: proven optimal). seed 1: 17, reached at 0.00 s, run ended at 0.00 s (proven optimal: equals the upper bound); seed 2: 17, reached at 0.00 s, run ended at 0.00 s (proven optimal: equals the upper bound); seed 3: 17, reached at 0.00 s, run ended at 0.00 s (proven optimal: equals the upper bound); seed 4: 17, reached at 0.00 s, run ended at 0.00 s (proven optimal: equals the upper bound); seed 5: 17, reached at 0.00 s, run ended at 0.00 s (proven optimal: equals the upper bound). All times are the single-threaded process's own CPU time (user + system), which excludes any time spent waiting for a core on the shared machine; Total Runtime and CPU Runtime are the mean time per run, Time to Solution the mean time at which each run first reached its own best. |
