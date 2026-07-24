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
"""Per-instance metric columns (the numbers shown in the problem tables).

Populates ``inst["metrics"]`` with the problem-specific values declared in
``config.PROBLEM_COLUMNS`` — sometimes parsed from the instance filename, and
sometimes read from the repository's generated ``models/*/lp_files/metrics.csv``
variable/constraint counts or a Market Split ``.dat`` header.
"""

from __future__ import annotations

import csv as _csv
import re
from pathlib import Path

from .text import canonical_name_from_filename, normalize_portfolio_lambda, num_or_none, to_int


def read_marketsplit_dims(problem_dir: Path, name: str) -> tuple[int | None, int | None]:
    """Market Split .dat files start with a line ``m n`` (constraints, variables)."""
    path = problem_dir / "instances" / f"{name}.dat"
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                return int(parts[0]), int(parts[1])
            break
    except Exception:
        pass
    return None, None


def load_lp_metrics(problem_dir: Path) -> dict[str, dict]:
    """
    Load per-instance LP metrics (variable / constraint counts, density) from the
    repository's generated ``models/*/lp_files/metrics.csv`` files, keyed by the
    canonical instance stem. Prefers a linear/integer model when several exist.
    """
    models_dir = problem_dir / "models"
    if not models_dir.is_dir():
        return {}

    candidates = sorted(models_dir.glob("*/lp_files/metrics.csv"))

    def rank(path: Path) -> tuple:
        text = str(path).lower()
        preferred = any(k in text for k in ("linear", "integer", "mixed", "flow", "mip"))
        return (0 if preferred else 1, len(text))

    candidates.sort(key=rank)

    for csv_path in candidates:
        result: dict[str, dict] = {}
        try:
            with open(csv_path, newline="", encoding="utf-8", errors="replace") as fh:
                for row in _csv.DictReader(fh):
                    fname = (row.get("file") or "").strip()
                    if not fname:
                        continue
                    stem = canonical_name_from_filename(fname)
                    stem = stem.removeprefix("bqp_").removeprefix("uqo_")
                    stem = normalize_portfolio_lambda(stem)
                    result.setdefault(stem, row)
        except Exception:
            continue
        if result:
            return result
    return {}


def load_qs_metrics(problem_dir: Path) -> dict[str, dict]:
    """
    Load per-instance QUBO metrics (``num_variables`` / ``density``) from the
    repository's generated ``models/*/qs_files/metrics.csv`` files, keyed by the
    canonical instance stem. Mirrors ``load_lp_metrics`` for the quadratic models
    used by the home-page complexity-landscape scatter.
    """
    models_dir = problem_dir / "models"
    if not models_dir.is_dir():
        return {}

    for csv_path in sorted(models_dir.glob("*/qs_files/metrics.csv")):
        result: dict[str, dict] = {}
        try:
            with open(csv_path, newline="", encoding="utf-8", errors="replace") as fh:
                for row in _csv.DictReader(fh):
                    fname = (row.get("file") or "").strip()
                    if not fname:
                        continue
                    stem = canonical_name_from_filename(fname)
                    stem = stem.removeprefix("bqp_").removeprefix("uqo_")
                    stem = normalize_portfolio_lambda(stem)
                    result.setdefault(stem, row)
        except Exception:
            continue
        if result:
            return result
    return {}


def attach_instance_metrics(problem_id: str, problem_dir: Path, instances: list[dict]) -> None:
    """Populate ``inst["metrics"]`` with the problem-specific values listed in PROBLEM_COLUMNS."""
    _lp_cache: dict | None = None

    def lp_metrics() -> dict:
        nonlocal _lp_cache
        if _lp_cache is None:
            _lp_cache = load_lp_metrics(problem_dir)
        return _lp_cache

    for inst in instances:
        name = inst.get("name") or ""
        m: dict = {}

        if problem_id == "01":
            # Filename ms_<m>_<coeff_range>_<seed>: the 2nd token is the coefficient
            # range, NOT the variable count. The true m (constraints) and n
            # (variables) live in the .dat header line "m n".
            g = re.match(r"ms_(\d+)_(\d+)_", name)
            markets, variables = read_marketsplit_dims(problem_dir, name)
            if markets is not None:
                m["markets"] = markets
                m["variables"] = variables
            elif g:
                m["markets"] = int(g.group(1))
            if g:
                m["coeff_range"] = int(g.group(2))
        elif problem_id == "02":
            g = re.search(r"(\d+)", name)
            if g:
                m["length"] = int(g.group(1))
        elif problem_id == "03":
            if inst.get("vars") is not None:
                m["dimension"] = inst["vars"]
        elif problem_id == "04":
            g = re.match(r"stp_s(\d+)_l(\d+)_t(\d+)_h(\d+)", name)
            if g:
                m["grid"] = int(g.group(1))
                m["layers"] = int(g.group(2))
                m["terminals"] = int(g.group(3))
                m["holes"] = int(g.group(4))
        elif problem_id in ("05", "08"):
            row = lp_metrics().get(name)
            if row:
                v = to_int(row.get("num_vars"))
                c = to_int(row.get("num_constraints"))
                if v is not None:
                    m["variables"] = v
                if c is not None:
                    m["constraints"] = c
        elif problem_id == "06":
            g = re.match(r"a(\d+)_t(\d+)", name)
            if g:
                m["assets"] = int(g.group(1))
                m["periods"] = int(g.group(2))
            lg = re.search(r"_l([0-9.]+(?:[eE]-?\d+)?)$", name)
            if lg:
                m["risk_lambda"] = lg.group(1)
        elif problem_id == "07":
            row = lp_metrics().get(name)
            if row:
                v = to_int(row.get("num_vars"))
                e = to_int(row.get("num_linear_constraints") or row.get("num_constraints"))
                if v is not None:
                    m["nodes"] = v
                if e is not None:
                    m["edges"] = e
        elif problem_id == "09":
            g = re.search(r"-n(\d+)-k(\d+)", name)
            if g:
                m["customers"] = int(g.group(1))
                m["vehicles"] = int(g.group(2))
        elif problem_id == "10":
            g = re.match(r"topology_(\d+)_(\d+)", name)
            if g:
                m["nodes"] = int(g.group(1))
                m["degree"] = int(g.group(2))

        if m:
            inst["metrics"] = m


def _model_stem(fname: str) -> str:
    """Canonical instance stem for an LP model file / metrics-row filename.
    Mirrors the keying used by ``models.scan_model_files`` and the old in-browser
    ``modelStemFromName`` so a metrics row maps back to its instance."""
    stem = canonical_name_from_filename(fname)
    stem = stem.removeprefix("bqp_").removeprefix("uqo_")
    return normalize_portfolio_lambda(stem)


def build_mip_points(problem_id: str, problem_dir: Path, instances: list[dict]) -> list[dict]:
    """Pre-compute the Instances-page "MIP Instance Map" scatter points from the
    repository's local ``models/*/lp_files/metrics.csv`` files.

    This is the build-time replacement for the old behaviour where the browser
    fetched every ``metrics.csv`` from raw.githubusercontent.com on each visit
    (slow, rate-limited and offline-fragile). One point is emitted per
    (instance, LP-model approach) with positive variable count and density,
    matching what the frontend used to compute at runtime.
    """
    models_dir = problem_dir / "models"
    if not models_dir.is_dir():
        return []

    # Map each LP model file stem -> the instance it belongs to. Built from the
    # already-assembled instances so it also covers Birkhoff (03), whose model
    # file names (bhD-NN-xxx) differ from the instance names.
    stem_to_inst: dict[str, str] = {}
    for inst in instances:
        for model in inst.get("models", []) or []:
            if model.get("kind") == "lp" and model.get("name"):
                stem_to_inst.setdefault(_model_stem(model["name"]), inst["name"])

    points: list[dict] = []
    for csv_path in sorted(models_dir.glob("*/lp_files/metrics.csv")):
        approach = csv_path.relative_to(models_dir).parts[0].replace("_", " ")
        model_key = f"{problem_id}::{approach}"
        try:
            with open(csv_path, newline="", encoding="utf-8", errors="replace") as fh:
                for row in _csv.DictReader(fh):
                    fname = (row.get("file") or "").strip()
                    if not fname:
                        continue
                    inst_name = stem_to_inst.get(_model_stem(fname))
                    if not inst_name:
                        continue
                    num_vars = num_or_none(row.get("num_vars"))
                    density = num_or_none(row.get("density"))
                    if num_vars is None or density is None or num_vars <= 0 or density <= 0:
                        continue
                    points.append({
                        "problem_id": problem_id,
                        "name": inst_name,
                        "num_vars": num_vars,
                        "density": density,
                        "model_approach": approach,
                        "model_kind": "lp",
                        "model_label": fname,
                        "model_key": model_key,
                    })
        except Exception:
            continue
    return points
