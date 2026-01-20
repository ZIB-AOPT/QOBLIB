# Miscellaneous

This directory contains utility scripts for generating and working with Steiner tree problem instances and solutions.

## Scripts

### generate_feasible_instance.py

Generates feasible Steiner tree packing instances on a multi-layer grid with configurable parameters.

**Prerequisites:**
- **ZIMPL**: Modeling language for mathematical programming ([SCIP Optimization Suite](https://www.scipopt.org/#download))
- **CPLEX**: IBM optimization solver ([IBM CPLEX](https://www.ibm.com/products/ilog-cplex-optimization-studio))
- **Python packages**: `numpy` (install via `pip install numpy`)

**Usage:**
```bash
python3 generate_feasible_instance.py <size> <num_layers> <max_terminals> [options]
```

**Arguments:**

| Argument            | Description                                                          | Default  |
| ------------------- | -------------------------------------------------------------------- | -------- |
| `size`              | Grid size (for size=n, creates n×n grid)                             | Required |
| `num_layers`        | Number of stacked grid layers                                        | Required |
| `max_terminals`     | Max terminals per net (reduced iteratively until feasible)           | Required |
| `--num_holes`       | Number of random holes in the grid                                   | `0`      |
| `--randseed`        | Random seed for reproducibility                                      | `12345`  |
| `--zimpl_path`      | Path to ZIMPL executable                                             | `zimpl`  |
| `--cplex_path`      | Path to CPLEX executable                                             | `cplex`  |
| `--force_diff_side` | Force second terminal of each net to be on different side from first | `False`  |

**Example:**
```bash
python3 generate_feasible_instance.py 10 3 5 \
    --num_holes 2 \
    --randseed 123 \
    --zimpl_path /path/to/zimpl \
    --cplex_path '/user/CPLEX_Studio2211/cplex/bin/x86-64_linux/cplex'
```

**Output files:**
- `arcs.dat`: Graph arcs
- `terms.dat`: Terminal nodes for each net
- `roots.dat`: Root node for each net
- `param.dat`: Final number of nodes and nets
- `partial_sol.txt`: Feasible Steiner tree packing (not necessarily optimal)

### get_instance_info.py

Generates summary tables of all instances with best known solution information.

**Usage:**
```bash
python get_instance_info.py
```

**Output:** Creates `.csv` and `.md` table files with instance information and best solutions.

### convert_sol2arcs.py

Converts Gurobi solution files to arc-based solution format.

**Usage:**
```bash
python convert_sol2arcs.py <input_file> <output_file> <arcs_file>
```

- `input_file`: Gurobi solution file
- `output_file`: Output arc solution file
- `arcs_file`: Instance arc file (needed to compute solution value)

**Note:** This script recomputes the solution value based on the arc information.
