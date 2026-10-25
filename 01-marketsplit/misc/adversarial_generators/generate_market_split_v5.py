#!/usr/bin/env python3
"""
generate_market_split_v5.py -- "exact + pruning-hardened" structural variant.

Same skeleton as v4 (multi-prime magnitudes, spread gadgets, anti-LDS pairs,
column-norm equalization, over-generate-and-select), but adds three
deterministic, solver-attacking construction levers:

  1. EXACT LP-midpoint (kills dual bounds).
     b_i = (1/2) * rowsum_i EXACTLY, enforced via a_i . y* = 0 per row
     (support-sum == complement-sum). x = 1/2 is then an exact LP vertex over a
     large face, so solvediophant's `Dual bounds` collapse to ~0 -- there is no
     LP signal telling enumeration which way to branch. (The analysis's
     "single most effective" amplifier; v4 only balanced to within sqrt(n).)

  2. PER-ROW MAGNITUDE UNIFORMITY (kills Hoelder pruning).
     Every row is a permutation of one common magnitude profile, so no row
     yields a tighter Hoelder bound than another. `Prune_hoelder` -- a top
     contributor in the solver telemetry -- loses its asymmetry to exploit.

  3. Exact midpoint also maximally defeats LDS: the LP relaxation is 1/2
     everywhere, so the rounded/greedy guess carries no information and limited-
     discrepancy search must explore deep (high lds_k).

Tradeoff vs v4: the transvection scramble is replaced by permutation-only
scrambling (row + column permutations), which preserves both exact balance and
per-row magnitude uniformity. There is no multi-prime block structure to hide
because the base is overwritten by the uniform-magnitude profile.

Run:
    python generate_market_split_v5.py --n 60 --m 5 --candidates 16 --seed 1 --outdir out
"""

from __future__ import annotations

import argparse

import numpy as np

import ms_core as core

BANNER = "Market split feasibility instance (v5 - exact LP-midpoint + anti-Hoelder)"


def generate_one(n: int, m: int, D: int, seed: int, args) -> core.Instance:
    rng = np.random.default_rng(seed)
    Q = args.gadgets if args.gadgets is not None else n // 6
    h = args.gadget_half if args.gadget_half is not None else int(np.floor(np.sqrt(n)))
    P_pairs = args.corr_pairs if args.corr_pairs is not None else n // 8

    x, S, Sbar = core.plant(n, rng)

    # Base: multi-prime magnitudes, then force every row to be a permutation of
    # one common magnitude profile (anti-Hoelder).
    A = core.multiprime_base(n, m, D, rng)
    A = core.make_rows_magnitude_uniform(A, rng)

    core.inject_correlations(A, S, P_pairs, D, rng)
    gadgets = core.inject_gadgets(A, S, Sbar, Q, h, D, rng)
    core.equalize_columns(A, D, rng=rng)

    # EXACT LP-midpoint last so balance is exact (b = rowsum/2).
    A = core.exact_lp_midpoint(A, x, D, rng)

    # Permutation-only scramble (preserves exact balance + row magnitude sets).
    A = A[rng.permutation(m)]
    sigma = rng.permutation(n)
    A = A[:, sigma]
    x = x[sigma]
    b = (A @ x).astype(np.int64)

    S = np.where(x == 1)[0]
    Sbar = np.where(x == 0)[0]
    y = (2 * x - 1).astype(np.int64)

    meta = {
        "gadgets": len(gadgets), "gadget_half": h, "corr_pairs": P_pairs,
        "exact_midpoint_gap": int(np.max(np.abs(b.astype(np.int64) - A.sum(axis=1) // 2))),
    }
    return core.Instance(A=A, b=b, x_star=x, y_star=y,
                         P=sorted(int(j) for j in S), N=sorted(int(j) for j in Sbar),
                         meta=meta)


def main() -> None:
    ap = argparse.ArgumentParser(description="v5: exact LP-midpoint + anti-Hoelder market-split generator.")
    core.add_common_args(ap, default_m=5)
    args = ap.parse_args()
    core.select_and_write(
        args, generate_one, variant_name="v5 (exact LP-midpoint + anti-Hoelder)",
        banner=BANNER,
        extra_banner_lines=["levers: EXACT b=rowsum/2, per-row magnitude uniformity, gadgets"])


if __name__ == "__main__":
    main()
