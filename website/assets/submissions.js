"use strict";

const {
    esc: qEsc,
    parseDate: qParseDate,
    fmtDate: qFmtDate,
    loadIndex: qLoadIndex,
    loadAllSubmissionGroups: qLoadAllSubmissionGroups,
    problemUrl: qProblemUrl,
    submissionUrl: qSubmissionUrl,
    initCommon: qInitCommon,
    classifySubmission: qClassify,
    SUBMISSION_CATEGORIES: qCATS,
    catBadge: qCatBadge,
    downloadCsv: qDownloadCsv,
    orderRowsByTable: qOrderRowsByTable,
    submissionDate: qSubmissionDate,
    submissionMethod: qSubmissionMethod,
    showError: qShowError,
    populateProblemFilter: qPopulateProblemFilter,
} = window.QOBLIB;

let allGroups = [];
let problemIndex = new Map();

// Compute-paradigm of a submission package. The builder tags each package with
// a `category` (the dominant paradigm of its rows); fall back to classifying
// the collapsed profile so the page still works against older data payloads.
function groupCategory(group) {
    return group.category || qClassify(group.profile || {});
}

function groupSearchText(group, problem) {
    const profile = group.profile || {};
    const sourceFiles = (group.source_files || []).join(" ");
    const instanceNames = (group.instances || []).map((item) => item.instance).join(" ");
    const cat = qCATS[groupCategory(group)] || qCATS.classical;
    return [
        group.id,
        group.source_dir,
        problem?.name,
        problem?.slug,
        profile.submitter,
        profile.affiliation,
        profile.date,
        qFmtDate(profile.date),
        profile.workflow,
        profile.hardware,
        profile.modeling_approach,
        profile.algorithm_type,
        cat.label,
        cat.short,
        sourceFiles,
        instanceNames,
    ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
}

function formatProblemLabel(problem) {
    if (!problem) return "-";
    return `${String(problem.id).padStart(2, "0")} - ${problem.name}`;
}

function renderStats(groups) {
    const totalInstances = groups.reduce((sum, group) => sum + (group.instances || []).length, 0);
    const problems = new Set(groups.map((group) => group.problem_id)).size;
    const authors = new Set(groups.map((group) => group.profile?.submitter || "").filter(Boolean)).size;
    const setStat = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value.toLocaleString();
    };
    setStat("sub-stat-packages", groups.length);
    setStat("sub-stat-instances", totalInstances);
    setStat("sub-stat-problems", problems);
    setStat("sub-stat-authors", authors);
}

function populateProblemFilter(indexData) {
    // Idempotent against the server-pre-rendered options — see the shared helper.
    qPopulateProblemFilter(
        document.getElementById("sub-prob"),
        indexData.problems || [],
        formatProblemLabel,
    );
}

function getFilteredGroups() {
    const search = (document.getElementById("sub-search")?.value || "").trim().toLowerCase();
    const problemId = document.getElementById("sub-prob")?.value || "";
    const category = document.getElementById("sub-cat")?.value || "";

    const filtered = allGroups.filter((group) => {
        if (problemId && group.problem_id !== problemId) return false;
        if (category && groupCategory(group) !== category) return false;
        if (!search) return true;
        const problem = problemIndex.get(group.problem_id);
        return groupSearchText(group, problem).includes(search);
    });

    // Default order is newest first. Re-sorting by any column is handled by the
    // clickable table headers (enableTableSorting), so no sort dropdown is needed.
    filtered.sort((a, b) => {
        const tsA = qParseDate(qSubmissionDate(a));
        const tsB = qParseDate(qSubmissionDate(b));
        return (Number.isFinite(tsB) ? tsB : -Infinity) - (Number.isFinite(tsA) ? tsA : -Infinity) ||
            String(a.problem_id).localeCompare(String(b.problem_id)) ||
            String(a.id).localeCompare(String(b.id));
    });

    return filtered;
}

function renderSubmissions() {
    const filtered = getFilteredGroups();
    const countEl = document.getElementById("sub-count");
    if (countEl) countEl.textContent = `${filtered.length} submission${filtered.length !== 1 ? "s" : ""}`;
    // The headline stat tiles are a stable dataset overview — always the global
    // totals, not the filtered subset (which silently shrank "Problems" to 1 etc.
    // as soon as any filter was applied). The count pill above already reflects
    // the active filter, so the tiles staying global is the least-surprising.
    renderStats(allGroups);

    const body = document.getElementById("sub-tbody");

    if (!filtered.length) {
        body.innerHTML = '<tr><td colspan="7" class="text-center padded">No submissions match the current filters.</td></tr>';
        return;
    }

    body.innerHTML = filtered
        .map((group) => {
            const problem = problemIndex.get(group.problem_id);
            const submitter = group.profile?.submitter || "-";
            const affiliation = group.profile?.affiliation || "-";
            const date = qFmtDate(qSubmissionDate(group));
            const instanceCount = (group.instances || []).length;
            // The package name already carries the date + author; surface just the
            // method here and link it to the package's detail page.
            return `
                <tr data-export-key="${qEsc(String(group.problem_id) + "::" + group.id)}">
                    <td><a class="rlink" href="${qSubmissionUrl(group.problem_id, group.id)}" title="${qEsc(group.id)}">${qEsc(qSubmissionMethod(group))}</a></td>
                    <td><a class="badge b-type" href="${qProblemUrl(group.problem_id)}">${qEsc(formatProblemLabel(problem))}</a></td>
                    <td>${qCatBadge(groupCategory(group))}</td>
                    <td>${qEsc(submitter)}</td>
                    <td>${qEsc(affiliation)}</td>
                    <td class="mono">${qEsc(date)}</td>
                    <td class="num">${instanceCount.toLocaleString()}</td>
                </tr>`;
        })
        .join("");

    // The <thead> persists across filter/search re-renders, so re-apply the
    // user's chosen column sort (and its header arrow) to the fresh rows.
    document.querySelector("#submissions-table table")?.reapplySort?.();
}

async function initSubmissionsPage() {
    qInitCommon();

    try {
        const [indexData, groups] = await Promise.all([qLoadIndex(), qLoadAllSubmissionGroups()]);
        problemIndex = new Map((indexData.problems || []).map((problem) => [problem.id, problem]));
        allGroups = [...groups];

        populateProblemFilter(indexData);
        renderStats(allGroups);
        renderSubmissions();
    } catch (error) {
        ["sub-stat-packages", "sub-stat-instances", "sub-stat-problems", "sub-stat-authors"].forEach((id) => {
            const el = document.getElementById(id);
            if (el) el.textContent = "—";
        });
        qShowError(document.getElementById("submissions-table"), error.message);
    }
}

function downloadSubmissionsCsv() {
    let groups = getFilteredGroups();
    // Honor the user's clicked-column sort so the CSV matches the visible table.
    const table = document.querySelector("#submissions-table table");
    if (table) groups = qOrderRowsByTable(table, groups, groups.map((g) => `${g.problem_id}::${g.id}`));
    const headers = [
        "Package", "Method", "Problem ID", "Problem", "Paradigm", "Submitter", "Affiliation", "Date",
        "Instances", "Files", "Workflow", "Algorithm", "Hardware", "Source files",
    ];
    const data = groups.map((group) => {
        const problem = problemIndex.get(group.problem_id);
        const profile = group.profile || {};
        const date = qSubmissionDate(group);
        return [
            group.id,
            qSubmissionMethod(group),
            String(group.problem_id).padStart(2, "0"),
            problem?.name || "",
            (qCATS[groupCategory(group)] || qCATS.classical).label,
            profile.submitter || "",
            profile.affiliation || "",
            date ? qFmtDate(date) : "",
            (group.instances || []).length,
            (group.source_files || []).length,
            profile.workflow || "",
            profile.algorithm_type || "",
            profile.hardware || "",
            (group.source_files || []).join("; "),
        ];
    });
    qDownloadCsv("qoblib_submissions.csv", headers, data);
}

window.renderSubmissions = renderSubmissions;
window.downloadSubmissionsCsv = downloadSubmissionsCsv;

document.getElementById("sub-search")?.addEventListener("input", renderSubmissions);
document.getElementById("sub-prob")?.addEventListener("change", renderSubmissions);
document.getElementById("sub-cat")?.addEventListener("change", renderSubmissions);
document.getElementById("sub-download")?.addEventListener("click", downloadSubmissionsCsv);

initSubmissionsPage();