# QOBLIB Stable Set Problem Solution Checker

This program is part of **QOBLIB - Quantum Optimization Benchmarking Library** and is designed to **verify solutions** to *Stable Set Problems*. It checks whether a given set of nodes in an undirected graph forms a **valid stable set** — that is, no two selected nodes share an edge.

## Problem Description

The maximum stable set problem - also often referred to as maximum stable set problem - describes the challenge of finding an stable set $I$ of a graph $G=(V,E)$ of maximum cardinality. 
$I$ is considered to be stable, if there does not exist an edge in $G$ between nodes of $I$.

## What This Checker Does

Given a graph and a proposed solution, this checker:

1. Parses the input graph (in DIMACS-like format).
2. Parses the solution (in several accepted formats).
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

Multiple formats are supported. The format is auto-detected:

#### 1. Binary string

A string of 0s and 1s, each representing whether the node is in the stable set.

- Inline:
```
010010
```

- Spaced or comma-separated:
```
0 1 0 0 1 0
```

#### 2. Index list

A list of 1-based node indices included in the set:
```
2
5
```

Or:
```
2 5
```

#### 3. Named variable format (e.g., from MIP solvers)

```
x#1 0
x#2 1
x#3 0
...
```

Only lines starting with `x#` are used.

## Usage

### Building

First, build the checker using Cargo:

```bash
cargo build --release
```

### Command

```bash
./target/release/check_stableset <graph-file> <solution-file-or-01-string>
```

### Arguments

* `graph-file`: Path to graph file or `-` for stdin
* `solution`: Path to solution file or a binary string directly

### Examples

Using a file:

```bash
./target/release/check_stableset graph.txt solution.txt
```

Using an inline binary string:

```bash
./target/release/check_stableset graph.txt 010101
```

## Output

If the solution is correct:

```
QOBLIB Stable Set Solution Checker Version 1.0
Graph has 6 nodes, 5 edges, 1 components, stable set size = 3 is ok
```

If invalid:

```
Graph has 6 nodes, 5 edges, 1 components, stable set size = 3 is wrong!
```

## Exit Codes

- **0**: Solution is valid
- **1**: Solution is invalid
- **2**: Error (e.g., file not found, parsing error)

## License

Part of **QOBLIB**, released under [**Apache 2.0**](http://www.apache.org/licenses/LICENSE-2.0).

## Author

**Thorsten Koch**
© 2025
