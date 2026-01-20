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

# TK 20May2024
# LABS Low Autocorrelation Binary Sequence modelled as an Integer Linear Program
#
param n := 47;

set I := {1 .. n};
set K := {1 .. n - 1};

var x[I] binary;
var c[<k> in K] integer >= - n + k  <= n - k;

# -1,1 => 2 x - 1

minimize energy: sum <k> in K : c[k] * c[k];

subto c1:
   forall <k> in K do
      c[k] == sum <i> in {1 .. n - k} : (2 * x[i] - 1) * (2 * x[i + k] - 1);
      
   