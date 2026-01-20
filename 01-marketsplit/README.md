# 01 - Market Split Problem

**Alternative Names:** Multi-Dimensional Subset Sum Problem

[← Back to Main Repository](../README.md)

---

## Overview

The Market Split Problem is a multi-dimensional variant of the classic subset sum problem, where multiple constraints must be satisfied simultaneously. Each row represents its own subset sum problem, making this a challenging combinatorial optimization task.

## Problem Description

Given a matrix $A \in \mathbb{N}^{m,n}$ and a right-hand side vector $b \in \mathbb{N}^m$, find a feasible binary vector $x \in \{0,1\}^{n}$ that satisfies:

$$
Ax = b
$$

where each row $i \in \{1,\ldots,m\}$ represents an independent subset sum constraint that must be fulfilled simultaneously.

## Directory Contents

- **[instances/](instances/)** - Problem instances in various formats
- **[models/](models/)** - Mathematical model formulations
- **[solutions/](solutions/)** - Optimal or best-known solutions
- **[check/](check/)** - Solution verification tools
- **[misc/](misc/)** - Utility scripts and instance generators
- **[submissions/](submissions/)** - Community solution submissions

## References

* **Cornuéjols, G., Dawande, M.** (1998). [A Class of Hard Small 0—1 Programs](https://doi.org/10.1007/3-540-69346-7_22). In: Bixby, R.E., Boyd, E.A., Ríos-Mercado, R.Z. (eds) Integer Programming and Combinatorial Optimization. IPCO 1998. Lecture Notes in Computer Science, vol 1412. Springer, Berlin, Heidelberg.
