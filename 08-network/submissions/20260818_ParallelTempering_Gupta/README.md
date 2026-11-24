# Parallel tempering over network topologies

The problem separates. Choosing the digraph is combinatorial, and the search
computes no lower bound for it. Choosing the routing on a fixed digraph is a
min-congestion multicommodity flow. So the search moves only over topologies and
scores each one with the LP relaxation of its routing.

Two things make that practical. On all 20 published solutions the ceiling of the
routing LP equals the published objective exactly, so the LP value is a sound
search energy and integrality only has to be restored at the end. And a 2-in/2-out
digraph is the union of two fixed-point-free permutations that disagree
everywhere, and the 2-exchange (a->b),(c->d) => (a->d),(c->b) preserves every
degree. A move that would create a loop or a repeated arc is skipped, and a
result that is not strongly connected is rejected.

Eight replicas on a geometric temperature ladder from 6% to 0.2% of the best
starting energy, degree-preserving 2- and 3-exchanges as the move, replica
exchange every 40 proposals. Every replica starts from an independently sampled
random 2-in/2-out topology: the published solutions are never read by the
search, so nothing here starts from an incumbent record. Five independent runs
per instance, seeds 0 to 4, 30 minutes (1800 s) of search each, one run at a time.

The integral routing is recovered once at the end by re-solving the same model
with integrality on the flow variables.

Each objective time series holds one entry per run, recorded whenever the best
found objective improves, with the final entry marking the end of the run.

Total Runtime is the wall clock time of the search loop; the setup and the final
integral re-solve were not timed, and CPU time was not recorded for these runs,
so CPU Runtime is N/A. Corrected on 2026-11-12 together with the non-zero counts,
which now follow n(n-1)(5n-3) as in the reference model.

Code, run records and the scripts at the commit with these runs:
https://github.com/mnn31/qoblib-solvers/tree/6a85c438851383a7943f9af29631b6a573699169/network

## AI disclosure

assisted —  code and repetitive boiler syntax implementation. The solver code,
the packaging scripts and the first drafts of the write-ups were written with help from
Claude (Claude Code, Claude Fable 5.1, Anthropic). All goals, problem choices,
methods and responses  were directed by the author, and every reported
run and solution file was executed, checked and confirmed by the author.
