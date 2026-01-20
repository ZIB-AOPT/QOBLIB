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

import re
import argparse

def parse_gurobi_solution(file_path):
    y_vars = {}
    with open(file_path, 'r') as file:
        for line in file:
            match = re.match(r'^y\#(\d+)\#(\d+)\#(\d+)\s+(\d+)', line)
            if match:
                node_idx1, node_idx2, belonging, value = map(int, match.groups())
                if value == 1:
                    if belonging not in y_vars:
                        y_vars[belonging] = []
                    y_vars[belonging].append((node_idx1, node_idx2))
    return y_vars

def parse_arc_costs(file_path):
    arc_costs = {}
    with open(file_path, 'r') as file:
        for line in file:
            match = re.match(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s*$', line)
            if match:
                node_idx1, node_idx2, cost = map(int, match.groups())
                arc_costs[(node_idx1, node_idx2)] = cost
    return arc_costs

def write_arcs_to_file(y_vars, total_cost, output_file_path):
    with open(output_file_path, 'w') as file:
        file.write(f"# Cost: {total_cost}\n\n")
        file.write("# Tail Head Net\n")
        for belonging in sorted(y_vars.keys()):
            for node_idx1, node_idx2 in sorted(y_vars[belonging]):
                file.write(f"{node_idx1} {node_idx2} {belonging}\n")

def compute_solution_cost(y_vars, arc_costs):
    total_cost = 0
    for belonging in y_vars:
        for node_idx1, node_idx2 in y_vars[belonging]:
            total_cost += arc_costs.get((node_idx1, node_idx2))
    return total_cost

def main():
    parser = argparse.ArgumentParser(description='Convert Gurobi solution to arcs format and compute the solution cost.')
    parser.add_argument('input_file_path', type=str, help='Path to the input Gurobi solution file')
    parser.add_argument('output_file_path', type=str, help='Path to the output arcs file')
    parser.add_argument('cost_file_path', type=str, help='Path to the file containing arc costs')
    args = parser.parse_args()

    y_vars = parse_gurobi_solution(args.input_file_path)
    arc_costs = parse_arc_costs(args.cost_file_path)

    total_cost = compute_solution_cost(y_vars, arc_costs)

    write_arcs_to_file(y_vars, total_cost, args.output_file_path)

    print(f"Wrote arcs to {args.output_file_path} with total cost {total_cost}")

if __name__ == "__main__":
    main()