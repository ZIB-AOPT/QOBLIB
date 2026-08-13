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
"""Server-render the "overview" pages' content into the static HTML.

Each overview page (home, problems, instances, submissions, leaderboard) ships
as a shell whose main container holds a ``<div class="loading">…</div>`` (or a
``<tbody>`` with a loading row) that the per-page JS fills client-side from
``data/*.json``. Without JavaScript those pages show only a spinner.

This module pre-renders the same semantic content — problem cards, instance and
submission tables, the leaderboard — into the container the JS targets, so the
page is usable without JS and the pre-JS paint matches the hydrated paint. The
client scripts then overwrite the same containers on load, exactly as
``html_pages.render_problem_page`` already does for problem detail pages
("hydration by replacement"). Markup here mirrors the JS render functions in
``website/assets/*.js`` — keep the two in sync.

Only the semantic content is pre-rendered; the heavy, already-data-backed SVG
figures (home-page landscape, MIP instance-map scatter) and the affiliations
ticker keep their client-only loading state.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .charts import (
    _best_value,
    _cnum,
    _esc,
    _is_attributable,
    _is_feasibility_problem,
    _is_feasible,
    _submission_method,
)
from .classify import classify_submission

# Paradigm badge labels/short forms — mirror SUBMISSION_CATEGORIES in common.js.
_CATS = {
    "quantum_hw": {"label": "Quantum hardware", "short": "Quantum HW", "color": "var(--cat-quantum-hw)"},
    "quantum_sim": {"label": "Quantum simulator", "short": "Quantum sim", "color": "var(--cat-quantum-sim)"},
    "classical": {"label": "Classical", "short": "Classical", "color": "var(--cat-classical)"},
}

# Status pill config — mirror statusPill() in common.js (label + non-color symbol).
_PILLS = {
    "optimal": ("var(--pill-ok-bg)", "var(--pill-ok-fg)", "Optimal", "✓"),
    "solved": ("var(--pill-ok-bg)", "var(--pill-ok-fg)", "Solved", "✓"),
    "best_known": ("var(--pill-best-bg)", "var(--pill-best-fg)", "Best known", "~"),
    "submitted": ("var(--pill-sub-bg)", "var(--pill-sub-fg)", "Submitted", "·"),
    "open": ("var(--pill-open-bg)", "var(--pill-open-fg)", "Open", "?"),
}

_QUANTUM_CATS = {"quantum_hw", "quantum_sim"}


def _pad(pid) -> str:
    return str(pid).zfill(2)


_FIGURES_RE = re.compile(r"window\.QOBLIB_PROBLEM_FIGURES\s*=\s*(\{.*\})\s*;", re.DOTALL)


def _load_problem_figures(out_dir: Path) -> dict:
    """Parse the per-problem illustration SVGs from the copied
    ``assets/problem_figures.js`` (``window.QOBLIB_PROBLEM_FIGURES = {…};``),
    keyed by problem slug. Returns {} if the file is absent or unparseable — the
    detail page then simply renders the description full-width, as the JS does."""
    path = out_dir / "assets" / "problem_figures.js"
    if not path.is_file():
        return {}
    m = _FIGURES_RE.search(path.read_text(encoding="utf-8"))
    if not m:
        return {}
    try:
        figures = json.loads(m.group(1))
    except (ValueError, TypeError):
        return {}
    return figures if isinstance(figures, dict) else {}


# --------------------------------------------------------------------------- #
# Number formatting — ports of common.js fmtNum / fmtInt (Intl.NumberFormat,
# en-US grouping). fmtNum caps at 4 fraction digits; fmtInt rounds to integer.
# --------------------------------------------------------------------------- #
def _fmt_num(n) -> str:
    """Port of ``fmtNum`` — locale grouping, up to 4 fraction digits, or '-'."""
    if n is None or n == "" or n == "-":
        return "-"
    v = _cnum(n)
    if v is None:
        return "-"
    s = f"{v:.4f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    neg = s.startswith("-")
    if neg:
        s = s[1:]
    intp, _, frac = s.partition(".")
    grouped = f"{int(intp):,}" if intp else "0"
    out = grouped + ("." + frac if frac else "")
    return ("-" + out) if (neg and out != "0") else out


def _fmt_int(n) -> str:
    """Port of ``fmtInt`` — Math.round then locale grouping, or '-'."""
    v = _cnum(n)
    if v is None:
        return "-"
    import math
    return f"{math.floor(v + 0.5):,}"


def _fmt_maybe_num(v) -> str:
    """Port of ``fmtMaybeNum`` — numbers grouped; other text passed through escaped."""
    if v is None or v == "":
        return "-"
    n = _cnum(v)
    return _fmt_num(n) if n is not None else _esc(str(v))


def _fmt_text(v) -> str:
    return "-" if v is None or v == "" else _esc(v)


def _status_pill(status) -> str:
    bg, fg, label, sym = _PILLS.get(status, ("var(--pill-open-bg)", "var(--pill-open-fg)", str(status or "").replace("_", " "), "·"))
    sym_html = f'<span aria-hidden="true" class="status-pill-sym">{sym}</span> ' if sym else ""
    return f'<span class="status-pill" style="background:{bg};color:{fg}">{sym_html}{_esc(label)}</span>'


def _cat_badge(cat) -> str:
    c = _CATS.get(cat, _CATS["classical"])
    return (
        f'<span class="cat-badge" title="{_esc(c["label"])}">'
        f'<span class="cat-dot" style="background:{c["color"]}"></span>{_esc(c["short"])}</span>'
    )


def _cat_of(sub) -> str:
    return sub.get("category") or classify_submission(sub)


# --------------------------------------------------------------------------- #
# Placeholder replacement — same regex style as html_pages.py.
# --------------------------------------------------------------------------- #

# Tags whose content is never reflowed. Inline SVG (and <script>/<style>) must
# keep their exact bytes: whitespace between SVG elements can change rendering,
# and the pre-baked chart/landscape SVGs are ~380 KB single lines we must not
# touch. The pretty-printer treats each of these as one opaque atom.
_OPAQUE_TAGS = ("svg", "script", "style")
_OPAQUE_RE = re.compile(r"<(svg|script|style)\b.*?</\1>", re.DOTALL | re.IGNORECASE)
# Void elements never get a close tag, so they must not increase indent depth.
_VOID_TAGS = {"br", "hr", "img", "input", "meta", "link", "source", "col", "area", "base", "wbr", "embed", "track"}
_TOKEN_RE = re.compile(r"<[^>]+>|[^<]+")


def _pretty_fragment(fragment: str, base_indent: str, unit: str = "    ") -> str:
    """Re-indent an HTML fragment to one tag/text node per line, nested under
    ``base_indent``. Elements in ``_OPAQUE_TAGS`` (SVG etc.) are kept verbatim as
    a single line. Best-effort structural pretty-print — not a validating parser,
    but the fragments here are well-formed builder output."""
    # Stash opaque runs behind sentinels so their bytes are preserved exactly.
    stash: list[str] = []

    def stash_opaque(m):
        stash.append(m.group(0))
        return f"\x00{len(stash) - 1}\x00"

    protected = _OPAQUE_RE.sub(stash_opaque, fragment)

    tokens = _TOKEN_RE.findall(protected)
    lines: list[str] = []
    depth = 0
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.startswith("<"):
            name_m = re.match(r"</?\s*([a-zA-Z0-9]+)", tok)
            name = (name_m.group(1).lower() if name_m else "")
            is_close = tok.startswith("</")
            is_self = tok.rstrip().endswith("/>") or name in _VOID_TAGS
            if is_close:
                depth = max(0, depth - 1)
                lines.append(base_indent + unit * depth + tok)
            else:
                # Keep a leaf element with a single short text child on one line:
                # <open>text</close> — reads far better than exploding to 3 lines.
                nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
                nxt2 = tokens[i + 2] if i + 2 < len(tokens) else ""
                if (not is_self and not nxt.startswith("<") and nxt2 == f"</{name}>"
                        and "\x00" not in nxt and len(nxt.strip()) <= 60):
                    lines.append(base_indent + unit * depth + tok + nxt.strip() + nxt2)
                    i += 3
                    continue
                lines.append(base_indent + unit * depth + tok)
                if not is_self:
                    depth += 1
        else:
            text = tok.strip()
            if text:
                lines.append(base_indent + unit * depth + text)
        i += 1

    out = "\n".join(lines)
    # Restore opaque runs verbatim.
    out = re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], out)
    return out


def _replace_container(html_text: str, container_id: str, inner_html: str, pretty: bool = True) -> str:
    """Replace the inner HTML of the element with ``id=container_id``.

    Finds the opening tag with that id and swaps everything up to its *matching*
    close tag, depth-counting nested tags of the same name. This matters because
    the loading placeholders are nested (e.g. ``<div id="pgrid"><div
    class="loading">…</div></div>``) — matching the first ``</div>`` would leave a
    stray unbalanced close tag.
    """
    m = re.search(rf'(<(\w+)[^>]*\bid="{re.escape(container_id)}"[^>]*>)', html_text)
    if not m:
        return html_text
    tag = m.group(2)
    open_end = m.end(1)
    # Walk nested open/close tags of the same name to find the matching close.
    depth = 1
    pos = open_end
    tag_re = re.compile(rf"<(/?){re.escape(tag)}\b[^>]*>", re.IGNORECASE)
    for tm in tag_re.finditer(html_text, open_end):
        depth += -1 if tm.group(1) else 1
        if depth == 0:
            pos = tm.start()
            break
    else:
        return html_text  # unbalanced — leave untouched rather than corrupt

    if pretty and inner_html.strip():
        # Indent the injected block one level under the container's own indent so
        # the generated markup reads cleanly instead of as one long line.
        line_start = html_text.rfind("\n", 0, m.start()) + 1
        container_indent = html_text[line_start:m.start()]
        if container_indent.strip() == "":  # only when the tag sits on its own line
            body = _pretty_fragment(inner_html, container_indent + "    ")
            inner_html = "\n" + body + "\n" + container_indent
    return html_text[:open_end] + inner_html + html_text[pos:]


def _set_element_text(html_text: str, element_id: str, text: str) -> str:
    """Replace the text content of a simple ``<tag id=...>OLD</tag>`` element."""
    return _replace_container(html_text, element_id, _esc(text), pretty=False)


def _problem_options(problems, include_dash=False) -> list:
    """`<option>` strings for a problem-class filter select. ``include_dash`` uses
    the "01 - Name" label form (instances/leaderboard/submissions) vs plain."""
    sep = " - " if include_dash else " "
    return [
        f'<option value="{_esc(p["id"])}">{_esc(_pad(p["id"]))}{sep}{_esc(p["name"])}</option>'
        for p in problems
    ]


# --------------------------------------------------------------------------- #
# Problem card — port of common.js problemCard(p). Shared by home + problems.
# --------------------------------------------------------------------------- #
def _problem_card(p) -> str:
    total = p.get("instance_count") or 0

    def pct(n):
        return (100 * (n or 0) / total) if total else 0

    solved_classical = pct(p.get("solved_classical_count", p.get("solved_count", 0)) or 0)
    best_known_classical = pct(p.get("classical_best_known_count", p.get("best_known_count", 0)) or 0)
    open_classical = max(0, 100 - solved_classical - best_known_classical)

    solved_quantum = pct(p.get("quantum_solved_count", 0) or 0)
    best_known_quantum = pct(p.get("quantum_best_known_count", 0) or 0)
    open_quantum = max(0, 100 - solved_quantum - best_known_quantum)

    why = f'<p class="pcard-why">{_esc(p["why"])}</p>' if p.get("why") else ""
    vars_badge = (
        f'<span class="badge b-vars">{_fmt_int(p.get("vars_min"))}–{_fmt_int(p.get("vars_max"))} vars</span>'
        if p.get("vars_min") is not None
        else ""
    )

    return f"""
        <a class="pcard" href="problem/{_esc(p['id'])}/">
            <div class="pcard-num">{_esc(_pad(p['id']))}</div>
            <div class="pcard-name">{_esc(p.get('name', ''))}</div>
            <div class="pcard-sub">{_esc(p.get('short', ''))}</div>
            {why}
            <div class="pcard-bars">
                <div class="pcard-bar-row">
                    <span class="pcard-bar-label">Classical</span>
                    <div class="pcard-bar">
                        <div class="pcard-bar-fill solved-classical" style="width:{solved_classical}%"></div>
                        <div class="pcard-bar-fill best-known-classical" style="width:{best_known_classical}%"></div>
                        <div class="pcard-bar-fill open-classical" style="width:{open_classical}%"></div>
                    </div>
                </div>
                <div class="pcard-bar-row">
                    <span class="pcard-bar-label">Quantum</span>
                    <div class="pcard-bar">
                        <div class="pcard-bar-fill solved-quantum" style="width:{solved_quantum}%"></div>
                        <div class="pcard-bar-fill best-known-quantum" style="width:{best_known_quantum}%"></div>
                        <div class="pcard-bar-fill open-quantum" style="width:{open_quantum}%"></div>
                    </div>
                </div>
            </div>
            <div class="pcard-foot">
                <span class="badge b-type">{_esc(p.get('type', ''))}</span>
                {vars_badge}
                <span class="badge b-form">{_esc(p.get('formulation', ''))}</span>
                <span class="badge b-tag">{_fmt_int(p.get('instance_count'))} inst.</span>
            </div>
        </a>"""


# --------------------------------------------------------------------------- #
# Per-page renderers
# --------------------------------------------------------------------------- #
def _render_problems(html_text: str, problems) -> str:
    jump = "".join(
        f"""
                <a class="jump-chip" href="problem/{_esc(p['id'])}/">
                    <span class="jump-num">{_esc(_pad(p['id']))}</span>
                    <span class="jump-name">{_esc(p.get('name', ''))}</span>
                </a>"""
        for p in problems
    )
    cards = "".join(_problem_card(p) for p in problems)
    html_text = _replace_container(html_text, "prob-jump", jump)
    html_text = _replace_container(html_text, "pgrid", cards)
    return html_text


def _fill_stat(html_text: str, element_id: str, text: str) -> str:
    """Pre-fill a stat number and drop the ``loading-val`` class so its animated
    "..." pseudo-element (``.stat-num.loading-val::after``) no longer shows."""
    html_text = _set_element_text(html_text, element_id, text)

    # Strip loading-val from the class of the element carrying this id. The class
    # attribute may appear before or after the id on the tag, so operate on the
    # whole opening tag rather than assume an order.
    def drop_loading_val(tag_m):
        tag = tag_m.group(0)
        return re.sub(
            r'(class=")([^"]*)"',
            lambda cm: cm.group(1) + " ".join(w for w in cm.group(2).split() if w != "loading-val") + '"',
            tag,
            count=1,
        )

    return re.sub(rf'<[^>]*\bid="{re.escape(element_id)}"[^>]*>', drop_loading_val, html_text, count=1)


# Corporate suffixes that get severed from an org name by a naive comma split
# and must be re-joined (mirror CORP_SUFFIX in index.js renderAffiliations).
_CORP_SUFFIX_RE = re.compile(
    r"^(?:inc|incorporated|ltd|limited|l\.?l\.?c|l\.?l\.?p|co|corp|corporation|company|"
    r"gmbh|ag|kg|s\.?a|s\.?à\.?r\.?l|sarl|b\.?v|n\.?v|plc|pty|pte|srl|s\.?r\.?l|s\.?p\.?a|"
    r"oy|ab|as)\.?$",
    re.IGNORECASE,
)


def _affiliation_counts(submission_groups) -> list:
    """Instance count per affiliation, mirroring renderAffiliations in index.js:
    split the comma-joined affiliation field, heal broken parentheses and severed
    corporate suffixes, count each distinct org once per package. Returns a list
    of (name, count) sorted alphabetically (case-insensitive)."""
    counts: dict[str, int] = {}
    for group in submission_groups:
        raw = ((group.get("profile") or {}).get("affiliation") or "").strip()
        if not raw or raw == "N/A":
            continue
        n_inst = len(group.get("instances") or [])
        parts = [s.strip() for s in raw.split(",") if s.strip()]
        healed: list[str] = []
        carry = ""
        for p in parts:
            combined = f"{carry}, {p}" if carry else p
            opens = combined.count("(")
            closes = combined.count(")")
            if opens > closes:
                carry = combined  # unmatched "(" — keep accumulating
            elif _CORP_SUFFIX_RE.match(combined) and healed:
                healed[-1] += f", {combined}"  # suffix belongs to the previous org
                carry = ""
            else:
                healed.append(combined)
                carry = ""
        if carry:
            healed.append(carry)
        # Each distinct org counted once per package (a package's affiliation
        # string repeats an org per co-author).
        for org in {a for a in healed if a and a != "N/A"}:
            counts[org] = counts.get(org, 0) + n_inst
    return sorted(counts.items(), key=lambda kv: kv[0].lower())


def _affil_chip(name, n, dup=False) -> str:
    cls = "affil-chip affil-chip-dup" if dup else "affil-chip"
    plural = "" if n == 1 else "s"
    return (
        f'<span class="{cls}"><span class="affil-chip-name">{_esc(name)}</span>'
        f'<span class="affil-chip-stat">{n} instance{plural}</span></span>'
    )


def _render_affiliations(html_text: str, submission_groups) -> str:
    orgs = _affiliation_counts(submission_groups)
    if not orgs:
        return html_text  # JS removes the section; leaving the shell's empty state is fine

    # Split across two rows (even indices → A, odd → B), matching index.js.
    rows = {"affil-track-a": [o for i, o in enumerate(orgs) if i % 2 == 0],
            "affil-track-b": [o for i, o in enumerate(orgs) if i % 2 == 1]}

    html_text = _set_element_text(html_text, "affil-count", str(len(orgs)))
    # Screen-reader-only static list mirroring the aria-hidden ticker (finding #7):
    # pre-render it so no-JS assistive-tech users still get the org names.
    sr_items = "".join(
        f'<li>{_esc(name)} — {n} instance{"" if n == 1 else "s"}</li>' for name, n in orgs
    )
    html_text = _replace_container(html_text, "affil-list", sr_items)
    for tid, row in rows.items():
        # Two copies of the set for the seamless CSS loop (as the JS does).
        chips = "".join(_affil_chip(n, c) for n, c in row) + "".join(_affil_chip(n, c, dup=True) for n, c in row)
        html_text = _replace_container(html_text, tid, chips)
        # Add the `running` class + speed vars the JS sets, so the marquee animates
        # without JS (~50 px/s, clamped 24–95s; --affil-shift is the -50% loop point).
        duration = min(95, max(24, len(row) * 190 / 50))
        html_text = re.sub(
            rf'<div class="(affil-track[^"]*)"([^>]*\bid="{tid}")',
            lambda m: f'<div class="{m.group(1)} running" style="--affil-duration:{duration}s;--affil-shift:-50%"{m.group(2)}',
            html_text,
            count=1,
        )
    return html_text


# The two webfont files the home-page hero paints in immediately: Source Serif
# 400 (the .hero-desc — the largest above-the-fold paint) and Syne (the <h1> at
# weight 700, plus the eyebrow and body text; after the build's content-dedup all
# Syne weights share the single 400 variable file). Only the `latin` subset is
# needed — the hero text is plain English — so `latin-ext` is left lazily loaded.
_HERO_PRELOAD_FONTS = (
    "assets/fonts/source-serif-4-400-normal-latin.woff2",
    "assets/fonts/syne-400-normal-latin.woff2",
)
# The local stylesheet link that a self-hosted-fonts build produces (see
# fonts.py / html_pages._swap_font_tags). Absent on the Google-Fonts fallback
# build, where the local woff2 files don't exist — so we key the preloads off it
# and emit nothing when it's missing (no dead preloads pointing at absent files).
_LOCAL_FONTS_LINK = '<link rel="stylesheet" href="assets/fonts.css" />'


def _preload_hero_fonts(html_text: str) -> str:
    """Home-page only: hint the browser to fetch the two hero webfonts in
    parallel with ``fonts.css`` instead of waiting to discover them inside it.

    ``crossorigin`` is required even though the fonts are same-origin: fonts are
    always fetched in CORS mode, and a non-CORS preload would be a *different*
    request than the one ``fonts.css`` triggers, so the file would download twice.

    Scoped to the home page on purpose. A global preload would make the JS-heavy
    problem pages (big chart SVGs, KaTeX) apply these fonts seconds after the
    download, tripping Firefox's "preloaded resource not used within a few
    seconds" warning. The hero uses both fonts on first paint, so no warning here.
    """
    if _LOCAL_FONTS_LINK not in html_text:
        return html_text
    preloads = "".join(
        f'    <link rel="preload" as="font" type="font/woff2" href="{_esc(href)}" crossorigin />\n'
        for href in _HERO_PRELOAD_FONTS
    )
    # Place the hints just before the stylesheet so they're discovered first.
    return html_text.replace(_LOCAL_FONTS_LINK, preloads + _LOCAL_FONTS_LINK, 1)


def _render_index(html_text: str, problems, index, landscape, submission_groups=None) -> str:
    html_text = _preload_hero_fonts(html_text)
    cards = "".join(_problem_card(p) for p in problems)
    html_text = _replace_container(html_text, "pgrid", cards)
    # Pre-fill the stat numbers (JS animateCount overwrites them on load); drop
    # the loading-val class so the "..." placeholder doesn't sit behind them.
    solved = sum((p.get("solved_count") or 0) for p in problems)
    html_text = _fill_stat(html_text, "s-inst", _fmt_int(index.get("total_instances", 0)))
    html_text = _fill_stat(html_text, "s-subs", _fmt_int(index.get("total_submissions", 0)))
    html_text = _fill_stat(html_text, "s-solved", _fmt_int(solved))
    # Inject the pre-rendered complexity-landscape SVGs (static; JS re-injects
    # the same markup on load). Skip only if a plot is missing from the payload.
    if submission_groups:
        html_text = _render_affiliations(html_text, submission_groups)
    if landscape:
        if landscape.get("mip"):
            html_text = _replace_container(html_text, "landscape-mip", landscape["mip"])
        if landscape.get("qubo"):
            html_text = _replace_container(html_text, "landscape-qubo", landscape["qubo"])
    return html_text


def _instance_row(inst, problem_id, problem_name, columns) -> str:
    metrics = inst.get("metrics") or {}
    parts = []
    for c in columns:
        key = c.get("key")
        val = metrics.get(key)
        if val is None or val == "":
            continue
        shown = _fmt_num(val) if c.get("numeric") else _esc(val)
        parts.append(f"{_esc(c.get('label'))} {shown}")
    metrics_text = " · ".join(parts)
    metrics_plain = " · ".join(
        f"{c.get('label')} {metrics.get(c.get('key'))}"
        for c in columns
        if metrics.get(c.get("key")) not in (None, "")
    )

    best = _best_value(inst)
    best_str = _fmt_num(best)
    best_cell = f"<strong>{best_str}</strong>" if inst.get("best_is_optimal") and best_str != "-" else best_str
    # A collapsed portfolio base has no single objective (its λ are different,
    # non-comparable objectives) — show the sweep size instead of a value.
    if best_str == "-" and inst.get("lambda_count"):
        best_cell = f'<span class="muted">{_esc(inst["lambda_count"])} λ</span>'

    src = inst.get("best_source_url")
    src_cell = (
        f'<a class="dl" href="{_esc(src)}" target="_blank" rel="noopener">'
        f'{_esc(inst.get("best_source_label") or inst.get("best_source_type") or "source")}</a>'
        if src else "-"
    )
    raw = inst.get("raw_url")
    raw_cell = f'<a class="dl" href="{_esc(raw)}" target="_blank" rel="noopener">↓ raw</a>' if raw else "-"

    return f"""
                <tr data-export-key="{_esc(str(problem_id) + '::' + inst['name'])}">
                    <td><a class="rlink mono" href="instance.html?problem={_esc(problem_id)}&amp;name={_esc(inst['name'])}">{_esc(inst['name'])}</a></td>
                    <td><a class="badge b-type" href="problem/{_esc(problem_id)}/">{_esc(_pad(problem_id))} {_esc(problem_name)}</a></td>
                    <td class="notes-cell" title="{_esc(metrics_plain)}">{metrics_text or "-"}</td>
                    <td class="num">{best_cell}</td>
                    <td>{src_cell}</td>
                    <td>{_status_pill(inst.get('status'))}</td>
                    <td>{raw_cell}</td>
                </tr>"""


def _instance_sort_key(name: str):
    """Numeric-aware ordering — mirror localeCompare(..., {numeric:true})."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", str(name))]


# Rows to pre-render in the big Instances table. The full list (1351 instances)
# is far more DOM than a viewport needs and dominates the page's initial parse.
# Pre-render a first page; instances.js reveals the rest via a "Show more" button
# (kept in sync with INST_PAGE in that file). No-JS users see this first page plus
# a note pointing to the per-problem pages (which list every instance).
#
# The leaderboard has no such global cap: it groups records into collapsible
# per-problem <details> sections (each set is naturally bounded), so every record
# is pre-rendered and reachable without JS — see _render_leaderboard.
_INST_PAGE = 100


def _render_instances(html_text: str, instances_groups, problems) -> str:
    rows = []
    for group in instances_groups:
        columns = group.get("columns") or []
        pid = group.get("id")
        pname = group.get("name", "")
        for inst in group.get("instances", []):
            rows.append((inst, pid, pname, columns))
    rows.sort(key=lambda r: _instance_sort_key(r[0]["name"]))
    total = len(rows)
    page = rows[:_INST_PAGE]
    body = "".join(_instance_row(inst, pid, pname, cols) for inst, pid, pname, cols in page)
    if not body:
        body = '<tr><td colspan="7" class="text-center padded">No instances match the current filters.</td></tr>'
    html_text = _replace_container(html_text, "i-tbody", body)
    html_text = _inject_options(html_text, "i-prob", _problem_options(problems, include_dash=False))
    # No-JS note when the list is truncated (the button needs JS; the full list
    # per problem is reachable without it via the problem pages).
    if total > len(page):
        hidden = total - len(page)
        note = (f'<noscript><p class="table-more-note">Showing the first {len(page):,} of '
                f'{total:,} instances. Enable JavaScript to load more, or browse every '
                f'instance by problem from the <a href="problems.html">Problems</a> page.</p></noscript>')
        html_text = _replace_container(html_text, "i-more", note)
    return html_text


def _inject_options(html_text: str, select_id: str, options: list) -> str:
    """Append `<option>`s (a list of strings) after the existing default option
    inside a `<select>`, each on its own line indented to match the default."""
    m = re.search(rf'(<select[^>]*\bid="{re.escape(select_id)}"[^>]*>)(.*?)(</select>)', html_text, re.DOTALL)
    if not m:
        return html_text
    existing = m.group(2)
    # Match the indentation of the shell's default <option> (or the </select>).
    im = re.search(r'\n([ \t]*)<option', existing) or re.search(r'\n([ \t]*)$', existing)
    indent = im.group(1) if im else "                "
    added = "".join(f"\n{indent}{opt}" for opt in options)
    # Drop a trailing blank-ish line before </select>, then re-add options + close.
    body = existing.rstrip() + added + "\n" + indent[:-4] if indent else existing + added
    return html_text[:m.start()] + m.group(1) + body + m.group(3) + html_text[m.end():]


def _render_submissions(html_text: str, submission_groups, problems) -> str:
    problem_by_id = {p["id"]: p for p in problems}

    def sub_date(group):
        # Prefer profile.date; fall back to the YYYYMMDD prefix on the dir name.
        own = (group.get("profile") or {}).get("date") or ""
        if own:
            return own
        m = re.match(r"^(\d{6,8})_", str(group.get("source_dir") or group.get("id") or ""))
        return m.group(1) if m else ""

    def sort_ts(group):
        d = sub_date(group)
        # YYYY-MM-DD or YYYYMMDD → sortable int; unknown sorts last (newest first).
        digits = re.sub(r"\D", "", d)
        return int(digits) if digits else -1

    groups = sorted(
        submission_groups,
        key=lambda g: (sort_ts(g), str(g.get("problem_id")), str(g.get("id"))),
        reverse=True,
    )

    rows = []
    for group in groups:
        pid = group.get("problem_id")
        problem = problem_by_id.get(pid)
        profile = group.get("profile") or {}
        cat = group.get("category") or classify_submission(profile)
        problem_label = f"{_pad(pid)} - {problem['name']}" if problem else "-"
        n_inst = len(group.get("instances") or [])
        date = sub_date(group)
        rows.append(f"""
                <tr data-export-key="{_esc(str(pid) + '::' + group['id'])}">
                    <td><a class="rlink" href="submission.html?problem={_esc(pid)}&amp;id={_esc(group['id'])}" title="{_esc(group['id'])}">{_esc(_submission_method(group.get('source_dir') or group.get('id')))}</a></td>
                    <td><a class="badge b-type" href="problem/{_esc(pid)}/">{_esc(problem_label)}</a></td>
                    <td>{_cat_badge(cat)}</td>
                    <td>{_esc(profile.get('submitter') or '-')}</td>
                    <td>{_esc(profile.get('affiliation') or '-')}</td>
                    <td class="mono">{_esc(date or '-')}</td>
                    <td class="num">{n_inst:,}</td>
                </tr>""")
    body = "".join(rows)
    if not body:
        body = '<tr><td colspan="7" class="text-center padded">No submissions match the current filters.</td></tr>'
    html_text = _replace_container(html_text, "sub-tbody", body)

    # Stat tiles (JS recomputes these; pre-fill the final values).
    total_inst = sum(len(g.get("instances") or []) for g in groups)
    n_problems = len({g.get("problem_id") for g in groups})
    n_authors = len({(g.get("profile") or {}).get("submitter") for g in groups if (g.get("profile") or {}).get("submitter")})
    html_text = _set_element_text(html_text, "sub-stat-packages", f"{len(groups):,}")
    html_text = _set_element_text(html_text, "sub-stat-instances", f"{total_inst:,}")
    html_text = _set_element_text(html_text, "sub-stat-problems", f"{n_problems:,}")
    html_text = _set_element_text(html_text, "sub-stat-authors", f"{n_authors:,}")

    html_text = _inject_options(html_text, "sub-prob", _problem_options(problems, include_dash=True))
    return html_text


# --------------------------------------------------------------------------- #
# Leaderboard — Overall view only (default). Ports lbChampion / lbMakeRecord.
# --------------------------------------------------------------------------- #
def _lb_champion(raw_subs, minimize, feas):
    """Best feasible submission for one instance (any paradigm). Returns the
    ``(sub, value, no_value)`` triple or None. Mirrors lbChampion in leaderboard.js."""
    cands = []
    for s in raw_subs:
        if not _is_attributable(s):
            continue
        raw = _cnum(s.get("value"))
        no_value = raw is None
        v = 0.0 if (no_value and feas) else raw
        if v is None:
            continue
        t = re.sub(r"\D", "", str(s.get("date") or "")) or "0"
        rt = _cnum(s.get("runtime_total"))
        cands.append((s, v, no_value, int(t), rt if rt is not None else float("inf")))
    if not cands:
        return None
    cands.sort(key=lambda c: (c[1] if minimize else -c[1], c[3], c[4]))
    s, v, no_value, _, _ = cands[0]
    return s, v, no_value


def _feasible_count(raw_subs, feas) -> int:
    # Counts submissions that *qualify* for the leaderboard (feasible and
    # attribution-eligible), matching the champion pool in _lb_champion and the
    # "Subs" column in leaderboard.js.
    n = 0
    for s in raw_subs:
        if not _is_attributable(s):
            continue
        raw = _cnum(s.get("value"))
        v = 0.0 if (raw is None and feas) else raw
        if v is not None:
            n += 1
    return n


def _lb_record_row(r) -> str:
    """One leaderboard <tr>. The Problem column is dropped here (the enclosing
    <details> section already names the problem) — mirrors lbRecordRow in
    leaderboard.js."""
    obj = ('<span title="A feasible solution was found; this problem reports no objective value">feasible</span>'
           if r["no_value"] else _fmt_num(r["value"]))
    star = ' <span title="Reaches the best-known objective" style="color:var(--star)">★</span>' if r["reached_best"] else ""
    return f"""
                <tr data-export-key="{_esc(str(r['problem_id']) + '::' + r['instance'])}">
                    <td class="mono"><a class="rlink mono" href="instance.html?problem={_esc(r['problem_id'])}&amp;name={_esc(r['instance'])}">{_esc(r['instance'])}</a></td>
                    <td class="num">{obj}{star}</td>
                    <td>{_status_pill(r['status'])}</td>
                    <td>{_fmt_text(r['holder'])}</td>
                    <td>{_cat_badge(r['category'])}</td>
                    <td class="mono">{_esc(r['date'] or '-')}</td>
                    <td class="num">{_fmt_maybe_num(r['runtime'])}</td>
                    <td class="num">{r['n_subs']}</td>
                </tr>"""


def _lb_problem_section(pid, pname, records, open_section: bool) -> str:
    """A collapsible <details> section for one problem's leaderboard records.

    The summary carries the problem number + name, its record count and how many
    of those records reach the best-known objective. Rendering every record here
    (each problem's set is naturally bounded) is what lets the no-JS page show the
    whole leaderboard without the old cross-problem "Show more" pagination."""
    n = len(records)
    n_best = sum(1 for r in records if r["reached_best"])
    best_chip = (f'<span class="lb-sec-best" title="Records reaching the best-known objective">'
                 f'★ {n_best:,}</span>') if n_best else ""
    rows = "".join(_lb_record_row(r) for r in records)
    return f"""<details class="lb-prob-section"{' open' if open_section else ''} data-problem="{_esc(pid)}">
        <summary>
            <a class="badge b-type" href="problem/{_esc(pid)}/" onclick="event.stopPropagation()">{_esc(_pad(pid))}</a>
            <span class="lb-sec-name">{_esc(pname)}</span>
            <span class="lb-sec-counts"><span class="lb-sec-recs">{n:,} record{'' if n == 1 else 's'}</span>{best_chip}</span>
        </summary>
        <div class="tw"><table>
        <thead>
            <tr>
                <th>Instance</th>
                <th style="text-align:right">Best objective</th>
                <th>Status</th>
                <th>Holder</th>
                <th>Type</th>
                <th>Date</th>
                <th style="text-align:right">Runtime (s)</th>
                <th style="text-align:right">Subs</th>
            </tr>
        </thead>
        <tbody>{rows}
        </tbody>
    </table></div>
    </details>"""


def _render_leaderboard(html_text: str, problems, instances_groups, instance_subs_by_problem) -> str:
    inst_by_problem = {}
    for group in instances_groups:
        inst_by_problem[group.get("id")] = {i["name"]: i for i in group.get("instances", [])}

    # Records grouped per problem, preserving the problem order from `problems`.
    by_problem = []  # [(pid, pname, [record, ...])]
    total = 0
    for p in problems:
        pid = p["id"]
        pname = p.get("name", _pad(pid))
        minimize = p.get("minimize") is not False
        insts = inst_by_problem.get(pid, {})
        feas = _is_feasibility_problem({"instances": list(insts.values())})
        entries = instance_subs_by_problem.get(pid, {})
        recs = []
        for name, inst in insts.items():
            raw_subs = entries.get(name, [])
            champ = _lb_champion(raw_subs, minimize, feas)
            if not champ:
                continue
            sub, v, no_value = champ
            best_known = _cnum(_best_value(inst))
            scale = max(1.0, abs(best_known) if best_known is not None else 0.0, abs(v))
            if feas:
                reached_best = abs(v) <= 1e-9
            else:
                reached_best = best_known is not None and abs(v - best_known) <= 1e-9 * scale
            recs.append({
                "problem_id": pid,
                "instance": name,
                "status": inst.get("status"),
                "value": v,
                "no_value": no_value and feas,
                "reached_best": reached_best,
                "holder": sub.get("submitter") or sub.get("author") or "",
                "category": _cat_of(sub),
                "date": sub.get("date") or "",
                "runtime": sub.get("runtime_total"),
                "n_subs": _feasible_count(raw_subs, feas),
            })
        if recs:
            recs.sort(key=lambda r: _instance_sort_key(r["instance"]))
            by_problem.append((pid, pname, recs))
            total += len(recs)

    if not by_problem:
        content = '<div class="lb-empty">No submissions yet.</div>'
    else:
        # Every section starts collapsed, so the page opens as a compact index of
        # problems the reader expands on demand. All records are still present in
        # the HTML (no JS needed to reveal them once a section is opened).
        sections = "".join(
            _lb_problem_section(pid, pname, recs, open_section=False)
            for pid, pname, recs in by_problem
        )
        legend = ('<div class="table-legend" style="margin:.4rem 0 .6rem;color:var(--muted)">'
                  'Records are grouped by problem — expand a section for its table. One record per '
                  'instance: the best feasible submission and who holds it. ★ = reaches the best-known '
                  'objective. "Subs" counts the ranked feasible submissions for that instance.</div>')
        content = f'<div class="lb-sections">{sections}</div>{legend}'

    html_text = _replace_container(html_text, "lb-content", content)
    html_text = _set_element_text(html_text, "lb-count", f"{total} record{'' if total == 1 else 's'}")
    html_text = _inject_options(html_text, "lb-prob", _problem_options(problems, include_dash=True))
    return html_text


# --------------------------------------------------------------------------- #
# Minimal Markdown → HTML for the problem README intro (description_md).
#
# The JS renders description_md with `marked`; to match it without a Markdown
# dependency (the builder is deliberately stdlib-only) we cover exactly the
# features the ten problem READMEs use: ## / ### headings, **bold**, *italic*,
# `code`, [text](url) links, and `-`/`*` bullet lists. Everything else is a
# paragraph. Two deliberate parities with the JS pipeline:
#   * Math ($…$, $$…$$) is preserved verbatim as literal text — KaTeX auto-render
#     picks it up client-side, exactly as it does for the JS-rendered version;
#     without JS it shows as raw TeX (same as every other math span on the site).
#   * Raw HTML blocks (the READMEs' <p align=center><img></p> figure) are dropped,
#     mirroring layoutDescriptionImage, which strips the README image in favour of
#     the site's own inline figure.
# This is intentionally small, not a general Markdown engine.
# --------------------------------------------------------------------------- #
_MD_MATH_RES = (
    re.compile(r"\$\$.+?\$\$", re.DOTALL),   # $$ display $$
    re.compile(r"\\\[.+?\\\]", re.DOTALL),   # \[ display \]
    re.compile(r"\\\(.+?\\\)", re.DOTALL),   # \( inline \)
    re.compile(r"(?<!\$)\$(?!\$)[^\n]*?\$"),  # $ inline $ (single line)
)
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_MD_ITALIC_RE = re.compile(r"(?<!\*)\*(?!\s)([^*\n]+?)(?<!\s)\*(?!\*)")
_MD_CODE_RE = re.compile(r"`([^`]+)`")
# Raw HTML the READMEs embed for the figure: a <p align=center> … </p> wrapper
# (with an <img> inside), or a bare <img>. Strip the whole container — including
# its contents and close tag — so no fragments leak into the rendered text.
_MD_HTML_BLOCK_RES = (
    re.compile(r"<(p|div|figure|table)\b[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE),
    re.compile(r"<img\b[^>]*/?>", re.IGNORECASE),
)


def _md_inline(text: str) -> str:
    """Escape, then apply inline Markdown (code, links, bold, italic). Math spans
    have already been stashed behind sentinels by ``_render_markdown``."""
    out = _esc(text)
    out = _MD_CODE_RE.sub(lambda m: f"<code>{m.group(1)}</code>", out)
    out = _MD_LINK_RE.sub(
        lambda m: f'<a href="{_esc(m.group(2))}" target="_blank" rel="noopener">{m.group(1)}</a>'
        if _safe_md_url(m.group(2)) else m.group(1),
        out,
    )
    out = _MD_BOLD_RE.sub(lambda m: f"<strong>{m.group(1)}</strong>", out)
    out = _MD_ITALIC_RE.sub(lambda m: f"<em>{m.group(1)}</em>", out)
    return out


def _safe_md_url(url: str) -> bool:
    u = url.strip().lower()
    return u.startswith(("http://", "https://", "mailto:", "#", "/", "./", "../"))


def _render_markdown(md: str) -> str:
    """Render the small Markdown subset used by the problem READMEs to HTML.
    Best-effort and deliberately minimal (see the block comment above)."""
    if not md:
        return ""
    # 1. Stash math verbatim so no inline rule mangles it; restore at the end.
    stash: list[str] = []

    def keep(m):
        stash.append(m.group(0))
        return f"\x00M{len(stash) - 1}\x00"

    text = md
    for rx in _MD_MATH_RES:
        text = rx.sub(keep, text)
    # 2. Drop raw HTML blocks (README figure) — the site renders its own figure.
    for rx in _MD_HTML_BLOCK_RES:
        text = rx.sub("", text)

    # 3. Block-level pass over blank-line-separated chunks.
    blocks: list[str] = []
    list_items: list[str] = []

    def flush_list():
        if list_items:
            blocks.append("<ul>" + "".join(f"<li>{it}</li>" for it in list_items) + "</ul>")
            list_items.clear()

    para_open = False  # whether the current paragraph is still accepting lines
    for raw_line in text.split("\n"):
        stripped = raw_line.strip()
        if not stripped:
            flush_list()
            para_open = False  # a blank line ends the current paragraph
            continue
        h = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        li = re.match(r"^[-*]\s+(.*)$", stripped)
        if h:
            flush_list()
            para_open = False
            level = min(max(len(h.group(1)), 2), 4)  # README ## → page <h2>…<h4>
            blocks.append(f"<h{level}>{_md_inline(h.group(2))}</h{level}>")
        elif li:
            para_open = False
            list_items.append(_md_inline(li.group(1)))
        else:
            # Soft-wrapped lines within one paragraph (no blank between) join with a
            # space; a blank line above starts a fresh <p> (para_open reset).
            if para_open and blocks and blocks[-1].endswith("</p>"):
                blocks[-1] = blocks[-1][:-4] + " " + _md_inline(stripped) + "</p>"
            else:
                flush_list()
                blocks.append(f"<p>{_md_inline(stripped)}</p>")
                para_open = True
    flush_list()

    html = "".join(blocks)
    # 4. Restore math verbatim (literal TeX; KaTeX renders it client-side).
    return re.sub(r"\x00M(\d+)\x00", lambda m: stash[int(m.group(1))], html)


_LEAD_HEADING_RE = re.compile(r"^\s*(<h[1-3]>.*?</h[1-3]>)", re.DOTALL | re.IGNORECASE)


def _split_lead_heading(html: str):
    """Split a leading <h1|h2|h3> off the front of rendered content, mirroring
    layoutDescriptionImage: the heading spans full width above the description +
    figure columns. Returns (lead_html, rest_html)."""
    m = _LEAD_HEADING_RE.match(html)
    if not m:
        return "", html
    return m.group(1), html[m.end():]


# --------------------------------------------------------------------------- #
# Problem detail page (#prob-detail) — full no-JS render for the deep
# problem/<id>/ pages. Mirrors problem.js initProblemPage container.innerHTML:
# header + description + performance charts + submissions + instances. The
# client overwrites #prob-detail on load, so this is the hydration fallback.
# --------------------------------------------------------------------------- #
_PERF_CHARTS = [
    ("cactus", "cactus-body", "has_cactus", "Runtime to reach best-known objective",
     "Sorted instances vs total runtime. A point (x, y) means x instances were solved within y seconds. Solid line + filled circle = proven exact; dashed line + open diamond = heuristic. Lower-right is better."),
    ("tts", "tts-body", "has_tts", "Time-to-solution (TTS) to reach best-known objective",
     "Same as the runtime cactus but uses the reported Time-to-Solution rather than total runtime. Solid = exact, dashed = heuristic."),
    ("profile", "profile-body", "has_profile", "Solution quality (performance profile)",
     "Share of instances each group brings within a given optimality gap of the best-known objective. Higher is better; the value at “best” is the share solved exactly."),
    ("scaling", "scaling-body", "has_scaling", "Runtime scaling with instance size",
     "Fastest feasible runtime (log scale) per instance versus {size} — shows how each group scales."),
]


def _collapsible(title, body_html, count=None) -> str:
    label = f'{_esc(title)} <span class="ps-count">({count})</span>' if count is not None else _esc(title)
    return (
        f'<details class="prob-section" open><summary class="prob-section-head">'
        f'<h2 class="prob-section-title">{label}</h2></summary>'
        f'<div class="prob-section-body">{body_html}</div></details>'
    )


def _perf_section(charts) -> str:
    """Performance charts section — inject the pre-baked SVGs for the default
    view (paradigm grouping, wide variant). Mirrors performanceSection + the
    initial renderPerf() in problem.js. Returns "" when nothing to plot."""
    if not charts:
        return ""
    if not (charts.get("modes") and (charts.get("has_cactus") or charts.get("has_tts")
                                     or charts.get("has_profile") or charts.get("has_scaling"))):
        return ""
    size_label = charts.get("size_label") or "size"
    paradigm = (charts.get("modes") or {}).get("paradigm") or {}
    cards = []
    for key, cid, has, title, desc in _PERF_CHARTS:
        if not charts.get(has):
            continue
        svg = (paradigm.get(key) or {}).get("wide", "")
        cards.append(
            f'<section class="tw chart-card"><div class="chart-head"><div>'
            f'<h3>{_esc(title)}</h3><p>{_esc(desc.format(size=size_label))}</p></div></div>'
            f'<div id="{cid}">{svg}</div></section>'
        )
    return (
        '<div class="perf-toolbar"><div class="seg-toggle" role="group" aria-label="Grouping">'
        '<button type="button" class="seg-btn on" data-mode="paradigm" aria-pressed="true">By paradigm</button>'
        '<button type="button" class="seg-btn" data-mode="submission" aria-pressed="false">By submission</button>'
        '</div></div>'
        f'<div class="perf-charts">{"".join(cards)}</div>'
    )


def _problem_submissions_section(pid, groups) -> str:
    if not groups:
        return ('<div class="empty-state">No submissions for this problem yet. '
                '<a class="sh-link" href="submit.html">Submit one →</a></div>')

    def sub_date(g):
        own = (g.get("profile") or {}).get("date") or ""
        if own:
            return own
        m = re.match(r"^(\d{6,8})_", str(g.get("source_dir") or g.get("id") or ""))
        return m.group(1) if m else ""

    def sort_ts(g):
        digits = re.sub(r"\D", "", sub_date(g))
        return int(digits) if digits else -1

    rows = []
    for g in sorted(groups, key=lambda g: (sort_ts(g), str(g.get("id"))), reverse=True):
        prof = g.get("profile") or {}
        cat = g.get("category") or classify_submission(prof)
        rows.append(
            f'<tr>'
            f'<td><a class="rlink" href="submission.html?problem={_esc(pid)}&amp;id={_esc(g["id"])}" title="{_esc(g["id"])}">{_esc(_submission_method(g.get("source_dir") or g.get("id")))}</a></td>'
            f'<td>{_fmt_text(prof.get("submitter"))}</td>'
            f'<td>{_cat_badge(cat)}</td>'
            f'<td class="mono">{_esc(sub_date(g) or "-")}</td>'
            f'<td class="num">{len(g.get("instances") or []):,}</td>'
            f'</tr>'
        )
    return (
        '<div class="tw"><table><thead><tr><th>Method</th><th>Submitter</th><th>Type</th>'
        '<th data-sort-default="desc">Date</th><th style="text-align:right">Instances</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def _problem_instance_cells(inst, columns) -> str:
    metrics = inst.get("metrics") or {}
    cells = []
    for c in columns:
        v = metrics.get(c.get("key"))
        cls = ' class="num"' if c.get("numeric") else ""
        if v is None or v == "":
            cells.append(f"<td{cls}>-</td>")
        else:
            cells.append(f"<td{cls}>{_fmt_num(v) if c.get('numeric') else _esc(v)}</td>")
    return "".join(cells)


def _problem_instances_section(pid, instances, columns) -> str:
    metric_head = "".join(
        ('<th style="text-align:right">' if c.get("numeric") else "<th>") + f'{_esc(c.get("label"))}</th>'
        for c in columns
    )
    ordered = sorted(instances, key=lambda i: _instance_sort_key(i.get("name", "")))
    rows = []
    for inst in ordered:
        best = _best_value(inst)
        best_str = _fmt_num(best)
        best_cell = f"<strong>{best_str}</strong>" if inst.get("best_is_optimal") and best_str != "-" else best_str
        # Collapsed portfolio base: no single objective — show the λ sweep size.
        if best_str == "-" and inst.get("lambda_count"):
            best_cell = f'<span class="muted">{_esc(inst["lambda_count"])} λ</span>'
        src = inst.get("best_source_url")
        src_cell = (
            f'<a class="dl" href="{_esc(src)}" target="_blank" rel="noopener">'
            f'{_esc(inst.get("best_source_label") or inst.get("best_source_type") or "source")}</a>'
            if src else "-"
        )
        raw = inst.get("raw_url")
        raw_cell = f'<a class="dl" href="{_esc(raw)}" target="_blank" rel="noopener">↓ raw</a>' if raw else "-"
        rows.append(
            f'<tr data-export-key="{_esc(inst["name"])}">'
            f'<td class="mono"><a class="rlink mono" href="instance.html?problem={_esc(pid)}&amp;name={_esc(inst["name"])}">{_esc(inst["name"])}</a></td>'
            f'{_problem_instance_cells(inst, columns)}'
            f'<td class="num">{best_cell}</td>'
            f'<td>{src_cell}</td>'
            f'<td>{_status_pill(inst.get("status"))}</td>'
            f'<td>{raw_cell}</td>'
            f'</tr>'
        )
    body = "".join(rows) or f'<tr><td colspan="{5 + len(columns)}" class="text-center padded">No instances match the search.</td></tr>'
    n = len(instances)
    return (
        '<div class="filters">'
        '<input type="text" class="fi-grow" id="prob-inst-search" placeholder="Search by instance name..." />'
        f'<span class="fi-count" id="prob-inst-count">{n:,} of {n:,}</span>'
        '<button class="btn btn-ghost btn-sm" type="button" id="prob-inst-csv-btn">⬇ Download CSV</button>'
        '</div>'
        '<div class="tw"><table><thead><tr>'
        '<th data-sort-default="asc">Name</th>'
        f'{metric_head}'
        '<th style="text-align:right">Best objective</th><th>Source</th><th>Status</th><th>Download</th>'
        '</tr></thead>'
        f'<tbody id="prob-inst-tbody">{body}</tbody></table></div>'
    )


def render_problem_detail(p, figure_svg=None) -> str:
    """Full server-rendered #prob-detail body for a deep problem page — mirrors
    problem.js. ``p`` is a full problem payload (meta + instances +
    submission_groups + charts); ``figure_svg`` is the problem's illustration
    (from problem_figures.js) laid out beside the description. The client
    hydrates over this on load."""
    pid = p.get("id", "")
    columns = p.get("columns") or []
    instances = p.get("instances") or []
    groups = p.get("submission_groups") or []
    charts = p.get("charts") or {}
    minimize = p.get("minimize") is not False
    solved = p.get("solved_count")
    if solved is None:
        solved = sum(1 for i in instances if i.get("status") in ("optimal", "solved"))

    tags = "".join(f'<span class="badge b-tag">{_esc(t)}</span>' for t in (p.get("tags") or []))
    vars_row = (
        f'<div class="mr"><span class="mk">Variable range</span><span class="mv">{_fmt_int(p.get("vars_min"))}–{_fmt_int(p.get("vars_max"))}</span></div>'
        if p.get("vars_min") is not None else ""
    )
    # Description: mirror problem.js priority exactly — the rendered README intro
    # (description_md) when present, else the plain `description`; the `formula`
    # line is shown only in the non-markdown branch (matching `!description_md &&
    # formula` in the JS). This keeps the no-JS text identical to what JS renders.
    desc_md = p.get("description_md")
    inner = ""
    if desc_md:
        inner = _render_markdown(desc_md)
    elif p.get("description"):
        inner = f'<p>{_esc(p.get("description"))}</p>'
        if p.get("formula"):
            inner += f'<div class="formula">{_esc(p.get("formula"))}</div>'
    elif p.get("formula"):
        inner = f'<div class="formula">{_esc(p.get("formula"))}</div>'

    desc_block = ""
    if inner:
        if figure_svg:
            # Two-column layout with the illustration, mirroring
            # layoutDescriptionImage: a leading heading (if any) spans full width
            # above, then the remaining content sits beside the figure.
            lead, rest = _split_lead_heading(inner)
            desc_block = (
                '<hr class="section-divider" />'
                '<div class="d-desc d-desc-layout">'
                f'{lead}'
                '<div class="d-desc-columns">'
                f'<div class="d-desc-content">{rest}</div>'
                f'<div class="d-desc-visual">{figure_svg}</div>'
                '</div></div>'
            )
        else:
            desc_block = f'<hr class="section-divider" /><div class="d-desc">{inner}</div>'

    header = (
        '<div class="dh"><div>'
        f'<div class="d-num">{_esc(_pad(pid))} / {_esc(p.get("slug", ""))}</div>'
        f'<h1 class="d-title">{_esc(p.get("name", ""))}</h1>'
        f'<div class="d-sub">{_esc(p.get("short", ""))}</div>'
        '<div class="pcard-foot">'
        f'<span class="badge b-type">{_esc(p.get("type", ""))}</span>'
        f'<span class="badge b-form">{_esc(p.get("formulation", ""))}</span>'
        f'{tags}</div></div>'
        '<div class="d-meta">'
        f'<div class="mr"><span class="mk">Instances</span><span class="mv">{_fmt_int(p.get("instance_count"))}</span></div>'
        f'<div class="mr"><span class="mk">Optimally solved</span><span class="mv">{_fmt_int(solved)} / {_fmt_int(p.get("instance_count"))}</span></div>'
        f'{vars_row}'
        f'<div class="mr"><span class="mk">Objective</span><span class="mv">{"minimize" if minimize else "maximize"}</span></div>'
        '</div></div>'
    )

    perf = _perf_section(charts)
    parts = [header, desc_block]
    if perf:
        parts.append(_collapsible("Performance", perf))
    parts.append(_collapsible("Submissions", _problem_submissions_section(pid, groups), len(groups)))
    parts.append(_collapsible("Instances", _problem_instances_section(pid, instances, columns), p.get("instance_count")))

    github = p.get("github_url")
    parts.append(
        '<div class="hero-actions" style="margin-top:1.5rem">'
        + (f'<a class="btn btn-ghost" href="{_esc(github)}" target="_blank" rel="noopener">View on GitHub ↗</a>' if github else "")
        + '<a class="btn btn-navy" href="leaderboard.html">View Leaderboard</a>'
        '<a class="btn btn-ghost" href="instances.html">Browse All Instances</a></div>'
    )
    return "".join(parts)


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def render_overview_pages(out_dir, site_data) -> None:
    """Pre-render content into the five overview pages under ``out_dir``.

    ``site_data`` carries the aggregates already computed by build_data:
      * ``index``            — the site index dict (built_at, totals, problems)
      * ``problems``         — the lightweight per-problem summaries (index.problems)
      * ``instances_groups`` — trimmed per-problem instance lists (+ columns)
      * ``submission_groups``— all submission packages across problems
      * ``instance_subs``    — {problem_id: {instance_name: [submission rows]}}
      * ``landscape``        — {"mip": <svg>, "qubo": <svg>} home-page scatters
    """
    out_dir = Path(out_dir)
    index = site_data["index"]
    problems = site_data["problems"]
    instances_groups = site_data["instances_groups"]
    # Per-λ groups for the leaderboard (portfolio keeps its 8× rows here); falls
    # back to the collapsed groups for any run that predates the split.
    lb_instances_groups = site_data.get("lb_instances_groups", instances_groups)
    submission_groups = site_data["submission_groups"]
    instance_subs = site_data["instance_subs"]
    landscape = site_data.get("landscape") or {}

    pages = {
        "problems.html": lambda h: _render_problems(h, problems),
        "index.html": lambda h: _render_index(h, problems, index, landscape, submission_groups),
        "instances.html": lambda h: _render_instances(h, instances_groups, problems),
        "submissions.html": lambda h: _render_submissions(h, submission_groups, problems),
        "leaderboard.html": lambda h: _render_leaderboard(h, problems, lb_instances_groups, instance_subs),
    }
    for filename, render in pages.items():
        path = out_dir / filename
        if not path.is_file():
            continue
        path.write_text(render(path.read_text(encoding="utf-8")), encoding="utf-8")
