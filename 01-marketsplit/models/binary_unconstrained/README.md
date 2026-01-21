# Binary Unconstrained Programming Formulation

This directory contains the binary unconstrained programming formulation for the Market Split problem.

## Model

$$
\begin{array}{rll}
    \min & \displaystyle\sum_{i \in I} \left(b_i - \sum_{j \in J} a_{ij} x_j\right)^2 & \\
    \text{s.t.} & x_j \in \{0,1\} & \forall j \in J
\end{array}
$$

## Variables and Parameters

- $A = [a_{ij}] \in \mathbb{N}^{m,n}$: Coefficient matrix
- $I \coloneqq \{1,\ldots,m\}$: Row index set
- $J \coloneqq \{1,\ldots,n\}$: Column index set
- $x_j$: Binary decision variables

## Feasibility

A feasible solution has been found when the objective value is $0$.

## Notes

This formulation can be readily transformed into QUBO (Quadratic Unconstrained Binary Optimization) form. 