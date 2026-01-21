# Integer Linear Programming Formulation

This directory contains the integer linear programming formulation for the Birkhoff problem.

## Model

$$
\begin{array}{rll}
    \min & \displaystyle\sum_{i \in I} z_i & \\
    \text{s.t.} & \displaystyle\sum_{i \in I} \lambda_i = S & \\
    & \displaystyle\sum_{i \in I} \lambda_i P_i = A & \\
    & 0\leq \lambda_i \leq S \cdot z_i & \forall i \in I \\
    & z_i \in \{0,1\} & \forall i \in I
\end{array}
$$

## Variables and Parameters

- $I \coloneqq \{1,\ldots,n!\}$: Index set of the permutation matrices
- $P_i$ for $i \in I$: Permutation matrices
- $S$: Integer scale (typically chosen to be $1000$)
- $\lambda_i$: Continuous variables representing weights
- $z_i$: Binary decision variables