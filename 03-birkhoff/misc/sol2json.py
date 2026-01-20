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

#!/usr/bin/env python

import json
import re
import os
import sys

USAGE = "Usage: python sol2json.py <solution_dir> <output_dir>"

def get_perm_from_index(index, n):
    """Get the permutation associated with its index reading p{n}.dat files"""
    miscdir = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(miscdir, f"zimpl_p{n:02d}.dat")
    with open(filepath, 'r') as reader:
        for i, line in enumerate(reader):
            if i + 1 == index:
                perm = [ int(s) for s in line.strip().split(' ') ]
                return perm

def get_column_stacked_matrix(permuts, weights, n):
    """Compute and return the column-stacked matrix from the decomposition"""
    matrix = [ 0 for _ in range(n*n) ]
    for index, perm in permuts.items():
        for col, row in enumerate(perm):
            row -= 1
            matrix[n*col + row] += weights[index]
    return matrix

def read_solution_file(data_at_num, filepath):
    """Read solution file #num and write associated matrix info into data"""
    with open(filepath, 'r') as reader:
        n = data_at_num['n']
        # Store permutations and weights in temporary dictionaries
        permuts = {}
        weights = {}
        # Read solution file line by line
        for i, line in enumerate(reader):
            # Ignore empty lines and comments
            if len(line) == 0 or line[0] == '#':
                continue
            try:
                # Regex split line at '#' and ' ' (hash and space)
                string, index, value = re.split(r"#| ", line)
                index = int(index) # starts at 1
                value = int(value)
            except ValueError:
                print("Skipping invalid line. Expecting '<str>#<int> <int>'")
                continue
            # 'z' => value decides if permutation #index used (1) or not used (0)
            # 'x' => value = weight corresponding to permutation #index
            # Append permutation value
            if string[0] == 'z' and value == 1:
                permuts[index] = get_perm_from_index(index, n)
            # Append weight if it is nonzero
            if string[0] == 'x' and value != 0:
                weights[index] = value
        assert len(permuts) == len(weights)
        # Write weights and permutations into data
        for index, perm in permuts.items():
            data_at_num["weights"].append(weights[index])
            data_at_num["permutations"] += perm
        # Write objective value k
        data_at_num['k'] = len(data_at_num["weights"])
        # Write matrix and scale
        data_at_num["scale"] = sum(weights.values())
        data_at_num["scaled_doubly_stochastic_matrix"] = \
            get_column_stacked_matrix(permuts, weights, n)

def write_json(data, filepath):
    """Write dictionary data to JSON file"""
    json_obj = json.dumps(data, indent=4)
    with open(filepath, "w") as writer:
        writer.write(json_obj)

def validate_json(filepath):
    """Read and validate a JSON solution file"""
    print(f"Validating {filepath}...")
    with open(filepath) as f:
        data = json.load(f)
    #TODO if we think we need validation

def main():
    # Read user input
    if len(sys.argv) != 3:
        print(USAGE)
        sys.exit(1)
    solution_dir = sys.argv[1]
    output_dir = sys.argv[2]

    # Get matrix sizes n from directory name
    solution_dir_basename = os.path.split(os.path.normpath(solution_dir))[-1]
    print(solution_dir_basename)
    # Extract n from basename like "bhD-03" or "bhS-03"
    parts = solution_dir_basename.split('-')
    if len(parts) != 2 or parts[0] not in ['bhD', 'bhS']:
        print("Error: <solution_dir> must be path/to/bhD-<n> or path/to/bhS-<n>")
        sys.exit(1)
    n = parts[1]
    if not n.isdecimal():
        print("Error: <solution_dir> must be path/to/bhD-<n> or path/to/bhS-<n>")
        sys.exit(1)
    n = int(n)

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create dictionary
    data = dict()

    # Determine density value based on dense (D) or sparse (S)
    density = n**2 if parts[0] == 'bhD' else n

    # For each size n and density (dense or sparse), compile all respective
    # solutions in solution_dir into one JSON file in output_dir 
    for filename in os.listdir(solution_dir):
        # Extract filename info to check correct naming and extension
        root, ext1 = os.path.splitext(filename)
        root, ext2 = os.path.splitext(root)
        # Extract number of instance
        num = root.split('-')[-1] # num is str of a natural in interval [1, 100]
        # Catch invalid files
        if ext1 != ".sol" or not num.isdecimal():
            print(f"Skipping {filename}")
            continue
        # Check if optimal solution
        is_opt = True if ext2 == ".opt" else False
        # Create instance id in format B{n}_{density}_{num}
        instance_id = f"B{n}_{density}_{int(num)}"
        # Read solution #num into data
        data[num] = {
            "id": instance_id,
            "scaled_doubly_stochastic_matrix": [],
            "weights": [],
            "permutations": [],
            "optimal": is_opt,
            'n': n,
            'k': None,
        }
        print(f"Reading {filename}")
        filepath = os.path.join(solution_dir, filename)
        read_solution_file(data[num], filepath)

    # Sort instance solutions by number of instance
    data = dict(sorted(data.items()))
    # Write data to JSON file
    filepath = os.path.join(output_dir, f"qbench_{solution_dir_basename}.json")
    print(filepath)
    write_json(data, filepath)

if __name__ == "__main__":
    main()
