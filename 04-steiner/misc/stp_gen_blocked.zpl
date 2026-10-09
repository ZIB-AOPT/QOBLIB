# Same as stp3d4 but with aggregated constraints.
#
set   Parameter := { "nodes", "nets" };
param parameter[Parameter] := read "param.dat" as "<1s> 2n" comment "#";

set L := { 1 .. parameter["nets"] };     # Nets
set V := { 1 .. parameter["nodes"] };    # Nodes
set S := { read "terms.dat" as "<1n>"    comment "#" };    # Special: Terms and Roots
set R := { read "roots.dat" as "<1n>"    comment "#" };    # Roots
set A := { read "arcs.dat"  as "<1n,2n>" comment "#" };
set T := S - R;  # only Terms
set N := V - S;  # Normal
set U := { read "blocked.dat" as "<1n, 2n>" comment "#" }; 

param innet[S]       := read "terms.dat" as "<1n> 2n"    comment "#";
param cost [A]       := read "arcs.dat" as "<1n,2n> 3n" comment "#";
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
subto terms_flow_bal_zero:
   forall <t> in T do 
      forall <s> in T with innet[s] != innet[t] do
         sum <j,s> in A : (x[j,s,t] + x[s,j,t]) == 0;

# for normal nodes flow balance
subto nodes_flow_bal:
   forall <t> in T do
      forall <n> in N do
         sum <n,i> in A : (x[n,i,t] - x[i,n,t]) == 0;

# bind y to x; disaggregated constraint
#subto bind_y_x:
#   forall <i,j> in A do
#      forall <k> in L do
#         forall <t> in T with innet[t] == k do
#	    x[i,j,t] <= y[i,j,k];


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

# add a constraint to prevent reuse of edges from blocked.dat
subto prevent_reuse:
   forall <k> in L do	
      sum <i,j> in U: y[i,j,k] <= 0;	
   


