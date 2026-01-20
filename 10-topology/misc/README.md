# Miscellaneous

This directory contains utility scripts for working with topology optimization instances and solutions.

## Scripts

### heuristic-random-graph.py

Python implementation of a heuristic algorithm based on generating random regular graphs for topology optimization problems.

**Usage:**
```bash
python heuristic-random-graph.py [options]
```

**Credits:** 
- Implementation by Robert Waniek
- Based on code by Ikki Fujiwara

**Use case:** Generate heuristic solutions or initial feasible solutions for topology optimization instances.

### convert_sol2gph_flow.py

Converts solution files from the flow-based MIP model format to `.gph` graph format.

**Usage:**
```bash
python3 convert_sol2gph_flow.py -f <filename>
```

- `<filename>`: Solution file (`.sol` format) from the [flow model](../models/flow_mip/)

**Output:** Creates a corresponding `.gph` file representing the solution graph.

### convert_sol2gph_seidel.py

Converts solution files from Seidel-based models to `.gph` graph format.

**Usage:**
```bash
python3 convert_sol2gph_seidel.py -f <filename>
```

- `<filename>`: Solution file (`.sol` format) from either [Seidel linear](../models/seidel_linear/) or [Seidel quadratic](../models/seidel_quadratic/) models

**Output:** Creates a corresponding `.gph` file representing the solution graph.

### convert_sol2gph.sh

Batch conversion script that converts all `.sol` files in a directory to `.gph` format using a specified conversion script.

**Usage:**
```bash
./convert_sol2gph.sh <problem_specific_python_script> <directory>
```

**Arguments:**
- `<problem_specific_python_script>`: Either `convert_sol2gph_flow.py` or `convert_sol2gph_seidel.py`
- `<directory>`: Directory containing `.sol` files to convert

**Example:**
```bash
./convert_sol2gph.sh convert_sol2gph_flow.py ../solutions/flow_solutions/
```

**Use case:** Batch process multiple solutions for faster benchmarking and validation.

### fix_indexing.py

Converts graph files with non-consecutive or non-one-starting vertex indices to a standardized format with consecutive indices starting from 1.

**Usage:**
```bash
python fix_indexing.py <input_file> <output_file>
```

- `<input_file>`: Edge list graph file with arbitrary vertex indices
- `<output_file>`: Output graph file with consecutive indices starting from 1

**Use case:** The solution checker assumes vertices are labeled from 1 to n consecutively. Use this script to standardize graph files before validation.