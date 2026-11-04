#!/usr/bin/env python3
"""TRICK 1 (compact): frozen (c,k)-XORSAT -> MIS WITHOUT variable vertices.
Only clause-assignment vertices (K_{2^{k-1}} per clause). Variable consistency is enforced by
direct edges between assignment-vertices of different clauses that DISAGREE on a shared variable.
n = M * 2^{k-1}  (vs 2N+4M before); alpha* = M (clique cover of M cliques; planted achieves it).
More frozen core per node => harder at fixed n."""
import sys, random
from itertools import product, combinations
N=int(sys.argv[1]); c=int(sys.argv[2]); k=int(sys.argv[3]); seed=int(sys.argv[4]); tag=sys.argv[5] if len(sys.argv)>5 else f"cx_N{N}_c{c}_k{k}_s{seed}"
random.seed(seed); assert (c*N)%k==0
M=c*N//k; S=2**(k-1)
xstar=[random.randint(0,1) for _ in range(N)]
for _t in range(500):
    stubs=[v for v in range(N) for _ in range(c)]; random.shuffle(stubs)
    clauses=[stubs[k*i:k*i+k] for i in range(M)]
    if all(len(set(cl))==k for cl in clauses): break
else: print("FAILED tanner"); sys.exit(1)
# per-clause satisfying assignments (parity = planted)
sats=[]
for vs in clauses:
    b=0
    for v in vs: b^=xstar[v]
    sats.append([t for t in product((0,1),repeat=k) if (sum(t)&1)==b])
E=set()
def add(u,v):
    if u!=v: E.add((min(u,v),max(u,v)))
def vid(ci,j): return ci*S+j
for ci in range(M):                          # K_S within each clause
    for i,j in combinations(range(S),2): add(vid(ci,i),vid(ci,j))
# variable occurrences: var -> [(clause, pos)]
occ={}
for ci,vs in enumerate(clauses):
    for pos,v in enumerate(vs): occ.setdefault(v,[]).append((ci,pos))
for v,lst in occ.items():                    # consistency edges between disagreeing assignments
    for (c1,p1),(c2,p2) in combinations(lst,2):
        for j1,t1 in enumerate(sats[c1]):
            for j2,t2 in enumerate(sats[c2]):
                if t1[p1]!=t2[p2]: add(vid(c1,j1),vid(c2,j2))
n=M*S
from collections import Counter
deg=Counter()
for a,b in E: deg[a]+=1; deg[b]+=1
mind=min(deg.values()); deg2=sum(1 for x in range(n) if deg[x]<=2)
import os; os.makedirs("logs/xor_lab",exist_ok=True)
with open(f"logs/xor_lab/{tag}.dimacs","w") as f:
    f.write(f"p edge {n} {len(E)}\n")
    for a,b in sorted(E): f.write(f"e {a+1} {b+1}\n")
IS=[vid(ci,sats[ci].index(tuple(xstar[v] for v in clauses[ci]))) for ci in range(M)]
open(f"logs/xor_lab/{tag}.sol","w").write("\n".join(str(v+1) for v in IS)+"\n")  # planted IS (1-indexed nodelist)
open(f"logs/xor_lab/{tag}.clauses","w").write("\n".join(" ".join(map(str,cl)) for cl in clauses)+"\n")
# GF(2) nullity of clause-incidence matrix A (rows=clauses over N vars): #size-M IS = 2^(N-rank)
rows=[0]*M
for ci,cl in enumerate(clauses):
    for v in cl: rows[ci]|=(1<<v)
piv={}; rank=0
for r in rows:
    cur=r
    while cur:
        hb=cur.bit_length()-1
        if hb in piv: cur^=piv[hb]
        else: piv[hb]=cur; rank+=1; break
nullity=N-rank
Es=set(E); bad=sum(1 for i,j in combinations(range(len(IS)),2) if (min(IS[i],IS[j]),max(IS[i],IS[j])) in Es)
print(f"{tag}: n={n} m={len(E)} alpha*={M} N={N} nullity={nullity} n_optima=2^{nullity} planted_internal={bad} min_deg={mind} deg<=2={deg2}")
