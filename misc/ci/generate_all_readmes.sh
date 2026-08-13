#!/usr/bin/env bash
#
# Run check_submission.py with --generate-readme on every submission directory
# in the repository.
#
# It discovers each directory that directly contains instance subdirectories
# holding a "<instance>_summary.csv" (the parent of every leaf summary dir) and
# runs the checker on it. This handles both the flat layout
#   <problem>/submissions/<submission>/<instance>/<instance>_summary.csv
# and the nested portfolio layout
#   <problem>/submissions/<submission>/<group>/<instance>/<instance>_summary.csv
#
# Usage:
#   misc/ci/generate_all_readmes.sh                 # generate READMEs, skip solution checks
#   misc/ci/generate_all_readmes.sh --fail-on-checker --strict-problem-match
#                                                # pass extra args straight to the checker
#
# Any extra arguments are forwarded to check_submission.py. When none are given
# it defaults to --no-check (READMEs only, no Rust solution checkers built/run).
# Override the interpreter with PYTHON=... if needed.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CHECKER="$SCRIPT_DIR/check_submission.py"
PY="${PYTHON:-python3}"

if [ ! -f "$CHECKER" ]; then
  echo "ERROR: checker not found at $CHECKER" >&2
  exit 2
fi

# Extra args forwarded to the checker (besides --generate-readme).
EXTRA_ARGS=("$@")
if [ "${#EXTRA_ARGS[@]}" -eq 0 ]; then
  EXTRA_ARGS=(--no-check)
fi

# Unique parents of every "*_summary.csv" directory.
ROOTS="$(find "$REPO_ROOT" -name '*_summary.csv' -exec dirname {} \; \
         | xargs -n1 dirname \
         | sort -u)"

if [ -z "$ROOTS" ]; then
  echo "No *_summary.csv files found under $REPO_ROOT" >&2
  exit 2
fi

count=0
fail=0
while IFS= read -r root; do
  [ -z "$root" ] && continue
  count=$((count + 1))
  echo "=== [$count] ${root#"$REPO_ROOT"/} ==="
  if ! "$PY" "$CHECKER" "$root" --generate-readme "${EXTRA_ARGS[@]}"; then
    fail=1
  fi
done <<EOF
$ROOTS
EOF

echo
echo "Processed $count submission root directories."
if [ "$fail" -ne 0 ]; then
  echo "One or more directories reported validation failures (READMEs were still generated)."
fi
exit "$fail"
