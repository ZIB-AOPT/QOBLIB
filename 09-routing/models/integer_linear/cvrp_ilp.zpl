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

# Vehicle Routing Problem (ILP)

param filename := "./../../instances/XSH-n20-k4-01.vrp"; 

# Define vehivle Limit
param VEHICLE_LIMIT := 4;

# Read the main information from the file
param DIMENSION := read filename as "2n" match "^DIMENSION" comment "#" use 1;
param CAPACITY := read filename as "2n" match "^CAPACITY" comment "#" use 1;

# Define the set of nodes
set NODES := { 1 .. DIMENSION };

# Read the nodes coordinates by matching all lines that have 3 numbers separated by spaces
param X_COORD[NODES] := read filename as "<1n> 2n" match "^[0-9]+\s+[0-9]+\s+[0-9]+\s*$" comment "#" use DIMENSION;
param Y_COORD[NODES] := read filename as "<1n> 3n" match "^[0-9]+\s+[0-9]+\s+[0-9]+\s*$" comment "#" use DIMENSION;

# Read the demand of each node by matching all lines that have 2 numbers separated by spaces
param DEMAND[NODES] := read filename as "<1n> 2n" match "^[0-9]+\s+[0-9]+\s*$" comment "#" use DIMENSION;

# Read the depot nodes
# "-1" means that the depot is not fixed
set DEPOTS := { read filename as "<1n>" match "^-?[0-9]+\s*$" comment "#" };

# Define distance function
defnumb dist(a, b) := sqrt((X_COORD[a] - X_COORD[b])^2 + (Y_COORD[a] - Y_COORD[b])^2);

# Define set of Variables
var x[NODES * NODES] binary;
var y[NODES] integer >= 0 <= CAPACITY;

# (10)
# Define the objective function to
# minimize the total distance traveled
minimize cost: sum <i,j> in NODES * NODES: dist(i, j) * x[i, j];

# (11) 
# Ensure that each customer is visited exactly once
# Except for the depot node
subto customer_visited_once: 
    forall <i> in NODES without {1}:
        sum <j> in NODES without {i}: x[i, j] == 1;

# (12)
# Flow conservation constraint
subto flow_conservation:
    forall <h> in NODES without {1}:
        sum <i> in NODES without {h}: (x[i, h] - x[h, i]) == 0; 

# (13)
# Ensure that we use at most VEHICLE_LIMIT vehicles
subto vehicle_limit:
    sum <j> in NODES without {1}: x[1, j] <= VEHICLE_LIMIT;

# (14)
# Ensure that y's are updated correctly
subto capacity_limit:
    forall <i> in NODES:
        forall <j> in NODES without {1, i}:
            y[j] >= y[i] + DEMAND[j] * x[i, j] - CAPACITY * (1 - x[i, j]);

# (15)
# Ensure that capacity is not exceeded at any node
subto capacity_limit_node_ub:
    forall <i> in NODES:
        y[i] <= CAPACITY;

subto capacity_limit_node_lb:
    forall <i> in NODES:
        DEMAND[i] <= y[i];
        