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
"""Assemble the full per-problem data payload.

``build_problem`` ties the pieces together: it discovers instances, attaches
metrics and model artifacts, resolves the best-known value and its canonical
source per instance, classifies which compute paradigms reached the optimum,
and groups submission rows into uploaded packages. The returned dict is later
split into the individual ``data/problems/<id>/*.json`` files.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from . import config
from .classify import classify_submission, is_infeasible_sub
from .instances import (
    build_birkhoff_instances,
    collect_generic_instance_sources,
    synthesize_instance_entry,
)
from .metrics import attach_instance_metrics
from .models import scan_model_files
from .solutions import read_solutions_folder
from .submissions import read_csv_submissions_folder
from .text import (
    extract_problem_intro,
    normalize_portfolio_lambda,
    num_or_none,
    parse_instance_filename,
)


def _submission_proves_optimal(sub: dict) -> bool:
    """A feasible submission proves optimality when its reported objective meets
    its own optimality bound — i.e. an exact solver that closed the gap.
    Works for both minimisation and maximisation (compares the absolute gap)."""
    obj = num_or_none(sub.get("value"))
    bound = num_or_none(sub.get("optimality_bound"))
    if obj is None or bound is None:
        return False
    tol = 1e-6 * max(1.0, abs(obj), abs(bound))
    return abs(obj - bound) <= tol


# Package-level metadata kept only when it is consistent across every row in a
# submission package (instance-specific counts are rendered in the table).
PROFILE_KEYS = [
    "submitter", "affiliation", "date", "reference", "modeling_approach",
    "algorithm_type", "paradigm", "workflow", "hardware", "runtime_total",
    "time_to_solution", "runtime_cpu", "runtime_gpu", "runtime_qpu",
    "runtime_other", "n_runs", "n_feasible", "n_successful",
    "success_threshold", "coefficients_type", "n_vars", "n_binary",
    "n_integer", "n_continuous", "n_nonzero", "optimality_bound", "remarks",
]


def _collect_instances(problem_id: str, problem_dir: Path, bkv_map: dict,
                       model_map: dict, csv_subs: dict) -> list[dict]:
    """Discover and assemble the raw instance list (pre best-value resolution)."""
    if problem_id == "03":
        return build_birkhoff_instances(problem_id, problem_dir, csv_subs)

    sources = collect_generic_instance_sources(problem_id, problem_dir)
    if problem_id == "02":
        all_names = set(bkv_map) | set(model_map)
    elif problem_id == "06":
        all_names = set(model_map) | {normalize_portfolio_lambda(name) for name in csv_subs}
    elif problem_id == "08":
        all_names = {
            name for name in set(bkv_map) | set(model_map) | set(csv_subs)
            if re.match(r"^network\d+$", name)
        }
    else:
        all_names = set(sources) | set(bkv_map) | set(model_map)

    instances: list[dict] = []
    for stem in sorted(all_names):
        source = dict(sources.get(stem) or synthesize_instance_entry(problem_id, problem_dir, stem))
        fn_meta = parse_instance_filename(problem_id, stem)
        n_vars = fn_meta.get("vars")
        bkv_entry = bkv_map.get(stem) or {}
        bkv = bkv_entry.get("value")
        status = bkv_entry.get("status", "open" if bkv is None else "best_known")

        inst_entry: dict = {
            "id": f"{problem_id}-{stem}",
            "name": stem,
            "file": source.get("file", stem),
            "format": source.get("format", "unknown"),
            "raw_url": source["raw_url"],
            "status": status,
        }
        if source.get("size_bytes") is not None:
            inst_entry["size_bytes"] = source["size_bytes"]
        if n_vars is not None:
            inst_entry["vars"] = n_vars
        if bkv is not None:
            inst_entry["bkv"] = bkv
        if stem in model_map:
            inst_entry["models"] = model_map[stem]
        for k in ("n_constraints", "index"):
            if k in fn_meta and fn_meta[k] is not None:
                inst_entry[k] = fn_meta[k]
        inst_subs = csv_subs.get(stem, [])
        if problem_id == "06" and not inst_subs:
            inst_subs = csv_subs.get(stem.replace("_l0.0", "_l0"), [])
        if inst_subs:
            inst_entry["submissions"] = inst_subs

        instances.append(inst_entry)

    instances.sort(key=lambda x: (x.get("vars") or 0, x.get("name", "")))
    return instances


def _paradigm_status(optimal_reached: bool, para_best, best_value, minimize: bool) -> str:
    """Classify how far one compute paradigm got on an instance, for the
    four-segment progress bars: ``optimal`` (proven) · ``best_known`` (matched
    the best value, optimality unproven) · ``found`` (some feasible solution,
    worse than the best value) · ``open`` (nothing feasible)."""
    if optimal_reached:
        return "optimal"
    if not isinstance(para_best, (int, float)):
        return "open"
    if isinstance(best_value, (int, float)):
        tol = 1e-6 * max(1.0, abs(float(best_value)))
        if abs(float(para_best) - float(best_value)) <= tol:
            return "best_known"
    return "found"


def _resolve_best_values(problem_dir: Path, meta: dict, instances: list[dict],
                         bkv_map: dict, csv_subs: dict) -> tuple[set, set, set]:
    """Annotate each instance with its best value + source, and report which
    compute paradigms reached the proven optimum."""
    solved_by_quantum_hw: set[str] = set()
    solved_by_quantum_sim: set[str] = set()
    solved_by_classical_sub: set[str] = set()

    for inst in instances:
        inst_name = inst.get("name")
        if not inst_name:
            continue

        bkv_entry = bkv_map.get(inst_name) or {}
        bkv = inst.get("bkv")
        solution_source_url = None
        solution_source_file = bkv_entry.get("source_file") or inst.get("reference_solution_source_file")
        if solution_source_file:
            solution_source_url = config.LINKS.blob(solution_source_file)

        ref_status = bkv_entry.get("status") or inst.get("status")
        if solution_source_url:
            inst["reference_solution_url"] = solution_source_url
        if isinstance(bkv_entry.get("value"), (int, float)):
            inst["reference_solution_value"] = bkv_entry["value"]
        elif isinstance(bkv, (int, float)):
            inst["reference_solution_value"] = bkv
        if ref_status:
            inst["reference_solution_status"] = ref_status

        # Avoid claiming optimality when there is no objective value and no reference artifact.
        if (
            inst.get("status") in ("optimal", "solved")
            and "reference_solution_value" not in inst
            and "reference_solution_url" not in inst
        ):
            inst["status"] = "best_known"

        # Infeasible runs (# Feasible Runs == 0) must never define the best
        # objective — their reported value is not a valid solution (this is what
        # made Market Split show a bogus negative QUBO energy).
        inst_subs = [
            s for s in (inst.get("submissions") or csv_subs.get(inst_name, []))
            if not is_infeasible_sub(s)
        ]

        best_value = bkv if isinstance(bkv, (int, float)) else None
        best_source_type = "solution" if best_value is not None else None
        best_source_url = solution_source_url if best_value is not None else None

        for sub in inst_subs:
            sub_val = sub.get("value")
            if not isinstance(sub_val, (int, float)):
                continue
            if best_value is None:
                better = True
            elif meta.get("minimize", True):
                better = sub_val < best_value
            else:
                better = sub_val > best_value

            # Strictly better submissions override the current best.
            # Equal values keep the reference solution as source when available.
            if better:
                best_value = sub_val
                best_source_type = "submission"
                if sub.get("_source_file"):
                    best_source_url = config.LINKS.blob(
                        f"{problem_dir.name}/submissions/{sub['_source_file']}"
                    )
                else:
                    best_source_url = config.LINKS.tree(f"{problem_dir.name}/submissions")

        numeric_sub_vals = [sub.get("value") for sub in inst_subs if isinstance(sub.get("value"), (int, float))]
        if (
            best_source_type == "submission"
            and solution_source_url
            and inst.get("status") in ("optimal", "solved")
            and numeric_sub_vals
            and len({float(v) for v in numeric_sub_vals}) == 1
        ):
            # If all available submission values are identical for an optimally solved instance,
            # prefer the repository reference solution as the canonical source.
            best_source_type = "solution"
            best_source_url = solution_source_url

        # In listings, prefer the repository reference source whenever it achieves the best value.
        if (
            solution_source_url
            and isinstance(bkv, (int, float))
            and isinstance(best_value, (int, float))
            and abs(float(best_value) - float(bkv)) <= 1e-12
        ):
            best_source_type = "solution"
            best_source_url = solution_source_url

        if best_value is not None:
            inst["best_value"] = best_value
        if best_source_type:
            inst["best_source_type"] = best_source_type
        if best_source_url:
            inst["best_source_url"] = best_source_url

        # Best feasible objective each paradigm achieved on this instance. Powers
        # the four-segment progress bars, which split "matched the best-known
        # value" from "found some (worse) feasible solution". The repository
        # reference solution counts as a classical result.
        classical_vals: list[float] = []
        quantum_vals: list[float] = []
        if isinstance(inst.get("reference_solution_value"), (int, float)):
            classical_vals.append(float(inst["reference_solution_value"]))
        for sub in inst_subs:
            sv = sub.get("value")
            if not isinstance(sv, (int, float)):
                continue
            cat = sub.get("category") or classify_submission(sub)
            target = quantum_vals if cat in ("quantum_hw", "quantum_sim") else classical_vals
            target.append(float(sv))
        pick = min if meta.get("minimize", True) else max
        inst["_classical_best"] = pick(classical_vals) if classical_vals else None
        inst["_quantum_best"] = pick(quantum_vals) if quantum_vals else None

        # A feasible submission can establish status even when no reference
        # solution carries an explicit optimal/best-known marker — e.g. Portfolio,
        # whose reference solutions are opaque archives. Optimality is proven when
        # a feasible submission's objective meets its own optimality bound;
        # otherwise a known feasible value makes the instance best-known.
        if inst.get("status") not in ("optimal", "solved"):
            if any(_submission_proves_optimal(sub) for sub in inst_subs):
                inst["status"] = "optimal"
            elif best_value is not None:
                inst["status"] = "best_known"

        is_optimal = inst.get("status") in ("optimal", "solved")
        inst["best_is_optimal"] = is_optimal
        if best_source_type == "solution":
            inst["best_source_label"] = "Reference solution"
        elif best_source_type == "submission":
            inst["best_source_label"] = "Best submission"

        # Did a (feasible) submission of each paradigm reach the proven optimum?
        if is_optimal:
            opt_val = inst.get("reference_solution_value")
            if not isinstance(opt_val, (int, float)):
                opt_val = best_value if isinstance(best_value, (int, float)) else None
            if isinstance(opt_val, (int, float)):
                tol = 1e-6 * max(1.0, abs(float(opt_val)))
                for sub in inst_subs:  # inst_subs is already feasible-only
                    sv = sub.get("value")
                    if not isinstance(sv, (int, float)) or abs(float(sv) - float(opt_val)) > tol:
                        continue
                    cat = sub.get("category") or classify_submission(sub)
                    if cat == "quantum_hw":
                        solved_by_quantum_hw.add(inst_name)
                    elif cat == "quantum_sim":
                        solved_by_quantum_sim.add(inst_name)
                    else:
                        solved_by_classical_sub.add(inst_name)

    return solved_by_quantum_hw, solved_by_quantum_sim, solved_by_classical_sub


def _build_submission_groups(problem_id: str, problem_dir: Path, csv_subs: dict) -> list[dict]:
    """Group submission rows by source package → one detail page per upload."""
    grouped_rows: dict[str, list[dict]] = defaultdict(list)
    for subs in csv_subs.values():
        for sub in subs:
            source_dir = (sub.get("_source_dir") or "").strip()
            source_file = (sub.get("_source_file") or "").strip()
            fallback = Path(source_file).stem if source_file else "submission"
            group_id = source_dir or fallback
            grouped_rows[group_id].append(sub)

    submission_groups: list[dict] = []
    for group_id in sorted(grouped_rows):
        rows = grouped_rows[group_id]
        first = rows[0]

        profile = {}
        for key in PROFILE_KEYS:
            values = [r.get(key) for r in rows if r.get(key) not in (None, "")]
            if not values:
                continue
            first_value = values[0]
            if all(value == first_value for value in values[1:]):
                profile[key] = first_value

        source_files = sorted({r.get("_source_file") for r in rows if r.get("_source_file")})
        source_urls = [
            config.LINKS.blob(f"{problem_dir.name}/submissions/{f}")
            for f in source_files
        ]

        instances_in_group = [
            {
                "instance": r.get("instance"),
                "value": r.get("value"),
                "optimality_bound": r.get("optimality_bound"),
                "date": r.get("date"),
            }
            for r in rows
            if r.get("instance")
        ]
        instances_in_group.sort(key=lambda x: x.get("instance") or "")

        # Compute-paradigm of the whole package: classify every row, then take
        # the dominant paradigm. Ties break toward the more "quantum" paradigm
        # (hw > sim > classical) so a package that touched real hardware is
        # surfaced as such. Rows already carry a per-row category (see
        # read_csv_submissions_folder); recompute defensively when absent.
        cat_counts = {"quantum_hw": 0, "quantum_sim": 0, "classical": 0}
        for r in rows:
            cat = r.get("category") or classify_submission(r)
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
        cat_priority = {"quantum_hw": 3, "quantum_sim": 2, "classical": 1}
        category = max(cat_counts, key=lambda c: (cat_counts[c], cat_priority[c]))

        submission_groups.append({
            "id": group_id,
            "problem_id": problem_id,
            "source_dir": first.get("_source_dir", ""),
            "source_files": source_files,
            "source_urls": source_urls,
            "category": category,
            "category_counts": cat_counts,
            "profile": profile,
            "instances": instances_in_group,
        })
    return submission_groups


def build_problem(problem_id: str, problem_dir: Path) -> dict:
    """Build the full per-problem data dict (also written to disk by the caller)."""
    meta = config.PROBLEM_META.get(problem_id, {})
    solutions_dir = problem_dir / "solutions"
    submissions_dir = problem_dir / "submissions"

    bkv_map = read_solutions_folder(solutions_dir)
    model_map = scan_model_files(problem_dir)

    # --- Read README for long description (fallback to static meta) ---
    readme_text = ""
    for rname in ("README.md", "readme.md", "README.txt"):
        rpath = problem_dir / rname
        if rpath.exists():
            readme_text = rpath.read_text(encoding="utf-8", errors="replace")
            break
    readme_intro_md = extract_problem_intro(readme_text)

    # The real instance names let the submission reader rescue rows whose
    # "Problem" column holds a label rather than the instance id (see
    # _resolve_instance); their path encodes the true instance.
    known_instances = set(bkv_map) | set(model_map)
    csv_subs = read_csv_submissions_folder(submissions_dir, known_instances)

    instances = _collect_instances(problem_id, problem_dir, bkv_map, model_map, csv_subs)

    # Attach problem-specific metric columns (nodes/edges, assets/periods, ...).
    attach_instance_metrics(problem_id, problem_dir, instances)

    solved_hw, solved_sim, solved_classical_sub = _resolve_best_values(
        problem_dir, meta, instances, bkv_map, csv_subs
    )

    # Per-instance "reached the optimum with a quantum submission" flag, mirroring
    # the quantum progress bar. Consumed by the home-page landscape scatter
    # (landscape.py via build.py); stripped before instances.json is written.
    quantum_optimal_names = solved_hw | solved_sim
    minimize = meta.get("minimize", True)
    # Four-segment progress-bar counts per paradigm: optimal · best-known
    # (matched the best value) · found (some feasible, worse) · open (rest).
    classical_best_known = classical_found = 0
    quantum_best_known = quantum_found = 0
    for inst in instances:
        name = inst.get("name")
        inst["quantum_optimal"] = name in quantum_optimal_names
        is_optimal = inst.get("status") in ("optimal", "solved")
        classical_optimal = is_optimal and (
            name in solved_classical_sub
            or inst.get("reference_solution_url")
            or isinstance(inst.get("reference_solution_value"), (int, float))
        )
        best_value = inst.get("best_value")
        cstat = _paradigm_status(classical_optimal, inst.pop("_classical_best", None), best_value, minimize)
        qstat = _paradigm_status(inst["quantum_optimal"], inst.pop("_quantum_best", None), best_value, minimize)
        # Per-paradigm tier, mirroring the four-segment progress bars. Consumed by
        # the home-page landscape insets (via build.py); stripped before
        # instances.json is written.
        inst["_classical_tier"] = cstat
        inst["_quantum_tier"] = qstat
        if cstat == "best_known":
            classical_best_known += 1
        elif cstat == "found":
            classical_found += 1
        if qstat == "best_known":
            quantum_best_known += 1
        elif qstat == "found":
            quantum_found += 1

    # Collect all submissions as leaderboard-format entries.
    submissions: list[dict] = []
    for subs in csv_subs.values():
        for sub in subs:
            submissions.append({
                "instance":   sub["instance"],
                "value":      sub["value"],
                "solver":     sub.get("modeling_approach") or sub.get("algorithm_type", ""),
                "author":     sub.get("submitter", ""),
                "date":       sub.get("date", ""),
                "notes":      sub.get("remarks") or sub.get("hardware", ""),
                "category":   sub.get("category") or classify_submission(sub),
                "problem_id": problem_id,
                "_source_dir": sub.get("_source_dir", ""),
            })

    submission_groups = _build_submission_groups(problem_id, problem_dir, csv_subs)

    # --- Assemble output ---
    n_solved = sum(1 for i in instances if i.get("status") in ("optimal", "solved"))
    n_best_known = sum(1 for i in instances if i.get("status") == "best_known")
    n_open = sum(1 for i in instances if i.get("status") == "open")
    # Classically-solved = optimal instances whose proven optimum came from a
    # classical method: either the repository's (classical) reference solution or
    # a classical submission that reached it. This is the counterpart to
    # quantum_solved_count and powers the "Classical" progress bar — unlike the
    # method-agnostic solved_count, it excludes instances proven optimal only by a
    # quantum submission.
    n_classical_solved = sum(
        1
        for i in instances
        if i.get("status") in ("optimal", "solved")
        and (
            i.get("name") in solved_classical_sub
            or i.get("reference_solution_url")
            or isinstance(i.get("reference_solution_value"), (int, float))
        )
    )
    n_quantum_solved = len(solved_hw | solved_sim)
    n_quantum_hw_solved = len(solved_hw)
    n_quantum_sim_solved = len(solved_sim)
    vars_list = [i["vars"] for i in instances if "vars" in i]

    return {
        "id": problem_id,
        "slug": meta.get("slug", problem_dir.name.split("-", 1)[-1]),
        "name": meta.get("name", problem_dir.name),
        "short": meta.get("short", ""),
        "why": meta.get("why", ""),
        "description": meta.get("description", ""),
        "description_md": readme_intro_md,
        "formula": meta.get("formula", ""),
        "type": meta.get("type", ""),
        "formulation": meta.get("formulation", ""),
        "minimize": meta.get("minimize", True),
        "tags": meta.get("tags", []),
        "columns": config.PROBLEM_COLUMNS.get(problem_id, []),
        "vars_min": min(vars_list) if vars_list else None,
        "vars_max": max(vars_list) if vars_list else None,
        "instance_count": len(instances),
        "solved_count": n_solved,
        "solved_classical_count": n_classical_solved,
        "classical_best_known_count": classical_best_known,
        "classical_found_count": classical_found,
        "best_known_count": n_best_known,
        "open_count": n_open,
        "quantum_solved_count": n_quantum_solved,
        "quantum_best_known_count": quantum_best_known,
        "quantum_found_count": quantum_found,
        "quantum_hw_solved_count": n_quantum_hw_solved,
        "quantum_sim_solved_count": n_quantum_sim_solved,
        "instances": instances,
        "submissions": submissions,
        "submission_groups": submission_groups,
        "github_url": config.LINKS.tree(problem_dir.name),
    }
