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
"""Tests for the overview-page pre-render (``site_builder.overview_pages``).

Each renderer is exercised against the REAL page shell in ``website/`` (so the
tests catch drift if a container id or the loading placeholder changes), and the
pure helpers (problem card, number formatting, leaderboard champion) are unit
tested directly.
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "misc" / "ci"))

from site_builder import overview_pages as O  # noqa: E402

WEBSITE = REPO_ROOT / "website"


def _shell(name: str) -> str:
    return (WEBSITE / name).read_text(encoding="utf-8")


PROBLEMS = [
    {
        "id": "01", "slug": "marketsplit", "name": "Market Split",
        "short": "Multi-dimensional subset sum", "why": "Split a market fairly.",
        "type": "Feasibility", "formulation": "ILP", "minimize": True,
        "tags": ["subset-sum"], "vars_min": 50, "vars_max": 500,
        "instance_count": 4, "solved_count": 2, "solved_classical_count": 2,
        "classical_best_known_count": 1, "best_known_count": 1,
        "quantum_solved_count": 1, "quantum_best_known_count": 0,
        "github_url": "https://github.com/ZIB-AOPT/QOBLIB/tree/main/01-marketsplit",
    },
    {
        "id": "07", "slug": "independentset", "name": "Maximum Independent Set",
        "short": "Largest non-adjacent vertex set", "why": "Biggest independent set.",
        "type": "Graph", "formulation": "QUBO", "minimize": False,
        "tags": ["graph"], "vars_min": 45, "vars_max": 900,
        "instance_count": 2, "solved_count": 1,
        "github_url": "https://github.com/ZIB-AOPT/QOBLIB/tree/main/07-independentset",
    },
]

INDEX = {"built_at": "2026-01-01T00:00:00Z", "total_instances": 6, "total_submissions": 9, "problems": PROBLEMS}

INSTANCES_GROUPS = [
    {
        "id": "01", "name": "Market Split",
        "columns": [{"key": "m", "label": "Constraints", "numeric": True}],
        "instances": [
            {"name": "ms_03_050_002", "status": "optimal", "best_value": 0.0,
             "best_is_optimal": True, "best_source_url": "https://ex/sol", "best_source_label": "Reference solution",
             "raw_url": "https://ex/raw", "metrics": {"m": 3}},
            {"name": "ms_03_050_010", "status": "open", "best_value": None,
             "raw_url": "https://ex/raw2", "metrics": {"m": 3}},
        ],
    },
]

# instance_subs[problem_id][instance_name] = [submission rows]
INSTANCE_SUBS = {
    "01": {
        "ms_03_050_002": [
            {"submitter": "Ada", "value": 0.0, "n_feasible": "1", "date": "2026-01-02",
             "runtime_total": "0.1", "category": "classical", "_source_dir": "20260102_Abs2_Ada"},
            {"submitter": "Bogus", "value": -999, "n_feasible": "0", "date": "2026-01-05",
             "category": "classical", "_source_dir": "20260105_Bogus_Bot"},
        ],
    },
}

SUBMISSION_GROUPS = [
    {
        "id": "20260102_Abs2_Ada", "problem_id": "01", "source_dir": "20260102_Abs2_Ada",
        "category": "classical",
        "profile": {"submitter": "Ada", "affiliation": "Zuse Institute", "date": "2026-01-02"},
        "instances": [{"instance": "ms_03_050_002"}],
    },
]

LANDSCAPE = {"mip": '<svg id="mip-scatter"></svg>', "qubo": '<svg id="qubo-scatter"></svg>'}

# A full per-problem payload as build_data assembles it for the deep pages.
PROBLEM_DETAIL = {
    **PROBLEMS[0],
    "description": "Split a set of items across bins so each dimension balances.",
    "formula": "Ax = b, x in {0,1}^n",
    "columns": INSTANCES_GROUPS[0]["columns"],
    "instances": INSTANCES_GROUPS[0]["instances"],
    "submission_groups": SUBMISSION_GROUPS,
    "charts": {
        "size_label": "variables", "has_cactus": True, "has_tts": False,
        "has_profile": False, "has_scaling": False,
        "modes": {"paradigm": {"cactus": {"wide": "<svg id=\"cactus-wide\"></svg>", "narrow": "<svg/>"}}},
    },
}

SITE_DATA = {
    "index": INDEX, "problems": PROBLEMS, "instances_groups": INSTANCES_GROUPS,
    "submission_groups": SUBMISSION_GROUPS, "instance_subs": INSTANCE_SUBS,
    "landscape": LANDSCAPE, "problem_details": [PROBLEM_DETAIL],
}


class TestHelpers(unittest.TestCase):
    def test_fmt_num(self):
        self.assertEqual(O._fmt_num(1234), "1,234")
        self.assertEqual(O._fmt_num(1234.5), "1,234.5")
        self.assertEqual(O._fmt_num(None), "-")
        self.assertEqual(O._fmt_num(""), "-")
        self.assertEqual(O._fmt_num(0), "0")

    def test_fmt_int(self):
        self.assertEqual(O._fmt_int(1976), "1,976")
        self.assertEqual(O._fmt_int(None), "-")

    def test_status_pill(self):
        pill = O._status_pill("optimal")
        self.assertIn("Optimal", pill)
        self.assertIn("status-pill", pill)

    def test_cat_badge(self):
        self.assertIn("Classical", O._cat_badge("classical"))
        self.assertIn("Quantum HW", O._cat_badge("quantum_hw"))

    def test_problem_card_markup(self):
        card = O._problem_card(PROBLEMS[0])
        self.assertIn('class="pcard"', card)
        self.assertIn('href="problem/01/"', card)
        self.assertIn("Market Split", card)
        # Two progress bars (classical + quantum) with fills.
        self.assertIn("solved-classical", card)
        self.assertIn("solved-quantum", card)
        self.assertIn("50–500 vars", card)


class TestRenderProblems(unittest.TestCase):
    def test_cards_and_jump_replace_loading(self):
        out = O._render_problems(_shell("problems.html"), PROBLEMS)
        self.assertIn('class="pcard"', out)
        self.assertIn('class="jump-chip"', out)
        self.assertIn("Maximum Independent Set", out)
        self.assertNotIn("Loading problem data", out)


class TestRenderIndex(unittest.TestCase):
    LANDSCAPE = {"mip": '<svg id="mip-scatter"></svg>', "qubo": '<svg id="qubo-scatter"></svg>'}

    def test_cards_and_stats(self):
        out = O._render_index(_shell("index.html"), PROBLEMS, INDEX, self.LANDSCAPE)
        self.assertIn('class="pcard"', out)
        self.assertNotIn('<div class="loading">Loading problem data</div>', out)
        # Stat numbers pre-filled (not the placeholder "0").
        import re
        self.assertEqual(re.search(r'id="s-inst"[^>]*>([^<]*)<', out).group(1), "6")
        self.assertEqual(re.search(r'id="s-subs"[^>]*>([^<]*)<', out).group(1), "9")
        # solved = 2 + 1
        self.assertEqual(re.search(r'id="s-solved"[^>]*>([^<]*)<', out).group(1), "3")

    def test_loading_val_class_removed(self):
        # The animated "..." pseudo-element must be gone (loading-val stripped).
        out = O._render_index(_shell("index.html"), PROBLEMS, INDEX, self.LANDSCAPE)
        self.assertNotIn("stat-num loading-val", out)

    def test_landscape_svgs_injected(self):
        out = O._render_index(_shell("index.html"), PROBLEMS, INDEX, self.LANDSCAPE)
        self.assertIn('<svg id="mip-scatter">', out)
        self.assertIn('<svg id="qubo-scatter">', out)
        self.assertNotIn("Loading landscape", out)

    def test_landscape_grid_stays_balanced(self):
        # Regression: the loading placeholder is a NESTED <div>, so a naive
        # first-</div> match left a stray close tag that broke the subgrid (the
        # card rendered double-width). The grid must contain exactly its 2 cards
        # and close cleanly.
        out = O._render_index(_shell("index.html"), PROBLEMS, INDEX, self.LANDSCAPE)
        start = out.index('<div class="landscape-grid"')
        depth, end = 0, None
        for m in re.finditer(r"<(/?)div\b[^>]*>", out[start:]):
            depth += -1 if m.group(1) else 1
            if depth == 0:
                end = start + m.end()
                break
        self.assertIsNotNone(end)
        block = out[start:end]
        self.assertEqual(block.count("landscape-card"), 2)
        # Nothing dangling before the next section divider.
        self.assertRegex(out[end:end + 40], r"^\s*</section>")

    def test_affiliations_rendered(self):
        groups = [
            {"problem_id": "01", "id": "g1",
             "profile": {"affiliation": "Zuse Institute"}, "instances": [{"instance": "a"}, {"instance": "b"}]},
            {"problem_id": "07", "id": "g2",
             "profile": {"affiliation": "Qunova Computing, Inc."}, "instances": [{"instance": "c"}]},
        ]
        out = O._render_index(_shell("index.html"), PROBLEMS, INDEX, self.LANDSCAPE, groups)
        self.assertEqual(re.search(r'id="affil-count"[^>]*>([^<]*)<', out).group(1), "2")
        self.assertIn("Zuse Institute", out)
        # Corporate suffix healed back onto the org name (not split into two orgs).
        self.assertIn("Qunova Computing, Inc.", out)
        self.assertIn("2 instances", out)  # Zuse: 2 instances
        self.assertIn("1 instance", out)   # Qunova: 1 instance (singular)
        # Marquee animates without JS: the `running` class + speed var are baked in.
        self.assertRegex(out, r'class="affil-track running"[^>]*--affil-duration')


class TestAffiliationCounts(unittest.TestCase):
    def test_multi_author_org_counted_once_per_package(self):
        # An org repeated across co-authors in one package counts once.
        groups = [{"problem_id": "01", "id": "g",
                   "profile": {"affiliation": "JIJ, JIJ, JIJ"}, "instances": [{"instance": "x"}]}]
        self.assertEqual(O._affiliation_counts(groups), [("JIJ", 1)])

    def test_broken_parenthesis_healed(self):
        groups = [{"problem_id": "01", "id": "g",
                   "profile": {"affiliation": "Uni (Dept A, Dept B)"}, "instances": [{"instance": "x"}]}]
        self.assertEqual(O._affiliation_counts(groups), [("Uni (Dept A, Dept B)", 1)])

    def test_na_and_empty_skipped(self):
        groups = [{"problem_id": "01", "id": "g",
                   "profile": {"affiliation": "N/A"}, "instances": [{"instance": "x"}]}]
        self.assertEqual(O._affiliation_counts(groups), [])


class TestRenderInstances(unittest.TestCase):
    def test_rows_and_filter(self):
        out = O._render_instances(_shell("instances.html"), INSTANCES_GROUPS, PROBLEMS)
        self.assertIn("ms_03_050_002", out)
        self.assertIn("status-pill", out)
        self.assertIn('href="instance.html?problem=01&amp;name=ms_03_050_002"', out)
        # Optimal best value is bold; the metrics column shows the column label.
        self.assertIn("<strong>0</strong>", out)
        self.assertIn("Constraints 3", out)
        self.assertNotIn("Loading instances", out)
        # Problem filter option injected.
        self.assertIn('<option value="01">01 Market Split</option>', out)

    def test_numeric_sort(self):
        out = O._render_instances(_shell("instances.html"), INSTANCES_GROUPS, PROBLEMS)
        # ms_03_050_002 sorts before ms_03_050_010 (numeric-aware).
        self.assertLess(out.index("ms_03_050_002"), out.index("ms_03_050_010"))


class TestRenderSubmissions(unittest.TestCase):
    def test_rows_stats_filter(self):
        out = O._render_submissions(_shell("submissions.html"), SUBMISSION_GROUPS, PROBLEMS)
        self.assertIn("Ada", out)
        self.assertIn("Zuse Institute", out)
        self.assertIn("cat-badge", out)
        self.assertIn('href="submission.html?problem=01&amp;id=20260102_Abs2_Ada"', out)
        self.assertNotIn("Loading submissions", out)
        import re
        self.assertEqual(re.search(r'id="sub-stat-packages"[^>]*>([^<]*)<', out).group(1), "1")
        self.assertIn('<option value="01">01 - Market Split</option>', out)


class TestRenderLeaderboard(unittest.TestCase):
    def test_champion_and_exclusions(self):
        out = O._render_leaderboard(_shell("leaderboard.html"), PROBLEMS, INSTANCES_GROUPS, INSTANCE_SUBS)
        # One record for the instance that has a feasible submission.
        self.assertIn("ms_03_050_002", out)
        self.assertIn("Ada", out)
        # The infeasible "-999" submission must NOT become the champion.
        self.assertNotIn("Bogus", out)
        self.assertNotIn("-999", out)
        # Feasibility problem (best value 0) → champion reaching 0 gets the star.
        self.assertIn("★", out)
        self.assertNotIn("Loading leaderboard", out)
        import re
        self.assertEqual(re.search(r'id="lb-count"[^>]*>([^<]*)<', out).group(1), "1 record")
        # The open instance with no submissions produces no row.
        self.assertNotIn("ms_03_050_010", out)


class TestRenderProblemDetail(unittest.TestCase):
    def setUp(self):
        self.body = O.render_problem_detail(PROBLEM_DETAIL)

    def test_header_and_description(self):
        self.assertIn('<h1 class="d-title">Market Split</h1>', self.body)
        self.assertIn("Split a set of items across bins", self.body)
        self.assertIn("Optimally solved", self.body)

    def test_sections_present(self):
        # Collapsible Submissions + Instances sections with counts.
        self.assertIn("Submissions", self.body)
        self.assertIn("Instances", self.body)
        self.assertIn('id="prob-inst-tbody"', self.body)
        # A real instance row links to the instance page.
        self.assertIn('href="instance.html?problem=01&amp;name=ms_03_050_002"', self.body)
        self.assertIn("ms_03_050_010", self.body)  # both instances listed

    def test_performance_charts_injected(self):
        # The pre-baked cactus SVG (paradigm/wide) is embedded, not left empty.
        self.assertIn('id="cactus-body"', self.body)
        self.assertIn('<svg id="cactus-wide">', self.body)
        # Charts that don't exist for this problem are omitted.
        self.assertNotIn('id="tts-body"', self.body)

    def test_submission_row(self):
        self.assertIn("Ada", self.body)
        self.assertIn('href="submission.html?problem=01&amp;id=20260102_Abs2_Ada"', self.body)

    def test_illustration_laid_out_when_provided(self):
        body = O.render_problem_detail(PROBLEM_DETAIL, figure_svg='<svg class="pfig" id="ms-fig"></svg>')
        self.assertIn('class="d-desc-visual"', body)
        self.assertIn('<svg class="pfig" id="ms-fig">', body)
        self.assertIn("d-desc-columns", body)

    def test_no_illustration_renders_full_width(self):
        # Without a figure the description is a plain full-width .d-desc block.
        self.assertNotIn("d-desc-visual", self.body)
        self.assertIn('<div class="d-desc">', self.body)

    def test_prefers_rendered_markdown_over_plain_description(self):
        # When description_md is present it is rendered (matching the JS), and the
        # plain `description` / `formula` non-markdown branch is NOT used.
        detail = {**PROBLEM_DETAIL,
                  "description_md": "## Overview\n\nThe **real** intro with $x^2$ math.",
                  "description": "Terse fallback summary.",
                  "formula": "Ax=b"}
        body = O.render_problem_detail(detail)
        self.assertIn("<h2>Overview</h2>", body)
        self.assertIn("<strong>real</strong>", body)
        self.assertIn("$x^2$", body)                     # math preserved for KaTeX
        self.assertNotIn("Terse fallback summary.", body)  # plain desc not used
        self.assertNotIn("Ax=b", body)                     # formula only in non-md branch

    def test_markdown_lead_heading_hoisted_above_figure_columns(self):
        detail = {**PROBLEM_DETAIL, "description_md": "## Overview\n\nBody text here."}
        body = O.render_problem_detail(detail, figure_svg='<svg class="pfig"></svg>')
        # The <h2> sits before the columns; body + figure inside them.
        i_h2 = body.index("<h2>Overview</h2>")
        i_cols = body.index("d-desc-columns")
        self.assertLess(i_h2, i_cols)
        self.assertIn("Body text here.", body[i_cols:])


class TestRenderMarkdown(unittest.TestCase):
    def test_headings_bold_italic_code(self):
        html = O._render_markdown("## Title\n\nA **bold** and *thin* word with `code`.")
        self.assertIn("<h2>Title</h2>", html)
        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<em>thin</em>", html)
        self.assertIn("<code>code</code>", html)

    def test_paragraphs_separated_by_blank_lines(self):
        html = O._render_markdown("First para.\n\nSecond para.")
        self.assertEqual(html.count("<p>"), 2)
        self.assertIn("<p>First para.</p>", html)
        self.assertIn("<p>Second para.</p>", html)

    def test_soft_wrapped_lines_join(self):
        html = O._render_markdown("Line one\nline two.")
        self.assertEqual(html.count("<p>"), 1)
        self.assertIn("Line one line two.", html)

    def test_unordered_list(self):
        html = O._render_markdown("- alpha\n- beta")
        self.assertIn("<ul><li>alpha</li><li>beta</li></ul>", html)

    def test_math_preserved_verbatim(self):
        html = O._render_markdown("Given $G=(V,E)$ and $$\\sum_i x_i$$ done.")
        self.assertIn("$G=(V,E)$", html)
        self.assertIn("$$\\sum_i x_i$$", html)

    def test_figure_block_and_img_stripped(self):
        md = 'Intro.\n\n<p align="center">\n  <img src="./x.png" alt="fig">\n</p>\n\n## Next'
        html = O._render_markdown(md)
        self.assertNotIn("<img", html)
        self.assertNotIn("&lt;/p&gt;", html)  # no leaked close tag
        self.assertNotIn("align=", html)
        self.assertIn("<h2>Next</h2>", html)

    def test_link_rendered_and_unsafe_scheme_dropped(self):
        self.assertIn('<a href="https://ex.org"', O._render_markdown("[site](https://ex.org)"))
        # javascript: URL is not linkified — only the text survives.
        out = O._render_markdown("[x](javascript:alert(1))")
        self.assertNotIn("<a ", out)
        self.assertNotIn("javascript:", out)

    def test_html_escaped(self):
        self.assertIn("&lt;script&gt;", O._render_markdown("a <script> tag"))

    def test_empty(self):
        self.assertEqual(O._render_markdown(""), "")


class TestRenderOverviewPagesOrchestration(unittest.TestCase):
    def test_writes_all_pages(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            for name in ("index.html", "problems.html", "instances.html",
                         "submissions.html", "leaderboard.html"):
                (out / name).write_text(_shell(name), encoding="utf-8")

            O.render_overview_pages(out, SITE_DATA)

            self.assertIn('class="pcard"', (out / "index.html").read_text(encoding="utf-8"))
            self.assertIn("ms_03_050_002", (out / "instances.html").read_text(encoding="utf-8"))
            self.assertIn("Ada", (out / "submissions.html").read_text(encoding="utf-8"))
            self.assertIn("Ada", (out / "leaderboard.html").read_text(encoding="utf-8"))

    def test_missing_page_is_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            (out / "index.html").write_text(_shell("index.html"), encoding="utf-8")
            # Only index.html present — must not raise for the others.
            O.render_overview_pages(out, SITE_DATA)
            self.assertFalse((out / "leaderboard.html").exists())


class TestLoadProblemFigures(unittest.TestCase):
    def test_parses_generated_figures_js(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            (out / "assets").mkdir()
            (out / "assets" / "problem_figures.js").write_text(
                '// banner\nwindow.QOBLIB_PROBLEM_FIGURES = '
                '{"marketsplit": "<svg id=\\"a\\"></svg>", "labs": "<svg/>"};\n',
                encoding="utf-8",
            )
            figs = O._load_problem_figures(out)
            self.assertEqual(set(figs), {"marketsplit", "labs"})
            self.assertIn('id="a"', figs["marketsplit"])

    def test_missing_file_returns_empty(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(O._load_problem_figures(Path(d)), {})


if __name__ == "__main__":
    unittest.main()
