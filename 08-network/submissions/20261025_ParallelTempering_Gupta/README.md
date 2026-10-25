# Parallel tempering over network topologies, longer runs

A follow up to the 2026-08-18 submission with the same method and more search
time, on the five instances where that submission did not hold the best known
value or held it with the largest remaining gap to its own lower bound.

The problem separates. Choosing the digraph is combinatorial and has no useful
lower bound; choosing the routing on a fixed digraph is a min-congestion
multicommodity flow, which is a linear program. So the search moves only over
topologies and scores each one with an exact LP. A 2-in/2-out digraph is the
union of two fixed-point-free permutations that disagree everywhere, so the
2-exchange (a->b),(c->d) => (a->d),(c->b) preserves every degree and every
proposal is feasible by construction.

Runs: six independent runs of eight replicas for 7200 s on each of the five
instances (seeds 0 to 5), and four further runs of twelve replicas for 10800 s
on network20, network22 and network23 (seeds 10 to 13). Every replica starts
from an independently sampled random topology; the published solutions are
never read by the search. The integral routing is recovered once at the end by
re-solving the same model with integrality on the flow variables.

Outcome against the best known table of 2026-10-25: network20 and network23
improve the recorded values, network12 reaches the recorded best known value
exactly, network22 and network24 do not reach it and are included so the method
stays comparable.

Each objective time series holds one entry per run, recorded whenever the best
found objective improves, with the final entry marking the end of the run.

Code: https://github.com/mnn31/qoblib-solvers/tree/main/network

## AI disclosure

assisted —  code and repetitive boiler syntax implementation. The solver code,
the packaging scripts and the first drafts of the write-ups were written with help from
Claude (Claude Code, Claude Fable 5.1, Anthropic). All goals, problem choices,
methods and responses  were directed by the author, and every reported
run and solution file was executed, checked and confirmed by the author.
