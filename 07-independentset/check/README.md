# QOBLIB Stable Set Problem Solution Checker

This program is part of **QOBLIB - Quantum Optimization Benchmarking Library** and is designed to **verify solutions** to *Stable Set Problems*. It checks whether a given set of nodes in an undirected graph forms a **valid stable set** — that is, no two selected nodes share an edge.

## Problem Description

The maximum stable set problem - also often referred to as maximum stable set problem - describes the challenge of finding an stable set $I$ of a graph $G=(V,E)$ of maximum cardinality. 
$I$ is considered to be stable, if there does not exist an edge in $G$ between nodes of $I$.

## What This Checker Does

Given a graph and a proposed solution, this checker:

1. Parses the input graph (in DIMACS-like format).
2. Parses the solution (a list of node indices).
3. Verifies that the selected nodes form a valid **stable set**.
4. Reports the number of nodes, edges, components, and size of the stable set.
5. Confirms validity or reports a violation.

This program does **not** check for optimality.

## Input Format

### Graph File

The graph must be in **DIMACS format** or gzipped `.gz`. Use `-` to read from stdin.

#### Supported Lines

- Comment lines:  
```
c This is a comment
```

- Problem line:  
```
p edge <node_count> <edge_count>
```

- Edge lines:  
```
e <node1> <node2>
```

#### Example

```
c Small stable set instance
p edge 6 5
e 1 2
e 2 3
e 3 4
e 4 5
e 5 6
```

### Solution Format

The solution is an **index list**: the 1-based indices of the nodes in the stable set, separated by whitespace (usually one index per line). Lines starting with `#` are comments.

```
# Objective value = 3
1
3
5
```

This is the only accepted format. The solution file is rejected as invalid if it contains

- anything other than node indices and `#` comment lines (e.g., a 0/1 vector or the `x#1 0` lines of a MIP solver solution),
- an index outside `1..<node_count>` (node indices are 1-based, so `0` is not a valid index),
- an index that is listed more than once, or
- no index at all.

## Usage

### Building

First, build the checker using Cargo:

```bash
cargo build --release
```

### Command

```bash
./target/release/check_stableset <graph-file> <solution-file>
```

### Arguments

* `graph-file`: Path to graph file or `-` for stdin
* `solution-file`: Path to solution file

### Example

```bash
./target/release/check_stableset graph.txt solution.txt
```

## Output

If the solution is a stable set:

```
Qbench Stable Set Solution Checker Version 2.0
Graph has 6 nodes, 5 edges, 1 components, stable set size = 3 is ok
VALID: Solution successfully verified
```

If the selected nodes are not a stable set:

```
Qbench Stable Set Solution Checker Version 2.0
Graph has 6 nodes, 5 edges, 1 components, stable set size = 3 is wrong!
INFEASIBLE: Valid solution file, but the set is not stable
```

If the solution file is invalid:

```
Qbench Stable Set Solution Checker Version 2.0
INVALID_FILE: ... Solution line 1. Expected node index found x#1
```

## Exit Codes

The exit codes follow the [checker contract](../../misc/ci/CHECKER_CONTRACT.md):

- **0**: Solution file is valid and the selected nodes are a stable set
- **21**: Solution file is valid, but the selected nodes are not a stable set
- **10**: Solution file is invalid (see [Solution Format](#solution-format))
- **2**: Usage error (e.g., missing arguments, file not found)

## License

Part of **QOBLIB**, released under [**Apache 2.0**](http://www.apache.org/licenses/LICENSE-2.0).

## Author

**Thorsten Koch**
© 2025
