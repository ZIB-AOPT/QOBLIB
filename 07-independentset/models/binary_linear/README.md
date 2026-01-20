# Binary Linear Programming Formulation

This directory contains the standard binary linear programming formulation for the Maximum Independent Set problem.

## Model

$$
\begin{darray}{ll}
    \max & \sum_{v \in V} x_v \\
    \text{s.t.} & x_v + x_w \leq 1 & \forall (v,w) \in E \\
    & x_v \in \{0,1\} & \forall v \in V
\end{darray}
$$

## Variables and Parameters

- $V$: Set of vertices
- $E$: Set of edges
- $x_v$: Binary decision variables indicating whether vertex $v$ is in the independent set