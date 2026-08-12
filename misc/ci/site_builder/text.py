# This file is part of QOBLIB - Quantum Optimization Benchmarking Library
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Small parsing / normalisation helpers shared across the builder.

Date parsing, numeric coercion, instance-name canonicalisation, problem-README
section extraction, and the per-problem filename parsers all live here so the
collection modules stay focused on structure rather than string wrangling.
"""

from __future__ import annotations

import re


# --- numeric coercion --------------------------------------------------------

def num_or_none(value) -> float | None:
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def to_int(value) -> int | None:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def format_portfolio_lambda(value) -> str:
    """Canonical *display* form for a risk-aversion λ, uniform everywhere.

    The λ values reach us in mixed spellings (``0.0001``, ``1e-06``, ``5e-05``,
    ``0.01``); a bare decimal point parses badly and reads inconsistently next to
    the scientific ones. Render every non-zero λ in single-mantissa scientific
    notation with a 2-digit exponent (``1e-04``, ``5e-05``, ``1e-02``) and zero as
    a plain ``0``. Returns the input unchanged if it isn't numeric (e.g. ``n/a``)."""
    num = num_or_none(value)
    if num is None:
        return str(value)
    if num == 0:
        return "0"
    return f"{num:.0e}"


# --- dates -------------------------------------------------------------------

_DATE_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _expand_two_digit_year(year: int) -> int:
    """Expand a 2-digit year to 4 digits. Submissions run 2024→, so a bare ``25``
    means 2025; map every 2-digit value into the 2000s (``00``–``99`` → 2000–2099),
    which covers the benchmark's lifetime without guessing a pivot."""
    return 2000 + year if year < 100 else year


def parse_date_str(s: str) -> str:
    """Normalise a free-text submission date to the canonical ``YYYY-MM-DD``.

    Authors write the ``Date`` column in assorted shapes; the checker only accepts
    ISO on new submissions, but existing data carries several forms. This mirrors
    the frontend ``parseDate`` (website/assets/common.js) so the pre-rendered HTML
    and the client-hydrated view agree. Recognised inputs:

      * ``2024-12-22`` / ``2024-12-22 09:32:08`` — ISO, optional time (year-first,
        also ``/`` or ``.`` separators);
      * ``20241206`` — compact YYYYMMDD (the submission-dir prefix);
      * ``22. Dec. 2024`` / ``22 Dec 2024`` — day-first with a month name;
      * ``Dec 22, 2024`` / ``August 5th, 2026`` / ``Nov. 17, 2025`` — month-name
        first, tolerating an ordinal suffix (``5th``);
      * ``09/03/2025`` / ``15.07.25`` — day-first numeric (European DD.MM.YY[YY]).

    Two-digit years expand into the 2000s. An unrecognised string is returned
    stripped but otherwise unchanged, so a novel format degrades to the author's
    original text rather than an empty cell."""
    if not s:
        return ""
    s = s.strip()
    if not s:
        return ""

    y = mo = d = None

    m = re.match(r"^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", s)
    if m:
        # Year-first: ISO 8601, YYYY-MM-DD, YYYY/MM/DD (any trailing time ignored).
        y, mo, d = m.group(1), m.group(2), m.group(3)
    elif re.match(r"^\d{8}$", s):
        # Compact YYYYMMDD.
        y, mo, d = s[:4], s[4:6], s[6:8]
    elif (m := re.match(r"^(\d{1,2})[.\s]+([A-Za-z]{3,})\.?[,\s]+(\d{2,4})$", s)):
        # Day-first with a month name: "22 Dec 2024", "22. Dec. 2024".
        d, mo, y = m.group(1), _DATE_MONTHS.get(m.group(2)[:3].lower()), m.group(3)
    elif (m := re.match(r"^([A-Za-z]{3,})\.?\s+(\d{1,2})(?:st|nd|rd|th)?[,.\s]+(\d{2,4})$", s)):
        # Month name first, optional ordinal suffix: "Dec 22, 2024", "August 5th, 2026".
        mo, d, y = _DATE_MONTHS.get(m.group(1)[:3].lower()), m.group(2), m.group(3)
    elif (m := re.match(r"^(\d{1,2})[-/.](\d{1,2})[-/.](\d{2,4})$", s)):
        # Day-first numeric, the common European source form: DD.MM.YY[YY].
        d, mo, y = m.group(1), m.group(2), m.group(3)

    if y is not None and mo is not None and d is not None:
        try:
            yi, moi, di = _expand_two_digit_year(int(y)), int(mo), int(d)
        except (TypeError, ValueError):
            return s
        if 1 <= moi <= 12 and 1 <= di <= 31:
            return f"{yi:04d}-{moi:02d}-{di:02d}"
    return s


# --- instance-name canonicalisation -----------------------------------------

def canonical_name_from_filename(name: str) -> str:
    parts = name.split(".")
    while parts and parts[-1] in {"xz", "gz", "bz2"}:
        parts.pop()
    if len(parts) > 1:
        parts.pop()
    return ".".join(parts)


def normalize_portfolio_lambda(name: str) -> str:
    """Canonical instance key for a portfolio (06) risk-aversion ``_l<λ>`` suffix.

    The same logical instance reaches the builder under several λ spellings: the
    manifest grid feeds decimals (``_l0.000001``, ``_l0.01``); the regenerated
    solution / model / submission filenames use a compact scientific tag
    (``_l1e-6``, ``_l0``, ``_l5e-5``); older data used yet other forms. Rewrite the
    suffix to one uniform spelling so all four producers key identically — zero →
    ``_l0``, every non-zero λ → single-mantissa scientific with a two-digit
    exponent (``_l1e-06``, ``_l5e-05``, ``_l1e-02``). Matches the display form
    produced by :func:`format_portfolio_lambda`.

    The rewrite is deliberately conservative: it fires only on a portfolio λ token
    (``0`` or a fractional / scientific value), never on a bare-integer suffix like
    Steiner's ``_l4`` level marker, so calling it on any problem's stems is safe.
    Names without a portfolio ``_l`` suffix are returned unchanged.
    """
    m = re.search(r"_l([0-9][0-9.eE+-]*)$", name)
    if not m:
        return name
    tok = m.group(1)
    if tok != "0" and not any(c in tok for c in ".eE"):
        return name  # bare integer (e.g. Steiner ``_l4``) — not a portfolio λ
    num = num_or_none(tok)
    if num is None:
        return name
    tag = "0" if num == 0 else f"{num:.0e}"
    return f"{name[:m.start()]}_l{tag}"


def portfolio_base_name(instance_name: str) -> str:
    name = normalize_portfolio_lambda(instance_name)
    if name.startswith("po_"):
        name = name[3:]
    # Strip the canonical λ suffix produced by normalize_portfolio_lambda
    # (``_l0`` or ``_l<m>e-<nn>``).
    name = re.sub(r"_l(?:0|\d+e-\d+)$", "", name)
    return name


# --- problem README sections -------------------------------------------------

def extract_readme_section(readme_text: str, heading: str) -> str:
    pattern = re.compile(rf'^##\s+{re.escape(heading)}\s*$', re.MULTILINE)
    match = pattern.search(readme_text)
    if not match:
        return ''
    rest = readme_text[match.end():]
    next_heading = re.search(r'^##\s+', rest, re.MULTILINE)
    section = rest[:next_heading.start()] if next_heading else rest
    return section.strip()


def extract_problem_intro(readme_text: str) -> str:
    parts: list[str] = []
    overview = extract_readme_section(readme_text, 'Overview')
    problem_description = extract_readme_section(readme_text, 'Problem Description')
    if overview:
        parts.append('## Overview\n\n' + overview)
    if problem_description:
        parts.append('## Problem Description\n\n' + problem_description)
    return '\n\n'.join(parts).strip()


# ---------------------------------------------------------------------------
# Filename parsers — return whatever metadata can be extracted from the stem.
# Add parsers here as new problem classes adopt naming conventions.
# ---------------------------------------------------------------------------

def parse_filename_generic(stem: str) -> dict:
    """
    Best-effort parser for the trailing instance *index* only.

    Historically this also guessed a variable count from the largest numeric
    token in the stem (``ms_05_100_003 -> 100``). That heuristic was wrong for
    most problem classes — the "largest number" is a coefficient range (01), a
    difficulty label (05), a λ token (06) or the trailing index itself (09) far
    more often than it is the variable count. The authoritative variable count
    comes from the generated LP ``metrics.csv`` (or the ``.dat`` header for 01),
    attached in :mod:`.metrics`; a wrong badge is worse than no badge, so this
    parser no longer emits ``vars`` or a guessed ``n_constraints`` at all.
    """
    tokens = re.split(r"[_\-]", stem)
    nums = [int(t) for t in tokens if t.isdigit()]
    result: dict = {}
    if nums:
        result["index"] = nums[-1]
    return result


def parse_ms_filename(stem: str) -> dict:
    # ms_<m>_<coeff_range>_<idx>  e.g. ms_05_100_003. The 2nd token is the
    # coefficient range, NOT the variable count (see metrics.read_marketsplit_dims,
    # which reads the true n from the .dat header). Only the constraint count (m)
    # and index are reliably encoded here.
    m = re.match(r"ms_(\d+)_(\d+)_(\d+)", stem)
    if m:
        return {"n_constraints": int(m.group(1)), "index": int(m.group(3))}
    return parse_filename_generic(stem)


def parse_labs_filename(stem: str) -> dict:
    # labs_<n>_<idx> or labs_n<n>_<idx>. The LABS sequence length N is the model's
    # variable count, but it is surfaced as the "length" metric (and the
    # authoritative vars) in :mod:`.metrics`; keep only the index here.
    m = re.match(r"labs[_\-]n?(\d+)[_\-](\d+)", stem, re.IGNORECASE)
    if m:
        return {"index": int(m.group(2))}
    return parse_filename_generic(stem)


FILENAME_PARSERS = {
    "01": parse_ms_filename,
    "02": parse_labs_filename,
}


def parse_instance_filename(problem_id: str, stem: str) -> dict:
    parser = FILENAME_PARSERS.get(problem_id, parse_filename_generic)
    return parser(stem)
