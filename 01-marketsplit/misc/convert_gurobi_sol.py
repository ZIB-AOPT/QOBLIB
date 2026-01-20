#!/usr/bin/env python3
"""
Convert Gurobi solution files to simple format.
Extracts x variables only and outputs their values as space-separated 0s and 1s.
"""

import sys
import re
from pathlib import Path


def convert_solution_file(input_file, output_file=None):
    """
    Convert a Gurobi solution file to simple format.
    
    Args:
        input_file: Path to input .sol file
        output_file: Path to output file (if None, prints to stdout)
    """
    x_vars = {}
    
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line.startswith('#') or not line:
                continue
            
            # Parse variable lines (e.g., "x#1 0" or "x#20 1")
            match = re.match(r'x#(\d+)\s+([01])', line)
            if match:
                var_num = int(match.group(1))
                value = match.group(2)
                x_vars[var_num] = value
    
    # Sort by variable number and create output
    sorted_vars = sorted(x_vars.items())
    values = [value for _, value in sorted_vars]
    output = ' '.join(values)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output + '\n')
    else:
        print(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_gurobi_sol.py <input.sol> [output.txt]")
        print("  If output file is not specified, prints to stdout")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    convert_solution_file(input_file, output_file)


if __name__ == '__main__':
    main()
