#!/usr/bin/env python3
"""
gpt_csp_spinglass.py


Hybrid CSP + Spin-Glass Generator for Hard Small Maximum Independent Set Instances


Implements the compact hybrid overlay described in:
"Generating Small Maximum Independent Set Instances that are Hard for
Both MILP and State-of-the-Art Heuristics" (April 9, 2026)


The generator combines:



A balanced near-threshold CSP conflict graph (MILP/exact hardness)

A hidden frustrated spin-glass layer (heuristic trap hardness)


into a single MIS graph with n = q*k < 100 vertices.


Integrates:



IBM CPLEX 22.1 for exact MILP solving (H_exact scoring)

ReduMIS / KaMIS for heuristic solving (H_heur scoring)
"""


import random
import itertools
import math
import copy
import os
import sys
import time
import subprocess
import tempfile
import shutil
import signal
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any, NamedTuple
from dataclasses import dataclass, field


import networkx as nx
import numpy as np


# Optional CPLEX import
try:
    from docplex.mp.model import Model as CplexModel
    from docplex.mp.solution import SolveSolution
    CPLEX_AVAILABLE = True
except ImportError:
    CPLEX_AVAILABLE = False


# =============================================================================
# Logging setup
# =============================================================================

# Module-level logger — handlers attached later by setup_run_logging()
logger = logging.getLogger(__name__)


def setup_run_logging(
    args: Any,
    base_log_dir: str = "logs",
    density_override: Optional[float] = None,
) -> Path:
    """
    Create a per-run log directory and configure all logging to go there.

    Directory name format:
        mis_gpt_{YYYYMMDD_HHMMSS}_n{nodes}_d{density}_q{q}_k{k}_dC{d_C}_dS{d_S}_{mode}

    Returns the Path to the created log directory.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Compute expected node count
    nodes = getattr(args, "q", 20) * getattr(args, "k", 4)

    # Estimate density if not overridden
    if density_override is not None:
        density_str = f"{density_override:.3f}"
    else:
        q = getattr(args, "q", 20)
        k = getattr(args, "k", 4)
        d_C = getattr(args, "d_C", 5)
        d_S = getattr(args, "d_S", 3)
        lam = getattr(args, "lam", 2)
        mu = getattr(args, "mu", 1)
        try:
            info = compute_max_edges(q, k, d_C, d_S, lam, mu)
            density_str = f"{info['estimated_density']:.3f}"
        except Exception:
            density_str = "unknown"

    mode = getattr(args, "mode", "full")
    density_preset = getattr(args, "density", None)

    dir_name = (
        f"mis_gpt_{timestamp}"
        f"_n{nodes}"
        f"_dens{density_str}"
        f"_q{getattr(args, 'q', '?')}"
        f"_k{getattr(args, 'k', '?')}"
        f"_dC{getattr(args, 'd_C', '?')}"
        f"_dS{getattr(args, 'd_S', '?')}"
        f"_lam{getattr(args, 'lam', '?')}"
        f"_mu{getattr(args, 'mu', '?')}"
        f"_{mode}"
    )
    if density_preset:
        dir_name += f"_preset-{density_preset}"

    log_dir = Path(base_log_dir) / dir_name
    log_dir.mkdir(parents=True, exist_ok=True)

    # ---- Root logger: captures everything from all modules ----
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Remove any pre-existing handlers (e.g. basicConfig defaults)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Shared formatter
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1. Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(fmt)
    root_logger.addHandler(console_handler)

    # 2. Main log file — everything DEBUG+
    main_log_path = log_dir / "run.log"
    file_handler = logging.FileHandler(main_log_path, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    root_logger.addHandler(file_handler)

    # 3. Solver-specific log file (INFO+)
    solver_log_path = log_dir / "solvers.log"
    solver_handler = logging.FileHandler(solver_log_path, mode="w", encoding="utf-8")
    solver_handler.setLevel(logging.INFO)
    solver_handler.setFormatter(fmt)
    # Attach only to solver-related loggers
    for solver_logger_name in [
        "gpt_csp_spinglass.CPLEXSolver",
        "gpt_csp_spinglass.ReduMISSolver",
        "gpt_csp_spinglass.SolverPortfolio",
    ]:
        sl = logging.getLogger(solver_logger_name)
        sl.addHandler(solver_handler)

    # 4. Write a params manifest so the run is self-documenting
    params_path = log_dir / "params.txt"
    with open(params_path, "w") as f:
        f.write(f"Run timestamp : {timestamp}\n")
        f.write(f"Log directory : {log_dir.resolve()}\n")
        f.write(f"Mode          : {mode}\n")
        f.write(f"Density preset: {density_preset or 'None'}\n")
        f.write(f"---\n")
        for attr in sorted(vars(args)):
            f.write(f"{attr:20s}: {getattr(args, attr)}\n")

    logger.info(f"Log directory created: {log_dir.resolve()}")
    logger.info(f"Parameters written to: {params_path}")

    return log_dir


# =============================================================================
# Data classes and configuration
# =============================================================================

@dataclass
class SolverConfig:
    """Configuration for external solvers."""
    # CPLEX settings
    cplex_time_limit: float = 300.0
    cplex_threads: int = 1
    cplex_mem_limit: int = 4096
    cplex_mip_emphasis: int = 0
    cplex_node_limit: int = -1

    # ReduMIS / KaMIS settings
    redumis_binary: str = "redumis"
    kamis_binary: str = "weighted_branch_reduce"
    heuristic_time_limit: float = 60.0
    heuristic_runs: int = 5
    heuristic_seed_base: int = 0

    # Scoring weights (Section 8)
    w_exact: float = 1.0
    w_heur: float = 1.0
    w_sg: float = 0.5
    w_red: float = 0.3

    # Paths
    temp_dir: str = "/tmp/hybrid_mis"

@dataclass
class SolverResult:
    """Result from a single solver invocation."""
    solver_name: str
    mis_size: int = 0
    solve_time: float = 0.0
    nodes_explored: int = 0
    gap: float = float('inf')
    status: str = "unknown"
    solution: Optional[List[int]] = None
    timed_out: bool = False
    lp_bound: float = 0.0
    error: Optional[str] = None


@dataclass
class HardnessProfile:
    """Complete hardness profile for an instance."""
    cplex_time: float = 0.0
    cplex_nodes: int = 0
    cplex_gap: float = 0.0
    cplex_mis_size: int = 0
    cplex_lp_bound: float = 0.0
    cplex_timed_out: bool = False

    heuristic_best: int = 0
    heuristic_worst: int = 0
    heuristic_mean: float = 0.0
    heuristic_std: float = 0.0
    heuristic_hit_optimum: bool = False
    heuristic_times: List[float] = field(default_factory=list)

    spin_trap_score: float = 0.0
    E_star: int = 0
    N_opt: int = 0
    N_loc: int = 0
    d_bar_opt: float = 0.0

    reduction_resistance: float = 0.0
    passed_filters: bool = False

    H_exact: float = 0.0
    H_heur: float = 0.0
    H_total: float = 0.0

# =============================================================================
# Parameter validation
# =============================================================================

def _validate_params(q: int, k: int, d_C: int, d_S: int):
    """Enforce all construction constraints from the paper."""
    if k % 2 != 0:
        raise ValueError(f"k must be even, got k={k}")
    if q * k >= 1000:
        raise ValueError(f"n = qk = {q * k} must be < 100")
    if (q * d_C) % 2 != 0:
        raise ValueError(f"qd_C must be even, got {q * d_C}")
    if (q * d_S) % 2 != 0:
        raise ValueError(f"q*d_S must be even, got {q * d_S}")
    if d_C >= q:
        raise ValueError(f"d_C={d_C} must be < q={q}")
    if d_S >= q:
        raise ValueError(f"d_S={d_S} must be < q={q}")


# =============================================================================
# Step 1-3: Graph generation utilities
# =============================================================================

def sample_connected_regular_graph(n: int, d: int, max_attempts: int = 1000) -> nx.Graph:
    """Sample a connected d-regular graph on n vertices."""
    if (n * d) % 2 != 0:
        raise ValueError(f"n*d must be even, got n={n}, d={d}")
    if d >= n:
        raise ValueError(f"Degree d={d} must be less than n={n}")

    for _ in range(max_attempts):
        G = nx.random_regular_graph(d, n)
        if nx.is_connected(G):
            return G
    raise RuntimeError(
        f"Failed to generate connected {d}-regular graph on {n} nodes "
        f"after {max_attempts} attempts"
    )

def sample_signed_regular_graph(
    n: int, d: int, frac_negative: float = 0.5, max_attempts: int = 1000
) -> Tuple[nx.Graph, Dict[Tuple[int, int], int]]:
    """Sample a connected d-regular graph with random edge signs."""
    G = sample_connected_regular_graph(n, d, max_attempts)
    sigma = {}
    for u, v in G.edges():
        i, j = min(u, v), max(u, v)
        sigma[(i, j)] = -1 if random.random() < frac_negative else +1
    return G, sigma


# =============================================================================
# Step 4: Balanced hidden spin labels
# =============================================================================

def assign_balanced_spin_labels(q: int, k: int) -> Dict[int, Dict[int, int]]:
    """
    For each variable i in [q], assign a balanced map tau_i: D -> {0, 1}
    such that exactly k/2 values map to 0 and k/2 map to 1.
    """
    if k % 2 != 0:
        raise ValueError(f"k must be even for balanced spin labels, got k={k}")

    D = list(range(1, k + 1))
    tau = {}
    for i in range(q):
        perm = D[:]
        random.shuffle(perm)
        label_map = {}
        for idx, val in enumerate(perm):
            label_map[val] = 0 if idx < k // 2 else 1
        tau[i] = label_map
    return tau

# =============================================================================
# Step 5: Balanced CSP forbidden pairs
# =============================================================================

def generate_balanced_csp_table(
    k: int, lam: int, existing_forbidden: Optional[Set[Tuple[int, int]]] = None,
    max_overlap: int = -1, max_attempts: int = 500
) -> Set[Tuple[int, int]]:
    """
    Generate a balanced forbidden-pair table F_csp using lambda random permutations.
    Each row and column has exactly lambda forbidden entries.
    """
    D = list(range(1, k + 1))

    for _ in range(max_attempts):
        forbidden = set()
        valid = True

        for t in range(lam):
            found = False
            for __ in range(100):
                perm = D[:]
                random.shuffle(perm)
                new_pairs = {(a, perm[idx]) for idx, a in enumerate(D)}
                if not new_pairs.intersection(forbidden):
                    found = True
                    forbidden.update(new_pairs)
                    break

            if not found:
                valid = False
                break

        if not valid:
            continue

        if existing_forbidden is not None and max_overlap >= 0:
            overlap = len(forbidden.intersection(existing_forbidden))
            if overlap > max_overlap:
                continue

        return forbidden

    # Fallback
    forbidden = set()
    for t in range(lam):
        perm = D[:]
        random.shuffle(perm)
        for idx, a in enumerate(D):
            forbidden.add((a, perm[idx]))
    return forbidden

# =============================================================================
# Step 6: Spin-glass trap forbidden pairs
# =============================================================================

def generate_spin_trap_table(
    k: int, mu: int, tau_i: Dict[int, int], tau_j: Dict[int, int],
    sigma_ij: int
) -> Set[Tuple[int, int]]:
    """
    Generate a balanced spin-trap forbidden-pair table for edge (i,j).
    sigma_ij = +1: forbid cross-spin pairs; -1: forbid same-spin pairs.
    """
    D = list(range(1, k + 1))

    D_i_0 = [a for a in D if tau_i[a] == 0]
    D_i_1 = [a for a in D if tau_i[a] == 1]
    D_j_0 = [b for b in D if tau_j[b] == 0]
    D_j_1 = [b for b in D if tau_j[b] == 1]

    forbidden = set()

    for t in range(mu):
        if sigma_ij == +1:
            perm_01 = D_j_1[:]
            random.shuffle(perm_01)
            for idx, a in enumerate(D_i_0):
                forbidden.add((a, perm_01[idx]))

            perm_10 = D_j_0[:]
            random.shuffle(perm_10)
            for idx, a in enumerate(D_i_1):
                forbidden.add((a, perm_10[idx]))
        else:
            perm_00 = D_j_0[:]
            random.shuffle(perm_00)
            for idx, a in enumerate(D_i_0):
                forbidden.add((a, perm_00[idx]))

            perm_11 = D_j_1[:]
            random.shuffle(perm_11)
            for idx, a in enumerate(D_i_1):
                forbidden.add((a, perm_11[idx]))

    return forbidden

# =============================================================================
# Core instance class
# =============================================================================

class HybridMISInstance:
    """Stores all data for a hybrid CSP + spin-glass MIS instance."""

    def __init__(self):
        self.q = 0
        self.k = 0
        self.d_C = 0
        self.d_S = 0
        self.lam = 0
        self.mu = 0

        self.H_C: Optional[nx.Graph] = None
        self.H_S: Optional[nx.Graph] = None
        self.sigma: Dict[Tuple[int, int], int] = {}
        self.tau: Dict[int, Dict[int, int]] = {}

        self.F_csp: Dict[Tuple[int, int], Set[Tuple[int, int]]] = {}
        self.F_sg: Dict[Tuple[int, int], Set[Tuple[int, int]]] = {}
        self.F: Dict[Tuple[int, int], Set[Tuple[int, int]]] = {}

        self.G: Optional[nx.Graph] = None
        self.vertex_map: Dict[Tuple[int, int], int] = {}
        self.reverse_map: Dict[int, Tuple[int, int]] = {}

        self.hardness: Optional[HardnessProfile] = None

    @property
    def n(self) -> int:
        return self.q * self.k


def _edge_key(i: int, j: int) -> Tuple[int, int]:
    return (min(i, j), max(i, j))


# =============================================================================
# CPLEX Solver Integration (Section 8.1 - H_exact)
# Compatible with CPLEX 22.1
# =============================================================================

class CPLEXSolver:
    """
    Solve Maximum Independent Set using IBM CPLEX via docplex.

    Formulation (standard MIS ILP):
        max  sum_v x_v
        s.t. x_u + x_v <= 1   for all (u,v) in E
             x_v in {0, 1}     for all v in V
    """

    def __init__(self, config: SolverConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.CPLEXSolver")
        if not CPLEX_AVAILABLE:
            self.logger.warning(
                "CPLEX (docplex) not available. Install with: "
                "pip install docplex cplex"
            )

    def _set_param_safe(self, params, path: str, value):
        """
        Set a CPLEX parameter by dotted path, swallowing errors.
        """
        try:
            obj = params
            parts = path.split('.')
            for part in parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, parts[-1], value)
            return True
        except Exception:
            return False

    def _get_detail_safe(self, details, *attrs):
        """Try multiple attribute names on solve_details, return first that works."""
        for attr in attrs:
            try:
                val = getattr(details, attr, None)
                if val is not None:
                    return val
            except Exception:
                continue
        return None

    def solve(self, G: nx.Graph, name: str = "MIS") -> SolverResult:
        """Solve MIS on graph G using CPLEX."""
        result = SolverResult(solver_name="CPLEX")

        if not CPLEX_AVAILABLE:
            result.error = "CPLEX not installed"
            result.status = "unavailable"
            return result

        n = G.number_of_nodes()
        nodes = sorted(G.nodes())
        node_to_idx = {v: i for i, v in enumerate(nodes)}

        try:
            mdl = CplexModel(name=name)
            cp = mdl.context.cplex_parameters

            self._set_param_safe(cp, 'threads', self.config.cplex_threads)
            mdl.set_time_limit(self.config.cplex_time_limit)

            if self.config.cplex_mem_limit > 0:
                self._set_param_safe(cp, 'workmem', self.config.cplex_mem_limit)

            if self.config.cplex_mip_emphasis != 0:
                set_ok = self._set_param_safe(
                    cp, 'emphasis.mip', self.config.cplex_mip_emphasis
                )
                if not set_ok:
                    try:
                        mdl.get_cplex().parameters.emphasis.mip.set(
                            self.config.cplex_mip_emphasis
                        )
                    except Exception:
                        self.logger.debug("Could not set MIP emphasis - using default")

            if self.config.cplex_node_limit > 0:
                self._set_param_safe(
                    cp, 'mip.limits.nodes', self.config.cplex_node_limit
                )

            self._set_param_safe(cp, 'output.clonelog', 0)
            try:
                mdl.context.solver.verbose = 0
            except Exception:
                pass

            x = mdl.binary_var_list(n, name="x")
            mdl.maximize(mdl.sum(x))

            for u, v in G.edges():
                idx_u = node_to_idx[u]
                idx_v = node_to_idx[v]
                mdl.add_constraint(x[idx_u] + x[idx_v] <= 1)

            start_time = time.time()
            solution = mdl.solve(log_output=False)
            elapsed = time.time() - start_time

            result.solve_time = elapsed

            if solution is not None:
                result.mis_size = int(round(solution.objective_value))
                result.solution = [
                    nodes[i] for i in range(n)
                    if solution.get_value(x[i]) > 0.5
                ]
                result.status = "optimal"
            else:
                sd = mdl.solve_details
                result.status = str(sd.status) if sd else "no_solution"

            sd = mdl.solve_details
            if sd:
                val = self._get_detail_safe(sd, 'mip_relative_gap', 'gap')
                result.gap = float(val) if val is not None else 0.0

                val = self._get_detail_safe(
                    sd,
                    'nb_nodes_processed',
                    'n_nodes_processed',
                    'nb_iterations',
                )
                result.nodes_explored = int(val) if val is not None else 0

                val = self._get_detail_safe(
                    sd, 'best_bound', 'mip_best_bound'
                )
                result.lp_bound = float(val) if val is not None else 0.0

                if elapsed >= self.config.cplex_time_limit * 0.99:
                    result.timed_out = True
                    result.status = "time_limit"

            mdl.end()

        except Exception as e:
            result.error = str(e)
            result.status = "error"
            self.logger.error(f"CPLEX error: {e}")

        return result

# =============================================================================
# ReduMIS / KaMIS Heuristic Integration (Section 8.2 - H_heur)
# =============================================================================

class ReduMISSolver:
    """
    Solve Maximum Independent Set using ReduMIS (from the KaMIS suite).
    """

    def __init__(self, config: SolverConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ReduMISSolver")
        self._ensure_temp_dir()

    def _ensure_temp_dir(self):
        os.makedirs(self.config.temp_dir, exist_ok=True)

    def _find_binary(self) -> Optional[str]:
        """Find the ReduMIS or KaMIS binary."""
        for binary in [self.config.redumis_binary, self.config.kamis_binary]:
            if shutil.which(binary):
                return binary
            for prefix in ["/usr/local/bin", "/opt/kamis/deploy",
                           os.path.expanduser("~/KaMIS/deploy")]:
                full_path = os.path.join(prefix, binary)
                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    return full_path
        return None

    @staticmethod
    def write_metis(G: nx.Graph, filepath: str):
        """Write graph G in METIS format."""
        nodes = sorted(G.nodes())
        node_to_idx = {v: i + 1 for i, v in enumerate(nodes)}
        n = len(nodes)
        m = G.number_of_edges()

        with open(filepath, 'w') as f:
            f.write(f"{n} {m}\n")
            for v in nodes:
                neighbors = sorted([node_to_idx[u] for u in G.neighbors(v)])
                f.write(" ".join(map(str, neighbors)) + "\n")

    @staticmethod
    def read_mis_output(filepath: str, n: int) -> List[int]:
        """Read ReduMIS/KaMIS output (one 0/1 per line)."""
        mis = []
        if not os.path.isfile(filepath):
            return mis

        with open(filepath, 'r') as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if line == '1':
                    mis.append(idx)
                if idx >= n - 1:
                    break
        return mis

    def solve_single(
        self, G: nx.Graph, graph_path: str, output_path: str,
        seed: int = 0, time_limit: Optional[float] = None
    ) -> SolverResult:
        """Run a single ReduMIS invocation."""
        result = SolverResult(solver_name="ReduMIS")
        binary = self._find_binary()

        if binary is None:
            result.error = (
                "ReduMIS/KaMIS binary not found. Install from: "
                "https://github.com/KarlsruheKaMIS/KaMIS"
            )
            result.status = "unavailable"
            return result

        if time_limit is None:
            time_limit = self.config.heuristic_time_limit

        self.write_metis(G, graph_path)

        cmd = [
            binary,
            graph_path,
            f"--output={output_path}",
            f"--seed={seed}",
            f"--time_limit={time_limit}",
        ]

        try:
            start_time = time.time()
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=time_limit + 30,
            )
            elapsed = time.time() - start_time

            result.solve_time = elapsed
            result.timed_out = elapsed >= time_limit * 0.99

            if proc.returncode == 0:
                n = G.number_of_nodes()
                mis_vertices = self.read_mis_output(output_path, n)
                result.mis_size = len(mis_vertices)
                result.solution = mis_vertices
                result.status = "heuristic_solution"

                nodes_sorted = sorted(G.nodes())
                mis_set = set(
                    nodes_sorted[v] for v in mis_vertices if v < len(nodes_sorted)
                )
                for u_node in mis_set:
                    for v_node in mis_set:
                        if u_node < v_node and G.has_edge(u_node, v_node):
                            self.logger.warning(
                                f"ReduMIS solution NOT independent! "
                                f"Edge ({u_node},{v_node}) violated."
                            )
                            result.status = "invalid_solution"
                            break
            else:
                result.error = proc.stderr[:500] if proc.stderr else "Unknown error"
                result.status = "error"
                for line in (proc.stdout or "").split('\n'):
                    if "MIS_size" in line or "best" in line.lower():
                        try:
                            parts = line.strip().split()
                            for p in parts:
                                if p.isdigit():
                                    result.mis_size = max(result.mis_size, int(p))
                        except Exception:
                            pass

        except subprocess.TimeoutExpired:
            result.timed_out = True
            result.solve_time = time_limit + 30
            result.status = "timeout"
        except FileNotFoundError:
            result.error = f"Binary not found: {binary}"
            result.status = "unavailable"
        except Exception as e:
            result.error = str(e)
            result.status = "error"

        return result

    def solve(self, G: nx.Graph, name: str = "MIS") -> List[SolverResult]:
        """Run multiple independent ReduMIS invocations."""
        results = []
        n_runs = self.config.heuristic_runs
        base_seed = self.config.heuristic_seed_base

        for run_idx in range(n_runs):
            graph_path = os.path.join(
                self.config.temp_dir, f"{name}_run{run_idx}.graph"
            )
            output_path = os.path.join(
                self.config.temp_dir, f"{name}_run{run_idx}.mis"
            )

            r = self.solve_single(
                G, graph_path, output_path,
                seed=base_seed + run_idx,
                time_limit=self.config.heuristic_time_limit
            )
            results.append(r)

            self.logger.debug(
                f"  ReduMIS run {run_idx}: size={r.mis_size}, "
                f"time={r.solve_time:.2f}s, status={r.status}"
            )

            for fp in [graph_path, output_path]:
                try:
                    os.remove(fp)
                except OSError:
                    pass

        return results

# =============================================================================
# Unified Solver Portfolio
# =============================================================================

class SolverPortfolio:
    """
    Manages CPLEX (exact) and ReduMIS (heuristic) solvers.
    Computes the composite hardness score from Section 8.
    """

    def __init__(self, config: Optional[SolverConfig] = None):
        self.config = config or SolverConfig()
        self.cplex_solver = CPLEXSolver(self.config)
        self.redumis_solver = ReduMISSolver(self.config)
        self.logger = logging.getLogger(f"{__name__}.SolverPortfolio")

    def evaluate_instance(
        self, inst: HybridMISInstance,
        run_cplex: bool = True,
        run_heuristic: bool = True,
        run_spin_analysis: bool = True,
        instance_name: str = "inst"
    ) -> HardnessProfile:
        """Full hardness evaluation using the solver portfolio."""
        profile = HardnessProfile()
        G = inst.G

        # Structural filters
        passed, reason = apply_structural_filters(inst)
        profile.passed_filters = passed
        if not passed:
            self.logger.debug(f"Instance {instance_name} failed filters: {reason}")

        # Reduction resistance
        profile.reduction_resistance = compute_reduction_resistance_score(inst)

        # Spin-glass analysis
        if run_spin_analysis and inst.q <= 22:
            try:
                analysis = analyze_spin_landscape(inst)
                profile.E_star = analysis['E_star']
                profile.N_opt = analysis['N_opt']
                profile.N_loc = analysis['N_loc']
                profile.d_bar_opt = analysis['d_bar_opt']
                profile.spin_trap_score = compute_spin_trap_score_from_analysis(
                    analysis
                )
            except Exception as e:
                self.logger.warning(f"Spin analysis failed: {e}")

        # CPLEX exact solve
        optimal_size = None
        if run_cplex:
            cplex_result = self.cplex_solver.solve(G, name=instance_name)
            profile.cplex_time = cplex_result.solve_time
            profile.cplex_nodes = cplex_result.nodes_explored
            profile.cplex_gap = cplex_result.gap
            profile.cplex_mis_size = cplex_result.mis_size
            profile.cplex_lp_bound = cplex_result.lp_bound
            profile.cplex_timed_out = cplex_result.timed_out

            if cplex_result.status == "optimal":
                optimal_size = cplex_result.mis_size

            self.logger.info(
                f"CPLEX [{instance_name}]: size={cplex_result.mis_size}, "
                f"time={cplex_result.solve_time:.2f}s, "
                f"nodes={cplex_result.nodes_explored}, "
                f"gap={cplex_result.gap:.4f}, "
                f"status={cplex_result.status}"
            )

        # ReduMIS heuristic solves
        if run_heuristic:
            heur_results = self.redumis_solver.solve(G, name=instance_name)
            valid_results = [r for r in heur_results if r.mis_size > 0]

            if valid_results:
                sizes = [r.mis_size for r in valid_results]
                times = [r.solve_time for r in valid_results]

                profile.heuristic_best = max(sizes)
                profile.heuristic_worst = min(sizes)
                profile.heuristic_mean = np.mean(sizes)
                profile.heuristic_std = np.std(sizes)
                profile.heuristic_times = times

                if optimal_size is not None:
                    profile.heuristic_hit_optimum = (
                        profile.heuristic_best >= optimal_size
                    )

                self.logger.info(
                    f"ReduMIS [{instance_name}]: best={profile.heuristic_best}, "
                    f"worst={profile.heuristic_worst}, "
                    f"mean={profile.heuristic_mean:.1f}, "
                    f"std={profile.heuristic_std:.2f}, "
                    f"hit_opt={profile.heuristic_hit_optimum}"
                )
            else:
                self.logger.warning(
                    f"ReduMIS [{instance_name}]: all runs failed or unavailable"
                )

        # Composite scores
        profile.H_exact = self._compute_H_exact(profile)
        profile.H_heur = self._compute_H_heur(profile, optimal_size)
        profile.H_total = self._compute_H_total(profile)

        inst.hardness = profile
        return profile

    def _compute_H_exact(self, profile: HardnessProfile) -> float:
        """Section 8.1: H_exact based on CPLEX difficulty."""
        if profile.cplex_timed_out:
            timeout_bonus = 10.0
        else:
            timeout_bonus = 0.0

        time_score = math.log(1.0 + profile.cplex_time)
        node_score = math.log(1.0 + profile.cplex_nodes)
        gap_penalty = (
            5.0 * profile.cplex_gap
            if profile.cplex_gap < float('inf') else 10.0
        )

        if profile.cplex_lp_bound > 0 and profile.cplex_mis_size > 0:
            integrality_gap = (
                profile.cplex_lp_bound - profile.cplex_mis_size
            ) / profile.cplex_mis_size
        else:
            integrality_gap = 0.0

        return (
            0.4 * node_score
            + 0.3 * time_score
            + 0.2 * gap_penalty
            + 0.1 * integrality_gap * 10.0
            + timeout_bonus
        )

    def _compute_H_heur(
        self, profile: HardnessProfile, optimal_size: Optional[int]
    ) -> float:
        """Section 8.2: H_heur based on heuristic failure."""
        if optimal_size is None or optimal_size == 0:
            return (
                2.0 * profile.heuristic_std
                + 1.0 * (1.0 - profile.reduction_resistance)
            )

        if profile.heuristic_best > 0:
            hit_rate = 0.0
            if profile.heuristic_hit_optimum:
                if profile.heuristic_mean >= optimal_size - 0.01:
                    hit_rate = 1.0
                else:
                    hit_rate = max(
                        0.0, 1.0 - (optimal_size - profile.heuristic_mean)
                    )
            miss_rate = 1.0 - hit_rate
        else:
            miss_rate = 1.0

        if profile.heuristic_mean > 0:
            avg_gap = (optimal_size - profile.heuristic_mean) / optimal_size
        else:
            avg_gap = 1.0

        variance_penalty = profile.heuristic_std

        return (
            4.0 * miss_rate
            + 3.0 * max(0.0, avg_gap)
            + 1.0 * variance_penalty
        )

    def _compute_H_total(self, profile: HardnessProfile) -> float:
        """Section 8.5: Composite hardness score."""
        filter_bonus = 5.0 if profile.passed_filters else 0.0

        return (
            self.config.w_exact * profile.H_exact
            + self.config.w_heur * profile.H_heur
            + self.config.w_sg * profile.spin_trap_score
            + self.config.w_red * profile.reduction_resistance * 3.0
            + filter_bonus
        )

# =============================================================================
# Algorithm 1: Full hybrid seed generator
# =============================================================================

def generate_hybrid_mis_seed(
    q: int = 20, k: int = 4, d_C: int = 5, d_S: int = 3,
    lam: int = 2, mu: int = 1, frac_negative: float = 0.5,
    max_overlap_ratio: float = 0.25, seed: Optional[int] = None
) -> HybridMISInstance:
    """Algorithm 1: Generate one compact hybrid CSP + spin-glass MIS seed."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    _validate_params(q, k, d_C, d_S)

    inst = HybridMISInstance()
    inst.q = q
    inst.k = k
    inst.d_C = d_C
    inst.d_S = d_S
    inst.lam = lam
    inst.mu = mu

    U = list(range(q))
    D = list(range(1, k + 1))

    # Step 2: CSP interaction graph
    inst.H_C = sample_connected_regular_graph(q, d_C)

    # Step 3: Signed spin-glass graph
    inst.H_S, inst.sigma = sample_signed_regular_graph(q, d_S, frac_negative)

    # Step 4: Balanced spin labels
    inst.tau = assign_balanced_spin_labels(q, k)

    # Collect edges
    E_C = set(_edge_key(u, v) for u, v in inst.H_C.edges())
    E_S = set(_edge_key(u, v) for u, v in inst.H_S.edges())
    E_U = E_C | E_S

    # Step 6: Spin-glass trap tables
    for (i, j) in E_S:
        sig = inst.sigma.get((i, j), inst.sigma.get((j, i), +1))
        inst.F_sg[(i, j)] = generate_spin_trap_table(
            k, mu, inst.tau[i], inst.tau[j], sig
        )

    # Step 5: CSP tables
    max_overlap = int(max_overlap_ratio * lam * k)
    for (i, j) in E_C:
        existing = inst.F_sg.get((i, j), None)
        inst.F_csp[(i, j)] = generate_balanced_csp_table(
            k, lam,
            existing_forbidden=existing,
            max_overlap=max_overlap if existing else -1
        )

    # Step 7: Merge layers
    for (i, j) in E_U:
        f_csp = inst.F_csp.get((i, j), set())
        f_sg = inst.F_sg.get((i, j), set())
        inst.F[(i, j)] = f_csp | f_sg

    # Step 8: Convert to MIS graph
    G = nx.Graph()

    node_id = 0
    for i in U:
        for a in D:
            inst.vertex_map[(i, a)] = node_id
            inst.reverse_map[node_id] = (i, a)
            G.add_node(node_id, variable=i, value=a, spin=inst.tau[i][a])
            node_id += 1

    # Variable cliques
    for i in U:
        block = [inst.vertex_map[(i, a)] for a in D]
        for idx1 in range(len(block)):
            for idx2 in range(idx1 + 1, len(block)):
                G.add_edge(block[idx1], block[idx2])

    # Conflict edges
    for (i, j), forbidden in inst.F.items():
        for (a, b) in forbidden:
            u = inst.vertex_map[(i, a)]
            v = inst.vertex_map[(j, b)]
            if not G.has_edge(u, v):
                G.add_edge(u, v)

    inst.G = G
    return inst

# =============================================================================
# Spin-glass analysis
# =============================================================================

def compute_spin_energy(
    sigma: Dict[Tuple[int, int], int],
    E_S: List[Tuple[int, int]],
    s: List[int]
) -> int:
    """Compute spin-glass energy E_sg(s)."""
    energy = 0
    for (i, j) in E_S:
        sig = sigma.get((i, j), sigma.get((j, i), +1))
        delta_ij = 0 if sig == +1 else 1
        xor_val = s[i] ^ s[j]
        if xor_val != delta_ij:
            energy += 1
    return energy


def analyze_spin_landscape(inst: HybridMISInstance) -> Dict[str, Any]:
    """Exhaustively analyze the spin-glass energy landscape (q <= 22)."""
    q = inst.q
    if q > 22:
        raise ValueError(f"Exhaustive spin analysis not feasible for q={q}")

    E_S = [_edge_key(u, v) for u, v in inst.H_S.edges()]
    sigma = inst.sigma

    energies = {}
    for bits in range(2 ** q):
        s = [(bits >> idx) & 1 for idx in range(q)]
        e = compute_spin_energy(sigma, E_S, s)
        energies[bits] = e

    E_star = min(energies.values())
    optima = [bits for bits, e in energies.items() if e == E_star]
    N_opt = len(optima)

    def is_local_minimum(bits, e):
        for idx in range(q):
            neighbor = bits ^ (1 << idx)
            if energies[neighbor] < e:
                return False
        return True

    local_minima = []
    for bits, e in energies.items():
        if e <= E_star + 2 and e > E_star:
            if is_local_minimum(bits, e):
                local_minima.append(bits)

    N_loc = len(local_minima)

    def hamming(a, b):
        return bin(a ^ b).count('1')

    if local_minima and optima:
        total_dist = sum(
            min(hamming(lm, opt) for opt in optima)
            for lm in local_minima
        )
        d_bar_opt = total_dist / len(local_minima)
    else:
        d_bar_opt = 0.0

    return {
        'E_star': E_star,
        'N_opt': N_opt,
        'N_loc': N_loc,
        'd_bar_opt': d_bar_opt,
        'all_optima': optima,
    }

def compute_spin_trap_score_from_analysis(
    analysis: Dict[str, Any],
    a_w: float = 1.0, b_w: float = 0.5, c_w: float = 2.0
) -> float:
    """Section 8.3: H_sg = a * N_loc + b * d_bar_opt - c * log(1 + N_opt)"""
    return (
        a_w * analysis['N_loc']
        + b_w * analysis['d_bar_opt']
        - c_w * math.log(1 + analysis['N_opt'])
    )


def compute_spin_trap_score(
    inst: HybridMISInstance,
    a_w: float = 1.0, b_w: float = 0.5, c_w: float = 2.0
) -> float:
    """Compute spin trap score for an instance."""
    analysis = analyze_spin_landscape(inst)
    return compute_spin_trap_score_from_analysis(analysis, a_w, b_w, c_w)


# =============================================================================
# Structural filters (Section 7)
# =============================================================================

def apply_structural_filters(
    inst: HybridMISInstance,
    max_cv: float = 0.3,
    min_kernel_ratio: float = 0.5
) -> Tuple[bool, str]:
    """Apply cheap structural filters before expensive solver calls."""
    G = inst.G

    if not nx.is_connected(G):
        return False, "Graph is disconnected"

    degrees = [d for _, d in G.degree()]
    mean_deg = np.mean(degrees)
    std_deg = np.std(degrees)
    cv = std_deg / mean_deg if mean_deg > 0 else float('inf')
    if cv > max_cv:
        return False, f"Degree CV={cv:.3f} > {max_cv}"

    if list(nx.articulation_points(G)):
        return False, "Graph has articulation points"

    reduced = G.copy()
    changed = True
    while changed:
        changed = False
        to_remove = []
        for v in list(reduced.nodes()):
            if reduced.degree(v) == 0:
                to_remove.append(v)
                changed = True
        reduced.remove_nodes_from(to_remove)

    kernel_ratio = (
        reduced.number_of_nodes() / G.number_of_nodes()
        if G.number_of_nodes() > 0 else 0
    )
    if kernel_ratio < min_kernel_ratio:
        return False, f"Kernel ratio={kernel_ratio:.3f} < {min_kernel_ratio}"

    return True, "Passed all filters"

def compute_reduction_resistance_score(inst: HybridMISInstance) -> float:
    """Section 8.4: kappa(G) / |V(G)|"""
    G = inst.G
    n = G.number_of_nodes()
    if n == 0:
        return 0.0

    reduced = G.copy()
    changed = True
    while changed:
        changed = False
        to_remove = []
        for v in list(reduced.nodes()):
            deg = reduced.degree(v)
            if deg == 0:
                to_remove.append(v)
                changed = True
            elif deg == 1:
                neighbor = list(reduced.neighbors(v))[0]
                to_remove.extend([v, neighbor])
                changed = True
                break
        reduced.remove_nodes_from(to_remove)

    return reduced.number_of_nodes() / n

# =============================================================================
# Mutations (Section 9.1)
# =============================================================================

def two_switch_rewire(G: nx.Graph, n_switches: int = 1) -> nx.Graph:
    """Perform 2-switches preserving degree sequence."""
    H = G.copy()
    edges = list(H.edges())

    for _ in range(n_switches):
        if len(edges) < 2:
            break
        for attempt in range(100):
            e1, e2 = random.sample(edges, 2)
            a, b = e1
            c, d = e2
            if len({a, b, c, d}) < 4:
                continue

            if not H.has_edge(a, d) and not H.has_edge(c, b):
                H.remove_edge(a, b)
                H.remove_edge(c, d)
                H.add_edge(a, d)
                H.add_edge(c, b)
                edges = list(H.edges())
                break
            elif not H.has_edge(a, c) and not H.has_edge(b, d):
                H.remove_edge(a, b)
                H.remove_edge(c, d)
                H.add_edge(a, c)
                H.add_edge(b, d)
                edges = list(H.edges())
                break

    return H

def _rebuild_instance(inst: HybridMISInstance):
    """Rebuild merged tables and MIS graph from current hidden structures."""
    q, k = inst.q, inst.k
    D = list(range(1, k + 1))
    U = list(range(q))

    E_C = set(_edge_key(u, v) for u, v in inst.H_C.edges())
    E_S = set(_edge_key(u, v) for u, v in inst.H_S.edges())
    E_U = E_C | E_S

    new_F_sg = {}
    for (i, j) in E_S:
        sig = inst.sigma.get((i, j), inst.sigma.get((j, i), +1))
        new_F_sg[(i, j)] = generate_spin_trap_table(
            k, inst.mu, inst.tau[i], inst.tau[j], sig
        )
    inst.F_sg = new_F_sg

    new_F_csp = {}
    max_overlap = int(0.25 * inst.lam * k)
    for (i, j) in E_C:
        existing_sg = inst.F_sg.get((i, j), None)
        old = inst.F_csp.get((i, j), None)
        if old is not None:
            new_F_csp[(i, j)] = old
        else:
            new_F_csp[(i, j)] = generate_balanced_csp_table(
                k, inst.lam,
                existing_forbidden=existing_sg,
                max_overlap=max_overlap if existing_sg else -1
            )
    inst.F_csp = new_F_csp

    inst.F = {}
    for (i, j) in E_U:
        f_csp = inst.F_csp.get((i, j), set())
        f_sg = inst.F_sg.get((i, j), set())
        inst.F[(i, j)] = f_csp | f_sg

    G = nx.Graph()
    inst.vertex_map = {}
    inst.reverse_map = {}

    node_id = 0
    for i in U:
        for a in D:
            inst.vertex_map[(i, a)] = node_id
            inst.reverse_map[node_id] = (i, a)
            G.add_node(node_id, variable=i, value=a, spin=inst.tau[i][a])
            node_id += 1

    for i in U:
        block = [inst.vertex_map[(i, a)] for a in D]
        for idx1 in range(len(block)):
            for idx2 in range(idx1 + 1, len(block)):
                G.add_edge(block[idx1], block[idx2])

    for (i, j), forbidden in inst.F.items():
        for (a, b) in forbidden:
            u = inst.vertex_map[(i, a)]
            v = inst.vertex_map[(j, b)]
            if not G.has_edge(u, v):
                G.add_edge(u, v)

    inst.G = G

def mutate_instance(
    inst: HybridMISInstance, mutation_type: Optional[str] = None
) -> HybridMISInstance:
    """Apply one random mutation to a HybridMISInstance."""
    mutations = [
        'rewire_HC', 'rewire_HS', 'flip_sign',
        'replace_csp', 'replace_spin', 'swap_tau'
    ]

    if mutation_type is None:
        mutation_type = random.choice(mutations)

    new_inst = HybridMISInstance()
    new_inst.q = inst.q
    new_inst.k = inst.k
    new_inst.d_C = inst.d_C
    new_inst.d_S = inst.d_S
    new_inst.lam = inst.lam
    new_inst.mu = inst.mu
    new_inst.H_C = inst.H_C.copy()
    new_inst.H_S = inst.H_S.copy()
    new_inst.sigma = dict(inst.sigma)
    new_inst.tau = {i: dict(t) for i, t in inst.tau.items()}
    new_inst.F_csp = {k_: set(v) for k_, v in inst.F_csp.items()}
    new_inst.F_sg = {k_: set(v) for k_, v in inst.F_sg.items()}

    if mutation_type == 'rewire_HC':
        new_H_C = two_switch_rewire(new_inst.H_C)
        if nx.is_connected(new_H_C):
            new_inst.H_C = new_H_C

    elif mutation_type == 'rewire_HS':
        new_H_S = two_switch_rewire(new_inst.H_S)
        if nx.is_connected(new_H_S):
            new_inst.H_S = new_H_S
            old_sigma = new_inst.sigma
            new_inst.sigma = {}
            for u, v in new_H_S.edges():
                ek = _edge_key(u, v)
                if ek in old_sigma:
                    new_inst.sigma[ek] = old_sigma[ek]
                else:
                    new_inst.sigma[ek] = random.choice([-1, +1])

    elif mutation_type == 'flip_sign':
        edges = list(new_inst.sigma.keys())
        if edges:
            edge = random.choice(edges)
            new_inst.sigma[edge] *= -1

    elif mutation_type == 'replace_csp':
        csp_edges = list(new_inst.F_csp.keys())
        if csp_edges:
            edge = random.choice(csp_edges)
            existing_sg = new_inst.F_sg.get(edge, None)
            max_overlap = int(0.25 * new_inst.lam * new_inst.k)
            new_inst.F_csp[edge] = generate_balanced_csp_table(
                new_inst.k, new_inst.lam,
                existing_forbidden=existing_sg,
                max_overlap=max_overlap if existing_sg else -1
            )

    elif mutation_type == 'replace_spin':
        sg_edges = list(new_inst.F_sg.keys())
        if sg_edges:
            edge = random.choice(sg_edges)
            i, j = edge
            sig = new_inst.sigma.get((i, j), new_inst.sigma.get((j, i), +1))
            new_inst.F_sg[edge] = generate_spin_trap_table(
                new_inst.k, new_inst.mu,
                new_inst.tau[i], new_inst.tau[j], sig
            )

    elif mutation_type == 'swap_tau':
        var = random.randint(0, new_inst.q - 1)
        D = list(range(1, new_inst.k + 1))
        D0 = [a for a in D if new_inst.tau[var][a] == 0]
        D1 = [a for a in D if new_inst.tau[var][a] == 1]
        if D0 and D1:
            a0 = random.choice(D0)
            a1 = random.choice(D1)
            new_inst.tau[var][a0] = 1
            new_inst.tau[var][a1] = 0

    _rebuild_instance(new_inst)
    return new_inst

# =============================================================================
# Algorithm 2: Solver-Aware Adversarial Refinement
# =============================================================================

def adversarial_refinement(
    q: int = 20, k: int = 4, d_C: int = 5, d_S: int = 3,
    lam: int = 2, mu: int = 1,
    population_size: int = 20,
    generations: int = 50,
    solver_config: Optional[SolverConfig] = None,
    use_solvers: bool = True,
    verbose: bool = True,
    seed: Optional[int] = None
) -> List[HybridMISInstance]:
    """Algorithm 2: Solver-aware adversarial refinement loop."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    _validate_params(q, k, d_C, d_S)

    if solver_config is None:
        solver_config = SolverConfig()

    portfolio = SolverPortfolio(solver_config)

    def score_instance(
        inst: HybridMISInstance, name: str = "inst", generation: int = 0
    ) -> float:
        if use_solvers:
            profile = portfolio.evaluate_instance(
                inst,
                run_cplex=CPLEX_AVAILABLE,
                run_heuristic=(
                    shutil.which(solver_config.redumis_binary) is not None
                    or shutil.which(solver_config.kamis_binary) is not None
                ),
                run_spin_analysis=(inst.q <= 22),
                instance_name=name
            )
            return profile.H_total
        else:
            score = 0.0
            try:
                h_sg = compute_spin_trap_score(inst)
                score += solver_config.w_sg * h_sg
            except Exception:
                pass

            h_red = compute_reduction_resistance_score(inst)
            score += solver_config.w_red * h_red

            passed, _ = apply_structural_filters(inst)
            if passed:
                score += 5.0

            return score

    # Generate initial population
    if verbose:
        logger.info(
            f"Generating initial population of {population_size} instances "
            f"(q={q}, k={k}, n={q * k})..."
        )

    archive: List[Tuple[float, HybridMISInstance]] = []
    for i in range(population_size):
        try:
            inst = generate_hybrid_mis_seed(q, k, d_C, d_S, lam, mu)
            s = score_instance(inst, name=f"seed_{i}", generation=0)
            archive.append((s, inst))
            if verbose:
                logger.info(
                    f"  Seed {i}: n={inst.n}, "
                    f"edges={inst.G.number_of_edges()}, score={s:.2f}"
                )
        except Exception as e:
            logger.warning(f"  Seed {i}: Failed ({e})")

    archive.sort(key=lambda x: -x[0])
    archive = archive[:max(population_size // 2, 2)]

    if not archive:
        logger.error("No valid seeds generated. Aborting.")
        return []

    best_ever_score = archive[0][0]
    stagnation_count = 0

    # Evolutionary refinement
    for gen in range(generations):
        children: List[Tuple[float, HybridMISInstance]] = []

        n_mutations = 1 if stagnation_count < 5 else random.randint(1, 3)

        for child_idx in range(population_size):
            if len(archive) >= 2:
                candidates = random.sample(archive, min(3, len(archive)))
                parent = max(candidates, key=lambda x: x[0])[1]
            else:
                parent = archive[0][1]

            try:
                child = parent
                for _ in range(n_mutations):
                    child = mutate_instance(child)

                passed, _ = apply_structural_filters(child)
                if not passed and random.random() > 0.3:
                    continue

                s = score_instance(
                    child,
                    name=f"gen{gen}_child{child_idx}",
                    generation=gen
                )
                children.append((s, child))
            except Exception:
                pass

        archive.extend(children)
        archive.sort(key=lambda x: -x[0])
        archive = archive[:population_size]

        current_best = archive[0][0]
        if current_best > best_ever_score + 0.01:
            best_ever_score = current_best
            stagnation_count = 0
        else:
            stagnation_count += 1

        if verbose and (gen + 1) % 5 == 0:
            best = archive[0][1]
            profile_str = ""
            if best.hardness is not None:
                h = best.hardness
                profile_str = (
                    f" | H_exact={h.H_exact:.2f}, H_heur={h.H_heur:.2f}, "
                    f"CPLEX_t={h.cplex_time:.1f}s, "
                    f"heur_best={h.heuristic_best}"
                )
            logger.info(
                f"Gen {gen + 1}/{generations}: "
                f"best_score={current_best:.2f}, "
                f"stagnation={stagnation_count}"
                f"{profile_str}"
            )

        if stagnation_count >= generations // 3:
            if verbose:
                logger.info(
                    f"Stopping early at generation {gen + 1} "
                    f"due to stagnation ({stagnation_count} gens)"
                )
            break

    return [inst for _, inst in archive]

# =============================================================================
# Section 10: Quiet planting
# =============================================================================

def generate_planted_then_frustrated(
    q: int = 20, k: int = 4, d_C: int = 5, d_S: int = 3,
    lam: int = 2, mu: int = 1, n_perturb: int = 2,
    seed: Optional[int] = None
) -> HybridMISInstance:
    """Section 10: Quiet Planting Then Frustration."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    _validate_params(q, k, d_C, d_S)

    D = list(range(1, k + 1))

    inst = HybridMISInstance()
    inst.q = q
    inst.k = k
    inst.d_C = d_C
    inst.d_S = d_S
    inst.lam = lam
    inst.mu = mu

    x_star = {i: random.choice(D) for i in range(q)}

    inst.H_C = sample_connected_regular_graph(q, d_C)
    inst.H_S, inst.sigma = sample_signed_regular_graph(q, d_S)
    inst.tau = assign_balanced_spin_labels(q, k)

    E_C = set(_edge_key(u, v) for u, v in inst.H_C.edges())
    E_S = set(_edge_key(u, v) for u, v in inst.H_S.edges())
    E_U = E_C | E_S

    for (i, j) in E_S:
        sig = inst.sigma.get((i, j), inst.sigma.get((j, i), +1))
        for _ in range(100):
            table = generate_spin_trap_table(k, mu, inst.tau[i], inst.tau[j], sig)
            if (x_star[i], x_star[j]) not in table:
                break
        inst.F_sg[(i, j)] = table

    max_overlap = int(0.25 * lam * k)
    for (i, j) in E_C:
        existing_sg = inst.F_sg.get((i, j), None)
        for _ in range(100):
            table = generate_balanced_csp_table(
                k, lam,
                existing_forbidden=existing_sg,
                max_overlap=max_overlap if existing_sg else -1
            )
            if (x_star[i], x_star[j]) not in table:
                break
        inst.F_csp[(i, j)] = table

    for (i, j) in E_U:
        f_csp = inst.F_csp.get((i, j), set())
        f_sg = inst.F_sg.get((i, j), set())
        inst.F[(i, j)] = f_csp | f_sg

    perturbable = [
        e for e in E_U
        if (x_star[e[0]], x_star[e[1]]) not in inst.F[e]
    ]
    n_perturb_actual = min(n_perturb, len(perturbable))

    for edge in random.sample(perturbable, n_perturb_actual):
        i, j = edge
        inst.F[edge].add((x_star[i], x_star[j]))

    G = nx.Graph()
    inst.vertex_map = {}
    inst.reverse_map = {}

    node_id = 0
    for i in range(q):
        for a in D:
            inst.vertex_map[(i, a)] = node_id
            inst.reverse_map[node_id] = (i, a)
            G.add_node(node_id, variable=i, value=a, spin=inst.tau[i][a])
            node_id += 1

    for i in range(q):
        block = [inst.vertex_map[(i, a)] for a in D]
        for idx1 in range(len(block)):
            for idx2 in range(idx1 + 1, len(block)):
                G.add_edge(block[idx1], block[idx2])

    for (i, j), forbidden in inst.F.items():
        for (a, b) in forbidden:
            u = inst.vertex_map[(i, a)]
            v = inst.vertex_map[(j, b)]
            if not G.has_edge(u, v):
                G.add_edge(u, v)

    inst.G = G
    return inst

# =============================================================================
# Dense instance configuration
# =============================================================================

def compute_max_edges(q: int, k: int, d_C: int, d_S: int,
                      lam: int, mu: int) -> dict:
    """Estimate edge counts for a given parameter set."""
    from math import comb

    n = q * k
    max_possible = comb(n, 2)

    clique_edges = q * comb(k, 2)
    n_csp_graph_edges = q * d_C // 2
    csp_conflict_max = n_csp_graph_edges * lam * k
    n_sg_graph_edges = q * d_S // 2
    sg_conflict_max = n_sg_graph_edges * mu * k

    estimated_total = clique_edges + csp_conflict_max + sg_conflict_max
    density = estimated_total / max_possible if max_possible > 0 else 0

    return {
        'n': n,
        'max_possible_edges': max_possible,
        'clique_edges': clique_edges,
        'csp_conflict_max': csp_conflict_max,
        'sg_conflict_max': sg_conflict_max,
        'estimated_total': estimated_total,
        'estimated_density': min(density, 1.0),
        'n_csp_interaction_edges': n_csp_graph_edges,
        'n_sg_interaction_edges': n_sg_graph_edges,
    }

def suggest_dense_params(
    target_density: float = 0.5,
    max_n: int = 99,
    verbose: bool = True
) -> Optional[dict]:
    """Search for parameter combinations achieving a target density."""
    from math import comb

    best = None
    best_gap = float('inf')
    candidates = []

    for k in [4, 6, 8, 10]:
        for q in range(4, max_n // k + 1):
            n = q * k
            if n >= 100:
                continue

            max_edges = comb(n, 2)
            if max_edges == 0:
                continue

            for d_C in range(2, q):
                if (q * d_C) % 2 != 0:
                    continue

                for d_S in range(2, q):
                    if (q * d_S) % 2 != 0:
                        continue

                    for lam_val in range(1, k):
                        for mu_val in range(1, k // 2 + 1):
                            info = compute_max_edges(
                                q, k, d_C, d_S, lam_val, mu_val
                            )
                            density = info['estimated_density']
                            gap = abs(density - target_density)

                            if gap < best_gap:
                                best_gap = gap
                                best = {
                                    'q': q, 'k': k,
                                    'd_C': d_C, 'd_S': d_S,
                                    'lam': lam_val, 'mu': mu_val,
                                    'estimated_density': density,
                                    'estimated_edges': info['estimated_total'],
                                    'n': n,
                                }

                            if gap < 0.02:
                                candidates.append({
                                    'q': q, 'k': k,
                                    'd_C': d_C, 'd_S': d_S,
                                    'lam': lam_val, 'mu': mu_val,
                                    'estimated_density': density,
                                    'estimated_edges': info['estimated_total'],
                                    'n': n,
                                })

    if verbose and best:
        print(f"Target density: {target_density:.2f}")
        print(f"Best params found:")
        for key, val in best.items():
            print(f"  {key}: {val}")

    if verbose and candidates:
        print(f"\n{len(candidates)} near-optimal parameter sets found.")
        seen_n = set()
        print("\nDiverse options:")
        for c in sorted(candidates, key=lambda x: x['n']):
            if c['n'] not in seen_n:
                seen_n.add(c['n'])
                print(
                    f"  n={c['n']:3d} (q={c['q']:2d}, k={c['k']}): "
                    f"d_C={c['d_C']}, d_S={c['d_S']}, "
                    f"lam={c['lam']}, mu={c['mu']}  "
                    f"-> density~{c['estimated_density']:.2f}"
                )
                if len(seen_n) >= 8:
                    break

    return best

# Paper-valid density presets
DENSITY_PRESETS = {
    'sparse': {
        'q': 20, 'k': 4, 'd_C': 5, 'd_S': 3, 'lam': 2, 'mu': 1,
    },
    'medium': {
        'q': 20, 'k': 4, 'd_C': 9, 'd_S': 7, 'lam': 3, 'mu': 2,
    },
    'dense': {
        'q': 20, 'k': 4, 'd_C': 13, 'd_S': 11, 'lam': 3, 'mu': 2,
    },
    'very_dense': {
        'q': 20, 'k': 4, 'd_C': 17, 'd_S': 15, 'lam': 3, 'mu': 2,
    },
    'extreme': {
        'q': 20, 'k': 4, 'd_C': 19, 'd_S': 17, 'lam': 3, 'mu': 2,
    },
    'large_domain_dense': {
        'q': 18, 'k': 6, 'd_C': 13, 'd_S': 11, 'lam': 3, 'mu': 2,
    },
    'large_graph': {
        'q': 50, 'k': 10, 'd_C': 19, 'd_S': 17, 'lam': 4, 'mu': 3,
    },
    'large_graph_320': {
        'q': 40, 'k': 8, 'd_C': 13, 'd_S': 11, 'lam': 3, 'mu': 2,
    },
    'medium_graph_320': {
        'q': 30, 'k': 6, 'd_C': 13, 'd_S': 11, 'lam': 3, 'mu': 2,
    },
}



def generate_dense_instance(
    preset: str = 'dense',
    seed: Optional[int] = None,
    custom_params: Optional[dict] = None,
) -> HybridMISInstance:
    """Generate an instance using a density preset or custom parameters."""
    if custom_params:
        params = custom_params
    elif preset in DENSITY_PRESETS:
        params = DENSITY_PRESETS[preset]
    else:
        raise ValueError(
            f"Unknown preset '{preset}'. "
            f"Available: {list(DENSITY_PRESETS.keys())}"
        )

    info = compute_max_edges(**{k_: v for k_, v in params.items()})
    logger.info(
        f"Generating '{preset}' instance: n={info['n']}, "
        f"estimated edges~{info['estimated_total']}, "
        f"density~{info['estimated_density']:.2f}"
    )

    inst = generate_hybrid_mis_seed(
        q=params['q'], k=params['k'],
        d_C=params['d_C'], d_S=params['d_S'],
        lam=params['lam'], mu=params['mu'],
        seed=seed
    )

    actual_density = (
        2 * inst.G.number_of_edges() /
        (inst.n * (inst.n - 1))
        if inst.n > 1 else 0
    )
    logger.info(
        f"Actual: {inst.G.number_of_nodes()} vertices, "
        f"{inst.G.number_of_edges()} edges, "
        f"density={actual_density:.3f}"
    )

    return inst

# =============================================================================
# Export utilities
# =============================================================================

def export_dimacs(inst: HybridMISInstance, filename: str):
    """Export the MIS graph in DIMACS format."""
    G = inst.G
    n = G.number_of_nodes()
    m = G.number_of_edges()

    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.',
                exist_ok=True)

    with open(filename, 'w') as f:
        f.write(f"c Hybrid CSP+SpinGlass MIS instance\n")
        f.write(f"c q={inst.q}, k={inst.k}, n={inst.n}\n")
        f.write(
            f"c d_C={inst.d_C}, d_S={inst.d_S}, "
            f"lambda={inst.lam}, mu={inst.mu}\n"
        )
        if inst.hardness:
            h = inst.hardness
            f.write(f"c H_total={h.H_total:.4f}\n")
            f.write(
                f"c CPLEX: size={h.cplex_mis_size}, "
                f"time={h.cplex_time:.2f}s, nodes={h.cplex_nodes}\n"
            )
            f.write(
                f"c Heuristic: best={h.heuristic_best}, "
                f"mean={h.heuristic_mean:.1f}\n"
            )
        f.write(f"p edge {n} {m}\n")
        for u, v in G.edges():
            f.write(f"e {u + 1} {v + 1}\n")

def export_metis(inst: HybridMISInstance, filename: str):
    """Export the MIS graph in METIS format (for KaMIS/ReduMIS)."""
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.',
                exist_ok=True)
    ReduMISSolver.write_metis(inst.G, filename)


def export_edge_list(inst: HybridMISInstance, filename: str):
    """Export as a simple edge list."""
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.',
                exist_ok=True)
    G = inst.G
    with open(filename, 'w') as f:
        f.write(
            f"# Hybrid CSP+SpinGlass MIS: "
            f"n={inst.n}, m={G.number_of_edges()}\n"
        )
        for u, v in G.edges():
            f.write(f"{u} {v}\n")


def export_full_report(inst: HybridMISInstance, filename: str):
    """Export a full human-readable report."""
    G = inst.G
    n = G.number_of_nodes()
    m = G.number_of_edges()
    degrees = [d for _, d in G.degree()]
    density = 2 * m / (n * (n - 1)) if n > 1 else 0

    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.',
                exist_ok=True)

    with open(filename, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("HYBRID CSP + SPIN-GLASS MIS INSTANCE REPORT\n")
        f.write("=" * 70 + "\n\n")

        f.write("--- Construction Parameters ---\n")
        f.write(f"  q (variables)     = {inst.q}\n")
        f.write(f"  k (domain size)   = {inst.k}\n")
        f.write(f"  n = q*k           = {inst.n}\n")
        f.write(f"  d_C (CSP degree)  = {inst.d_C}\n")
        f.write(f"  d_S (spin degree) = {inst.d_S}\n")
        f.write(f"  lambda            = {inst.lam}\n")
        f.write(f"  mu                = {inst.mu}\n\n")

        f.write("--- Graph Statistics ---\n")
        f.write(f"  Vertices          = {n}\n")
        f.write(f"  Edges             = {m}\n")
        f.write(f"  Density           = {density:.4f}\n")
        f.write(f"  Degree min/max    = {min(degrees)}/{max(degrees)}\n")
        f.write(
            f"  Degree mean+/-std = "
            f"{np.mean(degrees):.1f} +/- {np.std(degrees):.2f}\n"
        )
        f.write(f"  Connected         = {nx.is_connected(G)}\n\n")

        if inst.hardness:
            h = inst.hardness

            f.write("--- CPLEX Results ---\n")
            f.write(f"  MIS size          = {h.cplex_mis_size}\n")
            f.write(f"  Solve time        = {h.cplex_time:.2f}s\n")
            f.write(f"  B&B nodes         = {h.cplex_nodes}\n")
            f.write(f"  MIP gap           = {h.cplex_gap:.6f}\n")
            f.write(f"  LP bound          = {h.cplex_lp_bound:.2f}\n")
            f.write(f"  Timed out         = {h.cplex_timed_out}\n\n")

            f.write("--- ReduMIS Results ---\n")
            f.write(f"  Best MIS          = {h.heuristic_best}\n")
            f.write(f"  Worst MIS         = {h.heuristic_worst}\n")
            f.write(
                f"  Mean +/- std      = "
                f"{h.heuristic_mean:.1f} +/- {h.heuristic_std:.2f}\n"
            )
            f.write(f"  Hit optimum       = {h.heuristic_hit_optimum}\n\n")

            f.write("--- Spin-Glass Landscape ---\n")
            f.write(f"  E*_sg             = {h.E_star}\n")
            f.write(f"  N_opt             = {h.N_opt}\n")
            f.write(f"  N_loc             = {h.N_loc}\n")
            f.write(f"  d_bar_opt         = {h.d_bar_opt:.2f}\n")
            f.write(f"  Spin trap score   = {h.spin_trap_score:.2f}\n\n")

            f.write("--- Composite Scores ---\n")
            f.write(f"  H_exact           = {h.H_exact:.4f}\n")
            f.write(f"  H_heur            = {h.H_heur:.4f}\n")
            f.write(f"  H_total           = {h.H_total:.4f}\n")
            f.write(f"  Reduction resist. = {h.reduction_resistance:.4f}\n")
            f.write(f"  Passed filters    = {h.passed_filters}\n")

# =============================================================================
# Main
# =============================================================================

def main():
    """Main entry point with CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Hybrid CSP + Spin-Glass Hard MIS Instance Generator"
    )
    parser.add_argument("--q", type=int, default=20,
                        help="Number of hidden variables")
    parser.add_argument("--k", type=int, default=4,
                        help="Domain size (must be even)")
    parser.add_argument("--d_C", type=int, default=5,
                        help="CSP graph degree")
    parser.add_argument("--d_S", type=int, default=3,
                        help="Spin-glass graph degree")
    parser.add_argument("--lam", type=int, default=2,
                        help="CSP forbidden pair density")
    parser.add_argument("--mu", type=int, default=1,
                        help="Spin trap density")
    parser.add_argument("--pop", type=int, default=10,
                        help="Population size")
    parser.add_argument("--gens", type=int, default=20,
                        help="Generations")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")
    parser.add_argument("--cplex_time", type=float, default=60.0,
                        help="CPLEX time limit per instance (seconds)")
    parser.add_argument("--heur_time", type=float, default=30.0,
                        help="ReduMIS time limit per run (seconds)")
    parser.add_argument("--heur_runs", type=int, default=3,
                        help="Number of ReduMIS runs per instance")
    parser.add_argument("--no_solvers", action="store_true",
                        help="Skip external solver calls (proxy scoring only)")
    parser.add_argument("--output_prefix", type=str, default="hard_mis",
                        help="Output filename prefix")
    parser.add_argument(
        "--mode", type=str, default="full",
        choices=["single", "planted", "full", "dense_demo", "find_params"],
        help="Generation mode"
    )
    parser.add_argument(
        "--density", type=str, default=None,
        choices=list(DENSITY_PRESETS.keys()),
        help="Use a density preset (overrides q/k/d_C/d_S/lam/mu)"
    )
    parser.add_argument(
        "--target_density", type=float, default=None,
        help="Target density for --mode find_params"
    )
    parser.add_argument(
        "--log_dir", type=str, default="logs",
        help="Base directory for per-run log folders"
    )

    args = parser.parse_args()

    # Apply density preset BEFORE setting up logging so the directory name
    # reflects the actual parameters that will be used.
    if args.density:
        preset = DENSITY_PRESETS[args.density]
        args.q = preset['q']
        args.k = preset['k']
        args.d_C = preset['d_C']
        args.d_S = preset['d_S']
        args.lam = preset['lam']
        args.mu = preset['mu']

    # ---- Set up per-run logging ----
    log_dir = setup_run_logging(args, base_log_dir=args.log_dir)

    # Redirect output_prefix into the log directory so all artefacts live together
    output_prefix = str(log_dir / args.output_prefix)

    print("=" * 70)
    print("Hybrid CSP + Spin-Glass Hard MIS Instance Generator")
    print("with CPLEX 22.1 + ReduMIS Solver Integration")
    print(f"Log directory: {log_dir.resolve()}")
    print("=" * 70)

    if args.density:
        logger.info(f"Using density preset '{args.density}': {DENSITY_PRESETS[args.density]}")

    # Validate (except for find_params mode)
    if args.mode != "find_params":
        if args.q * args.k >= 1000:
            logger.error(f"n = q*k = {args.q * args.k} must be < 100")
            sys.exit(1)

    # Solver availability
    logger.info("--- Solver Availability ---")
    logger.info(
        f"  CPLEX (docplex): "
        f"{'AVAILABLE' if CPLEX_AVAILABLE else 'NOT FOUND'}"
    )
    redumis_path = shutil.which("redumis")
    kamis_path = shutil.which("weighted_branch_reduce")
    logger.info(
        f"  ReduMIS:         "
        f"{'AVAILABLE at ' + redumis_path if redumis_path else 'NOT FOUND'}"
    )
    logger.info(
        f"  KaMIS:           "
        f"{'AVAILABLE at ' + kamis_path if kamis_path else 'NOT FOUND'}"
    )

    solver_config = SolverConfig(
        cplex_time_limit=args.cplex_time,
        heuristic_time_limit=args.heur_time,
        heuristic_runs=args.heur_runs,
    )

    use_solvers = not args.no_solvers
    if not CPLEX_AVAILABLE and not redumis_path and not kamis_path:
        if use_solvers:
            logger.warning("No solvers found. Using proxy scoring.")
            use_solvers = False

    # ========== MODE: find_params ==========
    if args.mode == "find_params":
        target = args.target_density or 0.5
        logger.info(f"--- Finding parameters for density ~ {target} ---")
        suggest_dense_params(target_density=target, verbose=True)
        return

    # ========== MODE: dense_demo ==========
    if args.mode == "dense_demo":
        logger.info("--- Dense Instance Comparison ---")
        for preset_name in ['sparse', 'medium', 'dense', 'very_dense', 'extreme']:
            inst = generate_dense_instance(preset=preset_name, seed=args.seed)
            G = inst.G
            n = G.number_of_nodes()
            m = G.number_of_edges()
            density = 2 * m / (n * (n - 1)) if n > 1 else 0
            degrees = [d for _, d in G.degree()]
            logger.info(
                f"  {preset_name:20s}: n={n:3d}, m={m:5d}, "
                f"density={density:.3f}, "
                f"deg=[{min(degrees)}-{max(degrees)}], "
                f"mean_deg={np.mean(degrees):.1f}"
            )

            export_dimacs(inst, f"{output_prefix}_{preset_name}.dimacs")
            export_metis(inst, f"{output_prefix}_{preset_name}.metis")

        logger.info(f"Exported all presets with prefix '{output_prefix}_*'")
        return

    # ========== MODE: single ==========
    if args.mode == "single":
        logger.info(
            f"--- Single Seed "
            f"(q={args.q}, k={args.k}, n={args.q * args.k}) ---"
        )
        inst = generate_hybrid_mis_seed(
            q=args.q, k=args.k, d_C=args.d_C, d_S=args.d_S,
            lam=args.lam, mu=args.mu, seed=args.seed
        )
        G = inst.G
        n = G.number_of_nodes()
        m = G.number_of_edges()
        density = 2 * m / (n * (n - 1)) if n > 1 else 0
        logger.info(f"Graph: {n} vertices, {m} edges, density={density:.3f}")

        portfolio = SolverPortfolio(solver_config)
        profile = portfolio.evaluate_instance(
            inst,
            run_cplex=CPLEX_AVAILABLE and use_solvers,
            run_heuristic=use_solvers and bool(redumis_path or kamis_path),
            instance_name="single_seed"
        )

        logger.info("--- Results ---")
        logger.info(f"  H_exact = {profile.H_exact:.4f}")
        logger.info(f"  H_heur  = {profile.H_heur:.4f}")
        logger.info(f"  H_total = {profile.H_total:.4f}")

        export_dimacs(inst, f"{output_prefix}.dimacs")
        export_metis(inst, f"{output_prefix}.metis")
        export_full_report(inst, f"{output_prefix}_report.txt")
        logger.info(f"Exported: {output_prefix}.dimacs, .metis, _report.txt")

    # ========== MODE: planted ==========
    elif args.mode == "planted":
        logger.info("--- Planted Then Frustrated ---")
        inst = generate_planted_then_frustrated(
            q=args.q, k=args.k, d_C=args.d_C, d_S=args.d_S,
            lam=args.lam, mu=args.mu, n_perturb=3, seed=args.seed
        )
        G = inst.G
        n = G.number_of_nodes()
        m = G.number_of_edges()
        density = 2 * m / (n * (n - 1)) if n > 1 else 0
        logger.info(f"Graph: {n} vertices, {m} edges, density={density:.3f}")

        if use_solvers:
            portfolio = SolverPortfolio(solver_config)
            profile = portfolio.evaluate_instance(
                inst,
                run_cplex=CPLEX_AVAILABLE,
                run_heuristic=bool(redumis_path or kamis_path),
                instance_name="planted"
            )
            logger.info(f"  H_total = {profile.H_total:.4f}")

        export_dimacs(inst, f"{output_prefix}_planted.dimacs")
        export_metis(inst, f"{output_prefix}_planted.metis")
        logger.info(f"Exported: {output_prefix}_planted.dimacs, .metis")

    # ========== MODE: full ==========
    else:
        logger.info("--- Adversarial Refinement ---")
        logger.info(
            f"  Parameters: q={args.q}, k={args.k}, n={args.q * args.k}"
        )
        logger.info(
            f"  d_C={args.d_C}, d_S={args.d_S}, "
            f"lam={args.lam}, mu={args.mu}"
        )
        logger.info(f"  Population: {args.pop}, Generations: {args.gens}")
        logger.info(f"  Solvers: {'ENABLED' if use_solvers else 'PROXY ONLY'}")

        best_instances = adversarial_refinement(
            q=args.q, k=args.k, d_C=args.d_C, d_S=args.d_S,
            lam=args.lam, mu=args.mu,
            population_size=args.pop,
            generations=args.gens,
            solver_config=solver_config,
            use_solvers=use_solvers,
            verbose=True,
            seed=args.seed
        )

        if best_instances:
            logger.info(f"--- Top {min(5, len(best_instances))} Instances ---")
            for rank, inst in enumerate(best_instances[:5]):
                G = inst.G
                n = G.number_of_nodes()
                m = G.number_of_edges()
                density = 2 * m / (n * (n - 1)) if n > 1 else 0
                h = inst.hardness
                h_total = h.H_total if h else 0.0
                cplex_info = ""
                heur_info = ""
                if h:
                    cplex_info = (
                        f"CPLEX[size={h.cplex_mis_size}, "
                        f"t={h.cplex_time:.1f}s, "
                        f"nodes={h.cplex_nodes}]"
                    )
                    heur_info = (
                        f"ReduMIS[best={h.heuristic_best}, "
                        f"mean={h.heuristic_mean:.1f}]"
                    )

                logger.info(
                    f"  #{rank + 1}: n={n}, m={m}, "
                    f"density={density:.3f}, "
                    f"H={h_total:.2f} "
                    f"{cplex_info} {heur_info}"
                )

                prefix = f"{output_prefix}_rank{rank + 1}"
                export_dimacs(inst, f"{prefix}.dimacs")
                export_metis(inst, f"{prefix}.metis")
                export_full_report(inst, f"{prefix}_report.txt")

            logger.info(
                f"Exported top instances with prefix "
                f"'{output_prefix}_rank*'"
            )

    logger.info("=" * 70)
    logger.info("Done.")
    logger.info("=" * 70)

if __name__ == "__main__":
    main()