"use strict";

const {
    esc: qEsc,
    loadIndex: qLoadIndex,
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

async function initHomePage() {
    qInitCommon();
    renderLandscape();
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
