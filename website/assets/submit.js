"use strict";

const {
    esc: qEsc,
    fmtDate: qFmtDate,
    loadIndex: qLoadIndex,
    loadProblemData: qLoadProblemData,
    showError: qShowError,
    initCommon: qInitCommon,
} = window.QOBLIB;

const REPO = "ZIB-AOPT/QOBLIB";

// Canonical 30-column header — MUST match misc/ci/check_submission.py REQUIRED_COLUMNS exactly.
const CSV_COLUMNS = [
    "Problem", "Submitter", "Affiliation", "Date", "Reference", "Best Objective Value", "Optimality Bound",
    "Modeling Approach", "# Decision Variables", "# Binary Variables", "# Integer Variables", "# Continuous Variables",
    "# Non-Zero Coefficients", "Coefficients Type", "Coefficients Range", "Workflow", "Algorithm Type", "Paradigm",
    "# Runs", "# Feasible Runs", "# Successful Runs", "Success Threshold", "Hardware Specifications",
    "Total Runtime", "Time to Solution", "CPU Runtime", "GPU Runtime", "QPU Runtime", "Other HW Runtime", "Remarks",
];

const INT_COLUMNS = new Set([
    "# Decision Variables", "# Binary Variables", "# Integer Variables", "# Continuous Variables",
    "# Non-Zero Coefficients", "# Runs", "# Feasible Runs", "# Successful Runs",
]);
const FLOAT_COLUMNS = new Set([
    "Best Objective Value", "Optimality Bound", "Success Threshold",
    "Total Runtime", "Time to Solution", "CPU Runtime", "GPU Runtime", "QPU Runtime", "Other HW Runtime",
]);

// Fields entered once for the whole package (CSV column -> input spec).
const SHARED_FIELDS = [
    { col: "Submitter", label: "Submitter(s)", required: true, placeholder: "Ada Lovelace, Alan Turing" },
    { col: "Affiliation", label: "Affiliation(s)", required: true, placeholder: "Example Lab, Example University", hint: "One per author, in the same order (repeat shared affiliations)." },
    { col: "Date", label: "Date", type: "date", required: true },
    { col: "Reference", label: "Reference (paper / repo URL)", placeholder: "https://arxiv.org/abs/..." },
    { col: "Modeling Approach", label: "Modeling approach", required: true, placeholder: "QUBO, ILP, ..." },
    { col: "Coefficients Type", label: "Coefficients type", required: true, placeholder: "integer / continuous" },
    { col: "Algorithm Type", label: "Algorithm type", required: true, type: "select", options: ["", "Deterministic", "Stochastic"] },
    { col: "Paradigm", label: "Paradigm", required: true, type: "select", options: ["", "Classical", "Quantum Hardware", "Quantum Simulator"] },
    { col: "Workflow", label: "Workflow", required: true, type: "textarea", placeholder: "pre-processing → solver → post-processing" },
    { col: "Hardware Specifications", label: "Hardware specifications", required: true, type: "textarea", placeholder: "IBM Eagle r3 (127 qubits); 1× A100; ..." },
    { col: "__team", label: "Team / folder tag", placeholder: "MyTeam — used in the submission folder name" },
];

// Per-instance fields (CSV column -> input spec). "essential" ones are always visible.
// All fields are required; numeric ones accept "N/A" when they do not apply.
const ROW_FIELDS = [
    { col: "Best Objective Value", label: "Best objective value", essential: true, required: true, placeholder: "-1234.5 (or N/A for feasibility problems)" },
    { col: "Optimality Bound", label: "Optimality bound", required: true, placeholder: "number or N/A" },
    { col: "# Decision Variables", label: "# Decision vars", required: true, placeholder: "number or N/A" },
    { col: "# Binary Variables", label: "# Binary vars", required: true, placeholder: "number or N/A" },
    { col: "# Integer Variables", label: "# Integer vars", required: true, placeholder: "number or N/A" },
    { col: "# Continuous Variables", label: "# Continuous vars", required: true, placeholder: "number or N/A" },
    { col: "# Non-Zero Coefficients", label: "# Non-zero coeffs", required: true, placeholder: "number or N/A" },
    { col: "Coefficients Range", label: "Coefficients range", required: true, placeholder: "e.g. [1, 50] or N/A" },
    { col: "# Runs", label: "# Runs", required: true, placeholder: "number or N/A" },
    { col: "# Feasible Runs", label: "# Feasible runs", required: true, placeholder: "number or N/A" },
    { col: "# Successful Runs", label: "# Successful runs", required: true, placeholder: "number or N/A" },
    { col: "Success Threshold", label: "Success threshold ε", required: true, placeholder: "number or N/A" },
    { col: "Total Runtime", label: "Total runtime (s)", required: true, placeholder: "seconds or N/A" },
    { col: "Time to Solution", label: "Time to solution (s)", required: true, placeholder: "seconds or N/A" },
    { col: "CPU Runtime", label: "CPU runtime (s)", required: true, placeholder: "seconds or N/A" },
    { col: "GPU Runtime", label: "GPU runtime (s)", required: true, placeholder: "seconds or N/A" },
    { col: "QPU Runtime", label: "QPU runtime (s)", required: true, placeholder: "seconds or N/A" },
    { col: "Other HW Runtime", label: "Other HW runtime (s)", required: true, placeholder: "seconds or N/A" },
    // Free-text notes: the authoritative checker never requires a value here, so
    // don't force the user to type "N/A" into a notes field — leave it optional.
    { col: "Remarks", label: "Remarks", required: false, type: "textarea", placeholder: "notes — negative results welcome!" },
];

let SITE_INDEX = null;
const PROBLEM_CACHE = new Map();          // id -> loaded problem data
const INSTANCE_INDEX = new Map();         // instance name -> problem id (best effort)
let rowSeq = 0;
let validated = false;                     // becomes true after "Check submission" / export
const shared = {};                        // shared field values
const sharedTouched = new Set();          // shared cols the user edited by hand (import won't clobber these)

const NA = (v) => String(v || "").trim().toUpperCase();
const isNA = (v) => NA(v) === "N/A" || NA(v) === "NA";
const isBlank = (v) => String(v ?? "").trim() === "";

function showToast(msg, type = "success") {
    const t = document.getElementById("toast");
    if (!t) return;
    t.textContent = msg;
    t.style.background = type === "error" ? "var(--red)" : type === "warn" ? "var(--amber)" : "var(--green)";
    // Errors/warnings interrupt; success is announced politely.
    t.setAttribute("aria-live", type === "error" || type === "warn" ? "assertive" : "polite");
    t.classList.add("show");
    setTimeout(() => t.classList.remove("show"), 2800);
}

function sanitizeTag(s) {
    return String(s || "").trim().replace(/[^A-Za-z0-9._-]+/g, "_").replace(/^_+|_+$/g, "");
}

function problemDir(p) {
    return `${String(p.id).padStart(2, "0")}-${p.slug}`;
}

async function getProblem(id) {
    if (!id) return null;
    if (PROBLEM_CACHE.has(id)) return PROBLEM_CACHE.get(id);
    const data = await qLoadProblemData(id);
    PROBLEM_CACHE.set(id, data);
    (data.instances || []).forEach((i) => {
        if (!INSTANCE_INDEX.has(i.name)) INSTANCE_INDEX.set(i.name, id);
    });
    return data;
}

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

// Stable, unique DOM id for a field so its <label for> can point at the input.
function colId(prefix, col) {
    return `${prefix}-${String(col).replace(/[^a-z0-9]+/gi, "-").replace(/^-+|-+$/g, "").toLowerCase()}`;
}

function fieldInput(spec, value, oninput, idAttr) {
    const id = idAttr ? `id="${idAttr}"` : "";
    const ph = spec.placeholder ? `placeholder="${qEsc(spec.placeholder)}"` : "";
    if (spec.type === "textarea") {
        return `<textarea ${id} data-col="${qEsc(spec.col)}" ${ph} oninput="${oninput}">${qEsc(value || "")}</textarea>`;
    }
    if (spec.type === "select") {
        // Case-insensitive match so an imported value (e.g. "Deterministic") still
        // selects its option even if the casing differs from the option list.
        const valLower = String(value ?? "").toLowerCase();
        const opts = (spec.options || []).map((o) => `<option value="${qEsc(o)}"${String(o).toLowerCase() === valLower ? " selected" : ""}>${qEsc(o || "—")}</option>`).join("");
        return `<select ${id} data-col="${qEsc(spec.col)}" onchange="${oninput}">${opts}</select>`;
    }
    const type = spec.type === "date" ? "date" : "text";
    return `<input ${id} data-col="${qEsc(spec.col)}" type="${type}" value="${qEsc(value || "")}" ${ph} oninput="${oninput}" />`;
}

function renderShared() {
    const grid = document.getElementById("shared-grid");
    grid.innerHTML = SHARED_FIELDS.map((f) => {
        const full = f.type === "textarea" ? " ff-full" : "";
        const id = colId("sf", f.col);
        const hint = f.hint ? `<small class="ff-hint">${qEsc(f.hint)}</small>` : "";
        return `<div class="ff${full}">
            <label for="${id}">${qEsc(f.label)}${f.required ? "" : ' <span class="opt">(optional)</span>'}</label>
            ${fieldInput(f, shared[f.col] || "", "onSharedInput(this)", id)}
            ${hint}
        </div>`;
    }).join("");
}

function problemOptions(selected) {
    const opts = ['<option value="">Problem…</option>'];
    (SITE_INDEX.problems || []).forEach((p) => {
        const label = `${String(p.id).padStart(2, "0")} · ${p.name}`;
        opts.push(`<option value="${qEsc(p.id)}"${p.id === selected ? " selected" : ""}>${qEsc(label)}</option>`);
    });
    return opts.join("");
}

function rowTemplate(row) {
    const fieldBlock = (f) => {
        const id = colId(`rf${row.id}`, f.col);
        return `<div class="ff">
            <label for="${id}">${qEsc(f.label)}${f.required ? "" : ' <span class="opt">(optional)</span>'}</label>
            ${fieldInput(f, row.data[f.col] || "", `onRowInput(${row.id}, this)`, id)}
        </div>`;
    };
    const advanced = ROW_FIELDS.filter((f) => !f.essential).map(fieldBlock).join("");
    const essential = ROW_FIELDS.filter((f) => f.essential).map(fieldBlock).join("");

    return `
    <div class="srow" id="srow-${row.id}" data-rid="${row.id}">
        <div class="srow-top">
            <span class="srow-num">Row #${row.idx}</span>
            <button class="srow-del" type="button" title="Remove this row" onclick="removeRow(${row.id})">✕ Remove row</button>
        </div>
        <div class="srow-head">
            <div class="ff">
                <label for="prob-${row.id}">Problem class</label>
                <select id="prob-${row.id}" data-role="problem" onchange="onProblemChange(${row.id}, this)">${problemOptions(row.problemId)}</select>
            </div>
            <div class="ff fi-grow">
                <label for="inst-${row.id}">Instance</label>
                <div class="ac" data-rid="${row.id}">
                    <input id="inst-${row.id}" type="text" data-role="instance" autocomplete="off"
                           role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="acm-${row.id}"
                           value="${qEsc(row.instance || "")}" placeholder="start typing an instance name…"
                           oninput="onInstanceInput(${row.id}, this)" />
                    <ul class="ac-menu" id="acm-${row.id}" role="listbox" hidden></ul>
                </div>
            </div>
            ${essential}
        </div>
        <div class="srow-status" id="srow-status-${row.id}"></div>
        <details class="srow-adv" open>
            <summary>Model &amp; runtime details — enter N/A for any numeric field that does not apply</summary>
            <div class="field-grid">${advanced}</div>
        </details>
    </div>`;
}

const rows = [];

function renderRows() {
    const host = document.getElementById("rows");
    rows.forEach((r, i) => (r.idx = i + 1));
    host.innerHTML = rows.map(rowTemplate).join("");
    rows.forEach((r) => {
        if (r.problemId) loadRowInstances(r);
    });
    validateAll();
}

function addRow(initial = {}) {
    rowSeq += 1;
    rows.push({
        id: rowSeq,
        idx: rows.length + 1,
        problemId: initial.problemId || "",
        instance: initial.instance || "",
        data: initial.data || {},
    });
    renderRows();
}

function rowHasData(row) {
    if (!row) return false;
    if (row.problemId) return true;
    if (!isBlank(row.instance)) return true;
    return Object.values(row.data || {}).some((v) => !isBlank(v));
}

function removeRow(id) {
    const i = rows.findIndex((r) => r.id === id);
    if (i < 0) return;
    const row = rows[i];

    // Only confirm when the row actually contains entered data — an empty row is
    // removed immediately. A single confirm is enough.
    if (rowHasData(row)) {
        const label = !isBlank(row.instance) ? `“${row.instance}”` : `#${row.idx}`;
        if (!window.confirm(`Delete row ${label}? This permanently removes everything you typed into it.`)) return;
    }

    rows.splice(i, 1);
    renderRows();
}

// Cache the chosen problem's instance names on the row; the custom autocomplete
// (below) filters this list as the user types. Refresh an open menu in case the
// problem changed while the field was focused.
async function loadRowInstances(row) {
    if (!row.problemId) {
        row._instanceNames = [];
    } else {
        try {
            const p = await getProblem(row.problemId);
            row._instanceNames = (p.instances || []).map((i) => i.name).filter(Boolean);
        } catch {
            row._instanceNames = [];
        }
    }
    if (acMenu(row.id) && !acMenu(row.id).hidden) renderAc(row);
    validateAll();
}

// ---------------------------------------------------------------------------
// Instance autocomplete — a themed replacement for the native <datalist>, which
// renders with un-styleable OS chrome that clashes with the rest of the form.
// ---------------------------------------------------------------------------
const AC_MAX = 60; // cap rendered suggestions; "N more…" hints at the rest

const acMenu = (rowId) => document.getElementById(`acm-${rowId}`);
const acInput = (rowId) => document.getElementById(`inst-${rowId}`);
const acItems = (rowId) => {
    const m = acMenu(rowId);
    return m ? Array.from(m.querySelectorAll(".ac-item")) : [];
};

function closeAc(rowId) {
    const menu = acMenu(rowId);
    if (!menu || menu.hidden) return;
    menu.hidden = true;
    menu.innerHTML = "";
    menu.dataset.active = "-1";
    acInput(rowId)?.setAttribute("aria-expanded", "false");
}

function closeAllAc(except) {
    document.querySelectorAll("#rows .ac-menu:not([hidden])").forEach((m) => {
        const rid = m.id.replace("acm-", "");
        if (rid !== String(except)) closeAc(rid);
    });
}

function renderAc(row) {
    const menu = acMenu(row.id);
    const input = acInput(row.id);
    if (!menu || !input) return;
    const names = row._instanceNames || [];
    const q = String(row.instance || "").trim().toLowerCase();
    let matches = q ? names.filter((n) => n.toLowerCase().includes(q)) : names;
    // Already an exact pick — nothing useful to offer.
    if (matches.length === 1 && matches[0].toLowerCase() === q) matches = [];
    const shown = matches.slice(0, AC_MAX);
    if (!shown.length) {
        closeAc(row.id);
        return;
    }
    const extra = matches.length - shown.length;
    menu.innerHTML =
        shown
            .map((n) => `<li role="option" class="ac-item" data-rid="${row.id}" data-name="${qEsc(n)}">${qEsc(n)}</li>`)
            .join("") +
        (extra > 0 ? `<li class="ac-more" aria-hidden="true">${extra} more — keep typing to narrow…</li>` : "");
    menu.hidden = false;
    menu.dataset.active = "-1";
    input.setAttribute("aria-expanded", "true");
}

function setAcActive(rowId, idx) {
    const items = acItems(rowId);
    if (!items.length) return;
    const n = items.length;
    const at = ((idx % n) + n) % n;
    items.forEach((it, i) => it.classList.toggle("active", i === at));
    const menu = acMenu(rowId);
    if (menu) menu.dataset.active = String(at);
    const input = acInput(rowId);
    if (input) input.setAttribute("aria-activedescendant", items[at].id || "");
    items[at].scrollIntoView({ block: "nearest" });
}

function chooseAc(row, name) {
    setRowInstance(row, name);
    const input = acInput(row.id);
    if (input) input.value = name;
    closeAc(row.id);
}

// Shared by typing and by picking a suggestion.
function setRowInstance(row, value) {
    row.instance = value;
    // Auto-detect the problem if it is unambiguous and not set yet.
    if (!row.problemId && INSTANCE_INDEX.has(value)) {
        row.problemId = INSTANCE_INDEX.get(value);
        const sel = document.querySelector(`#srow-${row.id} select[data-role="problem"]`);
        if (sel) sel.value = row.problemId;
        loadRowInstances(row);
    }
    validateAll();
}

const rowForEvent = (target) => {
    const input = target.closest?.('[data-role="instance"]');
    if (!input || !input.closest(".ac")) return null;
    const row = rows.find((r) => String(r.id) === input.id.replace("inst-", ""));
    return row ? { row, input } : null;
};

function onRowsFocusin(e) {
    const ctx = rowForEvent(e.target);
    if (ctx) renderAc(ctx.row);
}

function onRowsMousedown(e) {
    const item = e.target.closest?.(".ac-item");
    if (!item) return;
    e.preventDefault(); // keep focus in the input so it doesn't blur-close first
    const row = rows.find((r) => String(r.id) === item.dataset.rid);
    if (row) chooseAc(row, item.dataset.name);
}

function onRowsKeydown(e) {
    const ctx = rowForEvent(e.target);
    if (!ctx) return;
    const { row } = ctx;
    const menu = acMenu(row.id);
    const open = menu && !menu.hidden;
    if (e.key === "ArrowDown") {
        e.preventDefault();
        if (!open) renderAc(row);
        setAcActive(row.id, Number(menu?.dataset.active ?? -1) + 1);
    } else if (e.key === "ArrowUp") {
        e.preventDefault();
        if (open) setAcActive(row.id, Number(menu.dataset.active ?? 0) - 1);
    } else if (e.key === "Enter") {
        const active = open ? Number(menu.dataset.active) : -1;
        if (active >= 0) {
            e.preventDefault();
            const it = acItems(row.id)[active];
            if (it) chooseAc(row, it.dataset.name);
        }
    } else if (e.key === "Escape") {
        if (open) {
            e.preventDefault();
            closeAc(row.id);
        }
    }
}

function onRowsFocusout(e) {
    const ctx = rowForEvent(e.target);
    if (!ctx) return;
    // Close unless focus moved within the same autocomplete (mousedown selection).
    const ac = ctx.input.closest(".ac");
    if (!ac.contains(e.relatedTarget)) closeAc(ctx.row.id);
}

// ---------------------------------------------------------------------------
// Input handlers (exposed on window for inline events)
// ---------------------------------------------------------------------------

function onSharedInput(el) {
    shared[el.dataset.col] = el.value;
    sharedTouched.add(el.dataset.col);
    validateAll();
}

function onRowInput(id, el) {
    const row = rows.find((r) => r.id === id);
    if (!row) return;
    row.data[el.dataset.col] = el.value;
    validateAll();
}

function onProblemChange(id, el) {
    const row = rows.find((r) => r.id === id);
    if (!row) return;
    row.problemId = el.value;
    loadRowInstances(row);
}

function onInstanceInput(id, el) {
    const row = rows.find((r) => r.id === id);
    if (!row) return;
    setRowInstance(row, el.value);
    renderAc(row);
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

function knownValues(problem, instanceName) {
    const inst = (problem.instances || []).find((i) => i.name === instanceName);
    if (!inst) return null;
    const best = inst.best_value ?? inst.reference_solution_value ?? inst.bkv ?? null;
    return {
        inst,
        bestKnown: best,
        optimal: inst.best_is_optimal ? best : null,
        status: inst.status,
    };
}

function numericIssues(row) {
    const issues = [];
    for (const f of ROW_FIELDS) {
        if (f.col === "Best Objective Value") continue; // validated explicitly with optimum cross-checks
        const v = row.data[f.col];
        if (isBlank(v) || isNA(v)) continue;
        const compact = String(v).replace(/,/g, "");
        if (INT_COLUMNS.has(f.col) && !/^[+-]?\d+$/.test(compact)) {
            issues.push({ col: f.col, msg: `${f.label} must be an integer or N/A (got “${v}”).` });
        } else if (FLOAT_COLUMNS.has(f.col) && !Number.isFinite(Number(compact))) {
            issues.push({ col: f.col, msg: `${f.label} must be a number or N/A (got “${v}”).` });
        }
    }
    return issues;
}

function validateRow(row) {
    const out = { errors: [], warns: [], oks: [] };
    if (!row.problemId) out.errors.push("Pick a problem class.");
    if (isBlank(row.instance)) out.errors.push("Enter an instance name.");

    const problem = row.problemId ? PROBLEM_CACHE.get(row.problemId) : null;
    if (row.problemId && problem && !isBlank(row.instance)) {
        const known = knownValues(problem, row.instance);
        if (!known) {
            out.errors.push(`Instance “${row.instance}” is not part of problem ${String(row.problemId).padStart(2, "0")}.`);
        } else {
            const valRaw = row.data["Best Objective Value"];
            if (isBlank(valRaw)) {
                out.errors.push("Best objective value is required (enter a value or N/A).");
            } else if (isNA(valRaw)) {
                // Feasibility problems (e.g. Market Split) have no objective to
                // optimise, so N/A is valid here — it is what the authoritative
                // checker accepts. There is nothing to cross-check against an optimum.
                out.oks.push("Objective reported as N/A (no value to cross-check).");
            } else if (!Number.isFinite(Number(String(valRaw).replace(/,/g, "")))) {
                out.errors.push(`Best objective value must be a number or N/A (got “${valRaw}”).`);
            } else {
                const v = Number(String(valRaw).replace(/,/g, ""));
                const minimize = problem.minimize !== false;
                const eps = 1e-6 * Math.max(1, Math.abs(known.optimal ?? known.bestKnown ?? v));
                if (known.optimal != null) {
                    if (minimize && v < known.optimal - eps) {
                        out.errors.push(`Objective ${v} is below the proven optimum ${known.optimal} — impossible for a feasible solution.`);
                    } else if (!minimize && v > known.optimal + eps) {
                        out.errors.push(`Objective ${v} is above the proven optimum ${known.optimal} — impossible for a feasible solution.`);
                    } else if (Math.abs(v - known.optimal) <= eps) {
                        out.oks.push(`Matches the proven optimum (${known.optimal}).`);
                    }
                } else if (known.bestKnown != null) {
                    const improves = minimize ? v < known.bestKnown - eps : v > known.bestKnown + eps;
                    if (improves) out.warns.push(`Improves the current best-known (${known.bestKnown} → ${v}) — nice! Double-check the solution file.`);
                    else out.oks.push(`Best-known is ${known.bestKnown}.`);
                }
            }
        }
    } else if (!isBlank(row.instance) && row.problemId && !problem) {
        out.warns.push("Loading instance list to verify…");
    }

    // Every per-instance field is required once the row is in use. Numeric
    // fields accept "N/A" when they do not apply (e.g. QPU runtime on a CPU run).
    if (row.problemId && !isBlank(row.instance)) {
        ROW_FIELDS.forEach((f) => {
            if (!f.required || f.col === "Best Objective Value") return; // objective handled above
            if (isBlank(row.data[f.col])) {
                const naHint = INT_COLUMNS.has(f.col) || FLOAT_COLUMNS.has(f.col) ? " (enter a value or N/A)" : "";
                out.errors.push(`${f.label} is required${naHint}.`);
            }
        });
    }

    numericIssues(row).forEach((i) => out.errors.push(i.msg));
    return out;
}

// Toggle the visual invalid state and the matching aria-invalid so the failure
// is conveyed to assistive tech, not just by colour.
function markInvalid(el, bad) {
    if (!el) return;
    el.classList.toggle("invalid", Boolean(bad));
    if (bad) el.setAttribute("aria-invalid", "true");
    else el.removeAttribute("aria-invalid");
}

function clearInvalidMarks() {
    document.querySelectorAll("#shared-grid .invalid, #rows .invalid").forEach((el) => {
        el.classList.remove("invalid");
        el.removeAttribute("aria-invalid");
    });
    rows.forEach((r) => {
        const s = document.getElementById(`srow-status-${r.id}`);
        if (s) s.innerHTML = "";
    });
}

// Compute all issues without touching the DOM, so callers can decide whether
// to *render* them (only after the user presses "Check submission").
function computeValidation() {
    const shErrors = [];
    const shWarns = [];
    const shInvalid = new Set();
    SHARED_FIELDS.forEach((f) => {
        if (!f.required) return;
        const blank = isBlank(shared[f.col]);
        let invalid = blank;
        if (blank) {
            shErrors.push(`${f.label} is required.`);
        } else if (f.col === "Date" && !/^\d{4}-\d{2}-\d{2}$/.test(String(shared["Date"]).trim())) {
            shErrors.push("Date must be in YYYY-MM-DD format.");
            invalid = true;
        }
        if (invalid) shInvalid.add(f.col);
    });
    // Multiple authors need one affiliation each, in the same order (mirrors the
    // authoritative checker's warning in misc/ci/check_submission.py).
    const submitters = String(shared["Submitter"] || "").split(",").map((s) => s.trim()).filter(Boolean);
    const affiliations = String(shared["Affiliation"] || "").split(",").map((s) => s.trim()).filter(Boolean);
    if (submitters.length > 1 && affiliations.length !== submitters.length) {
        shWarns.push(`${submitters.length} author(s) in Submitter but ${affiliations.length} in Affiliation — provide one affiliation per author, in the same order (repeat shared affiliations).`);
    }
    if (!rows.length) shErrors.push("Add at least one result row.");

    const seen = new Map();
    rows.forEach((r) => {
        const key = `${r.problemId}::${r.instance}`;
        if (r.problemId && r.instance) seen.set(key, (seen.get(key) || 0) + 1);
    });

    const rowResults = rows.map((r) => {
        const res = validateRow(r);
        if (r.problemId && r.instance && seen.get(`${r.problemId}::${r.instance}`) > 1) {
            res.warns.push("Duplicate of another row (same problem + instance).");
        }
        return { r, res };
    });

    const totalErr = shErrors.length + rowResults.reduce((a, x) => a + x.res.errors.length, 0);
    const totalWarn = shWarns.length + rowResults.reduce((a, x) => a + x.res.warns.length, 0);
    return { shErrors, shWarns, shInvalid, rowResults, totalErr, totalWarn };
}

function validateAll() {
    const { shErrors, shWarns, shInvalid, rowResults, totalErr, totalWarn } = computeValidation();
    const summary = document.getElementById("val-summary");
    const valList = document.getElementById("val-list");

    // Before the first explicit check: keep the form calm — no red boxes, no list.
    if (!validated) {
        clearInvalidMarks();
        if (summary) summary.innerHTML = '<span class="pill-warn">not checked yet</span>';
        if (valList) {
            valList.innerHTML = '<div class="vmsg vok">Fill in your results, then press <strong>Check submission</strong> to validate.</div>';
        }
        return totalErr;
    }

    // After checking: mark invalid inputs and render the issue list (stays live).
    SHARED_FIELDS.forEach((f) => {
        document.querySelectorAll(`#shared-grid [data-col="${f.col}"]`).forEach((el) => markInvalid(el, shInvalid.has(f.col)));
    });

    const blocks = [];
    if (shErrors.length || shWarns.length) {
        blocks.push(`<div class="vblock"><div class="vb-head">Shared details</div>${
            shErrors.map((m) => `<div class="vmsg verr">✕ ${qEsc(m)}</div>`).join("") +
            shWarns.map((m) => `<div class="vmsg vwarn">⚠ ${qEsc(m)}</div>`).join("")
        }</div>`);
    }

    rowResults.forEach(({ r, res }) => {
        const rowEl = document.getElementById(`srow-${r.id}`);
        if (rowEl) {
            const inUse = r.problemId && !isBlank(r.instance);
            markInvalid(rowEl.querySelector('[data-role="problem"]'), !r.problemId);
            markInvalid(rowEl.querySelector('[data-role="instance"]'), isBlank(r.instance));
            ROW_FIELDS.forEach((f) => {
                if (!f.required) return;
                const el = rowEl.querySelector(`[data-col="${f.col}"]`);
                markInvalid(el, Boolean(inUse) && isBlank(r.data[f.col]));
            });
        }

        const statusEl = document.getElementById(`srow-status-${r.id}`);
        if (statusEl) {
            if (res.errors.length) statusEl.innerHTML = `<span class="pill-err">${res.errors.length} error${res.errors.length > 1 ? "s" : ""}</span>`;
            else if (res.warns.length) statusEl.innerHTML = `<span class="pill-warn">${res.warns.length} warning${res.warns.length > 1 ? "s" : ""}</span>`;
            else statusEl.innerHTML = `<span class="pill-ok">✓ valid</span>`;
        }

        const label = r.problemId && r.instance ? `${String(r.problemId).padStart(2, "0")} / ${r.instance}` : `Row #${r.idx}`;
        if (res.errors.length || res.warns.length) {
            blocks.push(`<div class="vblock"><div class="vb-head">${qEsc(label)}</div>${
                res.errors.map((m) => `<div class="vmsg verr">✕ ${qEsc(m)}</div>`).join("") +
                res.warns.map((m) => `<div class="vmsg vwarn">⚠ ${qEsc(m)}</div>`).join("")
            }</div>`);
        }
    });

    if (summary) {
        if (totalErr === 0 && totalWarn === 0) summary.innerHTML = '<span class="pill-ok">✓ all checks pass</span>';
        else summary.innerHTML = `${totalErr ? `<span class="pill-err">${totalErr} error${totalErr > 1 ? "s" : ""}</span>` : ""} ${totalWarn ? `<span class="pill-warn">${totalWarn} warning${totalWarn > 1 ? "s" : ""}</span>` : ""}`;
    }
    if (valList) {
        valList.innerHTML = blocks.join("") || '<div class="vmsg vok">Nothing to flag yet — your submission looks valid.</div>';
    }

    return totalErr;
}

function runCheck() {
    validated = true;
    const errs = validateAll();
    if (errs === 0) {
        const panel = document.getElementById("validation-panel");
        if (panel) panel.scrollIntoView({ behavior: "smooth", block: "start" });
        showToast("All checks pass ✓");
        return;
    }
    // Send keyboard / AT users straight to the first problem rather than making
    // them hunt for the highlighted field.
    const firstInvalid = document.querySelector("#shared-grid .invalid, #rows .invalid");
    if (firstInvalid) {
        firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
        firstInvalid.focus({ preventScroll: true });
    } else {
        document.getElementById("validation-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    showToast(`${errs} issue${errs > 1 ? "s" : ""} to fix — see the highlighted fields.`, "error");
}

// ---------------------------------------------------------------------------
// CSV generation
// ---------------------------------------------------------------------------

function csvCell(v) {
    const s = v == null ? "" : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

function rowRecord(row) {
    const rec = {};
    CSV_COLUMNS.forEach((c) => (rec[c] = ""));
    rec["Problem"] = row.instance;
    // Shared fields.
    SHARED_FIELDS.forEach((f) => {
        if (f.col.startsWith("__")) return;
        if (CSV_COLUMNS.includes(f.col)) rec[f.col] = shared[f.col] || "";
    });
    // Per-row fields.
    ROW_FIELDS.forEach((f) => {
        if (CSV_COLUMNS.includes(f.col)) rec[f.col] = row.data[f.col] || "";
    });
    return rec;
}

function rowCsv(row) {
    const rec = rowRecord(row);
    const header = CSV_COLUMNS.join(",");
    const line = CSV_COLUMNS.map((c) => csvCell(rec[c])).join(",");
    return `${header}\n${line}\n`;
}

function folderName() {
    const date = String(shared["Date"] || "").replace(/-/g, "") || "submission";
    const tag = sanitizeTag(shared["__team"] || (shared["Submitter"] || "").split(/[ ,]/)[0]) || "team";
    return `${date}_${tag}`;
}

function buildFiles() {
    const folder = folderName();
    const files = [];
    rows.forEach((r) => {
        if (!r.problemId || !r.instance) return;
        const p = (SITE_INDEX.problems || []).find((x) => x.id === r.problemId);
        if (!p) return;
        const dir = problemDir(p);
        const path = `${dir}/submissions/${folder}/${r.instance}/${r.instance}_summary.csv`;
        files.push({ path, content: rowCsv(r), instance: r.instance, problem: dir });
    });
    return { folder, files };
}

function exportReadme(folder, files) {
    const byProblem = {};
    files.forEach((f) => (byProblem[f.problem] = byProblem[f.problem] || []).push(f.instance));
    const lines = [
        "QOBLIB submission bundle",
        "========================",
        "",
        `Folder tag: ${folder}`,
        "",
        "1. Unzip this archive at the ROOT of your QOBLIB fork (paths already match the repo).",
        "2. For every '<instance>_summary.csv' add the corresponding solution file in the SAME folder,",
        "   named '<instance>_solution.<ext>' (see the problem's solutions/ folder for the format).",
        "3. Validate locally:  uv run --project misc qoblib-check-submission <problem-dir>/submissions/" + folder,
        "4. Commit and open a pull request. A GitHub Action will re-validate automatically.",
        "",
        "Included instances:",
    ];
    Object.keys(byProblem).sort().forEach((dir) => {
        lines.push(`  ${dir}:`);
        byProblem[dir].sort().forEach((i) => lines.push(`    - ${i}  (add ${i}_solution.<ext>)`));
    });
    return lines.join("\n") + "\n";
}

async function downloadZip() {
    validated = true; // exporting counts as a check — surface any issues
    const errs = validateAll();
    const { folder, files } = buildFiles();
    if (!files.length) {
        showToast("Add at least one valid result row first.", "error");
        return;
    }
    if (typeof JSZip === "undefined") {
        showToast("ZIP library failed to load — use Preview files to copy CSVs instead.", "error");
        return;
    }
    const zip = new JSZip();
    files.forEach((f) => zip.file(f.path, f.content));
    zip.file(`SUBMISSION_README_${folder}.txt`, exportReadme(folder, files));
    const blob = await zip.generateAsync({ type: "blob" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `qoblib_submission_${folder}.zip`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    if (errs > 0) showToast(`ZIP downloaded with ${errs} unresolved error${errs > 1 ? "s" : ""} — fix before opening the PR.`, "warn");
    else showToast(`ZIP downloaded — ${files.length} instance file${files.length > 1 ? "s" : ""}.`);
}

function previewFiles() {
    const out = document.getElementById("preview-out");
    const { folder, files } = buildFiles();
    if (!files.length) {
        out.style.display = "block";
        out.innerHTML = '<div class="empty-state">No valid rows yet — pick a problem and instance.</div>';
        return;
    }
    out.style.display = "block";
    const tree = files.map((f) => `  ${qEsc(f.path)}`).join("\n");
    out.innerHTML =
        `<div class="ss-title">Folder layout (${files.length} file${files.length > 1 ? "s" : ""})</div>` +
        `<pre class="code-pre">${qEsc(folder)}/\n${tree}</pre>` +
        files.map((f, i) => `
            <div class="file-block">
                <div class="file-head">
                    <span class="mono">${qEsc(f.path)}</span>
                    <button class="btn btn-ghost btn-sm" type="button" onclick="copyFile(${i})">Copy CSV</button>
                </div>
                <pre class="code-pre" id="file-${i}">${qEsc(f.content)}</pre>
            </div>`).join("");
    window.__previewFiles = files;
}

function copyFile(i) {
    const f = (window.__previewFiles || [])[i];
    if (!f) return;
    navigator.clipboard.writeText(f.content).then(() => showToast("CSV copied to clipboard."));
}

// ---------------------------------------------------------------------------
// CSV import
// ---------------------------------------------------------------------------

function parseCsv(text) {
    // Minimal RFC-4180 parser (handles quotes, commas, newlines).
    text = text.replace(/^﻿/, "").replace(/\r\n?/g, "\n");
    const records = [];
    let field = "";
    let record = [];
    let inQuotes = false;
    for (let i = 0; i < text.length; i++) {
        const c = text[i];
        if (inQuotes) {
            if (c === '"') {
                if (text[i + 1] === '"') { field += '"'; i++; }
                else inQuotes = false;
            } else field += c;
        } else if (c === '"') inQuotes = true;
        else if (c === ",") { record.push(field); field = ""; }
        else if (c === "\n") { record.push(field); records.push(record); field = ""; record = []; }
        else field += c;
    }
    if (field !== "" || record.length) { record.push(field); records.push(record); }
    return records.filter((r) => r.length && r.some((v) => v.trim() !== ""));
}

async function importCsvText(text) {
    const recs = parseCsv(text);
    if (!recs.length) return 0;
    const header = recs[0].map((h) => h.trim());
    const idx = {};
    CSV_COLUMNS.forEach((c) => (idx[c] = header.indexOf(c)));
    if (idx["Problem"] < 0) {
        showToast("That CSV has no 'Problem' column — is it a QOBLIB summary file?", "error");
        return 0;
    }
    // Ensure all problems are indexed so we can map instance -> problem.
    await Promise.all((SITE_INDEX.problems || []).map((p) => getProblem(p.id)));

    let added = 0;
    recs.slice(1).forEach((rec) => {
        const get = (c) => (idx[c] >= 0 ? (rec[idx[c]] || "").trim() : "");
        const instance = get("Problem");
        if (!instance) return;
        // Adopt shared fields from the imported rows. Import wins over auto-filled
        // defaults (e.g. today's Date) and blanks, but never clobbers a value the
        // user typed in by hand before importing.
        SHARED_FIELDS.forEach((f) => {
            if (f.col.startsWith("__")) return;
            let imported = get(f.col);
            if (isBlank(imported) || sharedTouched.has(f.col)) return;
            // Normalise to the shapes the inputs/validator expect: dates → canonical
            // YYYY-MM-DD (authors write timestamps, "22. Dec. 2024", …); select values
            // → the option's exact casing (real data uses "Deterministic").
            if (f.col === "Date") {
                imported = qFmtDate(imported);
            } else if (f.type === "select" && f.options) {
                const match = f.options.find((o) => o && o.toLowerCase() === imported.toLowerCase());
                if (match) imported = match;
            }
            shared[f.col] = imported;
        });
        const data = {};
        ROW_FIELDS.forEach((f) => { if (!isBlank(get(f.col))) data[f.col] = get(f.col); });
        // Discard the pristine seeded row so an import doesn't leave a leading
        // blank row #1 that fails validation.
        if (added === 0 && rows.length === 1 && !rowHasData(rows[0])) rows.length = 0;
        rowSeq += 1;
        rows.push({
            id: rowSeq,
            idx: rows.length + 1,
            problemId: INSTANCE_INDEX.get(instance) || "",
            instance,
            data,
        });
        added += 1;
    });

    renderShared();
    renderRows();
    return added;
}

function onImportFiles(fileList) {
    const note = document.getElementById("import-note");
    const files = Array.from(fileList || []);
    if (!files.length) return;
    let total = 0;
    let pending = files.length;
    files.forEach((file) => {
        const reader = new FileReader();
        reader.onload = async () => {
            total += await importCsvText(String(reader.result || ""));
            pending -= 1;
            if (pending === 0) {
                note.style.display = "block";
                note.textContent = `Imported ${total} row${total !== 1 ? "s" : ""} from ${files.length} file${files.length !== 1 ? "s" : ""}. Review the flagged items below.`;
                showToast(`Imported ${total} row${total !== 1 ? "s" : ""}.`);
            }
        };
        reader.readAsText(file);
    });
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

async function initSubmitPage() {
    qInitCommon();
    try {
        SITE_INDEX = await qLoadIndex();
    } catch (error) {
        qShowError(document.getElementById("rows"), error.message);
        return;
    }

    shared["Date"] = new Date().toISOString().slice(0, 10);
    renderShared();
    addRow();

    // Guard each lookup so a renamed/removed control can't throw and take the
    // whole page down with it.
    document.getElementById("add-row-btn")?.addEventListener("click", () => addRow());
    document.getElementById("check-btn")?.addEventListener("click", runCheck);
    document.getElementById("zip-btn")?.addEventListener("click", downloadZip);
    document.getElementById("preview-btn")?.addEventListener("click", previewFiles);
    document.getElementById("csv-upload")?.addEventListener("change", (e) => onImportFiles(e.target.files));

    // Instance autocomplete: delegate on the persistent #rows host so dynamically
    // added rows are covered without re-binding per render.
    const rowsHost = document.getElementById("rows");
    if (rowsHost) {
        rowsHost.addEventListener("focusin", onRowsFocusin);
        rowsHost.addEventListener("focusout", onRowsFocusout);
        rowsHost.addEventListener("keydown", onRowsKeydown);
        rowsHost.addEventListener("mousedown", onRowsMousedown);
    }
    // Click outside any autocomplete closes the open menu.
    document.addEventListener("mousedown", (e) => {
        if (!e.target.closest?.(".ac")) closeAllAc();
    });

    // Warn before navigating away once the form holds entered data — there is no
    // server-side draft, so an accidental refresh would otherwise lose everything.
    window.addEventListener("beforeunload", (e) => {
        if (sharedTouched.size === 0 && !rows.some(rowHasData)) return;
        e.preventDefault();
        e.returnValue = "";
    });

    // Pre-select a problem/instance if linked from another page (?problem=07&instance=foo).
    const params = new URLSearchParams(window.location.search);
    const pid = params.get("problem");
    const inst = params.get("instance") || params.get("name");
    if (pid || inst) {
        rows.length = 0;
        addRow({ problemId: pid || "", instance: inst || "" });
    }
}

// Expose inline handlers.
window.onSharedInput = onSharedInput;
window.onRowInput = onRowInput;
window.onProblemChange = onProblemChange;
window.onInstanceInput = onInstanceInput;
window.removeRow = removeRow;
window.copyFile = copyFile;

initSubmitPage();
