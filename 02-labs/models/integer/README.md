# Integer Programming Formulation

This directory contains the integer programming formulation for the Low Autocorrelation Binary Sequences (LABS) problem.

## Model

$$
\begin{darray}{lll}
    \min & \sum_{k=1}^{n-1} c_k^2 & \\
    \text{s.t.} & c_k = \sum_{i=1}^{n-k} (2 x_i - 1) (2 x_{i+k} - 1) & \forall k \in \{1,\ldots,n-1\} \\
    & x_i \in \{0,1\} & \forall i \in \{1,\ldots,n\} \\
    & c_k \in \{-n+k,\ldots,n-k\} & \forall k \in \{1,\ldots,n-1\}
\end{darray}
$$

## Notes

We use the substitution $z = 2x-1$ to work with binary variables instead of spin variables. 