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

## Rounding

The objective is not evaluated in floating point anywhere. Prices and
covariances are parsed straight from the instance files into exact rationals,
and every quantity below is formed and rounded exactly, so the result is
bit-identical to the coefficients Zimpl writes into the shipped LP and QUBO
files.

Zimpl's `round` is half away from zero, which is not what IEEE or Python's
`round` does. On an exact rational x it is

    round(x) = trunc(x + 1/2)   if x >= 0
    round(x) = trunc(x - 1/2)   if x <  0

so 0.5 goes to 1 and -0.5 goes to -1, whereas banker's rounding would send both
to 0. Getting this wrong shifts individual coefficients by one unit and the
totals by more.

Unit prices are rebased exactly before anything is rounded: one unit of asset i
is `unit` of cash at t = 0, so `p[i,t] = raw_p[i,t] * unit / raw_p[i,0]` is kept
as a rational, never as a decimal.

Rounding is then applied once per model coefficient, exactly where the reference
model applies it, and never to a running total:

| coefficient | expression rounded |
| :--- | :--- |
| risk, per ordered group pair and period | `lambda * tau_i * tau_j * cov[i,j,t] * p[i,t] * p[j,t]` |
| return, per group and period | `tau * (p[i,t+1] - p[i,t])` |
| transaction and liquidation, per group and period | `delta * p[i,t]` |
| short selling, per short group and period | `rho * p[i,t]` |
| cash interest, per slack bit | `nu * unit * 2^k` |

Every rounded coefficient is an integer, so from that point on the whole
objective, and the dynamic program over it, is integer arithmetic with no
further rounding and no accumulation error.

This was validated against the shipped a010 reference solutions before any of
these results were produced: it reproduces their published objective values
exactly, including the ones marked proven optimal, which is what gives
confidence that the rounding matches the reference model term by term.

The method is exact and not anytime, so there is no objective time series: the
dynamic program produces no incumbent before it returns the optimum.

Code: https://github.com/mnn31/qoblib-solvers/tree/main/portfolio
