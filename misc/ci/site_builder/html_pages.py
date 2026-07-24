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
"""Post-build HTML enrichment for SEO, social sharing, and crawlability.

The interactive site renders problem/instance/submission pages client-side from
JSON behind query-param URLs (e.g. ``problem.html?id=07``), which search engines
and social scrapers index poorly. After the data is built, this module:

  * injects a per-page ``<title>``, meta description, Open Graph + Twitter cards,
    and a canonical link into every static page, plus a skip-to-content link;
  * generates a static, crawlable page per problem at ``problem-<slug>.html``
    (kept at the site root so the client's relative ``data/`` and ``assets/``
    fetches resolve exactly as they do for ``problem.html``). Each carries
    problem-specific meta and a server-rendered summary that the client then
    hydrates into the full interactive view;
  * writes ``sitemap.xml``, ``robots.txt`` and a styled ``404.html``.

Absolute-URL tags (canonical, og:url, og:image) are built here from a single
``base_url`` so there is one source of truth for the deployed origin.
"""

from __future__ import annotations

import html as _htmllib
import re
from pathlib import Path

SITE_NAME = "QOBLIB"
# Default social-share image (≈2:1, close to the 1.91:1 OG ideal). Site-relative.
DEFAULT_OG_IMAGE = "assets/images/mip_density_optsolvedIn_plot_aug25.png"
DEFAULT_DESCRIPTION = (
    "A curated benchmark suite of ten challenging optimization problem classes for "
    "fair, reproducible comparison of quantum and classical optimization methods."
)

# Per-page metadata for the hand-authored static pages, keyed by output filename.
# The interactive shells (problem/instance/submission) get a generic entry; their
# real per-item titles are set client-side and, for problems, by the generated
# ``problem-<slug>.html`` pages below.
PAGE_META = {
    "index.html": {
        "title": "QOBLIB — Quantum Optimization Benchmarking Library",
        "description": DEFAULT_DESCRIPTION,
        "canonical": "",  # home canonicalises to the site root
    },
    "problems.html": {
        "title": "Problem Classes — QOBLIB",
        "description": "The ten QOBLIB problem classes — from Market Split and LABS to "
        "Network Design and Topology — with formulations, instances and best-known results.",
    },
    "instances.html": {
        "title": "Instances — QOBLIB",
        "description": "Browse every QOBLIB benchmark instance across all problem classes, "
        "with sizes, best-known objectives and solution status.",
    },
    "leaderboard.html": {
        "title": "Leaderboard — QOBLIB",
        "description": "Best-known results across the QOBLIB benchmark, comparing classical, "
        "quantum-simulator and quantum-hardware submissions.",
    },
    "submissions.html": {
        "title": "Submissions — QOBLIB",
        "description": "All benchmark submissions to QOBLIB, grouped by package, with methods, "
        "hardware and runtimes.",
    },
    "submit.html": {
        "title": "Submit a Solution — QOBLIB",
        "description": "Contribute a result to QOBLIB: build a submission from the canonical "
        "summary CSV template and open a pull request.",
    },
    "instance.html": {
        "title": "Instance — QOBLIB",
        "description": "Detailed view of a single QOBLIB benchmark instance and its submissions.",
    },
    "submission.html": {
        "title": "Submission — QOBLIB",
        "description": "Detailed view of a single QOBLIB submission package.",
    },
    "problem.html": {
        "title": "Problem — QOBLIB",
        "description": DEFAULT_DESCRIPTION,
    },
}


def _esc(value) -> str:
    return _htmllib.escape("" if value is None else str(value), quote=True)


def _clean(text) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _truncate(text, limit=160) -> str:
    text = _clean(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


# --------------------------------------------------------------------------- #
# Head / body fragments
# --------------------------------------------------------------------------- #
def _meta_block(title, description, canonical_url, og_image_url, og_type="website") -> str:
    desc = _truncate(description)
    tags = [
        f'<meta name="description" content="{_esc(desc)}" />',
        f'<link rel="canonical" href="{_esc(canonical_url)}" />',
        f'<meta property="og:type" content="{_esc(og_type)}" />',
        f'<meta property="og:site_name" content="{SITE_NAME}" />',
        f'<meta property="og:title" content="{_esc(title)}" />',
        f'<meta property="og:description" content="{_esc(desc)}" />',
        f'<meta property="og:url" content="{_esc(canonical_url)}" />',
        f'<meta property="og:image" content="{_esc(og_image_url)}" />',
        '<meta name="twitter:card" content="summary_large_image" />',
        f'<meta name="twitter:title" content="{_esc(title)}" />',
        f'<meta name="twitter:description" content="{_esc(desc)}" />',
        f'<meta name="twitter:image" content="{_esc(og_image_url)}" />',
    ]
    return "".join(f"    {t}\n" for t in tags)


_TITLE_RE = re.compile(r"<title>.*?</title>", re.DOTALL)
_BODY_OPEN_RE = re.compile(r"(<body\b[^>]*>)")
_MAIN_OPEN_RE = re.compile(r"(<main\b[^>]*?)(>)")
_VIEWPORT_RE = re.compile(r'(<meta name="viewport"[^>]*>)')
_LOADING_RE = re.compile(r'<div class="loading">Loading problem data</div>')


def _set_title(html_text, title) -> str:
    return _TITLE_RE.sub(lambda _m: f"<title>{_esc(title)}</title>", html_text, count=1)


def _inject_into_head(html_text, block) -> str:
    return html_text.replace("</head>", block + "</head>", 1)


# The deep pages always live exactly two directories down (problem/<id>/), so a
# RELATIVE base resolves to the site root in every context — local preview served
# at /, file://, GitHub Pages under /<repo>/, or a custom-domain root. (An
# absolute base would hard-code the deploy path and break local/other deploys.)
PROBLEM_PAGE_BASE = "../../"


def _inject_base(html_text, base_href) -> str:
    """Add a <base> so deep pretty-URL pages (/problem/<id>/) resolve the site's
    relative asset and data fetches against the deploy root, wherever it lives."""
    tag = f'\n    <base href="{_esc(base_href)}" />'
    return _VIEWPORT_RE.sub(lambda m: m.group(1) + tag, html_text, count=1)


def _add_skip_link(html_text, main_href="#main") -> str:
    # On <base>-using pages a bare "#main" would resolve against the base URL, so
    # deep pages pass an absolute path to their own #main.
    if 'id="main"' not in html_text:
        html_text = _MAIN_OPEN_RE.sub(r'\1 id="main"\2', html_text, count=1)
    if 'class="skip-link"' not in html_text:
        link = f'<a class="skip-link" href="{_esc(main_href)}">Skip to content</a>'
        html_text = _BODY_OPEN_RE.sub(lambda m: m.group(1) + "\n        " + link, html_text, count=1)
    return html_text


def enrich_static_page(html_text, filename, base_url) -> str:
    """Inject title, meta/social tags, canonical and a skip link into a static page."""
    meta = PAGE_META.get(filename, {"title": SITE_NAME, "description": DEFAULT_DESCRIPTION})
    title = meta.get("title", SITE_NAME)
    desc = meta.get("description", DEFAULT_DESCRIPTION)
    # `canonical: ""` means "the site root" (home page); otherwise the file URL.
    rel = meta["canonical"] if "canonical" in meta else filename
    canonical = f"{base_url}/{rel}" if rel else f"{base_url}/"
    og_image = f"{base_url}/{DEFAULT_OG_IMAGE}"
    html_text = _set_title(html_text, title)
    html_text = _inject_into_head(html_text, _meta_block(title, desc, canonical, og_image))
    html_text = _add_skip_link(html_text)
    return html_text


# --------------------------------------------------------------------------- #
# Static per-problem pages
# --------------------------------------------------------------------------- #
def _problem_summary_block(p) -> str:
    """Server-rendered, crawlable summary injected into #prob-detail. The client
    overwrites this with the full interactive render once problem.js runs, so it
    doubles as the no-JS fallback."""
    pid = str(p.get("id", "")).zfill(2)
    name = _esc(p.get("name", ""))
    slug = _esc(p.get("slug", ""))
    short = _esc(p.get("short", ""))
    desc = _esc(_truncate(p.get("why") or p.get("short") or "", 320))
    facts = (
        f'{p.get("instance_count", 0)} instances · '
        f'{p.get("solved_count", 0)} optimally solved · '
        f'{"minimize" if p.get("minimize", True) else "maximize"}'
    )
    badges = "".join(
        f'<span class="badge b-tag">{_esc(t)}</span>' for t in (p.get("tags") or [])
    )
    github = _esc(p.get("github_url", ""))
    return (
        '<div class="dh"><div>'
        f'<div class="d-num">{pid} / {slug}</div>'
        f'<h1 class="d-title">{name}</h1>'
        f'<div class="d-sub">{short}</div>'
        f'<div class="pcard-foot">{badges}</div>'
        "</div></div>"
        f'<p class="d-desc">{desc}</p>'
        f'<p class="d-desc">{_esc(facts)}</p>'
        + (f'<p><a class="btn btn-ghost" href="{github}" target="_blank" rel="noopener">View on GitHub ↗</a></p>' if github else "")
    )


def render_problem_page(template_html, p, base_url) -> str:
    """Build a deep pretty-URL page (``/problem/<id>/``) from the problem.html
    template: a relative <base> so the client's relative fetches resolve at the
    deploy root, per-problem meta, a data-problem-id hook for problem.js, and a
    server-rendered summary."""
    pid = str(p.get("id", ""))
    name = p.get("name", "")
    title = f"{name} — {SITE_NAME}"
    # Prefer the richer "why" motivation sentence over the terse "short" subtitle.
    desc = p.get("why") or p.get("short") or DEFAULT_DESCRIPTION
    canonical = f"{base_url}/problem/{pid}/"
    og_image = f"{base_url}/{DEFAULT_OG_IMAGE}"
    # Relative to the <base> (site root), this points back at the current page.
    main_href = f"problem/{pid}/#main"

    html_text = _inject_base(template_html, PROBLEM_PAGE_BASE)
    html_text = _set_title(html_text, title)
    html_text = _inject_into_head(html_text, _meta_block(title, desc, canonical, og_image, og_type="article"))
    # Tell problem.js which problem to load (no ?id= query on these static URLs).
    html_text = _BODY_OPEN_RE.sub(
        lambda m: m.group(1)[:-1] + f' data-problem-id="{_esc(pid)}">',
        html_text,
        count=1,
    )
    html_text = _add_skip_link(html_text, main_href)
    html_text = _LOADING_RE.sub(lambda _m: _problem_summary_block(p), html_text, count=1)
    return html_text


# --------------------------------------------------------------------------- #
# sitemap.xml / robots.txt / 404.html
# --------------------------------------------------------------------------- #
def build_sitemap(base_url, problem_ids) -> str:
    paths = [
        "",  # home
        "problems.html",
        "instances.html",
        "leaderboard.html",
        "submissions.html",
        "submit.html",
    ]
    paths += [f"problem/{pid}/" for pid in problem_ids]
    locs = "".join(f"  <url><loc>{_esc(base_url + '/' + p)}</loc></url>\n" for p in paths)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{locs}"
        "</urlset>\n"
    )


def robots_txt(base_url) -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {base_url}/sitemap.xml\n"


# Inline theme-detection (same as the site pages) so the 404 honours dark mode.
_THEME_SCRIPT = (
    '<script>(function(){try{var t=localStorage.getItem("qoblib-theme");'
    'if(t!=="dark"&&t!=="light"){t=window.matchMedia&&window.matchMedia('
    '"(prefers-color-scheme: dark)").matches?"dark":"light";}'
    'document.documentElement.setAttribute("data-theme",t);}catch(e){}})();</script>'
)

# Page-local styling for the 404: a clean oversized "404".
_NOT_FOUND_CSS = """
        .e404 { min-height: 72vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
        .e404-num { font-family: var(--sans); font-weight: 700; line-height: 1;
            font-size: clamp(5.5rem, 26vw, 13rem); color: var(--navy); letter-spacing: -0.02em; margin: 0.2rem 0 0.6rem; }
        .e404 h1 { font-size: clamp(1.4rem, 4vw, 2.1rem); color: var(--navy); margin: 0 0 0.7rem; }
        .e404 .hero-desc { margin: 0 auto 1.6rem; max-width: 46ch; }
        .e404 .hero-actions { justify-content: center; }
        .e404-code { font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--faint); margin-top: 2.2rem; }
"""


def not_found_page(base_url) -> str:
    """A self-contained, on-theme 404 served from arbitrary paths (absolute assets)."""
    base = base_url.rstrip("/")
    home = f"{base}/"
    problems = f"{base}/problems.html"
    css = f"{base}/assets/styles.css"
    icon = f"{base}/assets/images/qoblib-favicon.svg"
    fonts = (
        "https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700"
        "&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:ital,wght@0,300;0,400;1,300&display=swap"
    )
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    {_THEME_SCRIPT}
    <title>Page not found — {SITE_NAME}</title>
    <meta name="robots" content="noindex" />
    <link rel="icon" type="image/svg+xml" href="{_esc(icon)}" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="{_esc(fonts)}" rel="stylesheet" />
    <link rel="stylesheet" href="{_esc(css)}" />
    <style>{_NOT_FOUND_CSS}</style>
</head>
<body data-nav="home">
    <main class="page e404" id="main">
        <div class="hero-eyebrow">Error 404 · No feasible solution</div>
        <div class="e404-num" aria-hidden="true">404</div>
        <h1>This page isn’t in the search space</h1>
        <p class="hero-desc">
            We branched, we bounded, and explored every node — but found no feasible
            solution. This page may have moved, been optimized away, or never existed.
        </p>
        <div class="hero-actions">
            <a class="btn btn-navy" href="{_esc(home)}">Back to home</a>
            <a class="btn btn-ghost" href="{_esc(problems)}">Browse problems</a>
        </div>
        <div class="e404-code">QOBLIB · status 404 · infeasible</div>
    </main>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def enrich_site(out_dir, problems, base_url) -> None:
    """Generate per-problem pages, enrich every static page, and emit SEO files."""
    out_dir = Path(out_dir)
    base_url = base_url.rstrip("/")

    # 1. Generate deep per-problem pages from the (raw, copied) template.
    generated_ids: list = []
    template_path = out_dir / "problem.html"
    if template_path.is_file():
        template = template_path.read_text(encoding="utf-8")
        for p in problems:
            pid = p.get("id")
            if not pid:
                continue
            page = render_problem_page(template, p, base_url)
            page_dir = out_dir / "problem" / str(pid)
            page_dir.mkdir(parents=True, exist_ok=True)
            (page_dir / "index.html").write_text(page, encoding="utf-8")
            generated_ids.append(str(pid))

    # 2. Enrich the hand-authored static pages (including the problem.html shell).
    for html_file in sorted(out_dir.glob("*.html")):
        text = html_file.read_text(encoding="utf-8")
        html_file.write_text(enrich_static_page(text, html_file.name, base_url), encoding="utf-8")

    # 3. SEO support files.
    (out_dir / "sitemap.xml").write_text(build_sitemap(base_url, generated_ids), encoding="utf-8")
    (out_dir / "robots.txt").write_text(robots_txt(base_url), encoding="utf-8")
    (out_dir / "404.html").write_text(not_found_page(base_url), encoding="utf-8")
