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
"""Downloadable model-artifact scanning.

Collects ``models/**/*.lp.xz`` and ``*.qs.xz`` files keyed by instance stem,
attaching the modelling approach (derived from the folder layout) and an
optional README description, so the instance pages can offer model downloads.
"""

from __future__ import annotations

from pathlib import Path

from . import config
from .text import normalize_portfolio_lambda


def read_model_description(path: Path, models_dir: Path) -> tuple[str, str] | tuple[None, None]:
    candidates = [path.parent, *path.parents]
    seen: set[Path] = set()
    for directory in candidates:
        if directory in seen or directory == directory.parent:
            continue
        seen.add(directory)
        try:
            directory.relative_to(models_dir)
        except ValueError:
            continue
        for name in ("README.md", "readme.md", "README.txt"):
            readme = directory / name
            if not readme.is_file():
                continue
            text = readme.read_text(encoding="utf-8", errors="replace").strip()
            if not text:
                continue
            first_heading = next((line.strip() for line in text.splitlines() if line.strip()), "")
            if first_heading.lower() == "# instance metrics":
                continue
            url = config.LINKS.blob(config.rel_to_root(readme))
            return text, url
    return None, None


def scan_model_files(problem_dir: Path) -> dict[str, list[dict]]:
    """Return downloadable model artifacts keyed by instance stem."""
    models_dir = problem_dir / "models"
    result: dict[str, list[dict]] = {}
    if not models_dir.is_dir():
        return result

    for path in sorted(models_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name.endswith(".lp.xz"):
            fmt = "lp.xz"
            inst = path.name[:-6]
        elif path.name.endswith(".qs.xz"):
            fmt = "qs.xz"
            inst = path.name[:-6]
        else:
            continue

        inst = normalize_portfolio_lambda(inst.removeprefix("bqp_").removeprefix("uqo_"))

        rel = path.relative_to(models_dir)
        approach = rel.parts[0].replace("_", " ") if len(rel.parts) > 1 else "model"
        description_md, description_url = read_model_description(path, models_dir)
        entry = {
            "name": path.name,
            "format": fmt,
            "kind": "lp" if fmt.startswith("lp") else "qs",
            "approach": approach,
            "size_bytes": path.stat().st_size,
            "raw_url": config.LINKS.raw(config.rel_to_root(path)),
        }
        if description_md:
            entry["description_md"] = description_md
        if description_url:
            entry["description_url"] = description_url
        result.setdefault(inst, []).append(entry)

    for entries in result.values():
        entries.sort(key=lambda entry: (entry["kind"], entry["approach"], entry["name"]))
    return result
