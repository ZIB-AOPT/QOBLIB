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
    "cactus":  "No group reached the best-known objective with a recorded runtime in this view.",
    "tts":     "No group reported a Time-to-Solution with a recorded best-known objective in this view.",
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


def _is_attributable(sub) -> bool:
    """Feasible *and* eligible to define/reach a best value.

    ``bkv_eligible == False`` marks a run whose reported objective is not
    comparable to exact results (currently Birkhoff decompositions that do not
    reconstruct exactly). Such a run must not tighten the reference best or be
    marked as "reached best-known" — same treatment charts already give infeasible
    runs. It still appears in the per-instance submission table (built separately
    in problem.py); it is only withheld from best-value/attribution here."""
    return _is_feasible(sub) and sub.get("bkv_eligible", True)


def _is_exact(sub) -> bool:
    """A submission is *exact* (proven optimal) when its Optimality Bound equals
    its Best Objective Value — i.e. the submitter asserts the solution is optimal.
    Algorithm type alone is NOT sufficient (a deterministic heuristic is not exact).
    """
    val   = _cnum(sub.get("value"))
    bound = _cnum(sub.get("optimality_bound"))
    if val is None or bound is None:
        return False
    scale = max(1.0, abs(val), abs(bound))
    return abs(val - bound) <= 1e-9 * scale


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


# --------------------------------------------------------------------------- #
# Axis ticks — tight, nicely-ticked log axes snapped to 1-2-5×10ⁿ bounds, so an
# axis never shows arbitrary values like "1234, 182938" AND never overshoots (a
# data max of 16 ends the axis at 20, not the next full decade 100). Mirrors
# ``niceLogAxis`` / ``niceLogBound`` in assets/common.js; keep the two in sync.
# --------------------------------------------------------------------------- #
def _nice_log_bound(value: float, direction: int) -> float:
    """Snap a positive value to the nearest 1-2-5×10ⁿ number. direction<0 rounds
    down (largest nice ≤ value); direction>0 rounds up (smallest nice ≥ value)."""
    if not (value > 0) or not math.isfinite(value):
        return 1.0
    e = math.floor(math.log10(value))
    base = 10.0 ** e
    m = value / base  # mantissa in [1, 10)
    steps = [1, 2, 5, 10]
    if direction < 0:
        chosen = 1
        for s in steps:
            if s <= m + 1e-9:
                chosen = s
        return chosen * base
    for s in steps:
        if s >= m - 1e-9:
            return s * base
    return 10 * base


def _nice_log_axis(min_val: float, max_val: float, *, max_major: int = 8):
    """Tight log axis for a positive data range. Returns ``(lo, hi, major, minor)``
    as real values: lo/hi are the endpoints snapped to nice 1-2-5 bounds, `major`
    are labelled tick values and `minor` are faint unlabelled guides. When the full
    1-2-5 sequence fits it is all labelled; over a wider span only decades are
    labelled and 2×/5× become minor guides."""
    lo = _nice_log_bound(min(min_val, max_val), -1)
    hi = _nice_log_bound(max(min_val, max_val), +1)
    if not (lo > 0):
        lo = 1.0
    if hi <= lo:
        hi = lo * 10  # guarantee a non-zero span (single-point data)

    e_lo = math.floor(math.log10(lo) + 1e-9)
    e_hi = math.ceil(math.log10(hi) - 1e-9)
    all_ticks: list = []
    for e in range(e_lo, e_hi + 1):
        for mm in (1, 2, 5):
            v = mm * 10.0 ** e
            if lo * (1 - 1e-9) <= v <= hi * (1 + 1e-9):
                all_ticks.append(v)
    uniq = sorted(set(all_ticks))
    if len(uniq) <= max_major:
        return lo, hi, uniq, []
    # Too many for full 1-2-5 labels: label decades, demote 2×/5× to faint guides
    # (only while the span is narrow enough that they stay legible).
    def is_decade(v):
        return abs(math.log10(v) - round(math.log10(v))) < 1e-9
    major = [v for v in uniq if is_decade(v)]
    minor = [v for v in uniq if not is_decade(v)] if (e_hi - e_lo) <= 3 else []
    return lo, hi, major, minor


def _use_log_axis(values) -> bool:
    """Whether a set of positive values is better shown on a log axis. True only
    when they span a wide multiplicative range (≥2 decades, i.e. a ≥100× spread).
    Small linear counting parameters — a LABS sequence length (2..100), a portfolio
    asset count, a matrix dimension — stay on a linear axis; only genuinely
    order-of-magnitude size ranges (e.g. variable counts spanning 100..13000) go
    log."""
    pos = [v for v in values if v is not None and v > 0]
    if len(pos) < 2:
        return False
    lo, hi = min(pos), max(pos)
    if lo <= 0:
        return False
    return math.log10(hi / lo) >= 2.0


def _nice_step(raw: float, *, integer: bool = False) -> float:
    """Round a raw step up to the nearest 1-2-5×10ⁿ. Mirrors ``niceStep`` in
    assets/common.js."""
    if not (raw > 0) or not math.isfinite(raw):
        return 1.0
    pow10 = 10.0 ** math.floor(math.log10(raw))
    frac = raw / pow10
    nice = 1 if frac <= 1 else 2 if frac <= 2 else 5 if frac <= 5 else 10
    step = nice * pow10
    if integer:
        step = max(1.0, round(step))
    return step


def _nice_linear_ticks(min_val: float, max_val: float, *, integer: bool = False, target: int = 5):
    """Tick values spanning [min, max] on a linear axis using a nice 1-2-5 step
    (integer-forced when the data is whole). Mirrors ``niceLinearTicks`` in
    assets/common.js."""
    lo, hi = float(min_val), float(max_val)
    if not (math.isfinite(lo) and math.isfinite(hi)):
        return []
    if lo > hi:
        lo, hi = hi, lo
    if lo == hi:
        return [round(lo) if integer else lo]
    step = _nice_step((hi - lo) / max(1, target), integer=integer)
    if not (step > 0):
        return [lo, hi]
    start = math.ceil(lo / step - 1e-9) * step
    ticks = []
    v = start
    while v <= hi + step * 1e-9:
        ticks.append(round(v) if integer else round(v, 10))
        v += step
    return ticks or [lo, hi]


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
            groups[k] = {"times": [], "tts": [], "gaps": [], "points": []}
        return groups[k]

    for inst in instances:
        inst_name = inst.get("name", "")
        subs = [s for s in (entries.get(inst_name) or []) if _is_attributable(s)]
        if not subs:
            continue
        target = _cnum(_best_value(inst))
        ref = 0 if feas else _ref_best(inst, subs, minimize)
        size = size_get(inst)

        best_rt:  dict = {}  # group -> (fastest runtime, exact_flag) that reached best-known
        best_tts: dict = {}  # group -> (fastest TTS, exact_flag) that reached best-known
        min_gap:  dict = {}  # group -> smallest optimality gap %
        feas_rt:  dict = {}  # group -> fastest feasible runtime (scaling)

        for s in subs:
            k = group_key(s)
            val   = _cnum(s.get("value"))
            rt    = _cnum(s.get("runtime_total"))
            tts   = _cnum(s.get("time_to_solution"))
            exact = _is_exact(s)

            if feas:
                reached = (val is None) or abs(val) <= 1e-9
            elif val is not None and target is not None:
                scale = max(1, abs(target), abs(val))
                reached = abs(val - target) <= 1e-9 * scale
            else:
                reached = False

            if reached and rt is not None:
                pr = best_rt.get(k)
                if pr is None or rt < pr[0]:
                    best_rt[k] = (rt, exact)

            # TTS: accept when the submission reached the best-known value and
            # reported a finite, non-negative TTS. tts == 0 is valid (solved
            # instantly / at first evaluation).
            if reached and tts is not None and tts >= 0:
                pr = best_tts.get(k)
                if pr is None or tts < pr[0]:
                    best_tts[k] = (tts, exact)

            if (not feas) and val is not None and ref is not None:
                gap = max(0, ((val - ref) if minimize else (ref - val)) / max(1, abs(ref)) * 100)
                pr = min_gap.get(k)
                if pr is None or gap < pr[0]:
                    min_gap[k] = (gap, inst_name)

            if size is not None and rt is not None:
                pr = feas_rt.get(k)
                if pr is None or rt < pr[0]:
                    feas_rt[k] = (rt, inst_name)

        for k, (rt, exact) in best_rt.items():
            G(k)["times"].append({"rt": rt, "exact": exact, "inst": inst_name})
        for k, (tts, exact) in best_tts.items():
            G(k)["tts"].append({"rt": tts, "exact": exact, "inst": inst_name})
        for k, (gap, iname) in min_gap.items():
            G(k)["gaps"].append({"gap": gap, "inst": iname})
        for k, (rt, iname) in feas_rt.items():
            G(k)["points"].append({"size": size, "rt": rt, "inst": iname})

    def finalize(key, name, color):
        g = groups[key]
        return {
            "key":    key,
            "name":   name,
            "color":  color,
            # Sort cactus/TTS entries by runtime; keep exact flag alongside.
            "times":  sorted(g["times"],  key=lambda x: x["rt"]),
            "tts":    sorted(g["tts"],    key=lambda x: x["rt"]),
            "gaps":   sorted(g["gaps"],   key=lambda x: x["gap"]),
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

def _diamond(cx: float, cy: float, r: float) -> str:
    """SVG polygon for an open diamond (rotated square) with half-size r."""
    pts = (f"{_f1(cx)},{_f1(cy - r)} {_f1(cx + r)},{_f1(cy)} "
           f"{_f1(cx)},{_f1(cy + r)} {_f1(cx - r)},{_f1(cy)}")
    return f'<polygon points="{pts}"'


_SVG_TITLE_SEQ = [0]


def _svg(w, h, body, aria_label=None) -> str:
    if not aria_label:
        return (
            f'<svg class="conv-svg" viewBox="0 0 {w} {h}" role="img" '
            f'preserveAspectRatio="xMidYMid meet">{body}</svg>'
        )
    # Accessible name via a <title> referenced by aria-labelledby (so it takes
    # precedence over the per-mark <title> tooltips inside the body). The id must
    # be unique per rendered SVG on the page; a monotonic counter keeps it so
    # across the several charts baked into one problem page.
    _SVG_TITLE_SEQ[0] += 1
    title_id = f"conv-svg-title-{_SVG_TITLE_SEQ[0]}"
    return (
        f'<svg class="conv-svg" viewBox="0 0 {w} {h}" role="img" '
        f'aria-labelledby="{title_id}" preserveAspectRatio="xMidYMid meet">'
        f'<title id="{title_id}">{_esc(aria_label)}</title>{body}</svg>'
    )


def _axes(m_l, m_t, m_b, m_r, w, h) -> str:
    return (
        f'<line class="conv-axis-line" x1="{m_l}" y1="{m_t}" x2="{m_l}" y2="{h - m_b}" />'
        f'<line class="conv-axis-line" x1="{m_l}" y1="{h - m_b}" x2="{w - m_r}" y2="{h - m_b}" />'
    )


def _cactus_body(series, field, dims, y_title_txt) -> str:
    """Shared renderer for both the runtime cactus and the TTS cactus.

    *field* is ``"times"`` or ``"tts"``; each entry is ``{"rt": float, "exact": bool}``.
    Exact submissions (proven optimal) are drawn with a solid line + filled circle;
    heuristics with a dashed line + open diamond marker.
    """
    w, h = dims
    live = [s for s in series if s[field]]
    all_rts = [e["rt"] for s in live for e in s[field]]
    if not all_rts:
        return ""

    m_t, m_r, m_b, m_l = 16, 18, 44, 66
    max_n = max((len(s[field]) for s in live), default=0)
    pos = [t for t in all_rts if t > 0]
    floor = min(pos) if pos else 1e-3
    clamp = lambda t: t if t > 0 else floor

    # Y (runtime, log): tight axis snapped to nice 1-2-5 bounds (a max of 16 s ends
    # at 20, not 100), labelled 1-2-5 ticks + faint minor guides. lo/hi are the
    # log10 endpoints used for positioning. X (instances solved): integer counts.
    y_min_v = min(clamp(t) for t in all_rts)
    y_max_v = max(clamp(t) for t in all_rts)
    lo_v, hi_v, yticks, y_minor = _nice_log_axis(y_min_v, y_max_v, max_major=6)
    if not yticks:
        yticks = [lo_v, hi_v]
    # Pad the plotted domain ~5% beyond the bounds so the fastest/slowest points
    # sit inset from the top/bottom frame rather than flush against it.
    PAD = 0.05
    _yspan = (math.log10(hi_v) - math.log10(lo_v)) or 1
    lo = math.log10(lo_v) - _yspan * PAD
    hi = math.log10(hi_v) + _yspan * PAD

    x_max = max(max_n, 1)
    # Inset the point row a little from both side frames (the first point is at
    # count 1, the last at x_max — map that span into 4%..96% of the plot width).
    x_px = lambda c: m_l + (w - m_l - m_r) * (0.5 if x_max <= 1 else 0.04 + 0.92 * (c / x_max))
    y_px = lambda t: h - m_b - (h - m_t - m_b) * ((math.log10(clamp(t)) - lo) / ((hi - lo) or 1))

    xticks: list = []
    step = max(1, math.ceil(x_max / 6))
    c = 0
    while c <= x_max:
        xticks.append(c)
        c += step
    if xticks[-1] != x_max:
        xticks.append(x_max)

    grid = "".join(
        f'<line class="conv-grid-minor" x1="{m_l}" y1="{_f1(y_px(v))}" x2="{w - m_r}" y2="{_f1(y_px(v))}" />'
        for v in y_minor
    ) + "".join(
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
    x_title_el = (
        f'<text class="conv-axis-title" text-anchor="middle" x="{_f1((m_l + (w - m_r)) / 2)}" '
        f'y="{h - 5}">instances solved →</text>'
    )
    cy = _f1((m_t + (h - m_b)) / 2)
    y_title_el = (
        f'<text class="conv-axis-title" text-anchor="middle" transform="rotate(-90 14 {cy})" '
        f'x="14" y="{cy}">{_esc(y_title_txt)}</text>'
    )

    parts = []
    for s in live:
        entries = s[field]
        pts = [(x_px(i + 1), y_px(e["rt"]), i + 1, e["rt"], e["exact"], e.get("inst", ""))
               for i, e in enumerate(entries)]

        # Line: solid for all-exact series, dashed when any entry is heuristic.
        all_exact = all(e["exact"] for e in entries)
        dash = "" if all_exact else ' stroke-dasharray="5 3"'
        d = "".join(
            f'{"M" if i == 0 else "L"} {_f1(px)} {_f1(py)} '
            for i, (px, py, *_) in enumerate(pts)
        )
        line = (
            f'<path d="{d.strip()}" fill="none" style="stroke:{s["color"]}"'
            f'{dash} stroke-width="2" stroke-linejoin="round" />'
        )

        # Markers: filled circle = exact; open diamond = heuristic.
        dot_parts = []
        for (px, py, cc, tt, exact, inst) in pts:
            tip = (f'{_esc(s["name"])} · {"exact" if exact else "heuristic"} '
                   f'· {_esc(inst)} · {_esc(_fmt_time(tt))} s')
            if exact:
                dot_parts.append(
                    f'<circle cx="{_f1(px)}" cy="{_f1(py)}" r="3.2" '
                    f'style="fill:{s["color"]}">'
                    f'<title>{tip}</title></circle>'
                )
            else:
                dot_parts.append(
                    f'{_diamond(px, py, 4.5)} '
                    f'style="fill:none;stroke:{s["color"]};stroke-width:1.5">'
                    f'<title>{tip}</title></polygon>'
                )
        parts.append(f'<g data-series="{_esc(s["key"])}">{line}{"".join(dot_parts)}</g>')

    body = grid + _axes(m_l, m_t, m_b, m_r, w, h) + y_labels + x_labels + x_title_el + y_title_el + "".join(parts)
    metric = "time-to-solution" if field == "tts" else "total runtime"
    label = (
        f"Cactus plot: cumulative number of instances solved (horizontal) versus "
        f"{metric} in seconds on a log scale (vertical), one line per method group; "
        f"lower-right is better."
    )
    return _svg(w, h, body, aria_label=label)


def _cactus_svg(series, dims) -> str:
    return _cactus_body(series, "times", dims, "runtime (s, log)")


def _tts_svg(series, dims) -> str:
    return _cactus_body(series, "tts", dims, "time-to-solution (s, log)")


def _profile_svg(groups, ref_n, dims) -> str:
    w, h = dims
    live = [g for g in groups if g["gaps"]]
    allg = [x["gap"] for g in live for x in g["gaps"]]
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
        # gaps is a list of {"gap": float, "inst": str}, already sorted by gap.
        s = g["gaps"]
        steps = []
        cum = 0
        inst_names: list = []
        for i in range(len(s)):
            cum += 1
            inst_names.append(s[i]["inst"])
            if i + 1 < len(s) and s[i + 1]["gap"] == s[i]["gap"]:
                continue
            steps.append((s[i]["gap"], cum / ref_n, list(inst_names)))
            inst_names = []
        prev_y = y_px(0)
        d = f"M {_f1(x_px(0))} {_f1(prev_y)}"
        dots = []
        for gap, frac, inames in steps:
            xx = x_px(gap)
            yy = y_px(frac)
            d += f" L {_f1(xx)} {_f1(prev_y)} L {_f1(xx)} {_f1(yy)}"
            lbl = "best" if gap <= 1e-9 else "+" + _esc(_fmt_gap(gap))
            inst_lbl = ", ".join(_esc(n) for n in inames)
            dots.append(
                f'<circle cx="{_f1(xx)}" cy="{_f1(yy)}" r="2.6" style="fill:{g["color"]}">'
                f'<title>{_esc(g["name"])} · within {lbl} · {_jround(frac * 100)}% · {inst_lbl}</title></circle>'
            )
            prev_y = yy
        d += f" L {_f1(x_px(axis_max_gap))} {_f1(prev_y)}"
        path = (
            f'<path d="{d}" fill="none" style="stroke:{g["color"]}" '
            f'stroke-width="2" stroke-linejoin="round" />'
        )
        parts.append(f'<g data-series="{_esc(g["key"])}">{path}{"".join(dots)}</g>')

    body = grid + _axes(m_l, m_t, m_b, m_r, w, h) + y_labels + x_labels + x_title + y_title + "".join(parts)
    label = (
        "Performance profile: share of instances (vertical) reached within a given "
        "optimality gap of the best-known objective (horizontal), one line per method "
        "group; higher is better."
    )
    return _svg(w, h, body, aria_label=label)


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

    # X (instance size): a log axis only makes sense when the sizes span a wide
    # multiplicative range. For problems like LABS the size is a small linear
    # sequence length (e.g. 3..66), where a log x-axis is misleading — use a linear
    # axis there. Heuristic: log only when the sizes cover >~1.5 decades.
    # Pad the plotted domain ~5% beyond the axis bounds on each side so points and
    # ticks sit inset from the frame rather than flush against the edges.
    PAD = 0.05

    def _pad(lo, hi):
        span = (hi - lo) or 1
        return lo - span * PAD, hi + span * PAD

    x_log = _use_log_axis(sizes)
    size_int = all(float(s).is_integer() for s in sizes)
    if x_log:
        x_lo_v, x_hi_v, xticks, x_minor = _nice_log_axis(min(sizes), max(sizes), max_major=6)
        xlo, xhi = _pad(math.log10(x_lo_v), math.log10(x_hi_v))
        if not xticks:
            xticks = [x_lo_v, x_hi_v]
        x_px = lambda s: m_l + (w - m_l - m_r) * ((math.log10(max(s, 1e-9)) - xlo) / ((xhi - xlo) or 1))
    else:
        xticks = _nice_linear_ticks(min(sizes), max(sizes), integer=size_int, target=6)
        x_minor = []
        lo0 = min([*xticks, min(sizes)]) if xticks else min(sizes)
        hi0 = max([*xticks, max(sizes)]) if xticks else max(sizes)
        xlo, xhi = _pad(lo0, hi0)
        x_px = lambda s: m_l + (w - m_l - m_r) * ((s - xlo) / ((xhi - xlo) or 1))

    # Y (runtime): always log — runtimes genuinely span orders of magnitude.
    y_lo_v, y_hi_v, yticks, y_minor = _nice_log_axis(
        min(clamp_r(r) for r in rts), max(clamp_r(r) for r in rts), max_major=5
    )
    ylo, yhi = _pad(math.log10(y_lo_v), math.log10(y_hi_v))
    if not yticks:
        yticks = [y_lo_v, y_hi_v]

    y_px = lambda r: h - m_b - (h - m_t - m_b) * ((math.log10(clamp_r(r)) - ylo) / ((yhi - ylo) or 1))
    grid = "".join(
        f'<line class="conv-grid-minor" x1="{m_l}" y1="{_f1(y_px(v))}" x2="{w - m_r}" y2="{_f1(y_px(v))}" />'
        for v in y_minor
    ) + "".join(
        f'<line class="conv-grid-minor" x1="{_f1(x_px(v))}" y1="{m_t}" x2="{_f1(x_px(v))}" y2="{_f1(h - m_b)}" />'
        for v in x_minor
    ) + "".join(
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
    x_scale_note = " (log)" if x_log else ""
    x_title = (
        f'<text class="conv-axis-title" text-anchor="middle" x="{_f1((m_l + (w - m_r)) / 2)}" '
        f'y="{h - 5}">{_esc(size_label)}{x_scale_note} →</text>'
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
            f'<title>{_esc(g["name"])} · {_esc(pt.get("inst", ""))} · '
            f'{_esc(size_label)} {_esc(_fmt_size(pt["size"]))} · '
            f'{_esc(_fmt_time(pt["rt"]))} s</title></circle>'
            for pt in g["points"]
            if pt["size"] is not None and pt["size"] > 0
        )
        parts.append(f'<g data-series="{_esc(g["key"])}">{circles}</g>')

    body = grid + _axes(m_l, m_t, m_b, m_r, w, h) + y_labels + x_labels + x_title + y_title + "".join(parts)
    label = (
        f"Scaling plot: fastest feasible runtime in seconds on a log scale (vertical) "
        f"versus {size_label} (horizontal), one series per method group."
    )
    return _svg(w, h, body, aria_label=label)


# --------------------------------------------------------------------------- #
# Legend + body assembly (port of renderInto) and the public entry point
# --------------------------------------------------------------------------- #
def _legend_html(groups, field) -> str:
    """Build legend entries for one chart.

    For cactus/TTS (``field`` is ``"times"`` or ``"tts"``) each entry carries an
    ``"exact"`` flag; we append an exact/heuristic note and use the right icon.
    For other charts the items are plain values so we just show the count.
    """
    parts = []
    for g in groups:
        items = g[field]
        if not items:
            continue
        n = len(items)
        # Detect cactus-family fields by checking whether items are dicts with "exact".
        if items and isinstance(items[0], dict) and "exact" in items[0]:
            n_exact = sum(1 for e in items if e["exact"])
            if n_exact == n:
                note = " · exact"
            elif n_exact == 0:
                note = " · heuristic"
            else:
                note = f" · {n_exact} exact, {n - n_exact} heuristic"
            # Solid circle icon for all-exact; open diamond icon for any heuristic.
            if n_exact == n:
                icon = f'<span class="conv-dot" style="background:{g["color"]}"></span>'
            else:
                icon = f'<span class="conv-dot conv-dot-heur" style="border-color:{g["color"]}"></span>'
        else:
            note = ""
            icon = f'<span class="conv-dot" style="background:{g["color"]}"></span>'
        parts.append(
            f'<span class="conv-leg" data-series="{_esc(g["key"])}" title="Click to solo / restore">'
            f'{icon}<span class="conv-leg-label">{_esc(g["name"])} ({n}{_esc(note)})</span></span>'
        )
    return "".join(parts)


def _body_html(svg, groups, field, empty_msg) -> str:
    if not svg:
        return f'<div class="empty-state">{_esc(empty_msg)}</div>'
    legend = _legend_html(groups, field)
    return f'<div class="conv-legend" style="margin:.1rem 0 .5rem">{legend}</div>{svg}'


# field name on each group dict that feeds each chart's legend / has-data check.
_CHART_FIELD = {"cactus": "times", "tts": "tts", "profile": "gaps", "scaling": "points"}


def build_problem_charts(problem):
    """Return the pre-rendered chart payload for one problem, or None if there is
    nothing to plot. Shape (consumed by ``performanceSection`` in problem.js)::

        {
          "problem_id": "07",
          "size_label": "Nodes",
          "ref_n": 42,
          "has_cactus": true, "has_tts": true, "has_profile": true, "has_scaling": true,
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
            subs = [s for s in (entries.get(inst.get("name")) or []) if _is_attributable(s)]
            if subs and _ref_best(inst, subs, minimize) is not None:
                ref_n += 1

    modes = {
        "paradigm":   _build_perf_mode(problem, "paradigm"),
        "submission": _build_perf_mode(problem, "submission"),
    }

    def any_field(field):
        return any(g[field] for g in modes["paradigm"]) or any(g[field] for g in modes["submission"])

    has_cactus  = any_field("times")
    has_tts     = any_field("tts")
    has_profile = (not feas) and ref_n > 0 and any_field("gaps")
    has_scaling = any_field("points")
    if not (has_cactus or has_tts or has_profile or has_scaling):
        return None

    present = []
    if has_cactus:
        present.append("cactus")
    if has_tts:
        present.append("tts")
    if has_profile:
        present.append("profile")
    if has_scaling:
        present.append("scaling")

    def render(chart, groups, dims):
        field = _CHART_FIELD[chart]
        if chart == "cactus":
            svg = _cactus_svg(groups, dims)
        elif chart == "tts":
            svg = _tts_svg(groups, dims)
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
        "problem_id":  problem.get("id"),
        "size_label":  size_label,
        "ref_n":       ref_n,
        "has_cactus":  has_cactus,
        "has_tts":     has_tts,
        "has_profile": has_profile,
        "has_scaling": has_scaling,
        "modes":       out_modes,
    }
