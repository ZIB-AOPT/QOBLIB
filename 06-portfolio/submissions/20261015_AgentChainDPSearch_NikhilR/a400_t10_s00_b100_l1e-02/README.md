# Submission for a400_t10_s00_b100_l1e-02

This directory contains the submission for the problem **a400_t10_s00_b100_l1e-02**.

| Field | Value 1 |
| --- | --- |
| Problem | a400_t10_s00_b100_l1e-02 |
| Submitter | Nikhil R |
| Affiliation | Independent |
| Date | 2026-10-15 |
| ====== |  |
| Reference | https://github.com/r-nikhil/V3R1T4S/tree/claim/2026-10-15-r-nikhil-7bf097a5/known-knowns/qoblib-market-split-and-portfolio/2026-10-15-r-nikhil-7bf097a5 |
| Best Objective Value | -1696664 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Reference model bqp_u3_c10.zpl with parameter_u3_c10.zpl, evaluated with its exact integer coefficients and searched directly over per period integer unit count portfolios |
| # Decision Variables | N/A |
| # Binary Variables | N/A |
| # Integer Variables | N/A |
| # Continuous Variables | N/A |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | Beam search over per period exchanges of distinct assets from a seed portfolio, period-by-period improvement with the neighbouring periods fixed, block beam search over groups of periods and a net-position beam, then an exact chain dynamic program that recombines period rows from several search pools. All objective values use the exact integer coefficients of the reference model. The search code was written and run by an AI agent (OpenAI Codex CLI, gpt-6-astra) under the submitter's direction; see the AI disclosure in the submission README. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M5 Pro laptop, 18 CPU cores, 48 GB RAM, macOS, Python 3.9, no GPU. Runs at low priority alongside other work, so wall clock times are indicative only. |
| ====== |  |
| Total Runtime | N/A |
| Time to Solution | N/A |
| CPU Runtime | N/A |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| Remarks | Improves the best value posted for this cell, -1090282 (open pull request #87); the best-known table has no row for this cell yet. Heuristic, so the optimality bound is N/A. Runtimes were not measured as a single run: the search ran in an agent research session over several hours with pauses, so they are reported as N/A. Feasibility and the objective were verified in exact arithmetic by independently written evaluators of the reference model, which first reproduce the value posted in pull request #87. |
