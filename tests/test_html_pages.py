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
"""Tests for the HTML enrichment / SEO page generation (``site_builder.html_pages``)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "misc" / "ci"))

from site_builder import html_pages as H  # noqa: E402

BASE = "https://example.org/QOBLIB"
TEMPLATE = (REPO_ROOT / "website" / "problem.html").read_text(encoding="utf-8")

PROBLEM = {
    "id": "07",
    "slug": "independentset",
    "name": "Maximum Independent Set",
    "short": "Largest non-adjacent vertex set",
    "why": "Find the largest set of mutually non-adjacent vertices in a graph.",
    "tags": ["graph", "NP-hard"],
    "instance_count": 42,
    "solved_count": 10,
    "minimize": False,
    "github_url": "https://github.com/ZIB-AOPT/QOBLIB/tree/main/07-independentset",
}


class TestEnrichStaticPage(unittest.TestCase):
    def test_home_page(self):
        src = (
            '<head>\n<meta name="viewport" content="x" />\n<title>QOBLIB - Home</title>\n</head>\n'
            '<body data-nav="home">\n<main class="page">x</main>\n</body>'
        )
        out = H.enrich_static_page(src, "index.html", BASE)
        self.assertIn("<title>QOBLIB — Quantum Optimization Benchmarking Library</title>", out)
        # Home canonicalises to the site root, not /index.html.
        self.assertIn('<link rel="canonical" href="https://example.org/QOBLIB/" />', out)
        self.assertIn('<meta name="description"', out)
        self.assertIn('<meta property="og:title"', out)
        self.assertIn('<meta name="twitter:card" content="summary_large_image" />', out)
        self.assertIn('<main class="page" id="main">', out)
        self.assertIn('<a class="skip-link" href="#main">', out)

    def test_subpage_canonical_is_file_url(self):
        src = '<head><title>x</title></head><body><main class="page"></main></body>'
        out = H.enrich_static_page(src, "problems.html", BASE)
        self.assertIn('<link rel="canonical" href="https://example.org/QOBLIB/problems.html" />', out)

    def test_no_anchor_points_degrade_gracefully(self):
        # Minimal HTML without </head>/<main>/<body> must not raise.
        out = H.enrich_static_page("<title>x</title>", "index.html", BASE)
        self.assertIn("<title>", out)


class TestRenderProblemPage(unittest.TestCase):
    def setUp(self):
        self.page = H.render_problem_page(TEMPLATE, PROBLEM, BASE)

    def test_base_and_meta(self):
        # Relative base: deploy-agnostic (works at /, /QOBLIB/, file://, ...).
        self.assertIn('<base href="../../" />', self.page)
        self.assertIn("<title>Maximum Independent Set — QOBLIB</title>", self.page)
        # Canonical stays absolute (the production URL) for SEO.
        self.assertIn('<link rel="canonical" href="https://example.org/QOBLIB/problem/07/" />', self.page)
        self.assertIn('<meta property="og:type" content="article" />', self.page)
        # Meta description uses the richer "why" sentence.
        self.assertIn("mutually non-adjacent vertices", self.page)

    def test_hydration_hook_and_ssr(self):
        self.assertIn('data-problem-id="07"', self.page)
        self.assertIn('<h1 class="d-title">Maximum Independent Set</h1>', self.page)
        self.assertIn("42 instances · 10 optimally solved · maximize", self.page)
        self.assertIn("View on GitHub", self.page)
        # The loading placeholder is replaced by the server-rendered summary.
        self.assertNotIn("Loading problem data", self.page)

    def test_skip_link_resolves_to_self_under_base(self):
        # Relative to <base> (site root) this is the page's own #main anchor.
        self.assertIn('<a class="skip-link" href="problem/07/#main">', self.page)

    def test_cdn_scripts_inherited_from_pinned_template(self):
        self.assertIn("marked@12.0.2/marked.min.js", self.page)
        self.assertIn('integrity="sha384-', self.page)


class TestSeoFiles(unittest.TestCase):
    def test_sitemap(self):
        sm = H.build_sitemap(BASE, ["01", "02"])
        self.assertIn("<loc>https://example.org/QOBLIB/</loc>", sm)
        self.assertIn("<loc>https://example.org/QOBLIB/problems.html</loc>", sm)
        self.assertIn("<loc>https://example.org/QOBLIB/problem/01/</loc>", sm)
        self.assertIn("<loc>https://example.org/QOBLIB/problem/02/</loc>", sm)

    def test_robots(self):
        self.assertIn("Sitemap: https://example.org/QOBLIB/sitemap.xml", H.robots_txt(BASE))

    def test_404(self):
        nf = H.not_found_page(BASE)
        self.assertIn('content="noindex"', nf)
        self.assertIn("https://example.org/QOBLIB/assets/styles.css", nf)
        self.assertIn('href="https://example.org/QOBLIB/"', nf)


class TestEnrichSite(unittest.TestCase):
    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            (out / "problem.html").write_text(TEMPLATE, encoding="utf-8")
            (out / "index.html").write_text(
                '<head>\n<meta name="viewport" content="x" />\n<title>QOBLIB</title>\n</head>'
                '<body><main class="page"></main></body>',
                encoding="utf-8",
            )
            H.enrich_site(out, [PROBLEM], BASE)

            page = (out / "problem" / "07" / "index.html")
            self.assertTrue(page.is_file())
            text = page.read_text(encoding="utf-8")
            self.assertIn('<base href="../../" />', text)
            self.assertIn('data-problem-id="07"', text)

            for name in ("sitemap.xml", "robots.txt", "404.html"):
                self.assertTrue((out / name).is_file(), name)
            self.assertIn("id=\"main\"", (out / "index.html").read_text(encoding="utf-8"))

    def test_missing_template_skips_problem_pages(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            (out / "index.html").write_text("<title>x</title>", encoding="utf-8")
            H.enrich_site(out, [PROBLEM], BASE)  # no problem.html present
            self.assertFalse((out / "problem" / "07").exists())
            self.assertTrue((out / "sitemap.xml").is_file())


if __name__ == "__main__":
    unittest.main()
