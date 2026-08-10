"use strict";

const {
    esc: qEsc,
    safeHref: qSafeHref,
    fmtNum: qFmtNum,
    fmtInt: qFmtInt,
    fmtMaybeNum: qFmtMaybeNum,
    fmtText: qFmtText,
    parseDate: qParseDate,
    fmtDate: qFmtDate,
    niceLinearTicks: qNiceLinearTicks,
    niceLogAxis: qNiceLogAxis,
    loadProblemData: qLoadProblemData,
    loadProblemTimeSeries: qLoadProblemTimeSeries,
    instanceUrl: qInstanceUrl,
    submissionUrl: qSubmissionUrl,
    problemUrl: qProblemUrl,
    statusPill: qStatusPill,
    detailModelList: qDetailModelList,
    renderMath: qRenderMath,
    showError: qShowError,
    enableTableSorting: qEnableTableSorting,
    initCommon: qInitCommon,
    classifySubmission: qClassify,
    SUBMISSION_CATEGORIES: qCATS,
    setPageMeta: qSetPageMeta,
    enhanceFigures: qEnhanceFigures,
} = window.QOBLIB;

// ---------------------------------------------------------------------------
// Submission-history plots, each split into the three compute paradigms:
// real quantum hardware, simulated quantum, and classical.
// ---------------------------------------------------------------------------

const CAT_ORDER = ["classical", "quantum_sim", "quantum_hw"];

function catOf(s) {
    return (s && s.category) || qClassify(s);
}

function catBadge(cat) {
    const c = qCATS[cat] || qCATS.classical;
    return `<span class="cat-badge"><span class="cat-dot" style="background:${c.color}"></span>${qEsc(c.short)}</span>`;
}

function pNum(v) {
    if (v == null || v === "") return NaN;
    return Number(String(v).replace(/,/g, "").trim());
}

function pDate(v) {
    return qParseDate(v);
}

function isInfeasibleSub(s) {
    const nf = pNum(s.n_feasible);
    return Number.isFinite(nf) && nf === 0;
}

// Palette matching charts.py CACTUS_PALETTE — one color per submission.
const TS_PALETTE = ["#2f6db0","#c0504d","#9bbb59","#8064a2","#4bacc6","#f79646","#7f6084","#5a7d2c"];

function fmtTick(v) {
    const a = Math.abs(v);
    if (a !== 0 && (a >= 1e5 || a < 1e-3)) return v.toExponential(1);
    // Whole numbers never show a decimal part (integer quantities stay integer).
    if (Number.isInteger(v)) return v.toLocaleString();
    const dp = a < 10 ? 3 : a < 1000 ? 1 : 0;
    return Number(v.toFixed(dp)).toLocaleString();
}

function fmtSec(v) {
    const a = Math.abs(v);
    if (a !== 0 && (a >= 1e5 || a < 1e-3)) return v.toExponential(1) + " s";
    const dp = a < 0.01 ? 3 : a < 10 ? 2 : a < 1000 ? 1 : 0;
    return Number(v.toFixed(dp)).toLocaleString() + " s";
}

// Derive a short display label from a submission's _source_dir field,
// mirroring _submission_method in charts.py: strip the date prefix and author suffix.
function tsLabel(sub) {
    const d = sub._source_dir || "";
    const m = d.match(/^\d{6,8}_(.+)_([^_]+)$/);
    return m ? m[1] : (d || sub.submitter || "Unknown");
}

// An "approximation" series is one whose points carry a third element: the
// approximation residual (for Birkhoff's incremental BirkhoffPlus method, the
// squared normalized Frobenius norm ‖D − Σλᵢ·Pᵢ‖²_F / ‖D‖²_F). For these the
// "Incumbent" value is the NUMBER OF PERMUTATION MATRICES used so far — a rising
// count, not a feasible objective — so they are plotted on a dedicated
// matrices-vs-residual chart (buildApproxChart) rather than the objective-over-
// time axis, where the rise would read as a minimization going the wrong way.
function seriesIsAccumulation(s) {
    return (s.runs || []).some((run) => run.some((p) => p.length >= 3 && Number.isFinite(p[2])));
}

// Build a step-function SVG for objective time series data.
// series: [{label, color, runs: [[[t,v],...], ...]}]
// bkv:    best-known value in the problem's canonical direction (or null)
// Each run is drawn faintly; the best-run envelope (min or max incumbent at each
// time point across all runs) is drawn as a solid line.
function buildTsChart(series, minimize, bkv) {
    const yTitleTxt = "incumbent";
    const W = 720, H = 300;
    const m = { t: 16, r: 36, b: 44, l: 66 };  // r=36 leaves room for "BKV" tag

    // Collect all raw points for sign-detection and axis range.
    const allPts = series.flatMap((s) => s.runs.flat());
    if (!allPts.length) return "";

    // Sign correction: an objective time series must be monotone in the problem's
    // optimization direction (non-decreasing for maximization, non-increasing for
    // minimization). If a run moves strictly the wrong way throughout, the submitter
    // stored the negated QUBO objective — negate it back. Checked per run so a mixed
    // series is handled entry by entry. A single-point run has no direction to check
    // and is left untouched. (Accumulation/approximation series never reach here —
    // they are split off to buildApproxChart before this is called.)
    const fixRun = (run) => {
        if (run.length < 2) return run;
        // Count steps in each direction (ignore flat steps).
        let nRight = 0, nWrong = 0;
        for (let i = 1; i < run.length; i++) {
            const delta = run[i][1] - run[i - 1][1];
            if (delta === 0) continue;
            if (minimize ? delta < 0 : delta > 0) nRight++;
            else nWrong++;
        }
        // Only invert when every non-flat step goes the wrong way.
        return (nWrong > 0 && nRight === 0)
            ? run.map((p) => [p[0], -p[1]])
            : run;
    };
    series = series.map((s) => ({ ...s, runs: s.runs.map(fixRun) }));

    const allT = allPts.map((p) => p[0]);
    const allV = series.flatMap((s) => s.runs.flat()).map((p) => p[1]);
    let tMin = Math.min(...allT), tMax = Math.max(...allT);
    if (tMin === tMax) { tMin = Math.max(0, tMin - 1); tMax += 1; }

    // Use log time axis when the range spans more than 2 orders of magnitude.
    const tPos = allT.filter((t) => t > 0);
    const useLogT = tPos.length > 0 && tMax / (Math.min(...tPos) || 1) > 100;
    const tFloor = tPos.length ? Math.min(...tPos) : 1e-3;
    const clampT = (t) => Math.max(t, tFloor);

    // On a log axis, tLo/tHi are the log10 endpoints, snapped to nice 1-2-5 bounds
    // (so a time range ending at 16 s stops at 20, not the next decade 100).
    let tLo, tHi;
    let tAxis = null;
    if (useLogT) {
        tAxis = qNiceLogAxis(clampT(tMin), clampT(tMax), { maxMajor: 6 });
        // Pad ~5% beyond the nice bounds so points sit inset from the side frames.
        const span = (Math.log10(tAxis.hi) - Math.log10(tAxis.lo)) || 1;
        tLo = Math.log10(tAxis.lo) - span * 0.05;
        tHi = Math.log10(tAxis.hi) + span * 0.05;
    } else {
        const pad = (tMax - tMin || 1) * 0.08;
        tLo = tMin - pad; tHi = tMax + pad;
    }

    // Y-axis: span only the data range, extended just enough to fit bkv.
    // The "best" end of the axis is always bkv (if provided); the "worst" end
    // is the worst incumbent seen in the data plus a small pad.
    const hasBkv = Number.isFinite(bkv);
    let vDataMin = Math.min(...allV), vDataMax = Math.max(...allV);
    // If bkv is outside the data range, stretch to include it.
    if (hasBkv) {
        if (minimize) vDataMin = Math.min(vDataMin, bkv);
        else          vDataMax = Math.max(vDataMax, bkv);
    }
    const vSpan = (vDataMax - vDataMin) || Math.abs(vDataMax) || 1;
    let vMin = vDataMin - vSpan * 0.05;
    let vMax = vDataMax + vSpan * 0.05;
    // Pin the bkv end of the axis exactly to bkv (with a tiny clearance so the
    // reference line isn't clipped), overriding the small pad above.
    if (hasBkv) {
        if (minimize) vMin = bkv - vSpan * 0.02;
        else          vMax = bkv + vSpan * 0.02;
    }

    const yPx = (v) => H - m.b - (H - m.t - m.b) * ((v - vMin) / ((vMax - vMin) || 1));
    const xPx = (t) => {
        const v = useLogT ? Math.log10(clampT(t)) : t;
        return m.l + (W - m.l - m.r) * ((v - tLo) / ((tHi - tLo) || 1));
    };

    // Y-ticks: nice 1/2/5×10ⁿ steps over the data range (integer-forced when every
    // incumbent value is a whole number, so an integer objective never shows
    // fractional ticks) + bkv labeled distinctly. Data ticks colliding with bkv
    // (within 5% of span) are dropped so the two labels never overlap.
    const yIsInteger = allV.every((v) => Number.isInteger(v)) && (!hasBkv || Number.isInteger(bkv));
    const yDataTicks = qNiceLinearTicks(vDataMin, vDataMax, { integer: yIsInteger, target: 4 });
    const bkvTol = vSpan * 0.05;
    const yticks = hasBkv
        ? yDataTicks.filter((v) => Math.abs(v - bkv) > bkvTol)
        : yDataTicks;

    // X-ticks: nice 1-2-5 log ticks (+ faint minor guides) on a log time axis;
    // nice linear steps otherwise. Time is in seconds, so not integer-forced.
    let xticks;
    let xMinorTicks = [];
    if (useLogT) {
        xticks = tAxis.major;
        xMinorTicks = tAxis.minor;
        if (!xticks.length) xticks = [tAxis.lo, tAxis.hi];
    } else {
        xticks = qNiceLinearTicks(tMin, tMax, { integer: false, target: 5 })
            .filter((v) => v >= tLo - 1e-9 && v <= tHi + 1e-9);
        if (!xticks.length) xticks = [tMin, tMax];
    }

    const f1 = (x) => x.toFixed(1);
    const gridMinor = xMinorTicks.map((v) =>
        `<line class="conv-grid-minor" x1="${f1(xPx(v))}" y1="${m.t}" x2="${f1(xPx(v))}" y2="${H - m.b}" />`
    ).join("");
    const grid = gridMinor + yticks.map((v) =>
        `<line class="conv-grid" x1="${m.l}" y1="${f1(yPx(v))}" x2="${W - m.r}" y2="${f1(yPx(v))}" />`
    ).join("");
    const axes =
        `<line class="conv-axis-line" x1="${m.l}" y1="${m.t}" x2="${m.l}" y2="${H - m.b}" />` +
        `<line class="conv-axis-line" x1="${m.l}" y1="${H - m.b}" x2="${W - m.r}" y2="${H - m.b}" />`;
    const yLabels = yticks.map((v) =>
        `<text class="conv-tick" text-anchor="end" x="${m.l - 8}" y="${f1(yPx(v) + 3)}">${qEsc(fmtTick(v))}</text>`
    ).join("");
    // Best-known reference line and its y-label (rendered on top of ordinary ticks).
    const bkvEl = hasBkv ? (() => {
        const py = f1(yPx(bkv));
        const line = `<line class="conv-grid" x1="${m.l}" y1="${py}" x2="${W - m.r}" y2="${py}" stroke-dasharray="6 3" style="stroke:var(--accent);stroke-opacity:0.7" />`;
        const label = `<text class="conv-tick" text-anchor="end" x="${m.l - 8}" y="${f1(yPx(bkv) + 3)}" style="fill:var(--accent);font-weight:600">${qEsc(fmtTick(bkv))}</text>`;
        const tag = `<text class="conv-axis-title" text-anchor="start" x="${W - m.r + 3}" y="${f1(yPx(bkv) + 3)}" style="fill:var(--accent)">BKV</text>`;
        return line + label + tag;
    })() : "";
    const xLabels = xticks.map((t) =>
        `<text class="conv-tick" text-anchor="middle" x="${f1(xPx(t))}" y="${H - m.b + 16}">${qEsc(fmtSec(t))}</text>`
    ).join("");
    const xTitle = `<text class="conv-axis-title" text-anchor="middle" x="${f1((m.l + W - m.r) / 2)}" y="${H - 4}">time${useLogT ? " (s, log)" : " (s)"} →</text>`;
    const yCy = f1((m.t + H - m.b) / 2);
    const yTitle = `<text class="conv-axis-title" text-anchor="middle" transform="rotate(-90 14 ${yCy})" x="14" y="${yCy}">${qEsc(yTitleTxt)}</text>`;

    // Draw each submission's runs.
    const parts = series.map((s) => {
        if (!s.runs.length) return "";

        // Build the best-run envelope: at every incumbent change across all runs,
        // track the best value seen so far across runs.
        const events = s.runs.flatMap((run) => run.map(([t, v]) => ({ t, v })));
        events.sort((a, b) => a.t - b.t);
        const env = [];
        let best = null;
        for (const { t, v } of events) {
            if (best === null || (minimize ? v < best : v > best)) {
                best = v;
                env.push([t, best]);
            }
        }

        // Faint individual run lines — only rendered when there are multiple runs,
        // because with a single run the envelope and the run are identical.
        const runLines = s.runs.length > 1 ? s.runs.map((run) => {
            if (run.length < 1) return "";
            const sorted = run.slice().sort((a, b) => a[0] - b[0]);
            let d = `M ${f1(xPx(sorted[0][0]))} ${f1(yPx(sorted[0][1]))}`;
            for (let i = 1; i < sorted.length; i++) {
                // Step: horizontal then vertical.
                d += ` L ${f1(xPx(sorted[i][0]))} ${f1(yPx(sorted[i - 1][1]))}`;
                d += ` L ${f1(xPx(sorted[i][0]))} ${f1(yPx(sorted[i][1]))}`;
            }
            // Extend to right edge.
            d += ` L ${f1(xPx(tMax))} ${f1(yPx(sorted[sorted.length - 1][1]))}`;
            return `<path d="${d}" fill="none" style="stroke:${s.color}" stroke-width="1" stroke-opacity="0.3" stroke-dasharray="3 2" />`;
        }).join("") : "";

        // Bold envelope line.
        let envPath = "";
        if (env.length) {
            let d = `M ${f1(xPx(env[0][0]))} ${f1(yPx(env[0][1]))}`;
            for (let i = 1; i < env.length; i++) {
                d += ` L ${f1(xPx(env[i][0]))} ${f1(yPx(env[i - 1][1]))}`;
                d += ` L ${f1(xPx(env[i][0]))} ${f1(yPx(env[i][1]))}`;
            }
            d += ` L ${f1(xPx(tMax))} ${f1(yPx(env[env.length - 1][1]))}`;

            // Dots at each improvement. A larger transparent circle over each dot
            // widens the hover target (the native <title> tooltip fires on it), so
            // the r=3 dots are no longer pixel-perfect to hit.
            const dots = env.map(([t, v]) => {
                const cx = f1(xPx(t));
                const cy = f1(yPx(v));
                return (
                    `<circle cx="${cx}" cy="${cy}" r="3" style="fill:${s.color}" />` +
                    `<circle cx="${cx}" cy="${cy}" r="10" fill="transparent" style="cursor:pointer">` +
                    `<title>${qEsc(s.label)} · ${qEsc(fmtSec(t))} · ${qEsc(fmtTick(v))}</title></circle>`
                );
            }).join("");

            envPath =
                `<path d="${d}" fill="none" style="stroke:${s.color}" stroke-width="2" stroke-linejoin="round" />` +
                dots;
        }

        return `<g data-series="${qEsc(s.key)}">${runLines}${envPath}</g>`;
    }).join("");

    return `<svg class="conv-svg" viewBox="0 0 ${W} ${H}" role="img" preserveAspectRatio="xMidYMid meet">${grid}${bkvEl}${axes}${yLabels}${xLabels}${xTitle}${yTitle}${parts}</svg>`;
}

// Approximation-progress chart for incremental methods (Birkhoff's BirkhoffPlus):
// x = number of permutation matrices used (integer), y = the squared normalized
// Frobenius reconstruction residual ‖D − Σλᵢ·Pᵢ‖²_F / ‖D‖²_F (the point's 3rd
// element), plotted verbatim on a linear axis anchored at 0. This is NOT a
// time series — it shows how quickly the decomposition converges as matrices are
// added, so more-matrices/lower-residual (lower-left of the tail) is better.
// series: [{label, color, runs: [[t, nMatrices, error], ...]}]
function buildApproxChart(series) {
    const W = 720, H = 300;
    const m = { t: 16, r: 18, b: 44, l: 66 };

    // Each run → [nMatrices, error] points (2nd and 3rd elements), sorted by count.
    const norm = series.map((s) => ({
        ...s,
        curves: (s.runs || [])
            .map((run) =>
                run
                    .filter((p) => p.length >= 3 && Number.isFinite(p[1]) && Number.isFinite(p[2]))
                    .map((p) => [p[1], p[2]])
                    .sort((a, b) => a[0] - b[0]),
            )
            .filter((c) => c.length),
    }));
    const allPts = norm.flatMap((s) => s.curves.flat());
    if (!allPts.length) return "";

    const xs = allPts.map((p) => p[0]);
    const ys = allPts.map((p) => p[1]);
    let xMin = Math.min(...xs), xMax = Math.max(...xs);
    if (xMin === xMax) { xMin = Math.max(0, xMin - 1); xMax += 1; }
    // Residual is ≥ 0 and its meaningful floor is exact reconstruction (0), so the
    // y-axis is anchored at 0 with a small headroom pad above the largest residual.
    const yMax = Math.max(...ys, 0);
    const yLo = 0;
    const yHi = yMax > 0 ? yMax * 1.05 : 1;

    const xPad = (xMax - xMin || 1) * 0.05;
    const xLo = Math.max(0, xMin - xPad), xHi = xMax + xPad;
    const xPx = (v) => m.l + (W - m.l - m.r) * ((v - xLo) / ((xHi - xLo) || 1));
    const yPx = (v) => H - m.b - (H - m.t - m.b) * ((v - yLo) / ((yHi - yLo) || 1));

    const f1 = (x) => x.toFixed(1);
    // X-ticks: integer matrix counts. Y-ticks: nice linear residual steps.
    const xticks = qNiceLinearTicks(xMin, xMax, { integer: true, target: 6 })
        .filter((v) => v >= xLo - 1e-9 && v <= xHi + 1e-9);
    const yticks = qNiceLinearTicks(yLo, yHi, { integer: false, target: 5 })
        .filter((v) => v >= yLo - 1e-9 && v <= yHi + 1e-9);

    const grid = yticks.map((v) =>
        `<line class="conv-grid" x1="${m.l}" y1="${f1(yPx(v))}" x2="${W - m.r}" y2="${f1(yPx(v))}" />`
    ).join("");
    const axes =
        `<line class="conv-axis-line" x1="${m.l}" y1="${m.t}" x2="${m.l}" y2="${H - m.b}" />` +
        `<line class="conv-axis-line" x1="${m.l}" y1="${H - m.b}" x2="${W - m.r}" y2="${H - m.b}" />`;
    const yLabels = yticks.map((v) =>
        `<text class="conv-tick" text-anchor="end" x="${m.l - 8}" y="${f1(yPx(v) + 3)}">${qEsc(fmtTick(v))}</text>`
    ).join("");
    const xLabels = xticks.map((v) =>
        `<text class="conv-tick" text-anchor="middle" x="${f1(xPx(v))}" y="${H - m.b + 16}">${qEsc(fmtTick(v))}</text>`
    ).join("");
    const xTitle = `<text class="conv-axis-title" text-anchor="middle" x="${f1((m.l + W - m.r) / 2)}" y="${H - 4}">number of permutation matrices →</text>`;
    const yCy = f1((m.t + H - m.b) / 2);
    const yTitle = `<text class="conv-axis-title" text-anchor="middle" transform="rotate(-90 14 ${yCy})" x="14" y="${yCy}">normalized residual ‖·‖²_F</text>`;

    const parts = norm.map((s) => {
        if (!s.curves.length) return "";
        const multi = s.curves.length > 1;
        const line = (curve, faint) => {
            let d = `M ${f1(xPx(curve[0][0]))} ${f1(yPx(curve[0][1]))}`;
            for (let i = 1; i < curve.length; i++) d += ` L ${f1(xPx(curve[i][0]))} ${f1(yPx(curve[i][1]))}`;
            const style = faint
                ? `stroke:${s.color};stroke-width:1;stroke-opacity:0.3;stroke-dasharray:3 2`
                : `stroke:${s.color};stroke-width:2`;
            return `<path d="${d}" fill="none" style="${style}" stroke-linejoin="round" />`;
        };
        // Faint per-run lines when multiple runs; a bold line for the first (or only) run.
        const faintLines = multi ? s.curves.map((c) => line(c, true)).join("") : "";
        const boldCurve = s.curves[0];
        const dots = boldCurve.map(([x, y]) =>
            `<circle cx="${f1(xPx(x))}" cy="${f1(yPx(y))}" r="3" style="fill:${s.color}" />` +
            `<circle cx="${f1(xPx(x))}" cy="${f1(yPx(y))}" r="10" fill="transparent" style="cursor:pointer">` +
            `<title>${qEsc(s.label)} · ${x} matrices · residual ${qEsc(fmtTick(y))}</title></circle>`
        ).join("");
        return `<g data-series="${qEsc(s.key)}">${faintLines}${line(boldCurve, false)}${dots}</g>`;
    }).join("");

    return `<svg class="conv-svg" viewBox="0 0 ${W} ${H}" role="img" preserveAspectRatio="xMidYMid meet">${grid}${axes}${yLabels}${xLabels}${xTitle}${yTitle}${parts}</svg>`;
}

function fmtDate(ms) {
    const d = new Date(ms);
    const mm = String(d.getUTCMonth() + 1).padStart(2, "0");
    const dd = String(d.getUTCDate()).padStart(2, "0");
    return `${d.getUTCFullYear()}-${mm}-${dd}`;
}

// Running-best envelope: emit a point each time the record improves → monotone.
function bestOverTime(items, minimize) {
    const sorted = items
        .filter((d) => Number.isFinite(d.t) && Number.isFinite(d.v))
        .sort((a, b) => a.t - b.t);
    const out = [];
    let best = null;
    sorted.forEach((d) => {
        if (best === null || (minimize ? d.v < best : d.v > best)) {
            best = d.v;
            out.push({ x: d.t, y: best });
        }
    });
    return out;
}

function buildConvergenceChart(series, opts) {
    const pts = series.flatMap((s) => s.points);
    if (!pts.length) return "";
    const W = 720;
    const H = 300;
    const m = { t: 16, r: 18, b: 40, l: 66 };
    const xsAll = pts.map((p) => p.x);
    const ysAll = pts.map((p) => p.y);
    let xMin = Math.min(...xsAll);
    let xMax = Math.max(...xsAll);
    if (xMin === xMax) { xMin -= 86400000; xMax += 86400000; }

    const useLog = Boolean(opts.yLog) && ysAll.every((y) => y > 0);
    let yMin = Math.min(...ysAll);
    let yMax = Math.max(...ysAll);
    let lo = 0;
    let hi = 1;
    let yAxis = null;
    if (useLog) {
        // lo/hi are log10 endpoints, snapped to nice 1-2-5 bounds (a max of 16
        // stops the axis at 20, not the next full decade 100), then padded ~5% so
        // points sit inset from the top/bottom frame.
        yAxis = qNiceLogAxis(yMin, yMax, { maxMajor: 5 });
        const span = (Math.log10(yAxis.hi) - Math.log10(yAxis.lo)) || 1;
        lo = Math.log10(yAxis.lo) - span * 0.05;
        hi = Math.log10(yAxis.hi) + span * 0.05;
    } else {
        const span = (yMax - yMin) || Math.abs(yMax) || 1;
        yMin -= span * 0.1; yMax += span * 0.1;
    }

    // Inset the x (time) domain ~4% so the first/last points don't hug the frames.
    const xPad = ((xMax - xMin) || 1) * 0.04;
    const xLoP = xMin - xPad;
    const xHiP = xMax + xPad;
    const xPx = (x) => m.l + (W - m.l - m.r) * ((x - xLoP) / ((xHiP - xLoP) || 1));
    const yPx = (y) => {
        if (useLog) {
            const v = Math.log10(y);
            return H - m.b - (H - m.t - m.b) * ((v - lo) / ((hi - lo) || 1));
        }
        return H - m.b - (H - m.t - m.b) * ((y - yMin) / ((yMax - yMin) || 1));
    };

    // Y-ticks: labeled decades (+ faint 2×/5× minor guides) on a log axis; nice
    // 1/2/5×10ⁿ linear steps otherwise, integer-forced when the data is whole.
    const yIsInteger = ysAll.every((y) => Number.isInteger(y));
    let yticks;
    let yMinorTicks = [];
    if (useLog) {
        yticks = yAxis.major.map((y) => ({ y, py: yPx(y) }));
        yMinorTicks = yAxis.minor;
        if (!yticks.length) yticks = [{ y: yAxis.lo, py: yPx(yAxis.lo) }];
    } else {
        yticks = qNiceLinearTicks(yMin, yMax, { integer: yIsInteger, target: 4 })
            .filter((v) => v >= yMin - 1e-9 && v <= yMax + 1e-9)
            .map((y) => ({ y, py: yPx(y) }));
        if (!yticks.length) yticks = [{ y: yMin, py: yPx(yMin) }];
    }
    const xticks = [];
    const nX = 3;
    for (let i = 0; i <= nX; i++) {
        const x = xMin + (xMax - xMin) * (i / nX);
        xticks.push({ x, px: xPx(x) });
    }

    const gridMinor = yMinorTicks
        .map((v) => `<line class="conv-grid-minor" x1="${m.l}" y1="${yPx(v).toFixed(1)}" x2="${W - m.r}" y2="${yPx(v).toFixed(1)}" />`)
        .join("");
    const grid = gridMinor + yticks
        .map((t) => `<line class="conv-grid" x1="${m.l}" y1="${t.py.toFixed(1)}" x2="${W - m.r}" y2="${t.py.toFixed(1)}" />`)
        .join("");
    const yLabels = yticks
        .map((t) => `<text class="conv-tick" text-anchor="end" x="${m.l - 8}" y="${(t.py + 3).toFixed(1)}">${qEsc(fmtTick(t.y))}</text>`)
        .join("");
    const xLabels = xticks
        .map((t) => `<text class="conv-tick" text-anchor="middle" x="${t.px.toFixed(1)}" y="${H - m.b + 16}">${qEsc(fmtDate(t.x))}</text>`)
        .join("");
    const axes =
        `<line class="conv-axis-line" x1="${m.l}" y1="${m.t}" x2="${m.l}" y2="${H - m.b}" />` +
        `<line class="conv-axis-line" x1="${m.l}" y1="${H - m.b}" x2="${W - m.r}" y2="${H - m.b}" />`;

    const drawn = series
        .map((s) => {
            if (!s.points.length) return "";
            const sp = s.points.slice().sort((a, b) => a.x - b.x);
            let d = "";
            sp.forEach((p, i) => {
                const X = xPx(p.x).toFixed(1);
                const Y = yPx(p.y).toFixed(1);
                if (i === 0) d = `M ${X} ${Y}`;
                else d += ` L ${xPx(p.x).toFixed(1)} ${yPx(sp[i - 1].y).toFixed(1)} L ${X} ${Y}`;
            });
            d += ` L ${xPx(xMax).toFixed(1)} ${yPx(sp[sp.length - 1].y).toFixed(1)}`;
            const line = `<path d="${d}" fill="none" style="stroke:${s.color}" stroke-width="2" stroke-linejoin="round" />`;
            // A larger transparent circle over each dot widens the hover target
            // (the native <title> tooltip fires on it) so the small dots are easy
            // to hit on desktop and touch alike.
            const dots = sp
                .map((p) => {
                    const cx = xPx(p.x).toFixed(1);
                    const cy = yPx(p.y).toFixed(1);
                    return (
                        `<circle cx="${cx}" cy="${cy}" r="3.6" style="fill:${s.color}" />` +
                        `<circle cx="${cx}" cy="${cy}" r="10" fill="transparent" style="cursor:pointer"><title>${qEsc(s.name)} · ${qEsc(fmtDate(p.x))} · ${qEsc(fmtTick(p.y))}</title></circle>`
                    );
                })
                .join("");
            return line + dots;
        })
        .join("");

    return `<svg class="conv-svg" viewBox="0 0 ${W} ${H}" role="img" preserveAspectRatio="xMidYMid meet">${grid}${axes}${yLabels}${xLabels}${drawn}</svg>`;
}

// Efficient-frontier chart for a portfolio λ sweep: objective (y) across the
// discrete risk-aversion λ values (x). x is categorical (evenly spaced, one slot
// per λ, labelled with the λ value) rather than a log scale — the sweep includes
// λ=0 (which a log axis can't place) and is a small discrete set, so even spacing
// reads more clearly than a true numeric axis. y is linear (objectives may be
// negative). `points` = [{label, y, selected}] already ordered low→high λ.
function buildFrontierChart(points) {
    const pts = points.filter((p) => Number.isFinite(p.y));
    if (pts.length < 2) return "";  // a single point is not a frontier
    const W = 720, H = 300;
    const m = { t: 16, r: 18, b: 44, l: 66 };
    const ys = pts.map((p) => p.y);
    let yMin = Math.min(...ys), yMax = Math.max(...ys);
    const span = (yMax - yMin) || Math.abs(yMax) || 1;
    yMin -= span * 0.1; yMax += span * 0.1;

    const n = points.length;
    const xPx = (i) => m.l + (W - m.l - m.r) * (n === 1 ? 0.5 : i / (n - 1));
    const yPx = (y) => H - m.b - (H - m.t - m.b) * ((y - yMin) / ((yMax - yMin) || 1));

    const yticks = qNiceLinearTicks(yMin, yMax, { integer: ys.every((y) => Number.isInteger(y)), target: 4 })
        .filter((v) => v >= yMin - 1e-9 && v <= yMax + 1e-9);
    const f1 = (x) => x.toFixed(1);
    const grid = yticks.map((v) =>
        `<line class="conv-grid" x1="${m.l}" y1="${f1(yPx(v))}" x2="${W - m.r}" y2="${f1(yPx(v))}" />`
    ).join("");
    const axes =
        `<line class="conv-axis-line" x1="${m.l}" y1="${m.t}" x2="${m.l}" y2="${H - m.b}" />` +
        `<line class="conv-axis-line" x1="${m.l}" y1="${H - m.b}" x2="${W - m.r}" y2="${H - m.b}" />`;
    const yLabels = yticks.map((v) =>
        `<text class="conv-tick" text-anchor="end" x="${m.l - 8}" y="${f1(yPx(v) + 3)}">${qEsc(fmtTick(v))}</text>`
    ).join("");
    const xLabels = points.map((p, i) =>
        `<text class="conv-tick" text-anchor="middle" x="${f1(xPx(i))}" y="${H - m.b + 16}">${qEsc(p.label)}</text>`
    ).join("");
    const xTitle = `<text class="conv-axis-title" text-anchor="middle" x="${f1((m.l + W - m.r) / 2)}" y="${H - 4}">risk aversion λ →</text>`;
    const yCy = f1((m.t + H - m.b) / 2);
    const yTitle = `<text class="conv-axis-title" text-anchor="middle" transform="rotate(-90 14 ${yCy})" x="14" y="${yCy}">objective</text>`;

    // Line through the points that have a value (skip gaps), then dots. The
    // currently-selected λ gets a larger ring so the page and chart stay in sync.
    const linePts = points.map((p, i) => ({ i, y: p.y })).filter((p) => Number.isFinite(p.y));
    let d = "";
    linePts.forEach((p, k) => { d += `${k === 0 ? "M" : "L"} ${f1(xPx(p.i))} ${f1(yPx(p.y))} `; });
    const line = `<path d="${d}" fill="none" style="stroke:var(--accent)" stroke-width="2" stroke-linejoin="round" />`;
    const dots = points.map((p, i) => {
        if (!Number.isFinite(p.y)) return "";
        const cx = f1(xPx(i)), cy = f1(yPx(p.y));
        const ring = p.selected ? `<circle cx="${cx}" cy="${cy}" r="6" fill="none" style="stroke:var(--accent)" stroke-width="2" />` : "";
        return ring +
            `<circle cx="${cx}" cy="${cy}" r="3.6" style="fill:var(--accent)" />` +
            `<circle cx="${cx}" cy="${cy}" r="10" fill="transparent" style="cursor:pointer"><title>λ ${qEsc(p.label)} · ${qEsc(fmtTick(p.y))}</title></circle>`;
    }).join("");

    return `<svg class="conv-svg" viewBox="0 0 ${W} ${H}" role="img" preserveAspectRatio="xMidYMid meet">${grid}${axes}${yLabels}${xLabels}${xTitle}${yTitle}${line}${dots}</svg>`;
}

function frontierChartCard(points) {
    const svg = buildFrontierChart(points);
    if (!svg) return "";
    return `<section class="tw chart-card">
        <div class="chart-head">
            <div><h3>Efficient frontier</h3><p>Best objective at each risk-aversion λ across the sweep. Each point is one λ instance; the ringed point is the λ shown below.</p></div>
        </div>
        ${svg}
    </section>`;
}

function convChartCard(title, desc, series, svg) {
    const legend = series
        .filter((s) => s.points.length)
        .map((s) => `<span class="conv-leg"><span class="conv-dot" style="background:${s.color}"></span>${qEsc(s.name)}</span>`)
        .join("");
    return `<section class="tw chart-card">
        <div class="chart-head">
            <div><h3>${qEsc(title)}</h3><p>${qEsc(desc)}</p></div>
            <div class="conv-legend">${legend}</div>
        </div>
        ${svg}
    </section>`;
}

function renderSubmissionPlots(p, inst, submissions) {
    const minimize = p.minimize !== false;
    const parsed = (submissions || [])
        .filter((s) => !isInfeasibleSub(s))
        .map((s) => ({
            v: pNum(s.value),
            t: pDate(s.date),
            rt: pNum(s.runtime_total),
            cat: catOf(s),
        }));

    const makeSeries = (items, isMin, valueKey) =>
        CAT_ORDER.map((key) => {
            const subset = items.filter((d) => d.cat === key).map((d) => ({ t: d.t, v: valueKey(d) }));
            return { name: qCATS[key].label, color: qCATS[key].color, points: bestOverTime(subset, isMin) };
        });

    // Plot 1: best objective value over submission time.
    let plot1 = "";
    const valueItems = parsed.filter((d) => Number.isFinite(d.v) && Number.isFinite(d.t));
    if (valueItems.length) {
        const series = makeSeries(valueItems, minimize, (d) => d.v);
        const svg = buildConvergenceChart(series, { yLog: false });
        if (svg) {
            plot1 = convChartCard(
                "Best objective value over submission time",
                `Best objective reached so far by each approach as submissions arrived (${minimize ? "lower is better, so the line only decreases" : "higher is better, so the line only increases"}).`,
                series,
                svg,
            );
        }
    }

    // Plot 2: runtime to reach the optimum over time (only when several submissions hit the optimum).
    let plot2 = "";
    const optimal = inst.best_is_optimal ? (inst.best_value ?? inst.reference_solution_value ?? inst.bkv ?? null) : null;
    if (optimal != null) {
        const eps = 1e-6 * Math.max(1, Math.abs(Number(optimal)));
        const optItems = parsed.filter(
            (d) => Number.isFinite(d.v) && Math.abs(d.v - Number(optimal)) <= eps && Number.isFinite(d.rt) && d.rt > 0 && Number.isFinite(d.t),
        );
        if (optItems.length >= 2) {
            const series = makeSeries(optItems, true, (d) => d.rt);
            const svg = buildConvergenceChart(series, { yLog: true });
            if (svg) {
                plot2 = convChartCard(
                    "Fastest runtime to reach the optimum over submission time",
                    "Among submissions that reached the optimal objective, the best (lowest) total runtime achieved so far by each approach.",
                    series,
                    svg,
                );
            }
        }
    }

    // Plot 3: time series — one series per submission that has time_series data.
    // Split into two charts: true incumbent-objective-over-time runs, and
    // "approximation" runs whose reported value only rises for a minimization (or
    // only falls for a maximization) — e.g. BirkhoffPlus reports the count of
    // permutation matrices added over time, which climbs toward the objective and
    // is not a feasible incumbent. Mixing the two on one axis made the objective
    // chart appear to increase for a minimization problem.
    let plot3 = "";
    const tsSubs = (submissions || []).filter((s) => Array.isArray(s.time_series) && s.time_series.length);
    if (tsSubs.length) {
        // Group by _source_dir (one entry per submission package), up to palette limit.
        const seen = new Map(); // source_dir → series index
        const tsSeries = [];
        for (const sub of tsSubs) {
            const key = sub._source_dir || sub.submitter || "unknown";
            if (!seen.has(key)) {
                if (seen.size >= TS_PALETTE.length) continue; // palette exhausted
                seen.set(key, tsSeries.length);
                tsSeries.push({
                    key,
                    label: tsLabel(sub),
                    color: TS_PALETTE[seen.size - 1],
                    runs: [],
                });
            }
            tsSeries[seen.get(key)].runs.push(...sub.time_series);
        }

        const approxSeries = tsSeries.filter((s) => seriesIsAccumulation(s));
        const approxKeys = new Set(approxSeries.map((s) => s.key));
        const incumbentSeries = tsSeries.filter((s) => !approxKeys.has(s.key));
        const bkv = pNum(inst.best_value ?? inst.bkv);

        // Wrap a rendered chart SVG in a legend + chart-card shell (or "" if empty).
        const chartCard = (svg, chartSeries, title, desc) => {
            if (!svg) return "";
            const legend = chartSeries.map((s) =>
                `<span class="conv-leg" data-series="${qEsc(s.key)}">` +
                `<span class="conv-dot" style="background:${s.color}"></span>` +
                `<span class="conv-leg-label">${qEsc(s.label)}</span></span>`
            ).join("");
            return `<section class="tw chart-card ts-chart-card">
                <div class="chart-head">
                    <div>
                        <h3>${qEsc(title)}</h3>
                        <p>${desc}</p>
                    </div>
                    <div class="conv-legend">${legend}</div>
                </div>
                ${svg}
            </section>`;
        };

        // Objective-over-time chart (true incumbent runs only).
        let incumbentCard = "";
        if (incumbentSeries.length) {
            const svg = buildTsChart(incumbentSeries, minimize, Number.isFinite(bkv) ? bkv : null);
            const nRuns = incumbentSeries.reduce((n, s) => n + s.runs.length, 0);
            const hasMultiRun = incumbentSeries.some((s) => s.runs.length > 1);
            const envNote = hasMultiRun
                ? " Bold line = best-run envelope; faint dashed lines = individual runs."
                : "";
            const desc = `Incumbent objective vs. wall-clock time per submission (${nRuns} run${nRuns === 1 ? "" : "s"} total).${envNote} Click a legend entry to solo/toggle.`;
            incumbentCard = chartCard(svg, incumbentSeries, "Objective time series", desc);
        }

        // Approximation-progress chart: matrices (x) vs squared normalized Frobenius
        // residual (y) — a convergence curve, not a time series.
        let approxCard = "";
        if (approxSeries.length) {
            const svg = buildApproxChart(approxSeries);
            const desc =
                "Reconstruction residual (squared normalized Frobenius norm) vs. the number of " +
                "permutation matrices used, for methods that build the decomposition incrementally. " +
                "Lower is better; residual 0 = exact reconstruction. Click a legend entry to solo/toggle.";
            approxCard = chartCard(svg, approxSeries, "Approximation progress", desc);
        }

        plot3 = incumbentCard + approxCard;
    }

    if (!plot1 && !plot2 && !plot3) return "";
    const plots = [plot1, plot2, plot3].filter(Boolean).join("");
    return `<div class="ss-title">Performance charts</div><div class="perf-charts">${plots}</div>`;
}

// Per-series visibility toggle for the time series chart.
// Same three-rule model as problem.js: all-on→solo, any-click-in-partial→toggle,
// all-off→restore. Scoped to .ts-chart-card so it doesn't interfere with other charts.
function _tsToggle(hidden, key, allKeys) {
    if (hidden.size === 0) {
        allKeys.forEach((k) => { if (k !== key) hidden.add(k); });
    } else if (hidden.size === allKeys.length) {
        hidden.clear();
    } else {
        if (hidden.has(key)) hidden.delete(key); else hidden.add(key);
        if (hidden.size === allKeys.length) hidden.clear();
    }
}

function wireTsToggles(root) {
    (root || document).querySelectorAll(".ts-chart-card").forEach((card) => {
        const hidden = new Set();
        card.querySelectorAll(".conv-leg[data-series]").forEach((leg) => {
            if (leg.dataset.bound === "1") return;
            leg.dataset.bound = "1";
            leg.addEventListener("click", () => {
                const allKeys = [...card.querySelectorAll(".conv-leg[data-series]")].map((l) => l.dataset.series);
                _tsToggle(hidden, leg.dataset.series, allKeys);
                card.querySelectorAll(".conv-leg[data-series]").forEach((l) => {
                    const off = hidden.has(l.dataset.series);
                    l.classList.toggle("conv-leg-off", off);
                    card.querySelectorAll(`[data-series="${CSS.escape(l.dataset.series)}"]`).forEach((el) => {
                        el.style.opacity = off ? "0.1" : "";
                    });
                });
            });
        });
    });
}

async function initInstancePage() {
    qInitCommon();
    const params = new URLSearchParams(window.location.search);
    const problemId = params.get("problem") || "";
    const instanceName = params.get("name") || "";
    const container = document.getElementById("inst-detail");

    if (!problemId || !instanceName) {
        qShowError(container, "Missing problem or instance in URL.");
        return;
    }

    try {
        const p = await qLoadProblemData(problemId);
        const inst = (p.instances || []).find((i) => i.name === instanceName);
        if (!inst) {
            throw new Error(`Instance \"${instanceName}\" was not found in problem ${problemId}.`);
        }
        qSetPageMeta({ title: `${inst.name} · ${p.name} — QOBLIB` });

        // Portfolio (06) instances are collapsed to one base per data set, with the
        // risk-aversion λ sweep carried in `inst.lambdas`. The page renders one λ at
        // a time (selected via a segmented control) and, above it, an efficient-
        // frontier chart of objective vs λ across the whole sweep. Every other
        // problem has no `lambdas` and renders exactly as before (sweep === null).
        const sweep = Array.isArray(inst.lambdas) && inst.lambdas.length ? inst.lambdas : null;
        // Default to the first λ that actually has a submission or reference value,
        // else the first entry — so the page opens on something populated.
        let selectedLambdaIdx = 0;
        if (sweep) {
            const firstPop = sweep.findIndex(
                (c) => c.has_submissions || Number.isFinite(Number(c.best_value ?? c.reference_solution_value)),
            );
            selectedLambdaIdx = firstPop >= 0 ? firstPop : 0;
        }

        // The lazy per-submission time-series file, fetched once and shared across
        // λ re-renders (keyed "<instance>::<_source_file>").
        let timeSeriesMap = {};
        try {
            timeSeriesMap = await qLoadProblemTimeSeries(problemId);
        } catch (e) { /* plots simply omitted if unavailable */ }

        const parseMaybeNumber = (value) => {
            if (value == null) return Number.NaN;
            return Number(String(value).replace(/,/g, "").trim());
        };
        const parseMaybeDate = (value) => qParseDate(value);
        // Canonical objective direction: treat an unspecified `minimize` as
        // minimize, matching the convergence chart (instance.js makeSeries) so the
        // ranking and the plot never disagree on which way is "better".
        const minimize = p.minimize !== false;
        const isMarketSplit = String(p.id || "").padStart(2, "0") === "01";
        const isInfeasibleSubmission = (submission) => {
            const nFeasible = parseMaybeNumber(submission?.n_feasible);
            return Number.isFinite(nFeasible) && nFeasible === 0;
        };
        const rankSymbol = (rank) => {
            if (rank === 1) return "▲";
            if (rank === 2) return "◆";
            if (rank === 3) return "●";
            return "·";
        };
        const isSameObjective = (value, target) => {
            const v = parseMaybeNumber(value);
            if (!Number.isFinite(target) || !Number.isFinite(v)) return false;
            const scale = Math.max(1, Math.abs(target), Math.abs(v));
            return Math.abs(v - target) <= 1e-9 * scale;
        };

        // Resolve the "view" for a given λ selection: which instance record supplies
        // the header/objective/models (the sweep child for portfolio, else the base
        // instance itself) and which name keys its submissions + time-series.
        const viewFor = (childIdx) => {
            if (!sweep) return { view: inst, name: instanceName };
            const child = sweep[childIdx] || sweep[0];
            // Merge the per-λ child over the base so shared fields (raw_url,
            // size_bytes, metrics) survive while λ-specific ones override.
            return { view: { ...inst, ...child }, name: child.name };
        };

        // Build the sorted submissions + best-known marker for one view. Pulls the
        // objective time-series onto each submission from the shared lazy map.
        const submissionsFor = (viewInst, viewName) => {
            const subs = [...(p.instance_submissions?.[viewName] || [])];
            subs.forEach((s) => {
                const key = `${viewName}::${s._source_file || s._source_dir || ""}`;
                if (timeSeriesMap[key]) s.time_series = timeSeriesMap[key];
            });
            subs.sort((a, b) => {
                const aInfeasible = isInfeasibleSubmission(a);
                const bInfeasible = isInfeasibleSubmission(b);
                if (aInfeasible !== bInfeasible) return aInfeasible ? 1 : -1;
                const av = parseMaybeNumber(a.value);
                const bv = parseMaybeNumber(b.value);
                if (Number.isFinite(av) && Number.isFinite(bv) && av !== bv) return minimize ? av - bv : bv - av;
                if (Number.isFinite(av) !== Number.isFinite(bv)) return Number.isFinite(av) ? -1 : 1;
                const ar = parseMaybeNumber(a.runtime_total);
                const br = parseMaybeNumber(b.runtime_total);
                if (Number.isFinite(ar) && Number.isFinite(br) && ar !== br) return ar - br;
                if (Number.isFinite(ar) !== Number.isFinite(br)) return Number.isFinite(ar) ? -1 : 1;
                const ad = parseMaybeDate(a.date);
                const bd = parseMaybeDate(b.date);
                if (Number.isFinite(ad) && Number.isFinite(bd) && ad !== bd) return ad - bd;
                if (Number.isFinite(ad) !== Number.isFinite(bd)) return Number.isFinite(ad) ? -1 : 1;
                return String(a._source_dir || "").localeCompare(String(b._source_dir || ""));
            });

            const bestKnown = parseMaybeNumber(viewInst.best_value ?? viewInst.bkv);
            const feasibleSubmissions = subs.filter((s) => !isInfeasibleSubmission(s));
            const submittedObjectives = feasibleSubmissions.map((s) => parseMaybeNumber(s.value)).filter((v) => Number.isFinite(v));
            const bestSubmittedObjective = submittedObjectives.length
                ? (minimize ? Math.min(...submittedObjectives) : Math.max(...submittedObjectives))
                : Number.NaN;
            const hasBestKnownMatch = feasibleSubmissions.some((s) => isSameObjective(s.value, bestKnown));
            const markerObjective = hasBestKnownMatch ? bestKnown : bestSubmittedObjective;
            const firstBestKnownSubmission = feasibleSubmissions
                .filter((s) => isSameObjective(s.value, markerObjective))
                .map((s) => ({ s, t: parseMaybeDate(s.date) }))
                .sort((a, b) => {
                    if (Number.isFinite(a.t) && Number.isFinite(b.t) && a.t !== b.t) return a.t - b.t;
                    if (Number.isFinite(a.t) !== Number.isFinite(b.t)) return Number.isFinite(a.t) ? -1 : 1;
                    const ar = parseMaybeNumber(a.s.runtime_total);
                    const br = parseMaybeNumber(b.s.runtime_total);
                    if (Number.isFinite(ar) && Number.isFinite(br) && ar !== br) return ar - br;
                    if (Number.isFinite(ar) !== Number.isFinite(br)) return Number.isFinite(ar) ? -1 : 1;
                    return String(a.s._source_dir || "").localeCompare(String(b.s._source_dir || ""));
                })[0]?.s;
            return { subs, firstBestKnownSubmission };
        };

        // Frontier points across the whole sweep (base-level, λ-independent).
        const frontierPoints = sweep
            ? sweep
                .filter((c) => c.risk_lambda !== "n/a")
                .map((c) => ({
                    label: c.risk_lambda,
                    y: parseMaybeNumber(c.best_value ?? c.reference_solution_value ?? c.bkv),
                    idx: sweep.indexOf(c),
                }))
            : [];

        // Instance navigation: alphabetical order, wraps around at both ends.
        const allInstances = [...(p.instances || [])].sort((a, b) =>
            a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: "base" })
        );
        const n = allInstances.length;
        const instIdx = allInstances.findIndex((i) => i.name === instanceName);
        const prevInst = n > 1 ? allInstances[(instIdx - 1 + n) % n] : null;
        const nextInst = n > 1 ? allInstances[(instIdx + 1) % n] : null;
        const instNavHtml = `<div class="inst-nav">
            ${prevInst
                ? `<a class="inst-nav-btn" href="${qEsc(qInstanceUrl(p.id, prevInst.name))}" title="${qEsc(prevInst.name)}">← ${qEsc(prevInst.name)}</a>`
                : `<span class="inst-nav-btn inst-nav-disabled"></span>`}
            <span class="inst-nav-pos">${instIdx + 1} / ${n}</span>
            <span class="inst-nav-search-wrap">
                <input class="inst-nav-search" type="search" placeholder="Jump to…" aria-label="Search instance" autocomplete="off"
                       role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="inst-nav-listbox" />
                <ul class="inst-nav-dropdown" id="inst-nav-listbox" role="listbox" aria-label="Instance results" hidden></ul>
            </span>
            ${nextInst
                ? `<a class="inst-nav-btn inst-nav-next" href="${qEsc(qInstanceUrl(p.id, nextInst.name))}" title="${qEsc(nextInst.name)}">${qEsc(nextInst.name)} →</a>`
                : `<span class="inst-nav-btn inst-nav-disabled"></span>`}
        </div>`;

        // λ selector (portfolio only): a segmented control over the sweep, reusing
        // the .seg-toggle idiom from problem.js. "n/a" entries (budget-less
        // submissions) are labelled distinctly.
        const lambdaSelectorHtml = sweep
            ? `<div class="lambda-panel">
                <div class="perf-toolbar lambda-selector">
                    <span class="lambda-selector-label">Risk aversion λ</span>
                    <div class="seg-toggle" role="group" aria-label="Risk aversion λ">
                        ${sweep.map((c, i) =>
                            `<button type="button" class="seg-btn${i === selectedLambdaIdx ? " on" : ""}"
                                     data-lambda-idx="${i}" aria-pressed="${i === selectedLambdaIdx ? "true" : "false"}"
                            >${c.risk_lambda === "n/a" ? "λ n/a" : qEsc(c.risk_lambda)}</button>`
                        ).join("")}
                    </div>
                </div>
                <p class="lambda-help">
                    This instance shares one dataset across a sweep of risk-aversion weights λ.
                    A larger λ penalises portfolio risk more heavily relative to return, so each λ
                    is a distinct objective — together they trace the risk–return efficient frontier
                    below. Objectives are minimised (lower is better; values are negative expected
                    return net of risk and costs). Pick a λ to see its models, submissions and best
                    known value.
                </p>
            </div>`
            : "";

        // Frontier chart (portfolio only): objective vs λ across the whole sweep.
        const renderFrontier = (activeIdx) => sweep
            ? frontierChartCard(frontierPoints.map((pt) => ({ ...pt, selected: pt.idx === activeIdx })))
            : "";

        // Everything below the header that depends on the selected λ. Rebuilt on
        // each λ change; for non-portfolio problems it renders once with the base
        // instance (viewFor returns it unchanged).
        const renderLambdaBody = (childIdx) => {
            const { view: viewInst, name: viewName } = viewFor(childIdx);
            const { subs, firstBestKnownSubmission } = submissionsFor(viewInst, viewName);
            const metricRows = (Array.isArray(p.columns) ? p.columns : [])
                .filter((c) => viewInst.metrics && viewInst.metrics[c.key] != null && viewInst.metrics[c.key] !== "")
                .map((c) => `<div class="mr"><span class="mk">${qEsc(c.label)}</span><span class="mv">${c.numeric ? qFmtNum(viewInst.metrics[c.key]) : qEsc(viewInst.metrics[c.key])}</span></div>`)
                .join("");
            // For portfolio, surface the selected λ as its own meta row (it's no
            // longer a base-level column).
            const lambdaRow = sweep && viewInst.risk_lambda && viewInst.risk_lambda !== "n/a"
                ? `<div class="mr"><span class="mk">Risk λ</span><span class="mv">${qEsc(viewInst.risk_lambda)}</span></div>`
                : "";

            return `
            <div class="d-meta">
                ${metricRows}
                ${lambdaRow}
                <div class="mr"><span class="mk">Best objective</span><span class="mv">${qFmtNum(viewInst.best_value ?? viewInst.bkv)}</span></div>
                <div class="mr"><span class="mk">Reference objective</span><span class="mv">${viewInst.reference_solution_value != null ? qFmtNum(viewInst.reference_solution_value) : "-"}</span></div>
                <div class="mr"><span class="mk">Submissions</span><span class="mv">${subs.length}</span></div>
                <div class="mr"><span class="mk">Models</span><span class="mv">${(viewInst.models || []).length}</span></div>
            </div>

            <div class="hero-actions" style="margin:1rem 0 1.5rem">
                ${viewInst.raw_url ? `<a class="btn btn-ghost" href="${qSafeHref(viewInst.raw_url)}" target="_blank" rel="noopener">Download Instance</a>` : ""}
                ${viewInst.reference_solution_url ? `<a class="btn btn-ghost" href="${qSafeHref(viewInst.reference_solution_url)}" target="_blank" rel="noopener">Download Solution</a>` : ""}
            </div>

            ${renderFrontier(childIdx)}

            ${renderSubmissionPlots(p, viewInst, subs)}

            <div class="ss-title">Uploaded Models (${(viewInst.models || []).length})</div>
            ${qDetailModelList(viewInst.models || [])}

            <div class="ss-title">Submissions (${subs.length})</div>
            ${
                subs.length
                    ? `<div class="tw">
                        <table>
                            <thead>
                                <tr>
                                    <th style="text-align:center" data-sort-type="number">Rank</th>
                                    <th style="text-align:right">Objective</th>
                                    <th>Submitter</th>
                                    <th>Date</th>
                                    <th>Approach</th>
                                    <th>Type</th>
                                    <th>Reference</th>
                                    <th style="text-align:right">Runtime (s)</th>
                                    <th>Remarks</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${subs
                                    .map(
                                        (s, idx) => {
                                            const infeasible = isInfeasibleSubmission(s);
                                            const showObjective = !(isMarketSplit && infeasible);
                                            return `
                                            <tr>
                                                <td class="mono" style="text-align:center">${idx + 1} ${rankSymbol(idx + 1)}${firstBestKnownSubmission === s ? " ★" : ""}</td>
                                                <td class="num" style="font-weight:600">${showObjective ? qFmtNum(s.value) : "-"}</td>
                                                <td>${s._source_dir ? `<a class="rlink" href="${qSubmissionUrl(p.id, s._source_dir)}">${qFmtText(s.submitter || s.author)}</a>` : qFmtText(s.submitter || s.author)}</td>
                                                <td class="mono">${qEsc(qFmtDate(s.date))}</td>
                                                <td>${qFmtText(s.modeling_approach || s.algorithm_type)}</td>
                                                <td title="${qEsc((qCATS[catOf(s)] || qCATS.classical).label)}">${catBadge(catOf(s))}</td>
                                                <td title="${qEsc(s.reference || "")}">${qFmtText(s.reference)}</td>
                                                <td class="num">${qFmtMaybeNum(s.runtime_total)}</td>
                                                <td>${infeasible ? '<span class="badge b-tag">infeasible</span> ' : ""}${(() => { const full = s.remarks || s.workflow || s.hardware || ""; if (!full) return "-"; const short = full.length > 80 ? full.slice(0, 80) + "…" : full; return full.length > 80 ? `<span class="remarks-short" title="Click to expand">${qEsc(short)}</span><span class="remarks-full" hidden>${qEsc(full)}</span><button class="remarks-toggle" type="button" aria-expanded="false" aria-label="Expand remarks">▾</button>` : qEsc(full); })()}</td>
                                            </tr>`;
                                        },
                                    )
                                    .join("")}
                            </tbody>
                        </table>
                    </div>
                    <div class="table-legend" style="margin:.25rem 0 .6rem;color:var(--muted)">Rank markers: 1 ▲, 2 ◆, 3 ●, ★ = first submission to reach the best known/best submitted objective.</div>
                    `
                    : '<div class="empty-state">No submissions are available for this instance yet.</div>'
            }`;
        };

        container.innerHTML = `
            <a class="back" href="${qProblemUrl(p.id)}">← Back to ${String(p.id).padStart(2, "0")} ${qEsc(p.name)}</a>
            ${instNavHtml}
            <div class="dh">
                <div>
                    <div class="d-num">${String(p.id).padStart(2, "0")} / ${qEsc(p.slug)}</div>
                    <h1 class="d-title">${qEsc(inst.name)}</h1>
                    <div class="d-sub">${qEsc(p.name)}</div>
                    <div class="pcard-foot">
                        <a class="badge b-type" href="${qProblemUrl(p.id)}" title="Open the ${qEsc(p.name)} problem overview">${String(p.id).padStart(2, "0")} ${qEsc(p.name)}</a>
                        ${qStatusPill(inst.status)}
                        ${inst.vars != null ? `<span class="badge b-vars">${qFmtInt(inst.vars)} vars</span>` : ""}
                        ${sweep ? `<span class="badge b-tag">${sweep.filter((c) => c.risk_lambda !== "n/a").length} λ</span>` : ""}
                    </div>
                </div>
            </div>
            ${lambdaSelectorHtml}
            <div id="inst-lambda-body">${renderLambdaBody(selectedLambdaIdx)}</div>
        `;

        // Post-render wiring, factored out so it re-runs after each λ swap.
        const wireLambdaBody = () => {
            container.querySelectorAll(".resource-desc").forEach((el) => qRenderMath(el));
            qEnableTableSorting(container);
            wireTsToggles(container);
            qEnhanceFigures(container); // expand affordance on the submission-history charts
        };
        wireLambdaBody();

        // λ selector: swap the body to the chosen λ and re-wire it.
        if (sweep) {
            const toggle = container.querySelector(".lambda-selector .seg-toggle");
            const body = container.querySelector("#inst-lambda-body");
            toggle?.addEventListener("click", (e) => {
                const btn = e.target.closest(".seg-btn[data-lambda-idx]");
                if (!btn) return;
                selectedLambdaIdx = Number(btn.dataset.lambdaIdx);
                toggle.querySelectorAll(".seg-btn").forEach((b) => {
                    const on = b === btn;
                    b.classList.toggle("on", on);
                    b.setAttribute("aria-pressed", on ? "true" : "false");
                });
                body.innerHTML = renderLambdaBody(selectedLambdaIdx);
                wireLambdaBody();
            });
        }

        // Expandable remarks toggle (delegated on the container, so it survives
        // λ-body re-renders).
        container.addEventListener("click", (e) => {
            const btn = e.target.closest(".remarks-toggle");
            if (!btn) return;
            const cell = btn.parentElement;
            const shortEl = cell.querySelector(".remarks-short");
            const fullEl = cell.querySelector(".remarks-full");
            const expanded = btn.getAttribute("aria-expanded") === "true";
            if (shortEl) shortEl.hidden = !expanded ? true : false;
            if (fullEl) fullEl.hidden = !expanded ? false : true;
            btn.setAttribute("aria-expanded", expanded ? "false" : "true");
            btn.textContent = expanded ? "▾" : "▴";
        });

        // Instance search/jump widget
        const searchInput = container.querySelector(".inst-nav-search");
        const dropdown = container.querySelector(".inst-nav-dropdown");
        if (searchInput && dropdown) {
            const setActive = (li) => {
                dropdown.querySelectorAll("li[aria-selected]").forEach((el) => el.removeAttribute("aria-selected"));
                if (li) {
                    li.setAttribute("aria-selected", "true");
                    searchInput.setAttribute("aria-activedescendant", li.id);
                } else {
                    searchInput.removeAttribute("aria-activedescendant");
                }
            };
            const show = (items) => {
                dropdown.innerHTML = items
                    .map((inst, i) => `<li role="option" id="inst-nav-opt-${i}" tabindex="-1" data-href="${qEsc(qInstanceUrl(p.id, inst.name))}">${qEsc(inst.name)}</li>`)
                    .join("");
                dropdown.hidden = items.length === 0;
                searchInput.setAttribute("aria-expanded", items.length ? "true" : "false");
                setActive(null);
            };
            const hide = () => {
                dropdown.hidden = true;
                searchInput.setAttribute("aria-expanded", "false");
                setActive(null);
            };

            searchInput.addEventListener("input", () => {
                const q = searchInput.value.trim().toLowerCase();
                if (!q) { hide(); return; }
                const matches = allInstances.filter((i) => i.name.toLowerCase().includes(q)).slice(0, 12);
                show(matches);
            });

            searchInput.addEventListener("keydown", (e) => {
                if (e.key === "Escape") { hide(); searchInput.value = ""; return; }
                if (e.key === "Enter") {
                    const first = dropdown.querySelector("li");
                    if (first) window.location.href = first.dataset.href;
                }
                if (e.key === "ArrowDown") {
                    const first = dropdown.querySelector("li");
                    if (first) { e.preventDefault(); first.focus(); setActive(first); }
                }
            });

            dropdown.addEventListener("keydown", (e) => {
                const cur = document.activeElement;
                if (e.key === "Enter" && cur.dataset.href) { window.location.href = cur.dataset.href; return; }
                if (e.key === "ArrowDown") { e.preventDefault(); const nx = cur.nextElementSibling; if (nx) { nx.focus(); setActive(nx); } }
                if (e.key === "ArrowUp") { e.preventDefault(); const pv = cur.previousElementSibling; if (pv) { pv.focus(); setActive(pv); } else { searchInput.focus(); setActive(null); } }
                if (e.key === "Escape") { hide(); searchInput.value = ""; searchInput.focus(); }
            });

            dropdown.addEventListener("click", (e) => {
                const li = e.target.closest("li[data-href]");
                if (li) window.location.href = li.dataset.href;
            });

            document.addEventListener("click", (e) => {
                if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) hide();
            }, true);
        }
    } catch (error) {
        qShowError(container, error.message);
    }
}

initInstancePage();
