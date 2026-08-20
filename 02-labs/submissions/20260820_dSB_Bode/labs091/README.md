# Submission for labs091

This directory contains the submission for the problem **labs091**.

| Field | Value 1 |
| --- | --- |
| Problem | labs091 |
| Submitter | Tim Bode |
| Affiliation | Forschungszentrum Jülich |
| Date | 2026-08-20 |
| ====== |  |
| Reference | Algorithm: H. Goto et al., Science Advances 7, eabe7953 (2021), https://doi.org/10.1126/sciadv.abe7953; implementation and benchmark data: https://github.com/Quicopt/Benchmarks |
| Best Objective Value | 737 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | HUBO (degree-4 spin polynomial, native — no quadratization) |
| # Decision Variables | 91 |
| # Binary Variables | 91 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 61755 |
| Coefficients Type | integer |
| Coefficients Range | 2 - 4 |
| ====== |  |
| Workflow | Pre-processing: expand E(s)=Σ_k C_k(s)^2 into a degree-4 spin polynomial and cancel repeated indices via s_i^2=1, giving a native HUBO over N spins (no quadratization, no auxiliary variables, no penalty parameter). Pre-solvers: none. Main algorithm: discrete Simulated Bifurcation (Goto et al.) integrated with symplectic Euler at fixed step, coupling evaluated at sign(x), perfectly-inelastic walls at \|x_i\|=1, pump detuning ramped linearly to zero. Independent random restarts differ only in the initial momenta. Post-processing: none (no local search or polishing applied). |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 700 |
| # Feasible Runs | 700 |
| # Successful Runs | 1 |
| Success Threshold | 0.0 |
| ====== |  |
| Hardware Specifications | AMD EPYC-Rome, 128 physical cores, 503 GB RAM, Ubuntu 24.04, Julia 1.12.6. N<=59: 128 Julia threads pinned to 128 cores. N>=60: 100 Julia threads pinned to 100 cores (taskset 0-99). Threads and cores 1:1 in both regimes; CPU-only, no GPU or QPU. |
| ====== |  |
| Total Runtime | 333.3918 |
| Time to Solution | 333.3918 |
| CPU Runtime | 33339.1829 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | LABS is unconstrained: every ±1 sequence is feasible, so # Feasible Runs = # Runs. One run = one independent dSB restart from random initial momenta; the reported value is best-of-700, found in 1 of them. No post-processing of any kind was applied — no local search, no 1-opt or tabu polish — so this is raw dSB output. Run as a depth portfolio: the 280 s budget was split evenly across n_steps ∈ {2500, 20000}, each arm receiving 140 s. The reported value came from the n_steps = 20000 arm. Instances up to N=59 ran a third arm at n_steps = 160000; it was dropped from N=60 onward. In a preparatory sweep over N=41–87 that arm produced the best value in 0 of 47 instances while consuming most of the wall time: at these sizes one 160000-step batch is a single chunk of one restart per thread, so the arm bought one extra batch for roughly two thirds of the budget. The effect is visible across the boundary — N=59 (three arms) drew 6912 restarts in 447 s, N=61 (two arms) drew 6600 in 295 s. The two surviving arms keep exactly the 140 s each they had at N ≤ 59, so the arms that produce the answers are treated identically across the whole sweep. These instances ran with 100 threads pinned to 100 cores rather than 128 on 128, so their restart counts are roughly 22% below what the full machine would give at the same N. Total Runtime is measured, not budgeted, and exceeds the nominal budget because an arm's deadline is tested before a batch starts rather than during it. CPU Runtime is wall time x the 100 cores the process ran on; threads and cores are 1:1 throughout, so this is measured machine time rather than an oversubscription artefact. Optimality Bound is N/A: dSB proves nothing. |
