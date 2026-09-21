# Submission for B15_225_5

This directory contains the submission for the problem **B15_225_5**.

| Field | Value 1 |
| --- | --- |
| Problem | B15_225_5 |
| Submitter | Manan Gupta |
| Affiliation | Independent Researcher |
| Date | 2026-08-17 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-birkhoff |
| Best Objective Value | 75 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | No optimisation model is built. Constructive exact decomposition: repeatedly select a positive perfect matching and subtract it. Variable counts describe the size of the emitted decomposition. |
| # Decision Variables | 1200 |
| # Binary Variables | 0 |
| # Integer Variables | 1200 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | At each iteration, maximize the smallest residual selected by a perfect matching. Within that threshold, maximize eliminated entries and then minimize the matching residual sum. Subtract the selected minimum exactly. |
| Algorithm Type | Deterministic |
| Paradigm | Classical |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M3 Pro (Mac15,6), 11 cores (5 performance + 6 efficiency), 18 GB unified memory, macOS 26.3, arm64. One process at a time with nothing else running. |
| ====== |  |
| Total Runtime | 0.026854 |
| Time to Solution | 0.026854 |
| CPU Runtime | 0.026854 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Exact reconstruction verified; no optimality claim is made. Decision variables are the K weights and the K permutations of length n in the emitted decomposition, all integers, so K(n+1) in total. No model is built, so the coefficient fields are N/A. Runs were executed strictly one at a time on an otherwise idle machine. |
