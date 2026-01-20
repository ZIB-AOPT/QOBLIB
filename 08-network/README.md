# 08 - Network Design

**Application Area:** Telecommunications Network Planning

[← Back to Main Repository](../README.md)

---

## Overview

The Network Design problem involves constructing a cost-efficient communication network that can handle specified traffic demands while maintaining degree constraints. This problem is relevant for telecommunications, data center design, and logistics networks.

<p align="center">
  <img src="./misc/figure.png" width="400" alt="Network Design Visualization">
</p>

## Problem Description

Given an $n \times n$ demand matrix $T$ (where $t_{ij}$ represents traffic from node $i$ to node $j$) and an integer $p > 0$:

1. **Construct** a simple directed graph $D$ with node set $\{1,\ldots,n\}$ where each node has in-degree and out-degree equal to $p$
2. **Route** $t_{ij}$ units of flow from $i$ to $j$ for all $1 \leq i, j \leq n$ with $i \neq j$
3. **Minimize** the maximum aggregate flow on any edge of $D$

**Instance Parameters:**
- $p = 2$ (each node has 2 incoming and 2 outgoing connections)
- $n \in \{5, \ldots, 24\}$ nodes
- Demand matrix entries: $t_{ij} \in \{0\} \cup [16, 100]$

## Directory Contents

- **[instances/](instances/)** - Network demand matrices
- **[models/](models/)** - Mathematical model formulations
- **[solutions/](solutions/)** - Optimal or best-known solutions
- **[check/](check/)** - Solution verification tools
- **[info/](info/)** - Additional documentation
- **[submissions/](submissions/)** - Community solution submissions

## References

* **Bienstock, D., Günlük, O.** (1995). [Computational experience with a difficult mixed-integer multicommodity flow problem](https://doi.org/10.1007/BF01585766). Mathematical Programming 68, 213–237.
