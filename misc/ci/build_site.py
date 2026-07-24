#!/usr/bin/env python3
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
"""Build the static GitHub Pages site for QOBLIB.

This is a thin command-line wrapper around the :mod:`site_builder` package. It
copies the static frontend from ``website/`` into the output directory and
generates the JSON data the frontend consumes. No HTML is generated here — all
markup lives in ``website/``.

    python misc/build_site.py --out _site --repo-url <url> --ref <ref>

The ``--repo-url`` / ``--ref`` options control the GitHub download links baked
into the data (defaulting to the canonical repo on ``main``), so a pull-request
preview build can point its links at the proposed changes.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Make the sibling ``site_builder`` package importable when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from site_builder import config  # noqa: E402
from site_builder.build import build_site  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the QOBLIB static site.")
    parser.add_argument(
        "--out",
        default="_site",
        type=Path,
        help="Output directory for the assembled site (default: _site).",
    )
    parser.add_argument(
        "--root",
        default=".",
        type=Path,
        help="Repository root to scan (default: current directory).",
    )
    parser.add_argument(
        "--repo-url",
        default=os.environ.get("SITE_REPO_URL", config.DEFAULT_REPO_URL),
        help="GitHub repository URL used for download links.",
    )
    parser.add_argument(
        "--ref",
        default=os.environ.get("SITE_REF", config.DEFAULT_REF),
        help="Git ref/sha used for download links.",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("SITE_BASE_URL", config.DEFAULT_BASE_URL),
        help="Deployed origin for canonical/Open Graph URLs and the pretty "
        "per-problem <base> path (default: %(default)s).",
    )
    parser.add_argument(
        "--no-static",
        action="store_true",
        help="Only generate data (skip copying the static frontend).",
    )
    args = parser.parse_args(argv)

    summary = build_site(
        out=args.out,
        root=args.root,
        repo_url=args.repo_url,
        ref=args.ref,
        copy_static=not args.no_static,
        base_url=args.base_url,
    )
    print(
        f"\nBuilt site at {args.out} "
        f"({summary['problems']} problems, {summary['instances']} instances, "
        f"{summary['submissions']} submissions)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
