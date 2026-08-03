e done# Partitioned QAOA E-FCFW Submission

This folder contains benchmarking results for the Birkhoff decomposition problem using a
quantum-classical hybrid approach combining Partitioned QAOA with Enhanced Frank-Wolfe
(E-FCFW) decomposition.

**Submitter:** Stephen DiAdamo (Qoro Quantum Ltd.)
**Affiliation:** Qoro Quantum Ltd., in collaboration with E.ON
**Date:** 2026-08-03

## Method

The algorithm decomposes a doubly stochastic matrix into a convex combination of
permutation matrices using the Enhanced Fully-Corrective Frank-Wolfe (E-FCFW) framework.
At each iteration, the method:

1. **Graph Partitioning:** The residual demand matrix is treated as a weighted bipartite
   graph. Kernighan-Lin bisection partitions the graph into subgraphs with at most
   `partition_size` edges each.
2. **QAOA Sampling:** Each partition is encoded as a QUBO maximum weight matching problem
   and solved via the Quantum Approximate Optimization Algorithm (QAOA) with 1 layer,
   executed on IBM Quantum hardware (ibm_pittsburgh) through Qoro Cloud Services.
3. **Greedy Repair & Beam Search:** Raw QAOA samples are repaired to ensure valid matchings.
   A beam search aggregation strategy constructs high-weight matchings from the partition
   solutions.
4. **Edge-Swap Refinement:** Local edge-swap moves improve matching weights post-aggregation.
5. **Weight Reoptimisation:** CPLEX reoptimises the convex combination weights across all
   accumulated matchings, discarding zero-weight matchings.

Edges discarded during partitioning are reintroduced in subsequent iterations.
The process repeats for a fixed number of iterations (default: 15).

## Software

- **Divi** (Qoro Quantum): QAOA circuit construction, compilation, and execution
- **CPLEX** (IBM): Convex weight reoptimisation
- **NetworkX**: Graph partitioning (Kernighan-Lin)

## Instance Naming

Each subfolder `B{X}_{Y}_{Z}` holds the result for one instance:
- `X` is the size of the doubly stochastic matrix (e.g., X = 16 for a 16×16 matrix).
- `Y` is the density indicator. Sparse matrices have Y = X; dense matrices have Y = X².
- `Z` is the instance id (1–10).

## References

- E-FCFW framework: Pennington & Mohseni, arXiv:2412.07254
- QOBLIB benchmark: https://arxiv.org/pdf/2504.03832
