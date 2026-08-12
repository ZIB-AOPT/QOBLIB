"use strict";

const {
    esc: qEsc,
    fmtNum: qFmtNum,
    fmtText: qFmtText,
    parseDate: qParseDate,
    fmtDate: qFmtDate,
    loadIndex: qLoadIndex,
    loadLeaderboard: qLoadLeaderboard,
    instanceUrl: qInstanceUrl,
    problemUrl: qProblemUrl,
    submissionUrl: qSubmissionUrl,
    statusPill: qStatusPill,
    showError: qShowError,
    initCommon: qInitCommon,
    classifySubmission: qClassify,
    SUBMISSION_CATEGORIES: qCATS,
    catBadge: qCatBadge,
    downloadCsv: qDownloadCsv,
    fmtMaybeNum: qFmtMaybeNum,
    enableTableSorting: qEnableTableSorting,
    populateProblemFilter: qPopulateProblemFilter,
} = window.QOBLIB;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function lbNum(v) {
    if (v == null || v === "") return NaN;
    const n = Number(String(v).replace(/,/g, "").trim());
    return Number.isFinite(n) ? n : NaN;
}

function lbDate(v) {
    return qParseDate(v);
}

// A submission counts only if it reported at least one feasible solution.
function lbFeasible(s) {
    const nf = lbNum(s.n_feasible);
    return !(Number.isFinite(nf) && nf === 0);
}

// A submission may define/win a best value only if it is *attribution-eligible*:
// feasible AND not flagged bkv_eligible === false. The flag marks a run whose
// reported objective is not comparable to exact results (currently Birkhoff
// decompositions that do not reconstruct exactly). Absent ⇒ eligible (every other
// problem). Ineligible runs still appear in the per-instance submission tables
// (rendered from instance_submissions); they are only barred from being champions.
function lbAttributable(s) {
    return lbFeasible(s) && s.bkv_eligible !== false;
}

// A feasibility problem (e.g. Market Split): the goal is a feasible point.
function lbIsFeasibilityProblem(p) {
    let sawZero = false;
    for (const i of p.instances || []) {
        const bv = lbNum(i.best_value ?? i.bkv);
        if (!Number.isFinite(bv)) continue;
        if (bv !== 0) return false;
        sawZero = true;
    }
    return sawZero;
}

// Categories that count as "quantum" for the Quantum view.
const QUANTUM_CATS = new Set(["quantum_hw", "quantum_sim"]);

// ---------------------------------------------------------------------------
// Champion selection
// Pick the best feasible submission from `subs`, optionally restricted to a
// set of categories.  Returns null if no qualifying submission exists.
// ---------------------------------------------------------------------------
function lbChampion(rawSubs, minimize, feas, allowedCats = null) {
    const subs = rawSubs
        .filter((s) => {
            if (!lbAttributable(s)) return false;
            if (allowedCats) {
                const cat = s.category || qClassify(s);
                if (!allowedCats.has(cat)) return false;
            }
            return true;
        })
        .map((s) => {
            const raw = lbNum(s.value);
            const noValue = !Number.isFinite(raw);
            const v = noValue && feas ? 0 : raw;
            return { s, v, noValue, t: lbDate(s.date), rt: lbNum(s.runtime_total) };
        })
        .filter((o) => Number.isFinite(o.v));

    if (!subs.length) return null;

    subs.sort(
        (a, b) =>
            (minimize ? a.v - b.v : b.v - a.v) ||
            (Number.isFinite(a.t) ? a.t : Infinity) - (Number.isFinite(b.t) ? b.t : Infinity) ||
            (Number.isFinite(a.rt) ? a.rt : Infinity) - (Number.isFinite(b.rt) ? b.rt : Infinity),
    );
    return subs[0];
}

// Build one leaderboard record given a champion and instance metadata.
function lbMakeRecord(p_id, inst, champ, feas, allFeasSubs) {
    const c = champ.s;
    const bestKnown = lbNum(inst.best_value ?? inst.bkv);
    const scale = Math.max(1, Math.abs(bestKnown), Math.abs(champ.v));
    const reachedBest = feas
        ? Math.abs(champ.v) <= 1e-9
        : Number.isFinite(bestKnown) && Math.abs(champ.v - bestKnown) <= 1e-9 * scale;

    return {
        problem_id: p_id,
        instance: inst.name,
        status: inst.status,
        value: champ.v,
        noValue: champ.noValue && feas,
        reachedBest,
        // "Subs" counts all feasible qualified submissions for this instance
        // in the current view, not just the single champion.
        nSubs: allFeasSubs.length,
        holder: c.submitter || c.author || "",
        category: c.category || qClassify(c),
        date: c.date || "",
        runtime: c.runtime_total,
        source_dir: c._source_dir || "",
    };
}

// Build the per-paradigm best cards for one instance (used in Overall view).
function lbParadigmBests(problem_id, instance, allSubs, minimize, feas) {
    const bests = { classical: null, quantum_hw: null, quantum_sim: null };
    for (const [cat] of Object.entries(bests)) {
        const champ = lbChampion(allSubs, minimize, feas, new Set([cat]));
        if (!champ) continue;
        const c = champ.s;
        bests[cat] = {
            problem_id,
            instance,
            value: champ.v,
            noValue: champ.noValue && feas,
            holder: c.submitter || c.author || "",
            category: cat,
            date: c.date || "",
            runtime: c.runtime_total,
            source_dir: c._source_dir || "",
        };
    }
    return bests;
}

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

let records = [];         // Overall leaderboard (best per instance, any paradigm)
let quantumRecords = [];  // Quantum leaderboard (best per instance, quantum only)

// instanceSubsMap[problem_id][instance] = raw submissions array (pre-filter)
let instanceSubsMap = {};
// instanceMeta[problem_id][instance] = { minimize, feas, inst }
let instanceMeta = {};
let indexData = null;

// Active view: "overall" | "quantum"
let activeView = "overall";

// ---------------------------------------------------------------------------
// Data loading
// ---------------------------------------------------------------------------

async function initLeaderboardPage() {
    qInitCommon();

    try {
        indexData = await qLoadIndex();
        const problems = indexData.problems || [];
        // One request for the whole leaderboard (aggregated + trimmed at build
        // time) instead of fanning out to meta + instances + instance_submissions
        // for every problem. Shape: { problems: [{id, name, minimize, instances,
        // instance_submissions}] } — the same per-problem shape this code expects.
        const lb = await qLoadLeaderboard();
        const datas = lb.problems || [];

        records = [];
        quantumRecords = [];
        instanceSubsMap = {};
        instanceMeta = {};

        datas.forEach((p) => {
            const minimize = p.minimize !== false;
            const feas = lbIsFeasibilityProblem(p);
            const entries = p.instance_submissions || {};

            instanceSubsMap[p.id] = {};
            instanceMeta[p.id] = {};

            (p.instances || []).forEach((inst) => {
                const rawSubs = entries[inst.name] || [];
                instanceSubsMap[p.id][inst.name] = rawSubs;
                instanceMeta[p.id][inst.name] = { minimize, feas, inst };

                // --- Overall champion (any paradigm) ---
                const overallChamp = lbChampion(rawSubs, minimize, feas, null);
                if (overallChamp) {
                    const allFeas = rawSubs
                        .filter(lbAttributable)
                        .map((s) => { const raw = lbNum(s.value); const v = !Number.isFinite(raw) && feas ? 0 : raw; return { v }; })
                        .filter((o) => Number.isFinite(o.v));
                    records.push(lbMakeRecord(p.id, inst, overallChamp, feas, allFeas));
                }

                // --- Quantum champion (quantum_hw | quantum_sim) ---
                const qChamp = lbChampion(rawSubs, minimize, feas, QUANTUM_CATS);
                if (qChamp) {
                    const qFeas = rawSubs
                        .filter((s) => lbAttributable(s) && QUANTUM_CATS.has(s.category || qClassify(s)))
                        .map((s) => { const raw = lbNum(s.value); const v = !Number.isFinite(raw) && feas ? 0 : raw; return { v }; })
                        .filter((o) => Number.isFinite(o.v));
                    quantumRecords.push(lbMakeRecord(p.id, inst, qChamp, feas, qFeas));
                }
            });
        });

        // Idempotent: the overview build pre-renders these options for no-JS, so
        // appending here would list every problem twice. qPopulateProblemFilter
        // replaces any pre-rendered set instead of adding to it.
        qPopulateProblemFilter(document.getElementById("lb-prob"), problems);

        renderLeaderboard();
    } catch (error) {
        qShowError(document.getElementById("lb-content"), error.message);
    }
}

// ---------------------------------------------------------------------------
// View toggle
// ---------------------------------------------------------------------------

function setLeaderboardView(view) {
    activeView = view;

    // Update button states (visual + aria-pressed for assistive tech).
    const overallBtn = document.getElementById("lb-vt-overall");
    const quantumBtn = document.getElementById("lb-vt-quantum");
    overallBtn?.classList.toggle("lb-vt-active", view === "overall");
    quantumBtn?.classList.toggle("lb-vt-active", view === "quantum");
    overallBtn?.setAttribute("aria-pressed", String(view === "overall"));
    quantumBtn?.setAttribute("aria-pressed", String(view === "quantum"));

    // In Quantum view the paradigm filter only makes sense for hw vs sim.
    const paradigmSel = document.getElementById("lb-paradigm");
    if (paradigmSel) {
        // Update the placeholder text so it reflects the active view.
        const allOpt = paradigmSel.querySelector("option[value='']");
        if (allOpt) allOpt.textContent = view === "quantum" ? "All quantum paradigms" : "All paradigms";

        // Reset to "All" if the user had "Classical" selected — that would show nothing in Quantum view.
        if (view === "quantum" && paradigmSel.value === "classical") {
            paradigmSel.value = "";
            const notice = document.getElementById("lb-filter-notice");
            if (notice) {
                notice.textContent = "Paradigm filter reset to \u201cAll\u201d \u2014 Classical submissions are excluded from the Quantum view.";
                notice.hidden = false;
                clearTimeout(notice._hideTimer);
                notice._hideTimer = setTimeout(() => { notice.hidden = true; }, 5000);
            }
        }
    }

    renderLeaderboard();
}

// ---------------------------------------------------------------------------
// Best-by-paradigm panel (Overall view, single-instance focus)
// ---------------------------------------------------------------------------

function renderParadigmBests() {
    const panel = document.getElementById("lb-paradigm-bests");
    if (!panel) return;

    // Only in overall view, only when a single instance is focused.
    const pid = document.getElementById("lb-prob")?.value || "";
    const iid = document.getElementById("lb-inst")?.value || "";
    if (activeView !== "overall" || !pid || !iid) {
        panel.innerHTML = "";
        return;
    }

    const rawSubs = (instanceSubsMap[pid] || {})[iid];
    const m = (instanceMeta[pid] || {})[iid];
    if (!rawSubs || !m) { panel.innerHTML = ""; return; }

    const bests = lbParadigmBests(pid, iid, rawSubs, m.minimize, m.feas);
    if (!Object.values(bests).some(Boolean)) { panel.innerHTML = ""; return; }

    const cards = Object.entries(bests).map(([cat, rec]) => {
        const c = qCATS[cat] || qCATS.classical;
        if (!rec) {
            return `<div class="lb-pdg-card lb-pdg-empty">
                <div class="lb-pdg-dot" style="background:${c.color}"></div>
                <div class="lb-pdg-label">${qEsc(c.label)}</div>
                <div class="lb-pdg-holder lb-pdg-none">No submission yet</div>
            </div>`;
        }
        const valHtml = rec.noValue
            ? `<span title="Feasible solution found; no objective value">feasible</span>`
            : `<strong>${qFmtNum(rec.value)}</strong>`;
        const holderHtml = rec.source_dir
            ? `<a class="rlink" href="${qSubmissionUrl(rec.problem_id, rec.source_dir)}">${qFmtText(rec.holder)}</a>`
            : qFmtText(rec.holder);
        return `<div class="lb-pdg-card">
            <div class="lb-pdg-dot" style="background:${c.color}"></div>
            <div class="lb-pdg-label">${qEsc(c.label)}</div>
            <div class="lb-pdg-value">${valHtml}</div>
            <div class="lb-pdg-holder">${holderHtml}</div>
            <div class="lb-pdg-date mono">${qEsc(qFmtDate(rec.date))}</div>
        </div>`;
    }).join("");

    panel.innerHTML = `<div class="lb-pdg-wrap">
        <div class="lb-pdg-title">Best by paradigm — ${qEsc(iid)}</div>
        <div class="lb-pdg-grid">${cards}</div>
    </div>`;
}

// ---------------------------------------------------------------------------
// Main render
// ---------------------------------------------------------------------------

// Problem id → display name (from index.json), for the section headers.
function lbProblemName(pid) {
    const p = (indexData?.problems || []).find((x) => String(x.id) === String(pid));
    return p ? p.name : String(pid).padStart(2, "0");
}

// One record <tr>. The Problem column is omitted — the enclosing <details>
// section already names the problem (mirrors _lb_record_row in overview_pages.py).
// `showGap` adds the Quantum-view "Gap to best" cell.
function lbRecordRowHtml(r, showGap) {
    let gapCell = "";
    if (showGap) {
        const m = (instanceMeta[r.problem_id] || {})[r.instance];
        const bk = m ? lbNum(m.inst.best_value ?? m.inst.bkv) : NaN;
        const feas = m?.feas ?? false;
        if (r.noValue || feas) {
            gapCell = '<td class="num">—</td>';
        } else if (!Number.isFinite(bk)) {
            gapCell = '<td class="num muted">N/A</td>';
        } else if (r.reachedBest) {
            gapCell = '<td class="num" style="color:var(--star)">0.00%</td>';
        } else {
            const gap = Math.abs(r.value - bk) / Math.max(1e-9, Math.abs(bk)) * 100;
            const fmt = gap >= 100 ? gap.toFixed(0) : gap >= 10 ? gap.toFixed(1) : gap.toFixed(2);
            gapCell = `<td class="num">${fmt}%</td>`;
        }
    }
    return `<tr data-export-key="${qEsc(String(r.problem_id) + "::" + r.instance)}">
        <td class="mono"><a class="rlink mono" href="${qInstanceUrl(r.problem_id, r.instance)}">${qEsc(r.instance)}</a></td>
        <td class="num">${r.noValue ? '<span title="A feasible solution was found; this problem reports no objective value">feasible</span>' : qFmtNum(r.value)}${r.reachedBest ? ' <span title="Reaches the best-known objective" style="color:var(--star)">★</span>' : ""}</td>
        ${gapCell}
        <td>${qStatusPill(r.status)}</td>
        <td>${r.source_dir ? `<a class="rlink" href="${qSubmissionUrl(r.problem_id, r.source_dir)}">${qFmtText(r.holder)}</a>` : qFmtText(r.holder)}</td>
        <td>${qCatBadge(r.category)}</td>
        <td class="mono">${qEsc(qFmtDate(r.date))}</td>
        <td class="num">${qFmtMaybeNum(r.runtime)}</td>
        <td class="num">${r.nSubs}</td>
    </tr>`;
}

// A collapsible <details> section for one problem's records (mirrors
// _lb_problem_section in overview_pages.py).
function lbProblemSectionHtml(pid, recs, showGap, openSection) {
    const nBest = recs.reduce((s, r) => s + (r.reachedBest ? 1 : 0), 0);
    const bestChip = nBest
        ? `<span class="lb-sec-best" title="Records reaching the best-known objective">★ ${nBest.toLocaleString()}</span>`
        : "";
    const rows = recs.map((r) => lbRecordRowHtml(r, showGap)).join("");
    return `<details class="lb-prob-section"${openSection ? " open" : ""} data-problem="${qEsc(pid)}">
        <summary>
            <a class="badge b-type" href="${qProblemUrl(pid)}" onclick="event.stopPropagation()">${String(pid).padStart(2, "0")}</a>
            <span class="lb-sec-name">${qEsc(lbProblemName(pid))}</span>
            <span class="lb-sec-counts"><span class="lb-sec-recs">${recs.length.toLocaleString()} record${recs.length !== 1 ? "s" : ""}</span>${bestChip}</span>
        </summary>
        <div class="tw"><table>
            <thead>
                <tr>
                    <th>Instance</th>
                    <th style="text-align:right">Best objective</th>
                    ${showGap ? '<th style="text-align:right" title="Gap to the global best-known value">Gap to best</th>' : ""}
                    <th>Status</th>
                    <th>Holder</th>
                    <th>Type</th>
                    <th>Date</th>
                    <th style="text-align:right">Runtime (s)</th>
                    <th style="text-align:right">Subs</th>
                </tr>
            </thead>
            <tbody>${rows}</tbody>
        </table></div>
    </details>`;
}

function renderLeaderboard() {
    const pid = document.getElementById("lb-prob")?.value || "";
    const paradigm = document.getElementById("lb-paradigm")?.value || "";

    // Repopulate the instance filter for the chosen problem, using the active
    // record set so only instances with quantum submissions appear in Quantum view.
    const activeRecords = activeView === "quantum" ? quantumRecords : records;
    const instSel = document.getElementById("lb-inst");
    const cur = instSel.value;
    instSel.innerHTML = '<option value="">All instances</option>';
    activeRecords
        .filter((r) => !pid || r.problem_id === pid)
        .forEach((r) => {
            const o = document.createElement("option");
            o.value = r.instance;
            o.textContent = r.instance;
            instSel.appendChild(o);
        });
    // Restore previous selection only if it still exists in the new list.
    instSel.value = [...instSel.options].some((o) => o.value === cur) ? cur : "";

    // The paradigm filter "classical" is meaningless in Quantum view — hide it.
    const classicalOpt = document.querySelector("#lb-paradigm option[value='classical']");
    if (classicalOpt) classicalOpt.hidden = activeView === "quantum";

    // Best-by-paradigm panel (Overall only, single instance).
    renderParadigmBests();

    const rows = getLeaderboardRows();
    const countEl = document.getElementById("lb-count");
    if (countEl) countEl.textContent = `${rows.length} record${rows.length !== 1 ? "s" : ""}`;

    const content = document.getElementById("lb-content");
    if (!content) return;

    if (!rows.length) {
        const filtering = pid || document.getElementById("lb-inst")?.value || paradigm;
        content.innerHTML = `<div class="lb-empty">${filtering ? "No records match the current filters." : "No submissions yet."}</div>`;
        return;
    }

    // In Quantum view: add a "Gap to best-known" column showing how the best
    // quantum result compares to the global best.
    const showGap = activeView === "quantum";

    // Group the filtered rows by problem, keeping problem order from index.json
    // (the order the sections appear in). Each problem becomes one <details>.
    const order = (indexData?.problems || []).map((p) => String(p.id));
    const byProblem = new Map();
    for (const r of rows) {
        const key = String(r.problem_id);
        if (!byProblem.has(key)) byProblem.set(key, []);
        byProblem.get(key).push(r);
    }
    const orderedPids = [...byProblem.keys()].sort(
        (a, b) => (order.indexOf(a) + 1 || Infinity) - (order.indexOf(b) + 1 || Infinity) || a.localeCompare(b),
    );

    // All sections start collapsed, so the page opens as a compact problem index.
    // The one exception: when the user has narrowed to a single section (e.g. a
    // problem filter leaves just one), open it — that's a deliberate drill-in, not
    // the initial load.
    const openAll = orderedPids.length === 1;
    const sections = orderedPids
        .map((p) => lbProblemSectionHtml(p, byProblem.get(p), showGap, openAll))
        .join("");

    const viewLabel = activeView === "quantum" ? "best quantum submission" : "best feasible submission";
    const paradigmExtra = paradigm ? ` (${(qCATS[paradigm] || qCATS.classical).label} only)` : "";

    content.innerHTML = `<div class="lb-sections">${sections}</div>
    <div class="table-legend" style="margin:.4rem 0 .6rem;color:var(--muted)">Records are grouped by problem — expand a section for its table. One record per instance: the ${viewLabel}${paradigmExtra} and who holds it. ★ = reaches the best-known objective. "Subs" counts the ranked feasible submissions for that instance${activeView === "quantum" ? " (quantum only)" : ""}.${showGap ? " Gap = |quantum best − global best| / |global best|." : ""}</div>`;

    // Each section's table is independently sortable by its column headers.
    qEnableTableSorting(content);
}

// ---------------------------------------------------------------------------
// Filter helpers
// ---------------------------------------------------------------------------

function getLeaderboardRows() {
    const pid = document.getElementById("lb-prob")?.value || "";
    const iid = document.getElementById("lb-inst")?.value || "";
    const paradigm = document.getElementById("lb-paradigm")?.value || "";
    const src = activeView === "quantum" ? quantumRecords : records;
    return src
        .filter(
            (r) =>
                (!pid || r.problem_id === pid) &&
                (!iid || r.instance === iid) &&
                (!paradigm || r.category === paradigm),
        )
        .sort(
            (a, b) =>
                String(a.problem_id).localeCompare(String(b.problem_id)) ||
                // Numeric-aware so "ms_10" sorts after "ms_2" — matches the server
                // pre-render (_instance_sort_key in overview_pages.py), otherwise the
                // rows visibly reshuffle when the JS hydrates over the static HTML.
                String(a.instance).localeCompare(String(b.instance), undefined, { numeric: true, sensitivity: "base" }),
        );
}

function downloadLeaderboardCsv() {
    const rows = getLeaderboardRows();
    const headers = [
        "Problem ID", "Instance", "Best objective", "Reaches best", "Status",
        "Holder", "Type", "Date", "Runtime (s)", "Submissions",
    ];
    // Export in the default per-problem grouped order (grouped by problem, then
    // numeric-aware by instance). Each problem's table now sorts independently, so
    // there is no single on-screen order to mirror; the grouped order is stable and
    // matches how the page reads top to bottom.
    const data = rows.map((r) => [
        String(r.problem_id).padStart(2, "0"),
        r.instance,
        r.noValue ? "feasible" : r.value,
        r.reachedBest ? "yes" : "",
        r.status,
        r.holder,
        (qCATS[r.category] || qCATS.classical).label,
        qFmtDate(r.date),
        r.runtime ?? "",
        r.nSubs,
    ]);
    const filename = activeView === "quantum"
        ? "qoblib_leaderboard_quantum.csv"
        : "qoblib_leaderboard.csv";
    qDownloadCsv(filename, headers, data);
}

window.renderLeaderboard = renderLeaderboard;
window.downloadLeaderboardCsv = downloadLeaderboardCsv;
window.setLeaderboardView = setLeaderboardView;

document.getElementById("lb-vt-overall")?.addEventListener("click", () => setLeaderboardView("overall"));
document.getElementById("lb-vt-quantum")?.addEventListener("click", () => setLeaderboardView("quantum"));
document.getElementById("lb-prob")?.addEventListener("change", renderLeaderboard);
document.getElementById("lb-inst")?.addEventListener("change", renderLeaderboard);
document.getElementById("lb-paradigm")?.addEventListener("change", renderLeaderboard);
document.getElementById("lb-download")?.addEventListener("click", downloadLeaderboardCsv);

initLeaderboardPage();
