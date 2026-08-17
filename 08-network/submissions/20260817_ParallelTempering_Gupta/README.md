# Parallel tempering over network topologies

The problem separates. Choosing the digraph is combinatorial and has no useful
lower bound; choosing the routing on a fixed digraph is a min-congestion
multicommodity flow, which is a linear program. So the search moves only over
topologies and scores each one with an exact LP.

Two things make that practical. On all 20 published solutions the ceiling of
the routing LP equals the published objective exactly, so the LP value is a
sound search energy and integrality only has to be restored at the end. And a
2-in/2-out digraph is the union of two fixed-point-free permutations that
disagree everywhere, so the 2-exchange (a->b),(c->d) => (a->d),(c->b) preserves
every degree and every proposal is feasible by construction.

Eight replicas, geometric temperature ladder, replica exchange every 40
proposals, half seeded from the published reference topology and half from
random topologies. Single core per run on a laptop.

Code: https://github.com/mnn31/qoblib-net
