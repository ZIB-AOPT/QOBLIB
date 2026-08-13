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
"""Instance discovery.

Turns each problem's ``instances/`` folder into instance source descriptors
(name, file, format, size, download URL). Most problems are a flat directory of
files; Steiner (04) and Portfolio (06) are directory *bundles*; Sports (05) is
scanned recursively; and Birkhoff (03) instances are unpacked from the
``qbench_*.json`` bundles together with their reference status and LP model.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from . import config
from .models import read_model_description
from .solutions import load_birkhoff_solution_map
from .text import (
    canonical_name_from_filename,
    format_portfolio_lambda,
    normalize_portfolio_lambda,
    num_or_none,
    portfolio_base_name,
)

# Portfolio (06) logical instances are the cross product of each physical data
# directory (assets × time-window × perturbation seed) with a budget determined
# by the asset count and a fixed grid of risk-aversion λ values. This mirrors the
# authoritative model-generation script exactly:
#   06-portfolio/models/binary_quadratic_programming/gen_archive.sh
# (budget `case "$a"` block + the `lambda_values` array). Kept here so instances
# are discovered from the on-disk data dirs even when no .lp/.qs model file was
# generated for them — historically the large a200/a400 instances had data dirs
# but no models (gen_archive.sh only globbed `po_a0*`), so they were invisible.
# The a003/a004/a005 sizes predate no model-generation rule (gen_archive.sh's
# case block only handles 10/50/200/400 and defaults everything else to B=0), so
# their budgets come from the instance authors directly: a003 -> B=3, a004 -> B=4,
# a005 -> B=4. Without these keys the smallest data dirs are skipped and never
# render on the site.
#
# These are the *fallback* values: the authoritative source is
# 06-portfolio/instances/manifest.json (read by _load_portfolio_manifest). The
# constants are kept in sync with the manifest so the builder still works if the
# file is missing or malformed.
_PORTFOLIO_BUDGET_BY_ASSETS = {3: 3, 4: 4, 5: 4, 10: 4, 50: 20, 200: 50, 400: 100}
_PORTFOLIO_LAMBDAS = ("0", "0.000001", "0.00001", "0.00005", "0.0001", "0.0005", "0.001", "0.01")

# Auxiliary files that live under a problem's ``instances/`` folder but are not
# themselves benchmark instances. ``bounds.csv`` (Topology, 10) is a table of
# diameter lower/upper bounds; without this exclusion it was collected as an
# instance named "bounds" with status "open", inflating the instance and open
# counts. Compared case-insensitively against the file name.
_NON_INSTANCE_FILES = {"readme.md", "bounds.csv", "manifest.json"}


def _load_portfolio_manifest(problem_dir: Path) -> tuple[dict[int, int], tuple[str, ...]]:
    """Read ``instances/manifest.json`` (the single source of truth for the
    portfolio λ grid + budget-by-asset rule), falling back to the module constants
    when the file is absent or malformed. Returns ``(budget_by_assets, lambda_grid)``.

    The manifest keeps the grid out of Python constants so contributors can adjust
    the parametrization without editing the site builder; the constants remain a
    safety net so a bad/missing file never breaks the build."""
    manifest_path = problem_dir / "instances" / "manifest.json"
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        budget = {int(k): int(v) for k, v in data["budget_by_assets"].items()}
        grid = tuple(str(x) for x in data["lambda_grid"])
        if not budget or not grid:
            raise ValueError("empty manifest fields")
        return budget, grid
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return dict(_PORTFOLIO_BUDGET_BY_ASSETS), tuple(_PORTFOLIO_LAMBDAS)


def collect_portfolio_instance_sources(problem_dir: Path) -> dict[str, dict]:
    """Portfolio logical-instance sources, expanded from the physical data dirs.

    Each ``instances/po_a<AAA>_t<TT>_<seed>`` directory yields one entry per λ in
    the grid, keyed by the same normalized stem the model files use (so a source
    and its model, when present, merge onto one instance). The download target is
    the shared data-bundle directory (the per-λ split lives only in the model)."""
    instances_dir = problem_dir / "instances"
    sources: dict[str, dict] = {}
    if not instances_dir.is_dir():
        return sources

    budget_by_assets, lambda_grid = _load_portfolio_manifest(problem_dir)

    for inst_dir in sorted(p for p in instances_dir.iterdir() if p.is_dir()):
        m = re.match(r"po_a(\d{3})_t(\d{2})_(s\d{2}|orig)$", inst_dir.name)
        if not m:
            continue
        assets = int(m.group(1))
        budget = budget_by_assets.get(assets)
        if budget is None:
            continue  # an asset size with no defined budget rule — skip, don't guess
        size_bytes = sum(p.stat().st_size for p in inst_dir.rglob("*") if p.is_file())
        raw_url = config.LINKS.tree(config.rel_to_root(inst_dir))
        stem_base = f"a{assets:03d}_t{m.group(2)}_{m.group(3)}_b{budget:03d}"
        for lam in lambda_grid:
            name = normalize_portfolio_lambda(f"{stem_base}_l{lam}")
            sources[name] = {
                "name": name,
                "file": inst_dir.name,
                "format": "bundle",
                "size_bytes": size_bytes,
                "raw_url": raw_url,
            }
    return sources


# Fields projected from each fully-resolved per-λ instance into its base entry's
# ``lambdas[]`` child. Kept small: the heavy submission/time-series payloads stay
# in their own JSON files, keyed by the child ``name`` below.
_PORTFOLIO_CHILD_FIELDS = (
    "name", "status", "best_value", "bkv", "reference_solution_value",
    "reference_solution_url", "best_source_url", "best_source_label",
    "best_source_type", "best_is_optimal", "models",
)


def _portfolio_lambda_of(name: str) -> tuple[str, float | None]:
    """Extract the risk-aversion λ from a per-λ instance name (``..._l<λ>``).
    Returns ``(display, numeric)`` where display is the uniform scientific form
    (:func:`format_portfolio_lambda`) — e.g. ``("1e-06", 1e-06)``, ``("0", 0.0)``,
    ``("1e-04", 0.0001)`` — so the selector, frontier axis, and meta row never mix
    decimal and scientific spellings. A name with no ``_l`` suffix (e.g. a
    ``po_a010_t10_orig`` submission that doesn't target a specific λ) yields
    ``("n/a", None)`` so it folds into its base as an "unspecified λ" sweep entry
    rather than a stray base of its own."""
    m = re.search(r"_l([0-9.eE+-]+)$", name)
    if not m:
        return "n/a", None
    return format_portfolio_lambda(m.group(1)), num_or_none(m.group(1))


def portfolio_canonical_base(name: str, budget_by_assets: dict[int, int]) -> str:
    """Canonical base-instance key for a per-λ (or budget-less) portfolio name.

    :func:`portfolio_base_name` already strips the ``po_`` prefix and ``_l<λ>``
    suffix, but some submissions target a budget-less name (``po_a010_t10_orig``);
    those must fold into the same base as the real ``a010_t10_orig_b004`` sweep.
    When the budget token is missing, inject it from the asset count via the
    manifest rule so both group together."""
    base = portfolio_base_name(name)
    if re.search(r"_b\d+$", base):
        return base
    m = re.match(r"a(\d+)_", base)
    if m:
        budget = budget_by_assets.get(int(m.group(1)))
        if budget is not None:
            return f"{base}_b{budget:03d}"
    return base


def collapse_portfolio_instances(instances: list[dict], budget_by_assets: dict[int, int] | None = None) -> list[dict]:
    """Collapse the per-λ portfolio instances into one base entry per data set.

    The repository (and every other builder consumer — leaderboard, MIP scatter,
    landscape, per-λ solutions/submissions/time-series) keeps the full per-λ list.
    Only the browsable *instance list*, the per-problem instance table, and the
    instance-page navigation want one row per base data set, with the 8 λ folded
    into a ``lambdas[]`` sweep the instance page drives its selector + efficient-
    frontier chart from. Pure function: does not mutate its input.

    Base key = :func:`portfolio_canonical_base` (drops the ``po_`` prefix and the
    ``_l<λ>`` suffix, keeps/injects the ``_b<budget>`` token) so all 8 λ of one
    data set group together — and a budget-less submission name like
    ``po_a010_t10_orig`` folds into the same ``a010_t10_orig_b004`` base as an
    "unspecified λ" (``n/a``) sweep entry rather than a stray base of its own.
    Each ``lambdas[]`` child keeps its own per-λ ``name`` — the exact key
    ``instance_submissions.json`` / ``time_series.json`` use — so the front-end
    can look those up on demand."""
    if budget_by_assets is None:
        budget_by_assets = dict(_PORTFOLIO_BUDGET_BY_ASSETS)

    groups: dict[str, list[dict]] = {}
    order: list[str] = []
    for inst in instances:
        name = inst.get("name")
        if not name:
            continue
        base = portfolio_canonical_base(name, budget_by_assets)
        if base not in groups:
            groups[base] = []
            order.append(base)
        groups[base].append(inst)

    bases: list[dict] = []
    for base in order:
        children_src = groups[base]
        # Sort the sweep ascending by λ (0 first), "n/a" entries (budget-less
        # submissions with no specific λ) last, so the selector and frontier chart
        # read low→high risk aversion left to right.
        annotated = []
        for inst in children_src:
            disp, num = _portfolio_lambda_of(inst.get("name", ""))
            annotated.append((num if num is not None else float("inf"), disp, inst))
        annotated.sort(key=lambda t: t[0])

        lambdas: list[dict] = []
        n_real = n_solved = n_open = 0
        for num, disp, inst in annotated:
            child = {k: inst[k] for k in _PORTFOLIO_CHILD_FIELDS if k in inst}
            child["risk_lambda"] = disp
            child["risk_lambda_num"] = num if num != float("inf") else None
            child["models_count"] = len(inst.get("models") or [])
            # ``_has_subs`` is stamped by build.py before the submissions list is
            # popped; fall back to the live field when collapsing pre-pop data
            # (e.g. in unit tests that call this helper directly).
            child["has_submissions"] = bool(inst.get("_has_subs") or inst.get("submissions"))
            lambdas.append(child)
            # "n/a" children (no defined λ) stay selectable but don't count toward
            # the λ sweep size or the frontier's solved/open aggregate.
            if disp == "n/a":
                continue
            n_real += 1
            status = inst.get("status")
            if status in ("optimal", "solved"):
                n_solved += 1
            elif status == "open":
                n_open += 1

        # Aggregate status over the real λ sweep: a base is "optimal" only when its
        # whole frontier is solved, "open" only when nothing on it is,
        # "best_known" otherwise. Falls back to any child's status if there are no
        # real-λ children at all (defensive; real bases always have the sweep).
        if n_real and n_solved == n_real:
            agg_status = "optimal"
        elif n_real and n_open == n_real:
            agg_status = "open"
        elif n_real:
            agg_status = "best_known"
        else:
            agg_status = lambdas[0].get("status", "open") if lambdas else "open"

        # λ-free metadata shared across the sweep. Prefer the first real-λ child
        # (a budget-less submission child carries no metrics and points at the same
        # data dir, so a real child is the authoritative source).
        first = next((inst for _n, d, inst in annotated if d != "n/a"), children_src[0])
        metrics = dict(first.get("metrics") or {})
        metrics.pop("risk_lambda", None)  # varies per λ — lives on each child instead

        entry = {
            "id": f"06-{base}",
            "name": base,
            "file": first.get("file", base),
            "format": first.get("format", "bundle"),
            "raw_url": first.get("raw_url"),
            "status": agg_status,
            "lambda_count": n_real,
            "solved_lambda_count": n_solved,
            "has_submissions": any(c["has_submissions"] for c in lambdas),
            "lambdas": lambdas,
        }
        if first.get("size_bytes") is not None:
            entry["size_bytes"] = first["size_bytes"]
        if metrics:
            entry["metrics"] = metrics
        bases.append(entry)

    return bases


def synthesize_instance_entry(problem_id: str, problem_dir: Path, name: str) -> dict:
    if problem_id == "06":
        base = portfolio_base_name(name)
        inst_dir = problem_dir / "instances" / ("po_" + re.sub(r"_b\d+$", "", base))
        if inst_dir.is_dir():
            size_bytes = sum(p.stat().st_size for p in inst_dir.rglob('*') if p.is_file())
            return {
                "name": name,
                "file": inst_dir.name,
                "format": "bundle",
                "size_bytes": size_bytes,
                "raw_url": config.LINKS.tree(config.rel_to_root(inst_dir)),
            }
    return {
        "name": name,
        "file": name,
        "format": "generated",
        "raw_url": config.LINKS.tree(problem_dir.name),
    }


def collect_generic_instance_sources(problem_id: str, problem_dir: Path) -> dict[str, dict]:
    instances_dir = problem_dir / "instances"
    sources: dict[str, dict] = {}
    if not instances_dir.is_dir():
        return sources

    if problem_id == "04":
        for inst_dir in sorted(p for p in instances_dir.iterdir() if p.is_dir()):
            size_bytes = sum(p.stat().st_size for p in inst_dir.rglob('*') if p.is_file())
            sources[inst_dir.name] = {
                "name": inst_dir.name,
                "file": inst_dir.name,
                "format": "bundle",
                "size_bytes": size_bytes,
                "raw_url": config.LINKS.tree(config.rel_to_root(inst_dir)),
            }
        return sources

    file_iter = instances_dir.rglob('*') if problem_id == "05" else instances_dir.iterdir()
    for inst_file in sorted(p for p in file_iter if p.is_file()):
        if inst_file.name.startswith('.') or inst_file.name.lower() in _NON_INSTANCE_FILES:
            continue
        name = canonical_name_from_filename(inst_file.name)
        sources[name] = {
            "name": name,
            "file": inst_file.name,
            "format": canonical_name_from_filename(inst_file.name).split('.')[-1],
            "size_bytes": inst_file.stat().st_size,
            "raw_url": config.LINKS.raw(config.rel_to_root(inst_file)),
        }
        # overwrite format with meaningful outer format
        suffixes = [s.lstrip('.') for s in inst_file.suffixes if s]
        suffixes = [s for s in suffixes if s not in {'xz', 'gz', 'bz2'}]
        sources[name]['format'] = suffixes[-1] if suffixes else 'unknown'
    return sources


def build_birkhoff_instances(problem_id: str, problem_dir: Path, csv_subs: dict) -> list[dict]:
    instances_dir = problem_dir / 'instances'
    solution_map = load_birkhoff_solution_map(problem_dir)
    instances: list[dict] = []
    for inst_file in sorted(instances_dir.glob('qbench_*.json')):
        try:
            data = json.loads(inst_file.read_text(encoding='utf-8'))
        except Exception:
            continue
        bundle = inst_file.stem
        m = re.match(r'qbench_(\d+)_(dense|sparse)', bundle)
        if not m or not isinstance(data, dict):
            continue
        n = int(m.group(1))
        dense = m.group(2) == 'dense'
        model_prefix = f"bh{'D' if dense else 'S'}-{n:02d}"
        model_dir = problem_dir / 'models' / 'integer_linear' / 'lp_files' / model_prefix
        for key, entry in sorted(data.items()):
            if not isinstance(entry, dict):
                continue
            name = entry.get('id')
            if not name:
                continue
            num = str(key).zfill(3)
            inst_entry = {
                'id': f'{problem_id}-{name}',
                'name': name,
                'file': inst_file.name,
                'format': 'json',
                'size_bytes': inst_file.stat().st_size,
                'raw_url': config.LINKS.raw(config.rel_to_root(inst_file)),
                'status': solution_map.get(name, {}).get('status', 'open'),
                'vars': entry.get('n'),
            }
            if 'value' in solution_map.get(name, {}):
                inst_entry['bkv'] = solution_map[name]['value']
            if 'source_file' in solution_map.get(name, {}):
                inst_entry['reference_solution_source_file'] = solution_map[name]['source_file']
            model_path = model_dir / f'{model_prefix}-{num}.lp.xz'
            if model_path.exists():
                description_md, description_url = read_model_description(model_path, problem_dir / 'models')
                model_entry = {
                    'name': model_path.name,
                    'format': 'lp.xz',
                    'kind': 'lp',
                    'approach': 'integer linear',
                    'size_bytes': model_path.stat().st_size,
                    'raw_url': config.LINKS.raw(config.rel_to_root(model_path)),
                }
                if description_md:
                    model_entry['description_md'] = description_md
                if description_url:
                    model_entry['description_url'] = description_url
                inst_entry['models'] = [model_entry]
            inst_subs = csv_subs.get(name, [])
            if inst_subs:
                inst_entry['submissions'] = inst_subs
            instances.append(inst_entry)
    instances.sort(key=lambda x: (x.get('vars') or 0, x.get('name', '')))
    return instances
