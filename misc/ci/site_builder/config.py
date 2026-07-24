# This file is part of QOBLIB - Quantum Optimization Benchmarking Library
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Shared configuration for the QOBLIB site-data builder.

Holds the build context (repository root + the GitHub repo/ref used to build
download links), the static per-problem metadata, and the per-problem table
columns rendered by the frontend. The context is configured once per build via
:func:`configure` so the data-collection helpers can construct repository URLs
without every function taking a repo/ref argument.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import urlsplit


DEFAULT_REPO_URL = "https://github.com/ZIB-AOPT/QOBLIB"
DEFAULT_REF = "main"
# Deployed origin (no trailing slash) used to build absolute canonical / Open
# Graph URLs and the <base> path for the pretty per-problem pages. Override with
# `--base-url` for a custom domain.
DEFAULT_BASE_URL = "https://zib-aopt.github.io/QOBLIB"

PROBLEM_DIR_PATTERN = re.compile(r"^(\d{2})-(.+)$")


class RepoLinks:
    """Builds blob / tree / raw GitHub URLs for a given repo and ref.

    Parametrising these (instead of hard-coding ``ZIB-AOPT/QOBLIB@main``) lets
    the GitHub Pages workflow point preview builds at the pull-request head, so
    download links in a PR preview resolve against the proposed changes.
    """

    def __init__(self, repo_url: str = DEFAULT_REPO_URL, ref: str = DEFAULT_REF) -> None:
        self.repo_url = repo_url.rstrip("/")
        self.ref = ref

    @property
    def owner_repo(self) -> tuple[str, str]:
        parts = urlsplit(self.repo_url).path.strip("/").split("/")
        owner = parts[0] if len(parts) >= 1 else "ZIB-AOPT"
        repo = parts[1] if len(parts) >= 2 else "QOBLIB"
        return owner, repo

    def blob(self, rel_path: str) -> str:
        return f"{self.repo_url}/blob/{self.ref}/{rel_path}"

    def tree(self, rel_path: str) -> str:
        return f"{self.repo_url}/tree/{self.ref}/{rel_path}"

    def raw(self, rel_path: str) -> str:
        owner, repo = self.owner_repo
        return f"https://raw.githubusercontent.com/{owner}/{repo}/{self.ref}/{rel_path}"


# --- Build context (configured once per build via configure()) ---------------

REPO_ROOT: Path = Path(".")
LINKS: RepoLinks = RepoLinks()


def configure(root: Path | str = ".", repo_url: str = DEFAULT_REPO_URL, ref: str = DEFAULT_REF) -> None:
    """Set the repository root and the repo/ref used for download links."""
    global REPO_ROOT, LINKS
    REPO_ROOT = Path(root)
    LINKS = RepoLinks(repo_url, ref)


def rel_to_root(path: Path) -> str:
    """Repository-relative POSIX path for ``path`` (used to build URLs)."""
    return path.relative_to(REPO_ROOT).as_posix()


def get_commit_hash() -> str | None:
    """Best-effort current commit hash: CI env var first, then local git."""
    for var in ("GITHUB_SHA", "GIT_COMMIT", "COMMIT_SHA"):
        sha = os.environ.get(var)
        if sha:
            return sha.strip()
    try:
        import subprocess

        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        ).stdout.strip()
        return sha or None
    except Exception:
        return None


def find_problem_dirs() -> list[tuple[str, Path]]:
    """Return ``[(id, path)]`` for every ``NN-name`` problem directory, sorted by id."""
    results: list[tuple[str, Path]] = []
    for entry in sorted(REPO_ROOT.iterdir()):
        match = PROBLEM_DIR_PATTERN.match(entry.name)
        if match and entry.is_dir():
            results.append((match.group(1), entry))
    return results


# ---------------------------------------------------------------------------
# Static metadata that cannot be inferred from filenames alone.
# Extend / correct these as the library evolves.
# ---------------------------------------------------------------------------

PROBLEM_META: dict[str, dict] = {
    "01": {
        "slug": "marketsplit",
        "why": "These instances stress multi-constraint subset-sum structure, where feasibility is easy to state but difficult to certify at useful sizes.",
        "name": "Market Split",
        "short": "Multi-dimensional Subset Sum",
        "type": "Binary",
        "formulation": "QUBO / ILP",
        "minimize": True,
        "tags": ["combinatorial", "NP-hard", "subset-sum"],
        "formula": "min  Σ_ij Q_ij x_i x_j,   x ∈ {0,1}^n",
        "description": (
            "The Market Split problem asks whether a set of items can be partitioned "
            "into two groups such that multiple knapsack constraints are satisfied "
            "simultaneously. It is a generalization of subset sum to higher dimensions "
            "and is strongly NP-hard. Instances become intractable for classical "
            "branch-and-bound solvers already at a few hundred variables due to the "
            "highly degenerate structure of the feasible set."
        ),
    },
    "02": {
        "slug": "labs",
        "why": "LABS is a canonical spin benchmark with direct links to communications, radar, and cryptography, and it becomes harder as sequence length grows.",
        "name": "LABS",
        "short": "Low Autocorrelation Binary Sequences",
        "type": "Binary",
        "formulation": "QUBO",
        "minimize": True,
        "tags": ["signal-processing", "dense", "NP-hard"],
        "formula": "min  E(s) = Σ_{k=1}^{n-1} C_k²,   C_k = Σ_{i=1}^{n-k} s_i s_{i+k}",
        "description": (
            "The Low Autocorrelation Binary Sequence (LABS) problem seeks a ±1 sequence "
            "of length n minimising the sum of squared off-peak autocorrelations. "
            "Even for n ≈ 50 the problem is open for exact methods. The dense QUBO "
            "structure makes it a stringent test of quantum hardware."
        ),
    },
    "03": {
        "slug": "birkhoff",
        "why": "Minimum Birkhoff decomposition links assignment structure, sparse representation, and quantum physics applications through a hard cardinality objective.",
        "name": "Min. Birkhoff Decomposition",
        "short": "Doubly Stochastic Matrix Decomposition",
        "type": "Binary + Integer",
        "formulation": "MIP / QUBO",
        "minimize": True,
        "tags": ["matrix-theory", "combinatorial", "telecommunications"],
        "formula": "min |S|  s.t.  D = Σ_{P∈S} λ_P P,  Σ λ_P = 1,  λ_P ≥ 0",
        "description": (
            "Find the minimum number of permutation matrices needed to express a given "
            "doubly stochastic matrix as a convex combination. Direct applications in "
            "optical circuit switching and traffic scheduling."
        ),
    },
    "04": {
        "slug": "steiner",
        "why": "Steiner tree packing models wire-routing pressure in VLSI-style grids, where many connection demands must coexist without conflicts.",
        "name": "Steiner Tree Packing",
        "short": "VLSI Design / Wire Routing",
        "type": "Binary",
        "formulation": "ILP / QUBO",
        "minimize": True,
        "tags": ["graph-theory", "VLSI", "NP-hard"],
        "formula": "max Σ_k y_k  s.t.  Σ_k x_{e,k} ≤ 1 ∀e,  (x_k, y_k) span tree for T_k",
        "description": (
            "Find a maximum set of edge-disjoint Steiner trees connecting terminal sets "
            "in a graph. Models multi-commodity wire routing in VLSI design. Instances "
            "are derived from real chip routing benchmarks with large sparse graphs."
        ),
    },
    "05": {
        "slug": "sports",
        "why": "Sports timetabling captures realistic constraint interactions from round-robin tournaments, with instances selected for diversity and difficulty.",
        "name": "Sports Tournament Scheduling",
        "short": "Constraint Satisfaction / Scheduling",
        "type": "Binary",
        "formulation": "ILP / QUBO",
        "minimize": True,
        "tags": ["scheduling", "CSP", "symmetry-rich"],
        "formula": "min Σ_{t,r} dist(venue_{t,r-1}, venue_{t,r})  s.t. feasibility",
        "description": (
            "Schedule a round-robin tournament minimising travel distance subject to "
            "hard constraints: each team plays once per round, home/away balance, "
            "no three consecutive games at the same venue. Highly symmetric structure "
            "makes it a natural testbed for symmetry-exploitation methods."
        ),
    },
    "06": {
        "slug": "portfolio",
        "why": "Portfolio instances add transaction costs, short selling, borrowing costs, and time coupling to a familiar financial optimization model.",
        "name": "Portfolio Optimization",
        "short": "Multi-period with Transaction Costs & Short Selling",
        "type": "Binary + Continuous",
        "formulation": "MIQP / QUBO",
        "minimize": True,
        "tags": ["finance", "MIQP", "real-world"],
        "formula": "min Σ_t (λ risk_t - profit_t + transaction and borrowing costs)",
        "description": (
            "Minimise risk-adjusted portfolio cost over multiple periods with transaction "
            "costs, cardinality constraints, short-selling limits, and turnover bounds. "
            "Multi-period structure introduces complex intertemporal dependencies."
        ),
    },
    "07": {
        "slug": "independentset",
        "why": "Maximum independent set is a fundamental graph problem with compact QUBO structure and hard instances from social, biological, and benchmark graphs.",
        "name": "Maximum Independent Set",
        "short": "Unweighted MIS on Hard Graphs",
        "type": "Binary",
        "formulation": "QUBO",
        "minimize": False,
        "tags": ["graph-theory", "NP-hard", "benchmark-classic"],
        "formula": "max Σ_i x_i  s.t.  x_i + x_j ≤ 1  ∀(i,j)∈E,  x ∈ {0,1}^n",
        "description": (
            "Find the largest subset of vertices with no two adjacent. Instances are "
            "carefully selected to be hard for state-of-the-art solvers, not randomly "
            "generated easy cases. NP-hard to approximate within n^{1-ε}."
        ),
    },
    "08": {
        "slug": "network",
        "why": "Network design represents traffic-routing and degree-constrained infrastructure planning, with objective values tied to congestion.",
        "name": "Network Design",
        "short": "Telecommunications Network Planning",
        "type": "Binary",
        "formulation": "ILP / QUBO",
        "minimize": True,
        "tags": ["network", "telecommunications", "NP-hard"],
        "formula": "min c^T y  s.t.  Σ_e f_{ke} = d_k ∀k,  f_{ke} ≤ cap_e · y_e,  y ∈ {0,1}^m",
        "description": (
            "Select a subset of potential links minimising installation cost while "
            "ensuring connectivity and capacity for all traffic demands, with "
            "survivability requirements (connectivity after any single link failure)."
        ),
    },
    "09": {
        "slug": "routing",
        "why": "Vehicle routing combines route selection, capacity, and time-window pressure, reflecting core logistics and mobility applications.",
        "name": "Vehicle Routing",
        "short": "VRP with Time Windows + Capacity",
        "type": "Binary",
        "formulation": "ILP / QUBO",
        "minimize": True,
        "tags": ["logistics", "VRP", "real-world"],
        "formula": "min Σ_{i,j,k} c_{ij} x_{ijk}  s.t.  time windows, capacity, flow",
        "description": (
            "The VRP with Time Windows and Capacity Constraints combines TSP-like "
            "sequencing with knapsack constraints. Instances from logistics benchmarks "
            "include depot constraints, heterogeneous capacities, and late-arrival "
            "penalty terms."
        ),
    },
    "10": {
        "slug": "topology",
        "why": "Topology design asks for low-diameter graphs under degree limits, a concise model for communication latency and network architecture.",
        "name": "Topology Design",
        "short": "Graph Golf / Node-Degree-Diameter Problem",
        "type": "Binary",
        "formulation": "QUBO / ILP",
        "minimize": True,
        "tags": ["graph-theory", "network-design", "combinatorial"],
        "formula": "min diam(G)  s.t.  deg(v) ≤ Δ  ∀v,  G=(V,E),  |V|=n",
        "description": (
            "Design a graph on n vertices with bounded degree Δ and minimum diameter. "
            "Corresponds to efficient low-latency network design. Rich automorphism "
            "structure makes these instances natural fits for symmetry-based methods."
        ),
    },
}

# ---------------------------------------------------------------------------
# Problem-specific instance columns shown on the problem / instance pages.
#   key     — looked up in inst["metrics"]
#   label   — column header
#   numeric — right-align + thousands formatting (False keeps the raw string)
# ---------------------------------------------------------------------------

PROBLEM_COLUMNS: dict[str, list[dict]] = {
    "01": [{"key": "markets", "label": "Markets", "numeric": True},
           {"key": "variables", "label": "Variables", "numeric": True},
           {"key": "coeff_range", "label": "Coeff. range", "numeric": True}],
    "02": [{"key": "length", "label": "Length N", "numeric": True}],
    "03": [{"key": "dimension", "label": "Matrix n", "numeric": True}],
    "04": [{"key": "grid", "label": "Grid", "numeric": True},
           {"key": "layers", "label": "Layers", "numeric": True},
           {"key": "terminals", "label": "Terminals", "numeric": True},
           {"key": "holes", "label": "Holes", "numeric": True}],
    "05": [{"key": "variables", "label": "Variables", "numeric": True},
           {"key": "constraints", "label": "Constraints", "numeric": True}],
    "06": [{"key": "assets", "label": "Assets", "numeric": True},
           {"key": "periods", "label": "Periods", "numeric": True},
           {"key": "risk_lambda", "label": "Risk λ", "numeric": False}],
    "07": [{"key": "nodes", "label": "Nodes", "numeric": True},
           {"key": "edges", "label": "Edges", "numeric": True}],
    "08": [{"key": "variables", "label": "Variables", "numeric": True},
           {"key": "constraints", "label": "Constraints", "numeric": True}],
    "09": [{"key": "customers", "label": "Customers", "numeric": True},
           {"key": "vehicles", "label": "Vehicles", "numeric": True}],
    "10": [{"key": "nodes", "label": "Nodes", "numeric": True},
           {"key": "degree", "label": "Max degree", "numeric": True}],
}
