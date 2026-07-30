"use strict";

const {
    esc: qEsc,
    fmtBytes: qFmtBytes,
    fmtNum: qFmtNum,
    loadInstancesList: qLoadInstancesList,
    niceLogAxis: qNiceLogAxis,
    enhanceFigures: qEnhanceFigures,
    instanceUrl: qInstanceUrl,
    problemUrl: qProblemUrl,
    statusPill: qStatusPill,
    showError: qShowError,
    initCommon: qInitCommon,
    downloadCsv: qDownloadCsv,
    orderRowsByTable: qOrderRowsByTable,
} = window.QOBLIB;

let allInstances = [];
let visibleMipModels = new Set();

const PROBLEM_COLORS = {
    "01": { fill: "#2E6F95", stroke: "#1C4A65" },
    "02": { fill: "#B85C38", stroke: "#7D3D25" },
    "03": { fill: "#5D8A66", stroke: "#3E5F45" },
    "04": { fill: "#7A6EA8", stroke: "#514A75" },
    "05": { fill: "#C58A24", stroke: "#875E17" },
    "06": { fill: "#3F8D7E", stroke: "#2A6156" },
    "07": { fill: "#A14F7A", stroke: "#6D3552" },
    "08": { fill: "#4E7FB9", stroke: "#34577E" },
    "09": { fill: "#B66A46", stroke: "#7E4931" },
    "10": { fill: "#6F9E44", stroke: "#4D6D30" },
};

function colorForProblem(problemId) {
    return PROBLEM_COLORS[String(problemId || "").padStart(2, "0")] || { fill: "#1f6f6c", stroke: "#0e4f4d" };
}

// Approaches of the same problem share the base hue but get progressively
// lightened/darkened shades, so overlapping scatter points (and their legend
// dots) for different model formulations of one problem stay distinguishable.
const SHADE_STEPS = [26, -22, 50, -44];

function shadeHex(hex, percent) {
    const m = /^#?([0-9a-fA-F]{6})$/.exec(String(hex || ""));
    if (!m || !percent) return hex;
    const n = parseInt(m[1], 16);
    const target = percent < 0 ? 0 : 255;
    const p = Math.abs(percent) / 100;
    const mix = (c) => Math.round((target - c) * p) + c;
    const r = mix((n >> 16) & 255);
    const g = mix((n >> 8) & 255);
    const b = mix(n & 255);
    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
}

let MODEL_COLORS = new Map(); // model key -> { fill, stroke }

function buildModelColors(points) {
    const byProblem = new Map(); // pid -> ordered unique model keys
    points.forEach((point) => {
        const pid = String(point.problem_id || "").padStart(2, "0");
        const key = modelKeyForPoint(point);
        if (!byProblem.has(pid)) byProblem.set(pid, []);
        const list = byProblem.get(pid);
        if (!list.includes(key)) list.push(key);
    });
    MODEL_COLORS = new Map();
    byProblem.forEach((keys, pid) => {
        const base = colorForProblem(pid);
        keys.sort((a, b) => a.localeCompare(b));
        keys.forEach((key, i) => {
            const amt = i === 0 ? 0 : SHADE_STEPS[(i - 1) % SHADE_STEPS.length];
            MODEL_COLORS.set(key, { fill: shadeHex(base.fill, amt), stroke: shadeHex(base.stroke, amt) });
        });
    });
}

function colorForModelKey(key, problemId) {
    return MODEL_COLORS.get(key) || colorForProblem(problemId);
}

function prettyModelLabel(label) {
    return String(label || "model")
        .replace(/_/g, " ")
        .replace(/\s+/g, " ")
        .trim();
}

function modelKeyForPoint(point) {
    return `${String(point.problem_id || "").padStart(2, "0")}::${String(point.model_approach || point.model_kind || point.model_label || "model")}`;
}

function renderProblemLegend(points) {
    const legendRoot = document.getElementById("mip-chart-legend");
    if (!legendRoot) return;

    const classInfo = new Map();
    points.forEach((point) => {
        const pid = String(point.problem_id || "").padStart(2, "0");
        const modelLabel = prettyModelLabel(point.model_approach || point.model_kind || point.model_label || "model");
        const key = modelKeyForPoint(point);
        if (!pid || !modelLabel || classInfo.has(key)) return;
        classInfo.set(key, { pid, model: modelLabel });
    });

    const keys = [...classInfo.keys()].sort((a, b) => a.localeCompare(b));
    if (!keys.length) {
        legendRoot.innerHTML = "";
        return;
    }

    if (!visibleMipModels.size) {
        visibleMipModels = new Set(keys);
    }

    legendRoot.innerHTML = keys
        .map((key) => {
            const meta = classInfo.get(key) || {};
            const color = colorForModelKey(key, meta.pid);
            const active = visibleMipModels.has(key);
            return `
                <button type="button" class="legend-item${active ? " on" : " off"}" data-model-key="${qEsc(key)}" aria-pressed="${active ? "true" : "false"}">
                    <span class="dot" style="background:${qEsc(color.fill)};border-color:${qEsc(color.stroke)}"></span>
                    <span class="legend-text"><strong>${qEsc(meta.pid)}</strong> ${qEsc(meta.model || "model")}</span>
                </button>`;
        })
        .join("");

    legendRoot.querySelectorAll(".legend-item").forEach((button) => {
        button.addEventListener("click", () => {
            const key = String(button.dataset.modelKey || "");
            if (!key) return;
            const allVisible = keys.every((itemKey) => visibleMipModels.has(itemKey));
            if (allVisible) {
                visibleMipModels = new Set([key]);
            } else if (visibleMipModels.has(key)) {
                visibleMipModels.delete(key);
                if (!visibleMipModels.size) {
                    visibleMipModels = new Set(keys);
                }
            } else {
                visibleMipModels.add(key);
            }
            updateMipPointVisibility();
        });
    });
}

function updateMipPointVisibility() {
    const root = document.getElementById("mip-chart");
    const legendRoot = document.getElementById("mip-chart-legend");
    if (!root || !legendRoot) return;

    root.querySelectorAll(".mip-pt").forEach((group) => {
        const key = String(group.dataset.modelKey || "");
        group.classList.toggle("hidden", !visibleMipModels.has(key));
    });

    legendRoot.querySelectorAll(".legend-item").forEach((button) => {
        const key = String(button.dataset.modelKey || "");
        const active = visibleMipModels.has(key);
        button.classList.toggle("on", active);
        button.classList.toggle("off", !active);
        button.setAttribute("aria-pressed", active ? "true" : "false");
    });
}

function formatDensity(v) {
    if (!Number.isFinite(v)) return "-";
    if (v === 0) return "0";
    if (Math.abs(v) < 1e-4) return v.toExponential(2);
    return v.toLocaleString(undefined, { maximumSignificantDigits: 5 });
}

function renderMipChart(points) {
    const root = document.getElementById("mip-chart");
    if (!root) return;

    const positivePoints = points.filter((p) => p.num_vars > 0 && p.density > 0);
    buildModelColors(positivePoints);
    // renderProblemLegend seeds visibleMipModels in the *computed* key-space
    // (modelKeyForPoint). Do NOT pre-seed it here from the raw p.model_key field:
    // that lives in a different key-space, so the legend items and point groups
    // would never match — every legend entry would render "off" and its toggle
    // would do nothing.
    renderProblemLegend(positivePoints);

    if (!positivePoints.length) {
        root.innerHTML = '<div class="empty-state" style="padding:2rem">No LP metrics found for the current dataset.</div>';
        return;
    }

    const width = 940;
    const height = 460;
    const margin = { top: 16, right: 18, bottom: 52, left: 68 };
    const plotW = width - margin.left - margin.right;
    const plotH = height - margin.top - margin.bottom;

    const log10 = (v) => Math.log(v) / Math.log(10);

    const xMinRaw = Math.min(...positivePoints.map((p) => p.num_vars));
    const xMaxRaw = Math.max(...positivePoints.map((p) => p.num_vars));
    const yMinRaw = Math.min(...positivePoints.map((p) => p.density));
    const yMaxRaw = Math.max(...positivePoints.map((p) => p.density));

    // Tight log axes snapped to nice 1-2-5 bounds (a data max of 16 ends the axis
    // at 20, not the next full decade 100).
    const xAxis = qNiceLogAxis(xMinRaw, xMaxRaw, { maxMajor: 8 });
    const yAxis = qNiceLogAxis(yMinRaw, yMaxRaw, { maxMajor: 6 });

    const xMin = xAxis.lo;
    const xMax = xAxis.hi;
    const yMin = yAxis.lo;
    const yMax = yAxis.hi;

    // Pad the plotted domain ~5% beyond the axis bounds so points (and ticks) sit
    // inset from the edges rather than flush against them. Ticks/grid still render
    // at their nice values — they just no longer hug the frame.
    const PAD = 0.05;
    const xSpan = Math.max(1e-12, log10(xMax) - log10(xMin));
    const ySpan = Math.max(1e-12, log10(yMax) - log10(yMin));
    const xLoP = log10(xMin) - xSpan * PAD;
    const yLoP = log10(yMin) - ySpan * PAD;
    const xRange = xSpan * (1 + 2 * PAD);
    const yRange = ySpan * (1 + 2 * PAD);

    const xPos = (v) => margin.left + ((log10(v) - xLoP) / xRange) * plotW;
    const yPos = (v) => margin.top + (1 - (log10(v) - yLoP) / yRange) * plotH;

    const formatLogTick = (v) => {
        const p = Math.round(log10(v));
        if (p >= -2 && p <= 4) return qFmtNum(v);
        return `1e${p}`;
    };

    const xTickValues = xAxis.major;
    const yTickValues = yAxis.major;
    const xMinorValues = xAxis.minor;
    const yMinorValues = yAxis.minor;

    const gridX = xMinorValues
        .map((v) => `<line class="mip-grid-minor" x1="${xPos(v)}" y1="${margin.top}" x2="${xPos(v)}" y2="${height - margin.bottom}" />`)
        .join("")
        + xTickValues
            .map((v) => `<line class="mip-grid-line" x1="${xPos(v)}" y1="${margin.top}" x2="${xPos(v)}" y2="${height - margin.bottom}" />`)
            .join("");
    const gridY = yMinorValues
        .map((v) => `<line class="mip-grid-minor" x1="${margin.left}" y1="${yPos(v)}" x2="${width - margin.right}" y2="${yPos(v)}" />`)
        .join("")
        + yTickValues
            .map((v) => `<line class="mip-grid-line" x1="${margin.left}" y1="${yPos(v)}" x2="${width - margin.right}" y2="${yPos(v)}" />`)
            .join("");
    const labelsX = xTickValues
        .map((v) => `<text class="mip-axis-tick" text-anchor="middle" x="${xPos(v)}" y="${height - margin.bottom + 15}">${qEsc(formatLogTick(v))}</text>`)
        .join("");
    const labelsY = yTickValues
        .map((v) => `<text class="mip-axis-tick" text-anchor="end" x="${margin.left - 8}" y="${yPos(v) + 3}">${qEsc(formatLogTick(v))}</text>`)
        .join("");

    // Each point is a small visible dot (.mip-dot) plus a much larger transparent
    // hit circle (.mip-point) sharing the same centre. The r="4" dot alone is only
    // ~9px across — too small to reliably hover/tap; the hit circle widens the
    // pointer/touch target to ~24px without cluttering the scatter. The hit circle
    // carries all the data + interaction (it sits on top, so it catches the event);
    // the dot is inert (pointer-events:none) and gets the active/hover styling.
    const circles = positivePoints
        .map((p, idx) => {
            const href = qInstanceUrl(p.problem_id, p.name);
            // Use the computed key everywhere (colors, legend, and this group's
            // data-model-key) so legend toggles reliably match their points.
            const color = colorForModelKey(modelKeyForPoint(p), p.problem_id);
            const cx = xPos(p.num_vars);
            const cy = yPos(p.density);
            const modelKey = qEsc(modelKeyForPoint(p));
            return `
                <g class="mip-pt" data-model-key="${modelKey}">
                    <circle
                        class="mip-dot"
                        id="mip-point-${idx}"
                        cx="${cx}"
                        cy="${cy}"
                        style="--p-fill:${qEsc(color.fill)};--p-stroke:${qEsc(color.stroke)}"
                        r="4"
                    ></circle>
                    <circle
                        class="mip-point"
                        data-idx="${idx}"
                        data-name="${qEsc(p.name)}"
                        data-problem="${qEsc(p.problem_id)}"
                        data-model-key="${modelKey}"
                        data-vars="${p.num_vars}"
                        data-density="${p.density}"
                        data-model="${qEsc(p.model_approach || p.model_kind || "model")}"
                        data-url="${qEsc(href)}"
                        cx="${cx}"
                        cy="${cy}"
                        r="12"
                        tabindex="0"
                        role="link"
                        aria-label="${qEsc(p.name)}"
                    ></circle>
                </g>`;
        })
        .join("");

    root.innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" aria-label="MIP instance scatter plot">
            <g>
                ${gridX}
                ${gridY}
                <line class="mip-axis-line" x1="${margin.left}" y1="${height - margin.bottom}" x2="${width - margin.right}" y2="${height - margin.bottom}" />
                <line class="mip-axis-line" x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${height - margin.bottom}" />
                ${labelsX}
                ${labelsY}
                <text class="mip-axis-label" text-anchor="middle" x="${margin.left + plotW / 2}" y="${height - 10}">Number of Variables (log scale)</text>
                <text class="mip-axis-label" text-anchor="middle" transform="translate(16 ${margin.top + plotH / 2}) rotate(-90)">Density (log scale)</text>
                ${circles}
            </g>
        </svg>
        <div class="mip-tooltip" id="mip-tooltip">
            <div class="mip-tooltip-title">Hover or focus a point</div>
            <div class="mip-tooltip-row"><span>Instance</span><strong>-</strong></div>
            <div class="mip-tooltip-row"><span>Variables</span><strong>-</strong></div>
            <div class="mip-tooltip-row"><span>Density</span><strong>-</strong></div>
        </div>`;

    const tooltip = document.getElementById("mip-tooltip");
    const pointsEls = Array.from(root.querySelectorAll(".mip-point"));

    // Move the "active" highlight onto the *visible* dot (the sibling of the
    // transparent hit circle that actually receives the event), since the dot is
    // what carries the fill/radius styling.
    const activatePoint = (el) => {
        root.querySelectorAll(".mip-dot.active").forEach((d) => d.classList.remove("active"));
        el.previousElementSibling?.classList.add("active");
        tooltip.innerHTML = `
            <div class="mip-tooltip-title">${qEsc(el.dataset.name || "")}</div>
            <div class="mip-tooltip-row"><span>Problem</span><strong>${qEsc(el.dataset.problem || "")}</strong></div>
            <div class="mip-tooltip-row"><span>Model</span><strong>${qEsc(prettyModelLabel(el.dataset.model || "model"))}</strong></div>
            <div class="mip-tooltip-row"><span>Variables</span><strong>${qEsc(qFmtNum(Number(el.dataset.vars || 0)))}</strong></div>
            <div class="mip-tooltip-row"><span>Density</span><strong>${qEsc(formatDensity(Number(el.dataset.density || 0)))}</strong></div>`;
    };

    pointsEls.forEach((el) => {
        el.addEventListener("mouseenter", () => activatePoint(el));
        el.addEventListener("focus", () => activatePoint(el));
        el.addEventListener("click", () => {
            const href = el.dataset.url;
            if (href) window.location.href = href;
        });
        el.addEventListener("keydown", (ev) => {
            if (ev.key === "Enter" || ev.key === " ") {
                ev.preventDefault();
                const href = el.dataset.url;
                if (href) window.location.href = href;
            }
        });
    });

    if (pointsEls[0]) activatePoint(pointsEls[0]);
    updateMipPointVisibility();
}

async function initInstancesPage() {
    qInitCommon();
    try {
        // One aggregated, trimmed request (data/instances.json) backs the whole
        // page — instance rows, the per-problem column metadata, and the MIP
        // scatter points — instead of fetching 1 + 2×N per-problem files.
        const agg = await qLoadInstancesList();
        const problems = agg.problems || [];

        const filter = document.getElementById("i-prob");
        problems.forEach((p) => {
            const o = document.createElement("option");
            o.value = p.id;
            o.textContent = `${String(p.id).padStart(2, "0")} - ${p.name}`;
            filter.appendChild(o);
        });

        allInstances = problems.flatMap((p) => {
            const cols = Array.isArray(p.columns) ? p.columns : [];
            return (p.instances || []).map((inst) => ({
                ...inst,
                problem_id: p.id,
                problem_name: p.name,
                metrics_text: cols
                    .filter((c) => inst.metrics && inst.metrics[c.key] != null && inst.metrics[c.key] !== "")
                    .map((c) => `${qEsc(c.label)} ${c.numeric ? qFmtNum(inst.metrics[c.key]) : qEsc(inst.metrics[c.key])}`)
                    .join(" · "),
                metrics_plain: cols
                    .filter((c) => inst.metrics && inst.metrics[c.key] != null && inst.metrics[c.key] !== "")
                    .map((c) => `${c.label} ${inst.metrics[c.key]}`)
                    .join(" · "),
            }));
        });

        // Scatter points are pre-baked per problem at build time (see metrics.py)
        // and carried in the same aggregate.
        renderMipChart(problems.flatMap((p) => p.points || []));
        qEnhanceFigures(document); // expand affordance on the MIP instance map

        renderInstances();
    } catch (error) {
        qShowError(document.getElementById("instances-table"), error.message);
        qShowError(document.getElementById("mip-chart"), error.message);
    }
}

function getFilteredInstances() {
    const q = (document.getElementById("i-search")?.value || "").toLowerCase();
    const pid = document.getElementById("i-prob")?.value || "";
    const st = document.getElementById("i-status")?.value || "";

    let rows = allInstances.filter(
        (r) =>
            (!q || r.name.toLowerCase().includes(q) || r.problem_name.toLowerCase().includes(q) || r.status.toLowerCase().includes(q)) &&
            (!pid || r.problem_id === pid) &&
            (!st || r.status === st),
    );

    rows.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }));

    return rows;
}

function downloadInstancesCsv() {
    let rows = getFilteredInstances();
    // Honour the user's clicked-column sort so the CSV matches the visible table.
    const table = document.querySelector("#instances-table table");
    if (table) rows = qOrderRowsByTable(table, rows, rows.map((r) => `${r.problem_id}::${r.name}`));
    const headers = ["Problem ID", "Problem", "Instance", "Parameters", "Best objective", "Optimal", "Source", "Source URL", "Status", "Raw URL"];
    const data = rows.map((r) => [
        String(r.problem_id).padStart(2, "0"),
        r.problem_name,
        r.name,
        r.metrics_plain || "",
        r.best_value ?? r.bkv ?? "",
        r.best_is_optimal ? "yes" : "",
        r.best_source_label || r.best_source_type || "",
        r.best_source_url || "",
        r.status,
        r.raw_url || "",
    ]);
    qDownloadCsv("qoblib_instances.csv", headers, data);
}

function renderInstances() {
    const rows = getFilteredInstances();

    const countEl = document.getElementById("i-count");
    if (countEl) countEl.textContent = `${rows.length.toLocaleString()} instance${rows.length !== 1 ? "s" : ""}`;

    const tbody = document.getElementById("i-tbody");
    if (!tbody) return;
    tbody.innerHTML =
        rows
            .map(
                (r) => `
                <tr data-export-key="${qEsc(String(r.problem_id) + "::" + r.name)}">
                    <td><a class="rlink mono" href="${qInstanceUrl(r.problem_id, r.name)}">${qEsc(r.name)}</a></td>
                    <td><a class="badge b-type" href="${qProblemUrl(r.problem_id)}">${String(r.problem_id).padStart(2, "0")} ${qEsc(r.problem_name)}</a></td>
                    <td class="notes-cell" title="${r.metrics_text || ""}">${r.metrics_text || "-"}</td>
                    <td class="num">${(() => { const v = qFmtNum(r.best_value ?? r.bkv); return r.best_is_optimal && v !== "-" ? `<strong>${v}</strong>` : v; })()}</td>
                    <td>${r.best_source_url ? `<a class="dl" href="${qEsc(r.best_source_url)}" target="_blank" rel="noopener">${qEsc(r.best_source_label || r.best_source_type || "source")}</a>` : "-"}</td>
                    <td>${qStatusPill(r.status)}</td>
                    <td>${r.raw_url ? `<a class="dl" href="${qEsc(r.raw_url)}" target="_blank" rel="noopener">↓ raw</a>` : "-"}</td>
                </tr>`,
            )
            .join("") || '<tr><td colspan="7" class="text-center padded">No instances match the current filters.</td></tr>';

    // Re-apply the user's column sort to the freshly rendered rows so filtering or
    // searching doesn't silently snap the table back to the default name order.
    document.querySelector("#instances-table table")?.reapplySort?.();
}

window.renderInstances = renderInstances;
window.downloadInstancesCsv = downloadInstancesCsv;

document.getElementById("i-search")?.addEventListener("input", renderInstances);
document.getElementById("i-prob")?.addEventListener("change", renderInstances);
document.getElementById("i-status")?.addEventListener("change", renderInstances);
document.getElementById("i-download")?.addEventListener("click", downloadInstancesCsv);

initInstancesPage();
