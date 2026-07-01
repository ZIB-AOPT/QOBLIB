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
"""Pre-render the home-page complexity-landscape scatter plots (MIP + QUBO).

The home page used to ship two static PNGs — a variables-vs-density scatter of
every instance, plus an inset marking which were solved to optimality. This
module reproduces them as theme-aware SVG at build time, mirroring what
``charts.py`` does for the per-problem performance charts.

Each figure has:
  • a main scatter, one point per instance, coloured by problem class (the colours
    mirror ``PROBLEM_COLORS`` in ``assets/instances.js`` — keep the two in sync), and
  • two small insets re-plotting the same points, colouring each by how far
    CLASSICAL vs QUANTUM methods got (optimal · best-known · open), in the
    same tier ramps as the problem-card progress bars (``var(--bar-*)``).

The main plot and both insets share one pair of log axes so point positions line
up. ``num_vars`` / ``density`` come from the repository's generated
``models/*/lp_files/metrics.csv`` (MIP) and ``qs_files/metrics.csv`` (QUBO); the
optimal / quantum-optimal flags come from the build's per-instance status (see
``problem.py``). Axes, grid and ticks reuse the ``mip-*`` CSS classes so they stay
theme-aware, exactly like the instances-page scatter.
"""

from __future__ import annotations

import math
import re

from .metrics import load_lp_metrics, load_qs_metrics
from .text import canonical_name_from_filename, normalize_portfolio_lambda

# Mirror PROBLEM_COLORS in assets/instances.js — (fill, stroke). Keep in sync so
# the home-page scatter matches the instances-page scatter.
PROBLEM_COLORS = {
    "01": ("#2E6F95", "#1C4A65"),
    "02": ("#B85C38", "#7D3D25"),
    "03": ("#5D8A66", "#3E5F45"),
    "04": ("#7A6EA8", "#514A75"),
    "05": ("#C58A24", "#875E17"),
    "06": ("#3F8D7E", "#2A6156"),
    "07": ("#A14F7A", "#6D3552"),
    "08": ("#4E7FB9", "#34577E"),
    "09": ("#B66A46", "#7E4931"),
    "10": ("#6F9E44", "#4D6D30"),
}
DEFAULT_COLOR = ("#1f6f6c", "#0e4f4d")

# Inset tier colours: theme variables, matching the problem-card progress bars so
# the home page reads consistently. Each paradigm uses its own tier ramp:
# optimal · best-known (matched the best value) · open (everything else — no
# feasible solution, or only a worse feasible one).
CLASSICAL_OPTIMAL_FILL = "var(--bar-solved-classical)"
CLASSICAL_BESTKNOWN_FILL = "var(--bar-best-known-classical)"
QUANTUM_OPTIMAL_FILL = "var(--bar-solved-quantum)"
QUANTUM_BESTKNOWN_FILL = "var(--bar-best-known-quantum)"
GREY_FILL = "var(--border-mid)"                     # open / not solved (legend swatch)
UNSOLVED_STYLE = f"fill:{GREY_FILL};fill-opacity:0.5"

# Plain-language definitions of the tiers, surfaced as native hover tooltips on
# the inset colour keys (and mirrored in the bar legends on index/problems.html).
TIER_TOOLTIPS = {
    "optimal": "Optimal: the proven optimal objective value has been reached. This "
               "includes a heuristic that attains the optimal value without proving "
               "optimality itself — e.g., when the optimum was already proven by a "
               "different method.",
    "best-known": "A solution matching the best-known objective value is known, "
                  "but it is not proven to be optimal.",
    "open": "No solution reaching the best-known value yet — either no feasible "
            "solution is known, or only worse ones.",
}

MAIN_DIMS = (720, 380)
INSET_DIMS = (340, 220)


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def _num(value):
    if value is None or value == "":
        return None
    try:
        n = float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None
    return n if math.isfinite(n) else None


def _esc(value) -> str:
    s = "" if value is None else str(value)
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _f1(x) -> str:
    return f"{x:.1f}"


def _tier_title(label) -> str:
    """`` title="…"`` attribute (with a leading space) explaining a tier, or ""."""
    tip = TIER_TOOLTIPS.get(str(label))
    return f' title="{_esc(tip)}"' if tip else ""


def _fmt_tick(power: int) -> str:
    """Axis tick label for 10**power — plain number in the readable range, else 1e±N."""
    if -2 <= power <= 4:
        v = 10 ** power
        return f"{int(round(v)):,}" if power >= 0 else f"{v:g}"
    return f"1e{power}"


def _log_ticks(p_lo: int, p_hi: int, max_ticks: int) -> list[int]:
    ticks = list(range(p_lo, p_hi + 1))
    if len(ticks) <= max_ticks:
        return ticks
    step = math.ceil(len(ticks) / max_ticks)
    return [t for i, t in enumerate(ticks) if i % step == 0 or i == len(ticks) - 1]


# --------------------------------------------------------------------------- #
# Point collection (join metrics.csv rows to per-instance optimal/quantum flags)
# --------------------------------------------------------------------------- #
def _metric_stem(model_name: str) -> str:
    """Canonical metrics.csv key for a model filename, matching ``load_lp_metrics``
    (strip compression + model extension, drop bqp_/uqo_, normalise the λ suffix)."""
    stem = canonical_name_from_filename(model_name or "")
    stem = re.sub(r"\.(lp|mps|qs)$", "", stem, flags=re.IGNORECASE)
    stem = stem.removeprefix("bqp_").removeprefix("uqo_")
    return normalize_portfolio_lambda(stem)


def _collect_points(entries, which: str) -> list[dict]:
    """One point per instance that has a positive (num_vars, density) metric.

    ``which`` selects the model family: "mip" → lp_files (column ``num_vars``),
    "qubo" → qs_files (column ``num_variables``). The join is on each instance's
    model-file stem (the authoritative key the metrics CSV is indexed by), with a
    fallback to the instance name for problems whose names already match.
    """
    kind = "lp" if which == "mip" else "qs"
    var_col = "num_vars" if which == "mip" else "num_variables"
    points: list[dict] = []

    for entry in entries:
        rows = (
            load_lp_metrics(entry["problem_dir"])
            if which == "mip"
            else load_qs_metrics(entry["problem_dir"])
        )
        if not rows:
            continue

        for inst in entry["instances"]:
            # Candidate keys: each model file of the right kind, then the
            # instance name itself (covers problems where they coincide).
            keys = [
                _metric_stem(m.get("name"))
                for m in (inst.get("models") or [])
                if m.get("kind") == kind
            ]
            nm = inst.get("name") or ""
            keys += [nm, normalize_portfolio_lambda(nm)]

            row = next((rows[k] for k in keys if k and k in rows), None)
            if row is None:
                continue

            nv = _num(row.get(var_col) or row.get("num_vars") or row.get("num_variables"))
            dens = _num(row.get("density"))
            if nv is None or dens is None or nv <= 0 or dens <= 0:
                continue
            # Per-paradigm tier (optimal·best_known·found·open). Fall back to the
            # legacy boolean flags for older inputs that predate the tier fields.
            ctier = inst.get("classical_tier")
            if ctier is None:
                ctier = "optimal" if inst.get("is_optimal") else (
                    "best_known" if inst.get("best_known") else "open"
                )
            qtier = inst.get("quantum_tier")
            if qtier is None:
                qtier = "optimal" if inst.get("quantum_optimal") else "open"
            points.append({
                "problem_id": entry["problem_id"],
                "problem_name": entry["problem_name"],
                "name": inst.get("name"),
                "num_vars": nv,
                "density": dens,
                "classical_tier": ctier,
                "quantum_tier": qtier,
            })

    return points


# --------------------------------------------------------------------------- #
# SVG scatter rendering
# --------------------------------------------------------------------------- #
def _scale(points):
    """Shared log-axis bounds (integer decade powers) for the main plot + insets."""
    xs = [p["num_vars"] for p in points]
    ys = [p["density"] for p in points]
    x_lo, x_hi = math.floor(math.log10(min(xs))), math.ceil(math.log10(max(xs)))
    y_lo, y_hi = math.floor(math.log10(min(ys))), math.ceil(math.log10(max(ys)))
    if x_lo == x_hi:
        x_hi += 1
    if y_lo == y_hi:
        y_hi += 1
    return x_lo, x_hi, y_lo, y_hi


def _scatter_svg(points, scale, dims, *, style_of, radius, svg_class, with_labels,
                 x_title=None, y_title=None, with_titles=True) -> str:
    x_lo, x_hi, y_lo, y_hi = scale
    w, h = dims
    if with_labels:
        m_l, m_r, m_t, m_b = 58, 16, 14, 44
    else:
        m_l = m_r = m_t = m_b = 10
    plot_w = w - m_l - m_r
    plot_h = h - m_t - m_b
    x_rng = max(1e-9, x_hi - x_lo)
    y_rng = max(1e-9, y_hi - y_lo)

    def x_px(v):
        return m_l + ((math.log10(v) - x_lo) / x_rng) * plot_w

    def y_px(v):
        return m_t + (1 - (math.log10(v) - y_lo) / y_rng) * plot_h

    xticks = _log_ticks(x_lo, x_hi, 8 if with_labels else 4)
    yticks = _log_ticks(y_lo, y_hi, 6 if with_labels else 4)

    grid = "".join(
        f'<line class="mip-grid-line" x1="{_f1(x_px(10 ** p))}" y1="{m_t}" '
        f'x2="{_f1(x_px(10 ** p))}" y2="{_f1(h - m_b)}" />'
        for p in xticks
    ) + "".join(
        f'<line class="mip-grid-line" x1="{m_l}" y1="{_f1(y_px(10 ** p))}" '
        f'x2="{_f1(w - m_r)}" y2="{_f1(y_px(10 ** p))}" />'
        for p in yticks
    )
    axes = (
        f'<line class="mip-axis-line" x1="{m_l}" y1="{_f1(h - m_b)}" '
        f'x2="{_f1(w - m_r)}" y2="{_f1(h - m_b)}" />'
        f'<line class="mip-axis-line" x1="{m_l}" y1="{m_t}" x2="{m_l}" y2="{_f1(h - m_b)}" />'
    )

    labels = ""
    if with_labels:
        labels += "".join(
            f'<text class="mip-axis-tick" text-anchor="middle" x="{_f1(x_px(10 ** p))}" '
            f'y="{_f1(h - m_b + 14)}">{_esc(_fmt_tick(p))}</text>'
            for p in xticks
        )
        labels += "".join(
            f'<text class="mip-axis-tick" text-anchor="end" x="{m_l - 6}" '
            f'y="{_f1(y_px(10 ** p) + 3)}">{_esc(_fmt_tick(p))}</text>'
            for p in yticks
        )
        if x_title:
            labels += (
                f'<text class="mip-axis-label" text-anchor="middle" '
                f'x="{_f1(m_l + plot_w / 2)}" y="{h - 6}">{_esc(x_title)}</text>'
            )
        if y_title:
            labels += (
                f'<text class="mip-axis-label" text-anchor="middle" '
                f'transform="translate(13 {_f1(m_t + plot_h / 2)}) rotate(-90)">{_esc(y_title)}</text>'
            )

    def _circle(p):
        c = (f'<circle class="landscape-dot" cx="{_f1(x_px(p["num_vars"]))}" '
             f'cy="{_f1(y_px(p["density"]))}" r="{radius}" style="{style_of(p)}"')
        # Tooltips only on the main scatter; the insets re-plot the same points,
        # so dropping their <title>s trims ~a third of the payload / DOM weight.
        if with_titles:
            return c + f'><title>{_esc(p["name"])} · {_esc(p["problem_name"])}</title></circle>'
        return c + " />"

    dots = "".join(_circle(p) for p in points)

    return (
        f'<svg class="{svg_class}" viewBox="0 0 {w} {h}" role="img" '
        f'preserveAspectRatio="xMidYMid meet">{grid}{axes}{labels}{dots}</svg>'
    )


def _main_style(p) -> str:
    fill, stroke = PROBLEM_COLORS.get(p["problem_id"], DEFAULT_COLOR)
    return f"fill:{fill};stroke:{stroke};stroke-width:0.5;fill-opacity:0.9"


def _inset_svg(points, scale, layers) -> str:
    """Inset scatter. ``layers`` is an ordered list of (predicate, style): points
    matching no layer are drawn grey first, then each layer paints on top."""
    def rank(p):
        for i, (pred, _style) in enumerate(layers):
            if pred(p):
                return i + 1
        return 0

    def style_of(p):
        for pred, style in layers:
            if pred(p):
                return style
        return UNSOLVED_STYLE

    ordered = sorted(points, key=rank)  # grey base first, highlighted layers on top
    return _scatter_svg(
        ordered, scale, INSET_DIMS,
        style_of=style_of, radius=2.2,
        svg_class="landscape-svg landscape-inset-svg", with_labels=False,
        with_titles=False,
    )


def _legend(points) -> str:
    seen: dict[str, str] = {}
    for p in points:
        seen.setdefault(p["problem_id"], p["problem_name"])
    items = "".join(
        f'<span class="ls-leg-item"><span class="ls-leg-dot" '
        f'style="background:{PROBLEM_COLORS.get(pid, DEFAULT_COLOR)[0]}"></span>'
        f'<strong>{_esc(pid)}</strong> {_esc(name)}</span>'
        for pid, name in sorted(seen.items())
    )
    return f'<div class="ls-legend">{items}</div>'


def _inset_block(svg, title, swatches) -> str:
    """One inset: scatter, then the title + colour key (list of (colour, label))
    BELOW it. Keeping the key below the SVG means a taller (wrapped) key never
    pushes its scatter down, so the two insets stay top-aligned."""
    keys = "".join(
        f'<span class="ls-inset-key"{_tier_title(label)}><span class="ls-leg-dot" '
        f'style="background:{colour}"></span>{_esc(label)}</span>'
        for colour, label in swatches
    )
    return (
        f'<figure class="landscape-inset">'
        f'{svg}'
        f'<figcaption><span class="ls-inset-title">{_esc(title)}</span>{keys}</figcaption>'
        f'</figure>'
    )


def _figure(points, caption) -> str:
    if not points:
        return ""
    scale = _scale(points)
    main = _scatter_svg(
        points, scale, MAIN_DIMS,
        style_of=_main_style, radius=3.2,
        svg_class="landscape-svg landscape-main", with_labels=True,
        x_title="Number of variables (log)", y_title="Density (log)",
    )
    # Both insets mirror the problem-card bars: optimal · best-known · open. "Open"
    # is the grey base drawn for points matching no layer — this now also absorbs
    # instances where a paradigm only found a worse feasible solution.
    classical = _inset_svg(points, scale, [
        (lambda p: p["classical_tier"] == "optimal", f"fill:{CLASSICAL_OPTIMAL_FILL}"),
        (lambda p: p["classical_tier"] == "best_known", f"fill:{CLASSICAL_BESTKNOWN_FILL}"),
    ])
    quantum = _inset_svg(points, scale, [
        (lambda p: p["quantum_tier"] == "optimal", f"fill:{QUANTUM_OPTIMAL_FILL}"),
        (lambda p: p["quantum_tier"] == "best_known", f"fill:{QUANTUM_BESTKNOWN_FILL}"),
    ])
    # Direct children of the card (no wrapping <figure>) so the cards can use a
    # CSS subgrid to align main / legend / insets / caption across both columns.
    return (
        main
        + _legend(points)
        + '<div class="landscape-insets">'
        + _inset_block(classical, "Classical", [
            (CLASSICAL_OPTIMAL_FILL, "optimal"), (CLASSICAL_BESTKNOWN_FILL, "best-known"),
            (GREY_FILL, "open"),
        ])
        + _inset_block(quantum, "Quantum", [
            (QUANTUM_OPTIMAL_FILL, "optimal"), (QUANTUM_BESTKNOWN_FILL, "best-known"),
            (GREY_FILL, "open"),
        ])
        + '</div>'
        + f'<div class="plot-cap">{_esc(caption)}</div>'
    )


_CAPTIONS = {
    "mip": "Mixed Integer Programming formulations — variables vs. density, with "
           "classical / quantum insets (optimal · best-known · open)",
    "qubo": "QUBO formulations — variables vs. density, with "
            "classical / quantum insets (optimal · best-known · open)",
}


def build_landscape(entries) -> dict:
    """Return prebaked figure HTML for the two home-page scatter plots.

    ``entries`` is a list of ``{problem_id, problem_name, problem_dir, instances}``
    where each instance carries ``name`` plus the per-paradigm ``classical_tier`` /
    ``quantum_tier`` (optimal·best_known·found·open; legacy ``is_optimal`` /
    ``best_known`` / ``quantum_optimal`` booleans are accepted as a fallback).
    Shape (consumed by ``renderLandscape`` in index.js)::

        {"mip": "<svg…><div…>…", "qubo": "…"}

    Each value is the run of card children (main SVG, legend, insets, caption);
    a model family with no joinable instances yields "" (the client shows an
    empty state).
    """
    return {
        "mip": _figure(_collect_points(entries, "mip"), _CAPTIONS["mip"]),
        "qubo": _figure(_collect_points(entries, "qubo"), _CAPTIONS["qubo"]),
    }
