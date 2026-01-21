# Quadratic Unconstrained Binary Optimization (QUBO) Formulation

This directory contains the QUBO formulation for the Low Autocorrelation Binary Sequences (LABS) problem. This formulation generates LABS instances from length 2 to 100.

## Model

$$
\begin{array}{rll}
    \min & \displaystyle\sum_{k=1}^{N-1} \left(\sum_{i=1}^{N-k} 4 z_{ik} - 2 x_i - 2 x_{i+k} + 1\right)^2 \\
    & + \displaystyle\sum_{k=1}^{N-1} \sum_{i=1}^{N-k} P (3 z_{ik} - 2 z_{ik} x_i - 2 z_{ik} x_{i+1} + x_i x_{i+k}) & \\
    \text{s.t.} & z_{ik} \in \{0,1\} & \forall i \in \{1, \ldots, N-k\}, \; \forall k \in \{1, \ldots, N-1\} \\
    & x_i \in \{0,1\} & \forall i\in \{1, \ldots, N\}
\end{array}
$$

## Notes

- The penalty term enforces that $z_{ik} = x_i x_{i+k}$
- $P$ is the penalty parameter

## Acknowledgment

Thank you, Noah Krümbugel, for this formulation.