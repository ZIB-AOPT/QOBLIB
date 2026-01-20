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
import argparse

def is_gurobi_solution_format(input_file):
    """
    Check if the file is in Gurobi solution format.
    
    Expected format:
    - Comment lines starting with #
    - Variable lines: variable_name value
    
    Args:
        input_file (str): Path to the input file.
    
    Returns:
        bool: True if file appears to be in Gurobi solution format.
    """
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            return False
        
        # Check if first line is a comment (typical Gurobi format)
        has_header = False
        has_variable_lines = False
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Check for comment lines
            if line.startswith('#'):
                has_header = True
                continue
            
            # Check for variable lines (should have exactly 2 parts: name and value)
            parts = line.split()
            if len(parts) == 2:
                var_name, var_value = parts
                # Check if second part is a number
                try:
                    float(var_value)
                    has_variable_lines = True
                except ValueError:
                    return False
            else:
                # Invalid format
                return False
        
        # File should have at least variable lines
        return has_variable_lines
    
    except Exception as e:
        print(f"Error reading file {input_file}: {e}")
        return False

def convert_solution_to_active(input_file, output_file=None):
    """
    Convert a solution file to only include active variables (value = 1).
    
    Args:
        input_file (str): Path to the input solution file.
        output_file (str): Path to the output solution file. If None, will use input_file with .active.sol extension.
    """
    # Validate that the file is in Gurobi solution format
    if not is_gurobi_solution_format(input_file):
        print(f"Warning: {input_file} does not appear to be in Gurobi solution format. Skipping.")
        return False
    
    if output_file is None:
        # Create output filename by adding .active before .sol
        if input_file.endswith('.sol'):
            output_file = input_file[:-4] + '.active.sol'
        else:
            output_file = input_file + '.active'
    
    active_vars = []
    header_lines = []
    
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Keep comment lines (headers)
            if line.startswith('#'):
                header_lines.append(line)
                continue
            
            # Skip empty lines
            if not line:
                continue
            
            # Parse variable lines
            parts = line.split()
            if len(parts) == 2:
                var_name = parts[0]
                var_value = parts[1]
                
                # Only keep variables with value 1
                if var_value == '1' or var_value == '1.0':
                    active_vars.append(var_name)
    
    # Write output file
    with open(output_file, 'w') as f:
        # Write conversion notice
        f.write('# Converted from Gurobi solution format (active variables only)\n')
        
        # Write header
        for header in header_lines:
            f.write(header + '\n')
        
        # Write active variables (extract indices only)
        for var in active_vars:
            # Extract index from variable name (e.g., "x#7" -> "7")
            if '#' in var:
                index = var.split('#', 1)[1]
                f.write(index + '\n')
            else:
                # If no #, write the whole variable name
                f.write(var + '\n')
    
    print(f"Converted {input_file}")
    print(f"  Total active variables: {len(active_vars)}")
    print(f"  Output written to: {output_file}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert solution files to only include active variables (value = 1).")
    parser.add_argument("input", type=str, help="Path to the input solution file or directory")
    parser.add_argument("--output", type=str, default=None, help="Path to the output solution file (only for single file mode)")
    parser.add_argument("--recursive", action="store_true", help="Process all .sol files in directory recursively")
    args = parser.parse_args()
    
    if os.path.isfile(args.input):
        # Single file mode
        convert_solution_to_active(args.input, args.output)
    elif os.path.isdir(args.input):
        # Directory mode
        if args.recursive:
            # Recursive directory traversal
            for root, dirs, files in os.walk(args.input):
                for filename in files:
                    if filename.endswith('.sol') and not filename.endswith('.active.sol'):
                        input_path = os.path.join(root, filename)
                        convert_solution_to_active(input_path)
        else:
            # Single directory (non-recursive)
            for filename in os.listdir(args.input):
                if filename.endswith('.sol') and not filename.endswith('.active.sol'):
                    input_path = os.path.join(args.input, filename)
                    if os.path.isfile(input_path):
                        convert_solution_to_active(input_path)
    else:
        print(f"Error: {args.input} is not a valid file or directory")
        exit(1)
