#!/usr/bin/env python3
"""Exact Birkhoff--von Neumann decomposition benchmarks for QOBLIB.

The solver preserves integer residuals throughout.  It supports two constructive
policies: maximum total residual weight (``largest_weight``) and maximum
bottleneck weight (``max_min``).  Both extract a positive perfect matching and
subtract its smallest selected residual, so the output is an exact convex
decomposition of every input matrix.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment


def positive_perfect_matching(residual: np.ndarray, policy: str) -> np.ndarray:
    """Return a perfect matching using only positive entries of ``residual``."""
    n = residual.shape[0]
    largest = int(residual.max())
    forbidden = n * largest + 1

    if policy == "largest_weight":
        cost = np.where(residual > 0, -residual, forbidden)
        rows, cols = linear_sum_assignment(cost)
        assert np.all(residual[rows, cols] > 0)
        return cols

    if policy not in {
        "max_min",
        "max_min_zero_max",
        "max_min_low_sum",
        "max_min_zero_low_sum",
    }:
        raise ValueError(f"Unknown policy: {policy}")

    values = np.unique(residual[residual > 0])
    low, high = 0, len(values) - 1
    best: np.ndarray | None = None
    while low <= high:
        middle = (low + high) // 2
        threshold = values[middle]
        allowed = residual >= threshold
        cost = np.where(allowed, 0, 1)
        if policy == "max_min_zero_max":
            cost = np.where(allowed, (residual > threshold).astype(int), forbidden)
        elif policy == "max_min_low_sum":
            cost = np.where(allowed, residual, forbidden)
        elif policy == "max_min_zero_low_sum":
            zero_priority = n * largest + 1
            forbidden = (n + 1) * zero_priority + largest
            cost = np.where(
                allowed,
                (residual > threshold).astype(np.int64) * zero_priority + residual,
                forbidden,
            )
        rows, cols = linear_sum_assignment(cost)
        if np.all(allowed[rows, cols]):
            best = cols
            low = middle + 1
        else:
            high = middle - 1
    assert best is not None
    return best


def decompose(instance: dict[str, object], policy: str) -> tuple[list[int], list[list[int]]]:
    """Build an exact integer decomposition and validate its reconstruction."""
    n = int(instance["n"])
    target = np.asarray(instance["scaled_doubly_stochastic_matrix"], dtype=np.int64)
    target = target.reshape(n, n)
    residual = target.copy()
    weights: list[int] = []
    permutations: list[list[int]] = []

    while np.any(residual):
        permutation = positive_perfect_matching(residual, policy)
        chosen = residual[np.arange(n), permutation]
        weight = int(chosen.min())
        assert weight > 0
        residual[np.arange(n), permutation] -= weight
        weights.append(weight)
        permutations.append((permutation + 1).tolist())

    reconstructed = np.zeros_like(target)
    for weight, permutation in zip(weights, permutations, strict=True):
        reconstructed[np.arange(n), np.asarray(permutation) - 1] += weight
    assert np.array_equal(reconstructed, target)
    assert sum(weights) == int(instance["scale"])
    return weights, permutations


def solve_file(input_path: Path, output_path: Path, policy: str) -> None:
    payload = json.loads(input_path.read_text())
    solutions: dict[str, dict[str, object]] = {}
    for key, instance in payload.items():
        if key == "_license":
            continue
        started = time.perf_counter()
        weights, permutations = decompose(instance, policy)
        elapsed = time.perf_counter() - started
        instance_id = str(instance["id"])
        print(f"{instance_id}\tterms={len(weights)}\tseconds={elapsed:.3f}")
        solutions[key] = {
            "id": instance_id,
            "scaled_doubly_stochastic_matrix": instance["scaled_doubly_stochastic_matrix"],
            "weights": weights,
            "permutations": [entry for permutation in permutations for entry in permutation],
        }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(solutions, separators=(",", ":")) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--policy",
        choices=(
            "largest_weight",
            "max_min",
            "max_min_zero_max",
            "max_min_low_sum",
            "max_min_zero_low_sum",
        ),
        default="largest_weight",
    )
    arguments = parser.parse_args()
    solve_file(arguments.input, arguments.output, arguments.policy)


if __name__ == "__main__":
    main()
