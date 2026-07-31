"use strict";

const {
    esc: qEsc,
    loadIndex: qLoadIndex,
    loadAllSubmissionGroups: qLoadAllSubmissionGroups,
    problemCard: qProblemCard,
    animateCount: qAnimateCount,
    showError: qShowError,
    initCommon: qInitCommon,
    enhanceFigures: qEnhanceFigures,
    attachFigureExpand: qAttachFigureExpand,
} = window.QOBLIB;

// The whole card's content (main scatter + legend + inset sub-plots + caption),
// wrapped for the lightbox so an expanded landscape keeps everything the card
// shows — not just the first SVG.
function landscapeFigureHtml(card) {
    const inner = Array.from(card.children)
        .filter((c) => !c.classList.contains("fig-expand"))
        .map((c) => c.outerHTML)
        .join("");
    return inner ? `<div class="landscape-expanded">${inner}</div>` : "";
}

// Inject the pre-rendered complexity-landscape scatter SVGs (built once by
// misc/ci/site_builder/landscape.py → data/landscape.json) into the two plot cards.
async function renderLandscape() {
    const targets = [
        ["landscape-mip", "mip"],
        ["landscape-qubo", "qubo"],
    ].map(([id, key]) => [document.getElementById(id), key]);
    if (!targets.some(([el]) => el)) return;

    const fill = (el, html) => {
        if (!el) return;
        el.innerHTML = html || '<div class="empty-state" style="padding:2rem">No data available.</div>';
    };
    try {
        const res = await fetch("data/landscape.json");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        targets.forEach(([el, key]) => fill(el, data[key]));
        // Expand to the full card (main scatter + legend + inset sub-plots +
        // caption), not just the first SVG, so nothing is lost when enlarged.
        targets.forEach(([el]) => {
            if (el && el.querySelector("svg")) {
                qAttachFigureExpand(el, { html: () => landscapeFigureHtml(el) });
            }
        });
        qEnhanceFigures(document); // any other figures on the page
    } catch (error) {
        targets.forEach(([el]) => {
            if (el) el.innerHTML = '<div class="empty-state" style="padding:2rem">Could not load the landscape plot.</div>';
        });
    }
}

// Collect unique affiliations + per-org instance counts from submission_groups.json.
// Builds two counter-scrolling tracks (row A → left, row B ← right) where each
// chip shows the org name and how many instances they have contributed results for.
// A count-up number above shows the total number of contributing organizations.
async function renderAffiliations() {
    const trackA = document.getElementById("affil-track-a");
    const trackB = document.getElementById("affil-track-b");
    if (!trackA || !trackB) return;

    const section = trackA.closest("section");

    try {
        const allGroups = await qLoadAllSubmissionGroups();

        // Accumulate instance counts per affiliation.
        // CSV affiliation fields are comma-separated when multi-author; we split
        // on commas but then re-join any fragment that looks like a broken
        // parenthesised name (e.g. "Foo (Bar" + "Baz)" → "Foo (Bar, Baz)").
        const counts = new Map(); // affiliation → instance count
        allGroups.forEach((group) => {
            const raw = (group.profile?.affiliation || "").trim();
            if (!raw || raw === "N/A") return;
            const nInst = (group.instances || []).length;

            // The affiliation field is comma-joined across multiple authors, so we
            // split on commas — but a single org name can itself contain a comma
            // ("Qunova Computing, Inc."). Split, then heal two cases that a naive
            // split breaks apart:
            //   1. broken parentheses — a fragment with an unclosed "(" is merged
            //      with following fragments until the paren closes;
            //   2. a trailing corporate suffix (Inc., Ltd, LLC, GmbH, …) that got
            //      severed from its org name is re-joined to the previous entry.
            const CORP_SUFFIX = /^(?:inc|incorporated|ltd|limited|l\.?l\.?c|l\.?l\.?p|co|corp|corporation|company|gmbh|ag|kg|s\.?a|s\.?à\.?r\.?l|sarl|b\.?v|n\.?v|plc|pty|pte|srl|s\.?r\.?l|s\.?p\.?a|oy|ab|as)\.?$/i;
            const parts = raw.split(",").map((s) => s.trim()).filter(Boolean);
            const healed = [];
            let carry = "";
            for (const p of parts) {
                const combined = carry ? `${carry}, ${p}` : p;
                const opens = (combined.match(/\(/g) || []).length;
                const closes = (combined.match(/\)/g) || []).length;
                if (opens > closes) {
                    carry = combined; // unmatched open paren — keep accumulating
                } else if (CORP_SUFFIX.test(combined) && healed.length) {
                    // A standalone corporate suffix belongs to the preceding org.
                    healed[healed.length - 1] += `, ${combined}`;
                    carry = "";
                } else {
                    healed.push(combined);
                    carry = "";
                }
            }
            if (carry) healed.push(carry); // flush any remaining fragment

            healed.forEach((a) => {
                if (a && a !== "N/A") {
                    counts.set(a, (counts.get(a) || 0) + nInst);
                }
            });
        });

        if (!counts.size) {
            if (section) section.remove();
            return;
        }

        // Sort alphabetically for a consistent, non-hierarchical display.
        const orgs = Array.from(counts.entries()).sort((a, b) =>
            a[0].localeCompare(b[0], undefined, { sensitivity: "base" }),
        );

        // Animate the count number.
        const countEl = document.getElementById("affil-count");
        if (countEl) qAnimateCount("affil-count", orgs.length);

        // Build a stat card: name + instance count below.
        const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
        const card = (name, n, dup = false) =>
            `<span class="affil-chip${dup ? " affil-chip-dup" : ""}">` +
            `<span class="affil-chip-name">${esc(name)}</span>` +
            `<span class="affil-chip-stat">${n} instance${n === 1 ? "" : "s"}</span>` +
            `</span>`;

        // Split orgs across two rows for visual variety.
        // Odd-indexed go on row B so neither row is an exact subset of the other.
        const rowA = orgs.filter((_, i) => i % 2 === 0);
        const rowB = orgs.filter((_, i) => i % 2 === 1);

        // Each track needs two copies of its set for the seamless loop.
        const fill = (track, row, reverse) => {
            const html = (dup) => row.map(([n, c]) => card(n, c, dup)).join("");
            track.innerHTML = html(false) + html(true);
            // Speed proportional to content width (~70 px/s, clamped 18–70 s).
            const estWidth = row.length * 190;
            const duration = Math.min(70, Math.max(18, estWidth / 70));
            track.style.setProperty("--affil-duration", `${duration}s`);
            track.style.setProperty("--affil-shift", "-50%");
            if (reverse) track.classList.add("affil-track-reverse");
            track.classList.add("running");
        };

        fill(trackA, rowA, false);
        fill(trackB, rowB, true);
    } catch {
        if (section) section.remove();
    }
}

async function initHomePage() {
    qInitCommon();
    renderLandscape();
    renderAffiliations();
    try {
        const idx = await qLoadIndex();
        qAnimateCount("s-inst", idx.total_instances || 0);
        qAnimateCount("s-subs", idx.total_submissions || 0);
        qAnimateCount(
            "s-solved",
            (idx.problems || []).reduce((sum, p) => sum + (p.solved_count || 0), 0),
        );

        const grid = document.getElementById("pgrid");
        grid.innerHTML = (idx.problems || []).map(qProblemCard).join("");
    } catch (error) {
        // Clear the perpetual "…" loading spinner on the stat numbers so a failed
        // load reads as an error state rather than a hang.
        ["s-inst", "s-subs", "s-solved"].forEach((id) => {
            const el = document.getElementById(id);
            if (el) {
                el.classList.remove("loading-val");
                el.textContent = "—";
            }
        });
        qShowError(document.getElementById("pgrid"), error.message);
    }
}

initHomePage();
