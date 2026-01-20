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

# Define the directory to scan
directory = "./../solutions/"  # Replace with your actual directory path

# CSV file to write the extracted data
output_csv = "output.csv"

# Regex to extract info from file names
file_pattern = re.compile(r"stp_s(?P<Size>\d+)_l(?P<Layers>\d+)_t(?P<Terminals>\d+)_h(?P<Holes>\d+)_rs(?P<Seed>\d+).*\.sol")

# List to store the extracted data
data = []

# Traverse the directory
for root, dirs, files in os.walk(directory):
    for file in files:
        match = file_pattern.match(file)
        if match:
            info = match.groupdict()
            sol_file_path = os.path.join(root, file)

            # Try to read the solution file
            if os.path.exists(sol_file_path):
                with open(sol_file_path, "r") as sol_file:
                    first_line = sol_file.readline().strip()
                    cost_match = re.match(r"# Cost: (?P<Cost>\d+)", first_line)
                    if cost_match:
                        info["Cost"] = cost_match.group("Cost")
                    else:
                        info["Cost"] = "N/A"  # Handle cases where the cost line is missing
            else:
                info["Cost"] = "N/A"  # Handle cases where the solution file is missing

            # Mark the solution with a '*' if it has .opt.sol in the filename
            if ".opt.sol" in file:
                info["Cost"] += "\\*"

            # Append the info to the data list
            data.append(info)

data.sort(key=lambda x: (int(x["Size"]), int(x["Layers"]), int(x["Terminals"]), int(x["Holes"]), int(x["Seed"])))

# Write the data to a CSV file
with open(output_csv, "w", newline="") as csvfile:
    fieldnames = ["Size", "Layers", "Terminals", "Holes", "Seed", "Cost"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(data)

print(f"Data extraction complete. Output saved to {output_csv}")

def csv_to_markdown(csv_path):
    """Converts a CSV file to a Markdown table."""
    with open(csv_path, "r") as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    # Extract header and data rows
    header = rows[0]
    data_rows = rows[1:]

    # Create Markdown table
    markdown_table = "| " + " | ".join(header) + " |\n"
    markdown_table += "| " + " | ".join(["-" * len(col) for col in header]) + " |\n"
    for row in data_rows:
        markdown_table += "| " + " | ".join(row) + " |\n"

    return markdown_table

# Convert the CSV file to a Markdown table
markdown_output = "output.md"
markdown_table = csv_to_markdown(output_csv)

# Write the Markdown table to a file
with open(markdown_output, "w") as mdfile:
    mdfile.write(markdown_table)
