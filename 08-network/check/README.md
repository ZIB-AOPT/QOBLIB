# QOBLIB Network Design Solution Checker

This program is part of **QOBLIB - Quantum Optimization Benchmarking Library** and is designed to **verify solutions** to *Network Design Problems*. It checks whether a proposed network topology satisfies degree constraints and correctly routes flows according to demand.

## Problem Description

Design a network with N nodes (between 5 and 24) where each node has exactly two incoming and two outgoing connections. The objective is to minimize the maximum aggregate flow on any edge while routing traffic according to a demand matrix.

## What This Checker Does

Given an instance size, demand matrix, and solution file, this checker:

1. **Parses** the Gurobi-format solution file.
2. **Validates** degree constraints (each node has exactly 2 in-edges and 2 out-edges).
3. **Verifies** flow conservation for each commodity at each node.
4. **Checks** that flows only use existing edges.
5. **Computes** the maximum aggregate flow and verifies it matches the objective.

This program does **not** check for optimality.

## Input Format

### Solution File

The checker reads Gurobi solution files with the following format:

```
# Solution for model obj
# Objective value = 65500
z 65500
x#1#5 0
x#1#4 0
x#1#3 1
...
f#1#2#5 21000
f#1#2#4 0
...
```

Where:
- `z` is the objective value (maximum flow on any edge, scaled by 1000)
- `x#i#j` is 1 if there's an edge from node i to node j, 0 otherwise
- `f#k#i#j` is the amount of flow for commodity k on edge (i,j), scaled by 1000

## Usage

### Building

First, build the checker using Cargo:

```bash
cargo build --release
```

### Command

```bash
./target/release/check_network <instance_size> <demand_file> <solution_file>
```

### Arguments

* `instance_size`: Number of nodes (e.g., 5 for network05)
* `demand_file`: Path to the demand matrix file
* `solution_file`: Path to the solution file

### Examples

Check a single solution:

```bash
./target/release/check_network 5 ../instances/demand.txt ../solutions/network05.opt.sol
```

Check all solutions:

```bash
./check_all.sh
```

## Output

The checker validates:

1. **Degree constraints**: Each node has exactly in-degree = 2 and out-degree = 2
2. **Flow conservation**: For each commodity k at each node i (i ≠ k), the net flow equals the demand
3. **Flow capacity**: Flows can only use edges where x[i,j] = 1
4. **Objective value**: The maximum aggregate flow matches the reported objective

If all checks pass:

```
Solution is valid
```

Otherwise, specific constraint violations are reported.

## Exit Codes

- **0**: Solution is valid
- **1**: Solution is invalid
- **2**: Error (e.g., file not found, parsing error)

## License

Part of **QOBLIB**, released under [**Apache 2.0**](http://www.apache.org/licenses/LICENSE-2.0).

## Author

**Maximilian Schicker**
© 2025
