# Submission for network24

This directory contains the submission for the problem **network24**.

| Field | Value 1 |
| --- | --- |
| Problem | network24 |
| Submitter | Manan Gupta |
| Affiliation | The Harker School |
| Date | 2026-11-23 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-solvers/tree/ebb9d76c343accef20c53b72e9f8ae2e8ba68a0c/network |
| Best Objective Value | 694584 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Reference integer multicommodity flow model of d3ver0int.zpl, decomposed into a topology search over 2-in/2-out digraphs with an exact min-congestion flow solved for each candidate |
| # Decision Variables | 13249 |
| # Binary Variables | 552 |
| # Integer Variables | 12697 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 64584 |
| Coefficients Type | Integer |
| Coefficients Range | 1 - 1000000 |
| ====== |  |
| Workflow | Parallel tempering over 2-in/2-out digraphs with 8 replicas. The temperatures form a geometric ladder from 6% down to 0.2% of the best energy among the starting topologies. A move is a 2-exchange (85% of proposals) or a 3-exchange (15%) of arc heads, which keeps every in and out degree at 2. A proposal is discarded if it would create a loop or a repeated arc, or if the digraph is no longer strongly connected. Adjacent replicas try to swap every 40 proposals. The energy of a topology is the min-congestion multicommodity flow LP for it, solved with HiGHS on one thread. Every replica starts from a random 2-in/2-out topology drawn from the run's seed, and no published solution is read. At the end the integral routing of the best topology is computed once by solving the same model with integer flows, and the solution is checked with 08-network/check. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M3 Pro (Mac15,6), 11 cores (5 performance + 6 efficiency), 18 GB unified memory, arm64, macOS 26.3, on AC power; Python 3.11.7, HiGHS 1.15.1. Runs executed strictly one at a time, each on a single thread. The laptop was not kept otherwise idle: the search evaluation rate of a run is 86% to 100% of the fastest run of the same instance. One run that overlapped a leftover benchmark process was discarded and run again with the same seed. |
| ====== |  |
| Total Runtime | 7200.6 |
| Time to Solution | 4186.4 |
| CPU Runtime | 7184.0 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Does not reach the table value 663688 (best known); included so the method stays comparable. Heuristic, so the optimality bound is N/A. 5 independent runs from scratch, seeds 0, 1, 2, 3, 4, each with 8 replicas and 7200 s of search followed by the integral routing, strictly one run at a time. The seeds are those of the 2026-08-18 runs, and on this machine the search repeats itself for a given seed, so each run retraces the 1800 s run of its seed and then continues. Run values: 694681, 694584, 696688, 699929, 703447. Time to Solution is the mean time from the start of the run until the best topology was found, over the 1 successful run (runs reaching the reported value); its integral routing is computed at the end of the run and takes under a second. Total Runtime is the mean wall clock time and CPU Runtime the mean process CPU time over all runs, both including the integral routing. Each run is single threaded, so CPU time stays just under wall time. The declared objective is recomputed from the flows rather than taken from the solver's z variable, which the model only bounds from below. Verified with 08-network/check. |
