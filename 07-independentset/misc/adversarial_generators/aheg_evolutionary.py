#!/usr/bin/env python3
"""
AHEG-MIS: Adversarial Hard-instance Evolutionary Generator for Maximum Independent Set.

Implements the proposal:
  "An Adversarial Generator of Small Hard Instances for Maximum Independent Set
   Updated to Target Both MILP/Branch-and-Cut and State-of-the-Art Heuristics"

Requirements:
  - Python 3.8+
  - networkx, numpy
  - cplex  (IBM ILOG CPLEX Python API)
  - redumis binary on PATH (or path configured below)

Usage:
  python problems/mis/generators/aheg_evolutionary.py [options]

All results are logged under logs/<run_folder>/
"""

import os
import sys
import json
import time
import copy
import random
import logging
import argparse
import subprocess
import tempfile
import shutil
import math
import hashlib
from datetime import datetime
from pathlib import Path
from itertools import combinations
from collections import defaultdict

import numpy as np
import networkx as nx

# ---------------------------------------------------------------------------
# Try importing cplex
# ---------------------------------------------------------------------------
try:
    import cplex
    HAS_CPLEX = True
except ImportError:
    HAS_CPLEX = False

# ---------------------------------------------------------------------------
# Configuration for external solvers
# ---------------------------------------------------------------------------
REDUMIS_BINARY = shutil.which("redumis") or shutil.which("ReduMIS") or "redumis"


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description="AHEG-MIS: Adversarial hard MIS instance generator")
    p.add_argument("--n", type=int, default=64, help="Target number of vertices (< 100)")
    p.add_argument("--B_ex", type=float, default=10.0, help="Exact solver budget in seconds")
    p.add_argument("--B_heu", type=float, default=1.0, help="Heuristic budget in seconds")
    p.add_argument("--T", type=int, default=20, help="Number of outer iterations")
    p.add_argument("--M", type=int, default=10, help="Archive size")
    p.add_argument("--seed", type=int, default=42, help="Random seed")
    p.add_argument("--p_low", type=float, default=0.45, help="Lower bound on background edge probability")
    p.add_argument("--p_high", type=float, default=0.65, help="Upper bound on background edge probability")
    p.add_argument("--c1_low", type=int, default=8, help="Lower bound on decoy clique size")
    p.add_argument("--c1_high", type=int, default=12, help="Upper bound on decoy clique size")
    p.add_argument("--cert_budget", type=float, default=120.0, help="Certification oracle budget (seconds)")
    p.add_argument("--heu_seeds", type=int, default=5, help="Number of heuristic random seeds")
    p.add_argument("--mutations_per_parent", type=int, default=5, help="Mutations per parent per iteration")
    p.add_argument("--log_dir", type=str, default="logs", help="Base logging directory")
    # Exact solver hardness weights
    p.add_argument("--a1", type=float, default=5.0, help="Weight for unsolved indicator")
    p.add_argument("--a2", type=float, default=3.0, help="Weight for optimality gap")
    p.add_argument("--a3", type=float, default=1.0, help="Weight for log(B&B nodes)")
    p.add_argument("--a4", type=float, default=2.0, help="Weight for root gap")
    p.add_argument("--a5", type=float, default=2.0, help="Weight for cut gap")
    p.add_argument("--a6", type=float, default=3.0, help="Weight for sigmoid time pressure")
    p.add_argument("--a7", type=float, default=2.0, help="Weight for linear time ratio")
    p.add_argument("--a8", type=float, default=1.5, help="Weight for log(simplex iterations)")
    # Heuristic hardness weights
    p.add_argument("--b1", type=float, default=4.0, help="Weight for (1-p_h) heuristic fail rate")
    p.add_argument("--b2", type=float, default=3.0, help="Weight for heuristic quality gap")
    p.add_argument("--b3", type=float, default=1.0, help="Weight for log(tau_h) heuristic time")
    # Structural weights
    p.add_argument("--lam", type=float, default=1.0, help="Weight for kernel residual fraction")
    p.add_argument("--mu", type=float, default=0.5, help="Weight for near-optima density proxy")
    p.add_argument("--xi", type=float, default=0.5, help="Weight for symmetry proxy")
    p.add_argument("--zeta", type=float, default=1.0, help="Weight for polyhedral weakness proxy")
    # Portfolio weights
    p.add_argument("--w_ex", type=float, default=1.0, help="Overall weight for exact portfolio")
    p.add_argument("--w_heu", type=float, default=1.0, help="Overall weight for heuristic portfolio")
    return p.parse_args()


# ===========================================================================
# Logging setup
# ===========================================================================
def setup_logging(args):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = (
        f"n{args.n}_Bex{args.B_ex}_Bheu{args.B_heu}_T{args.T}_M{args.M}"
        f"_seed{args.seed}_{ts}"
    )
    run_path = Path(args.log_dir) / folder_name
    run_path.mkdir(parents=True, exist_ok=True)

    (run_path / "graphs" / "seeds").mkdir(parents=True, exist_ok=True)
    (run_path / "graphs" / "archive").mkdir(parents=True, exist_ok=True)
    (run_path / "graphs" / "offspring").mkdir(parents=True, exist_ok=True)
    (run_path / "graphs" / "best").mkdir(parents=True, exist_ok=True)
    (run_path / "evals" / "seeds").mkdir(parents=True, exist_ok=True)
    (run_path / "evals" / "archive").mkdir(parents=True, exist_ok=True)
    (run_path / "evals" / "offspring").mkdir(parents=True, exist_ok=True)
    (run_path / "iterations").mkdir(parents=True, exist_ok=True)

    log_file = run_path / "run.log"
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(str(log_file))
    fh.setFormatter(formatter)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    root_logger.addHandler(fh)
    root_logger.addHandler(sh)

    logging.info(f"Run directory: {run_path}")
    with open(run_path / "args.json", "w") as f:
        json.dump(vars(args), f, indent=2)

    return run_path


# ===========================================================================
# Graph I/O helpers
# ===========================================================================
def graph_to_dimacs(G: nx.Graph) -> str:
    n = G.number_of_nodes()
    m = G.number_of_edges()
    mapping = {v: i + 1 for i, v in enumerate(sorted(G.nodes()))}
    lines = [f"p edge {n} {m}"]
    for u, v in G.edges():
        lines.append(f"e {mapping[u]} {mapping[v]}")
    return "\n".join(lines) + "\n"


def graph_to_metis(G: nx.Graph) -> str:
    n = G.number_of_nodes()
    m = G.number_of_edges()
    mapping = {v: i for i, v in enumerate(sorted(G.nodes()))}
    lines = [f"{n} {m}"]
    adj = defaultdict(list)
    for u, v in G.edges():
        adj[mapping[u]].append(mapping[v])
        adj[mapping[v]].append(mapping[u])
    for i in range(n):
        neighbors = sorted([x + 1 for x in adj[i]])
        lines.append(" ".join(map(str, neighbors)) if neighbors else "")
    return "\n".join(lines) + "\n"


def save_graph_all_formats(G: nx.Graph, directory: Path, name: str) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    paths = {}

    dimacs_path = directory / f"{name}.clq"
    with open(dimacs_path, "w") as f:
        f.write(graph_to_dimacs(G))
    paths["dimacs"] = str(dimacs_path)

    metis_path = directory / f"{name}.metis"
    with open(metis_path, "w") as f:
        f.write(graph_to_metis(G))
    paths["metis"] = str(metis_path)

    edgelist_path = directory / f"{name}.edgelist"
    nx.write_edgelist(G, str(edgelist_path))
    paths["edgelist"] = str(edgelist_path)

    graphml_path = directory / f"{name}.graphml"
    nx.write_graphml(G, str(graphml_path))
    paths["graphml"] = str(graphml_path)

    if G.number_of_nodes() <= 200:
        adj_path = directory / f"{name}_adj.npy"
        np.save(str(adj_path), nx.to_numpy_array(G))
        paths["adj_npy"] = str(adj_path)

    return paths


def write_temp_graph(G: nx.Graph, fmt="dimacs"):
    fd, path = tempfile.mkstemp(suffix=".graph" if fmt == "metis" else ".clq")
    with os.fdopen(fd, "w") as f:
        if fmt == "metis":
            f.write(graph_to_metis(G))
        else:
            f.write(graph_to_dimacs(G))
    return path


def graph_fingerprint(G: nx.Graph) -> str:
    edges = sorted((min(u, v), max(u, v)) for u, v in G.edges())
    return hashlib.md5(str((sorted(G.nodes()), edges)).encode()).hexdigest()


# ===========================================================================
# CPLEX MIS solver
# ===========================================================================

class CplexMISResult:
    def __init__(self):
        self.incumbent = 0
        self.best_bound = float('inf')
        self.gap = float('inf')
        self.nodes = 0
        self.solved = False
        self.time = 0.0
        self.solution = []
        self.simplex_iters = 0


def solve_mis_cplex(G: nx.Graph, time_limit: float = 10.0, root_only: bool = False,
                    cut_budget_only: bool = False) -> CplexMISResult:
    result = CplexMISResult()
    if not HAS_CPLEX:
        return result

    nodes_list = sorted(G.nodes())
    n = len(nodes_list)
    if n == 0:
        return result
    node_idx = {v: i for i, v in enumerate(nodes_list)}
    var_names = [f"x{i}" for i in range(n)]

    try:
        prob = cplex.Cplex()
        prob.set_log_stream(None)
        prob.set_results_stream(None)
        prob.set_warning_stream(None)
        prob.set_error_stream(None)

        prob.objective.set_sense(prob.objective.sense.maximize)
        prob.variables.add(
            obj=[1.0] * n, lb=[0.0] * n, ub=[1.0] * n,
            types=["B"] * n, names=var_names,
        )

        rows = []
        for u, v in G.edges():
            i, j = node_idx[u], node_idx[v]
            rows.append(cplex.SparsePair(ind=[var_names[i], var_names[j]], val=[1.0, 1.0]))
        if rows:
            prob.linear_constraints.add(
                lin_expr=rows, senses=["L"] * len(rows), rhs=[1.0] * len(rows),
            )

        prob.parameters.timelimit.set(time_limit)
        prob.parameters.threads.set(1)
        prob.parameters.mip.display.set(0)

        if root_only:
            prob.parameters.mip.limits.nodes.set(0)
            prob.variables.set_types([(i, prob.variables.type.continuous) for i in range(n)])

        if cut_budget_only:
            prob.parameters.mip.limits.nodes.set(1)

        t0 = time.time()
        prob.solve()
        result.time = time.time() - t0

        status = prob.solution.get_status()

        if prob.solution.is_primal_feasible():
            vals = prob.solution.get_values()
            result.incumbent = int(round(sum(vals)))
            result.solution = [nodes_list[i] for i in range(n) if vals[i] > 0.5]

        try:
            result.best_bound = prob.solution.MIP.get_best_objective()
        except Exception:
            try:
                result.best_bound = prob.solution.get_objective_value()
            except Exception:
                result.best_bound = n

        try:
            result.nodes = prob.solution.progress.get_num_nodes_processed()
        except Exception:
            result.nodes = 0

        try:
            result.simplex_iters = prob.solution.progress.get_num_iterations()
        except Exception:
            try:
                result.simplex_iters = prob.get_stats().get_num_iterations()
            except Exception:
                result.simplex_iters = 0

        if status in (
            prob.solution.status.MIP_optimal,
            prob.solution.status.optimal,
            prob.solution.status.optimal_tolerance,
        ):
            result.solved = True

        result.gap = (result.best_bound - result.incumbent) / max(1, result.incumbent)

    except Exception as e:
        logging.error(f"CPLEX error: {e}")

    return result


def get_root_bound_cplex(G: nx.Graph) -> float:
    res = solve_mis_cplex(G, time_limit=60.0, root_only=True)
    return res.best_bound if res.best_bound < float('inf') else G.number_of_nodes()


def get_cut_bound_cplex(G: nx.Graph) -> float:
    res = solve_mis_cplex(G, time_limit=60.0, cut_budget_only=True)
    return res.best_bound if res.best_bound < float('inf') else G.number_of_nodes()


# ===========================================================================
# Certification oracle
# ===========================================================================
def certification_oracle(G: nx.Graph, budget: float = 120.0) -> tuple:
    n = G.number_of_nodes()
    if n == 0:
        return 0, []
    if HAS_CPLEX:
        res = solve_mis_cplex(G, time_limit=budget)
        if res.solved:
            return res.incumbent, res.solution
        else:
            logging.warning(f"Certification not proven optimal in {budget}s, "
                            f"incumbent={res.incumbent}, bound={res.best_bound:.2f}")
            return res.incumbent, res.solution
    s = greedy_mis(G)
    return len(s), s


# ===========================================================================
# Heuristic solvers
# ===========================================================================

def greedy_mis(G: nx.Graph, seed: int = 0) -> list:
    rng = random.Random(seed)
    nodes = list(G.nodes())
    rng.shuffle(nodes)
    independent_set = []
    excluded = set()
    for v in nodes:
        if v not in excluded:
            independent_set.append(v)
            excluded.add(v)
            excluded.update(G.neighbors(v))
    return independent_set


def local_search_mis(G: nx.Graph, init_set: list, budget: float = 1.0, seed: int = 0) -> list:
    rng = random.Random(seed)
    best = set(init_set)
    current = set(init_set)
    t0 = time.time()

    while time.time() - t0 < budget:
        excluded = set()
        for v in current:
            excluded.update(G.neighbors(v))
        candidates = set(G.nodes()) - current - excluded
        if candidates:
            v = rng.choice(list(candidates))
            current.add(v)
            if len(current) > len(best):
                best = set(current)
            continue

        if current:
            v_remove = rng.choice(list(current))
            current.remove(v_remove)
            excluded2 = set()
            for u in current:
                excluded2.update(G.neighbors(u))
            cands2 = list(set(G.nodes()) - current - excluded2)
            rng.shuffle(cands2)
            added = 0
            for c in cands2:
                if added >= 2:
                    break
                ok = True
                for u in current:
                    if G.has_edge(c, u):
                        ok = False
                        break
                if ok:
                    current.add(c)
                    added += 1
            if len(current) > len(best):
                best = set(current)
            elif len(current) < len(best) - 1:
                current = set(best)
                if current and rng.random() < 0.3:
                    current.remove(rng.choice(list(current)))

    return list(best)


def heuristic_mis_greedy_ls(G: nx.Graph, budget: float = 1.0, seed: int = 0) -> dict:
    t0 = time.time()
    init = greedy_mis(G, seed=seed)
    remaining = max(0.0, budget - (time.time() - t0))
    result = local_search_mis(G, init, budget=remaining, seed=seed)
    return {"value": len(result), "set": result, "time": time.time() - t0}


def heuristic_mis_redumis(G: nx.Graph, budget: float = 1.0, seed: int = 0) -> dict:
    result = {"value": 0, "set": [], "time": budget}
    if not shutil.which(REDUMIS_BINARY) and not os.path.isfile(REDUMIS_BINARY):
        return heuristic_mis_greedy_ls(G, budget=budget, seed=seed)

    try:
        graph_path = write_temp_graph(G, fmt="metis")
        fd_out, out_path = tempfile.mkstemp(suffix=".mis")
        os.close(fd_out)

        cmd = [
            REDUMIS_BINARY, graph_path,
            f"--output={out_path}",
            f"--time_limit={max(1, int(budget))}",
            f"--seed={seed}",
        ]

        t0 = time.time()
        subprocess.run(cmd, capture_output=True, text=True, timeout=budget + 10)
        elapsed = time.time() - t0

        nodes_list = sorted(G.nodes())
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            with open(out_path) as f:
                lines = f.read().strip().split("\n")
            mis_nodes = []
            for i, line in enumerate(lines):
                if line.strip() == "1" and i < len(nodes_list):
                    mis_nodes.append(nodes_list[i])
            result = {"value": len(mis_nodes), "set": mis_nodes, "time": elapsed}
        else:
            result = heuristic_mis_greedy_ls(G, budget=budget, seed=seed)

        for p in [graph_path, out_path]:
            try:
                os.unlink(p)
            except OSError:
                pass

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logging.debug(f"ReduMIS failed ({e}), falling back to greedy+LS.")
        result = heuristic_mis_greedy_ls(G, budget=budget, seed=seed)

    return result


# ===========================================================================
# Structural scores
# ===========================================================================

def kernel_residual_fraction(G: nx.Graph) -> float:
    H = G.copy()
    changed = True
    while changed:
        changed = False
        isolated = [v for v in H.nodes() if H.degree(v) == 0]
        if isolated:
            H.remove_nodes_from(isolated)
            changed = True
        pendants = [v for v in H.nodes() if H.degree(v) == 1]
        to_remove = set()
        for v in pendants:
            if v in H and H.degree(v) == 1:
                nbr = list(H.neighbors(v))[0]
                to_remove.add(nbr)
                to_remove.add(v)
        if to_remove:
            H.remove_nodes_from(to_remove)
            changed = True
        dom_remove = set()
        node_list = list(H.nodes())
        for u in node_list:
            if u in dom_remove or u not in H:
                continue
            Nu = set(H.neighbors(u)) | {u}
            for v in list(H.neighbors(u)):
                if v in dom_remove or v not in H:
                    continue
                Nv = set(H.neighbors(v)) | {v}
                if Nu.issubset(Nv) and H.degree(u) <= H.degree(v):
                    dom_remove.add(v)
        if dom_remove:
            H.remove_nodes_from(dom_remove)
            changed = True

    n_orig = G.number_of_nodes()
    return H.number_of_nodes() / n_orig if n_orig > 0 else 0.0


def near_optima_density_proxy(G: nx.Graph, alpha_star: int, num_samples: int = 200) -> float:
    n = G.number_of_nodes()
    if n == 0:
        return 0.0
    count_near = 0
    for seed_val in range(num_samples):
        mis = greedy_mis(G, seed=seed_val)
        if len(mis) >= alpha_star - 2:
            count_near += 1
    return count_near / (n + 1)


def symmetry_proxy(G: nx.Graph) -> float:
    n = G.number_of_nodes()
    if n <= 1:
        return 0.0
    nodes = sorted(G.nodes())
    adj = {v: set(G.neighbors(v)) for v in nodes}
    max_pairs = min(n * (n - 1) // 2, 5000)
    if n * (n - 1) // 2 <= max_pairs:
        pairs = list(combinations(nodes, 2))
    else:
        rng = random.Random(12345)
        pairs = set()
        while len(pairs) < max_pairs:
            u = rng.choice(nodes)
            v = rng.choice(nodes)
            if u != v:
                pairs.add((min(u, v), max(u, v)))
        pairs = list(pairs)

    near_twin_count = 0
    for u, v in pairs:
        if len(adj[u].symmetric_difference(adj[v])) <= 2:
            near_twin_count += 1
    return near_twin_count / max(1, len(pairs))


def polyhedral_weakness_proxy(G: nx.Graph, alpha_star: int) -> float:
    if not HAS_CPLEX:
        n = G.number_of_nodes()
        m = G.number_of_edges()
        avg_deg = 2 * m / max(1, n)
        lp_estimate = n / (1 + avg_deg / max(1, n - 1) * n)
        return max(0, lp_estimate - alpha_star) / max(1, alpha_star)

    root_bound = get_root_bound_cplex(G)
    delta_root = (root_bound - alpha_star) / max(1, alpha_star)
    if delta_root > 0.05:
        cut_bound = get_cut_bound_cplex(G)
        delta_cut = (cut_bound - alpha_star) / max(1, alpha_star)
    else:
        delta_cut = delta_root
    return delta_root + 0.5 * delta_cut


# ===========================================================================
# Seed family generators
# ===========================================================================

def seed_family_A(n: int, p: float, c1: int, rng: random.Random) -> nx.Graph:
    c2 = c1 + 1
    n0 = max(n - c1 - c2, 20)
    H = nx.erdos_renyi_graph(n0, p, seed=rng.randint(0, 2**31))
    nodes = list(H.nodes())

    if len(nodes) >= c1:
        decoy = rng.sample(nodes, c1)
        for u, v in combinations(decoy, 2):
            if not H.has_edge(u, v):
                H.add_edge(u, v)
    else:
        decoy = nodes[:]

    next_node = max(H.nodes()) + 1
    for vi in decoy[:min(len(decoy), c1 // 2)]:
        ri = rng.randint(1, 3)
        nbrs = list(H.neighbors(vi))
        for _ in range(ri):
            H.add_node(next_node)
            for nbr in nbrs:
                if nbr != next_node:
                    H.add_edge(next_node, nbr)
            next_node += 1

    all_nodes = list(H.nodes())
    if len(all_nodes) >= c2:
        overlap_count = min(c1 // 3, c2 - 1)
        hidden = rng.sample(decoy[:overlap_count], min(overlap_count, len(decoy)))
        remaining_pool = [v for v in all_nodes if v not in hidden]
        needed = c2 - len(hidden)
        if len(remaining_pool) >= needed:
            hidden += rng.sample(remaining_pool, needed)
        for u, v in combinations(hidden, 2):
            if not H.has_edge(u, v):
                H.add_edge(u, v)

    return nx.complement(H)


def seed_family_B(n: int, rng: random.Random) -> nx.Graph:
    degree = rng.randint(n // 3, 2 * n // 3)
    if degree >= n:
        degree = n - 2
    if degree < 1:
        degree = 1
    if (n * degree) % 2 != 0:
        degree -= 1
    if degree < 1:
        degree = 2 if n % 2 == 0 else 1
    try:
        G = nx.random_regular_graph(degree, n, seed=rng.randint(0, 2**31))
    except nx.NetworkXError:
        G = nx.erdos_renyi_graph(n, 0.5, seed=rng.randint(0, 2**31))

    edges = list(G.edges())
    for _ in range(max(1, n // 10)):
        if len(edges) < 2:
            break
        idx1, idx2 = rng.sample(range(len(edges)), 2)
        a, b = edges[idx1]
        c, d = edges[idx2]
        if len({a, b, c, d}) == 4 and not G.has_edge(a, d) and not G.has_edge(c, b):
            G.remove_edge(a, b)
            G.remove_edge(c, d)
            G.add_edge(a, d)
            G.add_edge(c, b)
            edges = list(G.edges())
    return G


def seed_family_C(n: int, rng: random.Random) -> nx.Graph:
    template_size = rng.choice([5, 7])
    T = nx.cycle_graph(template_size)
    bag_sizes = [rng.randint(2, 4) for _ in range(template_size)]
    while sum(bag_sizes) < n:
        bag_sizes[rng.randint(0, template_size - 1)] += 1
    while sum(bag_sizes) > n:
        idx = rng.randint(0, template_size - 1)
        if bag_sizes[idx] > 1:
            bag_sizes[idx] -= 1

    G = nx.Graph()
    bags = {}
    node_counter = 0
    for i in range(template_size):
        bag = list(range(node_counter, node_counter + bag_sizes[i]))
        bags[i] = bag
        G.add_nodes_from(bag)
        node_counter += bag_sizes[i]

    for u, v in T.edges():
        for a in bags[u]:
            for b in bags[v]:
                G.add_edge(a, b)
    return G


def seed_family_D(n: int, p: float, c1: int, rng: random.Random) -> nx.Graph:
    n_dec = n // 2
    n_poly = n - n_dec
    G_dec = seed_family_A(n_dec, p, min(c1, n_dec // 3), rng)
    G_poly = seed_family_C(n_poly, rng)

    offset = max(G_dec.nodes()) + 1 if G_dec.nodes() else 0
    mapping_poly = {v: v + offset for v in G_poly.nodes()}
    G_poly = nx.relabel_nodes(G_poly, mapping_poly)
    G = nx.compose(G_dec, G_poly)

    nodes_dec = sorted(G_dec.nodes())
    I_poly_nodes = sorted(mapping_poly.values())
    interface_size = max(2, min(len(nodes_dec), len(I_poly_nodes)) // 4)
    I_dec = rng.sample(nodes_dec, min(interface_size, len(nodes_dec)))
    I_poly = rng.sample(I_poly_nodes, min(interface_size, len(I_poly_nodes)))
    for u in I_dec:
        for v in I_poly:
            if rng.random() < 0.7:
                G.add_edge(u, v)
    return G


# ===========================================================================
# Graph normalization and repair
# ===========================================================================

def normalize_size(G: nx.Graph, target_n: int) -> nx.Graph:
    n = G.number_of_nodes()
    if n == target_n:
        return G
    if n > target_n:
        while G.number_of_nodes() > target_n:
            degrees = dict(G.degree())
            G.remove_node(min(degrees, key=degrees.get))
    elif n < target_n:
        rng = random.Random(999)
        existing = sorted(G.nodes())
        next_node = max(existing) + 1 if existing else 0
        while G.number_of_nodes() < target_n:
            G.add_node(next_node)
            for v in existing:
                if rng.random() < 0.5:
                    G.add_edge(next_node, v)
            existing.append(next_node)
            next_node += 1
    mapping = {v: i for i, v in enumerate(sorted(G.nodes()))}
    return nx.relabel_nodes(G, mapping)


def reduction_resistance_repair(G: nx.Graph, rng: random.Random) -> nx.Graph:
    nodes = sorted(G.nodes())
    if not nodes:
        return G
    for v in nodes:
        if G.degree(v) == 0:
            targets = [u for u in nodes if u != v]
            if targets:
                for u in rng.sample(targets, min(3, len(targets))):
                    G.add_edge(v, u)
    for v in nodes:
        if G.degree(v) == 1:
            nbr = list(G.neighbors(v))[0]
            targets = [u for u in nodes if u != v and u != nbr and not G.has_edge(v, u)]
            if targets:
                G.add_edge(v, rng.choice(targets))
    if not nx.is_connected(G):
        components = list(nx.connected_components(G))
        for i in range(1, len(components)):
            u = rng.choice(list(components[0]))
            v = rng.choice(list(components[i]))
            G.add_edge(u, v)
            components[0] = components[0] | components[i]
    return G


# ===========================================================================
# Mutation operators
# ===========================================================================

def mutation_two_switch(G: nx.Graph, rng: random.Random, num_switches: int = 3) -> nx.Graph:
    H = G.copy()
    edges = list(H.edges())
    for _ in range(num_switches):
        if len(edges) < 2:
            break
        idx1, idx2 = rng.sample(range(len(edges)), 2)
        a, b = edges[idx1]
        c, d = edges[idx2]
        if len({a, b, c, d}) == 4 and not H.has_edge(a, d) and not H.has_edge(c, b):
            H.remove_edge(a, b)
            H.remove_edge(c, d)
            H.add_edge(a, d)
            H.add_edge(c, b)
            edges = list(H.edges())
    return H


def mutation_add_remove_edge(G: nx.Graph, rng: random.Random) -> nx.Graph:
    H = G.copy()
    nodes = sorted(H.nodes())
    edges = list(H.edges())
    if edges:
        H.remove_edge(*rng.choice(edges))
    for _ in range(100):
        u, v = rng.sample(nodes, 2)
        if not H.has_edge(u, v):
            H.add_edge(u, v)
            break
    return H


def mutation_near_clone(G: nx.Graph, rng: random.Random) -> nx.Graph:
    H = G.copy()
    nodes = sorted(H.nodes())
    if len(nodes) < 3:
        return H
    v = rng.choice(nodes)
    nbrs = set(H.neighbors(v))
    nbrs_new = set(nbrs)
    if nbrs_new:
        nbrs_new.discard(rng.choice(list(nbrs_new)))
    non_nbrs = [u for u in nodes if u != v and u not in nbrs]
    if non_nbrs and rng.random() < 0.5:
        nbrs_new.add(rng.choice(non_nbrs))
    target = rng.choice([u for u in nodes if u != v])
    for u in list(H.neighbors(target)):
        H.remove_edge(target, u)
    for u in nbrs_new:
        if u != target:
            H.add_edge(target, u)
    return H


def mutation_hidden_optimum_shield(G: nx.Graph, alpha_star: int,
                                    opt_set: list, rng: random.Random) -> nx.Graph:
    H = G.copy()
    if not opt_set:
        return H
    opt_vertices = set(opt_set)
    non_opt = [v for v in H.nodes() if v not in opt_vertices]
    if len(non_opt) < 2:
        return H
    for _ in range(max(1, len(non_opt) // 4)):
        u, v = rng.sample(non_opt, 2)
        if not H.has_edge(u, v):
            H.add_edge(u, v)
    edges_non_opt = [(u, v) for u, v in H.edges() if u in non_opt and v in non_opt]
    for _ in range(min(3, len(edges_non_opt))):
        if not edges_non_opt:
            break
        e = rng.choice(edges_non_opt)
        H.remove_edge(*e)
        edges_non_opt.remove(e)
    return H


def mutation_root_gap_amplify(G: nx.Graph, rng: random.Random) -> nx.Graph:
    H = G.copy()
    nodes = sorted(H.nodes())
    if len(nodes) < 7:
        return H
    sample = rng.sample(nodes, 5)
    for i, j in combinations(range(5), 2):
        if H.has_edge(sample[i], sample[j]):
            H.remove_edge(sample[i], sample[j])
    for i in range(5):
        H.add_edge(sample[i], sample[(i + 1) % 5])
    return H


def generate_mutations(G: nx.Graph, alpha_star: int, opt_set: list,
                       rng: random.Random, num_mutations: int = 5) -> list:
    mutations = []
    mutation_ops = [
        ("two_switch", lambda g: mutation_two_switch(g, rng)),
        ("add_remove", lambda g: mutation_add_remove_edge(g, rng)),
        ("near_clone", lambda g: mutation_near_clone(g, rng)),
        ("shield", lambda g: mutation_hidden_optimum_shield(g, alpha_star, opt_set, rng)),
        ("root_gap", lambda g: mutation_root_gap_amplify(g, rng)),
    ]
    for _ in range(num_mutations):
        op_name, op_fn = rng.choice(mutation_ops)
        try:
            H = op_fn(G)
            H = reduction_resistance_repair(H, rng)
            if H.number_of_nodes() > 0 and H.number_of_edges() > 0:
                mutations.append((H, op_name))
        except Exception as e:
            logging.debug(f"Mutation {op_name} failed: {e}")
    return mutations


# ===========================================================================
# Evaluation
# ===========================================================================

class EvalResult:
    def __init__(self):
        self.n = 0
        self.m = 0
        self.density = 0.0
        self.alpha_star = 0
        self.root_bound = 0.0
        self.cut_bound = 0.0
        self.delta_root = 0.0
        self.delta_cut = 0.0
        self.cplex_incumbent = 0
        self.cplex_bound = 0.0
        self.cplex_gap = 0.0
        self.cplex_nodes = 0
        self.cplex_solved = False
        self.cplex_time = 0.0
        self.cplex_simplex_iters = 0
        self.cplex_time_ratio = 0.0
        self.cplex_time_pressure = 0.0
        self.heu_greedy_value = 0
        self.heu_greedy_p = 0.0
        self.heu_greedy_tau = 0.0
        self.heu_redumis_value = 0
        self.heu_redumis_p = 0.0
        self.heu_redumis_tau = 0.0
        self.kappa = 0.0
        self.nu = 0.0
        self.sigma = 0.0
        self.pi_val = 0.0
        self.phi = 0.0
        self.opt_set = []

    def to_dict(self):
        d = {}
        for k, v in vars(self).items():
            if isinstance(v, float) and (math.isinf(v) or math.isnan(v)):
                d[k] = str(v)
            else:
                d[k] = v
        return d


def save_eval_json(ev: EvalResult, path: Path):
    with open(path, "w") as f:
        json.dump(ev.to_dict(), f, indent=2, default=str)


def evaluate_hardness(G: nx.Graph, alpha_star: int, args, opt_set: list = None) -> EvalResult:
    res = EvalResult()
    n = G.number_of_nodes()
    m = G.number_of_edges()
    res.n = n
    res.m = m
    res.density = 2.0 * m / (n * (n - 1)) if n > 1 else 0.0
    res.alpha_star = alpha_star
    if opt_set:
        res.opt_set = list(opt_set)

    # ---- Exact portfolio: CPLEX ----
    if HAS_CPLEX:
        res.root_bound = get_root_bound_cplex(G)
        res.delta_root = (res.root_bound - alpha_star) / max(1, alpha_star)
        res.cut_bound = get_cut_bound_cplex(G)
        res.delta_cut = (res.cut_bound - alpha_star) / max(1, alpha_star)

        cplex_res = solve_mis_cplex(G, time_limit=args.B_ex)
        res.cplex_incumbent = cplex_res.incumbent
        res.cplex_bound = cplex_res.best_bound
        res.cplex_gap = cplex_res.gap
        res.cplex_nodes = cplex_res.nodes
        res.cplex_solved = cplex_res.solved
        res.cplex_time = cplex_res.time
        res.cplex_simplex_iters = cplex_res.simplex_iters

        # Time pressure metrics
        res.cplex_time_ratio = cplex_res.time / max(0.01, args.B_ex)
        res.cplex_time_pressure = 1.0 / (1.0 + math.exp(-12.0 * (res.cplex_time_ratio - 0.5)))

        if cplex_res.solution and not opt_set:
            res.opt_set = cplex_res.solution

    # ---- Heuristic portfolio ----
    greedy_values, greedy_found_opt, greedy_times = [], 0, []
    for s in range(args.heu_seeds):
        hr = heuristic_mis_greedy_ls(G, budget=args.B_heu, seed=s)
        greedy_values.append(hr["value"])
        greedy_times.append(hr["time"])
        if hr["value"] >= alpha_star:
            greedy_found_opt += 1
    res.heu_greedy_value = max(greedy_values) if greedy_values else 0
    res.heu_greedy_p = greedy_found_opt / max(1, args.heu_seeds)
    res.heu_greedy_tau = float(np.mean(greedy_times)) if greedy_times else args.B_heu

    redumis_values, redumis_found_opt, redumis_times = [], 0, []
    for s in range(args.heu_seeds):
        hr = heuristic_mis_redumis(G, budget=args.B_heu, seed=s)
        redumis_values.append(hr["value"])
        redumis_times.append(hr["time"])
        if hr["value"] >= alpha_star:
            redumis_found_opt += 1
    res.heu_redumis_value = max(redumis_values) if redumis_values else 0
    res.heu_redumis_p = redumis_found_opt / max(1, args.heu_seeds)
    res.heu_redumis_tau = float(np.mean(redumis_times)) if redumis_times else args.B_heu

    # ---- Structural scores ----
    res.kappa = kernel_residual_fraction(G)
    res.nu = near_optima_density_proxy(G, alpha_star)
    res.sigma = symmetry_proxy(G)
    res.pi_val = polyhedral_weakness_proxy(G, alpha_star)

    # ---- Combined Φ(G) with continuous time pressure ----
    exact_score = 0.0
    if HAS_CPLEX:
        c_e = 1.0 if res.cplex_solved else 0.0
        g_e = min(res.cplex_gap if res.cplex_gap < float('inf') else 10.0, 10.0)

        # Original terms
        exact_score += args.a1 * (1.0 - c_e)
        exact_score += args.a2 * g_e
        exact_score += args.a3 * math.log(1 + res.cplex_nodes)
        exact_score += args.a4 * max(0, res.delta_root)
        exact_score += args.a5 * max(0, res.delta_cut)

        # Continuous time-pressure terms
        exact_score += args.a6 * res.cplex_time_pressure
        exact_score += args.a7 * min(1.0, res.cplex_time_ratio)
        exact_score += args.a8 * math.log(1 + res.cplex_simplex_iters)

        exact_score *= args.w_ex

    heu_score = 0.0
    for p_h, val_h, tau_h in [
        (res.heu_greedy_p, res.heu_greedy_value, res.heu_greedy_tau),
        (res.heu_redumis_p, res.heu_redumis_value, res.heu_redumis_tau),
    ]:
        gap_h = (alpha_star - val_h) / max(1, alpha_star)
        heu_score += args.w_heu * (
            args.b1 * (1.0 - p_h) + args.b2 * gap_h + args.b3 * math.log(1 + tau_h)
        )

    struct_score = (
        args.lam * res.kappa + args.mu * res.nu
        + args.xi * res.sigma + args.zeta * res.pi_val
    )

    res.phi = exact_score + heu_score + struct_score
    return res


# ===========================================================================
# Archive management
# ===========================================================================
def keep_best_diverse(archive: list, max_size: int) -> list:
    archive.sort(key=lambda x: x[1].phi, reverse=True)
    kept, seen_fps = [], set()
    for entry in archive:
        fp = entry[2]
        if fp not in seen_fps:
            kept.append(entry)
            seen_fps.add(fp)
            if len(kept) >= max_size:
                break
    if len(kept) < max_size:
        for entry in archive:
            if entry not in kept:
                kept.append(entry)
                if len(kept) >= max_size:
                    break
    return kept[:max_size]


# ===========================================================================
# Per-iteration saving
# ===========================================================================
def save_iteration_state(iteration: int, archive: list, offspring_count: int,
                         run_path: Path):
    iter_dir = run_path / "iterations"
    summary = {
        "iteration": iteration,
        "offspring_evaluated": offspring_count,
        "archive_size": len(archive),
        "archive": [],
    }
    for rank, (g, ev, fp) in enumerate(archive):
        summary["archive"].append({
            "rank": rank + 1, "fingerprint": fp,
            "phi": round(ev.phi, 6), "alpha_star": ev.alpha_star,
            "n": ev.n, "m": ev.m, "density": round(ev.density, 4),
            "delta_root": round(ev.delta_root, 4),
            "cplex_solved": ev.cplex_solved, "cplex_nodes": ev.cplex_nodes,
            "cplex_time": round(ev.cplex_time, 4),
            "cplex_time_ratio": round(ev.cplex_time_ratio, 4),
            "cplex_time_pressure": round(ev.cplex_time_pressure, 4),
            "cplex_simplex_iters": ev.cplex_simplex_iters,
            "kappa": round(ev.kappa, 4),
            "greedy_p": round(ev.heu_greedy_p, 4),
            "redumis_p": round(ev.heu_redumis_p, 4),
        })
    with open(iter_dir / f"iteration_{iteration:03d}.json", "w") as f:
        json.dump(summary, f, indent=2)

    snap_dir = run_path / "graphs" / "archive" / f"iter_{iteration:03d}"
    snap_dir.mkdir(parents=True, exist_ok=True)
    for rank, (g, ev, fp) in enumerate(archive):
        name = f"rank{rank+1}_phi{ev.phi:.4f}_a{ev.alpha_star}"
        save_graph_all_formats(g, snap_dir, name)
        save_eval_json(ev, snap_dir / f"{name}_eval.json")


# ===========================================================================
# Main algorithm
# ===========================================================================
def aheg_mis(args, run_path: Path):
    rng = random.Random(args.seed)
    np.random.seed(args.seed)
    n = args.n

    logging.info("=" * 60)
    logging.info(f"AHEG-MIS: n={n}, B_ex={args.B_ex}, B_heu={args.B_heu}, T={args.T}, M={args.M}")
    logging.info(f"CPLEX: {HAS_CPLEX} | ReduMIS: {REDUMIS_BINARY}")
    logging.info(f"Time weights: a6={args.a6} a7={args.a7} a8={args.a8}")
    logging.info("=" * 60)

    # ---- Seed generation ----
    logging.info("Generating seeds...")
    seed_pool = []
    for _ in range(3):
        p = rng.uniform(args.p_low, args.p_high)
        c1 = rng.randint(args.c1_low, args.c1_high)
        seed_pool.append(("A", seed_family_A(n, p, c1, rng)))
    for _ in range(3):
        seed_pool.append(("B", seed_family_B(n, rng)))
    for _ in range(2):
        seed_pool.append(("C", seed_family_C(n, rng)))
    for _ in range(2):
        p = rng.uniform(args.p_low, args.p_high)
        c1 = rng.randint(args.c1_low, args.c1_high)
        seed_pool.append(("D", seed_family_D(n, p, c1, rng)))

    seed_graph_dir = run_path / "graphs" / "seeds"
    seed_eval_dir = run_path / "evals" / "seeds"
    archive = []

    for idx, (family, G) in enumerate(seed_pool):
        logging.info(f"  Seed {idx+1}/{len(seed_pool)} (family {family})...")
        G = normalize_size(G, n)
        G = reduction_resistance_repair(G, rng)

        seed_name = f"seed_{idx:02d}_family{family}"
        save_graph_all_formats(G, seed_graph_dir, seed_name)

        alpha_star, opt_set = certification_oracle(G, budget=args.cert_budget)
        logging.info(f"    α*={alpha_star}, n={G.number_of_nodes()}, m={G.number_of_edges()}")

        if alpha_star <= 0:
            logging.warning("    Skipping (α*=0)")
            continue

        ev = evaluate_hardness(G, alpha_star, args, opt_set=opt_set)
        fp = graph_fingerprint(G)
        save_eval_json(ev, seed_eval_dir / f"{seed_name}_eval.json")

        logging.info(f"    Φ={ev.phi:.4f} δ_root={ev.delta_root:.3f} κ={ev.kappa:.3f} "
                     f"σ={ev.sigma:.3f} time={ev.cplex_time:.3f}s "
                     f"ratio={ev.cplex_time_ratio:.2f} pressure={ev.cplex_time_pressure:.3f} "
                     f"simplex={ev.cplex_simplex_iters} "
                     f"greedy_p={ev.heu_greedy_p:.2f} redumis_p={ev.heu_redumis_p:.2f}")

        archive.append((G, ev, fp))

    archive = keep_best_diverse(archive, args.M)
    logging.info(f"Archive after init: {len(archive)} graphs")
    if archive:
        logging.info(f"  Best Φ = {archive[0][1].phi:.4f}")
    save_iteration_state(0, archive, 0, run_path)

    # ---- Evolutionary loop ----
    for t in range(1, args.T + 1):
        logging.info(f"\n--- Iteration {t}/{args.T} ---")
        if not archive:
            logging.warning("Archive empty, stopping.")
            break

        num_parents = max(1, len(archive) // 2)
        parents = archive[:num_parents]
        offspring = []
        offspring_count = 0

        offspring_graph_dir = run_path / "graphs" / "offspring" / f"iter_{t:03d}"
        offspring_eval_dir = run_path / "evals" / "offspring" / f"iter_{t:03d}"
        offspring_graph_dir.mkdir(parents=True, exist_ok=True)
        offspring_eval_dir.mkdir(parents=True, exist_ok=True)

        for p_idx, (G_parent, ev_parent, fp_parent) in enumerate(parents):
            mutations = generate_mutations(
                G_parent, ev_parent.alpha_star, ev_parent.opt_set, rng,
                num_mutations=args.mutations_per_parent,
            )

            for mut_idx, (H, op_name) in enumerate(mutations):
                if H.number_of_nodes() != n:
                    H = normalize_size(H, n)

                a_star_new, opt_set_new = certification_oracle(H, budget=args.cert_budget)
                if a_star_new <= 0:
                    continue

                ev_new = evaluate_hardness(H, a_star_new, args, opt_set=opt_set_new)
                fp_new = graph_fingerprint(H)

                off_name = f"p{p_idx}_m{mut_idx}_{op_name}"
                save_graph_all_formats(H, offspring_graph_dir, off_name)
                save_eval_json(ev_new, offspring_eval_dir / f"{off_name}_eval.json")

                offspring.append((H, ev_new, fp_new))
                offspring_count += 1
                logging.debug(f"    [{op_name}] Φ={ev_new.phi:.4f} α*={a_star_new} "
                              f"time={ev_new.cplex_time:.3f}s")

        archive = keep_best_diverse(archive + offspring, args.M)
        save_iteration_state(t, archive, offspring_count, run_path)

        if archive:
            b = archive[0][1]
            logging.info(f"  Best Φ={b.phi:.4f} α*={b.alpha_star} n={b.n} m={b.m} "
                         f"δ_root={b.delta_root:.3f} δ_cut={b.delta_cut:.3f} "
                         f"κ={b.kappa:.3f} σ={b.sigma:.3f} "
                         f"cplex_solved={b.cplex_solved} nodes={b.cplex_nodes} "
                         f"time={b.cplex_time:.3f}s ratio={b.cplex_time_ratio:.2f} "
                         f"pressure={b.cplex_time_pressure:.3f} "
                         f"simplex={b.cplex_simplex_iters} "
                         f"greedy_p={b.heu_greedy_p:.2f} redumis_p={b.heu_redumis_p:.2f}")

    if not archive:
        logging.error("No valid graphs produced!")
        return None, None, []

    return archive[0][0], archive[0][1], archive


# ===========================================================================
# Final reporting
# ===========================================================================
def save_final_results(G: nx.Graph, ev: EvalResult, archive: list, run_path: Path):
    if G is None or ev is None:
        logging.error("No results to save.")
        return

    logging.info("Saving final results...")

    best_dir = run_path / "graphs" / "best"
    paths = save_graph_all_formats(G, best_dir, "best_graph")
    save_eval_json(ev, best_dir / "best_graph_eval.json")
    for fmt, p in paths.items():
        logging.info(f"  {fmt}: {p}")

    # Final archive snapshot
    final_archive_dir = run_path / "graphs" / "archive" / "final"
    final_archive_dir.mkdir(parents=True, exist_ok=True)
    archive_summary = []
    for rank, (g, e, fp) in enumerate(archive):
        name = f"rank{rank+1}_phi{e.phi:.4f}_a{e.alpha_star}"
        save_graph_all_formats(g, final_archive_dir, name)
        save_eval_json(e, final_archive_dir / f"{name}_eval.json")
        archive_summary.append({
            "rank": rank + 1, "fingerprint": fp,
            "phi": round(e.phi, 6), "alpha_star": e.alpha_star,
            "n": e.n, "m": e.m, "density": round(e.density, 4),
            "delta_root": round(e.delta_root, 4),
            "delta_cut": round(e.delta_cut, 4),
            "cplex_solved": e.cplex_solved, "cplex_nodes": e.cplex_nodes,
            "cplex_time": round(e.cplex_time, 4),
            "cplex_time_ratio": round(e.cplex_time_ratio, 4),
            "cplex_time_pressure": round(e.cplex_time_pressure, 4),
            "cplex_simplex_iters": e.cplex_simplex_iters,
            "cplex_gap": round(e.cplex_gap, 4) if e.cplex_gap < float('inf') else "inf",
            "kappa": round(e.kappa, 4), "nu": round(e.nu, 4),
            "sigma": round(e.sigma, 4), "pi": round(e.pi_val, 4),
            "greedy_value": e.heu_greedy_value, "greedy_p": round(e.heu_greedy_p, 4),
            "redumis_value": e.heu_redumis_value, "redumis_p": round(e.heu_redumis_p, 4),
        })

    with open(run_path / "archive_final_summary.json", "w") as f:
        json.dump(archive_summary, f, indent=2)

    # Evaluation report
    report = {
        "graph_stats": {"n": ev.n, "m": ev.m, "density": round(ev.density, 6)},
        "exact_optimum": {"alpha_star": ev.alpha_star, "optimal_set": ev.opt_set},
        "exact_solver_cplex": {
            "root_bound": round(ev.root_bound, 4),
            "cut_bound": round(ev.cut_bound, 4),
            "delta_root": round(ev.delta_root, 4),
            "delta_cut": round(ev.delta_cut, 4),
            "incumbent": ev.cplex_incumbent,
            "best_bound": round(float(ev.cplex_bound), 4) if not math.isinf(ev.cplex_bound) else "inf",
            "gap": round(ev.cplex_gap, 4) if ev.cplex_gap < float('inf') else "inf",
            "nodes": ev.cplex_nodes,
            "solved": ev.cplex_solved,
            "time": round(ev.cplex_time, 4),
            "time_ratio": round(ev.cplex_time_ratio, 4),
            "time_pressure_score": round(ev.cplex_time_pressure, 4),
            "simplex_iterations": ev.cplex_simplex_iters,
        },
        "heuristic_greedy_ls": {
            "best_value": ev.heu_greedy_value,
            "success_rate": round(ev.heu_greedy_p, 4),
            "avg_time": round(ev.heu_greedy_tau, 4),
        },
        "heuristic_redumis": {
            "best_value": ev.heu_redumis_value,
            "success_rate": round(ev.heu_redumis_p, 4),
            "avg_time": round(ev.heu_redumis_tau, 4),
        },
        "structural_scores": {
            "kappa": round(ev.kappa, 4), "nu": round(ev.nu, 4),
            "sigma": round(ev.sigma, 4), "pi": round(ev.pi_val, 4),
        },
        "combined_hardness_phi": round(ev.phi, 6),
    }
    with open(run_path / "evaluation_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    # Human-readable summary
    with open(run_path / "summary.txt", "w") as f:
        f.write("=" * 60 + "\n")
        f.write("AHEG-MIS: Adversarial Hard MIS Instance — Final Report\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Graph: n={ev.n}, m={ev.m}, density={ev.density:.4f}\n")
        f.write(f"α*(G) = {ev.alpha_star}\n")
        f.write(f"Optimal set: {ev.opt_set}\n\n")

        f.write("--- MILP (CPLEX) ---\n")
        f.write(f"  Root LP bound:   {ev.root_bound:.2f}\n")
        f.write(f"  Cut bound:       {ev.cut_bound:.2f}\n")
        f.write(f"  δ_root:          {ev.delta_root:.4f}\n")
        f.write(f"  δ_cut:           {ev.delta_cut:.4f}\n")
        f.write(f"  Incumbent:       {ev.cplex_incumbent}\n")
        bb = f"{ev.cplex_bound:.2f}" if not math.isinf(ev.cplex_bound) else "inf"
        f.write(f"  Best bound:      {bb}\n")
        gg = f"{ev.cplex_gap:.4f}" if ev.cplex_gap < float('inf') else "inf"
        f.write(f"  Gap:             {gg}\n")
        f.write(f"  B&B nodes:       {ev.cplex_nodes}\n")
        f.write(f"  Solved:          {ev.cplex_solved}\n")
        f.write(f"  Time:            {ev.cplex_time:.3f}s\n")
        f.write(f"  Time/Budget:     {ev.cplex_time_ratio:.2f} ({ev.cplex_time_ratio*100:.0f}%)\n")
        f.write(f"  Time pressure:   {ev.cplex_time_pressure:.4f}\n")
        f.write(f"  Simplex iters:   {ev.cplex_simplex_iters}\n\n")

        f.write("--- Greedy+LS ---\n")
        f.write(f"  Best value:      {ev.heu_greedy_value}\n")
        f.write(f"  p_h:             {ev.heu_greedy_p:.2f}\n")
        f.write(f"  Avg time:        {ev.heu_greedy_tau:.4f}s\n\n")

        f.write("--- ReduMIS ---\n")
        f.write(f"  Best value:      {ev.heu_redumis_value}\n")
        f.write(f"  p_h:             {ev.heu_redumis_p:.2f}\n")
        f.write(f"  Avg time:        {ev.heu_redumis_tau:.4f}s\n\n")

        f.write("--- Structural ---\n")
        f.write(f"  κ (kernel):      {ev.kappa:.4f}\n")
        f.write(f"  ν (near-opt):    {ev.nu:.4f}\n")
        f.write(f"  σ (symmetry):    {ev.sigma:.4f}\n")
        f.write(f"  π (polyh.):      {ev.pi_val:.4f}\n\n")

        f.write(f"*** Φ(G) = {ev.phi:.6f} ***\n\n")

        f.write(f"Archive ({len(archive)} graphs):\n")
        for rank, (_, e, fp) in enumerate(archive):
            f.write(f"  #{rank+1}: Φ={e.phi:.4f} α*={e.alpha_star} "
                    f"n={e.n} m={e.m} time={e.cplex_time:.3f}s "
                    f"pressure={e.cplex_time_pressure:.3f} "
                    f"simplex={e.cplex_simplex_iters} "
                    f"solved={e.cplex_solved} fp={fp[:8]}...\n")

    logging.info(f"All results saved under: {run_path}")


# ===========================================================================
# Entry point
# ===========================================================================
def main():
    args = parse_args()
    run_path = setup_logging(args)

    logging.info("Starting AHEG-MIS")
    logging.info(f"Arguments: {vars(args)}")

    t_start = time.time()
    best_G, best_ev, archive = aheg_mis(args, run_path)
    total_time = time.time() - t_start

    logging.info(f"\nTotal time: {total_time:.1f}s ({total_time/60:.1f} min)")

    with open(run_path / "timing.json", "w") as f:
        json.dump({
            "total_seconds": round(total_time, 2),
            "total_minutes": round(total_time / 60, 2),
        }, f, indent=2)

    if best_G is not None:
        save_final_results(best_G, best_ev, archive, run_path)
        logging.info(f"\nBest: Φ={best_ev.phi:.6f} n={best_ev.n} m={best_ev.m} "
                     f"α*={best_ev.alpha_star} time={best_ev.cplex_time:.3f}s "
                     f"pressure={best_ev.cplex_time_pressure:.3f} "
                     f"simplex={best_ev.cplex_simplex_iters}")
    else:
        logging.error("No valid graphs produced.")

    logging.info("Done.")


if __name__ == "__main__":
    main()