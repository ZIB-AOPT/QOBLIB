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

#TK 13Jul2024

#param a3[J*J] :=
#      <1,1> 916, <1,2>  84, <1,3>   0,
#      <2,1>  84, <2,2> 457, <2,3> 459,
#      <3,1>   0, <3,2> 459, <3,3> 541
#      ;
#set P3 := {
#   <1,2,3>, <1,3,2>, <2,1,3>, <2,3,1>, <3,1,2>, <3,2,1>
#};

param msize := 3;
param ssize := 1000;
set J := { 1 .. msize };

param A[J*J] := read filename as "<1n,2n> 3n";

set P := permute(J);
set I   := { 1 .. card(P) };

var x[I] integer <= ssize;
var z[I] binary;

minimize count: sum <i> in I: z[i];

subto c1:
   sum <i> in I: x[i] == ssize;

subto c2:
   forall <m,n> in J*J do
      sum <i> in I with ord(P, i, m) == n: x[i] == A[m,n];
       
subto c3:
   forall <i> in I do
      x[i] <= ssize * z[i];
