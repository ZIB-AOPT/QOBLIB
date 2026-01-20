# Integer Linear Programming Formulation

This directory contains the integer linear programming formulation for the Capacitated Vehicle Routing Problem (CVRP).

## Model

$$
\begin{align*}
    \min_{x,y} & \sum_{\substack{i,j=0 \\ i \neq j}}^{n+1} c_{ij} x_{ij} \\
    \text{s.t.} & \sum_{\substack{j=1 \\ j \neq i}}^{n+1} x_{ij} = 1 & \forall i \in \{ 1, \ldots, n\} \\
    & \sum_{\substack{i=0 \\ i \neq h}}^{n} x_{ih} = \sum_{\substack{j=1 \\ j \neq h}}^{n+1} x_{hj} & \forall h \in \{1, \ldots, n \} \\
    & \sum_{j=1}^{n} x_{0j} \leq K \\
    & y_{j} \geq y_{i} + d_j x_{ij} - Q ( 1 - x_{ij} ) & \forall i\neq j \in \{ 0, \ldots, n+1\} \\
    & d_{i} \leq y_{i} \leq Q & \forall i \in \{0, \ldots, n+1\} \\
    & x_{ij} \in \{0,1\} & \forall i,j \in\{0, \ldots, n+1\} \\
    & y_{i} \in \mathbb{N}_0 & \forall i \in\{ 0, \ldots, n+1\}
\end{align*}
$$

## Variables and Parameters

- $x_{ij}$: Binary decision variables indicating whether the arc from $i$ to $j$ is used
- $y_i$: Integer variables representing cumulative demand/capacity usage
- $c_{ij}$: Cost of traveling from location $i$ to location $j$
- $d_i$: Demand at location $i$
- $K$: Maximum number of vehicles
- $Q$: Vehicle capacity
- $n$: Number of customers

## Notes

For a detailed review of the constraints and variables, please refer to the main paper. 