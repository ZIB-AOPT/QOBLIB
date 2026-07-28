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
"""Tests for check_submission.py — focusing on objective time series validation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "misc" / "ci"))

from check_submission import validate_objective_time_series, InstanceReport  # noqa: E402


def _report(instance: str = "inst") -> InstanceReport:
    return InstanceReport(instance=instance, path=Path("."))


def _write_ts(tmp: Path, instance: str, data: object) -> None:
    """Write a time-series JSON file into a temp directory."""
    (tmp / f"{instance}_objective_time_series.json").write_text(
        json.dumps(data), encoding="utf-8"
    )


class TestObjectiveTimeSeriesMonotonicity(unittest.TestCase):
    """validate_objective_time_series enforces per-run monotonicity."""

    def test_minimize_valid_strictly_decreasing(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _write_ts(tmp, "inst", [[
                {"Time": 0.1, "Incumbent": 10.0},
                {"Time": 0.5, "Incumbent": 5.0},
                {"Time": 1.0, "Incumbent": 1.0},
            ]])
            r = _report()
            validate_objective_time_series("inst", tmp, r, minimize=True)
            self.assertTrue(r.ok)
            self.assertFalse(any("monoton" in m for m in r.messages))

    def test_minimize_valid_equal_incumbent(self):
        # Plateau (equal consecutive values) is allowed — not an improvement,
        # but also not a violation.
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _write_ts(tmp, "inst", [[
                {"Time": 0.1, "Incumbent": 5.0},
                {"Time": 0.5, "Incumbent": 5.0},
                {"Time": 1.0, "Incumbent": 3.0},
            ]])
            r = _report()
            validate_objective_time_series("inst", tmp, r, minimize=True)
            self.assertTrue(r.ok)

    def test_minimize_violation_detected(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _write_ts(tmp, "inst", [[
                {"Time": 0.1, "Incumbent": 5.0},
                {"Time": 0.5, "Incumbent": 8.0},   # goes UP — violation
            ]])
            r = _report()
            validate_objective_time_series("inst", tmp, r, minimize=True)
            self.assertFalse(r.ok)
            errors = " ".join(r.messages)
            self.assertIn("monoton", errors)
            self.assertIn("run 1 entry 2", errors)
            self.assertIn("5.0", errors)
            self.assertIn("8.0", errors)
            self.assertIn("decrease", errors)

    def test_maximize_valid_increasing(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _write_ts(tmp, "inst", [[
                {"Time": 0.1, "Incumbent": 1.0},
                {"Time": 0.5, "Incumbent": 5.0},
                {"Time": 1.0, "Incumbent": 10.0},
            ]])
            r = _report()
            validate_objective_time_series("inst", tmp, r, minimize=False)
            self.assertTrue(r.ok)

    def test_maximize_violation_detected(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _write_ts(tmp, "inst", [[
                {"Time": 0.1, "Incumbent": 10.0},
                {"Time": 0.5, "Incumbent": 7.0},   # goes DOWN — violation
            ]])
            r = _report()
            validate_objective_time_series("inst", tmp, r, minimize=False)
            self.assertFalse(r.ok)
            errors = " ".join(r.messages)
            self.assertIn("monoton", errors)
            self.assertIn("run 1 entry 2", errors)
            self.assertIn("increase", errors)

    def test_multiple_runs_violation_in_second_run(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _write_ts(tmp, "inst", [
                [{"Time": 0.1, "Incumbent": 5.0}, {"Time": 0.5, "Incumbent": 3.0}],  # OK
                [{"Time": 0.1, "Incumbent": 4.0}, {"Time": 0.5, "Incumbent": 6.0}],  # violation
            ])
            r = _report()
            validate_objective_time_series("inst", tmp, r, minimize=True)
            self.assertFalse(r.ok)
            errors = " ".join(r.messages)
            self.assertIn("run 2 entry 2", errors)

    def test_single_entry_run_is_valid(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _write_ts(tmp, "inst", [[{"Time": 0.1, "Incumbent": 42.0}]])
            r = _report()
            validate_objective_time_series("inst", tmp, r, minimize=True)
            self.assertTrue(r.ok)

    def test_no_file_is_informational_only(self):
        with tempfile.TemporaryDirectory() as d:
            r = _report()
            validate_objective_time_series("inst", Path(d), r, minimize=True)
            self.assertTrue(r.ok)
            self.assertTrue(any("not provided" in m for m in r.messages))

    def test_non_numeric_incumbent_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _write_ts(tmp, "inst", [[{"Time": 0.1, "Incumbent": "bad"}]])
            r = _report()
            validate_objective_time_series("inst", tmp, r, minimize=True)
            self.assertFalse(r.ok)
            self.assertTrue(any("numeric" in m for m in r.messages))

    def test_missing_keys_reported(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _write_ts(tmp, "inst", [[{"Time": 0.1}]])  # missing Incumbent
            r = _report()
            validate_objective_time_series("inst", tmp, r, minimize=True)
            self.assertFalse(r.ok)
            self.assertTrue(any("Incumbent" in m for m in r.messages))


if __name__ == "__main__":
    unittest.main()
