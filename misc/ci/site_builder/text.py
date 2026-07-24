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


# --- dates -------------------------------------------------------------------

def parse_date_str(s: str) -> str:
    """Parse date strings like '22. Dec. 2024' or '2024-12-22' to YYYY-MM-DD."""
    if not s:
        return ""
    s = s.strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}", s):
        return s[:10]
    months = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04",
        "may": "05", "jun": "06", "jul": "07", "aug": "08",
        "sep": "09", "oct": "10", "nov": "11", "dec": "12",
    }
    m = re.match(r"(\d{1,2})[.\s]+(\w{3,})[.\s]+(\d{4})", s, re.IGNORECASE)
    if m:
        day, mon, year = m.group(1), m.group(2)[:3].lower(), m.group(3)
        mon_num = months.get(mon)
        if mon_num:
            return f"{year}-{mon_num}-{int(day):02d}"
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
    name = (name
            .replace("_l0.000001", "_l1e-06")
            .replace("_l0.00001", "_l1e-05")
            .replace("_l0.00005", "_l5e-05"))
    if name.endswith("_l0"):
        name = f"{name}.0"
    return name


def portfolio_base_name(instance_name: str) -> str:
    name = normalize_portfolio_lambda(instance_name)
    if name.startswith("po_"):
        name = name[3:]
    name = re.sub(r"_l(?:0(?:\.\d+)?|\d+(?:e-\d+)?)$", "", name)
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
    Best-effort parser. Looks for numeric tokens that could be variable counts.
    E.g. ms_05_100_003 -> tries [5, 100, 3] and picks the largest as n_vars.
    This is a heuristic — proper parsing per format is preferred.
    """
    tokens = re.split(r"[_\-]", stem)
    nums = [int(t) for t in tokens if t.isdigit()]
    result: dict = {}
    if nums:
        result["vars"] = max(nums)
        if len(nums) >= 3:
            result["n_constraints"] = nums[1] if nums[0] < 20 else None
        result["index"] = nums[-1]
    return result


def parse_ms_filename(stem: str) -> dict:
    # ms_<m>_<n>_<idx>  e.g. ms_05_100_003
    m = re.match(r"ms_(\d+)_(\d+)_(\d+)", stem)
    if m:
        return {"n_constraints": int(m.group(1)), "vars": int(m.group(2)), "index": int(m.group(3))}
    return parse_filename_generic(stem)


def parse_labs_filename(stem: str) -> dict:
    # labs_<n>_<idx> or labs_n<n>_<idx>
    m = re.match(r"labs[_\-]n?(\d+)[_\-](\d+)", stem, re.IGNORECASE)
    if m:
        return {"vars": int(m.group(1)), "index": int(m.group(2))}
    return parse_filename_generic(stem)


FILENAME_PARSERS = {
    "01": parse_ms_filename,
    "02": parse_labs_filename,
}


def parse_instance_filename(problem_id: str, stem: str) -> dict:
    parser = FILENAME_PARSERS.get(problem_id, parse_filename_generic)
    return parser(stem)
