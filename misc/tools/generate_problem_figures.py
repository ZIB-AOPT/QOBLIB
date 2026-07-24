#!/usr/bin/env python3
"""Generate per-problem SVG figures for the QOBLIB website.

Each problem page shows a small illustrative figure in the side panel. Four of
the problems (steiner, independentset, network, routing) shipped a PNG figure in
their repo ``misc/`` directory; those are recreated here as SVG in the site
colour scheme. The remaining six get a newly designed figure that resembles the
problem. All figures are *inline* SVG (emitted into ``problem_figures.js``) so
they reference the site's CSS custom properties and adapt to light/dark mode.

Run:  python3 misc/tools/generate_problem_figures.py
Output: website/assets/problem_figures.js
"""

from __future__ import annotations

import json
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "website" / "assets" / "problem_figures.js"

# --- palette (CSS variable references; resolve against the active theme) ------
TEAL = "var(--accent)"
TEAL2 = "var(--cat-classical)"
PURPLE = "var(--cat-quantum-hw)"
ORANGE = "var(--cat-quantum-sim)"
WARM = "var(--warm)"
GREEN = "var(--green)"
BLUE = "var(--blue)"
RED = "var(--red)"
GRID = "var(--border)"
EDGE = "var(--border-mid)"
MUTED = "var(--muted)"
FAINT = "var(--faint)"
INK = "var(--text)"
SURFACE = "var(--surface)"          # node halo: separates nodes from edges/each other
SURFACE2 = "var(--surface2)"


def svg(view_w, view_h, body, label):
    return (
        f'<svg viewBox="0 0 {view_w} {view_h}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{label}" class="pfig">{body}</svg>'
    )


def node(cx, cy, r, fill, stroke=SURFACE, sw=3):
    return (
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
        f'style="fill:{fill};stroke:{stroke};stroke-width:{sw}" />'
    )


def line(x1, y1, x2, y2, stroke, sw=2, opacity=1.0, extra=""):
    op = f";opacity:{opacity}" if opacity != 1.0 else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'style="stroke:{stroke};stroke-width:{sw};stroke-linecap:round{op}"{extra} />'
    )


def path(d, stroke=None, fill="none", sw=2, opacity=1.0, extra=""):
    s = f"fill:{fill}"
    if stroke:
        s += f";stroke:{stroke};stroke-width:{sw};stroke-linejoin:round;stroke-linecap:round"
    if opacity != 1.0:
        s += f";opacity:{opacity}"
    return f'<path d="{d}" style="{s}"{extra} />'


def polygon(pts, fill, stroke=None, opacity=1.0, sw=1.5):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    s = f"fill:{fill}"
    if stroke:
        s += f";stroke:{stroke};stroke-width:{sw};stroke-linejoin:round"
    if opacity != 1.0:
        s += f";opacity:{opacity}"
    return f'<polygon points="{p}" style="{s}" />'


def text(x, y, s, fill=MUTED, size=14, anchor="middle", extra_style=""):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'style="fill:{fill};font:{size}px var(--mono){(";" + extra_style) if extra_style else ""}">{s}</text>'
    )


def circle_layout(cx, cy, r, n, start_deg=-90, step_deg=None):
    step = step_deg if step_deg is not None else 360.0 / n
    pts = []
    for i in range(n):
        a = math.radians(start_deg + step * i)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# =============================================================================
# 07 — Maximum Independent Set  (recreate: wheel graph, alternating set chosen)
# =============================================================================
def fig_independentset():
    W, H = 320, 300
    c = (160, 150)
    outer = circle_layout(*c, 118, 6, start_deg=-90)
    nr = 27
    body = []
    edges = '<g>'
    # ring edges
    for i in range(6):
        a, b = outer[i], outer[(i + 1) % 6]
        edges += line(*a, *b, EDGE, 2.4)
    # spokes
    for p in outer:
        edges += line(*c, *p, EDGE, 2.4)
    edges += '</g>'
    body.append(edges)
    selected = {0, 2, 4}
    body.append(node(*c, nr, FAINT))  # centre, not selected
    for i, p in enumerate(outer):
        body.append(node(*p, nr, WARM if i in selected else FAINT))
    return svg(W, H, "".join(body), "Maximum independent set: chosen vertices have no shared edge")


# =============================================================================
# 08 — Network Design  (directed network where every node has in- and
# out-degree 2: a 2-regular circulant digraph i -> i+1, i -> i+2)
# =============================================================================
def fig_network():
    W, H = 320, 300
    n = 5
    pts = circle_layout(160, 150, 118, n, start_deg=-90)
    nr = 24
    marker = (
        '<defs><marker id="pf-arrow" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" style="fill:{TEAL}" /></marker></defs>'
    )
    body = [marker]

    def arrow(i, j, opacity):
        x1, y1 = pts[i]
        x2, y2 = pts[j]
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        sx, sy = x1 + ux * nr, y1 + uy * nr
        ex, ey = x2 - ux * (nr + 5), y2 - uy * (nr + 5)
        return line(sx, sy, ex, ey, TEAL, 2.4, opacity,
                    extra=' marker-end="url(#pf-arrow)"')

    edges = '<g>'
    for i in range(n):
        edges += arrow(i, (i + 1) % n, 0.85)   # out-edge to next   (ring)
        edges += arrow(i, (i + 2) % n, 0.5)    # out-edge to next+1 (chord)
    edges += '</g>'
    body.append(edges)
    for p in pts:
        body.append(node(*p, nr, WARM))
    return svg(W, H, "".join(body), "Network design: a directed network with in- and out-degree two at every node")


# =============================================================================
# 09 — Vehicle Routing  (recreate: central depot, three coloured routes)
# =============================================================================
def fig_routing():
    W, H = 330, 300
    depot = (165, 163)
    # Each route is one tour depot -> customers -> depot. The three vehicles fan
    # out into evenly spaced 120-degree sectors, and within a sector customers sit
    # at fixed angles/radii. This keeps every node well separated (no overlaps)
    # and each loop star-shaped around the depot (no backtracking).
    spread, r_side, r_mid = 35, 110, 130
    fans = [(TEAL, -90), (WARM, 30), (BLUE, 150)]
    routes = []
    for color, base in fans:
        custs = []
        for da, r in ((-spread, r_side), (0, r_mid), (spread, r_side)):
            a = math.radians(base + da)
            custs.append((depot[0] + r * math.cos(a), depot[1] + r * math.sin(a)))
        routes.append((color, custs))

    body = []
    for color, custs in routes:
        seq = [depot] + custs + [depot]
        d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in seq)
        body.append(path(d, stroke=color, sw=3))
    for color, custs in routes:
        for x, y in custs:
            body.append(node(x, y, 18, color))
    body.append(node(*depot, 23, INK))   # depot = neutral hub anchoring all routes
    return svg(W, H, "".join(body), "Vehicle routing: one tour per vehicle from a central depot")


# =============================================================================
# 04 — Steiner Tree Packing  (VLSI wire routing: edge-disjoint orthogonal
# Steiner trees connecting each net's terminals on a routing grid)
# =============================================================================
def fig_steiner():
    W, H = 344, 344
    C, R = 6, 6
    cell = 44
    ox, oy = 40, 40

    def G(c, r):
        return (ox + c * cell, oy + r * cell)

    body = []
    # routing grid
    for r in range(R + 1):
        body.append(line(*G(0, r), *G(C, r), GRID, 1.2))
    for c in range(C + 1):
        body.append(line(*G(c, 0), *G(c, R), GRID, 1.2))

    # Three nets, each a Steiner tree of axis-aligned strokes that branch to reach
    # all of its terminals. The trees are edge-disjoint and never cross — that is
    # the "packing" constraint. (col, row) lattice coordinates.
    nets = [
        (TEAL, [[(1, 0), (1, 1), (5, 1)], [(3, 1), (3, 3)]], [(1, 0), (5, 1), (3, 3)]),
        (WARM, [[(5, 2), (5, 5), (6, 5)], [(5, 5), (3, 5), (3, 6)]], [(5, 2), (6, 5), (3, 6)]),
        (BLUE, [[(0, 4), (2, 4), (2, 3)], [(2, 4), (2, 6)]], [(0, 4), (2, 3), (2, 6)]),
    ]
    for color, strokes, _ in nets:
        for stroke in strokes:
            pts = [G(c, r) for c, r in stroke]
            d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
            body.append(path(d, stroke=color, sw=4.5))
    for color, _, terms in nets:
        for c, r in terms:
            body.append(node(*G(c, r), 8.5, color, sw=2.5))
    return svg(W, H, "".join(body), "Steiner tree packing: edge-disjoint orthogonal trees routing nets on a grid")


# =============================================================================
# 01 — Market Split  (equality constraints = hyperplanes cutting the Boolean
# lattice; feasible 0/1 points lie on their intersection)
# =============================================================================
def fig_marketsplit():
    W, H = 320, 280
    S, ddx, ddy = 122, 70, -50
    ox, oy = 78, 214

    def V(x, y, z):
        return (ox + x * S + z * ddx, oy - y * S + z * ddy)

    verts = {(x, y, z): V(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)}
    cube_edges = [
        ((0, 0, 0), (1, 0, 0)), ((1, 0, 0), (1, 1, 0)), ((1, 1, 0), (0, 1, 0)), ((0, 1, 0), (0, 0, 0)),
        ((0, 0, 1), (1, 0, 1)), ((1, 0, 1), (1, 1, 1)), ((1, 1, 1), (0, 1, 1)), ((0, 1, 1), (0, 0, 1)),
        ((0, 0, 0), (0, 0, 1)), ((1, 0, 0), (1, 0, 1)), ((1, 1, 0), (1, 1, 1)), ((0, 1, 0), (0, 1, 1)),
    ]
    body = []
    # Boolean lattice {0,1}^3 (hypercube graph)
    body.append('<g>')
    for a, b in cube_edges:
        body.append(line(*verts[a], *verts[b], GRID, 1.4))
    body.append('</g>')
    # Two equality constraints, drawn as the hyperplanes they define, slicing the
    # cube. Plane A: x+y=1   Plane B: y+z=1.  They intersect along x=z, y=1-x.
    plane_a = [verts[(1, 0, 0)], verts[(1, 0, 1)], verts[(0, 1, 1)], verts[(0, 1, 0)]]
    plane_b = [verts[(1, 1, 0)], verts[(1, 0, 1)], verts[(0, 0, 1)], verts[(0, 1, 0)]]
    body.append(polygon(plane_a, TEAL, TEAL, 0.20, 1.6))
    body.append(polygon(plane_b, BLUE, BLUE, 0.22, 1.6))
    # intersection line of the two hyperplanes (passes through 010 and 101)
    feasible = [(0, 1, 0), (1, 0, 1)]
    body.append(line(*verts[feasible[0]], *verts[feasible[1]], WARM, 2.6))
    # lattice vertices; the two on the intersection are the feasible solutions
    for key, p in verts.items():
        if key in feasible:
            body.append(node(*p, 10, WARM, sw=2.5))
        else:
            body.append(node(*p, 6.5, FAINT, sw=2))
    body.append(text(150, 24, "Ax = b  on  {0,1}ⁿ", fill=FAINT, size=14))
    return svg(W, H, "".join(body), "Market split: equality hyperplanes intersecting the Boolean lattice")


# =============================================================================
# 02 — LABS  (spin sequence + low autocorrelation sidelobes)
# =============================================================================
def fig_labs():
    W, H = 320, 230
    # Barker sequence of length 11: a genuine low-autocorrelation ±1 sequence
    # (all off-peak sidelobes are 0 or -1, i.e. |C_k| <= 1).
    seq = [1, 1, 1, -1, -1, -1, 1, -1, -1, 1, -1]
    n = len(seq)
    # aperiodic autocorrelations  C_k = sum_i s_i * s_{i+k}
    acf = [sum(seq[i] * seq[i + k] for i in range(n - k)) for k in range(1, n)]

    body = []
    x0, dxs, yc = 28, 26, 60
    for i, s in enumerate(seq):
        x = x0 + i * dxs
        up = s == 1                         # +1 -> up arrow (teal), -1 -> down (warm)
        color = TEAL if up else WARM
        body.append(node(x, yc, 11, color, sw=2))
        tip = yc - 6 if up else yc + 6
        base_y = yc + 6 if up else yc - 6
        wing = 4 if up else -4              # chevron wings point back toward the tail
        body.append(line(x, base_y, x, tip, SURFACE, 2))
        body.append(path(f"M {x-3:.0f} {tip+wing:.0f} L {x:.0f} {tip:.0f} L {x+3:.0f} {tip+wing:.0f}",
                         stroke=SURFACE, sw=2))
    body.append(text(160, 98, "±1 sequence  (length 11)", fill=FAINT, size=13))

    # autocorrelation sidelobes C_k for k = 1..n-1 (computed above)
    base = 168
    scale = 17                              # px per unit; |C_k| <= 1 here -> short bars
    body.append(line(28, base, 292, base, EDGE, 1.4))
    bx = 44
    dxb = (292 - 2 * (bx - 28)) / (len(acf) - 1)
    for i, v in enumerate(acf):
        x = bx + i * dxb
        if v == 0:
            body.append(node(x, base, 2.4, FAINT, sw=0))   # mark the zero sidelobes
        else:
            body.append(line(x, base, x, base - v * scale, TEAL, 5))
    body.append(text(160, 216, "autocorrelation Cₖ   (max |Cₖ| = 1)", fill=FAINT, size=13))
    return svg(W, H, "".join(body), "LABS: a Barker-11 sequence and its low autocorrelation sidelobes")


# =============================================================================
# 03 — Birkhoff decomposition  (D = sum of permutation matrices)
# =============================================================================
def fig_birkhoff():
    W, H = 380, 150
    cell = 22
    g = 3
    size = cell * g
    body = []

    def grid_at(gx, gy, dots, color, faint_all=False):
        out = [f'<g style="fill:none;stroke:{GRID};stroke-width:1.1">']
        out.append(f'<rect x="{gx}" y="{gy}" width="{size}" height="{size}" rx="3" />')
        for k in range(1, g):
            out.append(line(gx + k * cell, gy, gx + k * cell, gy + size, GRID, 1.1))
            out.append(line(gx, gy + k * cell, gx + size, gy + k * cell, GRID, 1.1))
        out.append('</g>')
        if faint_all:
            for r in range(g):
                for cc in range(g):
                    cx = gx + cc * cell + cell / 2
                    cy = gy + r * cell + cell / 2
                    out.append(f'<rect x="{cx-7:.1f}" y="{cy-7:.1f}" width="14" height="14" '
                               f'rx="2" style="fill:{MUTED};opacity:0.33" />')
        for (r, cc) in dots:
            cx = gx + cc * cell + cell / 2
            cy = gy + r * cell + cell / 2
            out.append(node(cx, cy, 6.5, color, sw=2))
        return "".join(out)

    def coef_label(cx, cy, idx):
        # "1/3 Pₖ": a stacked fraction next to the permutation name
        fx = cx - 13
        out = [
            text(fx, cy - 2, "1", MUTED, 12),
            line(fx - 5, cy + 1, fx + 5, cy + 1, MUTED, 1.1),
            text(fx, cy + 12, "3", MUTED, 12),
            f'<text x="{cx+2:.1f}" y="{cy+8:.1f}" style="fill:{MUTED};font:16px var(--sans)">'
            f'P<tspan dy="3" style="font-size:10px">{idx}</tspan></text>',
        ]
        return "".join(out)

    gy = 26
    perms = [
        ([(0, 0), (1, 1), (2, 2)], TEAL),
        ([(0, 1), (1, 2), (2, 0)], WARM),
        ([(0, 2), (1, 0), (2, 1)], BLUE),
    ]
    cy_lbl = gy + size + 20
    body.append(grid_at(12, gy, [], MUTED, faint_all=True))
    body.append(f'<text x="{12 + size / 2:.1f}" y="{cy_lbl + 4:.1f}" text-anchor="middle" '
                f'style="fill:{MUTED};font:16px var(--sans)">D</text>')
    x = 12 + size
    body.append(text(x + 13, gy + size / 2 + 5, "=", fill=FAINT, size=18))
    x += 26
    for idx, (dots, color) in enumerate(perms):
        body.append(grid_at(x, gy, dots, color))
        body.append(coef_label(x + size / 2, cy_lbl, idx + 1))
        x += size
        if idx < len(perms) - 1:
            body.append(text(x + 12, gy + size / 2 + 5, "+", fill=FAINT, size=18))
            x += 24
    return svg(W, H, "".join(body), "Birkhoff decomposition: a doubly stochastic matrix as a sum of permutation matrices")


# =============================================================================
# 05 — Sports Tournament Scheduling  (round-robin pairings on a circle)
# =============================================================================
def fig_sports():
    W, H = 300, 300
    pts = circle_layout(150, 150, 110, 6, start_deg=-90)
    nr = 24
    body = []
    # faint full round-robin (all pairings, over the whole tournament)
    faint = '<g>'
    for i in range(6):
        for j in range(i + 1, 6):
            faint += line(*pts[i], *pts[j], EDGE, 1.4, 0.4)
    faint += '</g>'
    body.append(faint)
    # one round's matching highlighted
    matches = [(0, 1), (2, 3), (4, 5)]
    for a, b in matches:
        body.append(line(*pts[a], *pts[b], WARM, 3.6))
    # rotation arrow (rounds advance by rotating teams)
    body.append('<defs><marker id="pf-rot" viewBox="0 0 10 10" refX="6" refY="5" '
                'markerWidth="6" markerHeight="6" orient="auto">'
                f'<path d="M0,0 L10,5 L0,10 z" style="fill:{FAINT}" /></marker></defs>')
    body.append(path("M 132 150 A 18 18 0 1 1 150 168", stroke=FAINT, sw=1.8,
                     extra=' marker-end="url(#pf-rot)"'))
    for p in pts:
        body.append(node(*p, nr, TEAL))   # teams share the brand teal; the round stands out in warm
    return svg(W, H, "".join(body), "Sports scheduling: round-robin pairings rotating across rounds")


# =============================================================================
# 06 — Portfolio Optimization  (efficient frontier with a chosen portfolio)
# =============================================================================
def fig_portfolio():
    W, H = 320, 260
    ax, ay0, ay1, ax1 = 48, 214, 32, 292
    body = []
    body.append(line(ax, ay0, ax1, ay0, EDGE, 1.8))     # x axis (risk)
    body.append(line(ax, ay0, ax, ay1, EDGE, 1.8))      # y axis (return)
    # asset cloud (sub-optimal points)
    cloud = [(112, 172), (150, 150), (182, 170), (138, 188), (206, 122),
             (232, 142), (196, 158), (168, 132), (224, 178), (120, 150)]
    for x, y in cloud:
        body.append(node(x, y, 6.5, FAINT, sw=1.5))
    # efficient frontier
    body.append(path("M 70 192 C 96 120 168 72 274 58", stroke=TEAL, sw=3.4))
    # chosen portfolio on the frontier
    body.append(node(176, 92, 9, WARM))
    body.append(f'<circle cx="176" cy="92" r="15" style="fill:none;stroke:{WARM};'
                'stroke-width:1.6;opacity:0.55" />')
    body.append(text(280, ay0 + 16, "risk", fill=FAINT, size=13, anchor="end"))
    body.append(f'<text x="{ax-14}" y="46" text-anchor="middle" '
                f'style="fill:{FAINT};font:13px var(--mono)" transform="rotate(-90 {ax-14} 46)">return</text>')
    return svg(W, H, "".join(body), "Portfolio optimization: the efficient frontier and a chosen portfolio")


# =============================================================================
# 10 — Topology Design  (a small degree/diameter solution: the Petersen graph,
# 10 nodes, every node degree 3, diameter 2 — optimal for (3, 2))
# =============================================================================
def fig_topology():
    W, H = 300, 300
    n = 5
    outer = circle_layout(150, 150, 120, n, start_deg=-90)
    inner = circle_layout(150, 150, 60, n, start_deg=-90)
    nr = 16
    body = []
    edges = '<g>'
    for i in range(n):
        edges += line(*outer[i], *outer[(i + 1) % n], EDGE, 2.0)     # outer 5-cycle
        edges += line(*inner[i], *inner[(i + 2) % n], EDGE, 2.0)     # inner pentagram
        edges += line(*outer[i], *inner[i], EDGE, 2.0)               # spokes
    edges += '</g>'
    body.append(edges)
    for p in outer + inner:
        body.append(node(*p, nr, TEAL))
    return svg(W, H, "".join(body), "Topology design: a small degree-3, diameter-2 graph (the Petersen graph)")


FIGURES = {
    "marketsplit": fig_marketsplit,
    "labs": fig_labs,
    "birkhoff": fig_birkhoff,
    "steiner": fig_steiner,
    "sports": fig_sports,
    "portfolio": fig_portfolio,
    "independentset": fig_independentset,
    "network": fig_network,
    "routing": fig_routing,
    "topology": fig_topology,
}


def main():
    figures = {slug: fn() for slug, fn in FIGURES.items()}
    payload = json.dumps(figures, ensure_ascii=False, indent=2)
    banner = (
        "// AUTO-GENERATED by misc/tools/generate_problem_figures.py — do not edit by hand.\n"
        "// Per-problem illustrative SVGs (inline so they use the site's CSS theme\n"
        "// variables and adapt to light/dark mode). Regenerate after edits.\n"
    )
    OUT.write_text(f"{banner}window.QOBLIB_PROBLEM_FIGURES = {payload};\n", encoding="utf-8")
    print(f"Wrote {OUT}  ({len(figures)} figures)")


if __name__ == "__main__":
    main()
