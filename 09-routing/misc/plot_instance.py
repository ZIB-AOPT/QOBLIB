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

import matplotlib.pyplot as plt
import sys
import math

def read_cvrp_instance(filename):
    nodes = {}
    demands = {}
    depot = None
    capacity = None
    
    with open(filename, 'r') as file:
        section = None
        for line in file:
            line = line.strip()
            if line.startswith("CAPACITY"):
                capacity = int(line.split(": ")[-1])
            elif line.startswith("NODE_COORD_SECTION"):
                section = "nodes"
                continue
            elif line.startswith("DEMAND_SECTION"):
                section = "demands"
                continue
            elif line.startswith("DEPOT_SECTION"):
                section = "depot"
                continue
            elif line.startswith("EOF"):
                break
            
            if section == "nodes":
                parts = line.split()
                nodes[int(parts[0])] = (int(parts[1]), int(parts[2]))
            elif section == "demands":
                parts = line.split()
                demands[int(parts[0])] = int(parts[1])
            elif section == "depot":
                depot = int(line) if int(line) != -1 else depot
    
    return nodes, demands, depot, capacity

def read_cvrp_solution(filename):
    routes = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("Route"):
                parts = line.split(": ")
                route = [int(node) + 1 for node in parts[1].split()]
                routes.append(route)
    return routes

def euclidean_distance(node1, node2):
    return math.sqrt((node1[0] - node2[0]) ** 2 + (node1[1] - node2[1]) ** 2)

def compute_solution_cost(nodes, depot, routes):
    total_cost = 0
    for route in routes:
        route_nodes = [depot] + route + [depot]
        for i in range(len(route_nodes) - 1):
            total_cost += euclidean_distance(nodes[route_nodes[i]], nodes[route_nodes[i + 1]])
    return total_cost

def check_capacity_constraint(routes, demands, capacity):
    for i, route in enumerate(routes):
        total_demand = sum(demands[node] for node in route)
        if total_demand > capacity:
            print(f"Warning: Capacity constraint violated on Route {i+1} (Demand: {total_demand}, Capacity: {capacity})")

def plot_cvrp_instance(nodes, demands, depot, basename, routes=None, capacity=None):
    plt.figure(figsize=(8, 8))
    for node, (x, y) in nodes.items():
        if node == depot:
            plt.scatter(x, y, color='red', s=200, label='Depot' if node == depot else "")
            plt.text(x, y, str(node), fontsize=12, ha='right', va='bottom', color='black')
        else:
            plt.scatter(x, y, color='blue', s=demands[node] * 2, alpha=0.7, label='Customer' if node == 2 else "")
            plt.text(x, y, str(node), fontsize=10, ha='right', va='bottom', color='black')
    
    total_cost = 0
    if routes:
        colors = ['green', 'purple', 'orange', 'cyan', 'magenta', 'yellow']
        for i, route in enumerate(routes):
            route_nodes = [depot] + route + [depot]
            for j in range(len(route_nodes) - 1):
                x1, y1 = nodes[route_nodes[j]]
                x2, y2 = nodes[route_nodes[j + 1]]
                plt.plot([x1, x2], [y1, y2], marker='o', color=colors[i % len(colors)], linestyle='-')
            total_cost += compute_solution_cost(nodes, depot, [route])
    
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.title(f"CVRP Instance - Solution Cost: {total_cost:.2f}")
    plt.legend()
    plt.grid()
    plt.savefig(f'{basename}.pdf')

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python script.py <instance_file> [solution_file]")
        sys.exit(1)
    
    instance_file = sys.argv[1]
    solution_file = sys.argv[2] if len(sys.argv) == 3 else None
    
    nodes, demands, depot, capacity = read_cvrp_instance(instance_file)
    routes = read_cvrp_solution(solution_file) if solution_file else None
    
    if routes:
        check_capacity_constraint(routes, demands, capacity)

    # get the basename of the file
    basename = instance_file.split('/')[-1].split('.')[0]
    
    plot_cvrp_instance(nodes, demands, depot, basename, routes, capacity)