# Submission for es60fst04

This directory contains the submission for the problem **es60fst04**.

| Field | Value 1 |
| --- | --- |
| Problem | es60fst04 |
| Submitter | Arhan Canli |
| Affiliation | Quantavane |
| Date | 2026-11-02 |
| Reference | https://github.com/arhancanli/quantavane-qoblib |
| Best Objective Value | 78 |
| Optimality Bound | N/A |
| Modeling Approach | Direct search (no MIP or QUBO model): minimum vertex cover local search, the stable set is the complement of the cover |
| # Decision Variables | 162 |
| # Binary Variables | 162 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| Workflow | Greedy vertex cover, then NuMVC local search (Cai et al. 2013): two-stage exchange, edge weighting with forgetting (gamma = n/2, rho = 0.3), configuration checking; every cover found is recorded and one vertex removed to look for a smaller one; each run ends at its wall-clock limit; stable set = complement of the best cover, re-checked by an independent program. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| Hardware Specifications | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run at nice 10 on a machine shared with other jobs (load about 70-80) |
| Total Runtime | 30.0 |
| Time to Solution | 0.0 |
| CPU Runtime | 12.6 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| Remarks | 30 s runs, seeds 1-5: Best stable set 78 over these 5 runs (listed best known 78: ours is equal to it). seed 1 (limit 30 s): 78, first reached at 0.0 s, run ended at 30.0 s wall / 12.5 s CPU; seed 2 (limit 30 s): 78, first reached at 0.0 s, run ended at 30.0 s wall / 12.5 s CPU; seed 3 (limit 30 s): 78, first reached at 0.0 s, run ended at 30.0 s wall / 12.4 s CPU; seed 4 (limit 30 s): 78, first reached at 0.0 s, run ended at 30.0 s wall / 12.8 s CPU; seed 5 (limit 30 s): 78, first reached at 0.0 s, run ended at 30.0 s wall / 12.6 s CPU. Total Runtime is the mean wall-clock time per run and CPU Runtime the mean process CPU time; the machine was shared, so a run waited for a free core part of the time and its CPU time is below its wall-clock time. Time to Solution is the mean wall-clock time at which each run first reached its own best. Optimality Bound N/A: the method computes no bound. |
