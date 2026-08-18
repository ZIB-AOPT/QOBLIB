# Submission for network17

This directory contains the submission for the problem **network17**.

| Field | Value 1 |
| --- | --- |
| Problem | network17 |
| Submitter | Manan Gupta |
| Affiliation | The Harker School |
| Date | 2026-08-18 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-solvers/tree/main/network |
| Best Objective Value | 434429 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Reference integer multicommodity flow model of d3ver0int.zpl, decomposed into a topology search over 2-in/2-out digraphs with an exact min-congestion flow solved for each candidate |
| # Decision Variables | 4625 |
| # Binary Variables | 272 |
| # Integer Variables | 4353 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 22848 |
| Coefficients Type | Integer |
| Coefficients Range | 1 - 1000000 |
| ====== |  |
| Workflow | Parallel tempering over 2-in/2-out digraphs. Eight replicas on a geometric temperature ladder from 6% to 0.2% of the incumbent energy; moves are degree-preserving 2- and 3-exchanges on the arc set, so every proposal is feasible by construction and only strong connectivity is rechecked; replica exchange every 40 proposals. A replica's energy is the exact min-congestion multicommodity flow LP for its topology, solved with HiGHS. Half the replicas start from the published reference topology and half from random topologies. The integral routing is recovered once at the end by re-solving the same model with integrality on the flow variables. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M-series laptop, 11 cores, 18 GB RAM, macOS; single core per run |
| ====== |  |
| Total Runtime | 1200.0 |
| Time to Solution | 580.1 |
| CPU Runtime | 1200.0 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Heuristic, so the optimality bound is left as N/A. Runtimes are the average over the independent runs, single core each, queueing excluded. Time to solution is the average over runs of the moment each run last improved its incumbent. Successful runs are those reaching this method's own best value. Verified with 08-network/check. |
