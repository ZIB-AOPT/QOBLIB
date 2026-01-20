# 03 - Minimum Birkhoff Decomposition

[← Back to Main Repository](../README.md)

---

## Overview

The Minimum Birkhoff Decomposition problem seeks to express a doubly stochastic matrix as a minimal convex combination of permutation matrices. This problem arises in various applications including assignment problems, scheduling, and quantum physics.

## Problem Description

**Definitions:**
- A **doubly stochastic matrix** $D \in \mathbb{R}^{n \times n}$ has non-negative entries where all rows and columns sum to one
- A **permutation matrix** $P_i$ is a doubly stochastic matrix with binary entries
- Let $P_1, \ldots, P_{n!}$ denote all possible $n \times n$ permutation matrices

**Optimization Problem:**

For a given doubly stochastic matrix $D$, find:

$$
\underset{\lambda_i \in [0,1]}{\text{minimize}} \qquad  \sum_{i=1}^{n!} |\lambda_i|^0
$$

subject to:
$$
D = \sum_{i=1}^{n!} \lambda_i P_i, \qquad  \sum_{i=1}^{n!} \lambda_i = 1
$$

where $0^0 = 0$ by convention.

**Goal:** Find the smallest number of permutation matrices whose convex combination equals $D$.

## Directory Contents

- **[instances/](instances/)** - Doubly stochastic matrices to decompose
- **[models/](models/)** - Mathematical model formulations
- **[solutions/](solutions/)** - Optimal or best-known solutions
- **[check/](check/)** - Solution verification tools
- **[misc/](misc/)** - Utility scripts and generators
- **[submissions/](submissions/)** - Community solution submissions

## References

1. **Kulkarni, J., Lee, E., Singh, M.** (2017). [Minimum Birkhoff-von Neumann Decomposition](https://doi.org/10.1007/978-3-319-59250-3_28). In International Conference on Integer Programming and Combinatorial Optimization (pp. 343-354). Springer International Publishing, Cham.

2. **Dufossé, F., Uçar, B.** (2016). [Notes on Birkhoff–von Neumann decomposition of doubly stochastic matrices](https://doi.org/10.1016/j.laa.2016.02.023). Linear Algebra and its Applications, 497, pp.108-115.
 
