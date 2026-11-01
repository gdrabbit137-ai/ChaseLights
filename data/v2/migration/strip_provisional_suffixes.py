"""CL-UI-07: remove provisional/pending markers from W2 data and UI bundles.

One-off deterministic migration for the already-admitted canonical set (owner
approved, ticket CL-UI-07): the V1->V2 skeleton generator used to bake a
provisional English/Japanese title marker into name_i18n and a
pending-translation marker into description_i18n. Those markers leaked to the
UI. As of build_skeletons.py (this ticket) unreviewed en/ja titles carry the
zh-TW source value verbatim and the review state lives only in the internal
provenance.review_status field; the UI falls back to the zh-TW name for
locales without a reviewed title.

This tool applies the same transformation to:
1. data/v2/opportunities/*.json   (canonical records; name_i18n for the
   opportunity and every target, plus description_i18n)
2. the generated UI bundles under apps/web-v2/ (catalog.v2.json,
   browse-index.v2.json, opportunity-contracts.json, evaluations-latest.json,
   evaluations-details/*.json) — markers embedded by earlier generations are
   stripped textually so the shipped bundles match the regenerated canonical
   set until the scheduled evaluations refresh rewrites them.

Idempotent: re-running with no markers left is a no-op. The exact marker
strings are pinned constants — never a fuzzy/pattern match — so legitimate
prose (e.g. honest "not yet verified" advisories) is untouched.

Modes:
  python strip_provisional_suffixes.py --step check    report residual markers
  python strip_provisional_suffixes.py --step canonical
      patch canonical opportunity records in place
  python strip_provisional_suffixes.py --step pins --commit-sha <sha>
      refresh source-lock.json canonical_records byte pins after commit
  python strip_provisional_suffixes.py --step bundles
      patch the shipped apps/web-v2 bundle files in place
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANONICAL = ROOT / "data/v2/opportunities"
INDEX = ROOT / "data/v2/indexes/research"
WEB = ROOT / "apps/web-v2"

# Pinned marker strings (exact, from the pre-CL-UI-07 generator).
TITLE_SUFFIX_EN = " (provisional English title, pending review)"
TITLE_SUFFIX_JA = "（暫定日本語タイトル、レビュー待ち）"
# The JA description marker is replaced by "" (the trailing "。" that separates
# the note from the skeleton note belongs to the surrounding text and stays).
DESC_MARKER_EN = " (zh-TW source values retained pending translation)."
DESC_MARKER_JA = "（zh-TW原文のまま、翻訳待ち）"

MARKERS = (TITLE_SUFFIX_EN, TITLE_SUFFIX_JA, DESC_MARKER_EN, DESC_MARKER_JA)


def strip_text(value):
    """Strip pinned markers from one string; preserves all other bytes."""
    out = value
    if TITLE_SUFFIX_EN in out:
        out = out.replace(TITLE_SUFFIX_EN, "")
    if TITLE_SUFFIX_JA in out:
        out = out.replace(TITLE_SUFFIX_JA, "")
    if DESC_MARKER_EN in out:
        out = out.replace(DESC_MARKER_EN, "")
    if DESC_MARKER_JA in out:
        out = out.replace(DESC_MARKER_JA, "")
    return out


def strip_value(value):
    if isinstance(value, str):
        return strip_text(value)
    if isinstance(value, list):
        return [strip_value(v) for v in value]
    if isinstance(value, dict):
        return {k: strip_value(v) for k, v in value.items()}
    return value


def dump(doc):
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def residual_files(paths):
    hits = []
    for path in paths:
        raw = path.read_bytes()
        if any(m.encode("utf-8") in raw for m in MARKERS):
            hits.append(str(path.relative_to(ROOT)))
    return hits


def step_check():
    targets = sorted(CANONICAL.glob("*.json")) + sorted(WEB.glob("evaluations-details/*.json")) + [
        WEB / "catalog.v2.json", WEB / "browse-index.v2.json",
        WEB / "opportunity-contracts.json", WEB / "evaluations-latest.json"]
    hits = residual_files([p for p in targets if p.exists()])
    print(json.dumps({"residual_files": hits, "count": len(hits)}))
    return 1 if hits else 0


def step_canonical():
    changed = []
    for path in sorted(CANONICAL.glob("*.json")):
        raw = path.read_bytes()
        if not any(m.encode("utf-8") in raw for m in MARKERS):
            continue
        doc = json.loads(raw.decode("utf-8"))
        doc = strip_value(doc)
        if dump(doc).encode("utf-8") != raw:
            path.write_text(dump(doc), encoding="utf-8", newline="\n")
            changed.append(path.stem)
    print(json.dumps({"changed": len(changed), "ids": changed[:5], "total": len(changed)}))
    return 0


def blob(raw):
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def step_pins(commit_sha):
    """Refresh canonical_records byte pins in source-lock.json.

    Run after committing the patched canonical files: each pin's blob/sha256
    is recomputed from the committed bytes and stamped with the given commit
    sha, matching admit_to_canonical.py's pin format.
    """
    lock_path = INDEX / "source-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    updated = 0
    for pin in lock["canonical_records"]:
        raw = (ROOT / pin["path"]).read_bytes()
        new = {"opportunity_id": pin["opportunity_id"], "path": pin["path"],
               "blob_sha": blob(raw), "sha256": hashlib.sha256(raw).hexdigest(),
               "commit_sha": commit_sha}
        if new != pin:
            pin.clear()
            pin.update(new)
            updated += 1
    write = json.dumps(lock, ensure_ascii=False, indent=2) + "\n"
    if write.encode("utf-8") != lock_path.read_bytes():
        lock_path.write_text(write, encoding="utf-8", newline="\n")
    print(json.dumps({"updated_pins": updated, "commit_sha": commit_sha}))
    return 0


def step_bundles():
    changed = []
    targets = [WEB / "catalog.v2.json", WEB / "browse-index.v2.json",
               WEB / "opportunity-contracts.json", WEB / "evaluations-latest.json"]
    targets += sorted(WEB.glob("evaluations-details/*.json"))
    for path in targets:
        if not path.exists():
            continue
        raw = path.read_bytes()
        if not any(m.encode("utf-8") in raw for m in MARKERS):
            continue
        doc = json.loads(raw.decode("utf-8"))
        doc = strip_value(doc)
        # Preserve the original serialization style: minified bundles stay
        # minified, pretty-printed files keep indent=2 + trailing newline.
        pretty = b"    \"" in raw or b"\n  \"" in raw
        text = json.dumps(doc, ensure_ascii=False,
                          indent=2 if pretty else None,
                          separators=None if pretty else (",", ":"))
        if pretty:
            text += "\n"
        if text.encode("utf-8") != raw:
            path.write_text(text, encoding="utf-8", newline="\n")
            changed.append(str(path.relative_to(ROOT)))
    print(json.dumps({"changed": changed, "count": len(changed)}))
    return 0


def main():
    ap = argparse.ArgumentParser(description=(sys.modules[__name__].__doc__ or "").splitlines()[0])
    ap.add_argument("--step", choices=["check", "canonical", "pins", "bundles"], required=True)
    ap.add_argument("--commit-sha", default=None,
                    help="commit containing the patched canonical bytes (step=pins)")
    args = ap.parse_args()
    if args.step == "pins":
        if not args.commit_sha:
            ap.error("--commit-sha is required for step=pins")
        return step_pins(args.commit_sha)
    return {"check": step_check, "canonical": step_canonical, "bundles": step_bundles}[args.step]()


if __name__ == "__main__":
    sys.exit(main())
