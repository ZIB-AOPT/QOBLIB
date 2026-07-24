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
"""Instance discovery.

Turns each problem's ``instances/`` folder into instance source descriptors
(name, file, format, size, download URL). Most problems are a flat directory of
files; Steiner (04) and Portfolio (06) are directory *bundles*; Sports (05) is
scanned recursively; and Birkhoff (03) instances are unpacked from the
``qbench_*.json`` bundles together with their reference status and LP model.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from . import config
from .models import read_model_description
from .solutions import load_birkhoff_solution_map
from .text import canonical_name_from_filename, portfolio_base_name


def synthesize_instance_entry(problem_id: str, problem_dir: Path, name: str) -> dict:
    if problem_id == "06":
        base = portfolio_base_name(name)
        inst_dir = problem_dir / "instances" / ("po_" + re.sub(r"_b\d+$", "", base))
        if inst_dir.is_dir():
            size_bytes = sum(p.stat().st_size for p in inst_dir.rglob('*') if p.is_file())
            return {
                "name": name,
                "file": inst_dir.name,
                "format": "bundle",
                "size_bytes": size_bytes,
                "raw_url": config.LINKS.tree(config.rel_to_root(inst_dir)),
            }
    return {
        "name": name,
        "file": name,
        "format": "generated",
        "raw_url": config.LINKS.tree(problem_dir.name),
    }


def collect_generic_instance_sources(problem_id: str, problem_dir: Path) -> dict[str, dict]:
    instances_dir = problem_dir / "instances"
    sources: dict[str, dict] = {}
    if not instances_dir.is_dir():
        return sources

    if problem_id == "04":
        for inst_dir in sorted(p for p in instances_dir.iterdir() if p.is_dir()):
            size_bytes = sum(p.stat().st_size for p in inst_dir.rglob('*') if p.is_file())
            sources[inst_dir.name] = {
                "name": inst_dir.name,
                "file": inst_dir.name,
                "format": "bundle",
                "size_bytes": size_bytes,
                "raw_url": config.LINKS.tree(config.rel_to_root(inst_dir)),
            }
        return sources

    file_iter = instances_dir.rglob('*') if problem_id == "05" else instances_dir.iterdir()
    for inst_file in sorted(p for p in file_iter if p.is_file()):
        if inst_file.name.startswith('.') or inst_file.name.lower() == 'readme.md':
            continue
        name = canonical_name_from_filename(inst_file.name)
        sources[name] = {
            "name": name,
            "file": inst_file.name,
            "format": canonical_name_from_filename(inst_file.name).split('.')[-1],
            "size_bytes": inst_file.stat().st_size,
            "raw_url": config.LINKS.raw(config.rel_to_root(inst_file)),
        }
        # overwrite format with meaningful outer format
        suffixes = [s.lstrip('.') for s in inst_file.suffixes if s]
        suffixes = [s for s in suffixes if s not in {'xz', 'gz', 'bz2'}]
        sources[name]['format'] = suffixes[-1] if suffixes else 'unknown'
    return sources


def build_birkhoff_instances(problem_id: str, problem_dir: Path, csv_subs: dict) -> list[dict]:
    instances_dir = problem_dir / 'instances'
    solution_map = load_birkhoff_solution_map(problem_dir)
    instances: list[dict] = []
    for inst_file in sorted(instances_dir.glob('qbench_*.json')):
        try:
            data = json.loads(inst_file.read_text(encoding='utf-8'))
        except Exception:
            continue
        bundle = inst_file.stem
        m = re.match(r'qbench_(\d+)_(dense|sparse)', bundle)
        if not m or not isinstance(data, dict):
            continue
        n = int(m.group(1))
        dense = m.group(2) == 'dense'
        model_prefix = f"bh{'D' if dense else 'S'}-{n:02d}"
        model_dir = problem_dir / 'models' / 'integer_linear' / 'lp_files' / model_prefix
        for key, entry in sorted(data.items()):
            if not isinstance(entry, dict):
                continue
            name = entry.get('id')
            if not name:
                continue
            num = str(key).zfill(3)
            inst_entry = {
                'id': f'{problem_id}-{name}',
                'name': name,
                'file': inst_file.name,
                'format': 'json',
                'size_bytes': inst_file.stat().st_size,
                'raw_url': config.LINKS.raw(config.rel_to_root(inst_file)),
                'status': solution_map.get(name, {}).get('status', 'open'),
                'vars': entry.get('n'),
            }
            if 'value' in solution_map.get(name, {}):
                inst_entry['bkv'] = solution_map[name]['value']
            if 'source_file' in solution_map.get(name, {}):
                inst_entry['reference_solution_source_file'] = solution_map[name]['source_file']
            model_path = model_dir / f'{model_prefix}-{num}.lp.xz'
            if model_path.exists():
                description_md, description_url = read_model_description(model_path, problem_dir / 'models')
                model_entry = {
                    'name': model_path.name,
                    'format': 'lp.xz',
                    'kind': 'lp',
                    'approach': 'integer linear',
                    'size_bytes': model_path.stat().st_size,
                    'raw_url': config.LINKS.raw(config.rel_to_root(model_path)),
                }
                if description_md:
                    model_entry['description_md'] = description_md
                if description_url:
                    model_entry['description_url'] = description_url
                inst_entry['models'] = [model_entry]
            inst_subs = csv_subs.get(name, [])
            if inst_subs:
                inst_entry['submissions'] = inst_subs
            instances.append(inst_entry)
    instances.sort(key=lambda x: (x.get('vars') or 0, x.get('name', '')))
    return instances
