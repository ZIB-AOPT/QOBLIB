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
"""Top-level build orchestration.

``build_data`` scans every problem directory and emits the split JSON payload:

    <out>/data/index.json                              — lightweight home-page payload
    <out>/data/leaderboard.json                        — aggregated submissions
    <out>/data/instances.json                          — aggregated, trimmed instance list + MIP points
    <out>/data/problems/<id>/meta.json                 — per-problem metadata
    <out>/data/problems/<id>/instances.json            — per-problem instance list
    <out>/data/problems/<id>/solutions.json            — per-problem best-known values / statuses
    <out>/data/problems/<id>/submissions.json          — per-problem submission leaderboard entries
    <out>/data/problems/<id>/submission_groups.json    — per-package submission profiles
    <out>/data/problems/<id>/instance_submissions.json — per-instance detailed submissions
    <out>/data/problems/<id>/charts.json                — pre-rendered performance-chart SVGs

``build_site`` copies the static frontend (HTML/CSS/JS from ``website/``) into
the output directory, writes the generated data into ``<out>/data``, and then
post-processes the copied HTML: ``html_pages.enrich_site`` adds SEO/social meta
and the crawlable per-problem pages, and ``overview_pages.render_overview_pages``
pre-renders the overview pages' content (problem cards, instance / submission
tables, leaderboard) into their containers so the site works without JavaScript.
All page *structure* still lives in ``website/``; the Python side fills the
data-driven regions the client would otherwise populate on load.
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import config
from .charts import build_problem_charts
from .html_pages import enrich_site
from .landscape import build_landscape
from .metrics import build_mip_points
from .overview_pages import render_overview_pages
from .problem import build_problem


def _write_json(path: Path, payload) -> None:
    # Compact separators (no indent, no post-separator spaces): this data is read
    # by the client JS, never by humans, so pretty-printing is pure transfer
    # weight — it roughly halves the raw payload (~27 MB → ~15 MB across the tree,
    # led by the multi-MB per-problem time_series.json). Parses identically.
    path.write_text(
        json.dumps(payload, separators=(",", ":"), ensure_ascii=False),
        encoding="utf-8",
    )


def _index_problem_summary(data: dict) -> dict:
    """Lightweight per-problem record for the home page index."""
    return {
        "id": data["id"],
        "slug": data["slug"],
        "name": data["name"],
        "short": data["short"],
        "why": data["why"],
        "type": data["type"],
        "formulation": data["formulation"],
        "minimize": data["minimize"],
        "tags": data["tags"],
        "vars_min": data["vars_min"],
        "vars_max": data["vars_max"],
        "instance_count": data["instance_count"],
        "solved_count": data["solved_count"],
        "solved_classical_count": data["solved_classical_count"],
        "classical_best_known_count": data["classical_best_known_count"],
        "classical_found_count": data["classical_found_count"],
        "best_known_count": data["best_known_count"],
        "open_count": data["open_count"],
        "quantum_solved_count": data["quantum_solved_count"],
        "quantum_best_known_count": data["quantum_best_known_count"],
        "quantum_found_count": data["quantum_found_count"],
        "quantum_hw_solved_count": data["quantum_hw_solved_count"],
        "quantum_sim_solved_count": data["quantum_sim_solved_count"],
        "github_url": data["github_url"],
        "data_path": f"data/problems/{data['id']}",
    }


# The only per-instance fields the Instances *list* page reads. The aggregate
# data/instances.json carries just these (plus the MIP points) so the page makes
# one trimmed request instead of fetching every problem's full instances.json.
INSTANCE_LIST_FIELDS = (
    "name", "status", "best_value", "bkv", "best_is_optimal",
    "best_source_url", "best_source_label", "best_source_type", "raw_url", "metrics",
)


def _write_problem_chunks(problem_id: str, problem_dir: Path, data: dict, problems_root: Path) -> tuple[list[dict], int, dict, list[dict], dict, dict]:
    """Split one problem payload into the per-file chunks and return its
    (submissions, instance_count, instances_group, submission_groups,
    submissions_by_instance, charts) for the global aggregates + overview /
    problem-page pre-render."""
    chunk_dir = problems_root / problem_id
    chunk_dir.mkdir(parents=True, exist_ok=True)

    instances = data.pop("instances", [])

    # Pre-compute the Instances-page MIP scatter from local metrics.csv files so
    # the browser no longer fetches them from GitHub at runtime (see metrics.py).
    mip_points = build_mip_points(problem_id, problem_dir, instances)
    submissions = data.pop("submissions", [])
    submission_groups = data.pop("submission_groups", [])

    # Detailed submissions used by instance pages (popped off each instance).
    submissions_by_instance: dict[str, list[dict]] = {}
    for inst in instances:
        # Internal-only flags used by the landscape scatter (already collected by
        # build_data before this point) — keep them out of the public instances.json.
        inst.pop("quantum_optimal", None)
        inst.pop("_classical_tier", None)
        inst.pop("_quantum_tier", None)
        inst_name = inst.get("name")
        if not inst_name:
            continue
        detailed_subs = inst.pop("submissions", [])
        if detailed_subs:
            submissions_by_instance[inst_name] = detailed_subs

    solutions = [
        {
            "instance": inst.get("name"),
            "status": inst.get("status", "open"),
            **({"value": inst["bkv"]} if "bkv" in inst else {}),
        }
        for inst in instances
        if inst.get("name")
    ]

    # Pre-render the performance charts once, here, instead of in every browser
    # (see charts.py). Mirrors the `p` object the frontend assembles from the
    # meta + instances + instance_submissions chunks.
    charts = build_problem_charts({
        "id": problem_id,
        "minimize": data.get("minimize", True),
        "columns": data.get("columns", []),
        "instances": instances,
        "instance_submissions": submissions_by_instance,
    })

    # The objective time-series arrays are ~85% of instance_submissions.json but
    # are read by exactly one view (the instance-page convergence chart). Split
    # them into a separate per-instance/per-submission file so every other
    # consumer (problem, leaderboard, submission, submit pages) no longer pulls
    # megabytes of plot data. Charts are already rendered above (server-side) from
    # the in-memory copy, so stripping the written JSON costs nothing there.
    # Key each series by "<instance>::<_source_file>" so instance.js can re-attach
    # it to the right submission on demand.
    time_series: dict[str, list] = {}
    for inst_name, subs in submissions_by_instance.items():
        for s in subs:
            ts = s.pop("time_series", None)
            if ts:
                key = f"{inst_name}::{s.get('_source_file') or s.get('_source_dir') or ''}"
                time_series[key] = ts

    _write_json(chunk_dir / "meta.json", data)
    _write_json(chunk_dir / "instances.json", {"problem_id": problem_id, "instances": instances})
    _write_json(chunk_dir / "submissions.json", {"problem_id": problem_id, "entries": submissions})
    _write_json(chunk_dir / "submission_groups.json", {"problem_id": problem_id, "entries": submission_groups})
    _write_json(chunk_dir / "solutions.json", {"problem_id": problem_id, "entries": solutions})
    _write_json(chunk_dir / "instance_submissions.json", {"problem_id": problem_id, "entries": submissions_by_instance})
    _write_json(chunk_dir / "time_series.json", {"problem_id": problem_id, "entries": time_series})
    _write_json(chunk_dir / "charts.json", {"problem_id": problem_id, "entries": charts})
    _write_json(chunk_dir / "mip.json", {"problem_id": problem_id, "points": mip_points})

    # Trimmed group for the aggregated Instances-list payload (data/instances.json).
    instances_group = {
        "id": problem_id,
        "name": data.get("name", problem_id),
        "columns": data.get("columns", []),
        "instances": [
            {k: inst[k] for k in INSTANCE_LIST_FIELDS if k in inst}
            for inst in instances
        ],
        "points": mip_points,
    }

    print(
        f"  → {chunk_dir} "
        f"({len(instances)} instances, {data['solved_count']} solved, {len(submissions)} submissions)"
    )
    return submissions, data["instance_count"], instances_group, submission_groups, submissions_by_instance, charts


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _refuse_unsafe_output_dir(root: Path, out_dir: Path) -> None:
    root_resolved = root.resolve()
    out_resolved = out_dir.resolve()
    website_source = (root_resolved / "website").resolve()
    unsafe = {
        Path(out_resolved.anchor),
        root_resolved,
        root_resolved.parent,
        Path.home().resolve(),
        Path("/tmp").resolve(),
        Path("/var/tmp").resolve(),
    }
    if out_resolved in unsafe:
        raise SystemExit(f"Refusing to clean unsafe site output directory: {out_dir}")
    try:
        out_resolved.relative_to(website_source)
    except ValueError:
        pass
    else:
        raise SystemExit(
            f"Refusing to clean static frontend source directory as site output: {out_dir}"
        )


def clean_site_output(root: Path, out_dir: Path, copy_static: bool) -> None:
    """Remove stale generated output before a build.

    Full site builds own the whole output directory. Data-only builds are used
    to refresh JSON under an existing static frontend, so they only clear
    ``<out>/data``.
    """
    if copy_static:
        _refuse_unsafe_output_dir(root, out_dir)
        if out_dir.exists() or out_dir.is_symlink():
            _remove_path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        return

    data_root = out_dir / "data"
    if data_root.exists() or data_root.is_symlink():
        _remove_path(data_root)


def build_data(out_dir: Path, built_at: str | None = None) -> dict:
    """Scan the repository and write the split JSON payload under ``out_dir/data``.

    Returns a ``site_data`` dict with the site ``index`` plus the in-memory
    aggregates the overview pre-render step consumes (``problems``,
    ``instances_groups``, ``submission_groups``, ``instance_subs``)."""
    data_root = out_dir / "data"
    problems_root = data_root / "problems"
    data_root.mkdir(parents=True, exist_ok=True)
    problems_root.mkdir(parents=True, exist_ok=True)

    problem_dirs = config.find_problem_dirs()
    if not problem_dirs:
        print("No problem directories found. Run from the repository root.", file=sys.stderr)
        raise SystemExit(1)

    all_submissions: list[dict] = []
    index_problems: list[dict] = []
    landscape_inputs: list[dict] = []
    instances_groups: list[dict] = []
    all_submission_groups: list[dict] = []
    instance_subs_by_problem: dict[str, dict] = {}
    problem_details: list[dict] = []  # full per-problem payloads for the deep-page pre-render
    _minimize_by_problem: dict[str, bool] = {}
    total_instances = 0

    for problem_id, problem_dir in problem_dirs:
        print(f"Processing {problem_dir.name}…")
        data = build_problem(problem_id, problem_dir)
        _minimize_by_problem[problem_id] = data.get("minimize", True) is not False
        index_problems.append(_index_problem_summary(data))
        # Snapshot the per-instance fields the home-page landscape scatter needs,
        # before _write_problem_chunks pops instances/flags off the payload.
        landscape_inputs.append({
            "problem_id": problem_id,
            "problem_name": data["name"],
            "problem_dir": problem_dir,
            "instances": [
                {
                    "name": inst.get("name"),
                    "is_optimal": bool(inst.get("best_is_optimal")),
                    "best_known": inst.get("status") == "best_known",
                    "quantum_optimal": bool(inst.get("quantum_optimal")),
                    # Per-paradigm tier (optimal · best_known · found · open) that
                    # the landscape insets colour by, mirroring the problem-card bars.
                    "classical_tier": inst.get("_classical_tier"),
                    "quantum_tier": inst.get("_quantum_tier"),
                    # Model filenames carry the authoritative metric stem (an
                    # instance's name doesn't always match its model file, e.g.
                    # Birkhoff B3_3_1 → bhS-03-001) — landscape.py joins on these.
                    "models": [
                        {"name": m.get("name"), "kind": m.get("kind")}
                        for m in (inst.get("models") or [])
                    ],
                }
                for inst in data.get("instances", [])
            ],
        })
        submissions, instance_count, instances_group, submission_groups, subs_by_instance, charts = _write_problem_chunks(
            problem_id, problem_dir, data, problems_root
        )
        all_submissions.extend(submissions)
        instances_groups.append(instances_group)
        all_submission_groups.extend(submission_groups)
        instance_subs_by_problem[problem_id] = subs_by_instance
        total_instances += instance_count
        # Full per-problem payload for the deep-page pre-render: the meta (data,
        # with instances/submissions already popped off) plus the trimmed instance
        # list, this problem's submission packages, and its pre-baked charts.
        problem_details.append({
            **data,
            "instances": instances_group["instances"],
            "submission_groups": submission_groups,
            "charts": charts,
        })

    # Pre-render the home-page complexity-landscape scatter plots (MIP + QUBO)
    # once, here, instead of shipping static PNGs (see landscape.py).
    landscape = build_landscape(landscape_inputs)
    _write_json(data_root / "landscape.json", landscape)
    print(f"→ {data_root / 'landscape.json'}")

    # Aggregated leaderboard payload: a single self-contained file the page uses
    # to compute one champion record per instance, instead of fanning out to
    # meta + instances + instance_submissions for all ten problems (was ~30
    # requests / several MB). Trimmed to exactly the fields lbChampion /
    # lbMakeRecord read; keyed per problem so the page keeps its existing shape.
    _LB_SUB_FIELDS = ("value", "n_feasible", "runtime_total", "date", "category",
                      "submitter", "author", "_source_dir")
    _LB_INST_FIELDS = ("name", "status", "best_value", "bkv")
    leaderboard_problems = []
    for grp in instances_groups:
        pid = grp["id"]
        subs = instance_subs_by_problem.get(pid, {})
        trimmed_subs = {
            name: [{k: s[k] for k in _LB_SUB_FIELDS if k in s} for s in rows]
            for name, rows in subs.items()
        }
        leaderboard_problems.append({
            "id": pid,
            "name": grp.get("name", pid),
            "minimize": _minimize_by_problem.get(pid, True),
            "instances": [
                {k: inst[k] for k in _LB_INST_FIELDS if k in inst}
                for inst in grp.get("instances", [])
            ],
            "instance_submissions": trimmed_subs,
        })
    _write_json(data_root / "leaderboard.json", {"problems": leaderboard_problems})
    print(f"\n→ {data_root / 'leaderboard.json'}  ({len(all_submissions)} submissions, aggregated)")

    # Aggregated, trimmed Instances-list payload: lets the Instances page load in
    # a single request instead of fetching every problem's full instances.json +
    # mip.json (was 1 + 2×N files).
    _write_json(data_root / "instances.json", {"problems": instances_groups})
    print(f"→ {data_root / 'instances.json'}  ({total_instances} instances)")

    built_at = built_at or datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    index = {
        "built_at": built_at,
        "commit": config.get_commit_hash(),
        "total_instances": total_instances,
        "total_submissions": len(all_submissions),
        "problems": index_problems,
    }
    _write_json(data_root / "index.json", index)
    print(f"→ {data_root / 'index.json'}")
    print(f"\nDone. {len(problem_dirs)} problems, {total_instances} instances, {len(all_submissions)} submissions.")

    # Aggregates for the overview pre-render step (render_overview_pages). These
    # mirror the JSON the frontend fetches, so the pre-rendered HTML matches the
    # client-hydrated view. No extra files are written; this is in-memory only.
    return {
        "index": index,
        "problems": index_problems,
        "instances_groups": instances_groups,
        "submission_groups": all_submission_groups,
        "instance_subs": instance_subs_by_problem,
        "landscape": landscape,
        "problem_details": problem_details,
    }


def copy_static_frontend(root: Path, out_dir: Path) -> None:
    """Copy the static site (HTML/CSS/JS/images) from ``<root>/website`` into ``out_dir``."""
    website_dir = root / "website"
    if not website_dir.is_dir():
        raise SystemExit(f"Static frontend directory not found: {website_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(website_dir, out_dir, dirs_exist_ok=True)


def build_site(
    out: Path | str,
    root: Path | str = ".",
    repo_url: str = config.DEFAULT_REPO_URL,
    ref: str = config.DEFAULT_REF,
    built_at: str | None = None,
    copy_static: bool = True,
    base_url: str = config.DEFAULT_BASE_URL,
) -> dict:
    """Assemble the full static site under ``out``.

    Configures the build context, copies the static frontend, writes the
    generated data, and (for full builds) enriches the HTML with SEO/social meta
    and generates the pretty per-problem pages + sitemap. Returns a small summary
    dict (problem / instance / submission counts).
    """
    root = Path(root)
    out = Path(out)
    config.configure(root, repo_url, ref)
    clean_site_output(root, out, copy_static=copy_static)
    if copy_static:
        copy_static_frontend(root, out)
    site_data = build_data(out, built_at=built_at)
    index = site_data["index"]
    if copy_static:
        # Pass the full per-problem payloads so the deep problem/<id>/ pages are
        # rendered with their instances table, submissions and charts (not just a
        # summary) — usable without JS. Falls back to the summary if absent.
        enrich_site(out, index["problems"], base_url, problem_details=site_data.get("problem_details"))
        # Pre-render the overview pages' content into the copied HTML so the site
        # is usable without JavaScript (the client scripts hydrate over it). Runs
        # after enrich_site so meta/skip-link are already in place.
        render_overview_pages(out, site_data)
    return {
        "problems": len(index["problems"]),
        "instances": index["total_instances"],
        "submissions": index["total_submissions"],
    }
