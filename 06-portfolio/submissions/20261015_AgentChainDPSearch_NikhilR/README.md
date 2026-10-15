# Agent-run chain dynamic program and local search for po_a200_t10_s00 (B = 50, lambda = 0.01)

One solution for the a200 family: **a200_t10_s00_b050_l1e-02** with objective **-644342**, below the best value
posted for this cell in an open pull request (#87, -401535; #64 posts -192428). The best-known table has no row for
this cell yet. The method is a heuristic and claims no optimality.

**Method.** Each period's covariance is a 30-day sample covariance of rank 29, so integer baskets whose factor exposure
nearly cancels carry little risk, and good portfolios re-trade most of their units every period, so periods nearly
decouple. The search exploits this: a continuous relaxation rounded to integer unit counts (-487k), iterated local
search per period with both neighbouring periods fixed and exact incremental gains (-517k), an exact chain dynamic
program over the pool of local optima of every period (-520k), then rounds of per-period local search plus the chain
dynamic program with fresh seeds (-618978 after 6 rounds, -644342 after 60 more; the last seven rounds found nothing).
Every objective value uses the exact integer coefficients of the reference model.

**Validation.** Two independently written exact evaluators of the reference model (bqp_u3_c10.zpl with
parameter_u3_c10.zpl) first reproduce the posted values of pull requests #87 (-401535) and #64 (-192428), then agree
on this file: all ten periods feasible; risk 63057, return -784113, transaction costs 76812, cash interest -640, short
costs 542, liquidation 0; total -644342. The result does not depend on the rounding tie rule.

Code, verification scripts and the full record:
https://github.com/r-nikhil/V3R1T4S/tree/claim/2026-10-15-r-nikhil-8650bc1e/known-knowns/qoblib-market-split-and-portfolio/2026-10-15-r-nikhil-8650bc1e

## AI disclosure

generated — the search code, the evaluators and this write-up were produced by an AI agent: Claude Code running
Claude Opus 5.5 (Anthropic), inside the V3R1T4S research kit (https://github.com/elder-plinius/V3R1T4S), under the
submitter's direction. The submitter chose the problem, reviewed the result and its verification, and takes
responsibility for this submission. The solution was also re-evaluated independently by OpenAI Codex (gpt-6-astra) with
two separately written exact evaluators; that check is not part of the submission.

**AI as the method (AI_POLICY.md, section 3).** The optimisation itself is classical code (relaxation rounding, local
search and an exact chain dynamic program, as described above); an LLM agent (Claude Opus 5.5) designed these
heuristics, wrote the code, chose its parameters and ran it.
