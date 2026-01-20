# Market Split Generator

This repository provides a tool for generating feasible, random market share problem instances of arbitrary size. These instances are particularly useful for benchmarking solvers and evaluating their performance.

## Problem Definition

Given a matrix $A = [a_{ij}] \in \mathbb{N}^{m \times n}$ and a right-hand side $b = [b_i] \in \mathbb{N}^m$, determine whether there exists a solution vector $x \in \{0, 1\}^n$ such that:

$Ax = b$

This problem becomes challenging when the entries of $b$ are set as:

$b_i = \left\lfloor \frac{\sum_{j \in [n]} a_{ij}}{2} \right\rfloor$

Here, $b_i$ is computed as half the sum of the entries in the corresponding row of $A$, rounded down.

## Generating Instances

To benchmark solvers, it is essential to generate feasible instances of this problem. A naive approach is to randomly sample the entries of $A$ from a uniform distribution and compute $b$ accordingly. However, this approach often results in infeasible instances, which are less useful for benchmarking.

This repository provides an improved method to generate feasible instances by constructing them as follows:

### Procedure to Generate Feasible Instances

1. **Generate a Random Solution Vector**:  
   Create a random solution vector $x$ where approximately half (±2) of the entries are set to $1$, and the rest are set to $0$.

2. **Generate Matrix $A$**:  
   Sample the entries of $A$ uniformly from a specified range.

3. **Compute the Right-Hand Side $b$**:  
   Compute each entry of $b$ as:
   $b_i = \left\lfloor \frac{\sum_{j \in [n]} a_{ij}}{2} \right\rfloor$

4. **Adjust for Feasibility**:  
   Ensure feasibility of the generated instance using the following steps for each row:
   
   - **Step 1**: Repeat until no more improvement is possible:
     - Identify a pair of entries in the row where one corresponds to $0$ in $x$ and the other to $1$.
     - Perform a "switch" that reduces the absolute slack of the row as much as possible.

   - **Step 2**: If the row is still not feasible:
     - Calculate the slack $s$ for the row.
     - Set $c = \frac{3 \cdot \text{numones}}{2}$, where `num_ones` is the number of $1$'s in the row.
     - Find $c$ pairs of $0$ and $1$, and adjust the corresponding entries by adding $\frac{s}{c}$ to the $1$'s and subtracting it from the $0$'s.

   - **Step 3**: Repeat this adjustment until the row becomes feasible.

In most cases, only a few switches and adjustments are sufficient to achieve feasibility.

## Why Use This Method?

This method ensures that the generated instances:
- Are guaranteed to be feasible.
- Provide a diverse range of problems for benchmarking.
- Avoid the high infeasibility rates of naive random generation methods.

## Usage

Clone this repository and follow the instructions in the codebase to generate instances. Adjust the parameters for matrix size, value ranges, and solution vector generation as needed to fit your benchmarking needs.

## Contributing

Contributions to improve the code or add new features are welcome! Please feel free to submit a pull request or open an issue.

---

Happy benchmarking!
