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
"""Regression tests for the site audit's data-correctness fixes.

1. The per-instance ``vars`` (and the derived variable-range badge) must come
   from an authoritative source — the .dat header for Market Split (01), the LP
   ``metrics.csv`` num_vars elsewhere — never from the old "largest numeric token
   in the filename" heuristic, which reported the coefficient range (01), a
   difficulty label (05), or the trailing index (09) as if it were n.
2. ``10-topology/instances/bounds.csv`` is an auxiliary bounds table, not a
   benchmark instance, and must not be collected as one.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "misc" / "ci"))

from site_builder import config  # noqa: E402
from site_builder.instances import collect_generic_instance_sources  # noqa: E402
from site_builder.problem import build_problem  # noqa: E402
from site_builder.text import (  # noqa: E402
    parse_filename_generic,
    parse_labs_filename,
    parse_ms_filename,
)


class FilenameParsersDropBogusVars(unittest.TestCase):
    """The filename parsers must no longer guess a variable count."""

    def test_generic_parser_emits_no_vars(self):
        # XSH-n20-k4-01: the only bare-digit token is the trailing index.
        self.assertNotIn("vars", parse_filename_generic("XSH-n20-k4-01"))
        # Sports "Addition_000_Medium": 000 is a label, not n.
        self.assertNotIn("vars", parse_filename_generic("Addition_000_Medium"))

    def test_ms_parser_keeps_constraints_not_vars(self):
        parsed = parse_ms_filename("ms_03_050_002")
        # 050 is the coefficient range, not the variable count.
        self.assertNotIn("vars", parsed)
        self.assertEqual(parsed["n_constraints"], 3)
        self.assertEqual(parsed["index"], 2)

    def test_labs_parser_emits_no_vars(self):
        self.assertNotIn("vars", parse_labs_filename("labs_050_003"))


class AuthoritativeVarsFromRepo(unittest.TestCase):
    """End-to-end over the real repository data."""

    @classmethod
    def setUpClass(cls):
        config.configure(REPO_ROOT)

    def _instances(self, pid):
        problem_dir = REPO_ROOT / next(
            p.name for _id, p in config.find_problem_dirs() if _id == pid
        )
        return {i["name"]: i for i in build_problem(pid, problem_dir)["instances"]}

    def test_marketsplit_vars_match_dat_header(self):
        insts = self._instances("01")
        inst = insts["ms_03_050_002"]
        # The badge value must equal the metrics-panel value (both from the .dat
        # header) — this is the contradiction the audit flagged.
        self.assertEqual(inst.get("vars"), 20)
        self.assertEqual(inst["metrics"]["variables"], 20)

    def test_routing_vars_from_lp_metrics(self):
        insts = self._instances("09")
        # All XSH-n20-k4 instances genuinely have 441 model variables, not "1".
        self.assertTrue(insts)
        self.assertTrue(all(i.get("vars") == 441 for i in insts.values()))


class BoundsCsvExcluded(unittest.TestCase):
    def setUp(self):
        config.configure(REPO_ROOT)

    def test_bounds_csv_not_an_instance(self):
        topo_dir = REPO_ROOT / "10-topology"
        sources = collect_generic_instance_sources("10", topo_dir)
        self.assertNotIn("bounds", sources)
        # Sanity: real topology instances are still discovered.
        self.assertTrue(any(name.startswith("topology_") for name in sources))


if __name__ == "__main__":
    unittest.main()
