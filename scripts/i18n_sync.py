"""Incremental multilingual translation sync for the locales/ sidecar.

Rules enforced here:
  * Hash lock: only new or changed zh-TW source text is sent to the model.
    Finished translations are never re-run or overwritten.
  * Parent context injection: every request carries the parent place's
    zh-TW / en / ja names, lat/lon, genre_template and the global glossary.
  * Structured output: the model must return JSON matching RESPONSE_SCHEMA.
  * Sub-landmark resolution: abbreviated sub-landmarks in the title are expanded
    and written back to catalog.json (sub_landmarks) as anchors for future locales.
  * needs_review: anything the model cannot confirm is queued to i18n/review_queue.json.

This script never touches weather evaluation logic or condition thresholds and
never triggers a recompute.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_LANGS = ["en", "ja"]
SOURCE_LANG = "zh-TW"

RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["resolved_sub_landmarks", "translations", "needs_review", "review_reason"],
    "properties": {
        "resolved_sub_landmarks": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["source_term", "zh", "en", "ja", "confidence"],
                "properties": {
                    "source_term": {"type": "string"},
                    "zh": {"type": "string"},
                    "en": {"type": "string"},
                    "ja": {"type": "string"},
                    "confidence": {"type": "number"},
                },
            },
        },
        "translations": {
            "type": "object",
            "additionalProperties": False,
            "required": ["en", "ja"],
            "properties": {
                "en": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["name", "description"],
                    "properties": {"name": {"type": "string"}, "description": {"type": "string"}},
                },
                "ja": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["name", "description"],
                    "properties": {"name": {"type": "string"}, "description": {"type": "string"}},
                },
            },
        },
        "needs_review": {"type": "boolean"},
        "review_reason": {"type": "string"},
    },
}

SYSTEM_PROMPT = (
    "You are a professional photography-guide localizer for ChaseLights. "
    "Translate the supplied zh-TW opportunity title and description into English and Japanese. "
    "Use the provided parent place context and glossary so abbreviated sub-landmarks are expanded "
    "to their official names (for example 霞池 -> Kasumiga-ike / 霞ヶ池). "
    "Keep photography terminology consistent with the glossary. "
    "Never invent facts that are absent from the source text. "
    "If a sub-landmark cannot be confirmed from the given context, set needs_review=true and "
    "explain why in review_reason. Return JSON only."
)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")


def source_entries(root: Path) -> dict:
    """Collect zh-TW source text per opportunity with parent context."""
    catalog = load_json(root / "apps/web-v2/catalog.v2.json")
    places = {p["place_id"]: p for p in catalog.get("places", [])}
    entries = {}
    for p in sorted((root / "data/v2/opportunities").glob("*.json")):
        d = load_json(p)
        oid = d.get("opportunity_id")
        pid = d.get("place_id")
        cc = d.get("condition_contract") or {}
        name = (d.get("name_i18n") or {}).get(SOURCE_LANG, "")
        desc = (d.get("description_i18n") or {}).get(SOURCE_LANG, "")
        place = places.get(pid) or {}
        geo = []
        for cz in d.get("camera_contexts") or []:
            g = (cz.get("geometry") or {}).get("geojson") or {}
            if g.get("type") == "Point":
                geo = g.get("coordinates") or []
                break
        entries[oid] = {
            "opportunity_id": oid,
            "place_id": pid,
            "genre_template": cc.get("genre_template", ""),
            "name": name,
            "description": desc,
            "lat": geo[1] if len(geo) > 1 else None,
            "lon": geo[0] if len(geo) > 0 else None,
            "place_name_i18n": place.get("name_i18n") or {},
        }
    return entries


def build_payload(entry: dict, glossary: dict) -> dict:
    return {
        "source_lang": SOURCE_LANG,
        "target_langs": TARGET_LANGS,
        "opportunity": {
            "opportunity_id": entry["opportunity_id"],
            "genre_template": entry["genre_template"],
            "name_zh_tw": entry["name"],
            "description_zh_tw": entry["description"],
        },
        "parent_place": {
            "place_id": entry["place_id"],
            "name_zh_tw": entry["place_name_i18n"].get("zh-TW", ""),
            "name_en": entry["place_name_i18n"].get("en", ""),
            "name_ja": entry["place_name_i18n"].get("ja", ""),
            "lat": entry["lat"],
            "lon": entry["lon"],
        },
        "glossary": glossary.get("terms", {}),
    }


def _post(url: str, headers: dict, body: dict, timeout: int = 120) -> dict:
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_gemini(payload: dict, api_key: str, model: str = "gemini-2.5-flash") -> dict:
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
           f"?key={api_key}")
    body = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": json.dumps(payload, ensure_ascii=False)}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
            "temperature": 0.2,
        },
    }
    data = _post(url, {}, body)
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text)


def call_openrouter(payload: dict, api_key: str, model: str = "google/gemini-2.5-flash") -> dict:
    url = "https://openrouter.ai/api/v1/chat/completions"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        "response_format": {"type": "json_schema", "json_schema": {
            "name": "i18n_translation", "strict": True, "schema": RESPONSE_SCHEMA}},
        "temperature": 0.2,
    }
    data = _post(url, {"Authorization": f"Bearer {api_key}"}, body)
    text = data["choices"][0]["message"]["content"]
    return json.loads(text)


def stub_provider(payload: dict, entry: dict) -> dict:
    """Offline provider: echoes canonical translations from the source data.

    Used for --offline dry-runs (no API key) to prove the JSON schema, the
    sub-landmark resolution path and the write-back wiring.
    """
    src = load_json(ROOT / "data/v2/opportunities" / f"{entry['opportunity_id']}.json")
    name_i18n = src.get("name_i18n") or {}
    desc_i18n = src.get("description_i18n") or {}
    glossary = load_json(ROOT / "i18n/glossary.json").get("terms", {})
    landmarks = []
    for term, langs in glossary.items():
        if term in entry["name"] and term not in ("水面倒影", "城市夜景", "金色時刻", "藍調時刻",
                                                  "雲海", "晨光", "星空", "銀河", "櫻花", "紅葉",
                                                  "流冰", "霧", "瀑布", "峽谷", "能見度", "總雲量",
                                                  "低雲", "氣膠光學厚度", "降水", "風速", "月照率",
                                                  "非建議時段", "倒影", "構圖", "拍攝位置", "被攝主體"):
            landmarks.append({"source_term": term, "zh": term, "en": langs.get("en", ""),
                              "ja": langs.get("ja", ""), "confidence": 0.99})
    return {
        "resolved_sub_landmarks": landmarks,
        "translations": {
            "en": {"name": name_i18n.get("en", ""), "description": desc_i18n.get("en", "")},
            "ja": {"name": name_i18n.get("ja", ""), "description": desc_i18n.get("ja", "")},
        },
        "needs_review": False,
        "review_reason": "",
    }


def validate_response(resp: dict) -> list[str]:
    """Minimal JSON-schema check without external deps."""
    errs = []
    for key in RESPONSE_SCHEMA["required"]:
        if key not in resp:
            errs.append(f"missing {key}")
    if errs:
        return errs
    if not isinstance(resp["resolved_sub_landmarks"], list):
        errs.append("resolved_sub_landmarks not list")
    for lm in resp["resolved_sub_landmarks"]:
        for k in ("source_term", "zh", "en", "ja", "confidence"):
            if k not in lm:
                errs.append(f"sub_landmark missing {k}")
    tr = resp.get("translations") or {}
    for lang in TARGET_LANGS:
        node = tr.get(lang) or {}
        for k in ("name", "description"):
            if not node.get(k):
                errs.append(f"translations.{lang}.{k} empty")
    if not isinstance(resp.get("needs_review"), bool):
        errs.append("needs_review not bool")
    if not isinstance(resp.get("review_reason"), str):
        errs.append("review_reason not str")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--only", help="comma-separated opportunity ids")
    ap.add_argument("--dry-run", action="store_true", help="build payloads, call nothing")
    ap.add_argument("--offline", action="store_true", help="stub provider, no network")
    ap.add_argument("--force", action="store_true", help="ignore the hash lock")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    root = Path(args.root)
    locales = root / "locales"
    glossary = load_json(root / "i18n/glossary.json")
    lock_path = root / "i18n/i18n_lock.json"
    lock = load_json(lock_path) if lock_path.exists() else {"schema_version": "1.0", "entries": {}}
    queue_path = root / "i18n/review_queue.json"
    queue = load_json(queue_path) if queue_path.exists() else {"schema_version": "1.0", "items": []}

    entries = source_entries(root)
    only = set(args.only.split(",")) if args.only else None
    todo = []
    for oid, e in entries.items():
        if only and oid not in only:
            continue
        digest = sha256(e["name"] + "\n" + e["description"])
        prev = lock["entries"].get(oid)
        if not args.force and prev and prev.get("sha256") == digest:
            continue
        todo.append((oid, e, digest))
    if args.limit:
        todo = todo[: args.limit]

    results = []
    for oid, e, digest in todo:
        payload = build_payload(e, glossary)
        if args.dry_run:
            results.append({"id": oid, "payload_keys": sorted(payload), "hash": digest[:12]})
            continue
        if args.offline:
            resp = stub_provider(payload, e)
        else:
            key = os.environ.get("GEMINI_API_KEY")
            if key:
                resp = call_gemini(payload, key)
            else:
                key = os.environ.get("OPENROUTER_API_KEY")
                if not key:
                    print("ERROR: set GEMINI_API_KEY or OPENROUTER_API_KEY", file=sys.stderr)
                    return 2
                resp = call_openrouter(payload, key)
        errs = validate_response(resp)
        if errs:
            print(f"SCHEMA_FAIL {oid}: {errs}", file=sys.stderr)
            return 3

        # write translations into every locale catalog
        for lang in TARGET_LANGS:
            cat_path = locales / lang / "catalog.json"
            cat = load_json(cat_path)
            node = cat["opportunities"].setdefault(oid, {})
            node["name"] = resp["translations"][lang]["name"]
            node["description"] = resp["translations"][lang]["description"]
            save_json(cat_path, cat)

        # sub_landmarks anchors live on the parent place
        for lm in resp["resolved_sub_landmarks"]:
            for lang in [SOURCE_LANG] + TARGET_LANGS:
                cat_path = locales / lang / "catalog.json"
                cat = load_json(cat_path)
                place = cat["places"].setdefault(e["place_id"], {"name": "", "aliases": [], "sub_landmarks": {}})
                key = lm.get("zh") if lang == SOURCE_LANG else lm.get(lang)
                place.setdefault("sub_landmarks", {})[lm["source_term"]] = {
                    "name": key,
                    "confidence": lm.get("confidence", 0),
                }
                save_json(cat_path, cat)

        if resp.get("needs_review"):
            queue["items"].append({
                "opportunity_id": oid,
                "place_id": e["place_id"],
                "reason": resp.get("review_reason", ""),
                "source_name": e["name"],
            })
        lock["entries"][oid] = {
            "sha256": digest,
            "place_id": e["place_id"],
            "genre_template": e["genre_template"],
        }
        results.append({"id": oid, "needs_review": resp.get("needs_review"), "hash": digest[:12]})

    save_json(lock_path, lock)
    save_json(queue_path, queue)
    print(json.dumps({
        "processed": len(results),
        "skipped_unchanged": len(entries) - len(todo),
        "dry_run": args.dry_run,
        "offline": args.offline,
        "review_queue": len(queue["items"]),
        "results": results[:10],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
