# Submission for network12

This directory contains the submission for the problem **network12**.

| Field | Value 1 |
| --- | --- |
| Problem | network12 |
| Submitter | Manan Gupta |
| Affiliation | The Harker School |
| Date | 2026-11-22 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-solvers/tree/5b959cbb50c464a02cfee93575f02de4d966094a/network |
| Best Objective Value | 276474 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Reference integer multicommodity flow model of d3ver0int.zpl, decomposed into a topology search over 2-in/2-out digraphs with an exact min-congestion flow solved for each candidate |
| # Decision Variables | 1585 |
| # Binary Variables | 132 |
| # Integer Variables | 1453 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 7524 |
| Coefficients Type | Integer |
| Coefficients Range | 1 - 1000000 |
| ====== |  |
| Workflow | Parallel tempering over 2-in/2-out digraphs with 8 replicas. The temperatures form a geometric ladder from 6% down to 0.2% of the best energy among the starting topologies. A move is a 2-exchange (85% of proposals) or a 3-exchange (15%) of arc heads, which keeps every in and out degree at 2. A proposal is discarded if it would create a loop or a repeated arc, or if the digraph is no longer strongly connected. Adjacent replicas try to swap every 40 proposals. The energy of a topology is the min-congestion multicommodity flow LP for it, solved with HiGHS on one thread. Every replica starts from a random 2-in/2-out topology drawn from the run's seed, and no published solution is read. At the end the integral routing of the best topology is computed once by solving the same model with integer flows, and the solution is checked with 08-network/check. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 2 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M3 Pro (Mac15,6), 11 cores (5 performance + 6 efficiency), 18 GB unified memory, arm64, macOS 26.3, on AC power; Python 3.11.7, HiGHS 1.15.1. Runs executed strictly one at a time, each on a single thread; one run that overlapped another process on the machine was discarded and run again with the same seed. |
| ====== |  |
| Total Runtime | 7200.1 |
| Time to Solution | 3675.7 |
| CPU Runtime | 7190.0 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Reaches the table value 276474 (best known). Heuristic, so the optimality bound is N/A. 5 independent runs from scratch, seeds 0, 1, 2, 3, 4, each with 8 replicas and 7200 s of search followed by the integral routing, strictly one run at a time. Run values: 277527, 277572, 277000, 276474, 276474. Time to Solution is the mean time from the start of the run until the best topology was found, over the 2 successful runs (runs reaching the reported value); its integral routing is computed at the end of the run and takes under a second. Total Runtime is the mean wall clock time and CPU Runtime the mean process CPU time over all runs, both including the integral routing. Each run is single threaded, so CPU time stays just under wall time. The declared objective is recomputed from the flows rather than taken from the solver's z variable, which the model only bounds from below. Verified with 08-network/check. |
