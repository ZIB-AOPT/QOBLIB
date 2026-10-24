# Agent-run chain dynamic program and local search for three large portfolio cells (lambda = 0.01)

Three solutions for the a200 and a400 families, each below the best value posted for its cell in an open pull request;
the best-known table has no row for any of these cells yet. The method is a heuristic and claims no optimality.

| Instance | Objective | Best posted so far |
| --- | --- | --- |
| a200_t10_orig_b050_l1e-02 | **-691624** | -551385 (PR #87); -300647 (PR #64) |
| a200_t10_s00_b050_l1e-02 | **-644342** | -401535 (PR #87); -192428 (PR #64) |
| a400_t10_s00_b100_l1e-02 | **-1696664** | -1090282 (PR #87) |

**Method.** Each period's covariance is a 30-day sample covariance of rank 29, so integer baskets whose factor exposure
nearly cancels carry little risk, and good portfolios re-trade most of their units every period, so periods nearly
decouple. The search exploits this in stages: a continuous relaxation rounded to integer unit counts and descended
exactly; iterated local search per period with exact incremental gains; an exact chain dynamic program that mixes
periods from different solutions (over each period's pool of local optima); then, on a200_t10_s00, rounds of
per-period local search with both neighbouring periods fixed plus the chain dynamic program with fresh seeds (-618978
after 6 rounds, -644342 after 60 more; the last seven rounds found nothing). Every objective value uses the exact
integer coefficients of the reference model.

**Validation.** Two independently written exact evaluators of the reference model (bqp_u3_c10.zpl with
parameter_u3_c10.zpl) first reproduce the values posted in pull requests #87 and #64 for each cell, then agree
on each file: all ten periods feasible; a200_t10_s00 totals -644342 (risk 63057, return -784113, transaction costs
76812), a200_t10_orig totals -691624 (risk 58939, return -825237, transaction costs 75179). The comparisons do not
depend on the rounding tie rule.

Code, verification scripts and the full record (a200_t10_orig, then a200_t10_s00):
https://github.com/r-nikhil/V3R1T4S/tree/claim/2026-10-14-r-nikhil-3066ef03/known-knowns/qoblib-market-split-and-portfolio/2026-10-14-r-nikhil-3066ef03
https://github.com/r-nikhil/V3R1T4S/tree/claim/2026-10-15-r-nikhil-8650bc1e/known-knowns/qoblib-market-split-and-portfolio/2026-10-15-r-nikhil-8650bc1e

**The a400 cell** (added 2026-10-24) came from a separate agent run: beam searches over asset exchanges, periods, blocks
of periods and net positions, recombined by the same exact chain dynamic program; feasible in all ten periods with
objective -1696664, verified in exact arithmetic. Code and record:
https://github.com/r-nikhil/V3R1T4S/tree/claim/2026-10-15-r-nikhil-7bf097a5/known-knowns/qoblib-market-split-and-portfolio/2026-10-15-r-nikhil-7bf097a5

## AI disclosure

generated — the search code, the evaluators and this write-up were produced by AI agents: for the two a200 cells,
Claude Code running Claude Opus 5.5 (Anthropic); for the a400 cell, OpenAI Codex CLI running gpt-6-astra; inside the V3R1T4S research kit (https://github.com/elder-plinius/V3R1T4S), under the
submitter's direction. The submitter chose the problem, reviewed the result and its verification, and takes
responsibility for this submission. The solution was also re-evaluated independently by OpenAI Codex (gpt-6-astra) with
two separately written exact evaluators; that check is not part of the submission.

**AI as the method (AI_POLICY.md, section 3).** The optimisation itself is classical code (relaxation rounding, local
search and an exact chain dynamic program, as described above); LLM agents (Claude Opus 5.5 for the a200 cells, gpt-6-astra for
the a400 cell) designed these heuristics, wrote the code, chose their parameters and ran them.
