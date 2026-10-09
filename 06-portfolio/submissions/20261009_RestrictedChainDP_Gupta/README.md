# Restricted state chain dynamic program for the large portfolio families

The exact chain dynamic program in the ChainDP submission enumerates every
feasible per period portfolio, which is impossible for a050 and above. This
submission keeps the chain structure but restricts each period to a pool of good
portfolios found by exact integer local search, exact subset enumeration and
relaxation roundings, runs the exact chain dynamic program over the pools, and
polishes by coordinate descent. The method is a heuristic and claims no
optimality.

Validation before any of this was produced: it matches the proven optimum on all
160 instances of the a003 to a010 families, and on a050 it is within a few
hundredths of a percent of the published values at low lambda and clearly worse
at the two highest lambdas, where the published values come from a MIP solver.
Those a050 runs are included here so the gap is on record.

The a200 and a400 families had no feasible solution on record. Every solution
here was verified with 06-portfolio/check as it was produced.

Code: https://github.com/mnn31/qoblib-solvers/tree/main/portfolio
