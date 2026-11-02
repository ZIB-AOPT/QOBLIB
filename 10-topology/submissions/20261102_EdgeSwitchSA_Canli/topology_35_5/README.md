# Submission for topology_35_5

This directory contains the submission for the problem **topology_35_5**.

| Field | Value 1 |
| --- | --- |
| Problem | topology_35_5 |
| Submitter | Arhan Canli |
| Affiliation | Quantavane |
| Date | 2026-11-02 |
| Reference | https://github.com/ZIB-AOPT/QOBLIB/tree/main/10-topology/submissions/20261102_EdgeSwitchSA_Canli |
| Best Objective Value | 3 |
| Optimality Bound | 3 |
| Modeling Approach | Direct search over graphs (no MIP or QUBO model): fixed degree sequence, degree-preserving edge switches |
| # Decision Variables | 595 |
| # Binary Variables | 595 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| Workflow | Start from a circulant graph with every degree d (one node at d-1 when n*d is odd), scrambled by random degree-preserving switches; simulated annealing over switches (edges ab, ce become ac, be) on cost = (ordered pairs further apart than the target diameter) + (sum over k < target of pairs further apart than k); geometric cooling 8 -> 0.5 over 10,000,000 moves per round, reheating from the round best; stop at the first graph of diameter <= target; graph re-checked by an independent BFS program. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | 10 |
| Success Threshold | 0 |
| Hardware Specifications | Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2; one single-threaded process per run on a shared machine (nice 10) |
| Total Runtime | 0.01 |
| Time to Solution | 0.01 |
| CPU Runtime | 0.00 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| Remarks | Diameter 3 (previous best known 4). Lower bound 3: Moore bound: with maximum degree 5 a graph of diameter 2 has at most 1 + 5 + 20 = 26 nodes. 10 of 10 seeded runs (seeds 1-10) reached diameter 3; the solution file is the graph of seed 1 (143 moves). Runtimes are means over the 10 runs (wall clock and user+system CPU time, measured with /usr/bin/time). |
