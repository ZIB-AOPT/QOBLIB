#!/usr/bin/env bash
# Reproduce the GitHub Actions workflows locally (no Docker required).
#
# Each workflow is now a thin wrapper around `uv run --project misc qoblib-*`,
# so this runs the same commands from the repo root.
#
# Usage:
#   misc/ci/local-ci.sh [tests|pages|bkv|validate|all]   # default: all
#
# Env overrides:
#   BASE, HEAD    git refs the `validate` diff runs against
#                 (default: BASE=merge-base(origin/main,HEAD), HEAD=HEAD)
#   CHECK_ARGS    extra args to qoblib-check-submission
#                 (default: --no-check → fast structural pass, skips the Rust
#                  per-problem solution checkers; set CHECK_ARGS="" for the full
#                  check, which requires cargo + each problem's check/ project)
#
# For full container-level fidelity instead, install Docker + act and run:
#   act pull_request -W .github/workflows/pages.yml
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"

UV=(uv run --project misc)
rc=0
step() { printf '\n\033[1;34m▶ %s\033[0m\n' "$*"; }

run_tests() {   # .github/workflows/tests.yml
  step "tests: unit tests"
  "${UV[@]}" python -m unittest discover -s tests || rc=1
}

run_pages() {   # .github/workflows/pages.yml (main only — tests, then build + deploy)
  step "pages: unit tests"
  "${UV[@]}" python -m unittest discover -s tests || rc=1
  step "pages: build site → _site/ (gitignored)"
  "${UV[@]}" qoblib-build-site --out _site \
    --repo-url "$(git remote get-url origin 2>/dev/null || echo https://github.com/ZIB-AOPT/QOBLIB)" \
    --ref "$(git rev-parse HEAD)" || rc=1
}

run_bkv() {     # .github/workflows/update-bkv.yml (non-destructive: --check writes nothing)
  step "update-bkv: dry-run (--check; exits non-zero if tables are stale)"
  "${UV[@]}" qoblib-update-bkv --check || rc=1
}

run_validate() {  # .github/workflows/validate-submission.yml
  local base head
  base="${BASE:-$(git merge-base origin/main HEAD 2>/dev/null || git rev-parse HEAD~1)}"
  head="${HEAD:-$(git rev-parse HEAD)}"
  step "validate: changed submission roots in ${base:0:8}..${head:0:8}"
  # Portable read into an array (macOS ships bash 3.2, which lacks `mapfile`).
  ROOTS=()
  while IFS= read -r line; do [ -n "$line" ] && ROOTS+=("$line"); done < <(
    git diff --name-only "$base" "$head" \
      | grep -E '^[0-9]{2}-[^/]+/submissions/[^/]+/' \
      | sed -E 's#^([0-9]{2}-[^/]+/submissions/[^/]+)/.*#\1#' | sort -u
  )
  if [ "${#ROOTS[@]}" -eq 0 ]; then
    echo "  (none — nothing to validate; try: CHECK_ARGS=--no-check misc/ci/local-ci.sh validate)"
  else
    # shellcheck disable=SC2206
    local extra=(${CHECK_ARGS---no-check})
    for root in "${ROOTS[@]}"; do
      step "validate: $root"
      "${UV[@]}" qoblib-check-submission "$root" "${extra[@]}" || rc=1
    done
  fi
  step "validate: best-known-value check (informational)"
  "${UV[@]}" qoblib-check-bkv --warn-only --base "$base" --head "$head" || true
}

case "${1:-all}" in
  tests)    run_tests ;;
  pages)    run_pages ;;
  bkv)      run_bkv ;;
  validate) run_validate ;;
  all)      run_tests; run_pages; run_bkv; run_validate ;;
  *) echo "usage: $0 [tests|pages|bkv|validate|all]" >&2; exit 2 ;;
esac

if [ "$rc" -eq 0 ]; then printf '\n\033[1;32m✓ local CI passed\033[0m\n'; else printf '\n\033[1;31m✗ local CI had failures\033[0m\n'; fi
exit "$rc"
