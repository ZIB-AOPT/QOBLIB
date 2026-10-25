#!/usr/bin/env python3
"""Generate a QC-lifted frozen XOR-3 instance in the compact MIS encoding.

The Tanner graph is a cyclic lift of the K_3,3 protograph.  The lift shifts are
selected from 60 deterministic candidates by maximizing the measured Tanner
girth.  There are three variable groups, three constraint groups, and ``L``
vertices per group.  Each XOR constraint becomes a K4 of its four satisfying
local assignments; incompatible assignments in different K4s are joined.

The K4s cover the MIS graph and the planted assignment selects one vertex per
K4, proving alpha = 3L.  Arguments: L seed [tag].
"""

from __future__ import annotations

import random
import sys
from collections import Counter, deque
from itertools import combinations, product
from pathlib import Path


L = int(sys.argv[1])
SEED = int(sys.argv[2])
TAG = sys.argv[3] if len(sys.argv) > 3 else f"qc_v2_L{L}_s{SEED}"
VARIABLE_GROUPS = 3
CONSTRAINT_GROUPS = 3
N = VARIABLE_GROUPS * L
M = CONSTRAINT_GROUPS * L


def variable_id(group: int, offset: int) -> int:
    return group * L + offset


def constraint_id(group: int, offset: int) -> int:
    return group * L + offset


def build_clauses(shifts: dict[tuple[int, int], int]) -> list[list[int]]:
    constraints = {c: [] for c in range(M)}
    for variable_group in range(VARIABLE_GROUPS):
        for constraint_group in range(CONSTRAINT_GROUPS):
            shift = shifts[(variable_group, constraint_group)]
            for offset in range(L):
                constraints[constraint_id(constraint_group, offset)].append(
                    variable_id(variable_group, (offset + shift) % L)
                )
    return [sorted(constraints[c]) for c in range(M)]


def tanner_girth(clauses: list[list[int]]) -> int:
    variable_adjacency: dict[int, list[int]] = {}
    for clause_index, clause in enumerate(clauses):
        for variable in clause:
            variable_adjacency.setdefault(variable, []).append(clause_index)

    def neighbors(node: tuple[str, int]) -> list[tuple[str, int]]:
        kind, index = node
        if kind == "v":
            return [("c", c) for c in variable_adjacency.get(index, [])]
        return [("v", v) for v in clauses[index]]

    girth = 999
    for start_index in range(min(N, 60)):
        start = ("v", start_index)
        distance = {start: 0}
        parent = {start: None}
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for adjacent in neighbors(node):
                if adjacent not in distance:
                    distance[adjacent] = distance[node] + 1
                    parent[adjacent] = node
                    queue.append(adjacent)
                elif parent[node] != adjacent:
                    girth = min(girth, distance[node] + distance[adjacent] + 1)
        if girth <= 4:
            break
    return girth


best = None
for candidate in range(60):
    rng = random.Random(SEED * 7919 + candidate)
    shifts = {
        (variable_group, constraint_group): rng.randrange(L)
        for variable_group in range(VARIABLE_GROUPS)
        for constraint_group in range(CONSTRAINT_GROUPS)
    }
    clauses = build_clauses(shifts)
    if any(len(set(clause)) != 3 for clause in clauses):
        continue
    girth = tanner_girth(clauses)
    if best is None or girth > best[0]:
        best = (girth, clauses)

if best is None:
    raise RuntimeError("no valid cyclic lift found")

girth, clauses = best
plant_rng = random.Random(SEED)
planted_assignment = [plant_rng.randint(0, 1) for _ in range(N)]
satisfying_assignments = []
for clause in clauses:
    parity = sum(planted_assignment[v] for v in clause) & 1
    satisfying_assignments.append(
        [assignment for assignment in product((0, 1), repeat=3) if (sum(assignment) & 1) == parity]
    )


def vertex_id(clause_index: int, assignment_index: int) -> int:
    return clause_index * 4 + assignment_index


edges: set[tuple[int, int]] = set()


def add_edge(left: int, right: int) -> None:
    if left != right:
        edges.add((min(left, right), max(left, right)))


for clause_index in range(M):
    for left, right in combinations(range(4), 2):
        add_edge(vertex_id(clause_index, left), vertex_id(clause_index, right))

occurrences: dict[int, list[tuple[int, int]]] = {}
for clause_index, clause in enumerate(clauses):
    for position, variable in enumerate(clause):
        occurrences.setdefault(variable, []).append((clause_index, position))

for occurrences_of_variable in occurrences.values():
    for (clause_1, position_1), (clause_2, position_2) in combinations(occurrences_of_variable, 2):
        for assignment_1, tuple_1 in enumerate(satisfying_assignments[clause_1]):
            for assignment_2, tuple_2 in enumerate(satisfying_assignments[clause_2]):
                if tuple_1[position_1] != tuple_2[position_2]:
                    add_edge(vertex_id(clause_1, assignment_1), vertex_id(clause_2, assignment_2))

independent_set = [
    vertex_id(
        clause_index,
        satisfying_assignments[clause_index].index(
            tuple(planted_assignment[v] for v in clause)
        ),
    )
    for clause_index, clause in enumerate(clauses)
]

output_dir = Path("logs/xor_lab")
output_dir.mkdir(parents=True, exist_ok=True)
with (output_dir / f"{TAG}.dimacs").open("w") as output:
    output.write(f"p edge {4 * M} {len(edges)}\n")
    for left, right in sorted(edges):
        output.write(f"e {left + 1} {right + 1}\n")
(output_dir / f"{TAG}.sol").write_text(
    " ".join(str(vertex + 1) for vertex in independent_set) + "\n"
)
(output_dir / f"{TAG}.clauses").write_text(
    "\n".join(" ".join(map(str, clause)) for clause in clauses) + "\n"
)

degrees = Counter()
for left, right in edges:
    degrees[left] += 1
    degrees[right] += 1
conflicts = sum(
    1
    for left, right in combinations(sorted(independent_set), 2)
    if (left, right) in edges
)
print(
    f"{TAG}: n={4 * M} m={len(edges)} alpha*={M} N={N} L={L} "
    f"girth={girth} planted_internal={conflicts} "
    f"min_deg={min(degrees.values())}"
)
