# Submission for frb100-40

This directory contains the submission for the problem **frb100-40**.

| Field | Value 1 | Value 2 | Value 3 |
| --- | --- | --- | --- |
| Problem | frb100-40 | frb100-40 | frb100-40 |
| Submitter | Arhan Canli | Arhan Canli | Arhan Canli |
| Affiliation | Quantavane | Quantavane | Quantavane |
| Date | 2026-11-02 | 2026-11-02 | 2026-11-02 |
| Reference | https://github.com/arhancanli/quantavane-qoblib | https://github.com/arhancanli/quantavane-qoblib | https://github.com/arhancanli/quantavane-qoblib |
| Best Objective Value | 95 | 97 | 97 |
| Optimality Bound | N/A | N/A | N/A |
| Modeling Approach | Direct search (no MIP or QUBO model): minimum vertex cover local search, the stable set is the complement of the cover | Direct search (no MIP or QUBO model): minimum vertex cover local search, the stable set is the complement of the cover | Direct search (no MIP or QUBO model): minimum vertex cover local search, the stable set is the complement of the cover |
| # Decision Variables | 4000 | 4000 | 4000 |
| # Binary Variables | 4000 | 4000 | 4000 |
| # Integer Variables | 0 | 0 | 0 |
| # Continuous Variables | 0 | 0 | 0 |
| # Non-Zero Coefficients | N/A | N/A | N/A |
| Coefficients Type | N/A | N/A | N/A |
| Coefficients Range | N/A | N/A | N/A |
| Workflow | Greedy vertex cover, then NuMVC local search (Cai et al. 2013): two-stage exchange, edge weighting with forgetting (gamma = n/2, rho = 0.3), configuration checking; every cover found is recorded and one vertex removed to look for a smaller one; each run ends at its wall-clock limit; stable set = complement of the best cover, re-checked by an independent program. | Greedy vertex cover, then NuMVC local search (Cai et al. 2013): two-stage exchange, edge weighting with forgetting (gamma = n/2, rho = 0.3), configuration checking; every cover found is recorded and one vertex removed to look for a smaller one; each run ends at its wall-clock limit; stable set = complement of the best cover, re-checked by an independent program. | Greedy vertex cover, then NuMVC local search (Cai et al. 2013): two-stage exchange, edge weighting with forgetting (gamma = n/2, rho = 0.3), configuration checking; every cover found is recorded and one vertex removed to look for a smaller one; each run ends at its wall-clock limit; stable set = complement of the best cover, re-checked by an independent program. |
| Algorithm Type | Stochastic | Stochastic | Stochastic |
| Paradigm | Classical | Classical | Classical |
| # Runs | 5 | 5 | 2 |
| # Feasible Runs | 5 | 5 | 2 |
| # Successful Runs | 1 | 4 | 1 |
| Success Threshold | 0 | 0 | 0 |
| Hardware Specifications | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run at nice 10 on a machine shared with other jobs (load about 70-80) | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run at nice 10 on a machine shared with other jobs (load about 70-80) | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run at nice 10 on a machine shared with other jobs (load about 70-80) |
| Total Runtime | 30.0 | 3600.0 | 7200.0 |
| Time to Solution | 22.3 | 1369.6 | 1991.9 |
| CPU Runtime | 12.6 | 1684.6 | 3023.9 |
| GPU Runtime | N/A | N/A | N/A |
| QPU Runtime | N/A | N/A | N/A |
| Other HW Runtime | N/A | N/A | N/A |
| Remarks | 30 s runs, seeds 1-5: Best stable set 95 over these 5 runs (listed best known 96: ours is below it). seed 1 (limit 30 s): 95, first reached at 27.7 s, run ended at 30.0 s wall / 12.4 s CPU; seed 2 (limit 30 s): 94, first reached at 19.2 s, run ended at 30.0 s wall / 12.6 s CPU; seed 3 (limit 30 s): 94, first reached at 14.1 s, run ended at 30.0 s wall / 12.8 s CPU; seed 4 (limit 30 s): 94, first reached at 25.0 s, run ended at 30.0 s wall / 12.3 s CPU; seed 5 (limit 30 s): 94, first reached at 25.3 s, run ended at 30.0 s wall / 12.7 s CPU. Total Runtime is the mean wall-clock time per run and CPU Runtime the mean process CPU time; the machine was shared, so a run waited for a free core part of the time and its CPU time is below its wall-clock time. Time to Solution is the mean wall-clock time at which each run first reached its own best. Optimality Bound N/A: the method computes no bound. | Longer runs, seeds 1-5, limit 3600 s: Best stable set 97 over these 5 runs (listed best known 96: ours is above it). seed 1 (limit 3600 s): 97, first reached at 2517.2 s, run ended at 3600.0 s wall (CPU time not recorded); seed 2 (limit 3600 s): 97, first reached at 1811.0 s, run ended at 3600.0 s wall / 1833.3 s CPU; seed 3 (limit 3600 s): 97, first reached at 850.5 s, run ended at 3600.0 s wall / 1475.5 s CPU; seed 4 (limit 3600 s): 96, first reached at 137.5 s, run ended at 3600.0 s wall / 1573.2 s CPU; seed 5 (limit 3600 s): 97, first reached at 1531.8 s, run ended at 3600.0 s wall / 1856.3 s CPU. Total Runtime is the mean wall-clock time per run and CPU Runtime the mean process CPU time over the runs that recorded it; the machine was shared, so a run waited for a free core part of the time and its CPU time is below its wall-clock time. Time to Solution is the mean wall-clock time at which each run first reached its own best. Optimality Bound N/A: the method computes no bound. | Longer runs, seeds 6-7, limit 7200 s: Best stable set 97 over these 2 runs (listed best known 96: ours is above it). seed 6 (limit 7200 s): 96, first reached at 332.5 s, run ended at 7200.0 s wall / 3023.7 s CPU; seed 7 (limit 7200 s): 97, first reached at 3651.3 s, run ended at 7200.0 s wall / 3024.1 s CPU. Total Runtime is the mean wall-clock time per run and CPU Runtime the mean process CPU time; the machine was shared, so a run waited for a free core part of the time and its CPU time is below its wall-clock time. Time to Solution is the mean wall-clock time at which each run first reached its own best. Optimality Bound N/A: the method computes no bound. |
