#!/usr/bin/env python3
"""CL-DATA-30: Commons community signals (CL-DATA-29 method, implemented here).

Per valid-eligible photo:
  * quality badges: Commons categories (Featured pictures / Quality images /
    Valued images / Picture of the day)
  * 12-month Commons File page view counts (Wikimedia REST pageviews; missing
    payload = unknown, never 0)
Signals are attached per photo title in progress JSON `stage_community`;
finalize applies the owner-corrected composite rule (negative only after
complete badge inventory, ±0.25) on VALID photos only.
"""
from __future__ import annotations
import json, re, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "data/v2/audits/discovery/scenic-v3-full-progress.json"
UA = {"User-Agent": "ChaseLights-scenic-v3/1.0 (repo data research; read-only fetch)"}
PV_START, PV_END = "20251109", "20261108"  # 12-month window (owner correction: 60d median too low-res)

BADGE_PATTERNS = [
    ("featured", re.compile(r"Featured[_ ]pictures[_ ]on[_ ]Wikimedia[_ ]Commons", re.I)),
    ("quality", re.compile(r"Quality[_ ]images", re.I)),
    ("valued", re.compile(r"Valued[_ ]images", re.I)),
    ("potd", re.compile(r"Picture[_ ]of[_ ]the[_ ]day", re.I)),
    ("popular", re.compile(r"Popular[_ ]images", re.I)),
]

def _get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    for a in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {}
            time.sleep(1.0)
        except Exception:
            if a == 2:
                return {}
            time.sleep(1.0)
    return {}

def categories_for(titles):
    """titles: list of File:X -> {title: [categories]}"""
    out = {}
    for i in range(0, len(titles), 25):
        batch = titles[i:i + 25]
        u = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&formatversion=2"
             "&prop=categories&cllimit=100&clshow=!hidden&titles="
             + urllib.parse.quote("|".join(t.replace(" ", "_") for t in batch)))
        d = _get(u)
        for p in (d.get("query", {}) or {}).get("pages", []) or []:
            out[p.get("title", "")] = [c.get("title", "") for c in p.get("categories", []) or []]
        time.sleep(0.25)
    return out

def pageviews_for(title):
    """title: File:X -> 12-month view sum; None when payload missing (unknown, never 0)"""
    t = title.replace("File:", "").replace(" ", "_")
    u = (f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/commons.wikimedia/"
         f"all-access/user/{urllib.parse.quote(t)}/monthly/{PV_START}/{PV_END}")
    d = _get(u)
    items = d.get("items")
    if not items:
        return None  # payload missing -> unknown (owner correction)
    return sum(int(item.get("views", 0)) for item in items)

def main():
    prog = json.loads(OUT.read_text(encoding="utf-8"))
    stage = prog.setdefault("stage_community", {})
    todo = []
    for pid, entry in prog["stage_photos"].items():
        for ph in entry.get("photos", []):
            key = ph.get("title") or ph.get("url") or ""
            if key and key.startswith("File:") and key not in stage and ph.get("thumb"):
                todo.append((pid, key, ph))
    print(f"todo photos={len(todo)}", flush=True)
    # badges in bulk
    all_titles = sorted({k for _, k, _ in todo if k.startswith("File:")})
    cats = categories_for(all_titles)
    for i, (pid, key, ph) in enumerate(todo):
        cl = cats.get(key, []) or cats.get(key.replace(" ", "_"), []) or cats.get(key.replace("_", " "), [])
        badges = [name for name, pat in BADGE_PATTERNS if any(pat.search(c or "") for c in cl)]
        pv = pageviews_for(key) if key.startswith("File:") else None
        stage[key] = {"badges": badges, "pv12mo": pv, "pv_unknown": pv is None, "cats": cl[:8]}
        if i % 20 == 0:
            prog["updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            tmp = OUT.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(prog, ensure_ascii=False, indent=1), encoding="utf-8")
            tmp.replace(OUT)
            print(f"[{i}/{len(todo)}] {key[:50]} badges={badges} pv={pv}", flush=True)
        time.sleep(0.12)
    prog["updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(prog, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(OUT)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
