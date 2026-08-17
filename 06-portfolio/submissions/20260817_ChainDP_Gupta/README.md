# Exact chain dynamic programming for the portfolio instances

The reference model couples periods only through the rebalancing term between
consecutive periods, and charges no rebalancing into the final period. Every
other term, the risk quadratic, the return, the short-selling cost and the cash
interest on the slack register, depends on a single period's portfolio.

That makes the model a chain. Enumerating the feasible per-period portfolios
under the budget and capital slack registers and running a forward dynamic
program over them gives the exact optimum, with the last period detaching.

For the a003, a004 and a005 families a period has between 84 and 991 feasible
portfolios, so every instance closes in well under a second. All values here
are proven optima, not heuristic bounds.

The objective was implemented in exact rational arithmetic with Zimpl's
rounding, and validated against the shipped a010 reference solutions before any
of these were produced: it reproduces their published objective values exactly,
including the three that are marked proven optimal.

Code: https://github.com/mnn31/qoblib-net
