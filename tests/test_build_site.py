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
"""Tests for the QOBLIB static-site data builder (``misc/ci/site_builder``)."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "misc" / "ci"))

import site_builder  # noqa: E402
from site_builder import config  # noqa: E402
from site_builder.build import build_site  # noqa: E402


CANONICAL_COLUMNS = [
    "Problem", "Submitter", "Date", "Reference", "Best Objective Value",
    "Optimality Bound", "Modeling Approach", "# Decision Variables",
    "# Binary Variables", "# Integer Variables", "# Continuous Variables",
    "# Non-Zero Coefficients", "Coefficients Type", "Coefficients Range",
    "Workflow", "Algorithm Type", "# Runs", "# Feasible Runs",
    "# Successful Runs", "Success Threshold", "Hardware Specifications",
    "Total Runtime", "CPU Runtime", "GPU Runtime", "QPU Runtime",
    "Other HW Runtime", "Remarks",
]


def _write_summary_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CANONICAL_COLUMNS)
        writer.writeheader()
        for row in rows:
            full = {col: "N/A" for col in CANONICAL_COLUMNS}
            full.update(row)
            writer.writerow(full)


def make_fixture(root: Path) -> None:
    """A minimal repository with one Market Split (problem 01) instance, a
    reference solution, a feasible submission and an infeasible submission, plus
    a tiny static frontend so the static-copy step has something to copy."""
    # Static frontend source (what build_site copies into the output).
    (root / "website" / "assets").mkdir(parents=True)
    (root / "website" / "index.html").write_text("<!doctype html><title>QOBLIB</title>\n", encoding="utf-8")
    (root / "website" / "assets" / "styles.css").write_text("body{}\n", encoding="utf-8")

    problem = root / "01-marketsplit"
    (problem / "instances").mkdir(parents=True)
    (problem / "solutions").mkdir(parents=True)
    (problem / "README.md").write_text(
        "# 01 - Market Split\n\n"
        "## Overview\n\nA multi-dimensional subset sum benchmark.\n\n"
        "## Problem Description\n\nFind $x \\in \\{0,1\\}^n$ with $Ax = b$.\n",
        encoding="utf-8",
    )
    # Market Split .dat: header line "m n" = 3 constraints, 50 variables.
    (problem / "instances" / "ms_03_050_001.dat").write_text("3 50\n1 0 1\n", encoding="utf-8")
    # Reference optimal solution with an inline objective of 0.
    (problem / "solutions" / "ms_03_050_001.opt.sol").write_text(
        "# Objective value = 0\n0 1 0\n", encoding="utf-8"
    )

    _write_summary_csv(
        problem / "submissions" / "20260101_Abs2_Author" / "ms_03_050_001" / "ms_03_050_001_summary.csv",
        [{
            "Problem": "ms_03_050_001", "Submitter": "Ada Example",
            "Date": "2026-01-02", "Best Objective Value": "0",
            "Optimality Bound": "0", "Modeling Approach": "Binary Linear Program",
            "Algorithm Type": "Deterministic", "# Feasible Runs": "1",
            "Hardware Specifications": "Local machine", "Total Runtime": "0.1",
        }],
    )
    # An infeasible run reporting a bogus "better" value that must be ignored.
    _write_summary_csv(
        problem / "submissions" / "20260105_Bogus_Author" / "ms_03_050_001" / "ms_03_050_001_summary.csv",
        [{
            "Problem": "ms_03_050_001", "Submitter": "Bogus Bot",
            "Date": "2026-01-05", "Best Objective Value": "-999",
            "Modeling Approach": "QUBO", "# Feasible Runs": "0",
        }],
    )


class BuildSiteTests(unittest.TestCase):
    def build(self, repo_url: str = config.DEFAULT_REPO_URL, ref: str = config.DEFAULT_REF):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        make_fixture(root)
        out = root / "_site"
        summary = build_site(out=out, root=root, repo_url=repo_url, ref=ref,
                             built_at="2026-01-01T00:00:00Z")
        return root, out, summary

    def load(self, out: Path, *parts: str) -> dict:
        return json.loads((out.joinpath(*parts)).read_text(encoding="utf-8"))

    def test_summary_counts(self) -> None:
        _root, _out, summary = self.build()
        self.assertEqual(summary["problems"], 1)
        self.assertEqual(summary["instances"], 1)
        self.assertEqual(summary["submissions"], 2)  # both rows kept for the leaderboard

    def test_expected_data_files_and_static_copy(self) -> None:
        _root, out, _summary = self.build()
        # Static frontend copied verbatim.
        self.assertTrue((out / "index.html").is_file())
        self.assertTrue((out / "assets" / "styles.css").is_file())
        # Generated data payload split per problem.
        for rel in (
            "data/index.json", "data/leaderboard.json",
            "data/problems/01/meta.json", "data/problems/01/instances.json",
            "data/problems/01/solutions.json", "data/problems/01/submissions.json",
            "data/problems/01/submission_groups.json",
            "data/problems/01/instance_submissions.json",
        ):
            self.assertTrue((out / rel).is_file(), f"missing {rel}")

    def test_full_site_build_cleans_stale_output(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        make_fixture(root)
        out = root / "_site"
        (out / "assets").mkdir(parents=True)
        (out / "assets" / "stale.js").write_text("old\n", encoding="utf-8")

        build_site(out=out, root=root, built_at="2026-01-01T00:00:00Z")

        self.assertFalse((out / "assets" / "stale.js").exists())
        self.assertTrue((out / "index.html").is_file())
        self.assertTrue((out / "data" / "index.json").is_file())

    def test_full_site_build_refuses_static_source_output(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        make_fixture(root)
        source_index = root / "website" / "index.html"

        with self.assertRaises(SystemExit):
            build_site(out=root / "website", root=root, built_at="2026-01-01T00:00:00Z")
        self.assertTrue(source_index.is_file())

        with self.assertRaises(SystemExit):
            build_site(out=root / "website" / "_site", root=root, built_at="2026-01-01T00:00:00Z")
        self.assertTrue(source_index.is_file())

    def test_data_only_build_cleans_generated_data_only(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        make_fixture(root)
        out = root / "_site"
        out.mkdir()
        (out / "index.html").write_text("<title>keep</title>\n", encoding="utf-8")
        (out / "data").mkdir()
        (out / "data" / "stale.json").write_text("{}\n", encoding="utf-8")

        build_site(out=out, root=root, copy_static=False, built_at="2026-01-01T00:00:00Z")

        self.assertTrue((out / "index.html").is_file())
        self.assertFalse((out / "data" / "stale.json").exists())
        self.assertTrue((out / "data" / "index.json").is_file())

    def test_builder_emits_no_html(self) -> None:
        """The builder itself must not generate HTML — with the static copy
        disabled, the output contains only JSON data."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        make_fixture(root)
        out = root / "_data_only"
        build_site(out=out, root=root, copy_static=False, built_at="2026-01-01T00:00:00Z")
        produced = [p for p in out.rglob("*") if p.is_file()]
        self.assertTrue(produced)
        self.assertTrue(all(p.suffix == ".json" for p in produced),
                        f"non-JSON output: {[p.name for p in produced if p.suffix != '.json']}")

    def test_index_payload(self) -> None:
        _root, out, _summary = self.build()
        index = self.load(out, "data", "index.json")
        self.assertEqual(index["built_at"], "2026-01-01T00:00:00Z")
        self.assertEqual(index["total_instances"], 1)
        self.assertEqual(index["total_submissions"], 2)
        self.assertEqual(len(index["problems"]), 1)
        prob = index["problems"][0]
        self.assertEqual(prob["id"], "01")
        self.assertEqual(prob["slug"], "marketsplit")
        self.assertEqual(prob["data_path"], "data/problems/01")

    def test_problem_meta_and_columns(self) -> None:
        _root, out, _summary = self.build()
        meta = self.load(out, "data", "problems", "01", "meta.json")
        self.assertEqual(meta["name"], "Market Split")
        self.assertEqual(meta["instance_count"], 1)
        self.assertEqual(meta["solved_count"], 1)
        self.assertIn("Overview", meta["description_md"])
        self.assertEqual([c["key"] for c in meta["columns"]], ["markets", "variables", "coeff_range"])

    def test_portfolio_metadata_matches_minimization_readme(self) -> None:
        meta = config.PROBLEM_META["06"]
        self.assertTrue(meta["minimize"])
        self.assertTrue(meta["formula"].startswith("min "))
        self.assertIn("Minimise", meta["description"])

    def test_frontend_escapes_attributes_and_sanitizes_markdown(self) -> None:
        common_js = (REPO_ROOT / "website" / "assets" / "common.js").read_text(encoding="utf-8")
        self.assertIn('.replace(/"/g, "&quot;")', common_js)
        self.assertIn(".replace(/'/g, \"&#39;\")", common_js)
        self.assertIn("function sanitizeHtml(html)", common_js)
        self.assertIn("sanitizeHtml(window.marked.parse(protectedMd))", common_js)
        self.assertIn("!safeUrl(attr.value)", common_js)

    def test_instance_status_metrics_and_best_value(self) -> None:
        _root, out, _summary = self.build()
        instances = self.load(out, "data", "problems", "01", "instances.json")["instances"]
        self.assertEqual(len(instances), 1)
        inst = instances[0]
        self.assertEqual(inst["name"], "ms_03_050_001")
        self.assertEqual(inst["status"], "optimal")
        self.assertEqual(inst["bkv"], 0)
        # Header "3 50" → 3 markets, 50 variables; filename → coeff range 50.
        self.assertEqual(inst["metrics"]["markets"], 3)
        self.assertEqual(inst["metrics"]["variables"], 50)
        # The infeasible -999 submission must NOT win the best value.
        self.assertEqual(inst["best_value"], 0)
        self.assertEqual(inst["best_source_label"], "Reference solution")

    def test_solutions_and_instance_submissions_split(self) -> None:
        _root, out, _summary = self.build()
        solutions = self.load(out, "data", "problems", "01", "solutions.json")["entries"]
        self.assertEqual(solutions, [{"instance": "ms_03_050_001", "status": "optimal", "value": 0}])
        inst_subs = self.load(out, "data", "problems", "01", "instance_submissions.json")["entries"]
        self.assertIn("ms_03_050_001", inst_subs)
        self.assertEqual(len(inst_subs["ms_03_050_001"]), 2)

    def test_submission_classification(self) -> None:
        _root, out, _summary = self.build()
        entries = self.load(out, "data", "leaderboard.json")["entries"]
        by_author = {e["author"]: e for e in entries}
        self.assertEqual(by_author["Ada Example"]["category"], "classical")
        self.assertEqual(by_author["Bogus Bot"]["category"], "classical")

    def test_submission_group_category(self) -> None:
        """Each submission package is tagged with its dominant compute paradigm
        (and a per-paradigm breakdown), so the submissions page can label and
        filter by quantum hardware / quantum simulator / classical."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "website" / "assets").mkdir(parents=True)
        (root / "website" / "index.html").write_text("<title>x</title>\n", encoding="utf-8")
        problem = root / "01-marketsplit"
        (problem / "instances").mkdir(parents=True)
        for nm in ("ms_03_050_001", "ms_03_050_002"):
            (problem / "instances" / f"{nm}.dat").write_text("3 50\n1 0 1\n", encoding="utf-8")
        # A QAOA run on real hardware (measured QPU runtime) → quantum_hw.
        _write_summary_csv(problem / "submissions" / "20260101_QAOA_Q" / "ms_03_050_001_summary.csv", [{
            "Problem": "ms_03_050_001", "Submitter": "Q Team", "Date": "2026-01-01",
            "Best Objective Value": "0", "# Feasible Runs": "1", "Algorithm Type": "QAOA",
            "Hardware Specifications": "IBM Heron", "QPU Runtime": "1.5",
        }])
        # A deterministic classical solver → classical.
        _write_summary_csv(problem / "submissions" / "20260102_Gurobi_C" / "ms_03_050_002_summary.csv", [{
            "Problem": "ms_03_050_002", "Submitter": "C Team", "Date": "2026-01-02",
            "Best Objective Value": "0", "# Feasible Runs": "1", "Modeling Approach": "Binary Linear Program",
        }])
        out = root / "_site"
        build_site(out=out, root=root, copy_static=False, built_at="2026-01-01T00:00:00Z")
        groups = {g["id"]: g for g in self.load(out, "data", "problems", "01", "submission_groups.json")["entries"]}
        self.assertEqual(groups["20260101_QAOA_Q"]["category"], "quantum_hw")
        self.assertEqual(groups["20260101_QAOA_Q"]["category_counts"]["quantum_hw"], 1)
        self.assertEqual(groups["20260102_Gurobi_C"]["category"], "classical")

    def test_repo_url_and_ref_are_parametrised(self) -> None:
        _root, out, _summary = self.build(repo_url="https://github.com/octo/REPO", ref="deadbeef")
        instances = self.load(out, "data", "problems", "01", "instances.json")["instances"]
        self.assertEqual(
            instances[0]["raw_url"],
            "https://raw.githubusercontent.com/octo/REPO/deadbeef/01-marketsplit/instances/ms_03_050_001.dat",
        )
        meta = self.load(out, "data", "problems", "01", "meta.json")
        self.assertEqual(meta["github_url"], "https://github.com/octo/REPO/tree/deadbeef/01-marketsplit")

    def test_website_accepts_nested_submission_subfolders(self) -> None:
        """A summary CSV nested in arbitrary subfolders below the package is
        still discovered (the reader globs *_summary.csv recursively), and the
        top-level package remains the submission group."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "website" / "assets").mkdir(parents=True)
        (root / "website" / "index.html").write_text("<title>x</title>\n", encoding="utf-8")
        problem = root / "01-marketsplit"
        (problem / "instances").mkdir(parents=True)
        (problem / "instances" / "ms_03_050_001.dat").write_text("3 50\n1 0 1\n", encoding="utf-8")
        # Two extra folder levels (group_A) between the package and the instance.
        nested = problem / "submissions" / "20260109_Deep" / "group_A" / "ms_03_050_001"
        _write_summary_csv(nested / "ms_03_050_001_summary.csv", [{
            "Problem": "ms_03_050_001", "Submitter": "Deep Diver",
            "Date": "2026-01-09", "Best Objective Value": "0", "# Feasible Runs": "1",
        }])
        out = root / "_site"
        build_site(out=out, root=root, copy_static=False, built_at="2026-01-01T00:00:00Z")

        leaderboard = self.load(out, "data", "leaderboard.json")["entries"]
        self.assertEqual([e["author"] for e in leaderboard], ["Deep Diver"])
        inst_subs = self.load(out, "data", "problems", "01", "instance_submissions.json")["entries"]
        self.assertIn("ms_03_050_001", inst_subs)
        groups = self.load(out, "data", "problems", "01", "submission_groups.json")["entries"]
        self.assertEqual(groups[0]["source_dir"], "20260109_Deep")

    def test_submission_establishes_status(self) -> None:
        """A feasible submission sets the instance status even without a
        reference-solution marker: objective == optimality bound → optimal;
        a feasible value alone → best-known; nothing → open."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "website" / "assets").mkdir(parents=True)
        (root / "website" / "index.html").write_text("<title>x</title>\n", encoding="utf-8")
        problem = root / "01-marketsplit"
        (problem / "instances").mkdir(parents=True)
        for nm in ("ms_03_050_001", "ms_03_050_002", "ms_03_050_003"):
            (problem / "instances" / f"{nm}.dat").write_text("3 50\n1 0 1\n", encoding="utf-8")
        # _001: submission proves optimality (objective meets its bound).
        _write_summary_csv(problem / "submissions" / "20260101_S" / "ms_03_050_001" / "ms_03_050_001_summary.csv", [{
            "Problem": "ms_03_050_001", "Submitter": "A", "Date": "2026-01-01",
            "Best Objective Value": "42", "Optimality Bound": "42", "# Feasible Runs": "1",
        }])
        # _002: feasible value but the bound does not match → not proven.
        _write_summary_csv(problem / "submissions" / "20260101_S" / "ms_03_050_002" / "ms_03_050_002_summary.csv", [{
            "Problem": "ms_03_050_002", "Submitter": "A", "Date": "2026-01-01",
            "Best Objective Value": "42", "Optimality Bound": "40", "# Feasible Runs": "1",
        }])
        # _003: no submission and no reference solution → stays open.
        out = root / "_site"
        build_site(out=out, root=root, copy_static=False, built_at="2026-01-01T00:00:00Z")
        insts = {i["name"]: i for i in self.load(out, "data", "problems", "01", "instances.json")["instances"]}
        self.assertEqual(insts["ms_03_050_001"]["status"], "optimal")
        self.assertTrue(insts["ms_03_050_001"]["best_is_optimal"])
        self.assertEqual(insts["ms_03_050_002"]["status"], "best_known")
        self.assertEqual(insts["ms_03_050_003"]["status"], "open")
        meta = self.load(out, "data", "problems", "01", "meta.json")
        self.assertEqual(meta["solved_count"], 1)
        self.assertEqual(meta["best_known_count"], 1)
        self.assertEqual(meta["open_count"], 1)

    def test_public_api_exposed(self) -> None:
        for name in ("build_site", "build_data", "copy_static_frontend", "config"):
            self.assertTrue(hasattr(site_builder, name))


if __name__ == "__main__":
    unittest.main()
