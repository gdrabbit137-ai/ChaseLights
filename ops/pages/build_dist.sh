#!/usr/bin/env bash
# ops/pages/build_dist.sh — whitelist publisher for Cloudflare Pages.
#
# The GitHub Pages site used to publish the WHOLE repo root: that is how
# https://chaselights.app/workers/api/src/index.js and /AGENTS.md became
# publicly downloadable. This script publishes only the runtime surface the
# static site actually fetches, and refuses to emit a dist that still carries
# any engineering path.
#
# Usage:
#   bash ops/pages/build_dist.sh                # full site (incl. weathergrid/ + weather_details/)
#   bash ops/pages/build_dist.sh --light        # skip the heavy data dirs (fast local/CI contract runs)
#   bash ops/pages/build_dist.sh --dry-run      # print the resolved manifest, copy nothing
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

OUT=""
LIGHT=0
DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --light) LIGHT=1; shift ;;
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
  reminders.html
  weather-map.html
  genre-eval.html
  field-intake.html
  sources.html
  CNAME
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

manifest() {
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
  if [ "$LIGHT" -eq 0 ]; then
    for d in "${HEAVY_DIRS[@]}"; do
      [ -d "$ROOT/$d" ] && printf '%s/\n' "$d"
    done
  fi
  printf '_headers\n'
}

if [ "$DRY" -eq 1 ]; then
  manifest | sort
  exit 0
fi

# ---------------------------------------------------------------- build
rm -rf "$OUT"
mkdir -p "$OUT"

copy_entry() {
  local rel="$1"
  local src="$ROOT/${rel%/}"
  local dst="$OUT/${rel%/}"
  if [ -d "$src" ]; then
    mkdir -p "$dst"
    cp -R "$src/." "$dst/"
  elif [ -f "$src" ]; then
    mkdir -p "$(dirname "$dst")"
    cp -p "$src" "$dst"
  fi
}

manifest | sort -u > "$OUT/.manifest.tmp"
N_ENTRIES=0
while IFS= read -r rel; do
  [ "$rel" = "_headers" ] && continue
  copy_entry "$rel"
  N_ENTRIES=$((N_ENTRIES + 1))
done < "$OUT/.manifest.tmp"
rm -f "$OUT/.manifest.tmp"

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

printf 'build_dist: OK  entries=%d files=%d size=%.1f MiB (%.2f GiB) warn_near_limit=%d light=%d\n' \
  "$N_ENTRIES" "$N_FILES" \
  "$(awk -v b="$TOTAL" 'BEGIN{printf "%.1f", b/1048576}')" \
  "$(awk -v b="$TOTAL" 'BEGIN{printf "%.2f", b/1073741824}')" \
  "$WARNED" "$LIGHT"
