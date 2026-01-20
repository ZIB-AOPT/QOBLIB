# QOBLIB Node-Disjoint Steiner Tree Solution Checker

This program is part of **QOBLIB - Quantum Optimization Benchmarking Library** and is designed to **verify solutions** to the *Node-Disjoint Steiner Tree Problem (ND-STP)*. It checks whether proposed trees correctly connect terminals while maintaining node-disjointness.

## Problem Description

Given:

- An undirected graph with edge weights
- Several groups of **terminal nodes**, each group representing a **network**
- A proposed set of trees, one per network

The problem requires:

1. Each **tree** to connect all terminals of its network (Steiner Tree).
2. The trees to be **node-disjoint**, i.e., no node appears in more than one tree.
3. The total cost (sum of edge weights) to be minimized.

## What This Checker Does

Given three input files (`arcs`, `terminals`, and `solutions`), the program:

1. Verifies that each **network's terminals** are all present in the selected subgraph.
2. Ensures the **subgraph is connected** (i.e., forms a tree for that network).
3. Ensures **node-disjointness** across all networks.
4. **Computes the total cost** (sum of weights of selected edges).

If all checks pass, it confirms that the proposed solution is valid and prints the total cost.

The program does **not** check for optimality. 

## Input Files

### 1. Arcs File (`--arcs`)

Describes the undirected graph.  
Each line:

```
node1 node2 weight
```

- Comments starting with `#` and empty lines are ignored.
- The edge is undirected, so `(u, v)` = `(v, u)`.

#### Example

```
# Undirected graph

1 2 5
2 3 4
3 4 6
```

### 2. Terminals File (`--terms`)

Lists terminals for each network.  
Each line:

```
node network_id
```

- Each network must have at least one terminal.
- Comments and blank lines are ignored.

#### Example

```
# Format: node_id network_id

1 0
3 0
5 1
6 1
```


### 3. Solutions File (`--sol`)

Specifies which edges are selected in the solution.  
Each line:

```
node1 node2 network_id
```

- The edge must exist in the original arcs file.
- Comments and blank lines are ignored.

#### Example

```
1 2 0
2 3 0
5 6 1
```

## Usage

### Building

First, build the checker using Cargo:

```bash
cargo build --release
```

### Command

```bash
./target/release/check_steiner --arcs <arcs-file> --terms <terminals-file> --sol <solution-file>
```

### Arguments

* `--arcs` or `-a`: Path to the arcs file
* `--terms` or `-t`: Path to the terminals file
* `--sol` or `-s`: Path to the solution file

## Output

If all checks pass:

```
Total Cost 42
Successful: All Steiner trees are valid, connected, contain their terminals, and are node-disjoint!
```

If a check fails, a detailed error is shown:

* Terminal not included:

  ```
  Terminal node 5 of network 1 not present in its subgraph.
  ```

* Not connected:

  ```
  Terminal node 6 of network 1 is not connected to the other terminals.
  ```

* Node reuse:

  ```
  Networks 0 and 1 share at least one node, violating node-disjointness.
  ```

* Edge not in arcs:

  ```
  Solutions file line 7 references edge (3, 4) not in arcs.
  ```

## Exit Codes

- **0**: Solution is valid
- **1**: Solution is invalid
- **2**: Error (e.g., file not found, parsing error)

## License

Part of **QOBLIB**, released under [**Apache 2.0**](http://www.apache.org/licenses/LICENSE-2.0).

## Author

**Maximilian Schicker**
© 2025
