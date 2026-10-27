# -*- coding: utf-8 -*-
"""Multi-source harvest: Wikimedia Commons + Pixabay (AI pipeline, downloadable)
+ Unsplash (human reference only: URLs stored, NOT downloaded, NOT AI-analyzed).
Targets: zero-candidate spots from both phases + round2 pending list.
Resumable via harvest_state_m.json. Rate-limit friendly."""
import json, os, re, time, socket, urllib.parse, urllib.request

socket.setdefaulttimeout(40)
TMP = os.environ.get("TMPDIR", r"C:/Users/Dick_/AppData/Local/Temp")
STAGE = r"D:/Dick/Project/ChaseLights/data/v2/staging"
OUTDIR = os.path.join(STAGE, "photo_refs2")
UA = {"User-Agent": "ChaseLights-research/1.0 (photography genre research; gdrabbit137-ai)"}
WM_API = "https://commons.wikimedia.org/w/api.php"
UNSPLASH_KEY = None
PIXABAY_KEY = None
for line in open(r"C:/Users/Dick_/AppData/Local/hermes/profiles/photography_master/.env",
                 encoding="utf-8", errors="ignore"):
    if line.startswith("UNSPLASH_ACCESS_KEY="):
        UNSPLASH_KEY = line.split("=", 1)[1].strip()
    if line.startswith("PIXABAY_API_KEY="):
        PIXABAY_KEY = line.split("=", 1)[1].strip()

BAD_TITLE = re.compile(r"map|def\b|logo|diagram|sign|djvu|scan|painting|drawing|"
                       r"portrait|statue|book|document|stamp|coin|label", re.I)

def http_json(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40))

# ---------- Wikimedia ----------
def wm_search(q, limit=8):
    params = {"action": "query", "generator": "search", "gsrsearch": q, "gsrnamespace": "6",
              "gsrlimit": str(limit), "prop": "imageinfo", "iiprop": "url|size|mime", "format": "json"}
    for a in range(3):
        try:
            d = http_json(WM_API + "?" + urllib.parse.urlencode(params))
            out = []
            for p in (d.get("query", {}).get("pages", {}) or {}).values():
                ii = (p.get("imageinfo") or [{}])[0]
                if ii.get("mime", "").startswith("image/") and (ii.get("width") or 0) >= 800:
                    if BAD_TITLE.search(p["title"]):
                        continue
                    out.append({"src": "wikimedia", "title": p["title"], "url": ii["url"],
                                "w": ii.get("width"), "h": ii.get("height")})
            return out
        except Exception as e:
            print('  wm err:', type(e).__name__, str(e)[:100], flush=True)
            time.sleep(5 * (a + 1))
    return []

def wm_download(title, fn):
    tf = ("https://commons.wikimedia.org/wiki/Special:FilePath/"
          + urllib.parse.quote(title[5:]) + "?width=1600")
    return generic_download(tf, fn)

# ---------- Pixabay ----------
def px_search(q, limit=6):
    if not PIXABAY_KEY:
        return []
    for a in range(3):
        try:
            u = "https://pixabay.com/api/?" + urllib.parse.urlencode(
                {"key": PIXABAY_KEY, "q": q, "per_page": limit, "safesearch": "true",
                 "image_type": "photo", "orientation": "horizontal"})
            d = http_json(u)
            out = []
            for h in d.get("hits", []):
                t = h.get("tags", "")
                if BAD_TITLE.search(t):
                    continue
                if h.get("webformatWidth", 0) >= 800:
                    out.append({"src": "pixabay", "title": h.get("tags", ""),
                                "url": h.get("largeImageURL"),
                                "page": h.get("pageURL"),
                                "w": h.get("webformatWidth"), "h": h.get("webformatHeight")})
            return out
        except Exception as e:
            print('  px err:', type(e).__name__, str(e)[:100], flush=True)
            time.sleep(5 * (a + 1))
    return []

def px_download(url, fn):
    return generic_download(url, fn)

# ---------- Unsplash (URL only, no download) ----------
def us_search(q, limit=4):
    if not UNSPLASH_KEY:
        return []
    for a in range(2):
        try:
            u = ("https://api.unsplash.com/search/photos?"
                 + urllib.parse.urlencode({"query": q, "per_page": limit,
                                           "orientation": "landscape"})
                 + "&client_id=" + UNSPLASH_KEY)
            d = http_json(u)
            out = []
            for r in d.get("results", []):
                out.append({"src": "unsplash", "title": r.get("alt_description") or r.get("description") or "",
                            "url": r["urls"]["regular"], "page": r["links"]["html"],
                            "photographer": r["user"]["name"],
                            "w": r["width"], "h": r["height"]})
            return out
        except Exception as e:
            print('  us err:', type(e).__name__, str(e)[:100], flush=True)
            time.sleep(2)
    return []

# ---------- download helper ----------
def generic_download(url, fn):
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                data = r.read(40_000_000)
            if len(data) < 30000:
                return False
            with open(fn, "wb") as f:
                f.write(data)
            return True
        except Exception:
            time.sleep(15 * (a + 1))
    return False


def wm_geo(lat, lon, radius=5000, limit=6):
    """geosearch around coordinates - catches spots whose names transliterate badly"""
    params = {"action": "query", "generator": "geosearch", "ggscoord": f"{lat}|{lon}",
              "ggsradius": str(radius), "ggslimit": str(limit), "ggsnamespace": "6",
              "prop": "imageinfo", "iiprop": "url|size|mime", "format": "json"}
    try:
        d = http_json(WM_API + "?" + urllib.parse.urlencode(params))
        out = []
        for pg in sorted((d.get("query", {}).get("pages", {}) or {}).values(),
                         key=lambda x: x.get("index", 99)):
            ii = (pg.get("imageinfo") or [{}])[0]
            if ii.get("mime", "").startswith("image/") and (ii.get("width") or 0) >= 800:
                if BAD_TITLE.search(pg["title"]):
                    continue
                out.append({"src": "wikimedia", "title": pg["title"], "url": ii["url"],
                            "w": ii.get("width"), "h": ii.get("height")})
        return out
    except Exception as e:
        print("  geo err:", type(e).__name__, str(e)[:80], flush=True)
        return []

ZH_TAIL = re.compile(r"(層巒|遠眺|日出|夕景|夕照|晨曦|藍調|夜景|雲海|全景|鳥瞰|眺望|展望|"
                     r"海蝕|地景|花田|草原|森林|步道|溫泉|燈塔|大橋|老街|漁港|platform|"
                     r"sunrise|sunset|blue hour|night|panorama|viewpoint|lookout|forest|"
                     r"lake|bay|coast|cliff|skyline|harbor|temple|shrine)[，＋/／・(-]?.*$")
NUM = re.compile(r"^[A-Za-z]{2}-\d{3}")

def core_names(spot):
    """derive short search keys from zh/root/en"""
    names = []
    zh = spot.get("zh") or ""
    root = spot.get("root") or zh.split("・")[0]
    for src in (root, zh.split("・")[0], zh.split("，")[0], zh.split("（")[0]):
        if not src:
            continue
        base = ZH_TAIL.sub("", src).strip("　 ")
        for cand in (src, base):
            if cand and len(cand) >= 2 and cand not in names and not NUM.match(cand):
                names.append(cand)
    for seg in re.split(r"[／/|]", zh):
        seg = seg.strip()
        if len(seg) >= 2 and seg not in names and not NUM.match(seg):
            names.append(seg)
    if root and len(root) >= 5:
        for n in (4, 3):
            pref = root[:n]
            if pref not in names and not NUM.match(pref):
                names.append(pref)
    en = spot.get("pname_en") or spot.get("name_en") or spot.get("nav_en") or ""
    if en and len(en) > 3:
        en_short = en.split("·")[0].split(",")[0].split("・")[0].strip()
        if en_short and en_short not in names:
            names.append(en_short)
        for w in en_short.replace("-", " ").split():
            if len(w) >= 3 and w not in names:
                names.append(w)
    return names[:8]

# ---------- per-spot orchestration ----------
def harvest_one(oid, spot, outdir, n_target=6):
    zh = spot.get("zh") or ""
    name = spot.get("pname") or ""
    queries = core_names(spot)
    if name and name not in queries:
        queries.append(name)
    cands = {"wikimedia": [], "pixabay": [], "unsplash": []}
    for q in queries:
        if len(cands["wikimedia"]) >= 8 and len(cands["pixabay"]) >= 4:
            break
        if len(cands["wikimedia"]) < 8:
            cands["wikimedia"] += [c for c in wm_search(q, 8) if c not in cands["wikimedia"]]
        if len(cands["pixabay"]) < 4:
            cands["pixabay"] += [c for c in px_search(q, 6) if c not in cands["pixabay"]]
        if len(cands["unsplash"]) < 4:
            cands["unsplash"] += [c for c in us_search(q, 4) if c not in cands["unsplash"]]
        time.sleep(3)
    if len(cands["wikimedia"]) < 4 and spot.get("lat"):
        cands["wikimedia"] += [c for c in wm_geo(spot["lat"], spot["lon"])
                               if c not in cands["wikimedia"]]
    # pick: wikimedia up to 4, pixabay up to 2, unsplash urls up to 2 (reference only)
    picks = cands["wikimedia"][:4] + cands["pixabay"][:2]
    got = []
    for i, c in enumerate(picks, 1):
        fn = os.path.join(outdir, f"{oid}_m{i:02d}.jpg")
        ok = (wm_download(c["title"], fn) if c["src"] == "wikimedia" else px_download(c["url"], fn))
        if ok:
            got.append({**c, "file": os.path.basename(fn)})
    refs = cands["unsplash"][:2]
    return {"cands": len(cands["wikimedia"]) + len(cands["pixabay"]), "got": len(got),
            "got_detail": got, "unsplash_refs": refs, "queries": queries}

def load_targets():
    tg = {}
    for path in [TMP + "/harvest_targets.json", TMP + "/harvest_targets_p2.json"]:
        if os.path.exists(path):
            for t in json.load(open(path, encoding="utf-8")):
                tg[t["oid"]] = t
    return tg

def pending_oids():
    zero = []
    for phase, fname in (("photo_refs", "harvest_state.json"), ("photo_refs2", "harvest_state.json")):
        st = json.load(open(os.path.join(STAGE, phase, fname), encoding="utf-8"))
        for k, v in st.items():
            if isinstance(v, dict) and (v.get("cands", 1) == 0 or not v.get("files")):
                zero.append(k)
    return sorted(set(zero))

def main():
    tgt = load_targets()
    todo = pending_oids()
    if len(os.sys.argv) > 1:  # optional explicit oids
        todo = [o for o in os.sys.argv[1:] if o in tgt]
    state_path = os.path.join(OUTDIR, "harvest_state_m.json")
    state = json.load(open(state_path, encoding="utf-8")) if os.path.exists(state_path) else {}
    print(f"pending {len(todo)} oids", flush=True)
    for n, oid in enumerate(todo, 1):
        if oid in state and state[oid].get("got", 0) > 0:
            continue
        spot = tgt.get(oid, {})
        r = harvest_one(oid, spot, OUTDIR)
        state[oid] = r
        json.dump(state, open(state_path, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"[{n}/{len(todo)}] {oid} {spot.get('zh','')[:16]} cands={r['cands']} got={r['got']} unsplash={len(r['unsplash_refs'])} q={r['queries']}", flush=True)
        time.sleep(5)

if __name__ == "__main__":
    main()
