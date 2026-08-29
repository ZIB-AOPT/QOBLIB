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

import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "misc" / "ci"))

from check_submission import (  # noqa: E402
    REQUIRED_COLUMNS,
    InstanceReport,
    validate_csv,
    validate_objective_time_series,
)


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


class TestObjectiveTimeSeriesNullIncumbent(unittest.TestCase):
    """A null 'Incumbent' means "no feasible solution yet" and is accepted
    before the run's first incumbent (e.g. Gurobi root-relaxation log rows)."""

    def test_leading_nulls_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _write_ts(tmp, "inst", [[
                {"Time": 0.0, "Incumbent": None},
                {"Time": 0.0, "Incumbent": None},
                {"Time": 0.1, "Incumbent": 16.0},
                {"Time": 1.0, "Incumbent": 14.0},
            ]])
            r = _report()
            validate_objective_time_series("inst", tmp, r, minimize=True)
            self.assertTrue(r.ok, " ".join(r.messages))

    def test_all_null_run_accepted(self):
        # A run that never found a feasible solution is valid, just empty of
        # incumbents.
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _write_ts(tmp, "inst", [[
                {"Time": 0.0, "Incumbent": None},
                {"Time": 5.0, "Incumbent": None},
            ]])
            r = _report()
            validate_objective_time_series("inst", tmp, r, minimize=True)
            self.assertTrue(r.ok, " ".join(r.messages))

    def test_null_after_incumbent_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _write_ts(tmp, "inst", [[
                {"Time": 0.1, "Incumbent": 16.0},
                {"Time": 0.5, "Incumbent": None},   # lost the incumbent — impossible
            ]])
            r = _report()
            validate_objective_time_series("inst", tmp, r, minimize=True)
            self.assertFalse(r.ok)
            errors = " ".join(r.messages)
            self.assertIn("run 1 entry 2", errors)
            self.assertIn("null", errors)

    def test_nulls_do_not_mask_monotonicity_violation(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _write_ts(tmp, "inst", [[
                {"Time": 0.0, "Incumbent": None},
                {"Time": 0.1, "Incumbent": 5.0},
                {"Time": 0.5, "Incumbent": 8.0},   # goes UP — violation
            ]])
            r = _report()
            validate_objective_time_series("inst", tmp, r, minimize=True)
            self.assertFalse(r.ok)
            self.assertIn("monoton", " ".join(r.messages))

    def test_non_numeric_string_still_rejected(self):
        # A null is "no incumbent yet"; any other non-numeric value is still an error.
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _write_ts(tmp, "inst", [[{"Time": 0.1, "Incumbent": "n/a"}]])
            r = _report()
            validate_objective_time_series("inst", tmp, r, minimize=True)
            self.assertFalse(r.ok)
            self.assertIn("must be numeric", " ".join(r.messages))


class TestObjectiveTimeSeriesStructure(unittest.TestCase):
    """Structural checks that are independent of the monotonicity policy."""

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


class TestValidateCsvFieldChecks(unittest.TestCase):
    """validate_csv enforces Date format, Algorithm Type, and Paradigm enums."""

    def _write_csv(self, tmp: Path, instance: str, overrides: dict) -> Path:
        """Write a minimal valid summary CSV with optional field overrides."""
        row = {col: "" for col in REQUIRED_COLUMNS}
        row.update({
            "Problem": instance,
            "Best Objective Value": "42",
            "Date": "2024-12-22",
            "Algorithm Type": "Deterministic",
            "Paradigm": "Classical",
        })
        row.update(overrides)
        csv_path = tmp / f"{instance}_summary.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=REQUIRED_COLUMNS)
            writer.writeheader()
            writer.writerow(row)
        return csv_path

    def _validate(self, tmp: Path, instance: str, overrides: dict) -> InstanceReport:
        import argparse
        csv_path = self._write_csv(tmp, instance, overrides)
        report = InstanceReport(instance=instance, path=tmp)
        args = argparse.Namespace(strict_problem_match=False)
        validate_csv(instance, csv_path, args.strict_problem_match, report)
        return report

    # --- Date ---

    def test_date_valid_iso(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._validate(Path(d), "inst", {"Date": "2024-12-22"})
            self.assertTrue(r.ok)

    def test_date_datetime_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._validate(Path(d), "inst", {"Date": "2024-12-22 09:32:08"})
            self.assertFalse(r.ok)
            self.assertTrue(any("Date" in m for m in r.messages))

    def test_date_two_digit_year_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._validate(Path(d), "inst", {"Date": "15.07.25"})
            self.assertFalse(r.ok)
            self.assertTrue(any("Date" in m for m in r.messages))

    def test_date_slash_format_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._validate(Path(d), "inst", {"Date": "09/03/2025"})
            self.assertFalse(r.ok)
            self.assertTrue(any("Date" in m for m in r.messages))

    def test_date_empty_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._validate(Path(d), "inst", {"Date": ""})
            self.assertTrue(r.ok)

    # --- Algorithm Type ---

    def test_algorithm_type_deterministic_valid(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._validate(Path(d), "inst", {"Algorithm Type": "Deterministic"})
            self.assertTrue(r.ok)

    def test_algorithm_type_stochastic_valid(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._validate(Path(d), "inst", {"Algorithm Type": "Stochastic"})
            self.assertTrue(r.ok)

    def test_algorithm_type_lowercase_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._validate(Path(d), "inst", {"Algorithm Type": "stochastic"})
            self.assertFalse(r.ok)
            self.assertTrue(any("Algorithm Type" in m for m in r.messages))

    def test_algorithm_type_empty_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._validate(Path(d), "inst", {"Algorithm Type": ""})
            self.assertTrue(r.ok)

    # --- Paradigm ---

    def test_paradigm_classical_valid(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._validate(Path(d), "inst", {"Paradigm": "Classical"})
            self.assertTrue(r.ok)

    def test_paradigm_quantum_simulator_valid(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._validate(Path(d), "inst", {"Paradigm": "Quantum Simulator"})
            self.assertTrue(r.ok)

    def test_paradigm_quantum_hardware_valid(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._validate(Path(d), "inst", {"Paradigm": "Quantum Hardware"})
            self.assertTrue(r.ok)

    def test_paradigm_freeform_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._validate(Path(d), "inst", {"Paradigm": "Quantum Hardware / Hybrid"})
            self.assertFalse(r.ok)
            self.assertTrue(any("Paradigm" in m for m in r.messages))

    def test_paradigm_mixed_case_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._validate(Path(d), "inst", {"Paradigm": "Quantum and classical Hardware"})
            self.assertFalse(r.ok)
            self.assertTrue(any("Paradigm" in m for m in r.messages))

    def test_paradigm_empty_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._validate(Path(d), "inst", {"Paradigm": ""})
            self.assertTrue(r.ok)


if __name__ == "__main__":
    unittest.main()
