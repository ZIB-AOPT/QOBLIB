# Submission for a200_t10_s00_b050_l1e-02

This directory contains the submission for the problem **a200_t10_s00_b050_l1e-02**.

| Field | Value 1 |
| --- | --- |
| Problem | a200_t10_s00_b050_l1e-02 |
| Submitter | Nikhil R |
| Affiliation | Independent |
| Date | 2026-10-15 |
| ====== |  |
| Reference | https://github.com/r-nikhil/V3R1T4S/tree/claim/2026-10-15-r-nikhil-8650bc1e/known-knowns/qoblib-market-split-and-portfolio/2026-10-15-r-nikhil-8650bc1e |
| Best Objective Value | -644342 |
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
| Workflow | Continuous relaxation rounded to integer unit counts; iterated local search per period with both neighbouring periods fixed, using exact incremental gains; an exact chain dynamic program over every period's pool of local optima; then 66 rounds of per period local search plus the chain dynamic program, with fresh seeds. The search code was written and run by an AI agent (Claude Opus 5.5, Anthropic, in Claude Code) under the submitter's direction; see the AI disclosure in the submission README. |
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
| Remarks | Improves the best value posted for this cell, -401535 (open pull request #87); the best-known table has no row for this cell yet. Heuristic, so the optimality bound is N/A. Runtimes were not measured as a single run: the search ran in an agent research session over several hours with pauses, so they are reported as N/A. Verified with two independently written exact evaluators of the reference model, which first reproduce the posted values -401535 (pull request #87) and -192428 (pull request #64). |
