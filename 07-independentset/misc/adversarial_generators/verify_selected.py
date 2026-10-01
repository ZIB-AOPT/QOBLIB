#!/usr/bin/env python3
"""Verify selected MIS solutions and the XORSAT clique-cover certificates."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CASES = {
    "aheg_n99_s31": (7, None),
    "hybrid_csp_spinglass_n180_s42": (15, None),
    "frozen_xorsat_c3k3_compact_n700": (175, ("compact", 175)),
    "frozen_xorsat_c3k3_compact_n800": (200, ("compact", 200)),
    "frozen_xorsat_c3k3_compact_n1000": (250, ("compact", 250)),
    "frozen_xorsat_c3k3_compact_n1200": (300, ("compact", 300)),
    "frozen_xorsat_c3k3_regular_n1500": (500, ("regular", 250)),
    "frozen_xorsat_v2_qc_l75_s1": (225, ("compact", 225)),
    "frozen_xorsat_v2_qc_l100_s4": (300, ("compact", 300)),
    "frozen_xorsat_v2_qc_l125_s1": (375, ("compact", 375)),
}


def read_graph(path: Path) -> tuple[int, set[tuple[int, int]]]:
    n = declared_edges = None
    edges: set[tuple[int, int]] = set()
    for raw in path.read_text().splitlines():
        fields = raw.split()
        if not fields or fields[0] == "c":
            continue
        if fields[0] == "p":
            n, declared_edges = int(fields[2]), int(fields[3])
        elif fields[0] == "e":
            u, v = int(fields[1]), int(fields[2])
            if u == v:
                raise ValueError(f"self-loop in {path}: {u}")
            edges.add((min(u, v), max(u, v)))
    if n is None or declared_edges != len(edges):
        raise ValueError(f"bad DIMACS header in {path}")
    return n, edges


def require_clique(block: list[int], edges: set[tuple[int, int]], name: str) -> None:
    for u, v in combinations(block, 2):
        if (min(u, v), max(u, v)) not in edges:
            raise ValueError(f"{name}: certificate block is not a clique ({u}, {v})")


def main() -> None:
    for name, (optimum, certificate) in CASES.items():
        graph_path = ROOT / "07-independentset" / "instances" / f"{name}.gph"
        solution_path = ROOT / "07-independentset" / "solutions" / f"{name}.opt.sol"
        n, edges = read_graph(graph_path)
        solution = [int(value) for value in solution_path.read_text().split() if not value.startswith("#")]
        if len(solution) != optimum or len(set(solution)) != optimum:
            raise ValueError(f"{name}: expected {optimum} distinct solution vertices")
        if any(v < 1 or v > n for v in solution):
            raise ValueError(f"{name}: solution vertex outside 1..{n}")
        chosen = set(solution)
        if any(u in chosen and v in chosen for u, v in edges):
            raise ValueError(f"{name}: proposed solution is not independent")

        proof = "feasible; exact-solver certificate documented separately"
        if certificate:
            family, parameter = certificate
            blocks: list[list[int]] = []
            if family == "compact":
                blocks = [list(range(4 * i + 1, 4 * i + 5)) for i in range(parameter)]
            else:
                variable_count = parameter
                blocks.extend([[2 * i + 1, 2 * i + 2] for i in range(variable_count)])
                base = 2 * variable_count
                blocks.extend([list(range(base + 4 * i + 1, base + 4 * i + 5)) for i in range(variable_count)])
            if sorted(v for block in blocks for v in block) != list(range(1, n + 1)):
                raise ValueError(f"{name}: clique cover does not partition all vertices")
            for block in blocks:
                require_clique(block, edges, name)
            if len(blocks) != optimum:
                raise ValueError(f"{name}: clique-cover upper bound differs from solution size")
            proof = f"alpha={optimum} by independent set plus {len(blocks)}-clique vertex cover"
        print(f"OK {name}: n={n}, |E|={len(edges)}, {proof}")


if __name__ == "__main__":
    main()
