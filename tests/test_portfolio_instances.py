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
"""Regression tests for portfolio (06) instance discovery.

Guards the fix for a bug where the large a200/a400 instances were invisible on
the site: portfolio built its instance list from model files + submissions only,
and no .lp/.qs models were ever generated for those sizes (the model-generation
script globbed `po_a0*`), so 16 of 32 physical instances — every a200 and a400 —
were dropped. Discovery now expands the on-disk data directories directly.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "misc" / "ci"))

from site_builder import config  # noqa: E402
from site_builder.instances import (  # noqa: E402
    _PORTFOLIO_BUDGET_BY_ASSETS,
    _PORTFOLIO_LAMBDAS,
    _load_portfolio_manifest,
    collapse_portfolio_instances,
    collect_portfolio_instance_sources,
    portfolio_canonical_base,
)

PORTFOLIO_DIR = REPO_ROOT / "06-portfolio"


@unittest.skipUnless(PORTFOLIO_DIR.is_dir(), "portfolio data not present")
class TestPortfolioInstanceSources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config.configure(REPO_ROOT, "https://github.com/ZIB-AOPT/QOBLIB", "main")
        cls.sources = collect_portfolio_instance_sources(PORTFOLIO_DIR)

    def test_every_physical_dir_is_expanded(self):
        # Each po_a<AAA>_t<TT>_<seed> directory becomes exactly len(grid) logical
        # instances — nothing on disk is silently skipped.
        dirs = [
            p for p in (PORTFOLIO_DIR / "instances").iterdir()
            if p.is_dir() and re.match(r"po_a\d{3}_t\d{2}_(s\d{2}|orig)$", p.name)
        ]
        self.assertEqual(len(self.sources), len(dirs) * len(_PORTFOLIO_LAMBDAS))

    def test_large_instances_present(self):
        # The regression: a200 and a400 must appear (they have data dirs but no
        # model files). Each of the 16 large dirs × 8 lambdas = 128 entries.
        large = [n for n in self.sources if n.startswith(("a200", "a400"))]
        self.assertEqual(len(large), 16 * len(_PORTFOLIO_LAMBDAS))

    def test_small_instances_present(self):
        # The a003/a004/a005 data dirs (uploaded later, with no model files) must
        # also appear. Each of these 12 dirs × 8 lambdas = 96 entries.
        small = [n for n in self.sources if n.startswith(("a003", "a004", "a005"))]
        self.assertEqual(len(small), 12 * len(_PORTFOLIO_LAMBDAS))

    def test_budget_matches_asset_size(self):
        # Budget is derived from the asset count per the generation script's rule
        # (and the instance authors' values for the small sizes), not guessed.
        self.assertIn("a200_t10_orig_b050_l0.01", self.sources)
        self.assertIn("a400_t15_s02_b100_l0.01", self.sources)
        self.assertIn("a003_t02_orig_b003_l0.01", self.sources)
        self.assertIn("a004_t04_orig_b004_l0.01", self.sources)
        self.assertIn("a005_t04_orig_b004_l0.01", self.sources)
        self.assertEqual(
            _PORTFOLIO_BUDGET_BY_ASSETS,
            {3: 3, 4: 4, 5: 4, 10: 4, 50: 20, 200: 50, 400: 100},
        )

    def test_entries_carry_bundle_metadata(self):
        # Every synthesized source points at its data directory with a real size,
        # so the instance renders with a working download link.
        entry = self.sources["a200_t10_orig_b050_l0.01"]
        self.assertEqual(entry["file"], "po_a200_t10_orig")
        self.assertEqual(entry["format"], "bundle")
        self.assertGreater(entry["size_bytes"], 0)
        self.assertIn("po_a200_t10_orig", entry["raw_url"])

    def test_lambda_normalization_matches_model_keys(self):
        # Small lambdas are normalized to the same stems the model files use
        # (e.g. l0.000001 -> l1e-06), so a source and its model merge onto one
        # instance rather than producing a duplicate.
        self.assertIn("a010_t10_orig_b004_l1e-06", self.sources)
        self.assertNotIn("a010_t10_orig_b004_l0.000001", self.sources)


@unittest.skipUnless(PORTFOLIO_DIR.is_dir(), "portfolio data not present")
class TestPortfolioManifest(unittest.TestCase):
    def test_manifest_matches_constants(self):
        # The on-disk manifest is the source of truth and must agree with the
        # fallback constants (kept in sync so a missing file changes nothing).
        budget, grid = _load_portfolio_manifest(PORTFOLIO_DIR)
        self.assertEqual(budget, _PORTFOLIO_BUDGET_BY_ASSETS)
        self.assertEqual(grid, _PORTFOLIO_LAMBDAS)

    def test_fallback_when_manifest_absent(self):
        # A directory with no manifest.json falls back to the constants rather
        # than raising, so the build never breaks on a missing/parked file.
        budget, grid = _load_portfolio_manifest(REPO_ROOT / "does-not-exist")
        self.assertEqual(budget, _PORTFOLIO_BUDGET_BY_ASSETS)
        self.assertEqual(grid, _PORTFOLIO_LAMBDAS)


class TestPortfolioCanonicalBase(unittest.TestCase):
    def test_strips_prefix_and_lambda_keeps_budget(self):
        self.assertEqual(
            portfolio_canonical_base("a010_t10_orig_b004_l1e-06", _PORTFOLIO_BUDGET_BY_ASSETS),
            "a010_t10_orig_b004",
        )

    def test_injects_budget_for_budgetless_submission_name(self):
        # A budget-less submission name (Arvak's po_a010_t10_orig) must fold into
        # the same base as the real a010_t10_orig_b004 sweep.
        self.assertEqual(
            portfolio_canonical_base("po_a010_t10_orig", _PORTFOLIO_BUDGET_BY_ASSETS),
            "a010_t10_orig_b004",
        )


class TestCollapsePortfolioInstances(unittest.TestCase):
    def _per_lambda(self, base, lambdas, **extra):
        out = []
        for lam in lambdas:
            out.append({
                "name": f"{base}_l{lam}",
                "status": extra.get("status", "best_known"),
                "metrics": {"assets": 10, "periods": 10, "budget": 4, "risk_lambda": lam},
                **{k: v for k, v in extra.items() if k != "status"},
            })
        return out

    def test_groups_by_base_with_one_child_per_lambda(self):
        insts = self._per_lambda("a010_t10_orig_b004", ["0.0", "1e-06", "0.01"])
        bases = collapse_portfolio_instances(insts, dict(_PORTFOLIO_BUDGET_BY_ASSETS))
        self.assertEqual(len(bases), 1)
        b = bases[0]
        self.assertEqual(b["name"], "a010_t10_orig_b004")
        self.assertEqual(b["lambda_count"], 3)
        self.assertEqual(len(b["lambdas"]), 3)

    def test_children_sorted_ascending_by_lambda(self):
        insts = self._per_lambda("a010_t10_orig_b004", ["0.01", "0.0", "1e-06"])
        b = collapse_portfolio_instances(insts, dict(_PORTFOLIO_BUDGET_BY_ASSETS))[0]
        self.assertEqual([c["risk_lambda_num"] for c in b["lambdas"]], [0.0, 1e-06, 0.01])

    def test_display_lambda_is_uniform_scientific(self):
        # Mixed on-disk spellings render uniformly: 0, then single-mantissa
        # scientific with a 2-digit exponent — never a bare decimal.
        insts = self._per_lambda("a010_t10_orig_b004", ["0.0", "1e-06", "0.0001", "0.01"])
        b = collapse_portfolio_instances(insts, dict(_PORTFOLIO_BUDGET_BY_ASSETS))[0]
        self.assertEqual([c["risk_lambda"] for c in b["lambdas"]], ["0", "1e-06", "1e-04", "1e-02"])
        # Internal per-λ names (the JSON lookup keys) are left untouched.
        self.assertEqual(b["lambdas"][2]["name"], "a010_t10_orig_b004_l0.0001")

    def test_base_metrics_drop_risk_lambda(self):
        insts = self._per_lambda("a010_t10_orig_b004", ["0.0", "0.01"])
        b = collapse_portfolio_instances(insts, dict(_PORTFOLIO_BUDGET_BY_ASSETS))[0]
        self.assertNotIn("risk_lambda", b.get("metrics", {}))
        self.assertEqual(b["metrics"]["budget"], 4)

    def test_child_name_is_per_lambda_lookup_key(self):
        # Each child keeps the per-λ name (the instance_submissions/time_series key).
        insts = self._per_lambda("a010_t10_orig_b004", ["1e-06"])
        b = collapse_portfolio_instances(insts, dict(_PORTFOLIO_BUDGET_BY_ASSETS))[0]
        self.assertEqual(b["lambdas"][0]["name"], "a010_t10_orig_b004_l1e-06")

    def test_budgetless_submission_folds_in_as_na_child(self):
        # A po_-prefixed, budget-less, λ-less submission joins the real base as an
        # "n/a" child that doesn't count toward the λ sweep size.
        insts = self._per_lambda("a010_t10_orig_b004", ["0.0", "0.01"])
        insts.append({"name": "po_a010_t10_orig", "status": "best_known",
                      "metrics": {"assets": 10, "periods": 10}})
        bases = collapse_portfolio_instances(insts, dict(_PORTFOLIO_BUDGET_BY_ASSETS))
        self.assertEqual(len(bases), 1)
        b = bases[0]
        self.assertEqual(b["lambda_count"], 2)               # only real λ counted
        self.assertEqual(len(b["lambdas"]), 3)               # n/a child still present
        self.assertEqual(b["lambdas"][-1]["risk_lambda"], "n/a")

    def test_aggregate_status_partition(self):
        allsolved = collapse_portfolio_instances(
            self._per_lambda("a010_t10_orig_b004", ["0.0", "0.01"], status="optimal"),
            dict(_PORTFOLIO_BUDGET_BY_ASSETS))[0]
        self.assertEqual(allsolved["status"], "optimal")
        allopen = collapse_portfolio_instances(
            self._per_lambda("a010_t10_orig_b004", ["0.0", "0.01"], status="open"),
            dict(_PORTFOLIO_BUDGET_BY_ASSETS))[0]
        self.assertEqual(allopen["status"], "open")
        mixed_insts = self._per_lambda("a010_t10_orig_b004", ["0.0"], status="optimal")
        mixed_insts += self._per_lambda("a010_t10_orig_b004", ["0.01"], status="open")
        mixed = collapse_portfolio_instances(mixed_insts, dict(_PORTFOLIO_BUDGET_BY_ASSETS))[0]
        self.assertEqual(mixed["status"], "best_known")


if __name__ == "__main__":
    unittest.main()
