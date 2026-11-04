#!/usr/bin/env python3
"""Frozen REGULAR (c,3)-XORSAT -> MIS. Every var in exactly c clauses (var-vertex degree 1+2c),
every clause 3 vars. Planted-satisfiable. Regular XORSAT = expander-code regime: frozen, hard
for local search, and (unlike the sparse version) no low-degree vertices to peel."""
import sys, random
from itertools import product
N=int(sys.argv[1]); c=int(sys.argv[2]); seed=int(sys.argv[3]); tag=sys.argv[4] if len(sys.argv)>4 else f"xreg_N{N}_c{c}_s{seed}"
random.seed(seed)
assert (c*N)%3==0
M=c*N//3
xstar=[random.randint(0,1) for _ in range(N)]
# (c,3)-biregular Tanner via stub matching (retry to avoid a var appearing twice in a clause)
for _try in range(200):
    var_stubs=[v for v in range(N) for _ in range(c)]; random.shuffle(var_stubs)
    clauses=[var_stubs[3*i:3*i+3] for i in range(M)]
    if all(len(set(cl))==3 for cl in clauses): break
else:
    print("FAILED to build simple Tanner"); sys.exit(1)
BASE=2*N; E=set()
def add(u,v):
    if u!=v: E.add((min(u,v),max(u,v)))
for v in range(N): add(2*v,2*v+1)
cl_info=[]
for ci,(x,y,z) in enumerate(clauses):
    b=xstar[x]^xstar[y]^xstar[z]
    sats=[t for t in product((0,1),repeat=3) if (t[0]^t[1]^t[2])==b]
    cl_info.append((x,y,z,sats)); ids=[BASE+4*ci+k for k in range(4)]
    for i in range(4):
        for j in range(i+1,4): add(ids[i],ids[j])
    for k,(a,bb,cc) in enumerate(sats):
        add(ids[k],2*x+(1-a)); add(ids[k],2*y+(1-bb)); add(ids[k],2*z+(1-cc))
n=BASE+4*M
from collections import Counter
deg=Counter()
for u,v in E: deg[u]+=1; deg[v]+=1
mind=min(deg.values()); deg2=sum(1 for v in range(n) if deg[v]<=2)
import os; os.makedirs("logs/xor_lab",exist_ok=True)
with open(f"logs/xor_lab/{tag}.dimacs","w") as f:
    f.write(f"p edge {n} {len(E)}\n")
    for u,v in sorted(E): f.write(f"e {u+1} {v+1}\n")
IS=[2*v+xstar[v] for v in range(N)]
for ci,(x,y,z,sats) in enumerate(cl_info):
    IS.append(BASE+4*ci+sats.index((xstar[x],xstar[y],xstar[z])))
Es=set(E); bad=sum(1 for i in range(len(IS)) for j in range(i+1,len(IS)) if (min(IS[i],IS[j]),max(IS[i],IS[j])) in Es)
open(f"logs/xor_lab/{tag}.sol","w").write("\n".join(str(v+1) for v in IS)+"\n")
print(f"{tag}: n={n} m={len(E)} alpha*={N+M} planted_internal={bad} min_deg={mind} deg<=2={deg2}")
