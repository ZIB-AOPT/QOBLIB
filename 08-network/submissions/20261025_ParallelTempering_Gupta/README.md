# Parallel tempering over network topologies, longer runs

A follow up to the 2026-08-18 submission with the same method and more search
time per run (7200 s instead of 1800 s), on five instances: network12 and
network24, where the best known table holds the reference value, and network20,
network22 and network23, where it holds the values of the 2026-08-18 runs.

The problem separates. Choosing the digraph is combinatorial, and the search
computes no lower bound for it. Choosing the routing on a fixed digraph is a
min-congestion multicommodity flow. So the search moves only over topologies and
scores each one with the LP relaxation of its routing. A 2-in/2-out digraph is
the union of two fixed-point-free permutations that disagree everywhere, and the
2-exchange (a->b),(c->d) => (a->d),(c->b) preserves every degree. A move that
would create a loop or a repeated arc is skipped, and a result that is not
strongly connected is rejected.

## Runs

Five independent runs per instance, seeds 0 to 4, each with eight replicas and
7200 s of search, strictly one run at a time on one laptop on AC power. Every
replica starts from a random topology drawn from the run's seed, and no
published solution is read by the search. The integral routing of the best
topology is computed once at the end of a run by solving the same model with
integer flows, and the solution is checked with 08-network/check.

The seeds are the same as in the 2026-08-18 runs, and on this machine the
search repeats itself for a given seed: every run here has the incumbent
sequence of the 1800 s run of its seed as a prefix. So each run retraces that
run and then continues. The five runs are independent of each other, but not of
the 2026-08-18 runs, and a run here is at least as good as the earlier run with
the same seed.

Total Runtime is the mean wall clock time and CPU Runtime the mean process CPU
time over the five runs, both including the integral routing at the end. Each
run is single threaded (HiGHS on one thread), so CPU time stays just under wall
clock time. Time to Solution is the mean time from the start of a run until its
best topology was found, over the runs that reach the reported value. Each row
lists the value of every run in its remarks, and the objective time series
holds all five runs.

One run at a time means one benchmark run at a time. The laptop was not kept
otherwise idle, and the search evaluation rate of a run is between 86% and 100%
of the fastest run of the same instance. One run (network12, seed 0) overlapped
a leftover process of an earlier start of the same sweep. It was discarded and
run again with the same seed. Runs that were cut off when the laptop was
unplugged wrote no record and were run again from the start; the run log lists
them.

## Results

Against the best known table at commit 55384509 (lower is better):

| instance | best of five | the five runs | table | first version |
| :--- | ---: | :--- | ---: | ---: |
| network12 | 276474 | 277527, 277572, 277000, 276474, 276474 | 276474 | 276474 |
| network20 | 521064 | 523667, 524000, 521064, 522594, 526273 | 528528 | 522657 |
| network22 | 615810 | 628658, 618115, 615810, 621844, 618135 | 618135 | 619420 |
| network23 | 658257 | 659369, 661172, 664388, 658257, 668632 | 659369 | 648241 |
| network24 | 694584 | 694681, 694584, 696688, 699929, 703447 | 663688 | 689035 |

network20, network22 and network23 are below the table values, which come from
the 2026-08-18 runs of the same method. Another open submission
(20260908_4colors-Optimizer_4colors) reports 520929, 616578 and 656030 on these
three instances, so against it only network22 is lower. network12 reaches the
reference value in two of the five runs and does not improve it. network24 does
not reach the reference value and is included so the method stays comparable.

The last column holds the values of the first version of this submission
(2026-10-25). Those runs came from a shared cloud machine with several runs at
a time and two search settings (eight replicas for 7200 s, twelve replicas for
10800 s). Those rows are replaced by these and their values are not claimed
anymore. On network23 and network24 the first version was better.

Code, run records (json and solution of all 25 runs, run log, settings) and the
script that builds these rows from them:
https://github.com/mnn31/qoblib-solvers/tree/ebb9d76c343accef20c53b72e9f8ae2e8ba68a0c/network

## AI disclosure

assisted —  code and repetitive boiler syntax implementation. The solver code,
the packaging scripts and the first drafts of the write-ups were written with help from
Claude (Claude Code, Claude Fable 5.1, Anthropic). All goals, problem choices,
methods and responses  were directed by the author, and every reported
run and solution file was executed, checked and confirmed by the author.
