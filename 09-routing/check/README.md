# QOBLIB CVRP Solution Checker

This program is part of **QOBLIB - Quantum Optimization Benchmarking Library** and is designed to **verify solutions** to *Capacitated Vehicle Routing Problems (CVRP)*. It checks whether a given solution satisfies all constraints and computes the total route cost.

## Problem Description

The Capacitated Vehicle Routing Problem (CVRP) involves:
- A fleet of vehicles with capacity $X$
- A central depot (node 1)
- A set of customers with demands $d_i$
- Coordinates for all locations

The goal is to find routes for all vehicles that:
1. Visit all customers exactly once
2. Start and end at the depot
3. Respect vehicle capacity constraints
4. Minimize total distance

## What This Checker Does

This checker verifies a solution against a CVRP instance file by:

1. **Parsing** the instance file (TSPLIB/CVRPLIB format).
2. **Reading** the solution file with routes.
3. **Validating** each route:
   - Computes total demand on the route.
   - Checks capacity constraint.
   - Calculates Euclidean distance.
4. **Verifying** that all customers are visited exactly once.
5. **Computing** the total cost (sum of all route distances).
6. **Reporting** if the solution is feasible.

## Input Format

### Instance File (TSPLIB/CVRPLIB Format)

```
NAME : <instance-name>
DIMENSION : <number-of-nodes>
CAPACITY : <vehicle-capacity>
NODE_COORD_SECTION
<node-id> <x> <y>
...
DEMAND_SECTION
<node-id> <demand>
...
DEPOT_SECTION
1
-1
EOF
```

- Node 1 is the depot with demand 0
- Distances are computed using Euclidean distance rounded to nearest integer

### Solution File

```
Route #1: <customer1> <customer2> ...
Route #2: <customer3> <customer4> ...
...
Cost <total-cost>
```

- Routes list customer node IDs (excluding depot)
- Each route implicitly starts and ends at the depot
- Cost line is optional but recommended

#### Example
```
Route #1: 15 2 18 1 8
Route #2: 10 11 7 9 6
Route #3: 17 4 5 19 3
Route #4: 20 12 13 14 16
Cost 646
```

## Exit Codes

- **0**: Solution is valid (all constraints satisfied)
- **1**: Solution is invalid (constraint violation detected)
- **2**: Error reading files or parsing

## Building

```bash
cargo build --release
```

The binary will be in `target/release/check_cvrp`.

## Usage

```bash
./target/release/check_cvrp <instance-file> <solution-file>
```

### Example

```bash
./target/release/check_cvrp ../instances/XSH-n20-k4-01.vrp ../solutions/XSH-n20-k4-01.opt.sol
```

## Testing

Run unit tests:
```bash
cargo test
```

Check all solutions against instances:
```bash
./check_all.sh
```

## Validation Checks

The checker performs the following validations:

1. **Customer Coverage**: Every customer must be visited exactly once
2. **Capacity Constraint**: Total demand on each route ≤ vehicle capacity
3. **Valid Nodes**: All customer IDs must be valid (1 to DIMENSION)
4. **Cost Calculation**: Euclidean distances computed and rounded to nearest integer
5. **Cost Verification**: If a cost is claimed, it is compared with calculated cost

## Output

The checker outputs:
- Instance information (name, nodes, capacity)
- For each route:
  - Customer visits
  - Total load vs capacity
  - Route cost
  - Validation status (OK/INVALID)
- Total cost across all routes
- Final verdict: VALID or INVALID

## License

This file is part of QOBLIB - Quantum Optimization Benchmarking Library
Licensed under the Apache License, Version 2.0
