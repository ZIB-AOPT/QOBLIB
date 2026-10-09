# Submission for stp_s030_l4_t4_h0_rs97531

This directory contains the submission for the problem **stp_s030_l4_t4_h0_rs97531**.

| Field | Value 1 |
| --- | --- |
| Problem | stp_s030_l4_t4_h0_rs97531 |
| Submitter | Manan Gupta |
| Affiliation | The Harker School |
| Date | 2026-10-09 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-solvers/tree/main/steiner |
| Best Objective Value | 483 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | No optimisation model is built. Routing heuristic on the arc graph; variable counts describe the emitted routing. |
| # Decision Variables | 483 |
| # Binary Variables | 0 |
| # Integer Variables | 483 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | Negotiated congestion routing (PathFinder style rip up and reroute). Each net is routed as a greedy Steiner tree by multi source Dijkstra from the partial tree to the nearest unconnected terminal. Node cost is base cost plus present overuse times a pressure factor that grows by 1.5 each iteration, plus an accumulated history penalty; iterate until no node is shared by two nets. Then prune non terminal leaves and run three cost polish passes rerouting each net with the other nets' nodes forbidden. Routing order is shuffled by the seed. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 30 |
| # Feasible Runs | 30 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M3 Pro (Mac15,6), 11 cores (5 performance + 6 efficiency), 18 GB unified memory, macOS 26.3, arm64. Runs executed strictly one at a time on an otherwise idle machine. |
| ====== |  |
| Total Runtime | 0.358 |
| Time to Solution | 0.358 |
| CPU Runtime | 0.358 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Does not reach the published value 480; included so the method stays comparable. Runtimes are the average over the independent runs. Successful runs are those reaching this method's own best value. The objective is the total arc cost of the routing. Verified with 04-steiner/check. |
