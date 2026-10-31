# Submission for stp_s090_l2_t5_h0_rs97531

This directory contains the submission for the problem **stp_s090_l2_t5_h0_rs97531**.

| Field | Value 1 |
| --- | --- |
| Problem | stp_s090_l2_t5_h0_rs97531 |
| Submitter | Manan Gupta |
| Affiliation | The Harker School |
| Date | 2026-10-25 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-solvers/tree/main/steiner |
| Best Objective Value | 1730 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | No optimisation model is built. Routing heuristic on the arc graph; variable counts describe the emitted routing. |
| # Decision Variables | 1730 |
| # Binary Variables | 0 |
| # Integer Variables | 1730 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | Negotiated congestion routing (PathFinder style rip up and reroute) builds a feasible packing: each net is routed as a greedy Steiner tree by multi source Dijkstra on node costs that grow with present and historical overuse, until no node is shared. Then every net is replaced in turn by a minimum Steiner tree of the grid with the other nets' nodes removed (Dreyfus Wagner recursion driven by Dijkstra, exact since nets have at most six terminals), repeated until no net improves. A large neighbourhood search then rips up two to four adjacent nets and re-inserts them exactly in every order, with small random node costs on the earlier nets to leave room for the later ones, plus occasional random kicks; the best packing seen is kept. Routing order, kicks and neighbourhood choice depend on the seed. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 12 |
| # Feasible Runs | 12 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Cloud CPU container: 32 hardware threads of an AMD EPYC 9B45 host, 128 GB memory limit, Ubuntu 20.04, Python 3.12 with scipy, no GPU. Up to 14 single threaded runs executed concurrently in the container; the host is shared with other tenants and showed high load, so wall clock times are indicative only. |
| ====== |  |
| Total Runtime | 292.1 |
| Time to Solution | 292.1 |
| CPU Runtime | 292.1 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | This instance had no entry in the best known table before this submission. Re-run on 2026-10-25. Stage one: 6 independent runs (routing, exact polish, 120 s of neighbourhood search); stage two: 6 further runs that continue the stage one incumbent with different seeds and 450 s of neighbourhood search each. The best packing over all runs is reported; runs that stop at a worse value are counted as feasible, not successful. Runtimes are the average wall clock over all runs. The objective is the total arc cost of the routing. Verified with 04-steiner/check. |
