# Miscellaneous

This directory contains global utility scripts, tools, and binaries used across all problem classes in QOBLIB.

## Binaries

### ZIMPL

Mathematical programming modeling language used to create models and generate LP and QS files.

**Included versions:**
- `zimpl-3.7.1.linux.x86_64.gnu.static.opt`

**More information:** [zimpl.zib.de](https://zimpl.zib.de/)

## Submission and Validation Scripts

### check_submission.py

Validates that a submission matches QOBLIB contribution guidelines.

**Basic usage:**
```bash
python check_submission.py <path_to_submission>
```

**Full functionality:**
```bash
python check_submission.py -h
```

**Features:**
- Validates submission structure and format
- Checks solution correctness (with custom checker command)
- Verifies problem names in CSV files
- Auto-generates optional README files for problem directories

**Example (Independent Set):**
```bash
python check_submission.py \
    --generate-readme \
    --checker-cmd="{submission_root}/../../check/target/debug/check_stableset {submission_root}/../../instances/{instance}.gph {solution}" \
    --strict-problem-match \
    ../07-independentset/submissions/20250627_Quicopt_Bode/
```

This command validates structure, checks solutions, ensures correct problem naming, and generates the optional README.

## Metric Extraction

### get_metrics.py

Extracts metrics from archived model files across the project.

**Walk entire project:**
```bash
python get_metrics.py --parent_dir ../ --directory qs_files
```

Walks the project directory and extracts metrics from all `.tar.gz` archives named `qs_files`. Saves metrics in respective directories. Already generated metrics are skipped.

**Note:** Creates temporary directory in `/tmp`. If the script crashes, manually remove the temporary folder.

**Single archive:**
```bash
python get_metrics.py \
    --directory ../09-routing/models/integer_linear/lp_files.tar.gz \
    --output_csv metrics.csv
```

Extracts metrics from a single archive to specified CSV file.

## Format Conversion

### convert_lp2qubo.py

Converts linear program files to QUBO (Quadratic Unconstrained Binary Optimization) format.

**Usage:**
```bash
# Convert a single .lp.xz file
python convert_lp2qubo.py <path_to_file.lp.xz>

# Convert all .lp.xz files in a directory (recursively searches subdirectories)
python convert_lp2qubo.py <path_to_directory>
```

Converts `.lp.xz` files to compressed `.qs.xz` QUBO format files.

**Requirements:**
- Qiskit (for integer to binary variable conversion)
- All integer variables must be bounded

**Input:** `.lp.xz` compressed file(s)  
**Output:** `.qs.xz` compressed QUBO format files (placed in same directory as input files)

**Note:** When processing a directory, the script will recursively search all subdirectories for `.lp.xz` files and convert them individually, creating corresponding `.qs.xz` files alongside the originals.

### convert_info_to_md.py

Converts instance information files to Markdown format.

**Use case:** Generate documentation from instance metadata.

### convert_solution_to_active.py

Converts solution files to active variable format.

**Use case:** Extract only active (non-zero) variables from solutions for more compact representation.

## Documentation Utilities

### mdutils.py

Collection of helper functions for creating Markdown tables and documentation.

**Purpose:** Centralized utilities for generating consistent Markdown documentation across all problem classes.

**Usage:** Typically imported by scripts in `<problem_class>/misc/` directories to generate README files in `<problem_class>/solutions/`.

**Key functions:**
- Table formatting and generation
- Data structure conversion
- Markdown formatting helpers

## QUBO Processing

### simplify_qubo.py

Simplifies QUBO files to make them more suitable for quantum hardware execution.

**Main function:** `simplify_qubo_file`

**Process:**
1. Loads a `.qs` QUBO file
2. Simplifies according to maximum allowed SWAP gate layers
3. Creates new simplified QUBO file

**Parameters:** Based on SWAP network constraints for linear qubit topology.

**Reference:** Weidenfeller et al., Quantum 6, 870 (2022) for SWAP network details.

## Other Utilities

### add_licence.py

Adds license headers to source files.

**Use case:** Ensure all code files have proper Apache 2.0 license headers.

### rename_sol_files.sh

Batch renames solution files according to naming conventions.

**Use case:** Standardize solution file naming across the project.

### submission_template.csv

Template file for submission CSV format.

**Use case:** Reference for creating valid submission files.

## Generators Directory

### generators/

Contains instance generation utilities used across multiple problem classes.

**Use case:** Shared instance generation code and tools.
