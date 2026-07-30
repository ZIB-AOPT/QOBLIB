"use strict";

const {
    esc: qEsc,
    fmtNum: qFmtNum,
    fmtText: qFmtText,
    parseDate: qParseDate,
    fmtDate: qFmtDate,
    loadIndex: qLoadIndex,
    loadProblemData: qLoadProblemData,
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
    orderRowsByTable: qOrderRowsByTable,
    fmtMaybeNum: qFmtMaybeNum,
    enableTableSorting: qEnableTableSorting,
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
            if (!lbFeasible(s)) return false;
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
        // allSettled so one problem's data failing to load doesn't blank the whole
        // leaderboard — the failed problem is skipped (logged) and the rest render.
        const settled = await Promise.allSettled(problems.map((p) => qLoadProblemData(p.id)));
        const datas = [];
        settled.forEach((r, i) => {
            if (r.status === "fulfilled") datas.push(r.value);
            else console.warn(`Leaderboard: skipping problem ${problems[i]?.id}: ${r.reason?.message || r.reason}`);
        });

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
                        .filter(lbFeasible)
                        .map((s) => { const raw = lbNum(s.value); const v = !Number.isFinite(raw) && feas ? 0 : raw; return { v }; })
                        .filter((o) => Number.isFinite(o.v));
                    records.push(lbMakeRecord(p.id, inst, overallChamp, feas, allFeas));
                }

                // --- Quantum champion (quantum_hw | quantum_sim) ---
                const qChamp = lbChampion(rawSubs, minimize, feas, QUANTUM_CATS);
                if (qChamp) {
                    const qFeas = rawSubs
                        .filter((s) => lbFeasible(s) && QUANTUM_CATS.has(s.category || qClassify(s)))
                        .map((s) => { const raw = lbNum(s.value); const v = !Number.isFinite(raw) && feas ? 0 : raw; return { v }; })
                        .filter((o) => Number.isFinite(o.v));
                    quantumRecords.push(lbMakeRecord(p.id, inst, qChamp, feas, qFeas));
                }
            });
        });

        const lbProb = document.getElementById("lb-prob");
        problems.forEach((p) => {
            const o = document.createElement("option");
            o.value = p.id;
            o.textContent = `${String(p.id).padStart(2, "0")} - ${p.name}`;
            lbProb.appendChild(o);
        });

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

    // Update button states
    document.getElementById("lb-vt-overall")?.classList.toggle("lb-vt-active", view === "overall");
    document.getElementById("lb-vt-quantum")?.classList.toggle("lb-vt-active", view === "quantum");

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
    const prevSort = content.querySelector("table")?.qoblibSort;

    if (!rows.length) {
        const filtering = pid || document.getElementById("lb-inst")?.value || paradigm;
        content.innerHTML = `<div class="lb-empty">${filtering ? "No records match the current filters." : "No submissions yet."}</div>`;
        return;
    }

    // Build a context label for the legend.
    const viewLabel = activeView === "quantum" ? "best quantum submission" : "best feasible submission";
    const paradigmExtra = paradigm ? ` (${(qCATS[paradigm] || qCATS.classical).label} only)` : "";

    // In Quantum view: add a "Gap to best-known" column to show how the best
    // quantum result compares to the global best.
    const showGap = activeView === "quantum";

    content.innerHTML = `<div class="tw"><table>
        <thead>
            <tr>
                <th>Instance</th>
                <th>Problem</th>
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
        <tbody>
            ${rows.map((r) => {
                let gapCell = "";
                if (showGap) {
                    // Re-read best_known from instanceMeta for this instance.
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
                        // Gap = |quantum_best - global_best| / |global_best| × 100
                        const gap = Math.abs(r.value - bk) / Math.max(1e-9, Math.abs(bk)) * 100;
                        const fmt = gap >= 100 ? gap.toFixed(0) : gap >= 10 ? gap.toFixed(1) : gap.toFixed(2);
                        gapCell = `<td class="num">${fmt}%</td>`;
                    }
                }
                return `<tr data-export-key="${qEsc(String(r.problem_id) + "::" + r.instance)}">
                    <td class="mono"><a class="rlink mono" href="${qInstanceUrl(r.problem_id, r.instance)}">${qEsc(r.instance)}</a></td>
                    <td><a class="badge b-type" href="${qProblemUrl(r.problem_id)}">${String(r.problem_id).padStart(2, "0")}</a></td>
                    <td class="num">${r.noValue ? '<span title="A feasible solution was found; this problem reports no objective value">feasible</span>' : qFmtNum(r.value)}${r.reachedBest ? ' <span title="Reaches the best-known objective" style="color:var(--star)">★</span>' : ""}</td>
                    ${gapCell}
                    <td>${qStatusPill(r.status)}</td>
                    <td>${r.source_dir ? `<a class="rlink" href="${qSubmissionUrl(r.problem_id, r.source_dir)}">${qFmtText(r.holder)}</a>` : qFmtText(r.holder)}</td>
                    <td>${qCatBadge(r.category)}</td>
                    <td class="mono">${qEsc(qFmtDate(r.date))}</td>
                    <td class="num">${qFmtMaybeNum(r.runtime)}</td>
                    <td class="num">${r.nSubs}</td>
                </tr>`;
            }).join("")}
        </tbody>
    </table></div>
    <div class="table-legend" style="margin:.4rem 0 .6rem;color:var(--muted)">One record per instance: the ${viewLabel}${paradigmExtra} and who holds it. ★ = reaches the best-known objective. "Subs" counts the ranked feasible submissions for that instance${activeView === "quantum" ? " (quantum only)" : ""}. Gap = |quantum best − global best| / |global best|.</div>`;

    if (prevSort) {
        const table = content.querySelector("table");
        if (table) {
            qEnableTableSorting(content);
            table.qoblibSort = prevSort;
            table.reapplySort?.();
        }
    }
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
                String(a.instance).localeCompare(String(b.instance)),
        );
}

function downloadLeaderboardCsv() {
    const rows = getLeaderboardRows();
    const headers = [
        "Problem ID", "Instance", "Best objective", "Reaches best", "Status",
        "Holder", "Type", "Date", "Runtime (s)", "Submissions",
    ];
    // Reflect the user's clicked-column sort (the table re-orders in place; our
    // data list is in the page default order), so the CSV matches what's on screen.
    const table = document.querySelector("#lb-content table");
    const ordered = table
        ? qOrderRowsByTable(table, rows, rows.map((r) => `${r.problem_id}::${r.instance}`))
        : rows;
    const data = ordered.map((r) => [
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
