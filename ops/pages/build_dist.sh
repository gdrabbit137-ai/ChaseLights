#!/usr/bin/env bash
# ops/pages/build_dist.sh — whitelist publisher for Cloudflare Pages.
#
# The GitHub Pages site used to publish the WHOLE repo root: that is how
# https://chaselights.app/workers/api/src/index.js and /AGENTS.md became
# publicly downloadable. This script publishes only the runtime surface the
# static site actually fetches, and refuses to emit a dist that still carries
# any engineering path.
#
# The copy source is `git ls-files`, not the working tree: generated but
# uncommitted artefacts (weathergrid/ and weather_details/ carry ~2 GB of them
# locally) must never leak into a deployment.
#
# Usage:
#   bash ops/pages/build_dist.sh                # default: HTML/assets/indexes only (data lives on R2)
#   bash ops/pages/build_dist.sh --full         # also ship weathergrid/ + weather_details/ (rollback path)
#   bash ops/pages/build_dist.sh --light        # alias of the default (kept for old callers)
#   bash ops/pages/build_dist.sh --dry-run      # print the resolved file list, copy nothing
#   bash ops/pages/build_dist.sh --out DIR      # alternative output dir (default: <repo>/dist)
#
# Exit codes:
#   0  dist built (warnings allowed)
#   2  a forbidden engineering path leaked into dist
#   3  a single file reached the Cloudflare Pages 25 MiB per-file ceiling
#   4  dist exceeded the Cloudflare Pages 20,000-file deployment ceiling
#
# Environment overrides (tests only; production keeps the defaults):
#   DIST_WARN_BYTES  default 25165824  (24 MiB — warn)
#   DIST_MAX_BYTES   default 26214400  (25 MiB — Cloudflare hard ceiling)
#   DIST_MAX_FILES   default 20000     (Cloudflare hard ceiling)
set -euo pipefail
shopt -s nullglob

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
# Native tools (git on MSYS) do not translate /d/... paths — hand them the
# Windows form when cygpath is available, keep the POSIX form everywhere else.
ROOT_GIT="$(cygpath -m "$ROOT" 2>/dev/null || printf '%s' "$ROOT")"

OUT=""
FULL=0
DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --full) FULL=1; shift ;;
    --light) FULL=0; shift ;;
    --dry-run) DRY=1; shift ;;
    --out) OUT="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,40p' "$0"; exit 0 ;;
    *) echo "build_dist: unknown argument: $1" >&2; exit 64 ;;
  esac
done
OUT="${OUT:-$ROOT/dist}"

WARN_BYTES="${DIST_WARN_BYTES:-25165824}"
MAX_BYTES="${DIST_MAX_BYTES:-26214400}"
MAX_FILES="${DIST_MAX_FILES:-20000}"

# ---------------------------------------------------------------- whitelist
# Every entry here is a path the published site reads at runtime. Anything not
# named (directly or as a directory) never reaches dist.
SITE_FILES=(
  index.html
  404.html
  reminders.html
  weather-map.html
  genre-eval.html
  field-intake.html
  sources.html
)
SITE_DIRS=(
  assets
  locales
  data/v2/copy
  apps/web-v2/evaluations-details
)
SITE_JSON=(
  apps/web-v2/evaluations-latest.json
  apps/web-v2/catalog.v2.json
  apps/web-v2/browse-index.v2.json
  apps/web-v2/opportunity-contracts.json
)
# Subject-card bundle is fetched by name from assets/app.js (V2_SUBJECT_CARDS_FILE).
SITE_DATA_GLOB=(
  data/v2/evaluations/subject-cards-*.json
)
# Transitional: these move to R2 in Step ②. --light drops them.
HEAVY_DIRS=(
  weathergrid
  weather_details
)
# Never allowed to appear in dist, even if someone adds them to a dir above.
FORBIDDEN=(
  workers
  packages
  ops
  specs
  .github
  .ci
  .git
  data/v2/staging
  AGENTS.md
  SKILL.md
  README.md
  .hermes.md
)

if ! git -C "$ROOT_GIT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "build_dist: $ROOT is not a git work tree" >&2
  exit 64
fi

entries() {
  local f
  for f in "${SITE_FILES[@]}"; do
    [ -f "$ROOT/$f" ] && printf '%s\n' "$f"
  done
  for f in "$ROOT"/*_weather.json; do
    printf '%s\n' "${f#"$ROOT"/}"
  done
  for d in "${SITE_DIRS[@]}"; do
    [ -d "$ROOT/$d" ] && printf '%s/\n' "$d"
  done
  for f in "${SITE_JSON[@]}"; do
    [ -f "$ROOT/$f" ] && printf '%s\n' "$f"
  done
  for f in "$ROOT"/data/v2/evaluations/subject-cards-[0-9]*.json; do
    printf '%s\n' "${f#"$ROOT"/}"
  done
  if [ "$FULL" -eq 1 ]; then
    for d in "${HEAVY_DIRS[@]}"; do
      [ -d "$ROOT/$d" ] && printf '%s/\n' "$d"
    done
  fi
  printf '_headers\n'
}

# Tracked files only. A directory entry expands to its recursive tracked list.
resolve_files() {
  local e n
  while IFS= read -r e; do
    [ -z "$e" ] && continue
    if [ "$e" = "_headers" ]; then
      printf '%s\n' "_headers"
      continue
    fi
    n=$(git -C "$ROOT_GIT" ls-files -z -- "${e%/}" | tr -cd '\0' | wc -c | tr -d ' ')
    if [ "$n" -eq 0 ]; then
      echo "build_dist: WARN whitelist entry has no tracked files: $e" >&2
      continue
    fi
    git -C "$ROOT_GIT" ls-files -z -- "${e%/}" | tr '\0' '\n'
  done < <(entries)
}

if [ "$DRY" -eq 1 ]; then
  resolve_files | sort -u
  exit 0
fi

# ---------------------------------------------------------------- build
rm -rf "$OUT"
mkdir -p "$OUT"

resolve_files | sort -u > "$OUT/.files.tmp"
while IFS= read -r rel; do
  [ -z "$rel" ] && continue
  [ "$rel" = "_headers" ] && continue
  dst="$OUT/$rel"
  mkdir -p "$(dirname "$dst")"
  cp -p "$ROOT/$rel" "$dst"
done < "$OUT/.files.tmp"
rm -f "$OUT/.files.tmp"

cp -p "$SCRIPT_DIR/_headers" "$OUT/_headers"

# Belt and braces: nothing generated, no metadata, no caches.
find "$OUT" \( -name '__pycache__' -o -name '.git' -o -name '.DS_Store' -o -name '*.pyc' -o -name '.manifest.tmp' \) -prune -exec rm -rf {} + 2>/dev/null || true

# ---------------------------------------------------------------- leak gate
LEAKS=()
for p in "${FORBIDDEN[@]}"; do
  [ -e "$OUT/$p" ] && LEAKS+=("$p")
done
if [ "${#LEAKS[@]}" -gt 0 ]; then
  echo "build_dist: FORBIDDEN path(s) present in dist: ${LEAKS[*]}" >&2
  exit 2
fi

# ---------------------------------------------------------------- size gate
N_FILES=0
TOTAL=0
WARNED=0
OVERSIZE=""
while IFS= read -r -d '' f; do
  s=$(wc -c < "$f" | tr -d ' ')
  N_FILES=$((N_FILES + 1))
  TOTAL=$((TOTAL + s))
  if [ "$s" -ge "$MAX_BYTES" ]; then
    OVERSIZE="$f"
  elif [ "$s" -gt "$WARN_BYTES" ]; then
    WARNED=$((WARNED + 1))
    printf 'build_dist: WARN  %.1f MiB  %s (near the 25 MiB Cloudflare ceiling)\n' \
      "$(awk -v b="$s" 'BEGIN{printf "%.1f", b/1048576}')" "${f#"$OUT"/}"
  fi
done < <(find "$OUT" -type f -print0)

if [ -n "$OVERSIZE" ]; then
  echo "build_dist: FAIL single file over the 25 MiB Cloudflare Pages ceiling: ${OVERSIZE#"$OUT"/}" >&2
  exit 3
fi
if [ "$N_FILES" -gt "$MAX_FILES" ]; then
  echo "build_dist: FAIL $N_FILES files exceeds the Cloudflare Pages ${MAX_FILES}-file ceiling" >&2
  exit 4
fi

printf 'build_dist: OK  files=%d size=%.1f MiB (%.2f GiB) warn_near_limit=%d mode=%s\n' \
  "$N_FILES" \
  "$(awk -v b="$TOTAL" 'BEGIN{printf "%.1f", b/1048576}')" \
  "$(awk -v b="$TOTAL" 'BEGIN{printf "%.2f", b/1073741824}')" \
  "$WARNED" "$([ "$FULL" -eq 1 ] && echo full || echo light)"
