# QOBLIB Birkhoff Decomposition Solution Checker

This program is part of **QOBLIB - Quantum Optimization Benchmarking Library** and is designed to **verify solutions** to *Minimum Birkhoff Decomposition Problems*. It checks whether a given set of permutation matrices and weights correctly reconstruct the doubly stochastic matrix.

## Problem Description

The Birkhoff-von Neumann theorem states that any doubly stochastic matrix can be expressed as a convex combination of permutation matrices. The **Minimum Birkhoff Decomposition** problem asks for the minimal number of permutation matrices needed for this representation.

Given a doubly stochastic matrix $D \in \mathbb{R}^{n \times n}$, find:

$$
\underset{\lambda_i \in [0,1]}{\text{minimize}} \qquad  \sum_{i=1}^{n!} |\lambda_i|^0
$$

subject to:

$$
D = \sum_{i=1}^{k} \lambda_i P_i, \qquad  \sum_{i=1}^{k} \lambda_i = 1
$$

where $P_i$ are permutation matrices and $k$ is minimized.

## What This Checker Does

Given instance and solution files, this checker:

1. **Parses** JSON-formatted instance and solution files.
2. **Validates** each permutation matrix (ensures valid permutation of {1, ..., n}).
3. **Verifies** that weights are non-negative and sum to the scale factor (always exact).
4. **Reconstructs** the doubly stochastic matrix from the weighted permutation matrices.
5. **Measures** the reconstruction error as the normalised squared Frobenius norm.
6. **Accepts** the solution if the error is within the specified tolerance (default: 0, i.e. exact match).
7. **Reports** the number of permutation matrices used (k value) and the error metric.

This program does **not** check for optimality.

### Error metric

The reconstruction quality is measured by the **normalised squared Frobenius norm**:

$$\varepsilon = \frac{1}{n^2 \cdot \text{scale}^2} \sum_{i,j} \bigl(D_{ij} - \hat{D}_{ij}\bigr)^2$$

where $D$ is the target (scaled) matrix and $\hat{D}$ is the reconstruction.
This value is dimensionless and lies in $[0, 1]$ for any valid inputs.
An exact decomposition gives $\varepsilon = 0$.

## Input Format

### Instance File (JSON)

A JSON file containing one or more instances, each with:

- `id`: Instance identifier (e.g., "B3_9_5")
- `n`: Matrix dimension
- `scale`: Scaling factor (typically 1000 for integer arithmetic)
- `scaled_doubly_stochastic_matrix`: Flat array of $n^2$ integers representing the scaled doubly stochastic matrix (row-major order)
- `weights`: Array of integer weights (scaled)
- `permutations`: Array of integers representing permutation matrices

#### Example

```json
{
  "_license": "...",
  "001": {
    "id": "B3_9_1",
    "n": 3,
    "scale": 1000,
    "scaled_doubly_stochastic_matrix": [
      197, 275, 528,
      81, 723, 196,
      722, 2, 276
    ],
    "weights": [180, 127, 7, 315, 118],
    "permutations": [
      2, 1, 3,
      3, 1, 2,
      2, 1, 3,
      3, 2, 1,
      2, 1, 3
    ]
  }
}
```

**Permutation Encoding**: Each permutation of dimension $n$ is stored as $n$ consecutive integers. For example, for $n=3$, the array `[2, 1, 3, 3, 1, 2]` represents two permutations:
- First: $(2, 1, 3)$ meaning row 1→col 2, row 2→col 1, row 3→col 3
- Second: $(3, 1, 2)$ meaning row 1→col 3, row 2→col 1, row 3→col 2

### Solution File (JSON)

A JSON file with the same structure as the instance file, containing the proposed solutions. Each solution must have:

- `id`: Must match an instance ID
- `scaled_doubly_stochastic_matrix`: Should match the instance (for verification)
- `weights`: Array of weights (should sum to scale)
- `permutations`: Array encoding the permutation matrices

The checker verifies all solutions found in the solution file against matching instances.

#### Example

```json
{
  "001": {
    "id": "B3_9_1",
    "scaled_doubly_stochastic_matrix": [
      197, 275, 528,
      81, 723, 196,
      722, 2, 276
    ],
    "weights": [197, 79, 196, 526, 2],
    "permutations": [
      1, 2, 3,
      2, 1, 3,
      2, 3, 1,
      3, 2, 1,
      3, 1, 2
    ],
    "n": 3,
    "k": 5,
    "scale": 1000,
    "optimal": true
  }
}
```

## Usage

### Building

First, build the checker using Cargo:

```bash
cargo build --release
```

### Command

```bash
./target/release/check_birkhoff [--tolerance <t>] <instance-file> <solution-file>
```

### Arguments

* `--tolerance <t>`: Optional. Maximum allowed normalised squared Frobenius error (default: `0`, meaning an exact reconstruction is required). Use a small positive value such as `1e-6` to accept approximate solutions.
* `instance-file`: Path to the JSON file containing instance data
* `solution-file`: Path to the JSON file containing solution data

### Examples

Check a single instance set (exact match):

```bash
./target/release/check_birkhoff ../instances/qbench_03_dense.json ../solutions/qbench_03_dense.json
```

Check with a tolerance for approximate solutions:

```bash
./target/release/check_birkhoff --tolerance 1e-6 ../instances/qbench_03_dense.json solution.json
```

Check all solutions:

```bash
./check_all.sh
```

## Output

The checker produces output like:

```
QOBLIB Birkhoff Decomposition Solution Checker Version 1.0
Checking 50 solutions against 50 instances
  Instance B3_9_1: k=5, valid
  Instance B3_9_2: k=4, valid
  ...

VALID: All 50 instances verified successfully
```

For each solution, the checker reports:
- **Instance ID**
- **k value**: Number of permutation matrices used
- **Validity status**: Whether the decomposition correctly reconstructs the matrix

### Validation Checks

1. **Permutation validity**: Each permutation must contain each number from 1 to n exactly once
2. **Weight sum**: All weights must sum exactly to the scale factor (always enforced, regardless of `--tolerance`)
3. **Matrix reconstruction**: The normalised squared Frobenius error between the reconstruction and the target must not exceed the tolerance (0 by default → exact match required)

## Exit Codes

- **0** (`VALID`): All solutions pass verification
- **21** (`INFEASIBLE`): One or more solutions fail verification (weight sum wrong, invalid permutation, or error exceeds tolerance)
- **10** (`INVALID_FILE`): Solution file cannot be parsed
- **2** (`USAGE`): Bad arguments or unreadable instance file

## Notes

- The checker uses integer arithmetic with a scale factor (typically 1000) for reconstruction; the Frobenius error is computed in floating-point from those integers
- Instance files may contain multiple instances; the checker matches solutions by ID
- Missing solutions for some instances is acceptable; the checker only validates provided solutions
- The `optimal` field in solutions is informational only and not verified by the checker
- The weight-sum check is always enforced exactly; only the matrix-reconstruction comparison is softened by `--tolerance`

## License

Part of **QOBLIB**, released under [**Apache 2.0**](http://www.apache.org/licenses/LICENSE-2.0).

## Author

**Maximilian Schicker**
© 2026
