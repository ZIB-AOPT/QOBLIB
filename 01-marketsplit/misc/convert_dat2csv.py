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

import numpy as np
import csv
import sys
import os


def read_matrix(file_path):
    data = []
    with open(file_path, "r") as f:
        for line in f:
            i, j, q_ij = line.split()
            data.append((int(i) - 1, int(j), int(float(q_ij))))

    if not data:
        return np.array([[]])

    # Determine the size of the matrix
    max_row = max(data, key=lambda x: x[0])[0]
    max_col = max(data, key=lambda x: x[1])[1]

    # Initialize the matrix with zeros
    matrix = np.zeros((max_row + 1, max_col + 1))

    for i, j, q_ij in data:
        matrix[i, j] = q_ij

    return matrix


def convert_to_csv(matrix, output_path):
    rows, cols = matrix.shape

    # Move the first column to the end of the matrix
    matrix = np.roll(matrix, shift=-1, axis=1)

    with open(output_path, "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write the dimensions of the matrix in the first row
        csvwriter.writerow([f"{rows} {cols-1}"])

        # Write each row of the matrix
        for row in matrix:
            formatted_row = [
                f"{int(item):4d}" for item in row
            ]  # Format each item to occupy 3 spaces
            csvwriter.writerow(formatted_row)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <input_file_path>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not input_file.endswith(".dat"):
        print("Error: Input file must have a .dat extension")
        sys.exit(1)

    # Change the output file extension from .dat to .csv
    output_file = os.path.splitext(input_file)[0] + ".csv"

    matrix = read_matrix(input_file)
    convert_to_csv(matrix, output_file)
    print(f"Matrix has been converted to CSV and saved to {output_file}")
