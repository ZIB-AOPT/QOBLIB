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
"""Tests for submission affiliation normalisation.

Regression for a submission (Global Data Quantum) whose ``Affiliation`` field
used the footnote convention ``"[1] Org, <postal address>"``. The naive
comma-split shared by the home-page ticker (index.js) and the server pre-render
(overview_pages._affiliation_counts) turned the address into bogus "orgs"
(``Bizkaia``, ``Spain``, ``48001 Bilbo``, …) and never stripped the ``[N]``
marker. normalize_affiliation collapses such fields to their bare org names at
read time so every downstream consumer sees one clean organisation.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "misc" / "ci"))

from site_builder.submissions import normalize_affiliation as N  # noqa: E402


class TestNormalizeAffiliation(unittest.TestCase):
    def test_footnote_with_address_collapses_to_org(self):
        raw = ("[1] Global Data Quantum, Gran Vía de Don Diego López de Haro, 1, "
               "48001 Bilbo, Bizkaia, Spain")
        self.assertEqual(N(raw), "Global Data Quantum")

    def test_multiple_footnotes_keep_each_org(self):
        raw = "[1] Org A, City A, Country A, [2] Org B, City B, Country B"
        self.assertEqual(N(raw), "Org A, Org B")

    def test_footnote_org_deduplicated(self):
        # The same numbered affiliation repeated across authors yields one org.
        raw = "[1] Org A, City A, [1] Org A, City A"
        self.assertEqual(N(raw), "Org A")

    def test_plain_convention_passes_through(self):
        # No [N] marker → the plain "Org1, Org2" convention is left untouched so
        # the existing comma-splitters still see one org per author.
        for raw in (
            "Math.Tec, IBM, AQT, Math.Tec",
            "Qunova Computing, Inc.",
            "Kipu Quantum, Kipu Quantum and UPV/EHU",
            "UCAS (University of Chinese Academy of Sciences), SRIBD (Shenzhen "
            "Research Institute of Big Data)",
        ):
            self.assertEqual(N(raw), raw, raw)

    def test_empty_and_na_unchanged(self):
        self.assertEqual(N(""), "")
        self.assertEqual(N("   "), "")
        self.assertEqual(N("N/A"), "N/A")

    def test_bracketed_range_marker(self):
        # A shared affiliation footnoted as "[1, 2]" is still recognised.
        raw = "[1, 2] Shared Lab, Some Street, Some City"
        self.assertEqual(N(raw), "Shared Lab")


if __name__ == "__main__":
    unittest.main()
