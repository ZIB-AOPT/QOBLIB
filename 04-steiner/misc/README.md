# Steiner Tree Instance Generator

This script generates feasible instances for the Steiner tree problem on a grid. The grid can have multiple layers, random holes, and multiple terminals per net. The script uses ZIMPL and CPLEX for solving the instances. There are two versions of the script; the one called 'hard' makes additional effort to try to generate instances that cannot be solved by a simple decomposition heuristic, although this comes at the cost of additional computational effort and higher chance of failure. Nonetheless, the instances are not guaranteed to be difficult on the primal side.

## Prerequisites

Before using this script, ensure the following tools and packages are installed:

### Tools
1. **ZIMPL**: A modeling language for mathematical programming.
   - ZIMPL is included in and can be downloaded from the [SCIP Optimization Suite](https://www.scipopt.org/#download).
2. **CPLEX**: An optimization solver by IBM.
   - Obtain from [IBM CPLEX official site](https://www.ibm.com/products/ilog-cplex-optimization-studio).

### Python Packages
Install the required Python packages using `pip`:

```bash
pip install numpy
```

## Usage

### Command-Line Arguments

| Argument            | Description                                                                           | Default Value |
| ------------------- | ------------------------------------------------------------------------------------- | ------------- |
| `size`              | Grid size. For size=n, the final grid will be of size n*n.                            |               |
| `num_layers`        | Number of stacked grid layers.                                                        |               |
| `max_terminals`     | Maximum number of terminals per net, iteratively reduced until feasible net is found. |               |
| `--num_holes`       | Number of random holes to generate.                                                   | `0`           |
| `--randseed`        | Random seed for reproducibility.                                                      | `12345`       |
| `--zimpl_path`      | Path to the ZIMPL executable.                                                         | `zimpl`       |
| `--cplex_path`      | Path to the CPLEX executable.                                                         | `cplex`       |
| `--force_diff_side` | Force the second terminal of each net to be on a different side from the first        | `False`       |

### Example Usage

```bash
python3 generate_feasible_instance.py \
    10 \
    3 \
    5 \
    --num_holes 2 \
    --randsee 123 \
    --zimpl_path /path/to/zimpl \
    --cplex_path '/user/CPLEX_Studio2211/cplex/bin/x86-64_linux/cplex'
```

```bash
python3 generate_hard_feasible_instance.py \
    10 \
    3 \
    5 \
    --num_holes 2 \
    --randsee 123 \
    --zimpl_path /path/to/zimpl \
    --cplex_path '/user/CPLEX_Studio2211/cplex/bin/x86-64_linux/cplex'
```


### Output Files

The script generates several files that describes the final feasible steiner tree packing instance: 
- `arcs.dat`: Contains arcs of the final graph.
- `terms.dat`: Specifies terminal nodes for each net.
- `roots.dat`: Specifies the root node for each net.
- `param.dat`: Give the final number of nodes and nets generated.
- `partial_sol.txt`: Arcs in a feasible steiner tree packing constructed during generation; not necessarily optimal

## Getting Instance Info

Run

```bash
python get_instance_info.py
```

to generate a `.csv` and a `.md` table containing all the infromation on the provided instances with the best solutions.

## Converting Gurobi to Arc sol

Run

```bash
python convert_sol2arcs.py <input_file> <output_file> <arcs_file>
```

to convert the (Gurobi) solution `input_file` to an arc solution written to `output_file` where `arcs_file` has to be provided to (re)compute the value of the solution.
