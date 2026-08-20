# Discrete Simulated Bifurcation (dSB) on LABS — native degree-4 HUBO

## Scope

This is a benchmark of one specific, lean, dependency-free implementation of discrete Simulated
Bifurcation, applied to LABS as a native degree-4 HUBO with no quadratization and no auxiliary
variables.

It is not a benchmark of dSB as an algorithm family, nor of any commercial Simulated Bifurcation
Machine. Production SB implementations include enhancements this one deliberately omits, so
these results should not be read as an upper bound on what dSB can do on LABS.

## Attribution

The algorithm is discrete Simulated Bifurcation, due to **Goto et al.**:

> H. Goto, K. Endo, M. Suzuki, Y. Sakai, T. Kanao, Y. Hamakawa, R. Hidaka, M. Yamasaki,
> K. Tatsumura, *High-performance combinatorial optimization based on classical mechanics*,
> Science Advances **7**, eabe7953 (2021).

The implementation benchmarked here is an independent one written
by the submitter. Any weakness in these numbers is attributable to this implementation and its
parameterisation, not necessarily to the algorithm as published.

## Model — why no quadratization

LABS minimises `E(s) = Σ_{k=1}^{N-1} C_k(s)²` with `C_k(s) = Σ_{i=1}^{N-k} s_i s_{i+k}`,
`s ∈ {±1}^N`. Expanding `C_k²` gives a degree-4 polynomial in the spins; the `s_i² = 1`
identities collapse part of it to degree 2 and part to a constant.

This submission optimises that polynomial **directly**, over `N` spin variables. For contrast,
QOBLIB's own `models/quadratic_unconstrained` formulation introduces `z_ik = x_i·x_{i+k}` with
a penalty term:

| N | this submission | QOBLIB QUBO model |
| --- | --- | --- |
| 40 | 40 spins, 5 130 terms, degree 4 | 820 binaries + penalty parameter |
| 60 | 60 spins, 17 545 terms, degree 4 | 1 830 binaries + penalty parameter |
| 100 | 100 spins, 82 075 terms, degree 4 | 5 050 binaries + penalty parameter |

No penalty parameter is needed or tuned, because no constraint is introduced.

## The dynamics

SB embeds the discrete problem in a classical Hamiltonian system of `N` coupled nonlinear
oscillators and drives it through a bifurcation. Each spin `i` gets a position `x_i ∈ ℝ` and a
momentum `y_i ∈ ℝ`; the sign of `x_i` at the end of the run is the spin.

The objective enters as the polynomial the solver *maximises*,

```
Φ(ξ) = Σ_α b_α ∏_{i ∈ S_α} ξ_i ,        b_α = −(coefficient of that monomial in E)
```

where `S_α` is the index set of monomial `α`. LABS gives `|S_α| ∈ {2, 4}`. The coupling force is
its gradient,

```
f_i(ξ) = ∂Φ/∂ξ_i = Σ_{α : i ∈ S_α}  b_α  ∏_{j ∈ S_α, j ≠ i} ξ_j
```

which for degree 2 reduces to the usual `Σ_j J_ij ξ_j + h_i`. Nothing in the integrator assumes
degree 2; the degree only changes how `f` is evaluated.

**Equations of motion.** With pump amplitude `a(t)` and detuning `D(t) = a₀ − a(t)`:

```
ẋ_i = a₀ y_i
ẏ_i = −D(t) x_i  +  c₀ f_i(ξ)
```

The two variants differ only in where the coupling is sampled:

```
ξ = x          →  ballistic SB (bSB)
ξ = sign(x)    →  discrete SB (dSB)      ← used here
```

Sampling the coupling at `sign(x)` is what makes dSB discrete: the force depends only on the
current sign pattern, not on how far each oscillator has travelled, which removes the
analog-amplitude bias that costs bSB accuracy on combinatorial objectives.

**The bifurcation.** `a(t)` ramps linearly `0 → a₀` over the run, so `D(t)` ramps `a₀ → 0`. While
`D > 0` the `−D x` term is a restoring force and `x = 0` is stable — the system stays near the
origin and merely accumulates coupling information. As `D → 0` that restoring force vanishes and
each oscillator bifurcates, committing to a sign. The answer is read off as `σ = sign(x)` at
`t = T`.

**Integration.** Symplectic (semi-implicit) Euler at fixed step `Δt`, momentum first:

```
y ← y + Δt · ( −D_n x + c₀ f(ξ) )
x ← x + Δt · a₀ y                        ← uses the updated y
```

followed by perfectly-inelastic walls, which are what keep the trajectory bounded once `D → 0`:

```
if |x_i| > 1 :   x_i ← sign(x_i),   y_i ← 0
```

**Initial state and randomness.** `x = 0`, and `y` drawn uniformly from `(−0.1, 0.1)`. The
initial momenta are the *only* stochastic element — there is no thermal noise anywhere in the
run, so an independent restart means nothing more than a fresh `y`.

**The coupling constant.** `c₀` is set by Goto's prescription, extended to degree > 2 by
evaluating the coupling force at one random `±1` configuration and scaling to its RMS:

```
c₀ = c · 0.5 · a₀ / √( Σ_i f_i(ξ_rand)² / N )
```

so that the coupling term is comparable to the pressure term `a₀x` at the bifurcation. The
extension to degree-4 terms is the submitter's own, not from the literature (see *Omissions*).
All runs used `a₀ = 1`, `Δt = 0.25`, and scale `c = 2.0`; `Δt² · c ≈ 0.125` is the empirical
divergence boundary of this integrator, and every run sits on it (see *Tuning actually
performed*).

## Workflow

- **Pre-processing:** expand the objective into the spin polynomial above; cancel repeated
  indices via `s_i² = 1`. Deterministic, O(N³), done once per instance.
- **Pre-solvers:** none.
- **Main algorithm:** discrete SB — symplectic Euler at fixed step; coupling evaluated at
  `sign(x)`; perfectly-inelastic walls at `|x_i| = 1`; pump detuning ramped linearly to zero
  over the run. Independent restarts differ only in initial momenta.
- **Post-processing:** **none.** No local search, no 1-opt or tabu polish, no restart-from-best.

## Omissions

Each of the following would likely improve the numbers. They are listed because their absence is
the main reason to read these results as a floor rather than a ceiling.

1. **No local search.** Competitive LABS solvers pair a global method with a 1-opt/tabu polish.
   This is pure dSB output.
2. **No LABS-specific structure.** In particular no restriction to skew-symmetric sequences,
   which halves the effective search space for odd N and is exploited by most strong LABS
   heuristics.
3. **A heuristic coupling constant for degree > 2.** Goto's prescription for `c₀` is derived for
   *quadratic* Ising couplings. Its extension to degree-4 terms here (scaling from the RMS
   coupling force at a random ±1 point) is the submitter's own and is not from the literature.
   It is a plausible source of underperformance independent of the algorithm.

## Tuning actually performed

A four-stage parameter study (stability boundary, edge refinement, hit-probability scaling,
and throughput per CPU-second) is included in the reference repository. Two findings shaped the
runs:

- dSB **diverges** above `dt²·c₀scale ≈ 0.125`, and the risk grows with both `n_steps` and `N`.
  All submitted runs sit at `dt = 0.25, c₀scale = 2.0`, i.e. exactly on that boundary and no
  higher.
- The optimal `n_steps` is strongly N-dependent and does not transfer between instance sizes:
  at N=60 shallow-and-many wins on equal wall time, at N=80 the reverse held in a dedicated
  comparison. The campaign therefore ran a **depth portfolio**, splitting each instance's time
  budget evenly across `n_steps ∈ {2500, 20000, 160000}`.
- That portfolio's deep arm **never won**. Over N=41–100 the depth producing the reported value
  was 2500 or 20000; 160000 won 0 of the 47 instances it was measured over. It is starved by
  construction — a third of the budget buys it ~50 restarts, while the N=80 comparison that
  motivated it needed 256–512. From N=60 on it was dropped (see *Reading the results*).

## Results against the QOBLIB reference set

Scored against the curated values on `main` as of commit `48b285cc`:

| N | matched | gap to reference |
| --- | --- | --- |
| 2–43 | 42 of 42 | — |
| 44–59 | 3 of 16 (N=45, 46, 47) | opens at N=48 (+24), +64 by N=58 |
| 60–66 | 0 of 7 | +22…42 % (proven optima) |
| 67–100 | 0 of 34 | +10…79 % (best-known records) |

**45 of 99 matched, none beaten.** dSB reproduces every reference up to N=43 and three more at
N=45–47; above N=47 it matches nothing. The gap trends upward with N, averaging 61 % over
N=88–100 and peaking at +79 % at N=95. Merit factor falls to 5.42 at N=100, where the reference
set holds 8.65.

The binding constraint is hit probability, not run length: across most of the upper range the
reported value was found in a **single** restart out of hundreds or thousands (500 restarts at
N=100). The per-restart success probability collapses with N, and there is no local search to
compensate for it.

All 99 solutions were verified with the official checker (`02-labs/check`): 79 `VALID`,
20 `SUBOPTIMAL`, **0 `INVALID`**, 44 declared `OPTIMAL` (the checker rates only 3 ≤ N ≤ 66;
N=2 is valid but unrated, which reconciles 44 with the 45 matches above).

## Reading the results

Reported values are **best-of-`# Runs`** independent restarts. LABS is unconstrained, so every
±1 sequence is feasible and `# Feasible Runs = # Runs`. `Optimality Bound` is `N/A` throughout:
this method proves nothing. `CPU Runtime` is the measured wall time multiplied by the number of
cores actually available to the process — not a projection to a core count that was not used.

**The run protocol is not uniform in N, and the per-instance figures reflect what was actually
run:**

- **N=2–59** — three-arm portfolio `{2500, 20000, 160000}`, 420 s budget, 128 threads on
  128 cores.
- **N=60–100** — two-arm portfolio `{2500, 20000}`, 280 s budget, 100 threads on 100 cores.
  Each surviving arm keeps exactly the 140 s it had at N ≤ 59, so the arms that produce the
  answers are treated identically across the whole sweep; only the never-winning arm was
  removed. Restart counts for these instances are ~22 % below what the full machine would
  give at the same N.

Threads and cores are 1:1 in both regimes, so no instance was run oversubscribed and every
`CPU Runtime` is measured machine time.

The evidence for dropping the deep arm: across a preparatory sweep over N=41–87 it produced the
best value in **0 of 47** instances while consuming most of the wall time. At these sizes a
160000-step batch is a single chunk of one restart per thread, so the arm buys one extra batch
for roughly two thirds of the budget. The effect is visible across the boundary — N=59 (three
arms) drew **6912 restarts in 447 s**, N=61 (two arms) drew **6600 in 295 s**: the same pool of
restarts for two thirds of the wall time, on 22 % fewer cores.

Reported `Total Runtime` exceeds the nominal budget throughout, because an arm's deadline is
tested before a batch starts, not during it. The runtimes given are measured, not budgeted:
overshoot was 1.06× at N=59 under three arms and 1.05× at N=61 under two.
