# Submission for labs037

This directory contains the submission for the problem **labs037**.

| Field | Value 1 |
| --- | --- |
| Problem | labs037 |
| Submitter | Tim Bode |
| Affiliation | Forschungszentrum Jülich |
| Date | 2026-08-20 |
| ====== |  |
| Reference | Algorithm: H. Goto et al., Science Advances 7, eabe7953 (2021), https://doi.org/10.1126/sciadv.abe7953; implementation and benchmark data: https://github.com/Quicopt/Benchmarks |
| Best Objective Value | 86 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | HUBO (degree-4 spin polynomial, native — no quadratization) |
| # Decision Variables | 37 |
| # Binary Variables | 37 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 4047 |
| Coefficients Type | integer |
| Coefficients Range | 2 - 4 |
| ====== |  |
| Workflow | Pre-processing: expand E(s)=Σ_k C_k(s)^2 into a degree-4 spin polynomial and cancel repeated indices via s_i^2=1, giving a native HUBO over N spins (no quadratization, no auxiliary variables, no penalty parameter). Pre-solvers: none. Main algorithm: discrete Simulated Bifurcation (Goto et al.) integrated with symplectic Euler at fixed step, coupling evaluated at sign(x), perfectly-inelastic walls at \|x_i\|=1, pump detuning ramped linearly to zero. Independent random restarts differ only in the initial momenta. Post-processing: none (no local search or polishing applied). |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 13184 |
| # Feasible Runs | 13184 |
| # Successful Runs | 4 |
| Success Threshold | 0.0 |
| ====== |  |
| Hardware Specifications | AMD EPYC-Rome, 128 physical cores, 503 GB RAM, Ubuntu 24.04, Julia 1.12.6. N<=59: 128 Julia threads pinned to 128 cores. N>=60: 100 Julia threads pinned to 100 cores (taskset 0-99). Threads and cores 1:1 in both regimes; CPU-only, no GPU or QPU. |
| ====== |  |
| Total Runtime | 60.3961 |
| Time to Solution | 3.4218 |
| CPU Runtime | 7730.6976 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | LABS is unconstrained: every ±1 sequence is feasible, so # Feasible Runs = # Runs. One run = one independent dSB restart from random initial momenta; the reported value is best-of-13184, found in 4 of them. No post-processing of any kind was applied — no local search, no 1-opt or tabu polish — so this is raw dSB output. Run as a depth portfolio: the 420 s budget was split evenly across n_steps ∈ {2500, 20000, 160000}, each arm receiving 140 s. The reported value came from the n_steps = 2500 arm. Total Runtime is measured, not budgeted, and exceeds the nominal budget because an arm's deadline is tested before a batch starts rather than during it. CPU Runtime is wall time x the 128 cores the process ran on; threads and cores are 1:1 throughout, so this is measured machine time rather than an oversubscription artefact. Optimality Bound is N/A: dSB proves nothing. |
