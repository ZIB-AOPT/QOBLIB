# This file is part of QOBLIB - Quantum Optimization Benchmarking Library
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import csv
import re
import argparse
from pyscipopt import Model
import shutil
import lzma

def parse_lp(lp_file_path):
    """
    Parse an LP file using PySCIPOpt, extracting:
      - Number of variables (split by binary, integer, continuous).
      - Number of constraints (split by linear, quadratic).
      - A simplistic 'density' measure of the constraint matrix.
      - Minimum and maximum coefficients observed.

    Returns:
        dict: {
            'file': str,
            'num_binary_vars': int,
            'num_integer_vars': int,
            'num_continuous_vars': int,
            'num_linear_constraints': int,
            'num_quadratic_constraints': int,
            'density': float,
            'min_coeff': float or None,
            'max_coeff': float or None
        }
    """

    # 1) Create and read the model
    model = Model()
    model.readProblem(lp_file_path)

    # 2) Count variables by type
    num_binary_vars = model.getNBinVars()
    num_integer_vars = model.getNIntVars()
    num_continuous_vars = model.getNContVars()

    # 3) Count constraints by type & gather coefficient info
    num_linear_constraints = 0
    num_quadratic_constraints = 0
    nonzero_count = 0
    min_coeff = None
    max_coeff = None

    constraints = model.getConss()
    for cons in constraints:
        # Must be 'getConshdlrName()' as requested
        ctype = cons.getConshdlrName()

        if cons.isLinear():
            num_linear_constraints += 1

            # Get dictionary of Constraint variables and coefficients
            cons_dict = model.getValsLinear(cons)
            
            # We only need the coefs here, but we unpack everything to avoid the ValueError
            for coeff in cons_dict.values():
                # Update min, max
                if min_coeff is None or coeff < min_coeff:
                    min_coeff = coeff
                if max_coeff is None or coeff > max_coeff:
                    max_coeff = coeff

                if coeff != 0.0:
                    nonzero_count += 1

        elif model.checkQuadraticNonlinear(cons):
            num_quadratic_constraints += 1

            # Get the terms of the quadratic constraint
            bilin_terms, quad_terms, lin_terms = model.getTermsQuadratic(cons)
            
            # 1) Linear part
            for (var1, coeff) in lin_terms:
                if min_coeff is None or coeff < min_coeff:
                    min_coeff = coeff
                if max_coeff is None or coeff > max_coeff:
                    max_coeff = coeff
                if coeff != 0.0:
                    nonzero_count += 1

            # 2) Bilinear part
            for (var1, var2, coeff) in bilin_terms:
                if min_coeff is None or coeff < min_coeff:
                    min_coeff = coeff
                if max_coeff is None or coeff > max_coeff:
                    max_coeff = coeff
                if coeff != 0.0:
                    nonzero_count += 1

            # 3) Quadratic part
            for (var1, coeff, _) in quad_terms:
                if min_coeff is None or coeff < min_coeff:
                    min_coeff = coeff
                if max_coeff is None or coeff > max_coeff:
                    max_coeff = coeff
                if coeff != 0.0:
                    nonzero_count += 1

        else:
            # Skip or handle other constraint types (indicator, SOS, etc.)
            print(f"Unknown constraint type: {ctype}")

            print(cons)

            pass

    # 4) Compute a "density" measure
    total_vars = model.getNVars()
    total_constraints = num_linear_constraints + num_quadratic_constraints

    total_possible = total_vars * num_linear_constraints + total_vars * (total_vars + 3) / 2 * num_quadratic_constraints

    density = 0.0
    if total_possible > 0:
        density = nonzero_count / total_possible

    return {
        'file': os.path.basename(lp_file_path),
        'num_binary_vars': num_binary_vars,
        'num_integer_vars': num_integer_vars,
        'num_continuous_vars': num_continuous_vars,
        'num_vars': total_vars,
        'num_linear_constraints': num_linear_constraints,
        'num_quadratic_constraints': num_quadratic_constraints,
        'num_constraints': total_constraints,
        'density': density,
        'min_coeff': min_coeff,
        'max_coeff': max_coeff
    }

def parse_qs(qs_file_path):
    """
    Parse a QS (QUBO) file to extract:
      - The number of variables.
      - The QUBO matrix density (ratio of nonzero entries to total entries).
      - Minimum and maximum coefficients observed.
    
    Returns:
        dict: {
          'file': str,
          'num_variables': int,
          'density': float,
          'min_coeff': float or None,
          'max_coeff': float or None
        }
    """
    num_vars = 0
    nonzero_entries = 0
    min_coeff = None
    max_coeff = None

    with open(qs_file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if not line.lower().startswith("#"):
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    num_vars = int(parts[0])
                    break
                except ValueError:
                    pass

    print(f"Found {num_vars} variables in {qs_file_path}")

    for line in lines:
        if line.lower().startswith("#"):
            continue

        parts = line.split()

        if len(parts) == 3:
            try:
                i = int(parts[0])
                j = int(parts[1])
                val = float(parts[2])

                if min_coeff is None or val < min_coeff:
                    min_coeff = val
                if max_coeff is None or val > max_coeff:
                    max_coeff = val
                if val != 0:
                    # Count off-diagonal entries twice
                    nonzero_entries += 1

            except ValueError:
                pass

    total_entries = num_vars * (num_vars + 1) / 2
    density = 0.0
    if total_entries > 0:
        density = nonzero_entries / total_entries

    return {
        'file': os.path.basename(qs_file_path),
        'num_variables': num_vars,
        'density': density,
        'min_coeff': min_coeff,
        'max_coeff': max_coeff
    }

def generate_readme(rows, output_dir, base_dir, csv_filename):
    """
    Generate a README.md file with a markdown table containing the metrics.
    The first column (file) will be a link to the actual file.
    
    Args:
        rows (list): List of dictionaries containing the parsed data.
        output_dir (str): Directory where the README.md will be written.
        base_dir (str): Base directory containing the actual instance files.
        csv_filename (str): Name of the CSV file (for linking in the README).
    """
    readme_path = os.path.join(output_dir, 'README.md')
    
    if not rows:
        return
    
    all_keys = list(rows[0].keys())
    
    with open(readme_path, 'w') as f:
        f.write('# Instance Metrics\n\n')
        f.write(f'The metrics are also available in CSV format: [{csv_filename}]({csv_filename})\n\n')
        
        # Write table header
        f.write('| ' + ' | '.join(all_keys) + ' |\n')
        f.write('| ' + ' | '.join(['---'] * len(all_keys)) + ' |\n')
        
        # Write table rows
        for row in rows:
            row_values = []
            for key in all_keys:
                value = row.get(key, '')
                
                # For the 'file' column, create a link
                if key == 'file':
                    filename = str(value)
                    # Find the actual file path (could be .xz compressed or uncompressed)
                    file_found = False
                    
                    # Search for the file in the base directory
                    for root, dirs, files in os.walk(base_dir):
                        # Try different extensions in order of preference
                        for ext in ['.xz', '']:
                            # Try both .lp and .qs extensions
                            for base_ext in ['.lp', '.qs']:
                                # Check if filename already has the base extension
                                if filename.endswith(base_ext):
                                    search_name = filename + ext
                                else:
                                    search_name = filename + base_ext + ext
                                
                                if search_name in files:
                                    full_path = os.path.join(root, search_name)
                                    # Create relative path from output_dir to the file
                                    rel_path = os.path.relpath(full_path, output_dir)
                                    # Ensure forward slashes for GitHub compatibility
                                    rel_path = rel_path.replace('\\', '/')
                                    value = f'[{filename}]({rel_path})'
                                    file_found = True
                                    break
                                
                                if file_found:
                                    break
                        if file_found:
                            break
                    
                    if not file_found:
                        # If file not found, just use the filename without link
                        value = filename
                
                # Format the value
                if isinstance(value, float):
                    value = f'{value:.6f}'
                else:
                    value = str(value)
                
                row_values.append(value)
            
            f.write('| ' + ' | '.join(row_values) + ' |\n')
    
    print(f"README.md written to {readme_path}")

def parse_directory(directory_path, output_csv_path):
    """
    Goes through all .lp or .qs files in `directory_path`, parses them using
    parse_lp() or parse_qs(), then writes a CSV with the collected data.
    Also generates a README.md file with the same information in a table.
    
    Args:
        directory_path (str): Path to directory containing LP and QS files (may have substructures).
        output_csv_path (str): Path to the output CSV file.
    """
    print(f"Parsing files in {directory_path} and writing results to {output_csv_path}")

    rows = []

    for root, dirs, files in os.walk(directory_path):
        for filename in sorted(files):
            filepath = os.path.join(root, filename)
            if os.path.isfile(filepath):
                if filename.lower().endswith('.lp.xz') or filename.lower().endswith('.qs.xz'):
                    tmp_path = filepath[:-3]  # remove .xz
                    with lzma.open(filepath, 'rb') as f_in, open(tmp_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                    if tmp_path.lower().endswith('.lp'):
                        data = parse_lp(tmp_path)
                        rows.append(data)
                    elif tmp_path.lower().endswith('.qs'):
                        data = parse_qs(tmp_path)
                        rows.append(data)
                    os.remove(tmp_path)
                else:
                    if filename.lower().endswith('.lp'):
                        data = parse_lp(filepath)
                        rows.append(data)
                    elif filename.lower().endswith('.qs'):
                        data = parse_qs(filepath)
                        rows.append(data)

    if not rows:
        print("No files found to parse.")
        return

    all_keys = rows[0].keys()

    with open(output_csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=all_keys)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    
    # Generate README.md in the same directory as the CSV
    output_dir = os.path.dirname(output_csv_path)
    csv_filename = os.path.basename(output_csv_path)
    generate_readme(rows, output_dir, directory_path, csv_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse .lp and .qs files and output results to a CSV and README.md.")
    parser.add_argument("--directory", type=str, help="Path to the directory containing .lp and .qs files (may be .xz compressed)")
    parser.add_argument("--output_csv", type=str, default=None, help="Path to the output CSV file (default: metrics.csv in the directory)")
    parser.add_argument("--parent_dir", type=str, default=None,
                        help="If provided, recursively search subdirectories for the specified directory and parse each one, writing the CSV and README in the same directory.")
    args = parser.parse_args()

    

    if args.parent_dir:
        if not args.directory:
            print("Error: --directory argument is required when using --parent_dir.")
            print("Usage: python get_metrics.py --parent_dir <parent_directory> --directory <directory_name>")
            exit(1)

        directory_name = args.directory

        for root, dirs, files in os.walk(args.parent_dir):
            if directory_name in dirs:
                dir_path = os.path.join(root, directory_name)
                out_csv_path = os.path.join(dir_path, "metrics.csv")
                readme_path = os.path.join(dir_path, "README.md")
                # skip if the output files already exist
                if os.path.exists(out_csv_path) and os.path.exists(readme_path):
                    print(f"Skipping {dir_path}, output files already exist.")
                    continue
                parse_directory(dir_path, out_csv_path)
                print(f"Parsed {dir_path}, results written to {out_csv_path}")
    else:
        if not args.directory:
            print("Error: --directory argument is required.")
            print("Usage: python get_metrics.py --directory <path> [--output_csv <output_path>]")
            print("   or: python get_metrics.py --parent_dir <parent_path> --directory <directory_name>")
            exit(1)
        
        # Default output CSV path if not provided
        if not args.output_csv:
            args.output_csv = os.path.join(args.directory, "metrics.csv")
        
        parse_directory(args.directory, args.output_csv)
        print(f"Results written to {args.output_csv}")
