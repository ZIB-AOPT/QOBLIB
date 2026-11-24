# Submission for network06

This directory contains the submission for the problem **network06**.

| Field | Value 1 |
| --- | --- |
| Problem | network06 |
| Submitter | Manan Gupta |
| Affiliation | The Harker School |
| Date | 2026-08-18 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-solvers/tree/6a85c438851383a7943f9af29631b6a573699169/network |
| Best Objective Value | 101000 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Reference integer multicommodity flow model of d3ver0int.zpl, decomposed into a topology search over 2-in/2-out digraphs with an exact min-congestion flow solved for each candidate |
| # Decision Variables | 181 |
| # Binary Variables | 30 |
| # Integer Variables | 151 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 810 |
| Coefficients Type | Integer |
| Coefficients Range | 1 - 1000000 |
| ====== |  |
| Workflow | Parallel tempering over 2-in/2-out digraphs with eight replicas. The temperatures form a geometric ladder from 6% down to 0.2% of the best energy among the starting topologies. A move is a 2-exchange (85% of proposals) or a 3-exchange (15%) of arc heads, which keeps every in and out degree at 2. A proposal is discarded if it would create a loop or a repeated arc, or if the digraph is no longer strongly connected. Adjacent replicas try to swap every 40 proposals. The energy of a topology is the min-congestion multicommodity flow LP for it, solved with HiGHS. Every replica starts from an independently sampled random 2-in/2-out topology, and no published solution is read. The integral routing is recovered once at the end by re-solving the same model with integrality on the flow variables. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M3 Pro (Mac15,6), 11 cores (5 performance + 6 efficiency), 18 GB unified memory, arm64. Runs executed strictly one at a time. The machine was not kept otherwise idle during the runs of 2026-09-21 to 2026-09-23: 17 of the 100 runs show 33% to 78% of the highest evaluation rate seen for their instance. |
| ====== |  |
| Total Runtime | 1800.0 |
| Time to Solution | 0.4 |
| CPU Runtime | N/A |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Heuristic, so the optimality bound is left as N/A. Total Runtime is the mean wall clock time of the search loop over the five runs (seeds 0 to 4, 1800 s budget, one process per run); it excludes the setup and the final integral re-solve, which were not timed. CPU time was not recorded for these runs, so CPU Runtime is N/A. Time to solution is the average over runs of the moment each run last improved its incumbent. This run reaches the published value exactly without improving it; on network05 to network10 that value is the proven optimum. Successful runs are those reaching this method's own best value. The declared objective is recomputed from the flows rather than taken from the solver's z variable, which the model only bounds from below. Verified with 08-network/check. |
