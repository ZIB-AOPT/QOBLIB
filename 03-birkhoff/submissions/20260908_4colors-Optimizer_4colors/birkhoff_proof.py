#!/usr/bin/env python3
# Marcin Kaminski, 4colors Research.
# SPDX-License-Identifier: Apache-2.0
"""Optimality certificates for QOBLIB 03-birkhoff.

Standalone: the Python standard library only, no project imports, no solver
bindings, no code shared with our heuristics.

A valid decomposition writes the scaled matrix D as a non-negative combination
of permutation matrices, and every term of such a combination must be a perfect
matching of the support of D: a term placing weight on a zero cell could never
be cancelled, since all weights are non-negative.  The set of admissible columns
is therefore finite and, at the sizes handled here, small enough to list in
full.  Optimality of an incumbent of size k then reduces to a single question -
is there a combination of at most k-1 of those columns? - and a negative answer
is a proof.

This script does four things:

  enumerate   list every perfect matching of the support
  ryser       independently count them with Ryser's permanent formula
  lp          write the "at most k-1 columns" feasibility model as a .lp file,
              so any MILP solver can answer it; infeasible means k is optimal
  exact       for n = 3, answer the same question by exhaustive enumeration over
              every subset of columns in exact rational arithmetic, no solver

Usage:
    birkhoff_proof.py <instances.json> <instance-id> [--k K] [--lp FILE]
    birkhoff_proof.py <instances.json> --all --k-from <solutions.json>
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from itertools import combinations


# --------------------------------------------------------------------------
def load(path: str, inst_id: str | None = None):
    with open(path) as fh:
        blob = json.load(fh)
    entries = blob.values() if isinstance(blob, dict) else blob
    out = {}
    for e in entries:
        if not isinstance(e, dict) or "id" not in e:
            continue
        n = e["n"]
        flat = e["scaled_doubly_stochastic_matrix"]
        e["D"] = [flat[i * n:(i + 1) * n] for i in range(n)]
        out[e["id"]] = e
    return out[inst_id] if inst_id else out


def perfect_matchings(D):
    """Every permutation whose every cell of D is positive, as column tuples."""
    n = len(D)
    out, col = [], [0] * n

    def rec(row, used):
        if row == n:
            out.append(tuple(col))
            return
        for j in range(n):
            if not (used >> j) & 1 and D[row][j] > 0:
                col[row] = j
                rec(row + 1, used | (1 << j))
    rec(0, 0)
    return out


def ryser_permanent(D):
    """Permanent of the 0/1 support matrix, by Ryser's inclusion-exclusion.

        per(A) = (-1)^n * sum_{S subset of columns} (-1)^{|S|} prod_i sum_{j in S} A[i][j]

    Exact integer arithmetic throughout.  For a 0/1 matrix the permanent counts
    the perfect matchings, so it is an independent check on the enumeration.
    """
    n = len(D)
    A = [[1 if D[i][j] > 0 else 0 for j in range(n)] for i in range(n)]
    total = 0
    for mask in range(1 << n):
        prod = 1
        for i in range(n):
            s = 0
            for j in range(n):
                if (mask >> j) & 1:
                    s += A[i][j]
            prod *= s
            if prod == 0:
                break
        if prod:
            total += (-1) ** bin(mask).count("1") * prod
    return total * (-1) ** n


# --------------------------------------------------------------------------
def write_lp(D, perms, k, path):
    """Feasibility model: can D be written with at most k columns?

    x_p  weight given to column p, continuous, >= 0
    y_p  1 if column p is used
    reconstruction   sum_p x_p [p hits (i,j)] = D[i][j]     for every cell
    linking          x_p <= cap_p * y_p,  cap_p = min cell of D under p
    cardinality      sum_p y_p <= k

    cap_p is the largest weight column p could ever carry, since it cannot take
    more than the smallest entry it sits on.  The model has no objective: it is
    posed purely as a feasibility question, and INFEASIBLE is the certificate.
    """
    n = len(D)
    caps = [min(D[i][p[i]] for i in range(n)) for p in perms]
    with open(path, "w") as fh:
        fh.write("\\* at most %d permutation matrices *\\\n" % k)
        fh.write("Minimize\n obj: 0\nSubject To\n")
        for i in range(n):
            for j in range(n):
                terms = [f"x{t}" for t, p in enumerate(perms) if p[i] == j]
                if terms:
                    fh.write(f" r{i}_{j}: " + " + ".join(terms) + f" = {D[i][j]}\n")
                elif D[i][j]:
                    fh.write(f"\\* cell {i},{j} is positive but no column covers it *\\\n")
        for t, cap in enumerate(caps):
            fh.write(f" l{t}: x{t} - {cap} y{t} <= 0\n")
        fh.write(" card: " + " + ".join(f"y{t}" for t in range(len(perms))) + f" <= {k}\n")
        fh.write("Bounds\n")
        for t in range(len(perms)):
            fh.write(f" 0 <= x{t} <= {caps[t]}\n")
        fh.write("Binaries\n " + " ".join(f"y{t}" for t in range(len(perms))) + "\nEnd\n")
    return len(perms), sum(caps)


def exhaustive(D, perms, k):
    """Is there a combination of at most k columns?  Exact, solver-free.

    Only tractable for the smallest instances: it enumerates every subset of
    size k and solves the resulting equality system in rationals by elimination
    over the cells each column touches.  Returns a witness or None.
    """
    n = len(D)
    cells = [(i, j) for i in range(n) for j in range(n) if D[i][j] > 0]
    for subset in combinations(range(len(perms)), k):
        cols = [perms[t] for t in subset]
        # Each positive cell must be covered; build the linear system.
        rows = []
        for (i, j) in cells:
            coef = [1 if c[i] == j else 0 for c in cols]
            if not any(coef):
                break
            rows.append((coef, Fraction(D[i][j])))
        else:
            sol = solve_exact(rows, len(cols))
            if sol is not None and all(v >= 0 for v in sol):
                # every zero cell must stay zero
                ok = all(sum(sol[a] for a, c in enumerate(cols) if c[i] == j) == 0
                         for i in range(n) for j in range(n) if D[i][j] == 0)
                if ok:
                    return list(zip(subset, sol))
    return None


def solve_exact(rows, nvars):
    """Least-structure Gaussian elimination in Fractions; None if inconsistent."""
    m = [list(map(Fraction, coef)) + [rhs] for coef, rhs in rows]
    piv = []
    r = 0
    for c in range(nvars):
        p = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        inv = m[r][c]
        m[r] = [v / inv for v in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        piv.append(c)
        r += 1
        if r == len(m):
            break
    for i in range(r, len(m)):
        if all(v == 0 for v in m[i][:nvars]) and m[i][nvars] != 0:
            return None
    if len(piv) < nvars:
        return None                      # underdetermined: not a unique witness
    sol = [Fraction(0)] * nvars
    for i, c in enumerate(piv):
        sol[c] = m[i][nvars]
    return sol


# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("instances")
    ap.add_argument("instance_id", nargs="?")
    ap.add_argument("--k", type=int, help="incumbent size; the model asks for k-1")
    ap.add_argument("--lp", help="write the feasibility model here")
    ap.add_argument("--exact", action="store_true", help="solver-free replication (n = 3)")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args(argv)

    data = load(a.instances)
    ids = sorted(data) if a.all else [a.instance_id]
    for iid in ids:
        e = data[iid]
        D = e["D"]
        perms = perfect_matchings(D)
        per = ryser_permanent(D)
        agree = "agrees" if per == len(perms) else f"DISAGREES (Ryser {per})"
        print(f"{iid}: n={e['n']} scale={e['scale']} columns={len(perms)}  Ryser {agree}")
        if a.k and a.lp:
            cols, _ = write_lp(D, perms, a.k - 1, a.lp)
            print(f"  wrote {a.lp}: {cols} binary columns, cardinality <= {a.k - 1}")
        if a.k and a.exact:
            w = exhaustive(D, perms, a.k - 1)
            print(f"  exhaustive over all {a.k - 1}-subsets: "
                  + ("witness found, NOT optimal" if w else f"none exists, {a.k} is optimal"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
