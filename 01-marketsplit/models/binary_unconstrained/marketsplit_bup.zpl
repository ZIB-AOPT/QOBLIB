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
# Market Split problem modelled as Binary Unconstraint Program
#
param filename := "ms_3_100_1.dat";

set I   := { read filename as "<1n>" comment "#" };
set J   := { read filename as "<2n>" comment "#" };
set IxJ := { read filename as "<1n,2n>" comment "#" };
set JJ  := { <j> in J with j > 0 };

param a[IxJ] := read filename as "<1n,2n> 3n" comment "#";

var x[JJ] binary;

minimize obj: sum <i> in I : (a[i,0] - sum <j> in J with j > 0 : a[i,j] * x[j])^2;
