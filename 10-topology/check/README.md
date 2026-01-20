# QOBLIB Order-Degree Problem Solution Checker

This program is part of **QOBLIB - Quantum Optimization Benchmarking Library** and is designed to **verify solutions** to *Order-Degree Problems* on undirected graphs. It reads a graph representation and checks whether it meets the required properties: node count, maximum degree, connectedness, and diameter.

## Problem Description

An *Order-Degree Problem* asks:

> "Given a number of nodes `n`, what is the minimal possible diameter of an undirected graph with maximum degree `d`?"

This checker validates whether a given graph is a valid solution to a specific instance of this problem.

## What This Checker Does

Given a file describing an undirected graph and required parameters:

- **node count** `n`
- **maximum degree** `d`
- **required diameter** `D`

It verifies that:

1. The number of nodes matches `n`.
2. The maximum node degree is ≤ `d`.
3. The graph is connected (single component).
4. The graph's diameter is ≤ `D`.

This program does **not** check for optimality. 

## Input Format

### Supported File Types

- Plain `.txt` files
- Gzip-compressed `.gz` files
- Standard input (`-` as filename)

### Expected Format (DIMACS-like)

- Comment lines start with `c`
- Problem line starts with `p` and has the format:

```
p edge <node_count> <edge_count>
```

- Edge lines start with `e` and have the format:

```
e <node1> <node2>
```

- Node numbers are **1-based**.

#### Example
```
c Sample graph with diameter 3
p edge 15 22
e 1 9
e 1 11
e 1 12
e 2 7
e 2 10
...

```

## Usage

### Building

First, build the checker using Cargo:

```bash
cargo build --release
```

### Command

```bash
./target/release/check_order <node-count> <max-degree> <diameter> <graph-file>
```

### Arguments:

* `node-count`: Expected number of nodes in the graph
* `max-degree`: Maximum allowed degree of any node
* `diameter`: Required maximum graph diameter
* `graph-file`: Path to the graph file (or `-` to read from stdin)

### Example

```bash
./target/release/check_order 15 3 3 my_graph.txt
```

## Output

Example output:

```
QOBLIB Order-Degree Solution Checker Version 1.0
Graph my_graph has 15 nodes, 22 edges, max degree 3, diameter 3, ok
```

If the graph fails any criteria, the output highlights mismatches:

```
Graph my_graph has 15 nodes, expected 16, 22 edges, max degree 4, expected 3, 2 components, diameter 4, expected 3, failed
```

## Exit Codes

- **0**: Solution is valid
- **1**: Solution is invalid
- **2**: Error (e.g., file not found, parsing error)

## License

Part of **QOBLIB**, released under [**Apache 2.0**](http://www.apache.org/licenses/LICENSE-2.0).

## Author

**Thorsten Koch**
Copyright © 2025

