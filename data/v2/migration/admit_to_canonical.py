"""Admit parity-complete migration skeletons into W2 canonical (owner decision 2026-10-22).

Implements GOVERNANCE_DECISION_NO_REVIEW_GATE_20261022.md: no separate human
re-review cycle. Admission = mechanical, verified steps:

1. Copy data/v2/migration/skeletons/*.json -> data/v2/opportunities/
   (never overwriting existing canonical files).
2. Extend data/v2/indexes/research/source-lock.json canonical_records with
   byte pins for every new canonical file (commit resolved from Git after
   the files are committed; --commit-sha).
3. Pin the V1 source inputs (runtime catalog + per-region weather JSONs) as
   supporting_sources so place names resolve to byte-verified V1 sources.
4. Extend data/v2/indexes/research/curation.json: per-Place three-locale
   names (zh-TW/en/ja direct from the pinned V1 name_i18n) and per-Opportunity
   topic classifications via the deterministic legacy_theme -> topic formula
   (unevidenced themes stay unclassified, never force-fitted).

Idempotent; dry-run default. Steps: --step {move,pins,curation} --commit-sha.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/v2"
SKELETONS = DATA / "migration/skeletons"
CANONICAL = DATA / "opportunities"
INDEX = DATA / "indexes/research"
WEATHER_FILES = ["tw_weather.json", "jp_weather.json", "us_weather.json"]
CATALOG = "runtime_catalog_v004_r4_2.json"

# Deterministic legacy_theme -> topic formula (unevidenced themes stay unclassified).
THEME_TOPICS = {
    "sunrise": ["topic:sunrise"],
    "sunset": ["topic:sunset"],
    "reflection": ["topic:reflection"],
    "coast": ["topic:coastal-landscape"],
    "city_night": ["topic:cityscape"],
    "city_view": ["topic:cityscape"],
    "mountain_view": ["topic:mountain-landscape"],
}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8", newline="\n")


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def blob(raw):
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def git_commit_of(relpath):
    """The HEAD commit must contain the pinned bytes (file committed first)."""
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"]).decode().strip()


def canonical_pin(relpath):
    raw = (ROOT / relpath).read_bytes()
    return {"opportunity_id": Path(relpath).stem, "path": relpath,
            "blob_sha": blob(raw), "sha256": sha256(raw),
            "commit_sha": git_commit_of(relpath)}


def supporting_pin(relpath):
    raw = (ROOT / relpath).read_bytes()
    return {"path": relpath, "blob_sha": blob(raw), "sha256": sha256(raw),
            "commit_sha": git_commit_of(relpath)}


def step_move(dry_run):
    moved, kept = [], []
    for src in sorted(SKELETONS.glob("*.json")):
        dst = CANONICAL / src.name
        if dst.exists():
            kept.append(src.stem)
            continue
        if not dry_run:
            shutil.copyfile(src, dst)
        moved.append(src.stem)
    print(json.dumps({"moved": len(moved), "kept_canonical": len(kept)}))
    return 0


def step_pins(dry_run, commit_sha):
    lock = read(INDEX / "source-lock.json")
    pinned = {p["opportunity_id"] for p in lock["canonical_records"]}
    new = [p for p in sorted(CANONICAL.glob("*.json")) if p.stem not in pinned]
    supp_paths = {p["path"] for p in lock["supporting_sources"]}
    if dry_run:
        print(json.dumps({"new_pins": [p.stem for p in new], "supporting_to_add":
                          [f for f in [CATALOG] + WEATHER_FILES if f not in supp_paths]}))
        return 0
    for path in new:
        raw = path.read_bytes()
        lock["canonical_records"].append({
            "opportunity_id": path.stem, "path": f"data/v2/opportunities/{path.name}",
            "blob_sha": blob(raw), "sha256": sha256(raw), "commit_sha": commit_sha})
    for rel in [CATALOG] + WEATHER_FILES:
        if rel not in supp_paths:
            lock["supporting_sources"].append(supporting_pin(rel))
    lock["canonical_records"].sort(key=lambda p: p["opportunity_id"])
    lock["admission_basis"] = "GOVERNANCE_DECISION_NO_REVIEW_GATE_20261022"
    write(INDEX / "source-lock.json", lock)
    print(json.dumps({"canonical_records": len(lock["canonical_records"]),
                      "supporting_sources": len(lock["supporting_sources"])}))
    return 0


def _curation_names(wspot):
    names = (wspot.get("name_i18n") or {})
    out = {}
    for lang in ("zh-TW", "en", "ja"):
        value = names.get(lang)
        if not value:
            raise ValueError(f"V1 name missing for {wspot['spot_id']}/{lang}")
        out[lang] = {"direct_source": True, "source_path":
                     next(f for f in WEATHER_FILES
                          if read(ROOT / f) and any(s["spot_id"] == wspot["spot_id"]
                                                    for s in read(ROOT / f)["spots"])),
                     "spot_id": wspot["spot_id"], "pointer": f"/name_i18n/{lang}"}
    return out


def step_curation(dry_run):
    lock = read(INDEX / "source-lock.json")
    curation = read(INDEX / "curation.json")
    catalog = read(ROOT / CATALOG)
    spots = {s["spot_id"]: s for s in catalog["spots"]}
    docs = {p.stem: read(p) for p in CANONICAL.glob("*.json")}
    places = sorted({d["place_id"] for d in docs.values()})

    weather_source = {}
    for f in WEATHER_FILES:
        for s in read(ROOT / f)["spots"]:
            weather_source[s["spot_id"]] = f

    added_names = added_class = 0
    for pid in places:
        if pid not in curation["names"]:
            wspot = next(s for s in sum((read(ROOT / f)["spots"] for f in WEATHER_FILES), [])
                         if s["spot_id"] == pid)
            curation["names"][pid] = _curation_names(wspot)
            added_names += 1
    for oid, doc in docs.items():
        if oid in curation["classifications"]:
            continue
        opp = next(o for o in spots[doc["place_id"]]["opportunities"]
                   if o["opportunity_id"] == oid)
        topic_ids = THEME_TOPICS.get(opp.get("legacy_theme"), [])
        curation["classifications"][oid] = {
            "topic_ids": topic_ids,
            "canonical_pointers": ["/targets/0/name_i18n", "/description_i18n"],
            "evidence_claim_id": doc["evidence_claims"][0]["claim_id"],
            "evidence_refs": [],
            "classification_basis": f"legacy_theme={opp.get('legacy_theme')}",
        }
        added_class += 1
    if dry_run:
        print(json.dumps({"names_would_add": added_names, "classifications_would_add": added_class,
                          "places": len(places), "opportunities": len(docs)}))
        return 0
    curation["classification_method"] = "DETERMINISTIC_LEGACY_THEME_FORMULA_UNEVIDENCED_STAY_UNCLASSIFIED"
    curation["name_method"] = "V1_PINNED_SOURCE_VERBATIM_NO_NEW_TRANSLATION"
    curation["admission_basis"] = "GOVERNANCE_DECISION_NO_REVIEW_GATE_20261022"
    write(INDEX / "curation.json", curation)
    print(json.dumps({"names_added": added_names, "classifications_added": added_class,
                      "names_total": len(curation["names"]),
                      "classifications_total": len(curation["classifications"])}))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--step", choices=["move", "pins", "curation"], required=True)
    ap.add_argument("--commit-sha", default=None,
                    help="commit sha containing the admitted canonical files (step=pins)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.step == "pins" and not args.dry_run and not args.commit_sha:
        ap.error("--commit-sha required for step=pins (files must already be committed)")
    try:
        if args.step == "move":
            return step_move(args.dry_run)
        if args.step == "pins":
            return step_pins(args.dry_run, args.commit_sha)
        return step_curation(args.dry_run)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print("ERROR " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
