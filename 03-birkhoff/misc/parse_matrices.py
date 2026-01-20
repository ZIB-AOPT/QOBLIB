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

import json
import numpy as np
import sys
import os


def read_matrix_from_json(data, matrix_id, n):
    """Read matrix from JSON data and reshape it to (n, n)"""
    matrix = data[matrix_id]["scaled_doubly_stochastic_matrix"]
    matrix = np.array(matrix)
    matrix = np.reshape(matrix, (n, n))
    return matrix


def write_sparse_matrix_to_file(matrix, output_file):
    """Write the matrix in sparse format to the output file"""
    with open(output_file, "w") as f:
        # Write matrix dimensions and number of nonzero entries
        # nonzero_entries = np.count_nonzero(matrix)
        # f.write(f"{matrix.shape[0]} {nonzero_entries}\n")

        # Write each non-zero entry in the format: row index, column index, value
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                f.write(f"{i + 1} {j + 1} {matrix[i, j]}\n")


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python parse_matrices.py <json_file> <matrix_dimension> <output_directory>"
        )
        sys.exit(1)

    json_file = sys.argv[1]
    n = int(sys.argv[2])
    output_dir = sys.argv[3]

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(json_file, "r") as f:
        data = json.load(f)

    if "dense" in json_file:
        instance_type = "D"
    else:
        instance_type = "S"

    print(f"Parsing matrices from {json_file}")

    # Process each matrix ID from "1" to "100"
    for matrix_id in range(10):
        str_id = str(matrix_id + 1)
        if str_id in data:
            matrix = read_matrix_from_json(data, str_id, n)
            output_file = os.path.join(
                output_dir, f"bh{instance_type}-{n:02d}-{(matrix_id+1):03d}.dat"
            )
            write_sparse_matrix_to_file(matrix, output_file)
        else:
            print(f"Matrix ID {str_id} not found in the JSON file.")

    print(f"Done.")


if __name__ == "__main__":
    main()
