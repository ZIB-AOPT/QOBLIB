# Submission for topology_9344_6

This directory contains the submission for the problem **topology_9344_6**.

| Field | Value 1 |
| --- | --- |
| Problem | topology_9344_6 |
| Submitter | Arhan Canli |
| Affiliation | Quantavane |
| Date | 2026-11-02 |
| Reference | https://github.com/arhancanli/quantavane-qoblib |
| Best Objective Value | 8 |
| Optimality Bound | 6 |
| Modeling Approach | Direct search over graphs (no MIP or QUBO model): fixed degree sequence, degree-preserving edge switches |
| # Decision Variables | 43650496 |
| # Binary Variables | 43650496 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| Workflow | Start: circulant graph with every degree d (one node at d-1 when n*d is odd), scrambled by 20\|E\| random degree-preserving switches; its diameter is the first incumbent. Then simulated annealing over switches (edges ab, ce become ac, be) towards diameter incumbent-1, cost = (ordered pairs further apart than the target) + (sum over k < target of pairs further apart than k), geometric cooling 8 -> 0.5 over 1000 moves per round, reheating from the round best; each graph meeting the target becomes the incumbent and the target drops by one. The Moore lower bound is computed in the run; the target never goes below it and the run stops when the incumbent equals it (proven optimal); otherwise it ends at 120 s CPU or after 60 s CPU without a new incumbent. Graphs re-checked by an independent BFS program. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| Hardware Specifications | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run at nice 10 on a machine shared with other jobs (load about 70-80) |
| Total Runtime | 60.63 |
| Time to Solution | 0.09 |
| CPU Runtime | 60.63 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| Remarks | Best diameter 8 over 5 seeded runs (listed best known 7: ours is above it). Optimality Bound 6 is the Moore lower bound computed by the method. seed 1: diameter 8 (start 8) reached at 0.08 s, run ended at 60.10 s; seed 2: diameter 8 (start 8) reached at 0.09 s, run ended at 60.85 s; seed 3: diameter 8 (start 8) reached at 0.09 s, run ended at 60.86 s; seed 4: diameter 8 (start 8) reached at 0.09 s, run ended at 60.43 s; seed 5: diameter 8 (start 8) reached at 0.08 s, run ended at 60.91 s. All times are the single-threaded process's own CPU time (user + system), which excludes any time spent waiting for a core on the shared machine; Total Runtime and CPU Runtime are the mean time per run, Time to Solution the mean time at which each run first reached its own final diameter. The solution file is the graph of seed 1. Objective time series: all 5 runs, seeds 1-5 in order, times in CPU seconds. |
