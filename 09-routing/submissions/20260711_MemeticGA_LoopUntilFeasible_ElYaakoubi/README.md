# Loop-until-feasible Memetic GA — CVRP submission

**Submitter:** Othmane El Yaakoubi · **Date:** 2026-07-11 · **Code:** https://github.com/othma125/heuristicCVRP

This is a **loop-until-feasible** graph-based memetic GA (giant-tour chromosome + shortest-path
capacity split): each run restarts from a fresh random population until it returns a feasible
solution. See the [09-routing README](../../README.md) for the method and its adaptive stopping
criterion, and [`20260721_MemeticGA_LoopUntilFeasible_ElYaakoubi`](../20260721_MemeticGA_LoopUntilFeasible_ElYaakoubi)
for the same variant re-run on a later solver version.

## Why this variant

Under the tight `k = 4` capacity, a feasible capacity split is **not guaranteed** from a random
start — a single run may return no feasible solution. This variant wraps the solver in a retry loop:
each run **restarts from a fresh random population until it returns a feasible solution**. So every
reported run is feasible by construction (`# Feasible Runs = # Runs`), and the interesting new
statistic is **how many restarts feasibility costs**.

## Results (5 runs per instance, all feasible)

| Metric | Value |
| --- | --- |
| Instances | 55 (5 runs each = 275 runs, 0 failures) |
| Reach the known optimum (best of 5 = opt) | 39 / 54 instances with a known optimum |
| Mean best-run gap to optimum | 0.28 % (max 2.47 %) |
| **Avg attempts to feasibility** | **2.33** (median 1.6, per-instance range 1.0 – 21.4) |
| Instances feasible on the 1st attempt every run | 6 |
| Hardest to make feasible | `XSH-n20-k4-34` — 21.4 avg attempts (min 2, max 46) |
| Mean per-run wall-clock (retry-inclusive) | 13.5 s (max 104.0 s on `-34`) |

Per-instance figures — including avg/min/max attempts — are in
[`campaign_summary.csv`](campaign_summary.csv).

## Per-instance files (canonical format)

Each `XSH-n20-k4-NN/` directory contains:

- `NN_summary.csv` / `README.md` — the 30-field summary. `Total Runtime` and `Time to Solution` are
  **wall-clock and include the failed-attempt retries**; TTS is measured from the meta-run start to
  the last incumbent improvement. No cutoff is set, so `Success Threshold` is `N/A` and every
  feasible run counts as successful.
- `NN_solution.sol` — best feasible solution over the 5 runs (`Route #k:` format).
- `NN_objective_time_series.json.gz` — gzip'd JSON, an **array of 5 runs**; each run is an array of
  `{"Time": <seconds>, "Incumbent": <objective>, "step": <index>}` incumbent-improvement points.
  `Time` is offset by the retry overhead so it reads as wall-clock since the run started.
