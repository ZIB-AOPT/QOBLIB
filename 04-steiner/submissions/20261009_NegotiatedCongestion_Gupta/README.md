# Negotiated congestion routing for the Steiner tree packing instances

All 190 instances, each from five independent runs on a laptop. The rows replace
the earlier ones in this folder, which mixed machines and continued earlier runs.

The method has three parts. A PathFinder style rip up and reroute router, the
standard method for switchbox routing in VLSI, routes each net as a greedy
Steiner tree; nodes used by more than one net get a congestion penalty that grows
every iteration until the nets separate. An exact polish then replaces each net
in turn by a minimum Steiner tree of the grid with the other nets' nodes removed,
computed with the Dreyfus Wagner recursion (nets have at most six terminals),
until no net improves. Last, a large neighbourhood search rips up two to four
adjacent nets and re-inserts them exactly in every order, with small random node
costs on the earlier nets and occasional random kicks, for a fixed time budget.

No optimisation model is built, so the variable fields are N/A. No published
solution is read at any point.

## Runs

Every row has five runs, seeds 0 to 4, each starting from nothing. The search
budget is 600 s per run, or 120 s for the 29 instances with the smallest arc
files. Runs never stop early and are not given any target value. Five single
threaded runs went at a time on an Apple M3 Pro laptop (18 GB, macOS 26.3) on AC
power with nothing else running. Total Runtime and CPU Runtime are means over all
five runs, and Time to Solution is the mean time to the best value over the runs
that reach it. The objective time series of every run is in each row, and every
solution was verified with 04-steiner/check.

## Results against the current table

- 147 instances have no value in the table.
- 26 rows reach a value the table lists as optimal and 12 reach a best known value.
- stp_s070_l4_t6_h0_rs97531: 374 against the best known 375, in all five runs.
- stp_s030_l3_t5_h1_rs24098: 475, while the table lists 476 as optimal. One of
  the five runs found it. The packing passes 04-steiner/check, and we also checked
  separately that every net is a tree holding all its terminals and that no two
  nets share a node, which is all the node disjoint model asks. The optimal label
  on 476 may need a second look.
- Three rows miss the table value and are included anyway:
  stp_s020_l3_t3_h2_rs24098 (357 against the optimal 355),
  stp_s020_l3_t4_h2_rs97531 (265 against the optimal 264) and
  stp_s020_l5_t4_h0_rs24098 (243 against the best known 242).

Code: https://github.com/mnn31/qoblib-solvers/tree/95485bfe2108f3666e3472bfeb5f3e4c55edc4d7/steiner

Run records (one json per run with times, CPU time and every incumbent, plus the
solution and log of each run): https://github.com/mnn31/qoblib-solvers/tree/b644713d94ff18f6960cf5a9587eb426d325d5c6/steiner/runs_2026-11

## AI disclosure

assisted —  code and repetitive boiler syntax implementation. The solver code,
the packaging scripts and the first drafts of the write-ups were written with help from
Claude (Claude Code, Claude Fable 5.1, Anthropic). All goals, problem choices,
methods and responses  were directed by the author, and every reported
run and solution file was executed, checked and confirmed by the author.
