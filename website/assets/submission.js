"use strict";

const {
    esc: qEsc,
    fmtNum: qFmtNum,
    fmtDate: qFmtDate,
    submissionDate: qSubmissionDate,
    loadProblemData: qLoadProblemData,
    loadProblemSubmissionGroups: qLoadProblemSubmissionGroups,
    instanceUrl: qInstanceUrl,
    problemUrl: qProblemUrl,
    showError: qShowError,
    initCommon: qInitCommon,
    setPageMeta: qSetPageMeta,
} = window.QOBLIB;

function fmtMaybeNum(v) {
    if (v == null || v === "") return "-";
    const num = Number(v);
    return Number.isFinite(num) ? qFmtNum(num) : qEsc(String(v));
}

// Parse a runtime cell to a finite number, or null (blank / "N/A" / non-numeric).
function runtimeNum(v) {
    if (v == null || v === "") return null;
    const n = Number(String(v).replace(/,/g, "").trim());
    return Number.isFinite(n) ? n : null;
}

// A runtime field is "present" for a submission if any row reports a value that
// is strictly non-zero — a reported 0 s (or blank / N/A) carries no information,
// so those breakdown columns are dropped rather than shown as a column of zeros.
function hasNonZeroRuntime(rows, key) {
    return rows.some((r) => {
        const n = runtimeNum(r[key]);
        return n != null && n !== 0;
    });
}

// The optional per-hardware runtime breakdown columns, in display order. Total
// Runtime and Time to Solution are always shown; these appear only when used.
const RUNTIME_BREAKDOWN = [
    { key: "runtime_cpu", label: "CPU (s)" },
    { key: "runtime_gpu", label: "GPU (s)" },
    { key: "runtime_qpu", label: "QPU (s)" },
    { key: "runtime_other", label: "Other HW (s)" },
];

function fileDisplayName(path) {
    if (!path) return "submission file";
    const parts = String(path).split("/").filter(Boolean);
    if (!parts.length) return String(path);
    if (parts.length === 1) return parts[0];
    return `${parts[parts.length - 2]}/${parts[parts.length - 1]}`;
}

const PROFILE_FIELDS = [
    ["Submitter", "submitter"],
    ["Affiliation", "affiliation"],
    ["Date", "date"],
    ["Reference", "reference"],
    ["Modeling approach", "modeling_approach"],
    ["Algorithm type", "algorithm_type"],
    ["Paradigm", "paradigm"],
    ["Workflow", "workflow"],
    ["Hardware", "hardware"],
    ["Success threshold", "success_threshold"],
    ["Remarks", "remarks"],
];

function profileEntries(profile) {
    return PROFILE_FIELDS
        .map(([label, key]) => [label, key === "date" ? normalizeDate(profile?.[key]) : profile?.[key]])
        .filter(([, val]) => val != null && String(val).trim() !== "");
}

// Render the date in the canonical YYYY-MM-DD form, but leave empty values
// empty so the entry is filtered out rather than shown as a placeholder.
function normalizeDate(v) {
    return v == null || String(v).trim() === "" ? v : qFmtDate(v);
}

function valueByLabel(entries, label) {
    const found = entries.find((item) => item[0] === label);
    return found ? found[1] : "";
}

function renderDetailGrid(entries) {
    if (!entries.length) {
        return '<div class="empty-state">No metadata provided for this submission.</div>';
    }
    return `<div class="meta-grid">${entries
        .map(
            ([label, val]) => `
                <div class="meta-item">
                    <div class="meta-k">${qEsc(label)}</div>
                    <div class="meta-v">${qEsc(String(val))}</div>
                </div>`,
        )
        .join("")}</div>`;
}

async function initSubmissionPage() {
    qInitCommon();
    const params = new URLSearchParams(window.location.search);
    const problemId = params.get("problem") || "";
    const submissionId = params.get("id") || "";
    const container = document.getElementById("submission-detail");

    if (!problemId || !submissionId) {
        qShowError(container, "Missing problem or submission id in URL.");
        return;
    }

    try {
        const [problem, groups] = await Promise.all([
            qLoadProblemData(problemId),
            qLoadProblemSubmissionGroups(problemId),
        ]);

        const group = (groups || []).find((g) => g.id === submissionId);
        if (!group) {
            throw new Error(`Submission \"${submissionId}\" was not found in problem ${problemId}.`);
        }

        // Fill the date from the package name when the submission's own date is
        // missing/unparseable (see submissionDate), so the detail page shows it.
        const entries = profileEntries({ ...(group.profile || {}), date: qSubmissionDate(group) });
        const sourceFiles = group.source_files || [];
        const sourceDir = group.source_dir || submissionId;
        qSetPageMeta({ title: `${sourceDir} · ${problem.name} — QOBLIB` });
        const sourceFileCount = sourceFiles.length;

        const instances = [...(group.instances || [])].sort((a, b) => String(a.instance || "").localeCompare(String(b.instance || "")));
        const instanceSubmissionMap = new Map();
        Object.values(problem.instance_submissions || {}).flat().forEach((row) => {
            if ((row?._source_dir || "") === sourceDir && row.instance && !instanceSubmissionMap.has(row.instance)) {
                instanceSubmissionMap.set(row.instance, row);
            }
        });

        const summaryRows = [
            ["Submitted instances", String(instances.length)],
            ["Source package", sourceDir],
            ["CSV files", String(sourceFileCount)],
            ["Submitter", valueByLabel(entries, "Submitter")],
            ["Date", valueByLabel(entries, "Date")],
            ["Approach", valueByLabel(entries, "Modeling approach") || valueByLabel(entries, "Algorithm type")],
        ].filter(([, v]) => v != null && String(v).trim() !== "");

        container.innerHTML = `
            <a class="back" href="submissions.html">← Back to Submissions</a>
            <div class="dh">
                <div>
                    <div class="d-num">${String(problem.id).padStart(2, "0")} / submission package</div>
                    <h1 class="d-title">${qEsc(submissionId)}</h1>
                    <div class="d-sub">${qEsc(problem.name)}</div>
                    <div class="hero-actions submission-links" style="margin-top:0.6rem">
                        <a class="btn btn-ghost" href="${qProblemUrl(problem.id)}">Problem Overview</a>
                        <a class="btn btn-ghost" href="submissions.html">All Submissions</a>
                        <a class="btn btn-ghost" href="leaderboard.html">Leaderboard</a>
                    </div>
                </div>
                <div class="d-meta">
                    ${summaryRows
                        .map(([label, value]) => {
                            // Free-text fields can be long, so let them span the
                            // full width instead of cramping into a half column.
                            const wide = ["Source package", "Submitter", "Approach"].includes(label);
                            return `<div class="mr${wide ? " mr-wide" : ""}"><span class="mk">${qEsc(label)}</span><span class="mv">${qEsc(String(value))}</span></div>`;
                        })
                        .join("") || '<div class="mr mr-wide"><span class="mk">Summary</span><span class="mv">No metadata provided</span></div>'}
                </div>
            </div>

            <div class="ss-title">Submission Details</div>
            ${renderDetailGrid(entries)}

            <div class="ss-title">Submitted Instances (${instances.length})</div>
            ${instances.length ? (() => {
                // Pair each instance with its CSV row once, then keep only the
                // per-hardware runtime columns that carry a non-zero value in this
                // submission. Total Runtime and Time to Solution are always shown;
                // CPU/GPU/QPU/Other appear only when actually used, so a submission
                // never shows columns of zeros for hardware it did not touch.
                const csvRows = instances.map((row) => instanceSubmissionMap.get(row.instance) || {});
                const activeCols = RUNTIME_BREAKDOWN.filter((c) => hasNonZeroRuntime(csvRows, c.key));
                return `<div class="tw"><table>
                <thead>
                    <tr>
                        <th data-sort-default="asc">Instance</th>
                        <th style="text-align:right">Objective</th>
                        <th style="text-align:right">Optimality Bound</th>
                        <th style="text-align:right">Runtime (s)</th>
                        <th style="text-align:right">Time to Sol. (s)</th>
                        ${activeCols.map((c) => `<th style="text-align:right">${qEsc(c.label)}</th>`).join("")}
                        <th>Hardware</th>
                        <th style="text-align:right">Vars</th>
                    </tr>
                </thead>
                <tbody>
                    ${instances
                        .map(
                            (row, i) => {
                                const csvRow = csvRows[i];
                                return `
                                <tr>
                                    <td class="mono"><a class="rlink mono" href="${qInstanceUrl(problem.id, row.instance)}">${qEsc(row.instance)}</a></td>
                                    <td class="num" style="font-weight:600">${fmtMaybeNum(row.value)}</td>
                                    <td class="num">${fmtMaybeNum(row.optimality_bound)}</td>
                                    <td class="num">${fmtMaybeNum(csvRow.runtime_total)}</td>
                                    <td class="num">${fmtMaybeNum(csvRow.time_to_solution)}</td>
                                    ${activeCols.map((c) => `<td class="num">${fmtMaybeNum(csvRow[c.key])}</td>`).join("")}
                                    <td class="mono">${qEsc(csvRow.hardware || "")}</td>
                                    <td class="num">${fmtMaybeNum(csvRow.n_vars)}</td>
                                </tr>`;
                            }
                        )
                        .join("")}
                </tbody>
            </table></div>`;
            })() : '<div class="empty-state">No instances were found for this submission.</div>'}
        `;
    } catch (error) {
        qShowError(container, error.message);
    }
}

initSubmissionPage();
