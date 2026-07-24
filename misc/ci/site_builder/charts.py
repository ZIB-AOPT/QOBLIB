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
"""Pre-render the per-problem performance charts (cactus / profile / scaling).

These three SVG charts used to be computed in the browser on *every* problem-page
load (``website/assets/problem.js``). That is pure, build-time-deterministic work
— it only depends on the instance/submission data that is already frozen at build
time — so we render it once here and ship the markup in ``charts.json``. The
client then merely injects the prebaked SVG for the active grouping mode and
viewport breakpoint.

The maths below is a faithful port of ``problem.js``. The two MUST stay in sync:
if you change a chart's geometry, formatting, grouping, or colours in one, change
it in the other. The colours mirror ``SUBMISSION_CATEGORIES`` / ``CACTUS_PALETTE``
in ``assets/common.js`` and ``assets/problem.js`` (paradigm lines use the
``var(--cat-*)`` theme variables so they still adapt to light/dark mode; the axes,
grid and labels keep their ``conv-*`` CSS classes for the same reason).
"""

from __future__ import annotations

import math
import re

from .classify import classify_submission

# Paradigm grouping: fixed category order + full labels + theme-variable colours.
CAT_INFO = {
    "quantum_hw": ("Quantum hardware", "var(--cat-quantum-hw)"),
    "quantum_sim": ("Quantum simulator", "var(--cat-quantum-sim)"),
    "classical": ("Classical", "var(--cat-classical)"),
}
CACTUS_CATS = ["classical", "quantum_sim", "quantum_hw"]
# Submission grouping: one colour per curve, cycled. Hex (not theme vars) — these
# per-submission series have no semantic colour to track across themes.
CACTUS_PALETTE = ["#2f6db0", "#c0504d", "#9bbb59", "#8064a2", "#4bacc6", "#f79646", "#7f6084", "#5a7d2c"]

# Viewport variants: wide desktop vs. a taller/narrower phone aspect (perfDims).
DIMS = {"wide": (720, 300), "narrow": (430, 340)}

EMPTY_MSGS = {
    "cactus": "No group reached the best-known objective with a recorded runtime in this view.",
    "profile": "No optimality-gap data in this view.",
    "scaling": "No instance-size / runtime data in this view.",
}

_SUB_RE = re.compile(r"^\d{6,8}_(.+)_([^_]+)$")
_VAR_RE = re.compile(r"^(num[_-]?|n[_-]?)?vars?$|^variables$", re.IGNORECASE)
_SIZE_RE = re.compile(r"length|node|dimension|grid|asset|customer|size|qubit", re.IGNORECASE)


# --------------------------------------------------------------------------- #
# Small helpers (ports of the same-named frontend utilities)
# --------------------------------------------------------------------------- #
def _esc(value) -> str:
    """HTML-escape, matching ``esc`` in common.js (String(value ?? ""))."""
    s = "" if value is None else str(value)
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _cnum(value):
    """Parse to a finite float or None — port of ``cNum`` (Number.isFinite gate)."""
    if value is None or value == "":
        return None
    try:
        n = float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return None
    return n if math.isfinite(n) else None


def _best_value(inst):
    """``inst.best_value ?? inst.bkv`` — fall through only on a missing/None value."""
    v = inst.get("best_value")
    return v if v is not None else inst.get("bkv")


def _is_feasible(sub) -> bool:
    """``cIsFeasible``: feasible unless '# Feasible Runs' is explicitly 0."""
    nf = _cnum(sub.get("n_feasible"))
    return not (nf is not None and nf == 0)


def _is_feasibility_problem(problem) -> bool:
    """A problem whose every known best value is 0 (find-a-feasible-point goal)."""
    saw_zero = False
    for inst in problem.get("instances", []) or []:
        bv = _cnum(_best_value(inst))
        if bv is None:
            continue
        if bv != 0:
            return False
        saw_zero = True
    return saw_zero


def _ref_best(inst, feas_subs, minimize):
    """Reference best objective: recorded best-known tightened by feasible subs."""
    ref = _cnum(_best_value(inst))
    for s in feas_subs:
        v = _cnum(s.get("value"))
        if v is None:
            continue
        if ref is None:
            ref = v
        else:
            ref = min(ref, v) if minimize else max(ref, v)
    return ref


def _size_source(problem):
    """(label, getter) for the scaling x-axis — port of ``sizeSource``."""
    cols = [c for c in (problem.get("columns") or []) if c.get("numeric")]
    var_col = next((c for c in cols if _VAR_RE.search(str(c.get("key", "")))), None)
    size_col = (
        var_col
        or next((c for c in cols if _SIZE_RE.search(str(c.get("key", "")))), None)
        or (cols[0] if cols else None)
    )
    if size_col:
        key = size_col.get("key")
        label = size_col.get("label")
        return label, (lambda inst: _cnum((inst.get("metrics") or {}).get(key)))
    return "size", (lambda inst: None)


def _submission_method(dir_name) -> str:
    d = str(dir_name or "")
    m = _SUB_RE.match(d)
    return m.group(1) if m else (d if d else "Unknown")


def _submission_author(dir_name) -> str:
    m = _SUB_RE.match(str(dir_name or ""))
    return m.group(2) if m else ""


# --------------------------------------------------------------------------- #
# Number formatting (ports of cFmtTime / cFmtGap / cFmtSize)
# --------------------------------------------------------------------------- #
def _js_exponential(v, digits=1) -> str:
    """Match JS ``Number.prototype.toExponential`` — minimal exponent digits."""
    s = f"{v:.{digits}e}"
    mant, exp = s.split("e")
    exp_i = int(exp)
    sign = "+" if exp_i >= 0 else "-"
    return f"{mant}e{sign}{abs(exp_i)}"


def _num_locale(v, dp) -> str:
    """Match ``Number(v.toFixed(dp)).toLocaleString()`` (en-US grouping)."""
    s = f"{v:.{dp}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    neg = s.startswith("-")
    if neg:
        s = s[1:]
    if "." in s:
        intp, frac = s.split(".")
    else:
        intp, frac = s, ""
    grouped = f"{int(intp):,}" if intp else "0"
    out = grouped + ("." + frac if frac else "")
    return ("-" + out) if (neg and out != "0") else out


def _fmt_time(v) -> str:
    a = abs(v)
    if a != 0 and (a >= 1e5 or a < 1e-3):
        return _js_exponential(v, 1)
    dp = 2 if a < 10 else (1 if a < 1000 else 0)
    return _num_locale(v, dp)


def _fmt_gap(pct) -> str:
    a = abs(pct)
    dp = 2 if a < 1 else (1 if a < 10 else 0)
    return _num_locale(pct, dp) + "%"


def _fmt_size(v) -> str:
    a = abs(v)
    dp = 1 if a < 10 else 0
    return _num_locale(v, dp)


def _jround(x) -> int:
    """JS ``Math.round`` — half rounds toward +Infinity."""
    return math.floor(x + 0.5)


def _f1(x) -> str:
    return f"{x:.1f}"


# --------------------------------------------------------------------------- #
# Per-mode dataset assembly (port of buildPerfMode)
# --------------------------------------------------------------------------- #
def _build_perf_mode(problem, mode):
    instances = problem.get("instances", []) or []
    entries = problem.get("instance_submissions", {}) or {}
    minimize = problem.get("minimize", True) is not False
    feas = _is_feasibility_problem(problem)
    _label, size_get = _size_source(problem)

    def group_key(s):
        if mode == "submission":
            return s.get("_source_dir") or s.get("submitter") or s.get("author") or "Unknown"
        return s.get("category") or classify_submission(s)

    groups: dict = {}

    def G(k):
        if k not in groups:
            groups[k] = {"times": [], "gaps": [], "points": []}
        return groups[k]

    for inst in instances:
        subs = [s for s in (entries.get(inst.get("name")) or []) if _is_feasible(s)]
        if not subs:
            continue
        target = _cnum(_best_value(inst))
        ref = 0 if feas else _ref_best(inst, subs, minimize)
        size = size_get(inst)

        best_rt: dict = {}   # group -> fastest runtime that reached best-known
        min_gap: dict = {}   # group -> smallest optimality gap %
        feas_rt: dict = {}   # group -> fastest feasible runtime (scaling)

        for s in subs:
            k = group_key(s)
            val = _cnum(s.get("value"))
            rt = _cnum(s.get("runtime_total"))

            if feas:
                reached = (val is None) or abs(val) <= 1e-9
            elif val is not None and target is not None:
                scale = max(1, abs(target), abs(val))
                reached = abs(val - target) <= 1e-9 * scale
            else:
                reached = False
            if reached and rt is not None:
                pr = best_rt.get(k)
                if pr is None or rt < pr:
                    best_rt[k] = rt

            if (not feas) and val is not None and ref is not None:
                gap = max(0, ((val - ref) if minimize else (ref - val)) / max(1, abs(ref)) * 100)
                pr = min_gap.get(k)
                if pr is None or gap < pr:
                    min_gap[k] = gap

            if size is not None and rt is not None:
                pr = feas_rt.get(k)
                if pr is None or rt < pr:
                    feas_rt[k] = rt

        for k, rt in best_rt.items():
            G(k)["times"].append(rt)
        for k, g in min_gap.items():
            G(k)["gaps"].append(g)
        for k, rt in feas_rt.items():
            G(k)["points"].append({"size": size, "rt": rt})

    def finalize(key, name, color):
        g = groups[key]
        return {
            "key": key,
            "name": name,
            "color": color,
            "times": sorted(g["times"]),
            "gaps": sorted(g["gaps"]),
            "points": list(g["points"]),
        }

    if mode == "submission":
        keys = sorted(groups.keys(), key=lambda k: (-len(groups[k]["points"]), str(k)))
        label_counts: dict = {}
        for k in keys:
            lbl = _submission_method(k)
            label_counts[lbl] = label_counts.get(lbl, 0) + 1
        out = []
        for i, k in enumerate(keys):
            name = _submission_method(k)
            if label_counts[name] > 1:
                a = _submission_author(k)
                name = f"{name} ({a})" if a else k
            out.append(finalize(k, name, CACTUS_PALETTE[i % len(CACTUS_PALETTE)]))
        return out

    return [finalize(k, CAT_INFO[k][0], CAT_INFO[k][1]) for k in CACTUS_CATS if k in groups]


# --------------------------------------------------------------------------- #
# SVG builders (ports of buildCactusChart / buildProfileChart / buildScalingChart)
# --------------------------------------------------------------------------- #
def _svg(w, h, body) -> str:
    return (
        f'<svg class="conv-svg" viewBox="0 0 {w} {h}" role="img" '
        f'preserveAspectRatio="xMidYMid meet">{body}</svg>'
    )


def _axes(m_l, m_t, m_b, m_r, w, h) -> str:
    return (
        f'<line class="conv-axis-line" x1="{m_l}" y1="{m_t}" x2="{m_l}" y2="{h - m_b}" />'
        f'<line class="conv-axis-line" x1="{m_l}" y1="{h - m_b}" x2="{w - m_r}" y2="{h - m_b}" />'
    )


def _cactus_svg(series, dims) -> str:
    w, h = dims
    live = [s for s in series if s["times"]]
    all_times = [t for s in live for t in s["times"]]
    if not all_times:
        return ""

    m_t, m_r, m_b, m_l = 16, 18, 44, 66
    max_n = max((len(s["times"]) for s in live), default=0)
    pos = [t for t in all_times if t > 0]
    floor = min(pos) if pos else 1e-3
    clamp = lambda t: t if t > 0 else floor

    lo = math.log10(min(clamp(t) for t in all_times))
    hi = math.log10(max(clamp(t) for t in all_times))
    if lo == hi:
        lo -= 1
        hi += 1
    else:
        pad = (hi - lo) * 0.08
        lo -= pad
        hi += pad

    x_max = max(max_n, 1)
    x_px = lambda c: m_l + (w - m_l - m_r) * (0.5 if x_max <= 1 else c / x_max)
    y_px = lambda t: h - m_b - (h - m_t - m_b) * ((math.log10(clamp(t)) - lo) / ((hi - lo) or 1))

    yticks = [(10 ** (lo + (hi - lo) * (i / 4))) for i in range(5)]
    xticks: list = []
    step = max(1, math.ceil(x_max / 6))
    c = 0
    while c <= x_max:
        xticks.append(c)
        c += step
    if xticks[-1] != x_max:
        xticks.append(x_max)

    grid = "".join(
        f'<line class="conv-grid" x1="{m_l}" y1="{_f1(y_px(v))}" x2="{w - m_r}" y2="{_f1(y_px(v))}" />'
        for v in yticks
    )
    y_labels = "".join(
        f'<text class="conv-tick" text-anchor="end" x="{m_l - 8}" y="{_f1(y_px(v) + 3)}">{_esc(_fmt_time(v))}</text>'
        for v in yticks
    )
    x_labels = "".join(
        f'<text class="conv-tick" text-anchor="middle" x="{_f1(x_px(ct))}" y="{h - m_b + 16}">{ct}</text>'
        for ct in xticks
    )
    x_title = (
        f'<text class="conv-axis-title" text-anchor="middle" x="{_f1((m_l + (w - m_r)) / 2)}" '
        f'y="{h - 5}">instances solved →</text>'
    )
    cy = _f1((m_t + (h - m_b)) / 2)
    y_title = (
        f'<text class="conv-axis-title" text-anchor="middle" transform="rotate(-90 14 {cy})" '
        f'x="14" y="{cy}">runtime (s, log)</text>'
    )

    parts = []
    for s in live:
        pts = [(x_px(i + 1), y_px(t), i + 1, t) for i, t in enumerate(s["times"])]
        d = ""
        for i, (px, py, _c, _t) in enumerate(pts):
            d += f'{"M" if i == 0 else "L"} {_f1(px)} {_f1(py)} '
        line = (
            f'<path d="{d.strip()}" fill="none" style="stroke:{s["color"]}" '
            f'stroke-width="2" stroke-linejoin="round" />'
        )
        dots = "".join(
            f'<circle cx="{_f1(px)}" cy="{_f1(py)}" r="3.2" style="fill:{s["color"]}">'
            f'<title>{_esc(s["name"])} · solved {cc} · {_esc(_fmt_time(tt))} s</title></circle>'
            for (px, py, cc, tt) in pts
        )
        parts.append(line + dots)

    body = grid + _axes(m_l, m_t, m_b, m_r, w, h) + y_labels + x_labels + x_title + y_title + "".join(parts)
    return _svg(w, h, body)


def _profile_svg(groups, ref_n, dims) -> str:
    w, h = dims
    live = [g for g in groups if g["gaps"]]
    allg = [x for g in live for x in g["gaps"]]
    if not allg or not ref_n:
        return ""

    m_t, m_r, m_b, m_l = 16, 18, 44, 66
    g_max = max(allg)
    hi = math.log10(1 + g_max) if g_max > 0 else math.log10(2)
    axis_max_gap = 10 ** hi - 1
    x_px = lambda gap: m_l + (w - m_l - m_r) * (math.log10(1 + max(0, gap)) / hi)
    y_px = lambda f: h - m_b - (h - m_t - m_b) * f

    yticks = [0, 0.25, 0.5, 0.75, 1]
    grid = "".join(
        f'<line class="conv-grid" x1="{m_l}" y1="{_f1(y_px(f))}" x2="{w - m_r}" y2="{_f1(y_px(f))}" />'
        for f in yticks
    )
    y_labels = "".join(
        f'<text class="conv-tick" text-anchor="end" x="{m_l - 8}" y="{_f1(y_px(f) + 3)}">{_jround(f * 100)}%</text>'
        for f in yticks
    )
    xticks = [(10 ** (hi * (i / 4)) - 1) for i in range(5)]
    x_labels = "".join(
        f'<text class="conv-tick" text-anchor="middle" x="{_f1(x_px(gap))}" y="{h - m_b + 16}">'
        f'{("best" if gap <= 1e-9 else "+" + _esc(_fmt_gap(gap)))}</text>'
        for gap in xticks
    )
    x_title = (
        f'<text class="conv-axis-title" text-anchor="middle" x="{_f1((m_l + (w - m_r)) / 2)}" '
        f'y="{h - 5}">optimality gap from best-known →</text>'
    )
    cy = _f1((m_t + (h - m_b)) / 2)
    y_title = (
        f'<text class="conv-axis-title" text-anchor="middle" transform="rotate(-90 14 {cy})" '
        f'x="14" y="{cy}">instances solved (%)</text>'
    )

    parts = []
    for g in live:
        s = sorted(g["gaps"])
        steps = []
        cum = 0
        for i in range(len(s)):
            cum += 1
            if i + 1 < len(s) and s[i + 1] == s[i]:
                continue
            steps.append((s[i], cum / ref_n))
        prev_y = y_px(0)
        d = f"M {_f1(x_px(0))} {_f1(prev_y)}"
        dots = []
        for gap, frac in steps:
            xx = x_px(gap)
            yy = y_px(frac)
            d += f" L {_f1(xx)} {_f1(prev_y)} L {_f1(xx)} {_f1(yy)}"
            lbl = "best" if gap <= 1e-9 else "+" + _esc(_fmt_gap(gap))
            dots.append(
                f'<circle cx="{_f1(xx)}" cy="{_f1(yy)}" r="2.6" style="fill:{g["color"]}">'
                f'<title>{_esc(g["name"])} · within {lbl} · {_jround(frac * 100)}%</title></circle>'
            )
            prev_y = yy
        d += f" L {_f1(x_px(axis_max_gap))} {_f1(prev_y)}"
        parts.append(
            f'<path d="{d}" fill="none" style="stroke:{g["color"]}" '
            f'stroke-width="2" stroke-linejoin="round" />' + "".join(dots)
        )

    body = grid + _axes(m_l, m_t, m_b, m_r, w, h) + y_labels + x_labels + x_title + y_title + "".join(parts)
    return _svg(w, h, body)


def _scaling_svg(groups, size_label, dims) -> str:
    w, h = dims
    live = [g for g in groups if g["points"]]
    pts = [pt for g in live for pt in g["points"]]
    sizes = [pt["size"] for pt in pts if pt["size"] is not None and pt["size"] > 0]
    if not pts or not sizes:
        return ""

    m_t, m_r, m_b, m_l = 16, 18, 44, 70
    rts = [pt["rt"] for pt in pts]
    rpos = [r for r in rts if r > 0]
    rfloor = min(rpos) if rpos else 1e-3
    clamp_r = lambda r: r if r > 0 else rfloor

    xlo = math.log10(min(sizes))
    xhi = math.log10(max(sizes))
    if xlo == xhi:
        xlo -= 0.5
        xhi += 0.5
    else:
        pad = (xhi - xlo) * 0.06
        xlo -= pad
        xhi += pad
    ylo = math.log10(min(clamp_r(r) for r in rts))
    yhi = math.log10(max(clamp_r(r) for r in rts))
    if ylo == yhi:
        ylo -= 1
        yhi += 1
    else:
        pad = (yhi - ylo) * 0.08
        ylo -= pad
        yhi += pad

    x_px = lambda s: m_l + (w - m_l - m_r) * ((math.log10(max(s, 1e-9)) - xlo) / ((xhi - xlo) or 1))
    y_px = lambda r: h - m_b - (h - m_t - m_b) * ((math.log10(clamp_r(r)) - ylo) / ((yhi - ylo) or 1))

    xticks = [(10 ** (xlo + (xhi - xlo) * (i / 4))) for i in range(5)]
    yticks = [(10 ** (ylo + (yhi - ylo) * (i / 4))) for i in range(5)]
    grid = "".join(
        f'<line class="conv-grid" x1="{m_l}" y1="{_f1(y_px(v))}" x2="{w - m_r}" y2="{_f1(y_px(v))}" />'
        for v in yticks
    )
    y_labels = "".join(
        f'<text class="conv-tick" text-anchor="end" x="{m_l - 8}" y="{_f1(y_px(v) + 3)}">{_esc(_fmt_time(v))}</text>'
        for v in yticks
    )
    x_labels = "".join(
        f'<text class="conv-tick" text-anchor="middle" x="{_f1(x_px(v))}" y="{h - m_b + 16}">{_esc(_fmt_size(v))}</text>'
        for v in xticks
    )
    x_title = (
        f'<text class="conv-axis-title" text-anchor="middle" x="{_f1((m_l + (w - m_r)) / 2)}" '
        f'y="{h - 5}">{_esc(size_label)} (log) →</text>'
    )
    cy = _f1((m_t + (h - m_b)) / 2)
    y_title = (
        f'<text class="conv-axis-title" text-anchor="middle" transform="rotate(-90 14 {cy})" '
        f'x="14" y="{cy}">runtime (s, log)</text>'
    )

    parts = []
    for g in live:
        circles = "".join(
            f'<circle cx="{_f1(x_px(pt["size"]))}" cy="{_f1(y_px(pt["rt"]))}" r="3" '
            f'style="fill:{g["color"]};fill-opacity:0.78">'
            f'<title>{_esc(g["name"])} · {_esc(size_label)} {_esc(_fmt_size(pt["size"]))} · '
            f'{_esc(_fmt_time(pt["rt"]))} s</title></circle>'
            for pt in g["points"]
            if pt["size"] is not None and pt["size"] > 0
        )
        parts.append(circles)

    body = grid + _axes(m_l, m_t, m_b, m_r, w, h) + y_labels + x_labels + x_title + y_title + "".join(parts)
    return _svg(w, h, body)


# --------------------------------------------------------------------------- #
# Legend + body assembly (port of renderInto) and the public entry point
# --------------------------------------------------------------------------- #
def _legend_html(groups, field) -> str:
    return "".join(
        f'<span class="conv-leg"><span class="conv-dot" style="background:{g["color"]}"></span>'
        f'{_esc(g["name"])} ({len(g[field])})</span>'
        for g in groups
        if g[field]
    )


def _body_html(svg, groups, field, empty_msg) -> str:
    if not svg:
        return f'<div class="empty-state">{_esc(empty_msg)}</div>'
    legend = _legend_html(groups, field)
    return f'<div class="conv-legend" style="margin:.1rem 0 .5rem">{legend}</div>{svg}'


# field name on each group dict that feeds each chart's legend / has-data check.
_CHART_FIELD = {"cactus": "times", "profile": "gaps", "scaling": "points"}


def build_problem_charts(problem):
    """Return the pre-rendered chart payload for one problem, or None if there is
    nothing to plot. Shape (consumed by ``performanceSection`` in problem.js)::

        {
          "problem_id": "07",
          "size_label": "Nodes",
          "ref_n": 42,
          "has_cactus": true, "has_profile": true, "has_scaling": true,
          "modes": {
            "paradigm":   {"cactus": {"wide": "<html>", "narrow": "<html>"}, ...},
            "submission": {...}
          }
        }

    Each ``wide`` / ``narrow`` value is the ready-to-inject body HTML (legend +
    SVG, or an empty-state message when that mode has no data for the chart).
    """
    feas = _is_feasibility_problem(problem)
    size_label, _size_get = _size_source(problem)
    minimize = problem.get("minimize", True) is not False
    entries = problem.get("instance_submissions", {}) or {}
    instances = problem.get("instances", []) or []

    ref_n = 0
    if not feas:
        for inst in instances:
            subs = [s for s in (entries.get(inst.get("name")) or []) if _is_feasible(s)]
            if subs and _ref_best(inst, subs, minimize) is not None:
                ref_n += 1

    modes = {
        "paradigm": _build_perf_mode(problem, "paradigm"),
        "submission": _build_perf_mode(problem, "submission"),
    }

    def any_field(field):
        return any(g[field] for g in modes["paradigm"]) or any(g[field] for g in modes["submission"])

    has_cactus = any_field("times")
    has_profile = (not feas) and ref_n > 0 and any_field("gaps")
    has_scaling = any_field("points")
    if not (has_cactus or has_profile or has_scaling):
        return None

    present = []
    if has_cactus:
        present.append("cactus")
    if has_profile:
        present.append("profile")
    if has_scaling:
        present.append("scaling")

    def render(chart, groups, dims):
        field = _CHART_FIELD[chart]
        if chart == "cactus":
            svg = _cactus_svg(groups, dims)
        elif chart == "profile":
            svg = _profile_svg(groups, ref_n, dims)
        else:
            svg = _scaling_svg(groups, size_label, dims)
        return _body_html(svg, groups, field, EMPTY_MSGS[chart])

    out_modes = {}
    for mode, groups in modes.items():
        out_modes[mode] = {
            chart: {bp: render(chart, groups, dims) for bp, dims in DIMS.items()}
            for chart in present
        }

    return {
        "problem_id": problem.get("id"),
        "size_label": size_label,
        "ref_n": ref_n,
        "has_cactus": has_cactus,
        "has_profile": has_profile,
        "has_scaling": has_scaling,
        "modes": out_modes,
    }
