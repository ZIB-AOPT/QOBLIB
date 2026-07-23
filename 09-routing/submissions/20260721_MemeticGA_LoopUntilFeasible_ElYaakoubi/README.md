# Loop-until-feasible Memetic GA — CVRP submission (solver v1.0)

**Submitter:** Othmane El Yaakoubi · **Date:** 2026-07-21 ·
**Code:** [`othma125/heuristicCVRP@v1.0`](https://github.com/othma125/heuristicCVRP/releases/tag/v1.0) (commit `51b335b`)

All 55 `XSH-n20-k4` instances solved with the loop-until-feasible graph-based memetic GA
(giant-tour chromosome + shortest-path capacity split). See the
[09-routing README](../../README.md) for the method.

## Solver version

Run on `heuristicCVRP` tag `v1.0` (commit `51b335b`), which includes the population-initialisation
fix and always runs the intra-route local search inside the split. The objective time series is
recorded by campaign instrumentation that logs each incumbent improvement with its wall-clock
timestamp; it only reads the incumbent and does not affect the search, so all results are
attributable to `v1.0` as published.

## Results (5 runs per instance, all feasible)

| Metric | Value |
| --- | --- |
| Instances | 55 (5 runs each = 275 runs, 0 failures) |
| Reach the known optimum (best of 5) | 38 / 55 |
| Mean best-run gap to optimum | 0.19 % (max 1.51 % on `-43`) |
| Avg attempts to feasibility | 1.91 (per-instance range 1.0 – 8.0) |
| Hardest to make feasible | `XSH-n20-k4-34` — 8.0 avg attempts (min 3, max 18) |
| Mean per-run wall-clock (retry-inclusive) | 12.2 s |

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

Hardware: Intel Core i7-7700HQ @ 2.80GHz (4 cores / 8 threads), 16 GB RAM, Ubuntu 24.04 LTS,
Java 21 (Oracle GraalVM 21.0.2), multi-threaded. Full campaign: 3361 s.
