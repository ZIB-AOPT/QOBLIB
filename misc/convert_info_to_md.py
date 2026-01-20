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

def parse_info_file(file_path):
    instances = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("#") or not line.strip():
                continue  # Skip headers and empty lines
            parts = line.split()
            instance = parts[0].replace("./", "")  # Remove "./" from instance name
            status = parts[1]
            value = parts[2]
            instances.append((instance, status, value))
    return instances

def generate_markdown(instances, output_path):
    with open(output_path, 'w') as md_file:
        md_file.write("# Solutions\n")

        # Markdown table header
        md_file.write("| Instance | Our Solution | Best Solution in Literature | Citation |\n")
        md_file.write("|:---------|-------------:|---------------------------:|:---------|\n")

        # Fill in table rows
        for instance, status, value in instances:
            # Handle the `=opt=` case by auto-filling the best solution and removing the citation
            if status == "=opt=":
                best_solution = value  # If optimal, fill best solution with the same value
                citation = ""          # No citation for optimal solutions
            else:
                best_solution = "[TO FILL]"
                citation = "[Author, Year]"

            # Right-align solution values and write the row
            md_file.write(f"| {instance} | {value:>11} | {best_solution:>27} | {citation} |\n")

def process_info_files(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == "0-info.txt":
                file_path = os.path.join(dirpath, filename)
                instances = parse_info_file(file_path)

                # Generate corresponding markdown file in the same directory
                output_filename = "README_new.md"
                output_path = os.path.join(dirpath, output_filename)

                generate_markdown(instances, output_path)
                print(f"Generated markdown: {output_path}")

# Change this to your root directory containing the nested folders
root_directory = "./../"
process_info_files(root_directory)
