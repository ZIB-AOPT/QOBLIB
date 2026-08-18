# Exact chain dynamic programming for the portfolio instances

The reference model couples periods only through the rebalancing term between
consecutive periods, and charges no rebalancing into the final period. Every
other term, the risk quadratic, the return, the short-selling cost and the cash
interest on the slack register, depends on a single period's portfolio.

That makes the model a chain. Enumerating the feasible per-period portfolios
under the budget and capital slack registers and running a forward dynamic
program over them gives the exact optimum, with the last period detaching.

Contents, 160 instances:

* a003, a004 and a005, 96 instances, all previously listed open with no feasible
  solution on record. A period has between 84 and 991 feasible portfolios here,
  so each closes in well under a second.
* a010_t10 and a010_t15, 64 instances. These match the published values exactly,
  so nothing improves, but they are now proven optimal rather than best known.
  A period has 10,606 feasible portfolios, so these take a few minutes each.

All values are proven optima, not heuristic bounds, so the optimality bound
equals the objective throughout.

The objective was implemented in exact rational arithmetic with Zimpl's
rounding, and validated against the shipped a010 reference solutions before any
of these were produced: it reproduces their published objective values exactly,
including the ones marked proven optimal.

The method is exact and not anytime, so there is no objective time series: the
dynamic program produces no incumbent before it returns the optimum.

Code: https://github.com/mnn31/qoblib-solvers/tree/main/portfolio
