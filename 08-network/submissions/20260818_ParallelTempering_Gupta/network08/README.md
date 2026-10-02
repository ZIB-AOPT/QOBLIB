# Submission for network08

This directory contains the submission for the problem **network08**.

| Field | Value 1 |
| --- | --- |
| Problem | network08 |
| Submitter | Manan Gupta |
| Affiliation | The Harker School |
| Date | 2026-08-18 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-solvers/tree/main/network |
| Best Objective Value | 170231 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Reference integer multicommodity flow model of d3ver0int.zpl, decomposed into a topology search over 2-in/2-out digraphs with an exact min-congestion flow solved for each candidate |
| # Decision Variables | 449 |
| # Binary Variables | 56 |
| # Integer Variables | 393 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 2184 |
| Coefficients Type | Integer |
| Coefficients Range | 1 - 1000000 |
| ====== |  |
| Workflow | Parallel tempering over 2-in/2-out digraphs. Eight replicas on a geometric temperature ladder from 6% to 0.2% of the incumbent energy; moves are degree-preserving 2- and 3-exchanges on the arc set, so every proposal is feasible by construction and only strong connectivity is rechecked; replica exchange every 40 proposals. A replica's energy is the exact min-congestion multicommodity flow LP for its topology, solved with HiGHS. Every replica starts from an independently sampled random 2-in/2-out topology; the published solutions are never read by the search. The integral routing is recovered once at the end by re-solving the same model with integrality on the flow variables. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M3 Pro (Mac15,6), 11 cores (5 performance + 6 efficiency), 18 GB unified memory, macOS 26.3, arm64; one core per run |
| ====== |  |
| Total Runtime | 2400.0 |
| Time to Solution | 8.0 |
| CPU Runtime | 2400.0 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Heuristic, so the optimality bound is left as N/A. Runtimes are the average over the independent runs, single core each, queueing excluded. Time to solution is the average over runs of the moment each run last improved its incumbent. This run does not reach the published best-known value and is included so the method stays comparable over time rather than only appearing where it wins. Successful runs are those reaching this method's own best value. The declared objective is recomputed from the flows rather than taken from the solver's z variable, which the model only bounds from below. Verified with 08-network/check. |
