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

# Maximilian Schicker / September 2024

# Read the necessary parameter
param edges := read filename as "4n" use 1 match "^p" comment "c";
param nodes := read filename as "3n" use 1 match "^p" comment "c";

# get the set of edges
set E := { read filename as "<2n,3n>" match "^e" comment "c" };

# Initialize the set of nodes
set V := {1..nodes};

# Create binary variables for each node
var x[V] binary;

maximize obj:
  sum <v> in V   : x[v]
  - 2 * sum <u,v> in E : x[u] * x[v];