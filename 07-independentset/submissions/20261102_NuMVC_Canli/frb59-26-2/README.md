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
| Optimality Bound | N/A | N/A |
| Modeling Approach | Direct search (no MIP or QUBO model): minimum vertex cover local search, the stable set is the complement of the cover | Direct search (no MIP or QUBO model): minimum vertex cover local search, the stable set is the complement of the cover |
| # Decision Variables | 1534 | 1534 |
| # Binary Variables | 1534 | 1534 |
| # Integer Variables | 0 | 0 |
| # Continuous Variables | 0 | 0 |
| # Non-Zero Coefficients | N/A | N/A |
| Coefficients Type | N/A | N/A |
| Coefficients Range | N/A | N/A |
| Workflow | Greedy vertex cover, then NuMVC local search (Cai et al. 2013): two-stage exchange, edge weighting with forgetting (gamma = n/2, rho = 0.3), configuration checking; every cover found is recorded and one vertex removed to look for a smaller one; each run ends at its wall-clock limit; stable set = complement of the best cover, re-checked by an independent program. | Greedy vertex cover, then NuMVC local search (Cai et al. 2013): two-stage exchange, edge weighting with forgetting (gamma = n/2, rho = 0.3), configuration checking; every cover found is recorded and one vertex removed to look for a smaller one; each run ends at its wall-clock limit; stable set = complement of the best cover, re-checked by an independent program. |
| Algorithm Type | Stochastic | Stochastic |
| Paradigm | Classical | Classical |
| # Runs | 5 | 5 |
| # Feasible Runs | 5 | 5 |
| # Successful Runs | 3 | 1 |
| Success Threshold | 0 | 0 |
| Hardware Specifications | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run at nice 10 on a machine shared with other jobs (load about 70-80) | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run at nice 10 on a machine shared with other jobs (load about 70-80) |
| Total Runtime | 30.0 | 1677.2 |
| Time to Solution | 7.4 | 229.9 |
| CPU Runtime | 12.5 | 847.5 |
| GPU Runtime | N/A | N/A |
| QPU Runtime | N/A | N/A |
| Other HW Runtime | N/A | N/A |
| Remarks | 30 s runs, seeds 1-5: Best stable set 58 over these 5 runs (listed best known 58: ours is equal to it). seed 1 (limit 30 s): 57, first reached at 1.5 s, run ended at 30.0 s wall / 12.5 s CPU; seed 2 (limit 30 s): 58, first reached at 16.8 s, run ended at 30.0 s wall / 12.5 s CPU; seed 3 (limit 30 s): 58, first reached at 12.1 s, run ended at 30.0 s wall / 12.6 s CPU; seed 4 (limit 30 s): 58, first reached at 4.1 s, run ended at 30.0 s wall / 12.5 s CPU; seed 5 (limit 30 s): 57, first reached at 2.5 s, run ended at 30.0 s wall / 12.6 s CPU. Total Runtime is the mean wall-clock time per run and CPU Runtime the mean process CPU time; the machine was shared, so a run waited for a free core part of the time and its CPU time is below its wall-clock time. Time to Solution is the mean wall-clock time at which each run first reached its own best. Optimality Bound N/A: the method computes no bound. | Longer runs, seeds 1-5 (seed 1: limit 3600 s, ended by hand after reaching 59; seeds 2-5: limit 1800 s, set to end early at 59, which none reached): Best stable set 59 over these 5 runs (listed best known 58: ours is above it). seed 1 (limit 3600 s): 59, first reached at 1085.8 s, run ended at 1186.0 s wall (CPU time not recorded); ended by hand at 1186 s, after it had reached 59; seed 2 (limit 1800 s): 58, first reached at 15.4 s, run ended at 1800.0 s wall / 830.0 s CPU; seed 3 (limit 1800 s): 58, first reached at 10.8 s, run ended at 1800.0 s wall / 858.7 s CPU; seed 4 (limit 1800 s): 58, first reached at 3.7 s, run ended at 1800.0 s wall / 830.3 s CPU; seed 5 (limit 1800 s): 58, first reached at 33.9 s, run ended at 1800.0 s wall / 871.2 s CPU. Total Runtime is the mean wall-clock time per run and CPU Runtime the mean process CPU time over the runs that recorded it; the machine was shared, so a run waited for a free core part of the time and its CPU time is below its wall-clock time. Time to Solution is the mean wall-clock time at which each run first reached its own best. Optimality Bound N/A: the method computes no bound. |
