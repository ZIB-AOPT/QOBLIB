# QOBLIB Market Split Problem Solution Checker

This program is part of **QOBLIB - Quantum Optimization Benchmarking Library** and is designed to **verify solutions** to *Market Split Problems*. It checks whether a given binary solution satisfies the required balanced constraints across multiple partitions.

## Problem Description

Given a matrix $A \in \mathbb{N}^{m,n}$ and a RHS $b \in \mathbb{N}^m$, find a feasible vector $x \in \{0,1\}^{n}$ that fulfills 

$$
    Ax = b.
$$

Each row represents its own subset sum problem. 
Thus, this is referred to as multi-dimensional subset sum.

## What This Checker Does

This checker verifies a solution against a market split instance file by:

1. **Parsing** the instance file (matrix of weights with RHS constraints).
2. **Reading** a solution file or binary string.
3. **Evaluating** each constraint:
   - Computes total weight.
   - Computes weight of selected variables.
   - Checks if selection matches the expected RHS (half the total).
4. **Reporting** if the solution satisfies all constraints.

## Input Format

### Instance File

- First non-comment line:  
```
<number_of_constraints> <number_of_variables>
```
- Each following line:  
```
<w1> <w2> ... <wn> <rhs>
```
where `w1..wn` are variable weights and `rhs` is the expected half-sum.

- Comments can start with `#` and commas are also supported as delimiters.

#### Example
```
# 3 constraints, 20 variables

3 20
20 96 46 43 38 64 83 39 20 31 99 53 91 7 30 72 26 81 78 539
45 32 8 58 94 53 14 33 69 93 17 95 87 74 43 26 12 31 36 5 462
29 36 3 34 47 96 11 28 8 38 78 28 37 13 0 21 91 58 93 15 382
```


## Solution Formats

This checker supports **multiple formats**:

### 1. Binary String (compact or spaced)
```
01010100111101111101
```
Or
```
0 1 0 1 0 1 0 0 1 ...
```
Or
```
0,1,0,1,0,...
```

### 2. Variable Index Format
Each line lists a variable number (1-based) indicating it is set to 1:
```
1
4
5
...
```

### 3. Named Variable Format (e.g., from MIP solvers)
```
x#1 1
x#2 0
x#3 1
...
````

Lines that don't start with `x` are ignored. 
Missing indices are treated as `0`.

## Usage

### Building

First, build the checker using Cargo:

```bash
cargo build --release
```

### Command

```bash
./target/release/check_marketsplit <instance-file> <solution-file-or-01-string>
```

### Arguments:

* `instance-file`: Path to the text file describing the instance matrix.
* `solution-file-or-01-string`: Either a path to the solution file or a direct binary string.

### Examples

Using a binary string:

```bash
./target/release/check_marketsplit instance.txt 01010100111101111101
```

Using a solution file:

```bash
./target/release/check_marketsplit instance.txt solution.txt
```

## Output

The checker prints the number of variables and the status of each constraint:

```
Problem has 20 variables.
Constraint 1 ok
Constraint 2 ok
Constraint 3 ok
Solution successfully verified
```

If any constraint fails:

```
Constraint 2 failed: expected 462 got 451
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
