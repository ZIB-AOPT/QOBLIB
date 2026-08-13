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
"""Tests for the home-page complexity-landscape plots (``misc/ci/site_builder/landscape.py``).

Covers the divergence-prone helpers (metric-stem canonicalisation, log-axis
ticks/bounds) and an end-to-end ``build_landscape`` over a temp fixture: the
metrics.csv join (including the name≠model-file case), the classical
optimal/best-known/open split, the quantum split, and the inset tooltip trim.
"""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
import xml.dom.minidom as minidom
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "misc" / "ci"))

from site_builder import landscape  # noqa: E402


class TestHelpers(unittest.TestCase):
    def test_metric_stem(self):
        cases = [
            ("ms_1.lp.xz", "ms_1"),          # strip compression + model ext
            ("bhX-01.lp", "bhX-01"),
            ("inst.qs", "inst"),
            ("bqp_foo.qs", "foo"),           # drop bqp_ prefix
            ("uqo_bar.lp", "bar"),           # drop uqo_ prefix
            ("po_x_l0.000001.lp.xz", "po_x_l1e-06"),  # portfolio λ normalisation
        ]
        for name, expected in cases:
            self.assertEqual(landscape._metric_stem(name), expected, name)

    def test_fmt_tick_value(self):
        cases = [(1, "1"), (1000, "1,000"), (10000, "10,000"), (0.1, "0.1"),
                 (0.01, "0.01"), (20, "20"), (500, "500"),
                 (100000, "1e5"), (0.001, "1e-3"), (1e7, "1e7")]
        for v, expected in cases:
            self.assertEqual(landscape._fmt_tick_value(v), expected, f"_fmt_tick_value({v})")

    def test_nice_log_bound(self):
        # A data max of 16 snaps UP to 20 (not the next decade 100); 16 snaps DOWN to 10.
        self.assertEqual(landscape._nice_log_bound(16, +1), 20)
        self.assertEqual(landscape._nice_log_bound(16, -1), 10)
        # Exact nice values stay put.
        self.assertEqual(landscape._nice_log_bound(100, +1), 100)
        self.assertEqual(landscape._nice_log_bound(100, -1), 100)

    def test_scale_snaps_to_nice_tight_bounds(self):
        # x data 10..16 → axis 10..20 (NOT 10..100); labelled ticks 10, 20.
        points = [
            {"num_vars": 10, "density": 0.9},
            {"num_vars": 16, "density": 0.3},
        ]
        sc = landscape._scale(points)
        self.assertAlmostEqual(sc["x_hi"], math.log10(20))
        self.assertEqual(sc["x_major"], [10, 20])

    def test_num_and_esc(self):
        self.assertEqual(landscape._num("1,000"), 1000.0)
        self.assertEqual(landscape._num("1.5"), 1.5)
        self.assertIsNone(landscape._num(""))
        self.assertIsNone(landscape._num("nope"))
        self.assertIsNone(landscape._num("inf"))  # non-finite rejected
        self.assertEqual(landscape._esc('a<b>&"\''), "a&lt;b&gt;&amp;&quot;&#39;")


def _make_problem_dir() -> tempfile.TemporaryDirectory:
    """A temp problem dir with one LP and one QUBO metrics.csv."""
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    lp = root / "models" / "binary_linear" / "lp_files"
    qs = root / "models" / "binary_unconstrained" / "qs_files"
    lp.mkdir(parents=True)
    qs.mkdir(parents=True)
    (lp / "metrics.csv").write_text(
        "file,num_vars,density\n"
        "ms_1.lp,10,0.9\n"
        "bhX-01.lp,2000,0.002\n"   # joined via model stem, not the instance name
        "zero.lp,0,0.5\n",         # non-positive vars -> dropped (log axes)
        encoding="utf-8",
    )
    (qs / "metrics.csv").write_text(
        "file,num_variables,density\n"
        "ms_1.qs,8,1.0\n",
        encoding="utf-8",
    )
    return tmp


def _entries(problem_dir: Path) -> list[dict]:
    return [{
        "problem_id": "01",
        "problem_name": "Test Problem",
        "problem_dir": problem_dir,
        "instances": [
            {"name": "ms_1", "classical_tier": "optimal", "quantum_tier": "optimal",
             "models": [{"name": "ms_1.lp.xz", "kind": "lp"}, {"name": "ms_1.qs", "kind": "qs"}]},
            # Instance name (B1) differs from its model file stem (bhX-01) — the
            # join must follow the model file, like the instances-page scatter.
            # Classical only matched best-known; quantum found a (worse) solution.
            {"name": "B1", "classical_tier": "best_known", "quantum_tier": "found",
             "models": [{"name": "bhX-01.lp.xz", "kind": "lp"}]},
            {"name": "zero", "classical_tier": "optimal", "quantum_tier": "open",
             "models": [{"name": "zero.lp", "kind": "lp"}]},
        ],
    }]


def _svgs(figure: str) -> list[str]:
    import re
    return re.findall(r"<svg.*?</svg>", figure, re.S)


class TestBuildLandscape(unittest.TestCase):
    def setUp(self):
        self._tmp = _make_problem_dir()
        self.addCleanup(self._tmp.cleanup)
        self.data = landscape.build_landscape(_entries(Path(self._tmp.name)))

    def test_shape_and_wellformed(self):
        self.assertEqual(set(self.data), {"mip", "qubo"})
        for key in ("mip", "qubo"):
            fig = self.data[key]
            self.assertTrue(fig)
            # main + classical inset + quantum inset
            self.assertEqual(len(_svgs(fig)), 3, key)
            self.assertIn('viewBox="0 0 720 380"', fig)  # main dims
            self.assertIn('viewBox="0 0 340 220"', fig)  # inset dims
            self.assertIn('<div class="plot-cap">', fig)
            # The injected run of card children must be parseable markup.
            minidom.parseString("<root>" + fig + "</root>")

    def test_join_includes_name_mismatch_and_drops_nonpositive(self):
        main = _svgs(self.data["mip"])[0]
        # ms_1 + B1 join (B1 via its model stem); the zero-vars row is dropped.
        self.assertEqual(main.count("<circle"), 2)
        # QUBO only has the one instance with a qs model.
        self.assertEqual(_svgs(self.data["qubo"])[0].count("<circle"), 1)

    def test_classical_inset_marks_optimal_best_known_open(self):
        classical = _svgs(self.data["mip"])[1]
        self.assertIn("fill:var(--bar-solved-classical)", classical)      # ms_1 optimal
        self.assertIn("fill:var(--bar-best-known-classical)", classical)  # B1 best-known
        # The colour key lists the three retained tiers; "found" was folded into open.
        self.assertIn("best-known", self.data["mip"])
        self.assertIn(">open<", self.data["mip"])
        self.assertNotIn("found", self.data["mip"])

    def test_quantum_inset_folds_found_into_open(self):
        quantum = _svgs(self.data["mip"])[2]
        self.assertEqual(quantum.count("fill:var(--bar-solved-quantum)"), 1)  # ms_1 optimal
        # B1 is only a (worse) feasible "found" result for quantum, so it is no
        # longer a distinct tier — it renders as the grey "open" base.
        self.assertNotIn("var(--bar-found-quantum)", quantum)
        self.assertIn("fill:var(--border-mid)", quantum)

    def test_tier_tooltips_present(self):
        # The colour keys explain each retained tier via a native title tooltip.
        for phrase in ("proven optimal objective value", "best-known objective value", "No solution reaching"):
            self.assertIn(phrase, self.data["mip"])

    def test_legend_lists_problem(self):
        self.assertIn("Test Problem", self.data["mip"])
        self.assertIn("<strong>01</strong>", self.data["mip"])

    def test_tooltips_only_on_main_scatter(self):
        main, classical, quantum = _svgs(self.data["mip"])
        self.assertIn("<title>", main)          # main dots keep tooltips
        self.assertNotIn("<title>", classical)  # insets are trimmed
        self.assertNotIn("<title>", quantum)
        # Exactly one <title> per main dot, none elsewhere.
        self.assertEqual(self.data["mip"].count("<title>"), 2)

    def test_empty_problem_yields_blank_figures(self):
        empty = tempfile.TemporaryDirectory()
        self.addCleanup(empty.cleanup)
        data = landscape.build_landscape([{
            "problem_id": "00", "problem_name": "Empty",
            "problem_dir": Path(empty.name), "instances": [],
        }])
        self.assertEqual(data, {"mip": "", "qubo": ""})


if __name__ == "__main__":
    unittest.main()
