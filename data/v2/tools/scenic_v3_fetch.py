#!/usr/bin/env python3
"""CL-DATA-30: multi-source photo fetch for scenic-v3 full-catalog scoring.

Sources per place (CL-DATA-28 method, keyless only):
  1. Wikimedia Commons full-text search (en / zh / ja names)
  2. Wikipedia article images (zh / en / ja wiki) resolved on Commons
  3. Openverse API (keyless anonymous)

Incremental progress is written to data/v2/audits/discovery/scenic-v3-full-progress.json
after EVERY place, so the run is resumable.
"""
from __future__ import annotations
import json, re, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "data/v2/audits/discovery/scenic-v3-full-progress.json"
SCRATCH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("C:/Users/Dick_/AppData/Local/hermes/profiles/chaselights_manager/cache/scratch")
PILOT_PHOTOS = SCRATCH / "cl27_photos.json"

UA = {"User-Agent": "ChaseLights-scenic-v3/1.0 (repo data research; read-only fetch)"}
# conservative non-representative-photo title filter (repres. filter pre-scoring, CL-DATA-28 fix)
BAD = re.compile(
    r"(THETA|entrance|entrance|logo|icon|\.svg$|map\b|_map|satellite|地図|界碑|sign\b|signage|"
    r"parking|ticket|stamp\b|coin\b|plate\b|flag\b|seal\b|diagram|poster|banner|brochure|"
    r"人行天橋施工|sign|內部|inside|menu|desk|service|toilet|shower|ryokan|hotel\b)", re.I)
IMG_EXT = re.compile(r"\.(jpe?g|png|tiff?|webp)$", re.I)

def _get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if attempt == 3:
                print(f"  HTTP {e.code} FAIL {url[:110]}", flush=True)
                return {"__error__": f"HTTP {e.code}"}
            time.sleep(6.0 * (attempt + 1))  # 429 backoff: 6/12/18s
        except Exception as e:
            if attempt == 3:
                print(f"  NET FAIL {url[:110]}: {e}", flush=True)
                return {"__error__": str(e)}
            time.sleep(2.0 * (attempt + 1))

def commons_search(q, limit=8):
    u = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&formatversion=2"
         "&generator=search&gsrsearch=" + urllib.parse.quote(q) +
         f"&gsrnamespace=6&gsrlimit={limit}&prop=imageinfo&iiprop=url%7Csize%7Cmime%7Cextmetadata&iiurlwidth=640")
    d = _get(u)
    if "__error__" in d or "query" not in d:
        return []
    out = []
    for p in d["query"].get("pages", []):
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii or (ii.get("mime") or "").split("/")[0] != "image":
            continue
        out.append({"title": p.get("title", ""), "url": ii.get("url"), "thumb": ii.get("thumburl"),
                    "w": ii.get("width"), "h": ii.get("height"), "source": "commons-search",
                    "query": q, "desc": ii.get("extmetadata", {}).get("ImageDescription", {}).get("value", "")[:200]})
    return out

def wiki_images(lang, title, limit=10):
    u = (f"https://{lang}.wikipedia.org/w/api.php?action=query&format=json&formatversion=2&titles="
         + urllib.parse.quote(title) + f"&prop=images&imlimit={limit}&redirects=1")
    d = _get(u)
    if "__error__" in d or "query" not in d:
        return []
    pages = d["query"].get("pages", [])
    if not pages:
        return []
    titles = [im.get("title") for im in pages[0].get("images", []) or []]
    titles = [t for t in titles if t and IMG_EXT.search(t) and not BAD.search(t)]
    if not titles:
        return []
    u2 = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&formatversion=2&prop=imageinfo"
          "&iiprop=url%7Csize%7Cmime&iiurlwidth=640&titles=" + urllib.parse.quote("|".join(titles[:10])))
    d2 = _get(u2)
    if "__error__" in d2 or "query" not in d2:
        return []
    out = []
    for p in d2["query"].get("pages", []):
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii or (ii.get("mime") or "").split("/")[0] != "image":
            continue
        out.append({"title": p.get("title", ""), "url": ii.get("url"), "thumb": ii.get("thumburl"),
                    "w": ii.get("width"), "h": ii.get("height"), "source": f"wiki-{lang}", "query": title, "desc": ""})
    return out

def openverse(q):
    u = ("https://api.openverse.org/v1/images/?q=" + urllib.parse.quote(q) +
         "&page_size=6&filter_dead=false")
    d = _get(u)
    if "__error__" in d or "results" not in d:
        return []
    out = []
    for r in d["results"][:6]:
        out.append({"title": r.get("title") or "", "url": r.get("url"), "thumb": r.get("thumbnail"),
                    "w": r.get("width"), "h": r.get("height"), "source": "openverse", "query": q,
                    "license": (r.get("license") or "") + " " + (r.get("license_version") or ""), "desc": ""})
    return out

def dedupe_filter(cands):
    seen, out = set(), []
    for c in cands:
        if not c.get("thumb") and not c.get("url"):
            continue
        key = (c.get("title") or "").lower()
        if key in seen or not key:
            continue
        seen.add(key)
        w, h = c.get("w") or 0, c.get("h") or 0
        if w and h and (w < 500 or h < 350 or w / max(h, 1) > 3.2 or h / max(w, 1) > 2.6):
            continue
        if BAD.search(c.get("title") or ""):
            c = dict(c, filtered_out=True)
            out.append(c)
            continue
        out.append(c)
    return out

def load_registry():
    scoring = json.loads((REPO / "data/v2/audits/discovery/catalog-scoring.json").read_text(encoding="utf-8"))
    catalog = json.loads((REPO / "apps/web-v2/catalog.v2.json").read_text(encoding="utf-8"))
    i18n = {p["place_id"]: p.get("name_i18n", {}) for p in catalog["places"]}
    reg = {}
    for r in scoring["ranking"]:
        pid = r["place_id"]
        n = i18n.get(pid, {})
        reg[pid] = {"place_id": pid, "name_zh": r.get("name_zh"), "name_en": n.get("en"),
                    "name_ja": n.get("ja"), "region": r.get("region"), "coords": r.get("coords"),
                    "v2_weighted_total": r.get("weighted_total")}
    return reg

def main():
    reg = load_registry()
    prog = {"schema": "scenic-v3-full-progress/1", "ticket": "CL-DATA-30",
            "stage_photos": {}, "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if OUT.exists():
        old = json.loads(OUT.read_text(encoding="utf-8"))
        prog["stage_photos"] = old.get("stage_photos", {})
    if "--retry-low" in sys.argv:
        dropped = [pid for pid, e in prog["stage_photos"].items()
                   if not e.get("pilot_seed") and len(e.get("photos") or []) < 3]
        for pid in dropped:
            del prog["stage_photos"][pid]
        print(f"retry-low: dropped {len(dropped)}: {dropped}", flush=True)
    pilot = {}
    if PILOT_PHOTOS.exists():
        pilot = json.loads(PILOT_PHOTOS.read_text(encoding="utf-8"))
    todo = [pid for pid in reg if pid not in prog["stage_photos"]]
    print(f"registry={len(reg)} done={len(prog['stage_photos'])} todo={len(todo)}", flush=True)
    for i, pid in enumerate(todo):
        r = reg[pid]
        if pid in pilot:
            files = [dict(f, source="commons-search") for f in pilot[pid].get("files", [])]
            files = [f for f in files if not f.get("filtered_out")]
            prog["stage_photos"][pid] = {"name": r["name_zh"], "photos": files,
                                         "pilot_seed": True, "sources_tried": ["pilot-cl27"]}
        else:
            qs = []
            def _add(q):
                if q and q not in qs:
                    qs.append(q)
            for q in (r.get("name_en"), r.get("name_zh"), r.get("name_ja")):
                _add(q)
            # parenthetical-stripped variants: Commons full-text search fails on long phrases
            for q in list(qs):
                s = re.sub(r"[（(].*?[）)]", "", q).strip()
                if s and s != q:
                    _add(s)
                if re.match(r"^[\u4e00-\u9fff\u3040-\u30ff]", s or ""):
                    short = s[:2]
                    if len(s) > 2 and short not in qs:
                        _add(short)
                else:
                    short = " ".join(s.split()[:2])
                    if short and short != s and short not in qs:
                        _add(short)
            cands = []
            # parallel query batch (3 workers) with per-query spacing to stay API-polite
            import concurrent.futures as _cf
            with _cf.ThreadPoolExecutor(3) as ex:
                futs = [ex.submit(lambda q=q: (commons_search(q, 8), time.sleep(1.2))) for q in qs[:7]]
                for f in futs:
                    cands += f.result()[0]
            got_commons = len([c for c in dedupe_filter(cands) if not c.get("filtered_out")])
            if got_commons < 5:  # skip wiki-langlinks when Commons search is already rich
                wq = []
                for lang, q in (("zh", r.get("name_zh")), ("en", r.get("name_en")), ("ja", r.get("name_ja"))):
                    if q:
                        s2 = re.sub(r"[（(].*?[）)]", "", q).strip()
                        wq += [(lang, q)] + ([(lang, s2)] if s2 and s2 != q else [])
                with _cf.ThreadPoolExecutor(3) as ex:
                    futs = [ex.submit(lambda q=q: (wiki_images(q[0], q[1], 10), time.sleep(1.2))) for q in wq]
                    for f in futs:
                        cands += f.result()[0]
            if len([c for c in dedupe_filter(cands) if not c.get("filtered_out")]) < 6 and r.get("name_en"):
                cands += openverse(r["name_en"])
                time.sleep(0.5)
            cands = dedupe_filter(cands)
            good = [c for c in cands if not c.get("filtered_out")]
            dropped = [c.get("title") for c in cands if c.get("filtered_out")]
            files, srcs = [], set()
            # interleave sources for diversity
            by_src = {}
            for c in good:
                by_src.setdefault(c["source"], []).append(c)
            order = list(by_src)
            while len(files) < 6 and any(by_src[s] for s in order):
                for s in order:
                    if by_src[s] and len(files) < 6:
                        files.append(by_src[s].pop(0))
                        srcs.add(s)
            prog["stage_photos"][pid] = {"name": r["name_zh"], "photos": files, "dropped_titles": dropped,
                                         "sources_tried": sorted(srcs), "pilot_seed": False}
            prog["updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        tmp = OUT.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(prog, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(OUT)
        got = len(prog["stage_photos"][pid]["photos"])
        print(f"[{i+1}/{len(todo)}] {pid} {r['name_zh']}: {got} photos src={prog['stage_photos'][pid]['sources_tried']}", flush=True)
        if not prog["stage_photos"][pid].get("pilot_seed"):
            time.sleep(0.4)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
