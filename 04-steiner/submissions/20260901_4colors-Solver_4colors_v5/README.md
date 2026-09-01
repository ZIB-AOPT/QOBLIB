# 4colors Solver — Submission (2026-09-01)

**Submitter:** 4colors Research · **Affiliation:** 4colors Research · **Date:** 2026-09-01
**Instances:** 189 of the 190 instances of 04-steiner (one withheld, see below)

---

## Attribution — read this first

**This is a classical result. There is no quantum contribution to any objective value in this
submission.**

The optimizer is a **Pathfinder-style negotiated-congestion router** with rip-up-and-reroute
polish, exact Dreyfus–Wagner repair inside a terminal-bounded corridor, and an acceptance-walk
iterated local search — all C++17, single-threaded. Every value reported here was produced by
that classical pipeline.

The wider research project this work sits in does contain QUBO formulations. Their role on *this*
problem must be stated precisely, because it is not the same as on 08-network and the weaker
claim would be the false one here:

> **On 04-steiner the QUBO approach contributed nothing at all — not objective gain, and not
> feasibility.** A penalty-QUBO of the Steiner ILP was built and tested. At every beatable size
> (s020 and above) it produces ~139,000-variable / 1.4M-term instances, and after 300 s the best
> bitstring still violated **162 of 38,366** constraints — not a legal packing, so there was
> nothing to score. The encoding is correct (it recovers the optimum on the trivial s003/s004
> cases); the approach simply does not scale. It is a recorded negative result, and no part of
> it touches the solver used here.

There is no QUBO, annealer, simulator or QPU anywhere in `solvers/steiner/src/`. **No QPU, GPU,
annealer, or quantum simulator was used at any point. QPU runtime is 0 because there was no QPU
in the loop.**

If you are skimming this file and take away only one sentence: *these are classical
negotiated-congestion routing results; the quantum part of the project contributed nothing to
this problem class and we are not claiming otherwise.*

---

## What this submission does and does not claim

**All 189 instances are feasible under the official checker** (`04-steiner/check`), which was run
against the `.sol` files in this directory as part of building it. Total edge count across all
189: **181,057**.

**The bulk of the movement is on instances with no published reference, and it is first-known,
not a beat.** Of the 189 instances here, **42 carry a published reference** (28 `.opt`, 14
`.bst`) and **147 do not**.

**One instance of the benchmark's 190 is deliberately not in this directory.**
`stp_s030_l3_t5_h1_rs24098` is published as `.opt` at 476, and we hold a solution the official
checker accepts at 475. Rather than let a merge silently rewrite a curated proven-optimal record,
that instance is withheld pending a maintainer ruling on the label, and the evidence is filed as a
separate issue. No value for it is claimed here.

- Against the 147 unreferenced instances: these are **first-known values**. Nobody has published
  a number to compare them against. That is a *different and weaker* thing than beating a
  published result, and it is stated here before the results table rather than left for the
  reader to work out.
- Against the 42 referenced instances in this directory: **one strict beat**
  (`stp_s070_l4_t6_h0_rs97531`, `.bst` 375 → 374). The remaining 41 are **matched at equal
  cost, and none is worse.** Of those 41, one is matched by an edge-identical packing on a
  near-forced 4-edge instance; the rest are matched by a **structurally different packing**,
  verified by arc-set comparison rather than by cost.

**The 147 and the 42 are never summed into one figure of merit.** There is no "beats on N
instances" claim in this submission.

## Dual bound

An exact per-net Dreyfus–Wagner relaxation gives a valid lower bound of **177,614**, leaving slack of
**3,443 — 1.90%** against this submission's total.

The relaxation drops node-disjointness *between* trees but keeps the one consequence of it that
is free: a terminal of net *j* lies in net *j*'s tree in every feasible packing, so node-disjoint
routing forbids that node to every other net. Masking each net's foreign terminals out of its own
Dreyfus–Wagner solve is therefore still a relaxation, and never weaker. It is worth 932 units over
the unmasked bound across the full benchmark, improving 647 individual nets.

Four controls are discharged on the bound itself: it **equals** the published proven optimum on 10
instances; the masked bound is `>=` the unmasked bound on every net, asserted per net at run time;
it agrees with an independent shortest-path computation on every 2-terminal net (40.0% of all nets
in the benchmark); and the falsifier `cost < bound` fires on **0 of 189**.

**Most of that slack is bound looseness, not available headroom.** On the instances where the true
answer is published, the slack decomposes exactly, and **99.5% of it is the bound being loose (401
units)** rather than distance remaining between our solutions and the published optima.

`Optimality Bound` is set equal to the objective on **10** rows — exactly those where
this bound meets our cost, so `LB == cost == OPT` and the optimum is proven. It is `N/A`
everywhere else: outside those rows we assert no proven optimum. The certified rows are all small
instances; the bound does not close on any large one, which is a limitation of the bound and is
stated as such rather than left to be inferred.

Extrapolating to the 147 open instances is estimator-sensitive, so it is reported as a **bracket
and never as a point estimate: 37–1,861 units**. Two of six candidate estimators are refuted by
their own output — they predict an optimum *above* a solution already held, which is impossible —
and that self-refutation is what shows the calibration set must be congestion-matched to the
target set. No single number should be quoted from this range.

---

**Reference:** QOBLIB/solvers/steiner — Pathfinder-style negotiated-congestion + rip-up-and-reroute + iterated local search (C++17).

**Workflow:**

(1) Parse arcs/terms; (2) Pathfinder negotiated-congestion routing (Takahashi-Matsuyama tree per net + per-node pres/hist penalties); (3) Tree pruning of non-terminal leaves; (4) Rip-up-and-reroute polish on the residual graph; (5) Iterated local search (perturb K nets with tabu + re-polish; acceptance-walk that tolerates small worsening to cross ridges, with adaptive perturbation strength escalated on stall); (6) Multistart over 8 parameter combos (net-order × pres-init × pres-mult × hist-inc) padded with random restarts.

**Hardware:** AMD/Intel x86_64 single-threaded, g++ 13, -O3 -march=native

Per-instance details, solution files and summary CSVs are in the subdirectories.
