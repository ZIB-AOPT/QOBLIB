#!/usr/bin/env python3
"""Generate a complete QOBLIB submission for the open dense Birkhoff cases."""

from __future__ import annotations

import csv
import json
import subprocess
import time
from pathlib import Path

from benchmark_birkhoff import decompose


SUBMISSION_DATE = "2026-08-17"
SUBMITTER = "Manan Gupta"
AFFILIATION = "Independent Researcher"
POLICY = "max_min_zero_low_sum"
HARDWARE = "Apple MacBook Pro with Apple M3 Pro, 11 CPU cores, 18 GB unified memory"
SUMMARY_COLUMNS = [
    "Problem", "Submitter", "Affiliation", "Date", "Reference",
    "Best Objective Value", "Optimality Bound", "Modeling Approach",
    "# Decision Variables", "# Binary Variables", "# Integer Variables",
    "# Continuous Variables", "# Non-Zero Coefficients", "Coefficients Type",
    "Coefficients Range", "Workflow", "Algorithm Type", "Paradigm", "# Runs",
    "# Feasible Runs", "# Successful Runs", "Success Threshold",
    "Hardware Specifications", "Total Runtime", "Time to Solution", "CPU Runtime",
    "GPU Runtime", "QPU Runtime", "Other HW Runtime", "Remarks",
]


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def reference_url(root: Path) -> str:
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, check=True, text=True, capture_output=True
    ).stdout.strip()
    return f"https://github.com/mnn31/QOBLIB/tree/{revision}/experiments/birkhoff"


def write_instance(
    instance_key: str,
    instance: dict[str, object],
    destination: Path,
    reference: str,
) -> tuple[str, int, float]:
    started = time.perf_counter()
    weights, permutations = decompose(instance, POLICY)
    elapsed = time.perf_counter() - started
    instance_id = str(instance["id"])
    n = int(instance["n"])
    destination.mkdir(parents=True, exist_ok=True)

    solution = {
        instance_key: {
            "id": instance_id,
            "scaled_doubly_stochastic_matrix": instance["scaled_doubly_stochastic_matrix"],
            "weights": weights,
            "permutations": [value for permutation in permutations for value in permutation],
        }
    }
    (destination / f"{instance_id}_solution.json").write_text(
        json.dumps(solution, separators=(",", ":")) + "\n"
    )

    term_count = len(weights)
    row = {
        "Problem": instance_id,
        "Submitter": SUBMITTER,
        "Affiliation": AFFILIATION,
        "Date": SUBMISSION_DATE,
        "Reference": reference,
        "Best Objective Value": term_count,
        "Optimality Bound": "N/A",
        "Modeling Approach": "Exact integer Birkhoff decomposition using bottleneck perfect matchings.",
        "# Decision Variables": term_count * (n + 1),
        "# Binary Variables": term_count * n,
        "# Integer Variables": term_count,
        "# Continuous Variables": 0,
        "# Non-Zero Coefficients": 2 * n,
        "Coefficients Type": "Binary and integer",
        "Coefficients Range": f"1 to {int(instance['scale'])}",
        "Workflow": (
            "At each iteration, maximize the smallest residual selected by a perfect "
            "matching. Within that threshold, maximize eliminated entries and then "
            "minimize the matching residual sum. Subtract the selected minimum exactly."
        ),
        "Algorithm Type": "Deterministic",
        "Paradigm": "Classical",
        "# Runs": 1,
        "# Feasible Runs": 1,
        "# Successful Runs": 1,
        "Success Threshold": 0,
        "Hardware Specifications": HARDWARE,
        "Total Runtime": f"{elapsed:.6f}",
        "Time to Solution": f"{elapsed:.6f}",
        "CPU Runtime": f"{elapsed:.6f}",
        "GPU Runtime": 0,
        "QPU Runtime": 0,
        "Other HW Runtime": 0,
        "Remarks": "Exact reconstruction verified; no optimality claim is made.",
    }
    with (destination / f"{instance_id}_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerow(row)
    return instance_id, term_count, elapsed


def main() -> None:
    root = repository_root()
    output = root / "03-birkhoff" / "submissions" / "20260817_BirkhoffMaxMin_Gupta"
    reference = reference_url(root)
    results: list[tuple[str, int, float]] = []
    for size in (64, 100):
        source = root / "03-birkhoff" / "instances" / f"qbench_{size}_dense.json"
        instances = json.loads(source.read_text())
        for key, instance in instances.items():
            if key != "_license":
                results.append(write_instance(key, instance, output / instance["id"], reference))

    lines = [
        "# Dense Birkhoff decomposition submission",
        "",
        "This submission provides exact decompositions for the fifteen dense Birkhoff instances that were open when the results were generated.",
        "The objective is the number of permutation matrices, and no optimality is claimed.",
        "",
        "| Instance | Terms | Runtime (s) |",
        "| --- | ---: | ---: |",
    ]
    lines.extend(f"| {instance} | {terms} | {elapsed:.6f} |" for instance, terms, elapsed in sorted(results))
    lines.extend([
        "",
        "The solver and reproduction instructions are in [`experiments/birkhoff`](../../../experiments/birkhoff).",
    ])
    (output / "README.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
