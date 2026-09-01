# Submission for stp_s040_l3_t4_h1_rs24098

This directory contains the submission for the problem **stp_s040_l3_t4_h1_rs24098**.

## CSV Summary

| Field | Value |
|-------|-------|
| Problem | stp_s040_l3_t4_h1_rs24098 |
| Submitter | 4colors Research |
| Affiliation | 4colors Research |
| Date | 2026-09-01 |
| Reference | QOBLIB/solvers/steiner — Pathfinder-style negotiated-congestion + rip-up-and-reroute + iterated local search (C++17). |
| Best Objective Value | 483 |
| Optimality Bound | N/A |
| Modeling Approach | Directed multicommodity flow LP relaxation, heuristic packing |
| # Decision Variables | N/A |
| # Binary Variables | N/A |
| # Integer Variables | N/A |
| # Continuous Variables | N/A |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | Integer |
| Coefficients Range | 1 (unit edge cost) |
| Workflow | (1) Parse arcs/terms; (2) Pathfinder negotiated-congestion routing (Takahashi-Matsuyama tree per net + per-node pres/hist penalties); (3) Tree pruning of non-terminal leaves; (4) Rip-up-and-reroute polish on the residual graph; (5) Iterated local search (perturb K nets with tabu + re-polish; acceptance-walk that tolerates small worsening to cross ridges, with adaptive perturbation strength escalated on stall); (6) Multistart over 8 parameter combos (net-order × pres-init × pres-mult × hist-inc) padded with random restarts. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | N/A |
| Hardware Specifications | AMD/Intel x86_64 single-threaded, g++ 13, -O3 -march=native |
| Total Runtime | 0.000 |
| Time to Solution | N/A |
| CPU Runtime | 0.000 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| Remarks | nets= terminals=; objective is edge count (all weights unit). Classical result: there is no quantum contribution to any objective value in this submission. No QPU, GPU, annealer or quantum simulator was used at any point; QPU runtime is 0 because there was no QPU in the loop. |
