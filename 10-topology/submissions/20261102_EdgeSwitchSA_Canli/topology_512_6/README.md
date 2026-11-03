# Submission for topology_512_6

This directory contains the submission for the problem **topology_512_6**.

| Field | Value 1 |
| --- | --- |
| Problem | topology_512_6 |
| Submitter | Arhan Canli |
| Affiliation | Quantavane |
| Date | 2026-11-02 |
| Reference | https://github.com/arhancanli/quantavane-qoblib |
| Best Objective Value | 5 |
| Optimality Bound | N/A |
| Modeling Approach | Direct search over graphs (no MIP or QUBO model): fixed degree sequence, degree-preserving edge switches |
| # Decision Variables | 130816 |
| # Binary Variables | 130816 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| Workflow | Start: circulant graph with every degree d (one node at d-1 when n*d is odd), scrambled by 20\|E\| random degree-preserving switches; its diameter is the first incumbent. Then simulated annealing over switches (edges ab, ce become ac, be) towards diameter incumbent-1, cost = (ordered pairs further apart than the target) + (sum over k < target of pairs further apart than k), geometric cooling 8 -> 0.5 over 200000 moves per round, reheating from the round best; each graph meeting the target becomes the incumbent and the target drops by one. Run ends at 120 s CPU or after 60 s CPU without a new incumbent; no bound or known value is used. Graphs re-checked by an independent BFS program. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| Hardware Specifications | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run at nice 10 on a machine shared with other jobs (load about 70-80) |
| Total Runtime | 150.94 |
| Time to Solution | 0.02 |
| CPU Runtime | 60.02 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| Remarks | Best diameter 5 over 5 seeded runs (listed best known 5: ours is equal to it). seed 1: diameter 5 (start 6) first reached at 0.0 s wall / 0.0 s CPU, run ended at 151.1 s wall / 60.0 s CPU; seed 2: diameter 5 (start 6) first reached at 0.0 s wall / 0.0 s CPU, run ended at 150.8 s wall / 60.0 s CPU; seed 3: diameter 5 (start 6) first reached at 0.0 s wall / 0.0 s CPU, run ended at 150.9 s wall / 60.0 s CPU; seed 4: diameter 5 (start 6) first reached at 0.0 s wall / 0.0 s CPU, run ended at 151.0 s wall / 60.0 s CPU; seed 5: diameter 5 (start 6) first reached at 0.0 s wall / 0.0 s CPU, run ended at 150.8 s wall / 60.0 s CPU. Total Runtime and CPU Runtime are means per run (wall clock and process CPU time; the machine was shared, so a run waited for a free core part of the time and its CPU time is below its wall-clock time). Time to Solution is the mean wall-clock time at which each run first reached its own final diameter. The solution file is the graph of seed 1. Objective time series: all 5 runs, seeds 1-5 in order. |
