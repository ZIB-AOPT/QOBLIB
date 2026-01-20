# Miscellaneous

This directory contains utility scripts for working with Latin squares and balanced scheduling (LABS) problem instances and solutions.

## Scripts

### convert_to_sol.py

Converts solution files from various formats to the standardized `.sol` format used in the solutions directory.

**Usage:**
```bash
python convert_to_sol.py <input_directory> <output_directory> <file_extension>
```

- `input_directory`: Directory containing the solution files to convert
- `output_directory`: Directory where converted `.sol` files will be saved
- `file_extension`: Extension of the input files (e.g., `.txt`, `.dat`)

**Requirements:**
- Input solution files must contain the sequence length information
- Files will be converted to the format specified in [../solutions/](../solutions/)

**Example:**
```bash
python convert_to_sol.py ./raw_solutions ./formatted_solutions .txt
```
