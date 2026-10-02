# Parallel tempering over network topologies

The problem separates. Choosing the digraph is combinatorial and has no useful
lower bound; choosing the routing on a fixed digraph is a min-congestion
multicommodity flow, which is a linear program. So the search moves only over
topologies and scores each one with an exact LP.

Two things make that practical. On all 20 published solutions the ceiling of the
routing LP equals the published objective exactly, so the LP value is a sound
search energy and integrality only has to be restored at the end. And a 2-in/2-out
digraph is the union of two fixed-point-free permutations that disagree
everywhere, so the 2-exchange (a->b),(c->d) => (a->d),(c->b) preserves every
degree and every proposal is feasible by construction.

Eight replicas on a geometric temperature ladder from 6% to 0.2% of the
incumbent energy, degree-preserving 2- and 3-exchanges as the move, replica
exchange every 40 proposals. Every replica starts from an independently sampled
random 2-in/2-out topology: the published solutions are never read by the
search, so nothing here starts from an incumbent record. Five independent runs
per instance, single core each, 40 minutes per run, seeds 0 to 4.

The integral routing is recovered once at the end by re-solving the same model
with integrality on the flow variables.

Each objective time series holds one entry per run, recorded whenever the best
found objective improves, with the final entry marking the end of the run.

Code: https://github.com/mnn31/qoblib-solvers/tree/main/network
