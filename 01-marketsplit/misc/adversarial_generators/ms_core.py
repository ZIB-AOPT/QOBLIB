#!/usr/bin/env python3
"""
ms_core.py -- shared machinery for the structural market-split generators
(v5/v6/v7). Factored from generate_market_split_v4.py so the variants differ
ONLY in their structural construction step, making the comparison a clean
ablation. v4 itself is kept self-contained as the frozen baseline.

Find x in {0,1}^n  s.t.  A x = b,  A in [0, D-1]^{m x n}, b in Z_>=0^m.

Provides:
  - ridge / hardness estimators (critical D, density, log2 E, GH ratio)
  - the solver-free hardness proxy (logdet + sigma_min)
  - reusable construction STEPS (plant, multiprime base, gadgets, anti-LDS
    correlations, column-norm equalization, row balance, scramble/permute)
  - uniqueness guardrail (random feasible search)
  - validation + writers for the instances/ folder layout
  - add_common_args() and select_and_write(): the over-generate-and-select
    driver shared by every variant.

Each variant supplies a generate_one(n, m, D, seed, args) -> Instance and calls
ms_core.select_and_write(...). See generate_market_split_v5.py for the pattern.
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from dataclasses import dataclass, field
from functools import reduce
from math import gcd, lgamma, log, log2, pi, sqrt
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np


# ======================================================================
# Number theory (multi-prime modular base)
# ======================================================================

def is_prime(v: int) -> bool:
    if v < 2:
        return False
    if v < 4:
        return True
    if v % 2 == 0 or v % 3 == 0:
        return False
    r, d = 0, v - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if a >= v:
            continue
        x = pow(a, d, v)
        if x == 1 or x == v - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, v)
            if x == v - 1:
                break
        else:
            return False
    return True


def find_primes_in_range(lo: int, hi: int, count: int) -> List[int]:
    out: List[int] = []
    c = lo + 1
    while len(out) < count and c <= hi:
        if is_prime(c):
            out.append(c)
        c += 1
    return out


def prime_factors(v: int) -> List[int]:
    factors = []
    d = 2
    while d * d <= v:
        if v % d == 0:
            factors.append(d)
            while v % d == 0:
                v //= d
        d += 1
    if v > 1:
        factors.append(v)
    return factors


def smallest_primitive_root(p: int) -> int:
    if p == 2:
        return 1
    phi = p - 1
    fac = prime_factors(phi)
    for g in range(2, p):
        if all(pow(g, phi // q, p) != 1 for q in fac):
            return g
    raise ValueError(f"no primitive root for p={p}")


# ======================================================================
# Ridge / hardness estimators
# ======================================================================

def critical_log2D(n: int, m: int) -> float:
    """log2(D) at the uniqueness transition E[# other binary sols] ~= 1."""
    return n / m - 0.5 * log2(pi * n / 6.0)


def pick_D(n: int, m: int, delta: Optional[float]) -> int:
    if delta is not None and delta > 0:
        log2D = n / (m * delta)
    else:
        log2D = critical_log2D(n, m)
    return max(8, int(round(2.0 ** log2D)))


def density_delta(n: int, m: int, D: int) -> float:
    return n / (m * log2(D))


def log2_expected_other_solutions(n: int, m: int, std_entry: float) -> float:
    sigma = sqrt(n) * max(std_entry, 1e-9)
    log2_p_row = -log2(sqrt(2 * pi) * sigma)
    log2_binom = (lgamma(n + 1) - 2 * lgamma(n // 2 + 1)) / log(2.0)
    return log2_binom + m * log2_p_row


def gaussian_heuristic_ratio(A: np.ndarray, n: int) -> float:
    """GH(kernel lattice)/||y*||, ||y*||=sqrt(n). <~0.85 => hard for BKZ."""
    m = A.shape[0]
    Af = A.astype(np.float64)
    # Some rejected intermediate candidates can overflow this diagnostic even
    # though the final integer instance is bounded by D.  The score already
    # treats a non-positive/non-finite determinant as unusable, so keep the
    # regeneration log quiet and let that existing guard handle it.
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        sign, logdet_ATA = np.linalg.slogdet(Af @ Af.T)
    if sign <= 0 or not math.isfinite(logdet_ATA):
        return float("inf")
    d = n - m
    gh = sqrt(d / (2 * pi * math.e)) * math.exp((logdet_ATA / 2.0) / d)
    return gh / sqrt(n)


def hardness_proxy(A: np.ndarray, b: np.ndarray, lam: float = 1.0) -> Dict[str, float]:
    """score = logdet([A|b][A|b]^T)/m + lam*log(sigma_min(A))."""
    Af = A.astype(np.float64)
    M = np.concatenate([Af, b.astype(np.float64)[:, None]], axis=1)
    m = A.shape[0]
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        sign, logdet = np.linalg.slogdet(M @ M.T)
    logdet_term = (logdet / m) if sign > 0 and math.isfinite(logdet) else -1e18
    sv = np.linalg.svd(Af, compute_uv=False)
    sigma_min = float(sv[-1])
    log_sigma_min = log(sigma_min) if sigma_min > 0 else -1e9
    return {
        "score": logdet_term + lam * log_sigma_min,
        "logdet_per_dim": logdet_term,
        "sigma_min": sigma_min,
        "cond": float(sv[0] / (sv[-1] + 1e-15)),
    }


# ======================================================================
# Optional: pure-numpy float LLL (used by v7 as a selection signal)
# ======================================================================

def kernel_lattice_profile(A: np.ndarray, n_scale: float = 1e3,
                           delta: float = 0.99) -> Optional[Dict[str, float]]:
    """Build an approximate reduced basis of the kernel lattice {v: A v = 0} via
    the scaled embedding [ I_n | n_scale * A^T ] (LLL pushes the last m
    coordinates to ~0, recovering near-kernel vectors), float-LLL it, and report
    Gram-Schmidt-profile statistics.

    A FLAT GS profile is the worst case for enumeration. Returns None if LLL
    fails numerically. Intended as a cheap selection signal, NOT exact.
    """
    m, n = A.shape
    B = np.zeros((n, n + m), dtype=np.float64)
    B[:, :n] = np.eye(n)
    B[:, n:] = float(n_scale) * A.T.astype(np.float64)
    try:
        Bred, sq_gs = _lll_float(B, delta=delta)
    except Exception:
        return None
    if sq_gs is None or np.any(sq_gs <= 0):
        return None
    logs = 0.5 * np.log(sq_gs)
    idx = np.arange(len(logs))
    slope = float(np.polyfit(idx, logs, 1)[0])
    ker_norms = np.linalg.norm(Bred[:, :n], axis=1)
    return {
        "gsa_slope_abs": abs(slope),
        "gs_log_std": float(np.std(logs)),
        "min_kernel_norm": float(np.min(ker_norms)),
        "flatness": -abs(slope),   # bigger (closer to 0) = flatter = harder
    }


def _lll_float(B: np.ndarray, delta: float = 0.99,
               max_iters: int = 500000) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Incremental-GSO float LLL (textbook, with Lovasz swap updates). Adequate
    as a heuristic signal for dim ~60. Returns (reduced B, squared GS norms)."""
    B = B.astype(np.float64).copy()
    k = B.shape[0]
    mu = np.zeros((k, k))
    Bn = np.zeros(k)              # squared GS norms ||b_i*||^2

    # Initial full GSO.
    Bstar = np.zeros_like(B)
    for i in range(k):
        Bstar[i] = B[i].copy()
        for j in range(i):
            mu[i, j] = np.dot(B[i], Bstar[j]) / Bn[j]
            Bstar[i] -= mu[i, j] * Bstar[j]
        Bn[i] = float(np.dot(Bstar[i], Bstar[i]))
        if Bn[i] <= 0:
            return B, None

    kk = 1
    it = 0
    while kk < k and it < max_iters:
        it += 1
        # size-reduce b_kk against b_{kk-1..0}
        for j in range(kk - 1, -1, -1):
            if abs(mu[kk, j]) > 0.5:
                r = round(mu[kk, j])
                B[kk] -= r * B[j]
                mu[kk, :j] -= r * mu[j, :j]
                mu[kk, j] -= r
        if Bn[kk] >= (delta - mu[kk, kk - 1] ** 2) * Bn[kk - 1]:
            kk += 1
        else:
            # Lovasz swap of kk-1 and kk with incremental GSO update.
            mu_ = mu[kk, kk - 1]
            Bnew = Bn[kk] + mu_ * mu_ * Bn[kk - 1]
            if Bnew <= 0:
                return B, None
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
    return B, Bn


# ======================================================================
# Construction steps (reusable across variants)
# ======================================================================

@dataclass
class Instance:
    A: np.ndarray
    b: np.ndarray
    x_star: np.ndarray
    y_star: np.ndarray
    P: List[int]
    N: List[int]
    meta: dict = field(default_factory=dict)


def plant(n: int, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    w = n // 2
    x = np.zeros(n, dtype=np.int64)
    x[rng.choice(n, size=w, replace=False)] = 1
    return x, np.where(x == 1)[0], np.where(x == 0)[0]


def multiprime_base(n: int, m: int, D: int, rng: np.random.Generator) -> np.ndarray:
    K = max(1, math.ceil(m / 2))
    primes = find_primes_in_range(D, 3 * D, K)
    if len(primes) < K:
        half = D // 2
        bw = max(2, D // 3)
        return rng.integers(max(0, half - bw), min(D, half + bw) + 1, size=(m, n)).astype(np.int64)
    roots = [smallest_primitive_root(p) for p in primes]
    offs = [int(rng.integers(0, p - 1)) for p in primes]
    A = np.zeros((m, n), dtype=np.int64)
    for i in range(m):
        k = i * K // m
        p, g, w = primes[k], roots[k], offs[k]
        l = (i - (k * m // K)) + 1
        em = 2 * l - 1
        for j in range(n):
            A[i, j] = pow(g, ((j + 1) + w) * em, p) % D
    return A


def inject_correlations(A: np.ndarray, S: np.ndarray, num_pairs: int,
                        D: int, rng: np.random.Generator) -> int:
    m = A.shape[0]
    Ssh = rng.permutation(S)
    npairs = min(num_pairs, len(Ssh) // 2)
    for p in range(npairs):
        ja, jb = int(Ssh[2 * p]), int(Ssh[2 * p + 1])
        xi = rng.integers(-1, 2, size=m)
        newcol = np.floor((A[:, ja].astype(np.float64) + 3.0 * A[:, jb].astype(np.float64)) / 4.0).astype(np.int64) + xi
        A[:, jb] = np.clip(newcol, 0, D - 1)
    return npairs


def inject_gadgets(A: np.ndarray, S: np.ndarray, Sbar: np.ndarray, Q: int, h: int,
                   D: int, rng: np.random.Generator, noise_override: Optional[int] = None,
                   without_replacement: bool = True) -> List[dict]:
    """Spread gadgets: set complement columns ~= mean of support columns
    (+/- small nonzero noise) -> low-norm near-kernel +/-1 directions."""
    m = A.shape[0]
    noise = noise_override if noise_override is not None else max(1, int(math.floor(D ** 0.25)))
    Sa, Sba = list(S), list(Sbar)
    rng.shuffle(Sa)
    rng.shuffle(Sba)
    sp = sm = 0
    gadgets = []
    for _ in range(Q):
        if sp + h > len(Sa):
            rng.shuffle(Sa); sp = 0
        if sm + h > len(Sba):
            rng.shuffle(Sba); sm = 0
        Sp = Sa[sp:sp + h]
        Sm = Sba[sm:sm + h]
        if without_replacement:
            sp += h; sm += h
        else:
            sp += 1; sm += 1
        mean_plus = A[:, Sp].mean(axis=1)
        for j in Sm:
            eta = rng.integers(-noise, noise + 1, size=m)
            eta[eta == 0] = 1
            A[:, j] = np.clip(np.floor(mean_plus).astype(np.int64) + eta, 0, D - 1)
        gadgets.append({"S_plus": [int(x) for x in Sp], "S_minus": [int(x) for x in Sm]})
    return gadgets


def equalize_columns(A: np.ndarray, D: int, target_ratio: float = 1.1,
                     max_iters: int = 40000, rng: Optional[np.random.Generator] = None) -> np.ndarray:
    if rng is None:
        rng = np.random.default_rng(0)
    norms = np.linalg.norm(A.astype(np.float64), axis=0)
    hi_b = lo_b = np.median(norms)
    for it in range(max_iters):
        if it % 50 == 0:
            norms = np.linalg.norm(A.astype(np.float64), axis=0)
            if norms.max() / (norms.min() + 1e-10) <= target_ratio:
                break
            med = np.median(norms)
            hi_b, lo_b = 1.05 * med, 0.95 * med
        high = np.where(norms > hi_b)[0]
        low = np.where(norms < lo_b)[0]
        if len(high) == 0 and len(low) == 0:
            break
        for j in high[:3]:
            cand = np.where(A[:, j] > 0)[0]
            if len(cand):
                i = rng.choice(cand); A[i, j] -= 1
                norms[j] = np.linalg.norm(A[:, j].astype(np.float64))
        for j in low[:3]:
            cand = np.where(A[:, j] < D - 1)[0]
            if len(cand):
                i = rng.choice(cand); A[i, j] += 1
                norms[j] = np.linalg.norm(A[:, j].astype(np.float64))
    return A


def row_balance(A: np.ndarray, x: np.ndarray, D: int, rng: np.random.Generator,
                max_iters: int = 40000) -> np.ndarray:
    """Approximate LP-midpoint balance: |sum_S a - sum_Sbar a| <= sqrt(n)."""
    m, n = A.shape
    thr = sqrt(n)
    S = np.where(x == 1)[0]
    Sbar = np.where(x == 0)[0]
    for _ in range(max_iters):
        delta = A[:, S].sum(axis=1).astype(np.float64) - A[:, Sbar].sum(axis=1).astype(np.float64)
        viol = np.where(np.abs(delta) > thr)[0]
        if len(viol) == 0:
            break
        i = int(rng.choice(viol))
        if delta[i] > thr:
            dec = S[A[i, S] > 0]; inc = Sbar[A[i, Sbar] < D - 1]
            if len(dec):
                A[i, int(rng.choice(dec))] -= 1
            if len(inc):
                A[i, int(rng.choice(inc))] += 1
        else:
            inc = S[A[i, S] < D - 1]; dec = Sbar[A[i, Sbar] > 0]
            if len(inc):
                A[i, int(rng.choice(inc))] += 1
            if len(dec):
                A[i, int(rng.choice(dec))] -= 1
    return A


def exact_lp_midpoint(A: np.ndarray, x: np.ndarray, D: int,
                      rng: np.random.Generator, max_iters: int = 200000) -> np.ndarray:
    """Drive each row to EXACT balance sum_S a_ij = sum_Sbar a_ij (i.e.
    a_i . y* = 0, so b_i = (1/2) rowsum_i exactly), keeping entries in [0,D-1].

    This makes x=1/2 an EXACT LP vertex over a large face -> the solver's dual
    bounds collapse. Adjusts one support and one complement entry per step in
    opposite directions (preserves nothing about Ax* until b is recomputed by
    the caller -- callers set b = A x* afterwards)."""
    m, n = A.shape
    S = np.where(x == 1)[0]
    Sbar = np.where(x == 0)[0]
    for _ in range(max_iters):
        delta = (A[:, S].sum(axis=1) - A[:, Sbar].sum(axis=1)).astype(np.int64)
        worst = int(np.argmax(np.abs(delta)))
        if delta[worst] == 0 and np.all(delta == 0):
            break
        d = int(delta[worst])
        if d == 0:
            # pick any nonzero row
            nz = np.where(delta != 0)[0]
            if len(nz) == 0:
                break
            worst = int(nz[0]); d = int(delta[worst])
        step = 1 if d > 0 else -1
        # reduce |delta[worst]| by 2 per move (one support down/up, one comp up/down)
        if d > 0:
            dec = S[A[worst, S] > 0]
            inc = Sbar[A[worst, Sbar] < D - 1]
        else:
            dec = Sbar[A[worst, Sbar] > 0]
            inc = S[A[worst, S] < D - 1]
        moved = False
        if len(dec):
            A[worst, int(rng.choice(dec))] -= 1; moved = True
        if len(inc) and abs(d) >= 2:
            A[worst, int(rng.choice(inc))] += 1; moved = True
        if not moved:
            break
    return A


def make_rows_magnitude_uniform(A: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Anti-Hoelder: give every row the SAME multiset of entry magnitudes (a
    common profile), so no row yields a tighter Hoelder bound. Each row becomes
    a random permutation of that common profile.

    The profile is sampled from the FULL matrix entry distribution (n values),
    preserving the wide magnitude spread -- using compressed column medians would
    shrink the per-entry std and inflate E[# other solutions], breaking
    uniqueness. Returns a NEW matrix; caller must re-balance afterwards."""
    m, n = A.shape
    flat = A.reshape(-1)
    profile = np.sort(rng.choice(flat, size=n, replace=(flat.size < n)).astype(np.int64))
    out = np.zeros_like(A)
    for i in range(m):
        out[i, rng.permutation(n)] = profile
    return out


def scramble_and_permute(A: np.ndarray, x: np.ndarray, D: int,
                         rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    m, n = A.shape
    A = A[rng.permutation(m)]
    for _ in range(5 * m * m):
        i1, i2 = int(rng.integers(0, m)), int(rng.integers(0, m))
        if i1 == i2:
            continue
        lam = int(rng.choice([-1, 1]))
        c = int(rng.choice([2, 3, 4]))
        newrow = A[i2] + lam * (A[i1] // c)
        if np.all(newrow >= 0) and np.all(newrow <= D - 1):
            A[i2] = newrow
    sigma = rng.permutation(n)
    return A[:, sigma], x[sigma], sigma


def random_uniqueness_search(A: np.ndarray, b: np.ndarray, x: np.ndarray,
                             rng: np.random.Generator, samples: int = 60000) -> int:
    m, n = A.shape
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


# ======================================================================
# Validation
# ======================================================================

def validate(inst: Instance, D: int) -> bool:
    A, b, x = inst.A, inst.b, inst.x_star
    m, n = A.shape
    if b.shape != (m,) or x.shape != (n,):
        return False
    if not np.all((x == 0) | (x == 1)):
        return False
    if A.min() < 0 or A.max() > D - 1:
        return False
    if b.min() < 0:
        return False
    return np.array_equal(A @ x, b)


def row_gcd_with_rhs(row: np.ndarray, rhs: int) -> int:
    return reduce(gcd, [int(abs(v)) for v in row] + [int(abs(rhs))])


# ======================================================================
# Writers (instances/ folder layout)
# ======================================================================

def write_txt(path: str, A: np.ndarray, b: np.ndarray, x: np.ndarray) -> None:
    m, n = A.shape
    with open(path, "w") as f:
        f.write(f"{m} {n}\n")
        for i in range(m):
            f.write(" ".join(str(int(v)) for v in A[i]) + "\n")
        f.write("b\n")
        f.write(" ".join(str(int(v)) for v in b) + "\n")
        f.write("x_star\n")
        f.write(" ".join(str(int(v)) for v in x) + "\n")


def write_solution(path: str, x: np.ndarray, P: List[int], N: List[int]) -> None:
    with open(path, "w") as f:
        f.write("x_star\n")
        f.write(" ".join(str(int(v)) for v in x) + "\n")
        f.write("P\n")
        f.write(" ".join(str(j) for j in P) + "\n")
        f.write("N\n")
        f.write(" ".join(str(j) for j in N) + "\n")


def write_lp(path: str, A: np.ndarray, b: np.ndarray, banner: str) -> None:
    m, n = A.shape
    with open(path, "w") as f:
        f.write(f"\\ {banner}\n")
        f.write("Minimize\n obj: 0 x0\nSubject To\n")
        for i in range(m):
            terms = [f"{int(A[i, j])} x{j}" for j in range(n)]
            f.write(f" c{i}: " + " + ".join(terms) + f" = {int(b[i])}\n")
        f.write("Binary\n")
        for j in range(n):
            f.write(f" x{j}\n")
        f.write("End\n")


def write_npz(path: str, inst: Instance) -> None:
    np.savez_compressed(
        path,
        A=inst.A.astype(np.int64), b=inst.b.astype(np.int64),
        x_star=inst.x_star.astype(np.int64), y_star=inst.y_star.astype(np.int64),
        P=np.array(inst.P, dtype=np.int64), N=np.array(inst.N, dtype=np.int64),
    )


def write_all(outdir: str, inst: Instance, banner: str, log_lines: List[str]) -> None:
    os.makedirs(outdir, exist_ok=True)
    write_txt(os.path.join(outdir, "instance.txt"), inst.A, inst.b, inst.x_star)
    write_solution(os.path.join(outdir, "solution.txt"), inst.x_star, inst.P, inst.N)
    write_lp(os.path.join(outdir, "instance.lp"), inst.A, inst.b, banner)
    write_npz(os.path.join(outdir, "instance_npz.npz"), inst)
    with open(os.path.join(outdir, "gen.log"), "w") as f:
        f.write("\n".join(log_lines) + "\n")


# ======================================================================
# Over-generate-and-select driver (shared by all variants)
# ======================================================================

def add_common_args(ap: argparse.ArgumentParser, default_m: int = 5) -> None:
    ap.add_argument("--n", type=int, default=60, help="variables (even). default 60")
    ap.add_argument("--m", type=int, default=default_m, help=f"constraints. default {default_m}")
    ap.add_argument("--D", type=int, default=None, help="max entry (exclusive). default: critical D (E~=1)")
    ap.add_argument("--delta", type=float, default=None, help="target density n/(m log2 D)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--candidates", type=int, default=16,
                    help="over-generate K, keep best by proxy. default 16")
    ap.add_argument("--lam", type=float, default=1.0, help="weight on log(sigma_min) in the proxy")
    ap.add_argument("--gadgets", type=int, default=None, help="spread-gadget count (default n/6)")
    ap.add_argument("--gadget-half", type=int, default=None, help="gadget half-weight (default floor sqrt n)")
    ap.add_argument("--corr-pairs", type=int, default=None, help="anti-LDS pairs (default n/8)")
    ap.add_argument("--max-uniqueness", type=float, default=2.0,
                    help="reject if log2 E[# other] exceeds this (default 2.0)")
    ap.add_argument("--feas-samples", type=int, default=40000,
                    help="random feasible-search samples for the uniqueness guardrail")
    ap.add_argument("--outdir", type=str, default="market_split_out")


def resolve_params(args) -> int:
    # Odd n is allowed (planted x* simply uses floor(n/2) ones; y*=2x*-1 then has
    # sum +/-1 but a_i . y* = 0 is still achievable, so exact midpoint still works).
    # Odd n lets us hit kernel dims n-m between the even values -- e.g. n=83,m=4 ->
    # kernel 79, the SAME kernel as the hardest v* hits (n84,m5) but at n<84.
    if args.n % 2 != 0:
        print(f"NOTE: odd n={args.n} (planted x* uses {args.n // 2} ones)")
    if args.m >= args.n:
        sys.exit("ERROR: need m < n")
    return args.D if args.D is not None else pick_D(args.n, args.m, args.delta)


def select_and_write(args, generate_one: Callable[..., Instance], variant_name: str,
                     banner: str, extra_proxy: Optional[Callable[[Instance], Dict[str, float]]] = None,
                     extra_banner_lines: Optional[List[str]] = None) -> None:
    """Run the over-generate-and-select loop and write the winning instance.

    generate_one(n, m, D, seed, args) -> Instance.
    extra_proxy(inst) -> dict with at least a 'score_bonus' float added to the
        base proxy score (e.g. v7's LLL flatness signal), plus any fields to log.
    """
    D = resolve_params(args)
    log_lines: List[str] = []

    def emit(s: str = "") -> None:
        print(s)
        log_lines.append(s)

    emit("=" * 64)
    emit(f"MARKET-SPLIT {variant_name}")
    emit("=" * 64)
    emit(f"n={args.n}  m={args.m}  D={D}")
    emit(f"kernel dimension: {args.n - args.m}")
    emit(f"density delta = {density_delta(args.n, args.m, D):.3f}   "
         f"(critical log2 D={critical_log2D(args.n, args.m):.2f}, actual={log2(D):.2f})")
    emit(f"||y_star|| = sqrt(n) = {sqrt(args.n):.2f}")
    for ln in (extra_banner_lines or []):
        emit(ln)
    emit(f"over-generate-and-select: {args.candidates} candidate(s)")
    emit("")

    rng_master = np.random.default_rng(args.seed)
    best: Optional[Tuple[float, Instance, dict]] = None
    n_ok = n_rej = 0

    for c in range(args.candidates):
        cseed = int(rng_master.integers(0, 2**63 - 1))
        inst = generate_one(args.n, args.m, D, cseed, args)
        if not validate(inst, D):
            emit(f"  cand {c:3d} seed={cseed}: INVALID (A x* != b) -- skipped")
            continue

        std_entry = float(inst.A.std())
        log2E = log2_expected_other_solutions(args.n, args.m, std_entry)
        proxy = hardness_proxy(inst.A, inst.b, lam=args.lam)
        gh = gaussian_heuristic_ratio(inst.A, args.n)

        bonus = 0.0
        extra_fields: Dict[str, float] = {}
        if extra_proxy is not None:
            xp = extra_proxy(inst)
            bonus = float(xp.get("score_bonus", 0.0))
            extra_fields = {k: v for k, v in xp.items() if k != "score_bonus"}
        score = proxy["score"] + bonus

        unexpected = -1
        if log2E <= args.max_uniqueness:
            unexpected = random_uniqueness_search(
                inst.A, inst.b, inst.x_star,
                np.random.default_rng(cseed ^ 0x9E3779B9), samples=args.feas_samples)

        if log2E > args.max_uniqueness:
            tag = f"REJECT log2E={log2E:.1f}"; n_rej += 1
        elif unexpected > 0:
            tag = f"REJECT {unexpected} alt"; n_rej += 1
        else:
            tag = "ok"; n_ok += 1

        extra_str = " ".join(f"{k}={v:.3f}" for k, v in extra_fields.items())
        emit(f"  cand {c:3d} seed={cseed}: score={score:.3f} "
             f"logdet/m={proxy['logdet_per_dim']:.2f} sig_min={proxy['sigma_min']:.0f} "
             f"GH/||y||={gh:.3f} log2E={log2E:.1f} {extra_str} [{tag}]")

        if tag != "ok":
            continue
        meta = {**inst.meta, "seed": cseed, "log2E": log2E, "gh_ratio": gh,
                "score": score, **proxy, **extra_fields}
        if best is None or score > best[0]:
            best = (score, inst, meta)

    emit("")
    if best is None:
        emit("FATAL: no unique candidate passed the guardrail. Try more --candidates, "
             "a larger --m, or a smaller --delta (raise D).")
        os.makedirs(args.outdir, exist_ok=True)
        with open(os.path.join(args.outdir, "gen.log"), "w") as f:
            f.write("\n".join(log_lines) + "\n")
        sys.exit(2)

    score, inst, meta = best
    emit("=" * 64)
    emit("SELECTED INSTANCE")
    emit("=" * 64)
    emit(f"seed={meta['seed']}  proxy score={score:.4f}")
    emit(f"logdet([A|b][A|b]^T)/m = {meta['logdet_per_dim']:.4f}")
    emit(f"sigma_min(A) = {meta['sigma_min']:.2f}   cond(A) = {meta['cond']:.2e}")
    emit(f"GH/||y_star|| = {meta['gh_ratio']:.3f}   "
         f"({'hard (<0.85)' if meta['gh_ratio'] < 0.85 else 'borderline'})")
    emit(f"log2 E[# other solutions] = {meta['log2E']:.2f}  (unique)")
    cn = np.linalg.norm(inst.A.astype(np.float64), axis=0)
    emit(f"column-norm ratio max/min = {cn.max()/(cn.min()+1e-10):.4f}  (CV={cn.std()/cn.mean():.4f})")
    rs = inst.A.sum(axis=1).astype(np.float64)
    gap = np.abs(inst.b.astype(np.float64) - rs / 2.0)
    emit(f"LP-midpoint gap |b - rowsum/2|: max={gap.max():.1f}  "
         f"(exact balance => 0; threshold D*sqrt(n)/4 = {D*sqrt(args.n)/4:.1f})")
    emit(f"entry range [{int(inst.A.min())}, {int(inst.A.max())}]  std={inst.A.std():.1f}")
    for k, v in meta.items():
        if k in ("seed", "log2E", "gh_ratio", "score", "logdet_per_dim", "sigma_min", "cond"):
            continue
        if isinstance(v, (int, float)):
            emit(f"{k} = {v}")
    emit(f"candidates: {n_ok} unique-ok, {n_rej} rejected")
    emit("")
    emit("NOTE: proxy is solver-free. Confirm hardness by racing this folder")
    emit("through the CCC harness (bkz/pbkz x beta{10..75} x lds20).")

    write_all(args.outdir, inst, banner, log_lines)
    print(f"\nwrote instance files -> {args.outdir}")
