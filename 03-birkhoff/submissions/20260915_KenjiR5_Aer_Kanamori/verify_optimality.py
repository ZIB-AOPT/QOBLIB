#!/usr/bin/env python3
"""Public-only exact certificates for the 21 R5 Birkhoff submissions.

Reads only public QOBLIB instance matrices and submitted solution files.
No estimator internals, measurements, or reference solutions are used.
"""
from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
PROBLEM = HERE.parent.parent
GROUPS = (
    ("qbench_03_sparse.json", tuple(f"B3_3_{i}" for i in range(1, 11))),
    ("qbench_03_dense.json", tuple(f"B3_9_{i}" for i in range(1, 11))),
    ("qbench_04_sparse.json", ("B4_4_5",)),
)


def permutation_column(p):
    n = len(p)
    column = [0] * (n * n)
    for row, col in enumerate(p):
        column[row * n + col] = 1
    return column


def independent_nonnegative_solution(columns, target):
    """Exact rational solution for independent permutation columns, if feasible.

    Dependent feasible supports are never minimal: a convex combination with
    affine dependence can be reduced to a proper support, since every
    permutation matrix has the same entry sum.
    """
    k = len(columns)
    m = len(target)
    a = [
        [Fraction(columns[c][r]) for c in range(k)] + [Fraction(target[r])]
        for r in range(m)
    ]
    pivots = []
    row = 0
    for col in range(k):
        pivot = next((i for i in range(row, m) if a[i][col]), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        d = a[row][col]
        a[row] = [v / d for v in a[row]]
        for i in range(m):
            if i == row or not a[i][col]:
                continue
            factor = a[i][col]
            a[i] = [a[i][j] - factor * a[row][j] for j in range(k + 1)]
        pivots.append(col)
        row += 1
    if any(not any(a[i][c] for c in range(k)) and a[i][k] for i in range(m)):
        return None
    if len(pivots) < k:
        return None
    weights = [Fraction(0) for _ in range(k)]
    for r, col in enumerate(pivots):
        weights[col] = a[r][k]
    return weights if all(w >= 0 for w in weights) else None


def verify(instance, solution):
    ident = instance["id"]
    assert solution["id"] == ident, ident
    n, scale = instance["n"], instance["scale"]
    target = instance["scaled_doubly_stochastic_matrix"]
    assert target == solution["scaled_doubly_stochastic_matrix"], ident
    k = len(solution["weights"])
    assert k > 0 and len(solution["permutations"]) == k * n, ident
    assert solution.get("k", k) == k, ident
    assert solution.get("scale", scale) == scale, ident
    assert sum(solution["weights"]) == scale, ident
    assert all(isinstance(w, int) and w > 0 for w in solution["weights"]), ident

    submitted = []
    for i in range(k):
        p = solution["permutations"][i * n:(i + 1) * n]
        assert sorted(p) == list(range(1, n + 1)), ident
        submitted.append(permutation_column(tuple(x - 1 for x in p)))
    reconstructed = [
        sum(solution["weights"][i] * submitted[i][j] for i in range(k))
        for j in range(n * n)
    ]
    assert reconstructed == target, f"{ident}: submitted solution mismatch"

    all_columns = [permutation_column(p) for p in permutations(range(n))]
    for size in range(1, k):
        for chosen in combinations(all_columns, size):
            if independent_nonnegative_solution(chosen, target) is not None:
                raise AssertionError(
                    f"{ident}: feasible decomposition with {size} < {k} permutations"
                )
    print(f"{ident}: submitted={k}, proven optimum={k} PASS")
    return k


def main():
    count = 0
    for filename, identifiers in GROUPS:
        instances = json.loads((PROBLEM / "instances" / filename).read_text())
        by_id = {v["id"]: v for v in instances.values() if isinstance(v, dict) and "id" in v}
        for ident in identifiers:
            solution_file = HERE / ident / (ident + "_solution.json")
            submissions = json.loads(solution_file.read_text())
            record = next(v for v in submissions.values() if v["id"] == ident)
            verify(by_id[ident], record)
            count += 1
    assert count == 21, count
    print(f"PASS: {count}/21 public-instance optimality certificates")


if __name__ == "__main__":
    main()
