# Submission for topology_15_4

This directory contains the submission for the problem **topology_15_4**.

| Field | Value 1 |
| --- | --- |
| Problem | topology_15_4 |
| Submitter | Arhan Canli |
| Affiliation | Quantavane |
| Date | 2026-11-02 |
| Reference | https://github.com/arhancanli/quantavane-qoblib |
| Best Objective Value | 2 |
| Optimality Bound | N/A |
| Modeling Approach | Direct search over graphs (no MIP or QUBO model): fixed degree sequence, degree-preserving edge switches |
| # Decision Variables | 105 |
| # Binary Variables | 105 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| Workflow | Start: circulant graph with every degree d (one node at d-1 when n*d is odd), scrambled by 20\|E\| random degree-preserving switches; its diameter is the first incumbent. Then simulated annealing over switches (edges ab, ce become ac, be) towards diameter incumbent-1, cost = (ordered pairs further apart than the target) + (sum over k < target of pairs further apart than k), geometric cooling 8 -> 0.5 over 10000000 moves per round, reheating from the round best; each graph meeting the target becomes the incumbent and the target drops by one. Run ends at 150 s CPU or after 60 s CPU without a new incumbent; no bound or known value is used. Graphs re-checked by an independent BFS program. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| Hardware Specifications | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run at nice 10 on a machine shared with other jobs (load about 70-80) |
| Total Runtime | 152.00 |
| Time to Solution | 0.06 |
| CPU Runtime | 60.06 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| Remarks | Best diameter 2 over 5 seeded runs (listed best known 2: ours is equal to it). seed 1: diameter 2 (start 3) first reached at 0.0 s wall / 0.0 s CPU, run ended at 150.8 s wall / 60.0 s CPU; seed 2: diameter 2 (start 4) first reached at 0.1 s wall / 0.1 s CPU, run ended at 152.6 s wall / 60.1 s CPU; seed 3: diameter 2 (start 3) first reached at 0.1 s wall / 0.1 s CPU, run ended at 152.6 s wall / 60.1 s CPU; seed 4: diameter 2 (start 3) first reached at 0.0 s wall / 0.0 s CPU, run ended at 152.1 s wall / 60.0 s CPU; seed 5: diameter 2 (start 3) first reached at 0.1 s wall / 0.1 s CPU, run ended at 151.9 s wall / 60.1 s CPU. Total Runtime and CPU Runtime are means per run (wall clock and process CPU time; the machine was shared, so a run waited for a free core part of the time and its CPU time is below its wall-clock time). Time to Solution is the mean wall-clock time at which each run first reached its own final diameter. The solution file is the graph of seed 1. Objective time series: all 5 runs, seeds 1-5 in order. |
