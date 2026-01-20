# Binary Unconstrained Programming Formulation

This directory contains the unconstrained binary formulation for the Maximum Independent Set problem.

## Model

$$
\begin{darray}{ll}
    \max & \sum_{v \in V} x_v - 2 \sum_{(v,w) \in E} x_v x_w \\
    \text{s.t.} & x_v \in \{0,1\} & \forall v \in V
\end{darray}
$$

## Variables and Parameters

- $V$: Set of vertices
- $E$: Set of edges
- $x_v$: Binary decision variables indicating whether vertex $v$ is in the independent set

## Notes

This formulation penalizes edge violations by subtracting $2$ for each edge where both endpoints are selected. 