"use strict";

const {
    esc: qEsc,
    fmtBytes: qFmtBytes,
    fmtNum: qFmtNum,
    fmtInt: qFmtInt,
    fmtText: qFmtText,
    fmtDate: qFmtDate,
    parseDate: qParseDate,
    submissionDate: qSubmissionDate,
    submissionMethod: qSubmissionMethod,
    loadProblemData: qLoadProblemData,
    loadProblemSubmissionGroups: qLoadProblemSubmissionGroups,
    loadProblemCharts: qLoadProblemCharts,
    instanceUrl: qInstanceUrl,
    problemUrl: qProblemUrl,
    submissionUrl: qSubmissionUrl,
    statusPill: qStatusPill,
    catBadge: qCatBadge,
    renderMarkdown: qRenderMarkdown,
    renderMath: qRenderMath,
    showError: qShowError,
    initCommon: qInitCommon,
    classifySubmission: qClassify,
    SUBMISSION_CATEGORIES: qCATS,
    downloadCsv: qDownloadCsv,
    setPageMeta: qSetPageMeta,
    attachFigureExpand: qAttachFigureExpand,
    enhanceFigures: qEnhanceFigures,
} = window.QOBLIB;

// ---------------------------------------------------------------------------
// Performance section for the problem's instance family — three charts that
// share one "by paradigm / by submission" grouping toggle (so a given method
// keeps the same colour across all three):
//   • Cactus — runtime to reach the best-known objective.
//   • Performance profile — share of instances within a given optimality gap.
//   • Scaling — fastest feasible runtime versus instance size.
//
// The chart SVGs are PRE-RENDERED at build time (misc/ci/site_builder/charts.py,
// emitted to data/problems/<id>/charts.json) so the browser no longer recomputes
// them on every page load — it just injects the prebaked markup for the active
// grouping mode and viewport. Keep charts.py in sync if the chart maths change.
// ---------------------------------------------------------------------------

let PERF = null; // prebaked charts payload for the current problem (or null)
let PERF_MODE = "paradigm";
let currentProblem = null;

const PERF_CHARTS = [
    { key: "cactus", id: "cactus-body", has: "has_cactus" },
    { key: "profile", id: "profile-body", has: "has_profile" },
    { key: "scaling", id: "scaling-body", has: "has_scaling" },
];

// Wide layout on desktop; a taller, narrower aspect on phones so a single
// full-width chart stays legible. Mirrors the old perfDims breakpoint and
// selects which prebaked variant to inject.
function perfBreakpoint() {
    return window.innerWidth <= 640 ? "narrow" : "wide";
}

// Build the performance-section scaffolding (toolbar + chart cards) from the
// pre-rendered payload. Records module state used by wirePerformance/renderPerf.
// Returns "" when there is nothing to plot.
function performanceSection(charts) {
    PERF = charts && charts.modes && (charts.has_cactus || charts.has_profile || charts.has_scaling) ? charts : null;
    PERF_MODE = "paradigm";
    if (!PERF) return "";

    const sizeLabel = PERF.size_label || "size";
    const card = (id, title, desc) =>
        `<section class="tw chart-card"><div class="chart-head"><div><h3>${qEsc(title)}</h3><p>${qEsc(desc)}</p></div></div><div id="${id}"></div></section>`;

    return `<div class="perf-toolbar">
            <div class="seg-toggle" role="tablist" aria-label="Grouping">
                <button type="button" class="seg-btn on" data-mode="paradigm">By paradigm</button>
                <button type="button" class="seg-btn" data-mode="submission">By submission</button>
            </div>
        </div>
        <div class="perf-charts">
            ${PERF.has_cactus ? card("cactus-body", "Runtime to reach the best-known objective", "Each curve sorts a group's solved instances by total runtime — a point (x, y) means it reached the best-known objective on x instances, each within y seconds. Lower and further right is better.") : ""}
            ${PERF.has_profile ? card("profile-body", "Solution quality (performance profile)", "Share of instances each group brings within a given optimality gap of the best-known objective. Higher is better; the value at “best” is the share solved exactly.") : ""}
            ${PERF.has_scaling ? card("scaling-body", "Runtime scaling with instance size", `Fastest feasible runtime per instance versus ${sizeLabel}, both on log scales — shows how each group scales.`) : ""}
        </div>`;
}

// Inject the prebaked chart bodies for the active grouping mode + viewport.
function renderPerf() {
    if (!PERF) return;
    const bp = perfBreakpoint();
    const mode = (PERF.modes && PERF.modes[PERF_MODE]) || {};
    PERF_CHARTS.forEach(({ key, id, has }) => {
        if (!PERF[has]) return;
        const body = document.getElementById(id);
        if (!body) return;
        const variants = mode[key];
        body.innerHTML = (variants && variants[bp]) || "";
    });
}

function wirePerformance() {
    const tb = document.querySelector(".perf-toolbar");
    if (!tb || !PERF) return;
    tb.querySelectorAll(".seg-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            tb.querySelectorAll(".seg-btn").forEach((b) => b.classList.toggle("on", b === btn));
            PERF_MODE = btn.dataset.mode;
            renderPerf();
        });
    });
    renderPerf();
}

// Re-inject the matching aspect when the viewport crosses the phone breakpoint
// so the charts swap between the wide and the taller mobile variant.
let perfNarrow = window.innerWidth <= 640;
let perfResizeTimer = null;
window.addEventListener("resize", () => {
    if (!PERF) return;
    const narrow = window.innerWidth <= 640;
    if (narrow === perfNarrow) return;
    perfNarrow = narrow;
    clearTimeout(perfResizeTimer);
    perfResizeTimer = setTimeout(renderPerf, 150);
});

// Wrap a page section in a native <details> so it can be collapsed. Open by
// default; `count` is shown as a subtle "(N)" after the title.
function collapsibleSection(title, bodyHtml, count = null) {
    const label = count != null ? `${qEsc(title)} <span class="ps-count">(${count})</span>` : qEsc(title);
    return `<details class="prob-section" open>
        <summary class="prob-section-head">${label}</summary>
        <div class="prob-section-body">${bodyHtml}</div>
    </details>`;
}

// Submission packages for this problem, newest first. Each row links to the
// package's detail page; mirrors the global submissions table, scoped here.
function submissionsSection(p, groups) {
    if (!groups.length) {
        return `<div class="empty-state">No submissions for this problem yet. <a class="sh-link" href="submit.html">Submit one →</a></div>`;
    }
    const sorted = [...groups].sort((a, b) => {
        const ta = qParseDate(qSubmissionDate(a));
        const tb = qParseDate(qSubmissionDate(b));
        return (Number.isFinite(tb) ? tb : -Infinity) - (Number.isFinite(ta) ? ta : -Infinity) ||
            String(a.id).localeCompare(String(b.id));
    });
    const rows = sorted
        .map((g) => {
            const prof = g.profile || {};
            const cat = g.category || qClassify(prof);
            // The package name already carries the date + author; show the method.
            return `<tr>
                <td><a class="rlink" href="${qSubmissionUrl(p.id, g.id)}" title="${qEsc(g.id)}">${qEsc(qSubmissionMethod(g))}</a></td>
                <td>${qFmtText(prof.submitter)}</td>
                <td title="${qEsc((qCATS[cat] || qCATS.classical).label)}">${qCatBadge(cat)}</td>
                <td class="mono">${qEsc(qFmtDate(qSubmissionDate(g)))}</td>
                <td class="num">${(g.instances || []).length.toLocaleString()}</td>
            </tr>`;
        })
        .join("");
    return `<div class="tw"><table>
        <thead>
            <tr>
                <th>Method</th>
                <th>Submitter</th>
                <th>Type</th>
                <th data-sort-default="desc">Date</th>
                <th style="text-align:right">Instances</th>
            </tr>
        </thead>
        <tbody>${rows}</tbody>
    </table></div>`;
}

function getProblemRawBase(problem) {
    const url = String(problem?.github_url || "");
    const match = url.match(/^https:\/\/github\.com\/([^/]+)\/([^/]+)\/(tree|blob)\/([^/]+)\/(.+)$/i);
    if (!match) return null;
    const owner = match[1];
    const repo = match[2];
    const branch = match[4];
    const path = match[5];
    return `https://raw.githubusercontent.com/${owner}/${repo}/${branch}/${path}/`;
}

function rewriteDescriptionImageSources(html, problem) {
    if (!html) return html;

    // A bespoke inline figure (assets/problem_figures.js) replaces the README
    // image entirely — strip it so the browser never fetches a PNG we'd discard.
    if ((window.QOBLIB_PROBLEM_FIGURES || {})[problem?.slug]) {
        return html.replace(/<img\b[^>]*>/gi, "");
    }

    const rawBase = getProblemRawBase(problem);
    if (!rawBase) return html;

    return html.replace(/(<img\b[^>]*\bsrc\s*=\s*["'])([^"']+)(["'][^>]*>)/gi, (full, prefix, src, suffix) => {
        const normalized = String(src || "").trim();
        const isAbsolute = /^(?:https?:)?\/\//i.test(normalized) || normalized.startsWith("/") || normalized.startsWith("data:");
        if (isAbsolute) return full;

        const cleaned = normalized.replace(/^\.\//, "");
        return `${prefix}${rawBase}${cleaned}${suffix}`;
    });
}

function layoutDescriptionImage(descRoot, problem) {
    if (!descRoot) return;

    // Prefer our own theme-aware inline SVG (assets/problem_figures.js), keyed by
    // the problem slug. It replaces any figure embedded in the README so every
    // problem shows a figure in the site colour scheme, light or dark.
    const figureSvg = (window.QOBLIB_PROBLEM_FIGURES || {})[problem?.slug];

    const content = document.createElement("div");
    content.className = "d-desc-content";
    while (descRoot.firstChild) {
        content.appendChild(descRoot.firstChild);
    }

    // Drop the README's own image (we render our own visual instead).
    const readmeImg = content.querySelector("img");
    if (readmeImg) {
        const imgContainer = readmeImg.closest("figure, p, div");
        if (imgContainer && imgContainer !== content &&
            (imgContainer.tagName.toLowerCase() === "p" ||
             (imgContainer.children.length === 1 && imgContainer.textContent.trim() === ""))) {
            imgContainer.remove();
        } else {
            readmeImg.remove();
        }
    }

    const visual = document.createElement("div");
    visual.className = "d-desc-visual";
    if (figureSvg) {
        visual.innerHTML = figureSvg;
    } else if (readmeImg) {
        // No bespoke figure for this problem — fall back to the README image.
        const visualImg = readmeImg.cloneNode(true);
        visualImg.removeAttribute("align");
        visualImg.removeAttribute("width");
        visualImg.removeAttribute("height");
        visual.appendChild(visualImg);
    } else {
        // Nothing to show alongside — leave the description full-width.
        descRoot.appendChild(content);
        return;
    }

    qAttachFigureExpand(visual);

    const firstElement = content.firstElementChild;
    const leadHeading =
        firstElement && /^(H1|H2|H3)$/i.test(firstElement.tagName) ? firstElement : null;

    const columns = document.createElement("div");
    columns.className = "d-desc-columns";
    columns.appendChild(content);
    columns.appendChild(visual);

    descRoot.innerHTML = "";
    descRoot.classList.add("d-desc-layout");
    if (leadHeading) descRoot.appendChild(leadHeading);
    descRoot.appendChild(columns);
}

async function initProblemPage() {
    qInitCommon();
    const params = new URLSearchParams(window.location.search);
    // ?id= on the problem.html shell, or data-problem-id on the static
    // /problem/<id>/ pages generated at build time.
    const id = params.get("id") || document.body.dataset.problemId || "";
    const container = document.getElementById("prob-detail");

    if (!id) {
        qShowError(container, "Missing problem id in URL.");
        return;
    }

    try {
        const [p, submissionGroups, charts] = await Promise.all([
            qLoadProblemData(id),
            qLoadProblemSubmissionGroups(id).catch(() => []),
            qLoadProblemCharts(id).catch(() => null),
        ]);
        currentProblem = p;
        qSetPageMeta({ title: `${p.name} — QOBLIB`, canonical: `problem/${encodeURIComponent(p.id)}/` });
        // "Optimally solved" is method-agnostic: any instance whose status is
        // optimal/solved counts, regardless of whether a classical or quantum
        // submission proved it. Prefer the authoritative build-side count so this
        // matches the home-page total exactly; fall back to recomputing.
        const solved = Number.isFinite(p.solved_count)
            ? p.solved_count
            : (p.instances || []).filter((i) => ["optimal", "solved"].includes(i.status)).length;
        const renderedDesc = p.description_md ? rewriteDescriptionImageSources(qRenderMarkdown(p.description_md), p) : null;

        // Problem-specific instance columns (e.g. Nodes / Edges for MIS).
        const metricCols = Array.isArray(p.columns) ? p.columns : [];
        const metricHead = metricCols
            .map((c) => `<th${c.numeric ? ' style="text-align:right"' : ""}>${qEsc(c.label)}</th>`)
            .join("");

        // Build once (performanceSection records module state used by wirePerformance).
        const perfBody = performanceSection(charts);

        container.innerHTML = `
            <div class="dh">
                <div>
                    <div class="d-num">${String(p.id).padStart(2, "0")} / ${qEsc(p.slug)}</div>
                    <div class="d-title">${qEsc(p.name)}</div>
                    <div class="d-sub">${qEsc(p.short)}</div>
                    <div class="pcard-foot">
                        <span class="badge b-type">${qEsc(p.type)}</span>
                        <span class="badge b-form">${qEsc(p.formulation)}</span>
                        ${(p.tags || []).map((t) => `<span class="badge b-tag">${qEsc(t)}</span>`).join("")}
                    </div>
                </div>
                <div class="d-meta">
                    <div class="mr"><span class="mk">Instances</span><span class="mv">${qFmtInt(p.instance_count)}</span></div>
                    <div class="mr"><span class="mk">Optimally solved</span><span class="mv">${qFmtInt(solved)} / ${qFmtInt(p.instance_count)}</span></div>
                    ${p.vars_min != null ? `<div class="mr"><span class="mk">Variable range</span><span class="mv">${qFmtInt(p.vars_min)}–${qFmtInt(p.vars_max)}</span></div>` : ""}
                    <div class="mr"><span class="mk">Objective</span><span class="mv">${p.minimize ? "minimize" : "maximize"}</span></div>
                </div>
            </div>
            ${p.description_md || p.description ? `<hr class="section-divider" />` : ""}
            ${p.description_md ? `<div class="d-desc">${renderedDesc}</div>` : p.description ? `<p class="d-desc">${qEsc(p.description)}</p>` : ""}
            ${!p.description_md && p.formula ? `<div class="formula">${qEsc(p.formula)}</div>` : ""}

            ${perfBody ? collapsibleSection("Performance", perfBody) : ""}

            ${collapsibleSection("Submissions", submissionsSection(p, submissionGroups), submissionGroups.length)}

            ${collapsibleSection("Instances", `
                <div class="filters">
                    <input type="text" class="fi-grow" id="prob-inst-search" placeholder="Search by instance name..." oninput="filterProblemInstances()" />
                    <span class="fi-count" id="prob-inst-count">${(p.instances || []).length.toLocaleString()} of ${(p.instances || []).length.toLocaleString()}</span>
                    <button class="btn btn-ghost btn-sm" type="button" onclick="downloadProblemInstancesCsv()">⬇ Download CSV</button>
                </div>
                <div class="tw">
                    <table>
                        <thead>
                            <tr>
                                <th data-sort-default="asc">Name</th>
                                ${metricHead}
                                <th style="text-align:right">Best objective</th>
                                <th>Source</th>
                                <th>Status</th>
                                <th>Download</th>
                            </tr>
                        </thead>
                        <tbody id="prob-inst-tbody">${problemInstanceRowsHtml(p, filteredProblemInstances(p, ""))}</tbody>
                    </table>
                </div>`, p.instance_count)}

            <div class="hero-actions" style="margin-top:1.5rem">
                ${p.github_url ? `<a class="btn btn-ghost" href="${qEsc(p.github_url)}" target="_blank" rel="noopener">View on GitHub ↗</a>` : ""}
                <a class="btn btn-navy" href="leaderboard.html">View Leaderboard</a>
                <a class="btn btn-ghost" href="instances.html">Browse All Instances</a>
            </div>
        `;

        wirePerformance();

        const desc = container.querySelector(".d-desc");
        if (desc) {
            layoutDescriptionImage(desc, p);
            qRenderMath(desc);
        }

        // Add the "Expand" affordance to the performance charts (the README
        // figure is wired inside layoutDescriptionImage). Run after the chart
        // SVGs have been injected by wirePerformance() so they are present.
        qEnhanceFigures(container);
    } catch (error) {
        qShowError(container, error.message);
    }
}

// ---- Instances table (searchable) ----------------------------------------
// The table is re-rendered on search (rather than hiding rows) so the zebra
// striping recomputes over the visible set. Sorted by name (see the table's
// data-sort-default), filtered by a case-insensitive substring of the name.
function problemMetricCols(p) {
    return Array.isArray(p && p.columns) ? p.columns : [];
}

function problemMetricCells(inst, cols) {
    return cols
        .map((c) => {
            const v = inst.metrics ? inst.metrics[c.key] : undefined;
            if (v == null || v === "") return `<td${c.numeric ? ' class="num"' : ""}>-</td>`;
            return `<td${c.numeric ? ' class="num"' : ""}>${c.numeric ? qFmtNum(v) : qEsc(v)}</td>`;
        })
        .join("");
}

function filteredProblemInstances(p, query) {
    const q = String(query || "").trim().toLowerCase();
    return [...(p.instances || [])]
        .filter((i) => !q || String(i.name || "").toLowerCase().includes(q))
        .sort((a, b) => String(a.name || "").localeCompare(String(b.name || "")));
}

function problemInstanceRowsHtml(p, list) {
    const cols = problemMetricCols(p);
    if (!list.length) {
        return `<tr><td colspan="${5 + cols.length}" class="text-center padded">No instances match the search.</td></tr>`;
    }
    return list
        .map(
            (i) => `
            <tr>
                <td class="mono"><a class="rlink mono" href="${qInstanceUrl(p.id, i.name)}">${qEsc(i.name)}</a></td>
                ${problemMetricCells(i, cols)}
                <td class="num">${(() => { const v = qFmtNum(i.best_value ?? i.bkv); return i.best_is_optimal && v !== "-" ? `<strong>${v}</strong>` : v; })()}</td>
                <td>${i.best_source_url ? `<a class="dl" href="${qEsc(i.best_source_url)}" target="_blank" rel="noopener">${qEsc(i.best_source_label || i.best_source_type || "source")}</a>` : "-"}</td>
                <td>${qStatusPill(i.status)}</td>
                <td>${i.raw_url ? `<a class="dl" href="${qEsc(i.raw_url)}" target="_blank" rel="noopener">↓ raw</a>` : "-"}</td>
            </tr>`,
        )
        .join("");
}

function filterProblemInstances() {
    if (!currentProblem) return;
    const query = document.getElementById("prob-inst-search")?.value || "";
    const list = filteredProblemInstances(currentProblem, query);
    const tbody = document.getElementById("prob-inst-tbody");
    if (tbody) {
        tbody.innerHTML = problemInstanceRowsHtml(currentProblem, list);
        // Keep the user's chosen column sort after the search re-renders rows.
        tbody.closest("table")?.reapplySort?.();
    }
    const countEl = document.getElementById("prob-inst-count");
    if (countEl) {
        const total = (currentProblem.instances || []).length;
        countEl.textContent = `${list.length.toLocaleString()} of ${total.toLocaleString()}`;
    }
}

window.filterProblemInstances = filterProblemInstances;

function downloadProblemInstancesCsv() {
    const p = currentProblem;
    if (!p) return;
    const cols = Array.isArray(p.columns) ? p.columns : [];
    const headers = ["Instance", ...cols.map((c) => c.label), "Best objective", "Optimal", "Status", "Source", "Source URL", "Raw URL"];
    const data = (p.instances || []).map((i) => [
        i.name,
        ...cols.map((c) => (i.metrics && i.metrics[c.key] != null ? i.metrics[c.key] : "")),
        i.best_value ?? i.bkv ?? "",
        i.best_is_optimal ? "yes" : "",
        i.status,
        i.best_source_label || i.best_source_type || "",
        i.best_source_url || "",
        i.raw_url || "",
    ]);
    qDownloadCsv(`qoblib_${p.slug || p.id}_instances.csv`, headers, data);
}

window.downloadProblemInstancesCsv = downloadProblemInstancesCsv;

initProblemPage();
