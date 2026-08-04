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
"""Tests for build-time font self-hosting (``site_builder.fonts``) and the HTML
tag swap. The network is faked throughout so these run offline/deterministically."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "misc" / "ci"))

from site_builder import fonts as F  # noqa: E402
from site_builder import html_pages as H  # noqa: E402

# A synthetic slice of Google Fonts css2 output: two subsets for one face, plus
# a face we self-host and one subset we drop (cyrillic).
FAKE_CSS = """
/* cyrillic */
@font-face {
  font-family: 'Syne';
  font-style: normal;
  font-weight: 400;
  src: url(https://fonts.gstatic.com/s/syne/cyr-400.woff2) format('woff2');
  unicode-range: U+0400-045F;
}
/* latin */
@font-face {
  font-family: 'Syne';
  font-style: normal;
  font-weight: 400;
  src: url(https://fonts.gstatic.com/s/syne/lat-400.woff2) format('woff2');
  unicode-range: U+0000-00FF;
}
/* latin */
@font-face {
  font-family: 'Syne';
  font-style: normal;
  font-weight: 700;
  src: url(https://fonts.gstatic.com/s/syne/lat-700.woff2) format('woff2');
  unicode-range: U+0000-00FF;
}
/* latin */
@font-face {
  font-family: 'Source Serif 4';
  font-style: italic;
  font-weight: 400;
  src: url(https://fonts.gstatic.com/s/ss4/lat-i400.woff2) format('woff2');
  unicode-range: U+0000-00FF;
}
"""


def fake_download(url: str) -> bytes:
    return b"WOFF2:" + url.encode()


class TestLocalizeCss(unittest.TestCase):
    def setUp(self):
        self.css, self.files = F.localize_css(FAKE_CSS, fake_download)

    def test_drops_unwanted_subset(self):
        # The cyrillic Syne 400 face is not downloaded or referenced.
        self.assertNotIn("cyr-400", self.css)
        self.assertFalse(any("cyr" in n for n in self.files))

    def test_rewrites_src_to_local(self):
        # No gstatic URLs remain; src points at fonts/<name>.woff2.
        self.assertNotIn("fonts.gstatic.com", self.css)
        self.assertIn("url(fonts/syne-400-normal-latin.woff2)", self.css)
        self.assertIn("syne-400-normal-latin.woff2", self.files)
        self.assertIn("source-serif-4-400-italic-latin.woff2", self.files)

    def test_downloaded_bytes_captured(self):
        self.assertEqual(self.files["syne-400-normal-latin.woff2"], fake_download("https://fonts.gstatic.com/s/syne/lat-400.woff2"))

    def test_empty_css_raises(self):
        with self.assertRaises(ValueError):
            F.localize_css("/* greek */\n", fake_download)

    def test_dedupes_variable_font_shared_bytes(self):
        # A variable font: Google returns the SAME woff2 for several weights.
        # We must store the bytes once and point every face at that one file,
        # while each @font-face keeps its own font-weight.
        var_css = (
            "/* latin */\n@font-face { font-family: 'Syne'; font-style: normal; "
            "font-weight: 400; src: url(https://fonts.gstatic.com/s/syne/v.woff2) "
            "format('woff2'); unicode-range: U+0000-00FF; }\n"
            "/* latin */\n@font-face { font-family: 'Syne'; font-style: normal; "
            "font-weight: 700; src: url(https://fonts.gstatic.com/s/syne/v.woff2) "
            "format('woff2'); unicode-range: U+0000-00FF; }\n"
        )
        calls = []

        def dl(url):
            calls.append(url)
            return b"SHARED-VARIABLE-BYTES"

        css, files = F.localize_css(var_css, dl)
        # Downloaded once, stored once.
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(files), 1)
        # Both faces reference the single shared file...
        self.assertEqual(css.count("url(fonts/syne-400-normal-latin.woff2)"), 2)
        # ...and both weights are still declared.
        self.assertIn("font-weight: 400", css)
        self.assertIn("font-weight: 700", css)
        # No second (700-named) file is written.
        self.assertNotIn("syne-700-normal-latin.woff2", files)

    def test_rejects_non_gstatic_host(self):
        # A src pointing at an unexpected host (tampered response) is refused, and
        # the download function is never invoked for it.
        evil = (
            "/* latin */\n@font-face { font-family: 'Syne'; font-style: normal; "
            "font-weight: 400; src: url(https://evil.example/x.woff2) format('woff2'); "
            "unicode-range: U+0000-00FF; }\n"
        )
        called = []
        with self.assertRaises(ValueError):
            F.localize_css(evil, lambda u: called.append(u) or b"x")
        self.assertEqual(called, [])


class TestBuildFonts(unittest.TestCase):
    def test_success_writes_files_and_returns_info(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            info = F.build_fonts(out, css_fetcher=lambda _u: FAKE_CSS.encode(), downloader=fake_download)
            self.assertIsNotNone(info)
            self.assertEqual(info["css_path"], "assets/fonts.css")
            self.assertTrue((out / "assets" / "fonts.css").is_file())
            self.assertTrue((out / "assets" / "fonts" / "syne-400-normal-latin.woff2").is_file())

    def test_network_failure_returns_none(self):
        def boom(_url):
            raise OSError("no network")
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            self.assertIsNone(F.build_fonts(out, css_fetcher=boom))
            # Nothing written on failure.
            self.assertFalse((out / "assets" / "fonts.css").exists())


# The three Google Fonts tags exactly as they appear in the source shells.
GOOGLE_TAGS = (
    '    <link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    '    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:ital,wght@0,300;0,400;1,300&display=swap" rel="stylesheet" />'
)
FONT_INFO = {"css_path": "assets/fonts.css"}


class TestSwapFontTags(unittest.TestCase):
    def test_swaps_to_local_stylesheet(self):
        out = H._swap_font_tags(GOOGLE_TAGS, FONT_INFO)
        self.assertNotIn("fonts.googleapis.com", out)
        self.assertNotIn("fonts.gstatic.com", out)
        self.assertIn('<link rel="stylesheet" href="assets/fonts.css" />', out)
        # No preload tags are emitted (they caused "preloaded but unused" warnings).
        self.assertNotIn('rel="preload"', out)

    def test_no_font_info_keeps_google_tags(self):
        out = H._swap_font_tags(GOOGLE_TAGS, None)
        self.assertEqual(out, GOOGLE_TAGS)

    def test_enrich_static_page_swaps_when_selfhosted(self):
        src = (
            '<head>\n<meta name="viewport" content="x" />\n<title>x</title>\n'
            + GOOGLE_TAGS + '\n</head><body><main class="page"></main></body>'
        )
        out = H.enrich_static_page(src, "index.html", "https://ex.org/QOBLIB", font_info=FONT_INFO)
        self.assertIn("assets/fonts.css", out)
        self.assertNotIn("fonts.googleapis.com", out)

    def test_enrich_static_page_keeps_google_on_fallback(self):
        src = (
            '<head>\n<meta name="viewport" content="x" />\n<title>x</title>\n'
            + GOOGLE_TAGS + '\n</head><body><main class="page"></main></body>'
        )
        out = H.enrich_static_page(src, "index.html", "https://ex.org/QOBLIB", font_info=None)
        self.assertIn("fonts.googleapis.com", out)


if __name__ == "__main__":
    unittest.main()
