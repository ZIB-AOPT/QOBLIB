# Miscellaneous

This directory contains utility scripts for generating market split instances and converting between file formats.

## Scripts

### gen_instances.sh

Automatically generates market split instances with varying parameters and saves them to the appropriate folders.

**Usage:**
```bash
./gen_instances.sh
```

This script will generate multiple `.dat` files covering a range of instance sizes and parameters.

### gen_marketshare.cpp

C++ program to generate random market share instances with a specified seed.

**Usage:**
```bash
g++ gen_marketshare.cpp -o gen_marketshare
./gen_marketshare <m> <D> <seed>
```

- `m`: Number of markets
- `D`: Density parameter
- `seed`: Random seed for reproducibility

**Output:** Generates instance data in `.dat` format.

### convert_dat2csv.py

Converts instance files from `.dat` format to the standardized market split `.csv` format.

**Usage:**
```bash
python convert_dat2csv.py <input_file_path>
```

Refer to [../README.md](../README.md) for details on the `.csv` format specification.

### convert_dat2txt.awk

AWK script to convert `.dat` files to `.txt` files. This conversion is required for ZIMPL to process the instance data.

**Usage:**
```bash
awk -f convert_dat2txt.awk <input_file_path> > <output_file_path>
```

**Example:**
```bash
awk -f convert_dat2txt.awk instance.dat > instance.txt
```

### sol2mdtable.py

Generates Markdown documentation containing a table summarizing solutions.

**Usage:**
```bash
python sol2mdtable.py <outfile>
```

- `outfile`: Path where the resulting Markdown document will be written

**Note:** This script was used to create [../solutions/README.md](../solutions/README.md).

### convert_gurobi_sol.py

Converts Gurobi solution files (`.opt.sol`) from their original format to a simplified format containing only the x variable values as space-separated 0s and 1s in a single line. The s variables are filtered out, and x variables are sorted numerically.

**Usage:**
```bash
# Print to stdout
python ../../misc/convert_gurobi_sol.py <input.sol>

# Save to file
python ../../misc/convert_gurobi_sol.py <input.sol> <output.txt>
```

**Example:**
```bash
python ../../misc/convert_gurobi_sol.py ../solutions/ms_03_050_002.opt.sol ../solutions/ms_03_050_002.txt
```

**Input format (Gurobi):**
```
# Solution for model obj
# Objective value = 0
s#1 0
x#1 1
x#2 0
```

**Output format:**
```
1 0 1 1 0
```

## Directory

### marketsplit_gen/

Contains additional tools and utilities related to market split instance generation.

## Notes

The workflow for creating LP files from instances is:
1. Generate instances using `gen_marketshare.cpp` or `gen_instances.sh` → creates `.dat` files
2. Convert to text format using `convert_dat2txt.awk` → creates `.txt` files
3. Generate LP models using `convert_txt2lp.sh` → creates `.lp` files

