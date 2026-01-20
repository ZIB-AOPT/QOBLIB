# Binary Linear Programming Formulation

This directory contains the binary linear programming formulation for the Market Split problem.

## Model

$$
\begin{darray}{rll}
    \min & \sum_{i \in I} s_i & \\
    \text{s.t.} & s_i + \sum_{j \in J} a_{ij} x_j = b_i & \forall i \in I \\
    & s_i \geq 0 & \forall i \in I \\
    & x_j \in \{0,1\} & \forall j \in J
\end{darray}
$$

## Variables and Parameters

- $A = [a_{ij}] \in \mathbb{N}^{m,n}$: Coefficient matrix
- $I \coloneqq \{1,\ldots,m\}$: Row index set
- $J \coloneqq \{1,\ldots,n\}$: Column index set
- $x_j$: Binary decision variables
- $s_i$: Slack variables

## Feasibility

A feasible solution has been found when the objective value is $0$.