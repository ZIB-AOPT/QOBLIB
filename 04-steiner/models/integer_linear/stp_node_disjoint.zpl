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

# Steiner tree packing problem with node-disjoint trees.
# Corresponds to the multicommodity flow formulation in
# Section 2.2 of "Steiner tree packing revisited".
# Note that variable names x, y are switched compared to
# the paper.
#

# Hardcoded parameters as fallback
param param_file   := "./../../instances/stp_s020_l2_t3_h2_rs24098/param.dat";
param terms_file   := "./../../instances/stp_s020_l2_t3_h2_rs24098/terms.dat";
param roots_file   := "./../../instances/stp_s020_l2_t3_h2_rs24098/roots.dat";
param arcs_file    := "./../../instances/stp_s020_l2_t3_h2_rs24098/arcs.dat";

set   Parameter := { "nodes", "nets" };
param parameter[Parameter] := read param_file as "<1s> 2n" comment "#";

set L := { 1 .. parameter["nets"] };     # Nets
set V := { 1 .. parameter["nodes"] };    # Nodes
set S := { read terms_file as "<1n>"    comment "#" };    # Special: Terms and Roots
set R := { read roots_file as "<1n>"    comment "#" };    # Roots
set A := { read arcs_file  as "<1n,2n>" comment "#" };
set T := S - R;  # only Terms
set N := V - S;  # Normal

param innet[S]       := read terms_file as "<1n> 2n"    comment "#";
param cost [A]       := read arcs_file as "<1n,2n> 3n" comment "#";
param bigM           := parameter["nodes"] * parameter["nodes"];
param nets[<k> in L] := card({ <t> in T with innet[t] == k});

do forall <s> in S : check <innet[s]> in L;

var x[A * T] binary;
var y[A * L] binary;

minimize obj: 
   sum <i,j,k> in A * L : cost[i,j] * y[i,j,k]; #(cost[i,j] + (i + j) / bigM) * 

# for all roots flow out
subto root_flow_out: 
   forall <t> in T do
      forall <r> in R do
         sum <r,j> in A : x[r,j,t] == if innet[r] == innet[t] then 1 else 0 end;

# for all roots flow in
subto root_flow_in: 
   forall <t> in T do
      forall <r> in R do 
         sum <j,r> in A : x[j,r,t] == 0;


# for all terms flow out
subto terms_flow_out:
   forall <t> in T do 
       sum <t,j> in A : x[t,j,t] == 0;

# for all terms in their net one flow in
subto terms_flow_in:
   forall <t> in T do 
     sum <j,t> in A : x[j,t,t] == 1;

# for all terms in the same net in equals out
subto terms_flow_bal_same:
   forall <t> in T do 
      forall <s> in T with s != t and innet[s] == innet[t] do
         sum <j,s> in A : (x[j,s,t] - x[s,j,t]) == 0;

# for all terms in a different net its zero
subto terms_flow_bal_diff:
   forall <t> in T do 
      forall <s> in T with innet[s] != innet[t] do
         sum <j,s> in A : (x[j,s,t] + x[s,j,t]) == 0;

# for normal nodes flow balance
subto nodes_flow_bal:
   forall <t> in T do
      forall <n> in N do
         sum <n,i> in A : (x[n,i,t] - x[i,n,t]) == 0;

# bind y to x
subto bind_x_y:
   forall <i,j> in A do
      forall <k> in L do
         sum <t> in T with innet[t] == k :  x[i,j,t] <= nets[k] * y[i,j,k];

# node disjointness
subto disjoint_nonroot:
   forall <j> in V without R do
      sum <i,j,k> in A * L : y[i,j,k] <= 1;
subto disjoint_root:
   forall <r> in R do
      sum <i,r,k> in A * L : y[i,r,k] <= 0;



