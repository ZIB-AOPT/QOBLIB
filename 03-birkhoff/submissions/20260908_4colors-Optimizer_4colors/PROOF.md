# Optimality certificates for 03-birkhoff

Marcin Kaminski, 4colors Research. Code under Apache-2.0.

This submission asserts optimality on 18 instances. This note gives the argument, the code that
reproduces it, and the two independent checks that back it.

## The argument

A solution writes the scaled matrix `D` as a non-negative combination of permutation matrices. Every
term of such a combination is a perfect matching of the **support** of `D`: a term placing positive
weight on a cell where `D` is zero could never be cancelled, because all weights are non-negative.

So the set of admissible columns is exactly the set of perfect matchings of the support — finite,
and at these sizes small enough to list in full. Optimality of an incumbent of size `k` then reduces
to one question:

> is there a non-negative combination of at most `k-1` of those columns that reconstructs `D`?

A negative answer is a proof that `k` is optimal. The question is posed as a pure feasibility model,
with no objective, so the certificate is the word INFEASIBLE and nothing else.

## The model

For each admissible column `p`:

| | |
|---|---|
| `x_p >= 0` | weight given to column `p` |
| `y_p in {0,1}` | 1 if column `p` is used |
| reconstruction | `sum_p x_p [p hits (i,j)] = D[i][j]` for every cell |
| linking | `x_p <= cap_p * y_p` |
| cardinality | `sum_p y_p <= k-1` |

`cap_p` is the smallest entry of `D` under `p`. That is the largest weight the column could ever
carry, so the linking constraint is tight rather than a big-M, which is what keeps these models
solvable at all.

All data are the scaled integers from the instance file. No floating point enters the model.

## Reproducing it

`birkhoff_proof.py` depends on the Python standard library alone — no solver bindings, no project
imports, no code shared with our heuristics.

    # list the admissible columns and cross-check the count
    python3 birkhoff_proof.py 03-birkhoff/instances/qbench_09_sparse.json B9_9_1

    # write the feasibility model for any MILP solver
    python3 birkhoff_proof.py 03-birkhoff/instances/qbench_09_sparse.json B9_9_1 --k 9 --lp B9_9_1.lp

The `.lp` file is plain CPLEX LP format, readable by Gurobi, HiGHS, SCIP and CBC. Solving it and
getting INFEASIBLE reproduces the certificate independently of our software.

## Check 1 — the column set is complete

An enumeration that missed a column would make an infeasibility result meaningless. The number of
perfect matchings of a 0/1 matrix is its permanent, so the enumeration is cross-checked against
Ryser's inclusion-exclusion formula

    per(A) = (-1)^n * sum over column subsets S of (-1)^|S| * prod_i sum_{j in S} A[i][j]

computed in exact integer arithmetic by a separate routine that shares no code with the enumerator.
The two agree on every instance where a certificate was produced. Column sets run from 2 to 13,030.

## Check 2 — a solver-free replication at n = 3

At `n = 3` the same question is answered without any solver: every subset of `k-1` columns is
enumerated, the resulting equality system is solved in exact rational arithmetic by Gaussian
elimination over `fractions.Fraction`, and non-negativity is checked directly.

    python3 birkhoff_proof.py 03-birkhoff/instances/qbench_03_sparse.json --all --k 3 --exact

This agrees with the solver on every `n = 3` instance, including the ones where a witness *does*
exist and the answer is therefore "not optimal" — so the check has teeth in both directions.

## What the certificates rest on

| | |
|---|---|
| instances with a certificate | 65 |
| of which asserted in this submission | 18 (6 each at n = 7, 8, 9) |
| produced by Gurobi | 50 |
| produced by HiGHS | 15 |

Two solvers were used because a restricted Gurobi license caps a model at 2000 variables; models
above that were sent to HiGHS. For `n >= 4` the infeasibility result comes from a solver and is
contingent on that solver being correct. The `.lp` export exists so the reader does not have to take
either solver's word for it.

The 47 further instances where the enumeration closed are not part of this submission: 37 reproduce
a recorded optimum and 10 are reported separately as a status change.

## Files

    birkhoff_proof.py    enumeration, Ryser cross-check, .lp export, exact n = 3 replication
    PROOF.md             this note
