# Submission for B64_64_7

This directory contains the submission for the problem **B64_64_7**.

| Field | Value 1 |
| --- | --- |
| Problem | B64_64_7 |
| Submitter | Manan Gupta |
| Affiliation | The Harker School |
| Date | 2026-08-17 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-birkhoff |
| Best Objective Value | 163 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | No optimisation model is built. Constructive exact decomposition: repeatedly select a positive perfect matching and subtract it. Variable counts describe the size of the emitted decomposition. |
| # Decision Variables | 10595 |
| # Binary Variables | 0 |
| # Integer Variables | 10595 |
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
| Total Runtime | 3.476838 |
| Time to Solution | 3.476838 |
| CPU Runtime | 3.476838 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Exact reconstruction verified; no optimality claim is made. Decision variables are the K weights and the K permutations of length n in the emitted decomposition, all integers, so K(n+1) in total. No model is built, so the coefficient fields are N/A. Runs were executed strictly one at a time on an otherwise idle machine. |
