"""Extract human-readable strings into per-locale sidecar files.

Reads the canonical sources (apps/web-v2/app.mjs UI dictionaries, data/v2/templates,
data/v2/opportunities, apps/web-v2/catalog.v2.json) and writes:

  locales/<lang>/ui.json        static interface copy (buttons, filters, tier labels, help)
  locales/<lang>/taxonomy.json  genre template names, metric labels, status words
  locales/<lang>/catalog.json   place names, opportunity long/short names, seasonal notes,
                                locked sub_landmarks per place

No weather/evaluation logic is touched and no evaluation is recomputed.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ["zh-TW", "en", "ja"]
JS_LOCALE_KEYS = {"zh-TW", "en", "ja"}

STATUS_TERMS = {
    "zh-TW": {"REQUIRED": "必須", "QUALITY": "加分", "BLOCKER": "直接失敗", "UNKNOWN": "待確認"},
    "en": {"REQUIRED": "Required", "QUALITY": "Quality", "BLOCKER": "Blocker", "UNKNOWN": "Unknown"},
    "ja": {"REQUIRED": "必須", "QUALITY": "加点", "BLOCKER": "阻害", "UNKNOWN": "未確認"},
}


def _extract_object(src: str, start: int) -> str:
    """Return the balanced {...} object literal starting at `start`."""
    depth = 0
    i = start
    in_str = False
    esc = False
    while i < len(src):
        ch = src[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return src[start:i + 1]
        i += 1
    raise ValueError("unbalanced object literal")


def _js_to_json(text: str) -> str:
    # quote bare identifier keys: {key:  / ,key:
    text = re.sub(r'([{,]\s*)([A-Za-z_$][A-Za-z0-9_$-]*)\s*:', r'\1"\2":', text)
    return text


def _load_js_dict(src: str, name: str) -> dict:
    m = re.search(r"const\s+" + re.escape(name) + r"\s*=\s*\{", src)
    if not m:
        raise ValueError(f"{name} not found")
    obj = _extract_object(src, src.index("{", m.start()))
    return json.loads(_js_to_json(obj))


def _read_js(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_ui(app_mjs: Path) -> dict:
    src = _read_js(app_mjs)
    merged = {lang: {} for lang in LOCALES}
    for block in ["copy", "homeCopy", "browseCopy", "topicCopy"]:
        d = _load_js_dict(src, block)
        for lang in LOCALES:
            merged[lang].update(d.get(lang, {}))
    research = _load_js_dict(src, "researchCopy")
    out = {}
    for lang in LOCALES:
        out[lang] = {"app": merged[lang], "research": research.get(lang, {})}
    return out


def build_taxonomy(root: Path) -> dict:
    metrics = _load_js_dict(_read_js(root / "apps/web-v2/app.mjs"), "EVAL_METRICS")
    genres = {}
    for p in sorted((root / "data/v2/templates").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        tid = d.get("template_id") or p.stem
        title = d.get("title_i18n") or {}
        if title:
            genres[tid] = title
    # inline genres carry their name on the opportunity itself
    for p in sorted((root / "data/v2/opportunities").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        cc = d.get("condition_contract") or {}
        gid = cc.get("genre_template")
        if gid and gid not in genres and isinstance(cc.get("genre_template_name_i18n"), dict):
            genres[gid] = cc["genre_template_name_i18n"]
    out = {}
    for lang in LOCALES:
        out[lang] = {
            "genre_templates": {k: v.get(lang, v.get("en", "")) for k, v in genres.items()},
            "metrics": {k: {"label": v.get(lang, v.get("en", "")), "unit": v.get("unit", "")}
                        for k, v in metrics.items()},
            "status_terms": STATUS_TERMS[lang],
        }
    return out


def build_catalog(root: Path) -> dict:
    cat = json.loads((root / "apps/web-v2/catalog.v2.json").read_text(encoding="utf-8"))
    places = {p["place_id"]: p for p in cat.get("places", [])}
    opps = {o["opportunity_id"]: o for o in cat.get("opportunities", [])}
    short = {}
    sp = root / "data/v2/copy/genre_short_names.json"
    if sp.exists():
        short = json.loads(sp.read_text(encoding="utf-8")).get("genres", {})
    out = {}
    for lang in LOCALES:
        prior = {}
        prior_path = ROOT / "locales" / lang / "catalog.json"
        if prior_path.exists():
            try:
                prior = json.loads(prior_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                prior = {}
        prior_places = prior.get("places") or {}
        prior_opps = prior.get("opportunities") or {}
        place_out = {}
        for pid, p in places.items():
            name = (p.get("name_i18n") or {}).get(lang) or (p.get("name_i18n") or {}).get("en", "")
            aliases = (p.get("aliases_i18n") or {}).get(lang) or []
            prev = prior_places.get(pid) or {}
            place_out[pid] = {
                "name": name,
                "aliases": aliases,
                # sub_landmarks are resolved anchors; never wiped by a re-extract
                "sub_landmarks": prev.get("sub_landmarks") or {},
            }
        opp_out = {}
        for oid, o in opps.items():
            gid = (o.get("condition_contract") or {}).get("genre_template", "")
            s = (short.get(gid) or {}).get(lang) if isinstance(short.get(gid), dict) else None
            prev = prior_opps.get(oid) or {}
            # zh-TW always follows the canonical source; target languages keep the
            # last translated value until i18n_sync.py refreshes it.
            keep = lang != "zh-TW"
            opp_out[oid] = {
                "name": (prev.get("name") if keep else None) or (o.get("name_i18n") or {}).get(lang) or (o.get("name_i18n") or {}).get("en", ""),
                "short_name": s or prev.get("short_name") or "",
                "description": (prev.get("description") if keep else None) or (o.get("description_i18n") or {}).get(lang) or "",
                "seasonal_note": prev.get("seasonal_note") or "",
            }
        out[lang] = {"places": place_out, "opportunities": opp_out}
    return out


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT
    ui = build_ui(root / "apps/web-v2/app.mjs")
    tax = build_taxonomy(root)
    cat = build_catalog(root)
    for lang in LOCALES:
        d = root / "locales" / lang
        d.mkdir(parents=True, exist_ok=True)
        for name, payload in (("ui", ui[lang]), ("taxonomy", tax[lang]), ("catalog", cat[lang])):
            (d / f"{name}.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8", newline="\n")
    print(json.dumps({
        "locales": LOCALES,
        "ui_keys": {l: len(ui[l]["app"]) + len(ui[l]["research"]) for l in LOCALES},
        "genres": len(tax["zh-TW"]["genre_templates"]),
        "metrics": len(tax["zh-TW"]["metrics"]),
        "places": len(cat["zh-TW"]["places"]),
        "opportunities": len(cat["zh-TW"]["opportunities"]),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
