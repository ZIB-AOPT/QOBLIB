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
import re
import argparse

def read_mst_file(file_path, n):
    sequence = [0] * n
    with open(file_path, 'r') as file:
        for line in file:
            match = re.match(r'x#(\d+)\s+(\d+)', line)
            if match:
                var_num = int(match.group(1))
                if var_num <= n:
                    value = int(match.group(2))
                    sequence[var_num - 1] = value
    return sequence

def compute_energy(sequence):
    energy = 0
    n = len(sequence)
    converted_sequence = [2 * x - 1 for x in sequence]  # Convert 0 to -1 and 1 to 1
    for k in range(1, n):
        autocorrelation = sum(converted_sequence[i] * converted_sequence[i + k] for i in range(n - k))
        energy += autocorrelation ** 2
    return energy

def compute_consecutive_entries(sequence):
    if not sequence:
        return []
    consecutive_entries = []
    current_value = sequence[0]
    count = 1
    for value in sequence[1:]:
        if value == current_value:
            count += 1
        else:
            consecutive_entries.append(count)
            current_value = value
            count = 1
    consecutive_entries.append(count)
    return consecutive_entries

def write_sequence_to_file(sequence, energy, consecutive_entries, output_file):
    with open(output_file, 'w') as file:
        file.write(f"# Energy: {energy}\n")
        file.write(f"# Consecutive entries: {''.join(map(str, consecutive_entries))}\n")

        for value in sequence:
            file.write(f"{value}\n")

def process_directory(directory, output_directory, file_extension):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        
    for filename in os.listdir(directory):
        if filename.endswith(file_extension):
            match = re.match(r'labs(\d+)', filename)
            if match:
                n = int(match.group(1))
                file_path = os.path.join(directory, filename)
                sequence = read_mst_file(file_path, n)
                energy = compute_energy(sequence)
                consecutive_entries = compute_consecutive_entries(sequence)
                output_file = os.path.join(output_directory, f"{filename[:-len(file_extension)]}.sol")
                write_sequence_to_file(sequence, energy, consecutive_entries, output_file)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('input_directory', type=str, help='Path to the input directory containing the original solutions')
    parser.add_argument('output_directory', type=str, help='Path to the output directory for the new solutions')
    parser.add_argument('file_extension', type=str, help='File extension of the original solution files')

    args = parser.parse_args()

    process_directory(args.input_directory, args.output_directory, args.file_extension)