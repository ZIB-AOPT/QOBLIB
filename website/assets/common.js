"use strict";

const cache = new Map();
let INDEX = null;
const META_CACHE = new Map();
const INSTANCES_CACHE = new Map();
const INSTANCE_SUBS_CACHE = new Map();
const SUBMISSIONS_CACHE = new Map();
const SUBMISSION_GROUPS_CACHE = new Map();
const CHARTS_CACHE = new Map();
const MIP_POINTS_CACHE = new Map();
let ALL_SUBMISSION_GROUPS_CACHE = null;
let TABLE_SORT_OBSERVER = null;

function esc(s) {
    return String(s ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function safeUrl(value) {
    const s = String(value ?? "").trim();
    if (!s) return true;
    if (s.startsWith("#") || s.startsWith("/") || s.startsWith("./") || s.startsWith("../")) return true;
    const match = s.match(/^([a-z][a-z0-9+.-]*):/i);
    return !match || ["http", "https", "mailto"].includes(match[1].toLowerCase());
}

function sanitizeHtml(html) {
    if (typeof document === "undefined") return esc(html);

    const template = document.createElement("template");
    template.innerHTML = String(html ?? "");
    const allowedTags = new Set([
        "A", "B", "BLOCKQUOTE", "BR", "CODE", "DD", "DEL", "DIV", "DL", "DT", "EM",
        "FIGCAPTION", "FIGURE", "H1", "H2", "H3", "H4", "H5", "H6", "HR", "I", "IMG",
        "LI", "OL", "P", "PRE", "S", "SPAN", "STRONG", "SUB", "SUP", "TABLE", "TBODY",
        "TD", "TH", "THEAD", "TR", "UL",
    ]);
    const removeWithContent = new Set(["SCRIPT", "STYLE", "IFRAME", "OBJECT", "EMBED", "LINK", "META", "BASE"]);
    const globalAttrs = new Set(["title"]);
    const tagAttrs = {
        A: new Set(["href", "title"]),
        IMG: new Set(["src", "alt", "title", "width", "height"]),
        TH: new Set(["colspan", "rowspan", "align"]),
        TD: new Set(["colspan", "rowspan", "align"]),
    };
    const urlAttrs = new Set(["href", "src"]);

    function sanitizeNode(node) {
        if (node.nodeType === Node.TEXT_NODE) return;
        if (node.nodeType !== Node.ELEMENT_NODE) {
            node.remove();
            return;
        }

        const tag = node.tagName.toUpperCase();
        if (removeWithContent.has(tag)) {
            node.remove();
            return;
        }
        if (!allowedTags.has(tag)) {
            const parent = node.parentNode;
            while (node.firstChild) parent.insertBefore(node.firstChild, node);
            node.remove();
            sanitizeChildren(parent);
            return;
        }

        const allowedAttrs = tagAttrs[tag] || new Set();
        for (const attr of Array.from(node.attributes)) {
            const name = attr.name.toLowerCase();
            const allowed = globalAttrs.has(name) || allowedAttrs.has(attr.name) || allowedAttrs.has(name);
            if (!allowed || name.startsWith("on") || name === "style") {
                node.removeAttribute(attr.name);
                continue;
            }
            if (urlAttrs.has(name) && !safeUrl(attr.value)) {
                node.removeAttribute(attr.name);
            }
        }

        sanitizeChildren(node);
    }

    function sanitizeChildren(parent) {
        for (const child of Array.from(parent.childNodes)) sanitizeNode(child);
    }

    sanitizeChildren(template.content);
    return template.innerHTML;
}

function fmtBytes(b) {
    if (b == null) return "-";
    if (b < 1024) return `${b} B`;
    if (b < 1024 ** 2) return `${(b / 1024).toFixed(1)} KB`;
    return `${(b / 1024 ** 2).toFixed(2)} MB`;
}

function fmtNum(n) {
    if ((n ?? "-") === "-") return "-";
    return Number(n).toLocaleString(undefined, { maximumFractionDigits: 4 });
}

// Integer counts (instances, variables, …) — locale grouping, no decimals.
// Used for every raw count so large values get thousands separators site-wide.
function fmtInt(n) {
    if (n == null || n === "" || !Number.isFinite(Number(n))) return "-";
    return Math.round(Number(n)).toLocaleString();
}

// A value that is usually numeric (runtime, objective, …) but occasionally a
// free-text marker like "N/A". Format numbers with locale grouping; pass other
// text through escaped. Shared so runtimes look identical on every page.
function fmtMaybeNum(v) {
    if (v == null || v === "") return "-";
    const compact = typeof v === "string" ? v.replace(/,/g, "").trim() : v;
    const num = Number(compact);
    return Number.isFinite(num) && compact !== "" ? fmtNum(num) : esc(String(v));
}

function fmtText(v) {
    return v == null || v === "" ? "-" : esc(v);
}

// --- dates -------------------------------------------------------------------
// Submission dates reach the frontend in assorted shapes depending on how each
// author wrote them in the source CSV / submission directory name (ISO,
// compact YYYYMMDD, "22. Dec. 2024", "Dec 22, 2024", day-first DD.MM.YYYY, ...).
// `parseDate` understands all of those and returns a UTC timestamp; `fmtDate`
// renders the canonical YYYY-MM-DD used everywhere a date is shown, so every
// page prints dates the same way regardless of the original format.
const DATE_MONTHS = {
    jan: 1, feb: 2, mar: 3, apr: 4, may: 5, jun: 6,
    jul: 7, aug: 8, sep: 9, oct: 10, nov: 11, dec: 12,
};

function parseDate(v) {
    const s = String(v == null ? "" : v).trim();
    if (!s) return NaN;
    let m;
    let y;
    let mo;
    let d;
    if ((m = s.match(/^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})/))) {
        // Year-first: ISO 8601, YYYY-MM-DD, YYYY/MM/DD (time portion ignored).
        [, y, mo, d] = m;
    } else if ((m = s.match(/^(\d{4})(\d{2})(\d{2})$/))) {
        // Compact YYYYMMDD (e.g. the 20241206 prefix on submission directories).
        [, y, mo, d] = m;
    } else if ((m = s.match(/^(\d{1,2})[.\s]+([A-Za-z]{3,})\.?[,\s]+(\d{4})$/))) {
        // Day-first with a month name: "22 Dec 2024", "22. Dec. 2024".
        [, d, , y] = m;
        mo = DATE_MONTHS[m[2].slice(0, 3).toLowerCase()];
    } else if ((m = s.match(/^([A-Za-z]{3,})\.?\s+(\d{1,2})[,.\s]+(\d{4})$/))) {
        // Month name first: "Dec 22, 2024".
        [, , d, y] = m;
        mo = DATE_MONTHS[m[1].slice(0, 3).toLowerCase()];
    } else if ((m = s.match(/^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})$/))) {
        // Day-first numeric, the common European source form: DD.MM.YYYY.
        [, d, mo, y] = m;
    }
    if (y != null && mo != null && d != null) {
        const yi = Number(y);
        const moi = Number(mo);
        const di = Number(d);
        if (moi >= 1 && moi <= 12 && di >= 1 && di <= 31) {
            const ms = Date.UTC(yi, moi - 1, di);
            if (Number.isFinite(ms)) return ms;
        }
    }
    const t = Date.parse(s); // last resort: let the engine try the raw string.
    return Number.isFinite(t) ? t : NaN;
}

function fmtDate(v) {
    const ms = parseDate(v);
    if (!Number.isFinite(ms)) {
        // Unparseable — keep the author's original text rather than show nothing.
        const s = String(v == null ? "" : v).trim();
        return s || "-";
    }
    const dt = new Date(ms);
    const mm = String(dt.getUTCMonth() + 1).padStart(2, "0");
    const dd = String(dt.getUTCDate()).padStart(2, "0");
    return `${dt.getUTCFullYear()}-${mm}-${dd}`;
}

// Submission package directories are named "YYYYMMDD_<method>_<author>", so the
// date and the method are recoverable from the name even when a submission's own
// metadata is missing. Used by the submission tables and detail page.
function submissionDate(group) {
    // Prefer the submission's own date; fall back to the package-name date prefix
    // when that is missing or unparseable (some packages have a blank date field).
    const own = group?.profile?.date;
    if (Number.isFinite(parseDate(own))) return own;
    const m = String(group?.source_dir || group?.id || "").match(/^(\d{6,8})_/);
    return m && Number.isFinite(parseDate(m[1])) ? m[1] : own || "";
}

function submissionMethod(group) {
    const id = String(group?.source_dir || group?.id || "").trim();
    const m = id.match(/^\d{6,8}_(.+)_[^_]+$/);
    return m ? m[1].replace(/_/g, " ") : id;
}

// Pretty per-problem URL (e.g. problem/07/). The build generates a static page
// at each of these (misc/ci/site_builder/html_pages.py); problem.html?id= still
// works as a fallback. Relative form resolves against <base> on the deep pages
// and against the site root elsewhere.
function problemUrl(id) {
    return `problem/${encodeURIComponent(id ?? "")}/`;
}

// Update the document title and canonical link at runtime (for client-rendered
// detail pages). The canonical is resolved against document.baseURI, so it is
// correct both on the deep <base> pages and on the ?id= shell.
function setPageMeta({ title, canonical } = {}) {
    if (title) document.title = title;
    if (canonical) {
        let link = document.querySelector('link[rel="canonical"]');
        if (!link) {
            link = document.createElement("link");
            link.rel = "canonical";
            document.head.appendChild(link);
        }
        link.href = new URL(canonical, document.baseURI).href;
    }
}

function instanceUrl(problemId, instanceName) {
    return `instance.html?problem=${encodeURIComponent(problemId ?? "")}&name=${encodeURIComponent(instanceName ?? "")}`;
}

function submissionUrl(problemId, submissionId) {
    return `submission.html?problem=${encodeURIComponent(problemId ?? "")}&id=${encodeURIComponent(submissionId ?? "")}`;
}

function statusPill(s) {
    // Colours come from CSS variables (defined in styles.css) so the badges
    // track the active theme and stay muted on dark backgrounds.
    const cfg = {
        optimal: { bg: "var(--pill-ok-bg)", c: "var(--pill-ok-fg)", label: "Optimal" },
        solved: { bg: "var(--pill-ok-bg)", c: "var(--pill-ok-fg)", label: "Solved" },
        best_known: { bg: "var(--pill-best-bg)", c: "var(--pill-best-fg)", label: "Best known" },
        submitted: { bg: "var(--pill-sub-bg)", c: "var(--pill-sub-fg)", label: "Submitted" },
        open: { bg: "var(--pill-open-bg)", c: "var(--pill-open-fg)", label: "Open" },
    };
    const cc = cfg[s] || { bg: "var(--pill-open-bg)", c: "var(--pill-open-fg)" };
    // Show a friendly label (matching the filter dropdowns) instead of the raw
    // machine token, e.g. "Best known" rather than "best_known".
    const label = cc.label || String(s ?? "").replace(/_/g, " ");
    return `<span class="status-pill" style="background:${cc.bg};color:${cc.c}">${esc(label)}</span>`;
}

// Three-way classification of a submission's compute paradigm. The QUBO/Ising
// *formulation* is deliberately NOT treated as a quantum signal — classical
// heuristics (e.g. abs2, tabu, simulated annealing) routinely solve QUBOs.
// Colours are CSS custom properties (defined in styles.css) rather than literal
// hex so the dots, legends and chart lines all track the active light/dark
// theme. They resolve in inline `style` (including on SVG elements), but NOT in
// SVG presentation attributes — so chart fills/strokes are applied via `style`.
const SUBMISSION_CATEGORIES = {
    quantum_hw: { label: "Quantum hardware", short: "Quantum HW", color: "var(--cat-quantum-hw)" },
    quantum_sim: { label: "Quantum simulator", short: "Quantum sim", color: "var(--cat-quantum-sim)" },
    classical: { label: "Classical", short: "Classical", color: "var(--cat-classical)" },
};

// Explicit "Paradigm" column values → canonical category. Mirrors _PARADIGM_MAP
// in misc/ci/site_builder/classify.py — keep the two in sync.
const PARADIGM_MAP = {
    classical: "classical",
    "quantum hardware": "quantum_hw",
    "quantum simulator": "quantum_sim",
};

function classifySubmission(s) {
    if (!s) return "classical";
    // Trust the submitter-declared paradigm when present; otherwise infer below.
    const declared = PARADIGM_MAP[String(s.paradigm || "").trim().toLowerCase()];
    if (declared) return declared;

    const numv = (v) => (v == null || v === "" ? NaN : Number(String(v).replace(/,/g, "").trim()));
    const qpu = numv(s.runtime_qpu);
    const hw = String(s.hardware || "").toLowerCase();
    const wf = String(s.workflow || "").toLowerCase();
    const txt = [s.modeling_approach, s.workflow, s.hardware, s.algorithm_type, s.reference, s.remarks]
        .map((x) => String(x || "").toLowerCase())
        .join(" ");

    // Genuine quantum-*algorithm* / hardware signals (not the formulation).
    const QUANTUM = /\bqaoa\b|\bvqe\b|\bqite\b|\bqpe\b|variational quantum|quantum approximate optimization|quantum anneal|adiabatic quantum|grover|amplitude (?:amplification|estimation)|quantum circuit|state ?vector|\bqubits?\b|\bqpu\b|\bd-?wave\b/;
    const isQuantum = (Number.isFinite(qpu) && qpu > 0) || QUANTUM.test(txt);
    if (!isQuantum) return "classical";

    // Measured QPU time is the strongest evidence of a real device.
    if (Number.isFinite(qpu) && qpu > 0) return "quantum_hw";

    // Explicit simulator wording wins over any device name that may also appear.
    const SIM = /simulat|state ?vector|emulat|noiseless|\baer\b|tensor[- ]?network sim|mps sim/;
    if (SIM.test(txt)) return "quantum_sim";

    // A named real quantum device → hardware.
    const REAL_HW = /\bqpu\b|ibm[\s_-]?(?:q|quantum|fez|eagle|heron|brisbane|sherbrooke|torino|kyiv|marrakesh|nazca|cusco|kawasaki|aachen)|\baqt\b|ibex|ionq|quantinuum|\bh1-|\bh2-|rigetti|aspen|d-?wave|advantage|2000q|quera|aquila|pasqal|\boqc\b|sycamore|infleqtion|\biqm\b/;
    if (REAL_HW.test(hw) || REAL_HW.test(wf)) return "quantum_hw";

    // Quantum method with no hardware evidence → assume a simulator.
    return "quantum_sim";
}

// Compute-paradigm badge (Quantum HW / Quantum sim / Classical) — a coloured
// dot plus the short label, shared by the leaderboard and submissions pages so
// the three paradigms read the same everywhere.
function catBadge(cat) {
    const c = SUBMISSION_CATEGORIES[cat] || SUBMISSION_CATEGORIES.classical;
    return `<span class="cat-badge" title="${esc(c.label)}"><span class="cat-dot" style="background:${c.color}"></span>${esc(c.short)}</span>`;
}

function renderMarkdown(md) {
    if (!md) return "";
    if (!window.marked?.parse) return `<p>${esc(md)}</p>`;
    // Shield math from the Markdown processor: marked would otherwise strip TeX
    // backslash escapes (\\, \{, \(, ...) and turn _subscripts_ into <em>,
    // corrupting the source before KaTeX runs. Stash each math span behind an
    // ASCII sentinel, render Markdown, then restore the original TeX so
    // renderMath() (KaTeX) receives it intact. Display delimiters first.
    const stash = [];
    const keep = (tex) => `@@QMATH${stash.push(tex) - 1}@@`;
    const protectedMd = String(md)
        .replace(/\$\$[\s\S]+?\$\$/g, keep)    // $$ display $$
        .replace(/\\\[[\s\S]+?\\\]/g, keep)    // \[ display \]
        .replace(/\\\([\s\S]+?\\\)/g, keep)    // \( inline \)
        .replace(/\$(?!\$)[^\n]*?\$/g, keep);  // $ inline $ (single line)
    const html = sanitizeHtml(window.marked.parse(protectedMd));
    return html.replace(/@@QMATH(\d+)@@/g, (_, i) => esc(stash[Number(i)]));
}

function renderMath(root, _tries) {
    if (!root) return;
    // KaTeX auto-render is loaded with `defer`, so on a client-rendered page it may
    // not be ready when this first runs. Retry briefly instead of silently leaving
    // raw TeX on the page; give up after ~5s.
    if (!window.renderMathInElement) {
        if ((_tries || 0) >= 50) return;
        setTimeout(() => renderMath(root, (_tries || 0) + 1), 100);
        return;
    }
    window.renderMathInElement(root, {
        throwOnError: false,
        delimiters: [
            { left: "$$", right: "$$", display: true },
            { left: "$", right: "$", display: false },
            { left: "\\(", right: "\\)", display: false },
            { left: "\\[", right: "\\]", display: true },
        ],
    });
}

function showError(el, msg) {
    if (!el) return;
    el.innerHTML = `<div class="error-box" role="alert">Failed to load data: ${esc(msg)}</div>`;
}

function modelLinks(models) {
    if (!models || !models.length) return "";
    return models
        .map((m) => `<a class="dl" href="${esc(m.raw_url)}" target="_blank" rel="noopener">↓ ${esc(m.format)}</a>`)
        .join(" ");
}

function detailModelList(models) {
    if (!models || !models.length) {
        return '<div class="empty-state">No uploaded model artifacts are available for this instance.</div>';
    }
    return `<div class="resource-list">${models
        .map(
            (m) => `
            <div class="resource-item">
                <div class="resource-head">
                    <div>
                        <div class="resource-title">${esc(m.name)}</div>
                        <div class="resource-sub">${esc(m.approach || "model")} · ${esc(m.format)}</div>
                    </div>
                    <a class="dl" href="${esc(m.raw_url)}" target="_blank" rel="noopener">↓ download</a>
                </div>
                <div class="resource-meta">
                    <span class="badge b-tag">${esc(m.kind || "model")}</span>
                    ${m.size_bytes != null ? `<span class="badge b-tag">${fmtBytes(m.size_bytes)}</span>` : ""}
                </div>
                ${m.description_md ? `
                <details>
                    <summary>Model description</summary>
                    <div class="resource-desc">${renderMarkdown(m.description_md)}</div>
                    ${m.description_url ? `<div><a class="dl" href="${esc(m.description_url)}" target="_blank" rel="noopener">View README ↗</a></div>` : ""}
                </details>` : ""}
            </div>`
        )
        .join("")}</div>`;
}

// Problem summary card used by the home page and the Problems index page.
// Two stacked progress bars summarise how much of the instance family each
// paradigm has solved (counts are precomputed at build time, see build.py).
// Both bars use the same three segments:
//   solved (proven optimal) · best-known (matched the best value, unproven) ·
//   open (everything else — no feasible solution, or only a worse feasible one).
function problemCard(p) {
    const total = p.instance_count || 0;
    const pct = (n) => (total ? (100 * (n || 0)) / total : 0);

    // The "Classical" bar counts instances solved classically (reference solution
    // or a classical submission). Fall back to the method-agnostic solved_count
    // for older data payloads that predate solved_classical_count, and to the
    // instance-level best_known_count for ones predating classical_best_known_count.
    // Anything not proven optimal or matching best-known counts as "open" (this
    // folds the former "found a worse solution" tier into open).
    const solvedClassicalPct = pct(p.solved_classical_count ?? p.solved_count ?? 0);
    const bestKnownClassicalPct = pct(p.classical_best_known_count ?? p.best_known_count ?? 0);
    const classicalOpenPct = Math.max(0, 100 - solvedClassicalPct - bestKnownClassicalPct);

    const solvedQuantumPct = pct(p.quantum_solved_count || 0);
    const bestKnownQuantumPct = pct(p.quantum_best_known_count || 0);
    const quantumOpenPct = Math.max(0, 100 - solvedQuantumPct - bestKnownQuantumPct);

    return `
        <a class="pcard" href="${problemUrl(p.id)}">
            <div class="pcard-num">${String(p.id).padStart(2, "0")}</div>
            <div class="pcard-name">${esc(p.name)}</div>
            <div class="pcard-sub">${esc(p.short)}</div>
            ${p.why ? `<p class="pcard-why">${esc(p.why)}</p>` : ""}
            <div class="pcard-bars">
                <div class="pcard-bar-row">
                    <span class="pcard-bar-label">Classical</span>
                    <div class="pcard-bar">
                        <div class="pcard-bar-fill solved-classical" style="width:${solvedClassicalPct}%"></div>
                        <div class="pcard-bar-fill best-known-classical" style="width:${bestKnownClassicalPct}%"></div>
                        <div class="pcard-bar-fill open-classical" style="width:${classicalOpenPct}%"></div>
                    </div>
                </div>
                <div class="pcard-bar-row">
                    <span class="pcard-bar-label">Quantum</span>
                    <div class="pcard-bar">
                        <div class="pcard-bar-fill solved-quantum" style="width:${solvedQuantumPct}%"></div>
                        <div class="pcard-bar-fill best-known-quantum" style="width:${bestKnownQuantumPct}%"></div>
                        <div class="pcard-bar-fill open-quantum" style="width:${quantumOpenPct}%"></div>
                    </div>
                </div>
            </div>
            <div class="pcard-foot">
                <span class="badge b-type">${esc(p.type)}</span>
                ${p.vars_min != null ? `<span class="badge b-vars">${fmtInt(p.vars_min)}–${fmtInt(p.vars_max)} vars</span>` : ""}
                <span class="badge b-form">${esc(p.formulation)}</span>
                <span class="badge b-tag">${fmtInt(p.instance_count)} inst.</span>
            </div>
        </a>`;
}

async function loadJSON(path) {
    if (cache.has(path)) return cache.get(path);
    const r = await fetch(path);
    if (!r.ok) throw new Error(`HTTP ${r.status} fetching ${path}`);
    const d = await r.json();
    cache.set(path, d);
    return d;
}

async function loadIndex() {
    if (INDEX) return INDEX;
    INDEX = await loadJSON("data/index.json");
    return INDEX;
}

async function loadProblemMeta(id) {
    if (META_CACHE.has(id)) return META_CACHE.get(id);
    const d = await loadJSON(`data/problems/${id}/meta.json`);
    META_CACHE.set(id, d);
    return d;
}

async function loadProblemInstances(id) {
    if (INSTANCES_CACHE.has(id)) return INSTANCES_CACHE.get(id);
    const d = await loadJSON(`data/problems/${id}/instances.json`);
    INSTANCES_CACHE.set(id, d.instances || []);
    return INSTANCES_CACHE.get(id);
}

async function loadProblemInstanceSubmissions(id) {
    if (INSTANCE_SUBS_CACHE.has(id)) return INSTANCE_SUBS_CACHE.get(id);
    const d = await loadJSON(`data/problems/${id}/instance_submissions.json`);
    INSTANCE_SUBS_CACHE.set(id, d.entries || {});
    return INSTANCE_SUBS_CACHE.get(id);
}

async function loadProblemSubmissions(id) {
    if (SUBMISSIONS_CACHE.has(id)) return SUBMISSIONS_CACHE.get(id);
    const d = await loadJSON(`data/problems/${id}/submissions.json`);
    SUBMISSIONS_CACHE.set(id, d.entries || []);
    return SUBMISSIONS_CACHE.get(id);
}

async function loadProblemSubmissionGroups(id) {
    if (SUBMISSION_GROUPS_CACHE.has(id)) return SUBMISSION_GROUPS_CACHE.get(id);
    const d = await loadJSON(`data/problems/${id}/submission_groups.json`);
    SUBMISSION_GROUPS_CACHE.set(id, d.entries || []);
    return SUBMISSION_GROUPS_CACHE.get(id);
}

// Pre-rendered performance-chart SVGs (built by misc/ci/site_builder/charts.py).
// Returns null when a problem has no charts or the chunk is absent, so callers
// can simply skip the performance section.
async function loadProblemCharts(id) {
    if (CHARTS_CACHE.has(id)) return CHARTS_CACHE.get(id);
    let entries = null;
    try {
        const d = await loadJSON(`data/problems/${id}/charts.json`);
        entries = d.entries || null;
    } catch (e) {
        entries = null;
    }
    CHARTS_CACHE.set(id, entries);
    return entries;
}

// Pre-baked "MIP Instance Map" scatter points for one problem (built by
// misc/ci/site_builder/metrics.py → data/problems/<id>/mip.json). Replaces the old
// runtime fetch of metrics.csv files from raw.githubusercontent.com. Returns an
// empty array when a problem has no LP metrics or the chunk is absent.
async function loadProblemMipPoints(id) {
    if (MIP_POINTS_CACHE.has(id)) return MIP_POINTS_CACHE.get(id);
    let points = [];
    try {
        const d = await loadJSON(`data/problems/${id}/mip.json`);
        points = d.points || [];
    } catch (e) {
        points = [];
    }
    MIP_POINTS_CACHE.set(id, points);
    return points;
}

async function loadProblemData(id) {
    const [meta, instances, instanceSubs] = await Promise.all([
        loadProblemMeta(id),
        loadProblemInstances(id),
        loadProblemInstanceSubmissions(id),
    ]);
    return { ...meta, instances, instance_submissions: instanceSubs };
}

async function loadAllProblemSubmissions() {
    const idx = await loadIndex();
    const chunks = await Promise.all(idx.problems.map((p) => loadProblemSubmissions(p.id)));
    return chunks.flat();
}

async function loadAllSubmissionGroups() {
    if (ALL_SUBMISSION_GROUPS_CACHE) return ALL_SUBMISSION_GROUPS_CACHE;
    const idx = await loadIndex();
    const chunks = await Promise.all(idx.problems.map((p) => loadProblemSubmissionGroups(p.id)));
    ALL_SUBMISSION_GROUPS_CACHE = chunks.flat();
    return ALL_SUBMISSION_GROUPS_CACHE;
}

// Aggregated, trimmed instance list for the Instances page (one request instead
// of fetching every problem's full instances.json + mip.json). Shape:
//   { problems: [ { id, name, columns, instances: [...], points: [...] } ] }
let INSTANCES_LIST_CACHE = null;
async function loadInstancesList() {
    if (INSTANCES_LIST_CACHE) return INSTANCES_LIST_CACHE;
    INSTANCES_LIST_CACHE = await loadJSON("data/instances.json");
    return INSTANCES_LIST_CACHE;
}

function setActiveNav(navId) {
    document.querySelectorAll(".nl").forEach((el) => {
        el.classList.toggle("on", el.dataset.nav === navId);
    });
}

function setupMobileNav() {
    const navInner = document.querySelector(".nav-inner");
    const nav = document.querySelector("nav");
    if (!navInner || !nav || navInner.querySelector(".nav-toggle")) return;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "nav-toggle";
    btn.setAttribute("aria-label", "Toggle navigation menu");
    btn.setAttribute("aria-expanded", "false");
    btn.textContent = "☰";

    const close = () => {
        nav.classList.remove("open");
        btn.setAttribute("aria-expanded", "false");
        btn.textContent = "☰";
    };
    btn.addEventListener("click", () => {
        const open = nav.classList.toggle("open");
        btn.setAttribute("aria-expanded", open ? "true" : "false");
        btn.textContent = open ? "✕" : "☰";
    });
    // Collapse after choosing a destination.
    navInner.querySelectorAll(".nav-links a").forEach((a) => a.addEventListener("click", close));

    navInner.appendChild(btn);
}

const THEME_KEY = "qoblib-theme";

function currentTheme() {
    return document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
}

function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try {
        localStorage.setItem(THEME_KEY, theme);
    } catch {
        /* storage may be unavailable (private mode) — toggle still works in-session */
    }
    document.querySelectorAll(".theme-toggle").forEach((btn) => {
        const dark = theme === "dark";
        btn.textContent = dark ? "☀" : "☾";
        btn.setAttribute("aria-pressed", dark ? "true" : "false");
        btn.title = dark ? "Switch to light mode" : "Switch to dark mode";
    });
}

function initTheme() {
    // The inline head script has already set data-theme to avoid a flash;
    // here we sync the toggle button state and bind the click handler.
    applyTheme(currentTheme());
    document.querySelectorAll(".theme-toggle").forEach((btn) => {
        if (btn.dataset.bound === "1") return;
        btn.dataset.bound = "1";
        btn.addEventListener("click", () => {
            applyTheme(currentTheme() === "dark" ? "light" : "dark");
        });
    });
}

function animateCount(id, target) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.remove("loading-val");
    // Respect reduced-motion: jump straight to the final value, no count-up.
    const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (target === 0 || reduceMotion) {
        el.textContent = Number(target || 0).toLocaleString();
        return;
    }
    let cur = 0;
    const step = Math.ceil(target / 30);
    const timer = setInterval(() => {
        cur = Math.min(cur + step, target);
        el.textContent = cur.toLocaleString();
        if (cur >= target) clearInterval(timer);
    }, 30);
}

// Reset every header to its base label, then mark `activeTh` with a ▲/▼ arrow and
// aria-sort so a table visibly shows which column it is sorted by. Shared by the
// click handler, the on-load default, and the programmatic setTableSortIndicator.
function applySortIndicator(headers, activeTh, dir) {
    headers.forEach((h) => {
        h.dataset.sortDir = "none";
        h.textContent = h.dataset.sortLabel || String(h.textContent || "");
        h.removeAttribute("aria-sort");
    });
    if (!activeTh || (dir !== "asc" && dir !== "desc")) return;
    const label = activeTh.dataset.sortLabel || String(activeTh.textContent || "");
    activeTh.dataset.sortDir = dir;
    activeTh.textContent = `${label} ${dir === "asc" ? "▲" : "▼"}`;
    activeTh.setAttribute("aria-sort", dir === "asc" ? "ascending" : "descending");
}

// Programmatically reflect a non-click sort (e.g. a dropdown-driven one) in a
// table's header. `header` is the column label (case-insensitive) or a th node.
function setTableSortIndicator(table, header, dir) {
    if (!table) return;
    const headers = Array.from(table.querySelectorAll("thead th"));
    if (!headers.length) return;
    const th =
        typeof header === "string"
            ? headers.find(
                  (h) => (h.dataset.sortLabel || h.textContent || "").trim().toLowerCase() === header.trim().toLowerCase(),
              )
            : header;
    applySortIndicator(headers, th, dir);
}

function enableTableSorting(root = document, options = {}) {
    const defaultExcluded = new Set(["remarks"]);
    const cfgExcluded = Array.isArray(window.QOBLIB_TABLE_SORT?.excludedHeaders)
        ? window.QOBLIB_TABLE_SORT.excludedHeaders
        : [];
    const extraExcluded = Array.isArray(options.excludedHeaders) ? options.excludedHeaders : [];
    [...cfgExcluded, ...extraExcluded]
        .map((s) => String(s || "").trim().toLowerCase())
        .filter(Boolean)
        .forEach((name) => defaultExcluded.add(name));

    const parseSortValue = (raw) => {
        const text = String(raw || "").replace(/\s+/g, " ").trim();
        if (!text) return { type: "text", value: "" };

        if (/^\d{4}-\d{1,2}-\d{1,2}/.test(text) || /^\d{1,2}[./-]\d{1,2}[./-]\d{2,4}/.test(text)) {
            const ts = Date.parse(text);
            if (Number.isFinite(ts)) return { type: "number", value: ts };
        }

        const compact = text.replace(/,/g, "");
        if (/^[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$/.test(compact)) {
            const n = Number(compact);
            if (Number.isFinite(n)) return { type: "number", value: n };
        }

        const leadingNumber = compact.match(/^[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?/);
        if (leadingNumber) {
            const n = Number(leadingNumber[0]);
            if (Number.isFinite(n)) return { type: "number", value: n };
        }

        return { type: "text", value: text.toLowerCase() };
    };

    const sortRowsByColumn = (table, colIdx, dir) => {
        const body = table.tBodies?.[0];
        if (!body) return;

        const rows = Array.from(body.rows);
        const decorated = rows.map((row, idx) => {
            const cellText = row.cells?.[colIdx]?.textContent || "";
            return { row, idx, parsed: parseSortValue(cellText) };
        });

        decorated.sort((a, b) => {
            const av = a.parsed;
            const bv = b.parsed;

            if (av.type === "number" && bv.type === "number") {
                if (av.value !== bv.value) return dir === "asc" ? av.value - bv.value : bv.value - av.value;
            } else {
                // Numeric-aware so "network10" sorts after "network2", not before.
                const cmp = String(av.value).localeCompare(String(bv.value), undefined, { numeric: true });
                if (cmp !== 0) return dir === "asc" ? cmp : -cmp;
            }
            return a.idx - b.idx;
        });

        decorated.forEach((item) => body.appendChild(item.row));
    };

    const tables = root.querySelectorAll ? root.querySelectorAll("table") : [];
    tables.forEach((table) => {
        if (table.dataset.sortableBound === "1") return;

        const headers = Array.from(table.querySelectorAll("thead th"));
        if (!headers.length || !table.tBodies?.[0]) return;

        const tableExcluded = new Set(
            String(table.dataset.sortExclude || "")
                .split(",")
                .map((s) => s.trim().toLowerCase())
                .filter(Boolean),
        );

        let hasSortableHeader = false;
        headers.forEach((th, colIdx) => {
            const label = String(th.textContent || "").replace(/[\u25B2\u25BC]\s*$/, "").trim();
            const normalizedLabel = label.toLowerCase();
            const excluded =
                th.dataset.sortable === "false" ||
                th.dataset.noSort === "true" ||
                defaultExcluded.has(normalizedLabel) ||
                tableExcluded.has(normalizedLabel);

            th.dataset.sortLabel = label;
            th.dataset.sortDir = "none";

            if (excluded) return;
            hasSortableHeader = true;

            th.style.cursor = "pointer";
            th.title = "Click or press Enter to sort";
            // Make the header operable and discoverable for keyboard / AT users.
            // The <th> keeps its implicit columnheader role; we add focusability,
            // a sort-state hint, and Enter/Space activation below.
            th.tabIndex = 0;
            th.setAttribute("aria-sort", "none");
            const doSort = () => {
                const nextDir = th.dataset.sortDir === "asc" ? "desc" : "asc";
                applySortIndicator(headers, th, nextDir);
                sortRowsByColumn(table, colIdx, nextDir);
                table.qoblibSort = { colIdx, dir: nextDir };
            };
            th.addEventListener("click", doSort);
            th.addEventListener("keydown", (e) => {
                if (e.key === "Enter" || e.key === " " || e.key === "Spacebar") {
                    e.preventDefault();
                    doSort();
                }
            });
        });

        if (hasSortableHeader) {
            table.dataset.sortableBound = "1";
            // Pages that re-render their <tbody> under a persistent <thead> (on
            // filter/search) call this to re-apply the user's chosen sort to the
            // fresh rows. Without it the new rows render in the page's default order
            // while the header still shows the old sort arrow.
            table.reapplySort = () => {
                const s = table.qoblibSort;
                if (!s || !headers[s.colIdx]) return;
                applySortIndicator(headers, headers[s.colIdx], s.dir);
                sortRowsByColumn(table, s.colIdx, s.dir);
            };
            // Reflect the table's initial sort (applied by the page's own render
            // code) in the header so it is visible without a click. A column opts
            // in with data-sort-default="asc|desc".
            const defaultTh = headers.find(
                (h) => h.dataset.sortDefault === "asc" || h.dataset.sortDefault === "desc",
            );
            if (defaultTh && defaultTh.style.cursor === "pointer") {
                applySortIndicator(headers, defaultTh, defaultTh.dataset.sortDefault);
            }
        }
    });
}

async function renderFooter() {
    const buildEl = document.getElementById("footer-build");
    if (!buildEl) return;
    try {
        const idx = await loadIndex();
        const builtAt = idx.built_at ? idx.built_at.replace("T", " ").replace("Z", " UTC") : null;
        const commit = idx.commit;
        const repo = "https://github.com/ZIB-AOPT/QOBLIB";
        const commitHtml = commit
            ? `<a href="${repo}/commit/${esc(commit)}" target="_blank" rel="noopener">${esc(String(commit).slice(0, 7))}</a>`
            : `<a href="${repo}" target="_blank" rel="noopener">repository</a>`;
        buildEl.innerHTML = builtAt
            ? `Generated from ${commitHtml} on ${esc(builtAt)}`
            : `Generated from the QOBLIB ${commitHtml}`;
    } catch {
        buildEl.textContent = "Generated from the QOBLIB repository.";
    }
}

// The footer's "Download site data" link is the same markup on every page, but
// the data is split into many files. Point it at the JSON that actually backs
// the current view instead of always the home-page payload.
function footerDataTarget() {
    const page = (location.pathname.split("/").pop() || "index.html").toLowerCase();
    const params = new URLSearchParams(location.search);
    // problem.html uses ?id=<problem>; instance/submission use ?problem=<problem>.
    const probId = params.get("problem") || params.get("id");
    const pid = probId ? String(probId).padStart(2, "0") : null;

    if (page === "leaderboard.html") return { href: "data/leaderboard.json", label: "Download leaderboard data" };
    // The submissions overview is assembled from many per-problem chunks, so there
    // is no single "submissions" payload to download — fall through to the
    // site-wide index.json rather than mislabel the leaderboard file.
    if (page === "problem.html" && pid) return { href: `data/problems/${pid}/instances.json`, label: "Download this problem's data" };
    if (page === "instance.html" && pid) return { href: `data/problems/${pid}/instance_submissions.json`, label: "Download this instance's data" };
    if (page === "submission.html" && pid) return { href: `data/problems/${pid}/submission_groups.json`, label: "Download this submission's data" };
    // Home, problems, instances and submit are overview pages backed by index.json.
    return { href: "data/index.json", label: "Download site data" };
}

function updateFooterDataLink() {
    const link = document.querySelector('.site-footer a[href*="data/"]');
    if (!link) return;
    const { href, label } = footerDataTarget();
    link.setAttribute("href", href);
    link.textContent = label;
}

function initCommon() {
    const current = document.body.dataset.nav || "home";
    setActiveNav(current);
    setupMobileNav();
    initTheme();
    enableTableSorting(document);
    renderFooter();
    updateFooterDataLink();

    if (!TABLE_SORT_OBSERVER) {
        TABLE_SORT_OBSERVER = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType !== 1) return;
                    if (node.matches?.("table")) {
                        enableTableSorting(node.parentElement || document);
                    } else if (node.querySelectorAll) {
                        enableTableSorting(node);
                    }
                });
            });
        });
        TABLE_SORT_OBSERVER.observe(document.body, { childList: true, subtree: true });
    }
}

// --- CSV export -----------------------------------------------------------
// Used by the table pages to let visitors download exactly what they see
// (current filters + sort) as a spreadsheet-friendly CSV.

function csvField(value) {
    const s = value == null ? "" : String(value);
    return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

function toCsv(headers, rows) {
    const lines = [headers.map(csvField).join(",")];
    for (const row of rows) lines.push(row.map(csvField).join(","));
    return lines.join("\r\n");
}

function downloadCsv(filename, headers, rows) {
    // Prepend a UTF-8 BOM so Excel reads non-ASCII characters correctly.
    const blob = new Blob(["\uFEFF" + toCsv(headers, rows)], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
}

// --- figure lightbox -------------------------------------------------------
// A shared "expand" affordance for any figure (problem illustrations, the MIP
// instance map, the performance/convergence charts, the home-page landscape
// plots). attachFigureExpand() adds a hover/focus button to a figure container;
// clicking it opens the figure's SVG/img enlarged in a single reused overlay.
// The graphic is read at click time, so live charts (which re-inject their SVG
// on toggle/resize) always show their current state.

let figLightbox = null;
let figLightboxTrigger = null;

function closeFigureLightbox() {
    if (!figLightbox) return;
    figLightbox.hidden = true;
    figLightbox.querySelector(".fig-lightbox-inner").innerHTML = "";
    if (figLightboxTrigger && document.contains(figLightboxTrigger)) figLightboxTrigger.focus();
    figLightboxTrigger = null;
}

function ensureFigureLightbox() {
    if (figLightbox) return figLightbox;
    figLightbox = document.createElement("div");
    figLightbox.className = "fig-lightbox";
    figLightbox.hidden = true;
    figLightbox.innerHTML =
        '<div class="fig-lightbox-inner" role="dialog" aria-modal="true" aria-label="Enlarged figure"></div>' +
        '<button type="button" class="fig-lightbox-close" aria-label="Close enlarged figure" title="Close">✕</button>';
    figLightbox.addEventListener("click", (ev) => {
        if (ev.target === figLightbox || ev.target.closest(".fig-lightbox-close")) closeFigureLightbox();
    });
    document.addEventListener("keydown", (ev) => {
        if (ev.key === "Escape" && !figLightbox.hidden) closeFigureLightbox();
    });
    document.body.appendChild(figLightbox);
    return figLightbox;
}

function openFigureLightbox(html, trigger) {
    if (!html) return;
    const box = ensureFigureLightbox();
    box.querySelector(".fig-lightbox-inner").innerHTML = html;
    box.hidden = false;
    figLightboxTrigger = trigger || null;
    box.querySelector(".fig-lightbox-close").focus();
}

// Add a top-right expand button to `container`. By default the lightbox shows the
// whole figure (heading, legend and graphic) so nothing is lost when enlarged.
// `opts.target` (a selector string or function) instead enlarges just that single
// element; `opts.html` (a function returning an HTML string) supplies fully custom
// lightbox content (e.g. a re-laid-out multi-part figure). No-op if the container
// has no graphic yet, so call it after the figure has rendered.
function attachFigureExpand(container, opts = {}) {
    if (!container || container.querySelector(":scope > .fig-expand")) return;
    const findGraphic = () => {
        if (typeof opts.target === "function") return opts.target();
        if (typeof opts.target === "string") return container.querySelector(opts.target);
        return container.querySelector("svg, img");
    };
    if (!findGraphic()) return;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "fig-expand";
    btn.setAttribute("aria-label", "Expand figure");
    btn.title = "Expand figure";
    btn.innerHTML = '<span aria-hidden="true">⤢</span> Expand';
    btn.addEventListener("click", () => {
        // opts.html lets a caller supply richer lightbox content than a single
        // graphic — e.g. a whole figure with its legend, sub-plots and caption.
        if (typeof opts.html === "function") {
            const html = opts.html();
            if (html) openFigureLightbox(html, btn);
            return;
        }
        // An explicit opts.target enlarges just that one element.
        if (typeof opts.target !== "undefined") {
            const graphic = findGraphic();
            if (graphic) openFigureLightbox(graphic.outerHTML, btn);
            return;
        }
        // Default: enlarge the whole figure — heading (title), legend and graphic —
        // not just the first <svg>/<img>, so legends and titles aren't lost. Clone
        // the container, then drop the expand button and any interactive tooltip.
        const clone = container.cloneNode(true);
        clone.querySelectorAll(".fig-expand, .mip-tooltip").forEach((el) => el.remove());
        const html = clone.innerHTML.trim();
        if (html) openFigureLightbox(html, btn);
    });
    container.classList.add("has-fig-expand");
    container.appendChild(btn);
}

// Wire expand buttons onto every known figure container under `root`.
function enhanceFigures(root = document) {
    const scope = root && root.querySelectorAll ? root : document;
    scope.querySelectorAll(".chart-card, .plot-card, .d-desc-visual").forEach((el) => attachFigureExpand(el));
}

window.QOBLIB = {
    esc,
    fmtBytes,
    fmtNum,
    fmtInt,
    fmtMaybeNum,
    fmtText,
    parseDate,
    fmtDate,
    submissionDate,
    submissionMethod,
    problemUrl,
    instanceUrl,
    submissionUrl,
    statusPill,
    renderMarkdown,
    renderMath,
    showError,
    classifySubmission,
    SUBMISSION_CATEGORIES,
    catBadge,
    modelLinks,
    detailModelList,
    problemCard,
    loadIndex,
    loadProblemData,
    loadAllProblemSubmissions,
    loadProblemSubmissionGroups,
    loadProblemCharts,
    loadProblemMipPoints,
    loadAllSubmissionGroups,
    loadInstancesList,
    setPageMeta,
    openFigureLightbox,
    attachFigureExpand,
    enhanceFigures,
    enableTableSorting,
    setTableSortIndicator,
    initCommon,
    initTheme,
    applyTheme,
    animateCount,
    toCsv,
    downloadCsv,
};
