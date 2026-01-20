# Integer Programming Formulation

This directory contains the integer programming formulation for the Network Design problem.

## Model

$$
\begin{darray}{lll}
    \min & z & \\
    \text{s.t.} & \sum_{a \in \delta^+(v)} x_{a} = 2 & \forall v \in V \\
    & \sum_{a \in \delta^-(v)} x_{a} = 2 & \forall v \in V \\
    & \sum_{a \in \delta^+(t)} f_{s,a} - \sum_{a \in \delta^-(t)} f_{s,a} = t_{s, t} & \forall s, t \in V, s \neq t \\
    & \sum_{s \in V} f_{s, a} \leq z & \forall a \in A \\
    & f_{s, a} \leq M \cdot x_a & \forall s \in V, a \in A \\
    & f_{s,a} \geq 0 & \forall s \in V, a \in A \\
    & x_{a} \in \{0,1\} & \forall a \in A \\
    & z \geq 0 &
\end{darray}
$$

## Variables and Parameters

- $V$: Set of vertices
- $A$: Set of arcs
- $x_a$: Binary decision variables for arc selection
- $f_{s,a}$: Flow variables for commodity $s$ on arc $a$
- $z$: Objective variable (maximum flow)
- $M$: Big-M parameter (sufficiently large constant)
- $\delta^+(v)$: Set of outgoing arcs from vertex $v$
- $\delta^-(v)$: Set of incoming arcs to vertex $v$
- $t_{s,t}$: Traffic demand from node $s$ to node $t$

## Description

This formulation describes a multi-commodity flow problem where flow on an arc is only permitted if this arc is chosen to be in the solution. The big-M parameter $M$ should be chosen sufficiently large to not constrain the problem.
