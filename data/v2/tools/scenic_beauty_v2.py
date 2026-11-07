#!/usr/bin/env python3
"""Catalog scenic-beauty evidence extraction for rubric v2 (CL-DATA-25R).

Mechanical, honest: only in-repo evidence is used; places with no evidence
stay `unknown` (never fabricated).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
AUDITS = REPO_ROOT / "data/v2/audits"
EVIDENCE_REGISTRY = REPO_ROOT / "runtime_evidence_registry_r4_2.json"

# s2 official scenic classification markers (official A-class / UNESCO / Three-X style)
S2_PATTERNS = [
    r"世界[遺遗]産", r"世界[遗遗]产", r"UNESCO", r"世界遗产", r"World Heritage",
    r"日本三大", r"三大[樹樹氷冰名園名所夜景]", r"三大樹氷", r"三大夜景",
    r"全国観光資源台帳", r"全國觀光資源", r"特A", r"Ａ級", r"A級", r"A级",
    r"[八国日]大?[城景湯]?八景", r"室蘭八景", r"國家風景區", r"国家風景区",
    r"國家公園", r"国立公園", r"国家公园",
]
S2_TOP_PATTERNS = [
    r"世界[遺遗]産", r"世界[遗遗]产", r"UNESCO", r"世界遗产", r"World Heritage",
    r"之首", r"の首位", r"特A", r"Ａ級", r"A級（規模日本一）", r"A级（规模日本一）",
]
S1_PATTERNS = [
    r"みんなのカメラ", r"攝影社群", r"攝影社群常收錄", r"摄影社群", r"photo community",
    r"撮影コミュニティ",
]


def _load_audit_rows():
    rows = {}  # opportunity_id / place evidence text
    for f in sorted(AUDITS.glob("*evidence*.json")):
        try:
            doc = json.loads(f.read_bytes().decode("utf-8"))
        except Exception:
            continue
        for key in ("evidence", "source_records"):
            for row in doc.get(key, []) or []:
                oid = row.get("id") or ""
                text = " ".join(str(row.get(k, "")) for k in
                                ("supports", "subject", "evidence_scope", "url", "limitation"))
                rows.setdefault(oid, []).append({"file": f.name, "url": row.get("url"), "text": text})
        # web-evidence style: places[] with evidence[] per row
        for p in doc.get("places", []) or []:
            pid = p.get("place_id") or ""
            text = " ".join(str(p.get(k, "")) for k in ("coord_source", "slug"))
            urls = [u for u in (p.get("sources") or []) if isinstance(u, str)]
            rows.setdefault(pid, []).append({"file": f.name, "url": urls[0] if urls else None,
                                             "text": text, "urls": urls})
    try:
        reg = json.loads(EVIDENCE_REGISTRY.read_bytes().decode("utf-8"))
    except Exception:
        reg = {}
    for oid, v in (reg.get("opportunities") or {}).items():
        text = " ".join(str(v.get(k, "")) for k in ("subject", "evidence_scope", "forecast_boundary"))
        for s in v.get("sources") or []:
            text += " " + json.dumps(s, ensure_ascii=False)
        rows.setdefault(oid, []).append({"file": EVIDENCE_REGISTRY.name, "url": None, "text": text})
    return rows


def _place_evidence(place_id, opps, rows):
    """Aggregate evidence texts + URLs belonging to a place."""
    oids = [o["opportunity_id"] for o in opps if o["place_id"] == place_id]
    texts, urls = [], []
    for oid in oids:
        for r in rows.get(oid, []):
            texts.append(r["text"])
            if r.get("url"):
                urls.append(r["url"] if isinstance(r["url"], str) else None)
    for r in rows.get(place_id, []):
        texts.append(r["text"])
        for u in (r.get("urls") or [r.get("url")]):
            if isinstance(u, str):
                urls.append(u)
    return texts, [u for u in urls if u]


def _any(patterns, text):
    return any(re.search(p, text) for p in patterns)


def score_scenic_beauty(place_id, place_name, opps, rows):
    """Rubric v2 scenic_beauty, mechanical per CL-DATA-26 classes:
    base 2 + s1 photo-community(+1) + s2 official/UNESCO/Three-X classification(+1)
    + top-tier bonus(+1) + s3 guide-list frequency >=2 independent sources(+1), cap 5.
    Returns (value_or_None, detail) — None means honestly `unknown`."""
    name_zh, name_en, name_ja = (place_name.get("zh-TW", ""), place_name.get("en", ""),
                                 place_name.get("ja", ""))
    texts, urls = _place_evidence(place_id, opps, rows)
    # contract text is catalog-internal classification/scoring evidence too
    for o in opps:
        if o["place_id"] != place_id:
            continue
        blob = json.dumps(o, ensure_ascii=False)
        texts.append(blob)
    corpus = name_zh + " " + name_en + " " + name_ja + " " + " ".join(texts)
    s1 = _any(S1_PATTERNS, corpus)
    s2 = _any(S2_PATTERNS, corpus)
    top = s2 and _any(S2_TOP_PATTERNS, corpus)
    # s3: >=2 independent guide/media URLs across registry+audits for this place
    distinct = sorted({u.split("/")[2] if "://" in u else u for u in urls})
    s3 = len(distinct) >= 2
    if not (s1 or s2 or s3):
        return None, {"s1": 0, "s2": 0, "s3": 0, "top": 0,
                      "note": "no in-repo scenic-classification evidence — honest unknown",
                      "distinct_evidence_hosts": distinct}
    value = 2 + (1 if s1 else 0) + (1 if s2 else 0) + (1 if top else 0) + (1 if s3 else 0)
    return min(5, max(2, value)), {"s1": 1 if s1 else 0, "s2": 1 if s2 else 0,
                                   "s3": 1 if s3 else 0, "top": 1 if top else 0,
                                   "distinct_evidence_hosts": distinct}
