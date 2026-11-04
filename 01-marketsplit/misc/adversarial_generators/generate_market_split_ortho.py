#!/usr/bin/env python3
"""
generate_market_split_ortho.py  --  "tight-frame / max-determinant" market-split
generator.  A NEW generation method, independent of the generate_market_split_v*
family (it shares NO construction step with ms_core: no multi-prime base, no
spread gadgets, no anti-LDS pairs, no exact-midpoint hill-climb, no anti-Hoelder
permutation, no scramble).

------------------------------------------------------------------------------
Idea (why this is different and why it should be hard for sd2 / lll-bkz)
------------------------------------------------------------------------------
With midpoint RHS the market-split feasibility problem is equivalent to finding
the planted +/-1 vector y* = 2x*-1 (||y*|| = sqrt(n)) inside the integer KERNEL
lattice K = {v in Z^n : A v = 0}, dim d = n - m.  sd2 BKZ-reduces K and then
LDS-enumerates for a +/-1 vector.

Two levers drive sd2's failure, and this generator targets BOTH by *design*
rather than by template:

  (1) DEPTH of y*.  Enumeration must search a ball of radius ~sqrt(n); the cost
      grows as (sqrt(n)/GH(K))^d, where GH(K) ~ det(K)^{1/d} is the Gaussian
      heuristic length.  det(K) = sqrt(det(A A^T)) = sqrt(prod sigma_i(A)^2).
      For a FIXED entry budget (Frobenius norm ||A||_F^2 = sum sigma_i^2 is
      capped by D), AM-GM says prod sigma_i^2 is MAXIMISED exactly when all
      singular values are equal -- i.e. when A is a TIGHT FRAME (A A^T = c I).
      So we drive A toward a tight frame: this is the global, principled version
      of v*'s heuristic per-column-norm equalisation, and it maximises GH(K),
      pushing y* as deep as the entry budget allows.

  (2) KERNEL DIMENSION vs the beta<=75 reduction ceiling.  BKZ-beta ~ HKZ for
      dim <= beta, giving a steep GS profile and a cheap LDS tail.  We therefore
      run at SMALL m (few constraints) so d = n - m stays as large as possible
      for a given n -- keeping a flat, reduction-resistant GS tail even under the
      harness's beta-75 combo.  Small m at density~1 forces large coefficients D
      (accepted per the project decision: minimise n, relax the <300 bound).

Optional refinement (--lll-refine): feasibility-preserving local moves accepted
only if they FLATTEN the (numpy float-LLL) reduced GS profile of K.  v7 used a
flat-GS signal to *select* among random draws; here it is an *optimisation
objective* driving entry-level moves -- a different use.

Feasibility is exact: we plant a balanced x*, keep b = A x* at all times, and
every move preserves A x* (so x* stays a solution).  Uniqueness is guarded by a
randomised feasible search + an analytic E[# other solutions] estimate.

Output: the standard harness folder layout
    <outdir>/n{n}_m{m}_hi{D}_seed{seed}/{instance.txt,solution.txt,gen.log}
so deploy_variants_ccc.sh / submit_overnight.sh consume it directly.
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from math import lgamma, log, log2, pi, sqrt
from typing import List, Optional, Tuple

import numpy as np


# ----------------------------------------------------------------------------
# ridge / uniqueness estimators
# ----------------------------------------------------------------------------
def critical_log2D(n: int, m: int) -> float:
    return n / m - 0.5 * log2(pi * n / 6.0)


def ridge_D(n: int, m: int) -> int:
    return max(8, int(round(2.0 ** critical_log2D(n, m))))


def log2_expected_other_solutions(n: int, m: int, std_entry: float) -> float:
    sigma = sqrt(n) * max(std_entry, 1e-9)
    log2_p_row = -log2(sqrt(2 * pi) * sigma)
    log2_binom = (lgamma(n + 1) - 2 * lgamma(n // 2 + 1)) / log(2.0)
    return log2_binom + m * log2_p_row


def gaussian_heuristic_ratio(A: np.ndarray, n: int) -> float:
    """GH(kernel)/||y*||, ||y*||=sqrt(n).  Smaller => y* deeper => harder."""
    m = A.shape[0]
    Af = A.astype(np.float64)
    sign, logdet = np.linalg.slogdet(Af @ Af.T)
    if sign <= 0:
        return float("inf")
    d = n - m
    gh = sqrt(d / (2 * pi * math.e)) * math.exp((logdet / 2.0) / d)
    return gh / sqrt(n)


# ----------------------------------------------------------------------------
# tight-frame shaping: drive A toward A A^T = c I (all singular values equal)
# by single-entry moves, staying in [0, D).  Maximises det(A A^T) for the budget.
# ----------------------------------------------------------------------------
def balance_rows(A: np.ndarray, y: np.ndarray, D: int) -> np.ndarray:
    """Drive each row to EXACT midpoint balance a_i . y = 0 (=> b_i = rowsum_i/2,
    y* exactly in the kernel).  This collapses sd2's dual bounds -- standard
    market-split physics, applied here as a deterministic post-step.  Adjusts
    support (y=+1) and complement (y=-1) entries in opposite directions, 1 per
    unit of imbalance, staying in [0, D-1]."""
    A = A.astype(np.int64).copy()
    m, n = A.shape
    Sp = np.where(y > 0)[0]
    Sm = np.where(y < 0)[0]

    def absorb(i, cols, want, raise_):
        """Move `want` units across `cols` (raise toward D-1 if raise_ else lower
        toward 0). Returns units still unabsorbed."""
        for j in cols:
            if want <= 0:
                break
            if raise_:
                r = min(want, D - 1 - int(A[i, j]))
                A[i, j] += r
            else:
                r = min(want, int(A[i, j]))
                A[i, j] -= r
            want -= r
        return want

    for i in range(m):
        delta = int(A[i, Sp].sum() - A[i, Sm].sum())   # want == 0
        if delta > 0:        # remove delta from support, then (if needed) add to complement
            rem = absorb(i, Sp, delta, raise_=False)
            if rem > 0:
                rem = absorb(i, Sm, rem, raise_=True)
        elif delta < 0:      # add |delta| to support, then remove from complement
            rem = absorb(i, Sp, -delta, raise_=True)
            if rem > 0:
                rem = absorb(i, Sm, rem, raise_=False)
        # exact unless the entry budget [0,D-1] is too tight (then a tiny residual
        # remains; flagged by the caller's midpoint-gap report).
    return A


def balance_rows_free(A: np.ndarray, y: np.ndarray, D: int,
                      free: np.ndarray) -> np.ndarray:
    """Like balance_rows but adjusts ONLY the columns in `free` (a 1-D index
    array). Used by the decoy construction to restore the exact midpoint
    a_i . y = 0 WITHOUT disturbing the columns that carry planted decoy
    relations (those must stay fixed so A v_t = 0 holds)."""
    A = A.astype(np.int64).copy()
    m, _ = A.shape
    fy = y[free]
    Sp = free[np.where(fy > 0)[0]]
    Sm = free[np.where(fy < 0)[0]]

    def absorb(i, cols, want, raise_):
        for j in cols:
            if want <= 0:
                break
            if raise_:
                r = min(want, D - 1 - int(A[i, j])); A[i, j] += r
            else:
                r = min(want, int(A[i, j])); A[i, j] -= r
            want -= r
        return want

    for i in range(m):
        delta = int(A[i, np.where(y > 0)[0]].sum() - A[i, np.where(y < 0)[0]].sum())
        if delta > 0:
            rem = absorb(i, Sp, delta, raise_=False)
            if rem > 0:
                absorb(i, Sm, rem, raise_=True)
        elif delta < 0:
            rem = absorb(i, Sp, -delta, raise_=True)
            if rem > 0:
                absorb(i, Sm, rem, raise_=False)
    return A


def decoy_construct(n: int, m: int, D: int, rng: np.random.Generator,
                    n_decoys: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, list]:
    """DECOY-DENSE kernel construction (a NEW structural method, distinct from
    the v* family: no multiprime base, gadgets, anti-Hoelder permutation, or
    scramble; and distinct from the tight-frame/maxdet ortho modes).

    Rationale: at our cells GH(K)/||y*|| ~ 0.48, so sd2 is NOT doing unique-SVP
    on y* -- it enumerates short kernel vectors and tests each for 0/1
    feasibility. Hardness == how many SHORT non-solution decoy kernel vectors it
    must sift through. We therefore PLANT many short integer kernel relations
    v_t with A v_t = 0 exactly, each guaranteed NON-0/1 (so it is a pure decoy,
    never an alternate solution), lowering det(K) on purpose (opposite of
    maxdet) to pack the kernel with decoys.

    Each decoy uses 3 DISJOINT columns (i,k in the support, j in the complement):
        col_k := 2*col_i + col_j        =>  v_t = 2 e_i + e_j - e_k  in ker(A).
    The leading 2 e_i guarantees x* +/- v_t has an entry of 2 or -1 => infeasible
    => v_t is a pure decoy, never a rival 0/1 solution. Building-block columns
    col_i,col_j are drawn small (< D/4) so col_k = 2col_i+col_j < D stays in box.
    The exact midpoint a.y=0 is restored afterwards using only the FREE columns,
    leaving every planted relation intact.
    """
    x = np.zeros(n, dtype=np.int64)
    x[rng.choice(n, size=n // 2, replace=False)] = 1
    y = (2 * x - 1).astype(np.int64)
    S1 = list(np.where(x == 1)[0])
    S0 = list(np.where(x == 0)[0])
    rng.shuffle(S1); rng.shuffle(S0)

    A = rng.integers(0, D, size=(m, n), dtype=np.int64)

    decoys = []
    used = set()
    small_hi = max(2, D // 4)
    # need 2 support cols (i,k) + 1 complement col (j) per decoy, all disjoint
    max_by_supply = min(len(S1) // 2, len(S0))
    n_decoys = min(n_decoys, max_by_supply, n // 4)
    si = iter(S1); sj = iter(S0)
    for _ in range(n_decoys):
        try:
            i = next(si); k = next(si); j = next(sj)
        except StopIteration:
            break
        A[:, i] = rng.integers(0, small_hi, size=m)
        A[:, j] = rng.integers(0, small_hi, size=m)
        A[:, k] = 2 * A[:, i] + A[:, j]              # exact relation
        v = np.zeros(n, dtype=np.int64)
        v[i] = 2; v[j] = 1; v[k] = -1
        decoys.append(v)
        used.update((i, j, k))

    free = np.array([c for c in range(n) if c not in used], dtype=np.int64)
    A = balance_rows_free(A, y, D, free)             # exact midpoint, decoys untouched
    b = (A @ x).astype(np.int64)
    return A, b, x, decoys


def _paired_move(rng, Sp, Sm):
    """Return (i-cols) a same-sign pair of columns so a balance-preserving move
    (col_a -= s, col_b += s with both in Sp or both in Sm) keeps a_i . y = 0
    AND a_i . x* unchanged on Sp pairs."""
    grp = Sp if rng.random() < 0.5 else Sm
    if len(grp) < 2:
        grp = Sm if grp is Sp else Sp
    if len(grp) < 2:
        return None
    a, b = (int(t) for t in rng.choice(grp, size=2, replace=False))
    return a, b


def tight_frame_shape(A: np.ndarray, y: np.ndarray, D: int, rng: np.random.Generator,
                      iters: int = 8000) -> np.ndarray:
    """Stochastic minimisation of the singular-value spread (cond number) of A
    via BALANCE-PRESERVING paired moves (two same-sign columns, +/-s), so each
    move keeps a_i . y = 0 (midpoint preserved) while flattening the spectrum.
    Maximising det(A A^T) for the entry budget => deepest planted y*."""
    A = A.astype(np.int64).copy()
    m, n = A.shape
    Sp = np.where(y > 0)[0]
    Sm = np.where(y < 0)[0]

    def spread(M: np.ndarray) -> float:
        sv = np.linalg.svd(M.astype(np.float64), compute_uv=False)
        return float(log(sv[0] + 1e-12) - log(sv[-1] + 1e-12))

    cur = spread(A)
    for it in range(iters):
        pr = _paired_move(rng, Sp, Sm)
        if pr is None:
            break
        ca, cb = pr
        i = int(rng.integers(0, m))
        s = int(rng.choice((-1, 1)))
        if A[i, ca] - s < 0 or A[i, ca] - s > D - 1:
            continue
        if A[i, cb] + s < 0 or A[i, cb] + s > D - 1:
            continue
        A[i, ca] -= s
        A[i, cb] += s
        new = spread(A)
        if new <= cur:
            cur = new
        else:
            A[i, ca] += s
            A[i, cb] -= s
    return A


def _logdet_gram(M: np.ndarray) -> float:
    """log det(M M^T); -inf if singular. M is m x n with m <= n."""
    G = M.astype(np.float64)
    sign, logdet = np.linalg.slogdet(G @ G.T)
    return logdet if sign > 0 else float("-inf")


def maxdet_shape(A: np.ndarray, y: np.ndarray, D: int, rng: np.random.Generator,
                 iters: int = 12000, restarts: int = 1) -> np.ndarray:
    """Directly MAXIMISE log det(A A^T) via balance-preserving paired moves.

    Why this and not tight_frame_shape: GH(kernel) = sqrt(d/2*pi*e) *
    exp((logdet(A A^T)/2)/d), so logdet(A A^T) IS the planted-vector depth knob,
    exactly. Minimising the condition number (tight_frame_shape) is only a proxy
    and stalls on the all-ones/DC singular direction (Round-1 finding). Climbing
    logdet moves the WHOLE spectrum up subject to the entry budget, and because
    det is a product it keeps pushing even after the cond number flattens.

    Moves keep a_i . y = 0 (exact midpoint preserved) so the planted x* stays a
    solution. Greedy hill-climb with occasional random restart of the move pick;
    accepts strictly-improving (and ties) moves only."""
    A = A.astype(np.int64).copy()
    m, n = A.shape
    Sp = np.where(y > 0)[0]
    Sm = np.where(y < 0)[0]
    cur = _logdet_gram(A)
    for _ in range(iters):
        pr = _paired_move(rng, Sp, Sm)
        if pr is None:
            break
        ca, cb = pr
        i = int(rng.integers(0, m))
        # variable step: bigger jumps early help escape the DC-dominated basin
        smag = 1 + int(rng.integers(0, max(1, D // 200)))
        s = smag * int(rng.choice((-1, 1)))
        if A[i, ca] - s < 0 or A[i, ca] - s > D - 1:
            continue
        if A[i, cb] + s < 0 or A[i, cb] + s > D - 1:
            continue
        A[i, ca] -= s
        A[i, cb] += s
        new = _logdet_gram(A)
        if new >= cur:               # climb: deeper planted vector
            cur = new
        else:
            A[i, ca] += s
            A[i, cb] -= s
    return A


# ----------------------------------------------------------------------------
# float LLL on the kernel embedding (cheap GS-flatness surrogate, numpy only)
# ----------------------------------------------------------------------------
def _lll_float(B: np.ndarray, delta: float = 0.99,
               max_iters: int = 400000) -> Optional[np.ndarray]:
    B = B.astype(np.float64).copy()
    k = B.shape[0]
    mu = np.zeros((k, k))
    Bn = np.zeros(k)
    Bstar = np.zeros_like(B)
    for i in range(k):
        Bstar[i] = B[i].copy()
        for j in range(i):
            mu[i, j] = np.dot(B[i], Bstar[j]) / Bn[j]
            Bstar[i] -= mu[i, j] * Bstar[j]
        Bn[i] = float(np.dot(Bstar[i], Bstar[i]))
        if Bn[i] <= 0:
            return None
    kk, it = 1, 0
    while kk < k and it < max_iters:
        it += 1
        for j in range(kk - 1, -1, -1):
            if abs(mu[kk, j]) > 0.5:
                r = round(mu[kk, j])
                B[kk] -= r * B[j]
                mu[kk, :j] -= r * mu[j, :j]
                mu[kk, j] -= r
        if Bn[kk] >= (delta - mu[kk, kk - 1] ** 2) * Bn[kk - 1]:
            kk += 1
        else:
            mu_ = mu[kk, kk - 1]
            Bnew = Bn[kk] + mu_ * mu_ * Bn[kk - 1]
            if Bnew <= 0:
                return None
            mu[kk, kk - 1] = mu_ * Bn[kk - 1] / Bnew
            Bn[kk] = Bn[kk - 1] * Bn[kk] / Bnew
            Bn[kk - 1] = Bnew
            B[[kk - 1, kk]] = B[[kk, kk - 1]]
            if kk >= 2:
                tmp = mu[kk - 1, :kk - 1].copy()
                mu[kk - 1, :kk - 1] = mu[kk, :kk - 1]
                mu[kk, :kk - 1] = tmp
            for i in range(kk + 1, k):
                t = mu[i, kk]
                mu[i, kk] = mu[i, kk - 1] - mu_ * t
                mu[i, kk - 1] = t + mu[kk, kk - 1] * mu[i, kk]
            kk = max(kk - 1, 1)
    return Bn


def gs_flatness(A: np.ndarray, n_scale: float = 1e3) -> Optional[float]:
    """abs(GSA slope) of the LLL-reduced kernel embedding; smaller = flatter =
    harder.  Returns None on numerical failure."""
    m, n = A.shape
    B = np.zeros((n, n + m), dtype=np.float64)
    B[:, :n] = np.eye(n)
    B[:, n:] = float(n_scale) * A.T.astype(np.float64)
    sq = _lll_float(B)
    if sq is None or np.any(sq <= 0):
        return None
    logs = 0.5 * np.log(sq)
    idx = np.arange(len(logs))
    slope = float(np.polyfit(idx, logs, 1)[0])
    return abs(slope)


def lll_refine(A: np.ndarray, x: np.ndarray, D: int, rng: np.random.Generator,
               iters: int = 1500) -> np.ndarray:
    """Feasibility-preserving moves accepted iff they flatten the kernel GS
    profile (lower abs slope).  A move changes two entries in ONE row, on a
    support column and a complement column by the SAME signed amount, so that
    a_i . y* is unchanged (=> b = A x* unchanged, x* stays a solution).
    Wait: a_i . y* changes by step*(y_j_supp - y_k_comp) = step*(+1 - (-1))
    = 2*step != 0.  To keep a_i . x* fixed we instead move a support col DOWN by
    s and another support col UP by s (both x=1): net change to row dot x* = 0.
    Likewise two complement cols cancel trivially.  We use support/support pairs.
    """
    A = A.astype(np.int64).copy()
    S = np.where(x == 1)[0]
    base = gs_flatness(A)
    if base is None:
        return A
    cur = base
    m, n = A.shape
    for _ in range(iters):
        i = int(rng.integers(0, m))
        if len(S) < 2:
            break
        j, k = (int(t) for t in rng.choice(S, size=2, replace=False))
        s = int(rng.choice((-1, 1))) * int(rng.integers(1, max(2, D // 50)))
        if A[i, j] - s < 0 or A[i, j] - s > D - 1:
            continue
        if A[i, k] + s < 0 or A[i, k] + s > D - 1:
            continue
        A[i, j] -= s
        A[i, k] += s
        f = gs_flatness(A)
        if f is not None and f <= cur:
            cur = f
        else:
            A[i, j] += s
            A[i, k] -= s
    return A


# ----------------------------------------------------------------------------
# uniqueness guard
# ----------------------------------------------------------------------------
def random_uniqueness_search(A: np.ndarray, b: np.ndarray, x: np.ndarray,
                             rng: np.random.Generator, samples: int = 40000) -> int:
    n = A.shape[1]
    k = int(x.sum())
    xt = tuple(int(v) for v in x)
    xc = tuple(int(1 - v) for v in x)
    unexpected = 0
    for _ in range(samples):
        idx = rng.choice(n, size=k, replace=False)
        xx = np.zeros(n, dtype=np.int64)
        xx[idx] = 1
        if np.array_equal(A @ xx, b):
            t = tuple(int(v) for v in xx)
            if t != xt and t != xc:
                unexpected += 1
    return unexpected


# ----------------------------------------------------------------------------
# construction
# ----------------------------------------------------------------------------
def generate_one(n: int, m: int, D: int, seed: int, band: float,
                 tf_iters: int, lll: bool,
                 maxdet: bool = False, decoy: bool = False,
                 n_decoys: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)

    # DECOY-DENSE structural mode: distinct construction, returns immediately.
    if decoy:
        k = n_decoys if n_decoys is not None else max(4, n // 6)
        A, b, x, _ = decoy_construct(n, m, D, rng, k)
        return A, b, x

    # balanced planted solution
    x = np.zeros(n, dtype=np.int64)
    x[rng.choice(n, size=n // 2, replace=False)] = 1

    y = (2 * x - 1).astype(np.int64)

    # mid/high-band base: entries in [lo, D) -> no tiny entries for the solver's
    # gcd / "entries too small" preprocessing to exploit; uniform magnitude.
    lo = int(round(band * D))
    A = rng.integers(lo, D, size=(m, n), dtype=np.int64)

    # exact midpoint (a_i . y = 0 => kills dual bounds), then spectral shaping
    # via balance-preserving paired moves.
    A = balance_rows(A, y, D)
    if maxdet:
        # directly climb log det(A A^T) -- the exact planted-depth/GH knob;
        # beats cond-number minimisation below the kernel ceiling.
        A = maxdet_shape(A, y, D, rng, iters=tf_iters)
    else:
        A = tight_frame_shape(A, y, D, rng, iters=tf_iters)
    A = balance_rows(A, y, D)        # restore exactness after shaping (no-op if clean)

    if lll:
        A = lll_refine(A, x, D, rng)
        A = balance_rows(A, y, D)

    b = (A @ x).astype(np.int64)
    return A, b, x


def writes(outdir: str, name: str, A: np.ndarray, b: np.ndarray, x: np.ndarray,
           log_lines: List[str]) -> None:
    d = os.path.join(outdir, name)
    os.makedirs(d, exist_ok=True)
    m, n = A.shape
    with open(os.path.join(d, "instance.txt"), "w") as f:
        f.write(f"{m} {n}\n")
        for i in range(m):
            f.write(" ".join(str(int(v)) for v in A[i]) + "\n")
        f.write("b\n")
        f.write(" ".join(str(int(v)) for v in b) + "\n")
        f.write("x_star\n")
        f.write(" ".join(str(int(v)) for v in x) + "\n")
    P = sorted(int(j) for j in np.where(x == 1)[0])
    N = sorted(int(j) for j in np.where(x == 0)[0])
    with open(os.path.join(d, "solution.txt"), "w") as f:
        f.write("x_star\n" + " ".join(str(int(v)) for v in x) + "\n")
        f.write("P\n" + " ".join(map(str, P)) + "\n")
        f.write("N\n" + " ".join(map(str, N)) + "\n")
    with open(os.path.join(d, "gen.log"), "w") as f:
        f.write("\n".join(log_lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="tight-frame / max-determinant market-split generator")
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--m", type=int, required=True)
    ap.add_argument("--D", type=int, default=None, help="max entry (excl). default: uniqueness-ridge D")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--band", type=float, default=0.0,
                    help="entries in [band*D, D). 0 => full range U[0,D). e.g. 0.5 => high band")
    ap.add_argument("--tf-iters", type=int, default=6000, help="shaping moves")
    ap.add_argument("--maxdet", action="store_true",
                    help="maximise log det(A A^T) directly (deeper planted y*; "
                         "better below the kernel ceiling) instead of cond-number")
    ap.add_argument("--decoy", action="store_true",
                    help="DECOY-DENSE structural mode: plant many short non-0/1 "
                         "kernel relations to clutter enumeration (distinct from v*)")
    ap.add_argument("--n-decoys", type=int, default=None,
                    help="number of planted decoy relations (default ~n/6)")
    ap.add_argument("--lll-refine", action="store_true", help="add LLL GS-flatness refinement")
    ap.add_argument("--max-uniqueness", type=float, default=2.0)
    ap.add_argument("--feas-samples", type=int, default=40000)
    ap.add_argument("--outdir", type=str, default="market_split_ortho")
    args = ap.parse_args()

    if args.n % 2 != 0:
        print(f"NOTE: odd n={args.n} (planted x* uses {args.n // 2} ones)")
    if args.m >= args.n:
        sys.exit("ERROR: need m < n")
    D = args.D if args.D is not None else ridge_D(args.n, args.m)

    log_lines: List[str] = []

    def emit(s: str = "") -> None:
        print(s); log_lines.append(s)

    emit("=" * 64)
    emit("MARKET-SPLIT ortho (tight-frame / max-determinant) generator")
    emit("=" * 64)
    emit(f"n={args.n} m={args.m} D={D} seed={args.seed} band={args.band}")
    emit(f"kernel dim d = n-m = {args.n - args.m}   (beta<=75 ceiling: want d >~ 76)")
    emit(f"ridge D (E~=1) = {ridge_D(args.n, args.m)}   critical log2D={critical_log2D(args.n, args.m):.2f}")
    emit("")

    A, b, x = generate_one(args.n, args.m, D, args.seed, args.band, args.tf_iters,
                           args.lll_refine, maxdet=args.maxdet,
                           decoy=args.decoy, n_decoys=args.n_decoys)

    assert np.array_equal(A @ x, b), "feasibility broken"
    assert A.min() >= 0 and A.max() <= D - 1, "entry bound broken"

    std_entry = float(A.std())
    log2E = log2_expected_other_solutions(args.n, args.m, std_entry)
    gh = gaussian_heuristic_ratio(A, args.n)
    flat = gs_flatness(A)

    emit(f"entry range [{int(A.min())}, {int(A.max())}]  std={std_entry:.1f}")
    cn = np.linalg.norm(A.astype(np.float64), axis=0)
    emit(f"column-norm ratio max/min = {cn.max()/(cn.min()+1e-12):.4f}")
    sv = np.linalg.svd(A.astype(np.float64), compute_uv=False)
    emit(f"singular values: max={sv[0]:.1f} min={sv[-1]:.1f} cond={sv[0]/(sv[-1]+1e-12):.3f}")
    emit(f"GH(kernel)/||y*|| = {gh:.4f}   (smaller=deeper=harder)")
    emit(f"LLL GS-flatness |slope| = {flat if flat is None else round(flat,4)}  (smaller=flatter=harder)")
    emit(f"log2 E[# other solutions] = {log2E:.2f}")
    rs = A.sum(axis=1).astype(np.float64)
    gap = np.abs(b.astype(np.float64) - rs / 2.0)
    emit(f"LP-midpoint gap |b - rowsum/2|: max={gap.max():.1f}")

    if log2E > args.max_uniqueness:
        emit(f"WARNING: log2E={log2E:.2f} exceeds max_uniqueness={args.max_uniqueness} (may be non-unique)")
    unexpected = random_uniqueness_search(A, b, x, np.random.default_rng(args.seed ^ 0x9E3779B9),
                                          samples=args.feas_samples)
    emit(f"random uniqueness search: {unexpected} alt solution(s) found")
    if unexpected > 0:
        emit("WARNING: instance appears NON-UNIQUE; consider larger D or different seed")

    name = f"n{args.n}_m{args.m}_hi{D}_seed{args.seed}"
    writes(args.outdir, name, A, b, x, log_lines)
    print(f"\nwrote -> {os.path.join(args.outdir, name)}")


if __name__ == "__main__":
    main()
