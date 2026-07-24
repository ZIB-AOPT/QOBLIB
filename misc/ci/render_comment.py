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
"""Fill ``{{PLACEHOLDER}}`` tokens in a Markdown template and print the result.

Used by ``.github/workflows/validate-submission.yml`` to render the sticky PR
comment from ``comment_template.md`` — so the comment's wording lives in an
editable template instead of inline shell ``echo``s.

    render_comment.py TEMPLATE KEY=VALUE [KEY=VALUE ...]

Each ``KEY=VALUE`` replaces every ``{{KEY}}`` in the template. ``VALUE`` is used
literally, unless it starts with ``@``, in which case the replacement text is
read from the file at that path (handy for multi-line Markdown blocks). Missing
tokens are left untouched; unused keys are ignored. The result goes to stdout.
"""

from __future__ import annotations

import sys
from pathlib import Path


def render(template: str, values: dict[str, str]) -> str:
    for key, val in values.items():
        template = template.replace("{{" + key + "}}", val)
    return template


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: render_comment.py TEMPLATE KEY=VALUE ...", file=sys.stderr)
        return 2
    template = Path(argv[0]).read_text(encoding="utf-8")
    values: dict[str, str] = {}
    for pair in argv[1:]:
        if "=" not in pair:
            print(f"error: expected KEY=VALUE, got {pair!r}", file=sys.stderr)
            return 2
        key, val = pair.split("=", 1)
        if val.startswith("@"):
            val = Path(val[1:]).read_text(encoding="utf-8")
        values[key] = val
    sys.stdout.write(render(template, values))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
