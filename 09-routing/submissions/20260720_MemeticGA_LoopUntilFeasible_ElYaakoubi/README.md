# Loop-until-feasible Memetic GA — CVRP submission (recorded traces)

**Submitter:** Othmane El Yaakoubi · **Date:** 2026-07-20 · **Code:** https://github.com/othma125/heuristicCVRP

Single merged submission covering all 55 `XSH-n20-k4` instances with the loop-until-feasible
graph-based memetic GA (giant-tour chromosome + shortest-path capacity split). See the
[09-routing README](../../README.md) for the method.

Supersedes [`20260708_MemeticGA_ElYaakoubi`](../20260708_MemeticGA_ElYaakoubi) (34 instances,
single-shot variant) and reports the same method as
[`20260711_MemeticGA_LoopUntilFeasible_ElYaakoubi`](../20260711_MemeticGA_LoopUntilFeasible_ElYaakoubi)
from a fresh campaign.

## What is new

- **The objective time series is recorded by the solver.** Each incumbent improvement is logged with
  its wall-clock timestamp as the search runs, so the final trace point equals the reported
  `Time to Solution`. The traces in the 2026-07-11 directory were not produced this way.
- **A population-initialisation bug is fixed.** `InitialPopulation` aborted a run whenever slot 0
  took exactly 100 attempts, even when that 100th attempt was feasible, leaving the rest of the
  population unfilled. This made feasibility look harder than it is and could crash the search.

## Results (5 runs per instance, all feasible)

| Metric | Value |
| --- | --- |
| Instances | 55 (5 runs each = 275 runs, 0 failures) |
| Reach the known optimum (best of 5) | 34 / 55 |
| Mean best-run gap to optimum | 0.40 % (max 3.70 % on `-52`) |
| Avg attempts to feasibility | 2.04 (per-instance range 1.0 – 13.2) |
| Hardest to make feasible | `XSH-n20-k4-34` — 13.2 avg attempts (min 5, max 20) |
| Mean per-run wall-clock (retry-inclusive) | 16.5 s (max 102.3 s on `-34`) |

Against the 2026-07-11 campaign: 11 instances better, 16 worse, 28 unchanged. Both are single
stochastic campaigns, so a split of that size is within run-to-run variance; the numbers here are
reported exactly as this campaign produced them, with no per-instance selection between campaigns.

Per-instance figures are in [`campaign_summary.csv`](campaign_summary.csv).

## Per-instance files

Each `XSH-n20-k4-NN/` directory contains:

- `NN_summary.csv` / `README.md` — the 30-field summary. `Total Runtime` and `Time to Solution` are
  wall-clock and include the failed-attempt retries; TTS is measured from the meta-run start to the
  last incumbent improvement. No cutoff is set, so `Success Threshold` is `N/A` and every feasible
  run counts as successful.
- `NN_solution.sol` — best solution over the 5 runs, CVRPLIB route format.
- `NN_objective_time_series.json.gz` — gzipped JSON, one array per run, each entry
  `{"Time": <seconds>, "Incumbent": <cost>, "step": <n>}`. `Time` is wall-clock from the meta-run
  start, so it includes time spent on failed attempts.

## Reproducing

Solver at [`othma125/heuristicCVRP`](https://github.com/othma125/heuristicCVRP), branch
`objective-trace`. Hardware: Intel Core i7-7700HQ @ 2.80GHz (4 cores / 8 threads), 16 GB RAM,
Ubuntu 24.04 LTS, Java 21 (Oracle GraalVM 21.0.2), multi-threaded. Full campaign: 4534 s.
