# Method Overview

The **Aqarios Constrained Quantum Optimizer** is a fixed-angle iterative warm-start QAOA implementation with support for XY-Mixers to enforce one-hot constraints (see [Paper](https://arxiv.org/abs/2604.02083) for more details).

The following steps are executed:

1. **Preprocessing**
    - Identify constraint types
    - Check for set-packing constraints
        - Fix pendant and simplicial nodes
        - Extract cliques and replace multiple constraints by a single one
    - Constraint resolution
        - Apply constraint transformations, e.g. set-packing to one-hot
        - Evaluate penalty coefficient
        - Enforce one-hot constraints with XY-mixers
        - Penalize equality constraints with quadratic penalties
        - Penalize inequality constraints with unbalanced penalties
    - Evaluate scaling constant
    - Synthesize circuit
    - Transpile to hardware
2. **Algorithm Phase**
    - Initialize with uniform initial probabilities
    - Sample from QAOA with fixed angles
    - Greedy postprocessing of samples
    - Evaluate new warm-start probabilities with Boltzmann weights
    - Continue sample and update probabilities until the maximum number of shots have been gathered
3. **Postprocessing**
    - Evaluate all gathered samples for feasibility and find the best samples


## Algorithm Details

### Clique Extraction

The preprocessing step tries to find the largest cliques in the set-packing graph. When cliques exist, all constraints $x_i + x_j \leq 1 \ \forall (i, j) \in E_C$ can be replaced by a single constraint $\sum_{i\in V_C} x_i \leq 1$, where $(V_C, E_C)$ represent the clique nodes and edges. These set-packing constraints can subsequently be represented as a one-hot constraint by adding a slack binary variable, i.e., $\sum_i x_i + y = 1$.

Since finding the maximum cliques is itself NP-hard, we rely on heuristics in general and use exact methods only for sparse graphs. In particular, we use a combination of [igraph](https://igraph.org/python/versions/0.10.1/api/igraph.GraphBase.html#largest_cliques) and [cliquematch](https://cliquematch.readthedocs.io/en/stable/api.html#cliquematch.NWGraph.get_max_clique), where we utilize igraph's `largest_cliques` method for sparse graphs (density $\leq 0.1$) and cliquematch's `get_max_clique(use_heuristic=True, use_dfs=False)` heuristic for denser graphs.
We iteratively find an approximate largest clique, remove it from the graph and continue until no more cliques can be identified. All of these set-packing cliques can then be enforced with an XY-mixer.

#### Found cliques

**sloane_1dc_128**

Average runtime: _42 ms_

```
[10, 18, 19, 20, 22, 38, 42, 74]
[7, 11, 13, 14, 15, 23, 39, 71]
[16, 24, 28, 30, 31, 32, 48, 80]
[43, 75, 83, 85, 86, 87, 91, 107]
[58, 90, 106, 114, 115, 116, 118, 122]
[25, 41, 49, 50, 51, 53, 57, 89]
[47, 55, 59, 61, 62, 63, 95]
[36, 68, 70, 72, 76, 84, 100]
[81, 97, 98, 99, 101, 105, 113]
[44, 52, 54, 56, 60, 92, 108]
[21, 26, 27, 29, 45, 77]
[93, 109, 117, 121, 123, 125]
[46, 78, 88, 94, 110]
[4, 6, 8, 12]
[34, 35, 67, 82]
[79, 103, 104, 111]
```

**sloane_2dc_128**

Average runtime: _206 ms_
```
[14, 22, 23, 26, 27, 38, 39, 42, 43, 44, 45, 46, 47, 51, 52, 53, 54, 55, 59, 75, 77, 78, 83, 86, 87, 90, 91, 103]
[50, 57, 58, 82, 85, 89, 98, 99, 100, 101, 102, 105, 106, 107, 109, 113, 114, 115, 117, 121]
[8, 12, 15, 16, 20, 24, 28, 36, 40, 68, 70, 71, 72, 76, 79, 84]
[29, 30, 31, 61, 93]
```

**sloane_1zc_128**

Average runtime: _33 ms_
```
[4, 8, 12, 20, 36, 68]
[16, 24, 28, 30, 31, 32]
[13, 14, 15, 29, 45, 77]
[40, 72, 100, 102, 103, 104]
[49, 50, 51, 53, 57, 113]
[58, 90, 106, 114, 121, 122]
[66, 67, 69, 73, 81, 97]
[63, 95, 111, 119, 123, 125]
[22, 70, 82, 85, 86]
[43, 44, 47, 59, 107]
[83, 84, 87, 91, 115]
[6, 7, 21, 37]
[46, 48, 62, 110]
[10, 26, 42, 74]
[56, 88, 116, 118]
[61, 93, 109, 117]
[11, 19, 25, 27]
```

None in the `es60fst` instances.


### XY-Mixers

For hardware implementation cost reasons, we construct the XY-mixer with a line topology and a single trotter step.
