# Submission for topology_20_5

This directory contains the submission for the problem **topology_20_5**.

| Field | Value 1 |
| --- | --- |
| Problem | topology_20_5 |
| Submitter | Arhan Canli |
| Affiliation | Quantavane |
| Date | 2026-11-02 |
| Reference | https://github.com/arhancanli/quantavane-qoblib |
| Best Objective Value | 2 |
| Optimality Bound | 2 |
| Modeling Approach | Direct search over graphs (no MIP or QUBO model): fixed degree sequence, degree-preserving edge switches |
| # Decision Variables | 190 |
| # Binary Variables | 190 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| Workflow | Start: circulant graph with every degree d (one node at d-1 when n*d is odd), scrambled by 20\|E\| random degree-preserving switches; its diameter is the first incumbent. Then simulated annealing over switches (edges ab, ce become ac, be) towards diameter incumbent-1, cost = (ordered pairs further apart than the target) + (sum over k < target of pairs further apart than k), geometric cooling 8 -> 0.5 over 10000000 moves per round, reheating from the round best; each graph meeting the target becomes the incumbent and the target drops by one. The Moore lower bound is computed in the run; the target never goes below it and the run stops when the incumbent equals it (proven optimal); otherwise it ends at 150 s CPU or after 60 s CPU without a new incumbent. Graphs re-checked by an independent BFS program. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| Hardware Specifications | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run at nice 10 on a machine shared with other jobs (load about 70-80) |
| Total Runtime | 1.14 |
| Time to Solution | 1.14 |
| CPU Runtime | 1.14 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| Remarks | Best diameter 2 over 5 seeded runs (listed best known 2: ours is equal to it). Optimality Bound 2 is the Moore lower bound computed by the method (attained: proven optimal). seed 1: diameter 2 (start 4) reached at 1.18 s, run ended at 1.18 s (proven optimal: equals the lower bound); seed 2: diameter 2 (start 3) reached at 1.15 s, run ended at 1.15 s (proven optimal: equals the lower bound); seed 3: diameter 2 (start 3) reached at 1.15 s, run ended at 1.15 s (proven optimal: equals the lower bound); seed 4: diameter 2 (start 3) reached at 1.05 s, run ended at 1.05 s (proven optimal: equals the lower bound); seed 5: diameter 2 (start 3) reached at 1.18 s, run ended at 1.18 s (proven optimal: equals the lower bound). All times are the single-threaded process's own CPU time (user + system), which excludes any time spent waiting for a core on the shared machine; Total Runtime and CPU Runtime are the mean time per run, Time to Solution the mean time at which each run first reached its own final diameter. The solution file is the graph of seed 1. Objective time series: all 5 runs, seeds 1-5 in order, times in CPU seconds. |
