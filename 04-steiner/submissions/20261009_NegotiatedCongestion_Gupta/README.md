# Negotiated congestion routing for the Steiner tree packing instances

A PathFinder style rip up and reroute router, the standard method for switchbox
and channel routing in VLSI. Each net is routed as a greedy Steiner tree; nodes
used by more than one net accumulate a congestion penalty that grows every
iteration until the nets separate. Three cost polish passes follow.

No optimisation model is built. The reference formulation for this class is a
multicommodity flow MIP with millions of variables, which is why most instances
had no solution on record; the graphs themselves are small for a router, and
every instance here routes in seconds.

Every reported solution was verified with 04-steiner/check. Runs that do not
improve on a published value are included so the method stays comparable.

Code: https://github.com/mnn31/qoblib-solvers/tree/main/steiner

## AI disclosure

assisted —  code and repetitive boiler syntax implementation. The solver code,
the packaging scripts and the first drafts of the write-ups were written with help from
Claude (Claude Code, Claude Fable 5.1, Anthropic). All goals, problem choices,
methods and responses  were directed by the author, and every reported
run and solution file was executed, checked and confirmed by the author.
