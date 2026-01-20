# QOBLIB LABS (Low Autocorrelation Binary Sequence) Solution Checker

This program is part of **QOBLIB - Quantum Optimization Benchmarking Library** and is used to **evaluate and verify solutions** for the *Low Autocorrelation Binary Sequence (LABS)* problem.

It computes the energy of a given binary sequence and checks whether the solution is known to be optimal (for small instances).

## Problem Description

Given a sequence $\mathcal{S} = \{s_1, ..., s_n\}$ of spins $s_i \in \{-1,1\}, i \in [n]$, we define the autocorrelations of a sequence as

$$
    C_k(\mathcal{S}) \coloneqq \sum_{i = 1}^{n-k} s_i s_{i+k}
$$

and the energy of a sequence as

$$
    E(\mathcal{S}) \coloneqq \sum_{i \in [k]} C_k^2(\mathcal{S}).
$$

The goal is to find the sequence of minimum energy given its length $n$.

## What This Checker Does

Given a binary solution and a sequence length `k`, this checker:

1. Parses the solution in various formats.
2. Converts it to a ±1 vector.
3. Computes the energy of the sequence.
4. Prints a compact run-length encoding (LL code) of the sequence.
5. Compares energy to known optimal values (for small `k`).

This program does **not** check for optimality.

## Input Format

### Solution Formats

The checker automatically detects these formats:

#### 1. Binary Sequence (0s and 1s)

```
010011001101...
```

Or with separators:

```
0,1,0,0,1,1,...
```

#### 2. Index Format

Each line contains a variable index (1-based) to be interpreted as 0 (i.e., -1):

```
3
7
9
...
```

All others are assumed to be 1 (i.e., +1).

#### 3. Named Variable Format (as in MIP solvers)

```
x#1 1
x#2 0
x#3 1
...
```

Lines not starting with `x#` are ignored.

## Usage

### Building

First, build the checker using Cargo:

```bash
cargo build --release
```

### Command

```bash
./target/release/check_labs <k> <solution-file | 01-string | LL-string>
```

### Arguments

* `k`: Length of the binary sequence.
* `solution`: Can be a file or an inline string.

### Examples

From a file:

```bash
./target/release/check_labs 32 my_solution.txt
```

### From Inline Binary String

```bash
./target/release/check_labs 32 01010100101101111101
```

## Output

The output looks like:

```
QOBLIB LABS Solution Checker Version 1.0
LABS k=32 E(S)=64 seq=71112111133221221 optimal
```

Where:

* `E(S)` is the computed energy.
* `seq` is a compact run-length code.
* `optimal` indicates a known best solution (for small k).
* `failure` indicates suboptimal energy.

If the instance is too large to verify against known values:

```
LABS k=55 E(S)=321 seq=6c3b4b4d4b4d4b5 too big to check
```

## Exit Codes

- **0**: Solution is valid
- **1**: Solution fails validation
- **2**: Error (e.g., file not found, parsing error)

## License

Part of **QOBLIB**, released under [**Apache 2.0**](http://www.apache.org/licenses/LICENSE-2.0).

## Author

**Thorsten Koch**
© 2025
