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
"""Tests for the pre-rendered performance charts (``misc/ci/site_builder/charts.py``).

The chart maths is a port of ``website/assets/problem.js``; there is no JS runtime
in CI to diff against, so these tests pin the divergence-prone pieces — the number
formatters (which mirror JS ``toFixed``/``toLocaleString``/``toExponential``) and
the dataset grouping — to hand-computed expectations.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "misc" / "ci"))

from site_builder import charts  # noqa: E402


class TestFormatters(unittest.TestCase):
    def test_num_locale(self):
        cases = [
            (1234.5, 1, "1,234.5"),
            (1000, 0, "1,000"),
            (1234567, 0, "1,234,567"),
            (0.5, 2, "0.5"),
            (12.0, 1, "12"),       # Number(12.0.toFixed(1)) === 12 -> "12"
            (-0.0, 2, "0"),        # no "-0"
            (-12.5, 1, "-12.5"),
        ]
        for v, dp, expected in cases:
            self.assertEqual(charts._num_locale(v, dp), expected, f"_num_locale({v},{dp})")

    def test_js_exponential(self):
        self.assertEqual(charts._js_exponential(100000, 1), "1.0e+5")
        self.assertEqual(charts._js_exponential(0.0001, 1), "1.0e-4")
        self.assertEqual(charts._js_exponential(123456, 1), "1.2e+5")

    def test_fmt_time(self):
        cases = [
            (0, "0"),
            (0.5, "0.5"),
            (5, "5"),
            (12.34, "12.3"),
            (1500, "1,500"),
            (100000, "1.0e+5"),   # >= 1e5 -> exponential
            (0.0001, "1.0e-4"),   # < 1e-3 -> exponential
        ]
        for v, expected in cases:
            self.assertEqual(charts._fmt_time(v), expected, f"_fmt_time({v})")

    def test_fmt_gap(self):
        self.assertEqual(charts._fmt_gap(0.5), "0.5%")
        self.assertEqual(charts._fmt_gap(5), "5%")
        self.assertEqual(charts._fmt_gap(12.34), "12%")
        self.assertEqual(charts._fmt_gap(0), "0%")

    def test_fmt_size(self):
        self.assertEqual(charts._fmt_size(5), "5")
        self.assertEqual(charts._fmt_size(5.5), "5.5")
        self.assertEqual(charts._fmt_size(1500), "1,500")

    def test_jround_half_to_plus_infinity(self):
        self.assertEqual(charts._jround(0.5), 1)
        self.assertEqual(charts._jround(2.5), 3)
        self.assertEqual(charts._jround(-0.5), 0)

    def test_esc(self):
        self.assertEqual(charts._esc('a<b>&"\''), "a&lt;b&gt;&amp;&quot;&#39;")
        self.assertEqual(charts._esc(None), "")


def _synthetic_problem():
    """Minimisation problem, two instances, three feasible submission rows."""
    return {
        "id": "99",
        "minimize": True,
        "columns": [{"key": "nodes", "label": "Nodes", "numeric": True}],
        "instances": [
            {"name": "i1", "best_value": 10, "metrics": {"nodes": 4}},
            {"name": "i2", "best_value": 20, "metrics": {"nodes": 8}},
        ],
        "instance_submissions": {
            "i1": [
                {"value": 10, "runtime_total": "2", "n_feasible": "1", "category": "classical"},
                {"value": 12, "runtime_total": "1", "n_feasible": "1", "category": "quantum_hw"},
            ],
            "i2": [
                {"value": 20, "runtime_total": "5", "n_feasible": "1", "category": "classical"},
            ],
        },
    }


class TestBuildPerfMode(unittest.TestCase):
    def test_paradigm_grouping_and_sorting(self):
        groups = charts._build_perf_mode(_synthetic_problem(), "paradigm")
        by_key = {g["key"]: g for g in groups}
        # Fixed category order, only present categories, full labels + theme colours.
        self.assertEqual([g["key"] for g in groups], ["classical", "quantum_hw"])
        self.assertEqual(by_key["classical"]["name"], "Classical")
        self.assertEqual(by_key["classical"]["color"], "var(--cat-classical)")
        self.assertEqual(by_key["quantum_hw"]["color"], "var(--cat-quantum-hw)")

        # classical reached best-known on both instances (rt 2 and 5, sorted asc).
        self.assertEqual(by_key["classical"]["times"], [2.0, 5.0])
        # quantum_hw never reached best-known (val 12 vs target 10) -> no cactus point.
        self.assertEqual(by_key["quantum_hw"]["times"], [])
        # Optimality gaps: classical exact (0,0); quantum_hw (12-10)/10*100 = 20.
        self.assertEqual(by_key["classical"]["gaps"], [0.0, 0.0])
        self.assertEqual(by_key["quantum_hw"]["gaps"], [20.0])
        # Scaling points carry (size, fastest feasible runtime).
        self.assertEqual(
            sorted((p["size"], p["rt"]) for p in by_key["classical"]["points"]),
            [(4.0, 2.0), (8.0, 5.0)],
        )
        self.assertEqual([(p["size"], p["rt"]) for p in by_key["quantum_hw"]["points"]], [(4.0, 1.0)])

    def test_submission_mode_groups_by_source(self):
        groups = charts._build_perf_mode(_synthetic_problem(), "submission")
        # No _source_dir on the rows -> all collapse to the "Unknown" package.
        self.assertEqual([g["key"] for g in groups], ["Unknown"])
        self.assertEqual(groups[0]["color"], charts.CACTUS_PALETTE[0])


class TestBuildProblemCharts(unittest.TestCase):
    def test_payload_shape_and_flags(self):
        payload = charts.build_problem_charts(_synthetic_problem())
        self.assertIsNotNone(payload)
        self.assertTrue(payload["has_cactus"])
        self.assertTrue(payload["has_profile"])
        self.assertTrue(payload["has_scaling"])
        self.assertEqual(payload["size_label"], "Nodes")
        self.assertEqual(payload["ref_n"], 2)
        self.assertEqual(set(payload["modes"]), {"paradigm", "submission"})

        cactus = payload["modes"]["paradigm"]["cactus"]
        self.assertEqual(set(cactus), {"wide", "narrow"})
        self.assertIn('viewBox="0 0 720 300"', cactus["wide"])
        self.assertIn('viewBox="0 0 430 340"', cactus["narrow"])
        self.assertIn('class="conv-svg"', cactus["wide"])
        self.assertIn("var(--cat-classical)", cactus["wide"])
        # Legend only lists groups with data for THIS chart: classical has 2
        # cactus points; quantum_hw has none, so it is absent from the cactus legend.
        self.assertIn("Classical (2)", cactus["wide"])
        self.assertNotIn("Quantum hardware (", cactus["wide"])
        # Profile legend, by contrast, includes quantum_hw (it has a gap).
        self.assertIn("Quantum hardware (1)", payload["modes"]["paradigm"]["profile"]["wide"])

    def test_empty_problem_returns_none(self):
        empty = {"id": "00", "minimize": True, "columns": [], "instances": [], "instance_submissions": {}}
        self.assertIsNone(charts.build_problem_charts(empty))

    def test_feasibility_problem_has_no_profile(self):
        # All best values 0 -> feasibility problem -> profile chart suppressed,
        # and "reaching best-known" = producing a feasible (here zero-objective) point.
        prob = {
            "id": "98",
            "minimize": True,
            "columns": [{"key": "length", "label": "Length", "numeric": True}],
            "instances": [{"name": "a", "best_value": 0, "metrics": {"length": 3}}],
            "instance_submissions": {
                "a": [{"value": 0, "runtime_total": "4", "n_feasible": "1", "category": "classical"}],
            },
        }
        payload = charts.build_problem_charts(prob)
        self.assertIsNotNone(payload)
        self.assertFalse(payload["has_profile"])
        self.assertTrue(payload["has_cactus"])


if __name__ == "__main__":
    unittest.main()
