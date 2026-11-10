# Restricted state chain dynamic program for the large portfolio families

The exact chain dynamic program in the ChainDP submission enumerates every
feasible per period portfolio, which is impossible for a050 and above. This
submission keeps the chain structure but restricts each period to a pool of good
portfolios found by exact integer local search, exact subset enumeration and
relaxation roundings, runs the exact chain dynamic program over the pools, and
polishes by coordinate descent. The method is a heuristic and claims no
optimality.

## Runs

Every row is built directly from the records of independent runs on one machine
with code at a fixed commit. Each run starts from the instance alone, uses one
search setting for every row, and searches until it stops on its own, with no time
limit and no target. Each instance has ten runs (seeds 1 to 10). The 46 instances
where another open submission reported a value at least as good as this method's
earlier one have 23 more (seeds 11 to 33). The runs were made five at a time,
single threaded, on an Apple M3 Pro laptop on AC power with nothing else running.

Total Runtime and CPU Runtime are means over all runs, Time to Solution is the mean
time to the best value over the runs that reach it, and every row has the objective
time series of all its runs. No optimisation model is built, so the variable and
coefficient fields are N/A. No published solution is used anywhere.

## Results against the best known table

- 128 instances (a200 and a400) had no value on record. All of them have one now.
- 5 a050 rows improve the table value: a050_t10_s00 at lambda 1e-2 and 5e-4,
  a050_t15_orig at 1e-2 and 5e-4, and a050_t15_s02 at 1e-2.
- 37 a050 rows reach the table value, 8 of them listed as optimal.
- 22 a050 rows, all at lambda 5e-5 or above, do not reach the table value. They
  are included so the gap is on record.

Every solution was verified with 06-portfolio/check.

Code at the commit that ran: https://github.com/mnn31/qoblib-solvers/tree/7d5de733df73b639d2bb8534a62de4b38f2a6486/portfolio

Run records (json and solution for all 2978 runs, the run log, the settings and the
build script): https://github.com/mnn31/qoblib-solvers/tree/e2946eb2de9cbf38961c3b4a828f081bc947a7a2/portfolio/runs_2026-11

## AI disclosure

assisted —  code and repetitive boiler syntax implementation. The solver code,
the packaging scripts and the first drafts of the write-ups were written with help from
Claude (Claude Code, Claude Fable 5.1, Anthropic). All goals, problem choices,
methods and responses  were directed by the author, and every reported
run and solution file was executed, checked and confirmed by the author.
