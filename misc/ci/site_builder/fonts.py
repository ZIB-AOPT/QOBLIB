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
"""Build-time font self-hosting.

The site's three custom families (Syne, IBM Plex Mono, Source Serif 4) were
loaded from Google Fonts at runtime, which costs two extra cross-origin
handshakes (fonts.googleapis.com for the CSS, fonts.gstatic.com for the files)
plus a render-blocking external stylesheet before any text can paint.

At build time we instead fetch the pruned Google CSS, download the ``woff2``
files into ``<out>/assets/fonts/``, rewrite the ``src`` URLs to those local
copies, and emit ``<out>/assets/fonts.css``. ``html_pages`` then swaps the three
Google ``<link>`` tags for that single local stylesheet. All three families are
SIL Open Font License, which permits self-hosting.

Everything is best-effort: if the network is unavailable (e.g. offline local
dev) ``build_fonts`` returns ``None`` and the caller keeps the original Google
Fonts tags, so the site still works — it just isn't self-hosted that build.

Only the ``latin`` and ``latin-ext`` unicode-range subsets are kept (English
text plus accented author/affiliation names); the browser already fetches only
the subset a page needs, so dropping cyrillic/greek/vietnamese just trims the
build download, not runtime behaviour.

The weight-300 Source Serif variants (roman + italic) are pruned from the
request entirely — the stylesheet never uses weight 300.
"""

from __future__ import annotations

import re
import urllib.parse
import urllib.request
from pathlib import Path

# Pruned request: every weight/style the CSS actually uses, and nothing else.
#   Syne            400/500/600/700  (body + headings)
#   IBM Plex Mono   400/500          (mono/tabular text)
#   Source Serif 4  roman 400 + italic 400  (hero copy, subtitles, captions)
# `display=swap` keeps text visible in a fallback until the webfont arrives.
FONT_CSS_URL = (
    "https://fonts.googleapis.com/css2"
    "?family=Syne:wght@400;500;600;700"
    "&family=IBM+Plex+Mono:wght@400;500"
    "&family=Source+Serif+4:ital,wght@0,400;1,400"
    "&display=swap"
)

# Subsets to self-host (see module docstring).
_KEEP_SUBSETS = ("latin", "latin-ext")

# NB: we deliberately do NOT <link rel=preload> the fonts. `assets/fonts.css` is
# already a render-blocking stylesheet in <head>, so the browser discovers and
# fetches the needed faces very early anyway; a preload buys almost nothing on
# top of that and makes Firefox emit "preloaded resource not used within a few
# seconds" warnings whenever font *application* lags the download (e.g. the
# problem pages do heavy post-load work — big chart SVGs, KaTeX, hydration).

# Only download font binaries from Google's font CDN. The CSS itself comes from
# a hardcoded fonts.googleapis.com URL, so a `src:` pointing elsewhere would mean
# Google's response was tampered with — reject it as defense-in-depth against a
# compromised/MITM'd response rather than blindly fetching an arbitrary host.
_ALLOWED_FONT_HOSTS = ("fonts.gstatic.com",)

# A Google Fonts CSS block: an optional `/* subset */` comment then an @font-face.
_BLOCK_RE = re.compile(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})", re.DOTALL)
_FIELD_RE = {
    "family": re.compile(r"font-family:\s*'([^']+)'"),
    "style": re.compile(r"font-style:\s*(\w+)"),
    "weight": re.compile(r"font-weight:\s*(\d+)"),
}
_WOFF2_RE = re.compile(r"url\((https://[^)]+\.woff2)\)")


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


def _http_get(url: str) -> bytes:
    # A modern-browser UA so Google returns woff2 (not older ttf) with the
    # unicode-range subsetting we rely on.
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 (fixed Google host)
        return resp.read()


def localize_css(css_text: str, download_fn, *, keep_subsets=_KEEP_SUBSETS):
    """Rewrite Google Fonts CSS to self-hosted files. Pure except for
    ``download_fn(url) -> bytes`` (injected so tests can avoid the network).

    Returns ``(localized_css, files)`` where:
      * ``localized_css`` — @font-face rules with ``src`` pointing at
        ``fonts/<name>.woff2`` (relative to the emitted assets/fonts.css);
      * ``files`` — ``{local_name: bytes}`` to write under ``assets/fonts/``.
    Raises if a kept block has no downloadable woff2 (caller treats as failure).
    """
    out_blocks: list[str] = []
    files: dict[str, bytes] = {}
    # Download cache (same URL fetched once) and content dedup (identical bytes
    # stored once). Variable fonts — Syne here — are the reason: Google's css2
    # returns the SAME variable woff2 for every requested weight (400/500/600/700),
    # so all four faces share one file. Without dedup we'd write it four times
    # under different weight-named filenames, defeating the browser's own URL
    # dedup and downloading ~148 KB of identical bytes. See module docstring.
    by_url: dict[str, bytes] = {}
    name_by_content: dict[bytes, str] = {}

    for subset, block in _BLOCK_RE.findall(css_text):
        if subset not in keep_subsets:
            continue
        family = _FIELD_RE["family"].search(block)
        style = _FIELD_RE["style"].search(block)
        weight = _FIELD_RE["weight"].search(block)
        url_m = _WOFF2_RE.search(block)
        if not (family and url_m):
            continue
        # Only fetch from the allowed font CDN (defense-in-depth; see above).
        woff2_url = url_m.group(1)
        host = urllib.parse.urlsplit(woff2_url).hostname or ""
        if host not in _ALLOWED_FONT_HOSTS:
            raise ValueError(f"refusing to download font from unexpected host: {host}")

        fam = family.group(1)
        sty = style.group(1) if style else "normal"
        wgt = weight.group(1) if weight else "400"
        name = f"{_slug(fam)}-{wgt}-{sty}-{_slug(subset)}.woff2"

        data = by_url.get(woff2_url)
        if data is None:
            data = download_fn(woff2_url)
            by_url[woff2_url] = data

        # Reuse an already-stored file if these exact bytes were seen before; the
        # @font-face rule keeps its own font-weight, so a variable font still maps
        # each weight to the shared file correctly.
        target = name_by_content.get(data)
        if target is None:
            target = name
            files[name] = data
            name_by_content[data] = name

        # Rewrite the src to the local copy (relative to assets/fonts.css).
        out_blocks.append(_WOFF2_RE.sub(f"url(fonts/{target})", block, count=1))

    if not files:
        raise ValueError("no matching font faces found in CSS")

    header = "/* Self-hosted at build time from Google Fonts (see site_builder/fonts.py). */\n"
    return header + "\n".join(out_blocks) + "\n", files


def build_fonts(out_dir, *, url: str = FONT_CSS_URL, css_fetcher=_http_get, downloader=_http_get):
    """Fetch, download and self-host the site fonts under ``out_dir``.

    Returns ``{"css_path": "assets/fonts.css"}`` on success, or ``None`` if
    anything fails (no network, HTTP error, unexpected CSS) — in which case the
    caller keeps the original Google Fonts tags."""
    out_dir = Path(out_dir)
    try:
        css_text = css_fetcher(url).decode("utf-8")
        localized, files = localize_css(css_text, downloader)
    except Exception as exc:  # broad: any failure → graceful fallback
        print(f"  Fonts: not self-hosting this build ({exc}); keeping Google Fonts.")
        return None

    fonts_dir = out_dir / "assets" / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (fonts_dir / name).write_bytes(data)
    (out_dir / "assets" / "fonts.css").write_text(localized, encoding="utf-8")
    print(f"  Fonts: self-hosted {len(files)} woff2 files → assets/fonts/.")
    return {"css_path": "assets/fonts.css"}
