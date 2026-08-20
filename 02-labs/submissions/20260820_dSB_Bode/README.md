# Discrete Simulated Bifurcation (dSB) on LABS — native degree-4 HUBO

## What this submission is, and is not

**Is:** a benchmark of one specific, lean, dependency-free implementation of discrete
Simulated Bifurcation, applied to LABS as a *native degree-4 HUBO* with no quadratization and
no auxiliary variables.

**Is not:** a benchmark of "dSB" as an algorithm family, and not a benchmark of any commercial
Simulated Bifurcation Machine. Production SB implementations include enhancements this one
deliberately omits. Results here should not be read as an upper bound on what dSB can do on
LABS.

## Attribution

The algorithm is discrete Simulated Bifurcation, due to **Goto et al.**:

> H. Goto, K. Endo, M. Suzuki, Y. Sakai, T. Kanao, Y. Hamakawa, R. Hidaka, M. Yamasaki,
> K. Tatsumura, *High-performance combinatorial optimization based on classical mechanics*,
> Science Advances **7**, eabe7953 (2021).

The implementation benchmarked here is an independent one (`SimulatedBifurcation.jl`) written
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

## Workflow

- **Pre-processing:** expand the objective into the spin polynomial above; cancel repeated
  indices via `s_i² = 1`. Deterministic, O(N³), done once per instance.
- **Pre-solvers:** none.
- **Main algorithm:** discrete SB — symplectic Euler at fixed step; coupling evaluated at
  `sign(x)`; perfectly-inelastic walls at `|x_i| = 1`; pump detuning ramped linearly to zero
  over the run. Independent restarts differ only in initial momenta.
- **Post-processing:** **none.** No local search, no 1-opt or tabu polish, no restart-from-best.

## What is deliberately absent

Stated explicitly because each of these would likely improve the numbers, and their absence is
the main reason to read these results as a floor rather than a ceiling:

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
  was 2500 (47 instances) or 20000 (13 instances); 160000 won 0 of 60. It is starved by
  construction — a third of the budget buys it ~50 restarts, while the N=80 comparison that
  motivated it needed 256–512. From N=88 on it was dropped (see *Reading the results*).

## Results against the QOBLIB reference set

Scored against the curated values on `main` as of commit `48b285cc`:

| N | matched | gap to reference |
| --- | --- | --- |
| 2–43 | 42 of 42 | — |
| 44–59 | 3 of 16 (N=45, 46, 47) | opens at N=48 (+24), +64 by N=58 |
| 60–66 | 0 of 7 | +17…42 % (proven optima) |
| 67–100 | 0 of 34 | +10…79 % (best-known records) |

**45 of 99 matched, none beaten.** dSB reproduces every reference up to N=43 and three more at
N=45–47; above N=47 it matches nothing. The gap trends upward with N, averaging 55 % over
N=88–100 and peaking at +79 % at N=95. Merit factor falls to 5.42 at N=100, where the reference
set holds 8.65.

The binding constraint is hit probability, not run length: across most of the upper range the
reported value was found in a **single** restart out of hundreds or thousands (640 restarts at
N=100). That is the signature this submission is meant to document — a solver whose per-restart
success probability collapses with N, with no local search to compensate.

All 99 solutions were verified with the official checker (`02-labs/check`): 79 `VALID`,
20 `SUBOPTIMAL`, **0 `INVALID`**, 44 declared `OPTIMAL` (the checker rates only 3 ≤ N ≤ 66;
N=2 is valid but unrated, which reconciles 44 with the 45 matches above).

## Reading the results

Reported values are **best-of-`# Runs`** independent restarts. LABS is unconstrained, so every
±1 sequence is feasible and `# Feasible Runs = # Runs`. `Optimality Bound` is `N/A` throughout:
this method proves nothing. Runtimes are the measured wall time of the batch multiplied by the
thread count actually used — not a projection to a core count that was not used.

**The run protocol is not uniform in N, and the per-instance figures reflect what was actually
run:**

- **N=2–87** — three-arm portfolio `{2500, 20000, 160000}`, 420 s budget, 128 threads.
- **N=88–100** — two-arm portfolio `{2500, 20000}`, 280 s budget, 128 threads on 112 cores.
  Each surviving arm keeps exactly the 140 s it had at N ≤ 87, so the arms that produce the
  answers are treated identically across the whole sweep; only the never-winning arm was
  removed. Restart counts for these instances are ~12 % below what a same-N three-arm run on
  all 128 cores would have given.

The evidence for that change: N=87 (three arms) and N=88 (two arms) both did **1664 restarts**,
in 1123 s and 325 s respectively — the same restart count for 29 % of the wall time. At these
sizes a 160000-step batch is a single chunk of 128 restarts, so the deep arm spent roughly
800 s to add one batch to the pool.

Reported `Total Runtime` exceeds the nominal budget throughout, because an arm's deadline is
tested before a batch starts, not during it. The runtimes given are measured, not budgeted:
overshoot was 2.7× at N=87 under three arms and 1.16× at N=88 under two.
