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
"""Tests for submission date normalisation (``site_builder.text.parse_date_str``).

Submissions carry the ``Date`` column in assorted shapes (ISO with/without a
time, compact YYYYMMDD, day-first with a month name, month-name-first with an
ordinal suffix, European DD.MM.YY numeric). All must land on the canonical
``YYYY-MM-DD`` the checker enforces and the frontend prints, mirroring the
JS ``parseDate`` in website/assets/common.js. The cases here are the real
formats observed across the repository's submissions.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "misc" / "ci"))

from site_builder.text import parse_date_str as P  # noqa: E402


class TestParseDateStr(unittest.TestCase):
    def test_iso_passthrough_and_time_stripped(self):
        self.assertEqual(P("2025-01-20"), "2025-01-20")
        self.assertEqual(P("2024-12-23 09:32:08"), "2024-12-23")
        self.assertEqual(P("2026/07/04"), "2026-07-04")

    def test_compact_yyyymmdd(self):
        self.assertEqual(P("20241206"), "2024-12-06")

    def test_day_first_month_name(self):
        self.assertEqual(P("22. Dec. 2024"), "2024-12-22")
        self.assertEqual(P("8. Mar. 2026"), "2026-03-08")
        self.assertEqual(P("15. Jan. 2025"), "2025-01-15")

    def test_month_name_first_with_ordinal(self):
        self.assertEqual(P("Dec 22, 2024"), "2024-12-22")
        self.assertEqual(P("August 5th, 2026"), "2026-08-05")
        self.assertEqual(P("Nov. 17, 2025"), "2025-11-17")

    def test_european_numeric_day_first(self):
        # DD/MM/YYYY and DD.MM.YY — confirmed day-first by the sibling submission
        # dir (15.07.25 lives under 20250715_…).
        self.assertEqual(P("09/03/2025"), "2025-03-09")
        self.assertEqual(P("15.07.25"), "2025-07-15")

    def test_two_digit_year_month_first(self):
        self.assertEqual(P("Jun 2, 25"), "2025-06-02")
        self.assertEqual(P("Jun 27, 25"), "2025-06-27")

    def test_empty_and_unparseable(self):
        self.assertEqual(P(""), "")
        self.assertEqual(P("   "), "")
        # A novel format degrades to the author's stripped text, never an empty cell.
        self.assertEqual(P("  sometime last week  "), "sometime last week")

    def test_rejects_impossible_month_or_day(self):
        # 13 is not a month, 32 not a day — left as the original text.
        self.assertEqual(P("2025-13-01"), "2025-13-01")
        self.assertEqual(P("2025-01-32"), "2025-01-32")

    def test_output_is_zero_padded(self):
        self.assertEqual(P("1. Jan. 2025"), "2025-01-01")
        self.assertEqual(P("9/3/2025"), "2025-03-09")


if __name__ == "__main__":
    unittest.main()
