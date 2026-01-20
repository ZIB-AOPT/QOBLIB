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

import argparse

def read_graph(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    nodes = 0
    edges = 0
    edge_list = []
    comments = []

    for line in lines:
        if line.startswith('c'):
            comments.append(line)
        elif line.startswith('p edge'):
            parts = line.split()
            nodes = int(parts[2])
            edges = int(parts[3])
        elif line.startswith('e'):
            parts = line.split()
            node1 = int(parts[1])
            node2 = int(parts[2])
            edge_list.append((node1, node2))

    # Create a mapping from original node numbers to consecutive numbers
    unique_nodes = sorted(set(node for edge in edge_list for node in edge))
    node_mapping = {node: i + 1 for i, node in enumerate(unique_nodes)}

    # Adjust the indexing to consecutive numbers
    adjusted_edges = [(node_mapping[node1], node_mapping[node2]) for node1, node2 in edge_list]

    return len(unique_nodes), edges, adjusted_edges, comments

def write_graph(file_path, nodes, edges, edge_list, comments):
    with open(file_path, 'w') as file:
        for comment in comments:
            file.write(comment)
        file.write(f"p edge {nodes} {edges}\n")
        for node1, node2 in edge_list:
            file.write(f"e {node1} {node2}\n")
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a graph file and fix indexing.')
    parser.add_argument('input_file', type=str, help='Path to the input graph file')
    parser.add_argument('output_file', type=str, help='Path to the output graph file')
    args = parser.parse_args()

    nodes, edges, edge_list, comments = read_graph(args.input_file)
    write_graph(args.output_file, nodes, edges, edge_list, comments)