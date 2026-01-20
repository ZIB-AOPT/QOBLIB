# Miscellaneous

This directory contains utility scripts for validating and checking independent set (stable set) problem graph instances.

## Scripts

### validate_graph.py

Validates that a graph file conforms to the correct `.gph` format specification. Can also automatically fix and write a correctly formatted file.

**Usage:**
```bash
python validate_graph.py <graph_file>
```

- `graph_file`: Path to the `.gph` graph file to validate

**Features:**
- Checks graph file format compliance
- Reports format errors with detailed messages
- Option to write corrected file if format issues are detected

**Interactive:** If the graph is incorrectly formatted, the script will prompt whether to write a corrected version.

### check_all.sh

Batch validation script that checks the format of all `.gph` files in the instance directory.

**Usage:**
```bash
./check_all.sh
```

**What it does:**
- Scans [../instances/](../instances/) directory
- Validates each `.gph` file
- Reports any format violations
- Provides summary of validation results

**Use case:** Verify all instances are properly formatted before submitting or using them in experiments.
