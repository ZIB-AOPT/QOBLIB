# Submission for stp_s090_l2_t3_h2_rs24098

This directory contains the submission for the problem **stp_s090_l2_t3_h2_rs24098**.

| Field | Value 1 |
| --- | --- |
| Problem | stp_s090_l2_t3_h2_rs24098 |
| Submitter | Manan Gupta |
| Affiliation | The Harker School |
| Date | 2026-10-30 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-solvers/tree/main/steiner |
| Best Objective Value | 934 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | No optimisation model is built. Routing heuristic on the arc graph; variable counts describe the emitted routing. |
| # Decision Variables | 935 |
| # Binary Variables | 0 |
| # Integer Variables | 935 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | Negotiated congestion routing (PathFinder style rip up and reroute). Each net is routed as a greedy Steiner tree by multi source Dijkstra from the partial tree to the nearest unconnected terminal. Node cost is base cost plus present overuse times a pressure factor that grows by 1.5 each iteration, plus an accumulated history penalty; iterate until no node is shared by two nets. Then prune non terminal leaves and run three cost polish passes rerouting each net with the other nets' nodes forbidden. Routing order is shuffled by the seed. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 18 |
| # Feasible Runs | 18 |
| # Successful Runs | 4 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M3 Pro (Mac15,6), 11 cores (5 performance + 6 efficiency), 18 GB unified memory, macOS 26.3, arm64. Runs executed strictly one at a time on an otherwise idle machine. The last 8 runs: Apple M3 Pro laptop, 11 CPU cores, 18 GB RAM, macOS 26.3, Python 3.11 with scipy, no GPU, on AC power, up to 12 single threaded jobs at once, so wall clock times are indicative only. |
| ====== |  |
| Total Runtime | 400.9 |
| Time to Solution | 400.9 |
| CPU Runtime | 400.9 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | No feasible solution was on record for this instance before this submission. Runtimes are the average over the independent runs. Successful runs are those reaching this method's own best value. The objective is the total arc cost of the routing. Verified with 04-steiner/check. |
