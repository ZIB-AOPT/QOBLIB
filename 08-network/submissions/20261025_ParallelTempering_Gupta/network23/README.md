# Submission for network23

This directory contains the submission for the problem **network23**.

| Field | Value 1 |
| --- | --- |
| Problem | network23 |
| Submitter | Manan Gupta |
| Affiliation | The Harker School |
| Date | 2026-10-25 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-solvers/tree/main/network |
| Best Objective Value | 648241 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Reference integer multicommodity flow model of d3ver0int.zpl, decomposed into a topology search over 2-in/2-out digraphs with an exact min-congestion flow solved for each candidate |
| # Decision Variables | 11639 |
| # Binary Variables | 506 |
| # Integer Variables | 11133 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 57684 |
| Coefficients Type | Integer |
| Coefficients Range | 1 - 1000000 |
| ====== |  |
| Workflow | Parallel tempering over 2-in/2-out digraphs. Eight (or twelve, see remarks) replicas on a geometric temperature ladder from 6% to 0.2% of the incumbent energy; moves are degree-preserving 2- and 3-exchanges on the arc set, so every proposal is feasible by construction and only strong connectivity is rechecked; replica exchange every 40 proposals. A replica's energy is the exact min-congestion multicommodity flow LP for its topology, solved with HiGHS. Every replica starts from an independently sampled random 2-in/2-out topology; the published solutions are never read by the search. The integral routing is recovered once at the end by re-solving the same model with integrality on the flow variables. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Cloud CPU container: 32 hardware threads of an AMD EPYC 9B45 host, 128 GB memory limit, Ubuntu 20.04, Python 3.12 with HiGHS, no GPU. Eight single threaded runs executed concurrently in the container; the host is shared with other tenants and showed high load, so wall clock times are indicative only. |
| ====== |  |
| Total Runtime | 8640.0 |
| Time to Solution | 4281.4 |
| CPU Runtime | 8640.0 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Heuristic, so the optimality bound is left as N/A. Runs: six runs of eight replicas for 7200 s each (seeds 0 to 5) and four runs of twelve replicas for 10800 s each (seeds 10 to 13). Runtimes are the average over all those runs, single core each, queueing excluded. Time to solution is the average over runs of the moment each run last improved its incumbent. Successful runs are those reaching this method's own best value. The declared objective is recomputed from the flows rather than taken from the solver's z variable, which the model only bounds from below. Verified with 08-network/check. |
