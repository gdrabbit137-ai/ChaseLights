#!/usr/bin/env python3
"""CL-DATA-30: build per-place photo montages for visual scoring (vision layer).

Downloads each photo's 640px thumb, lays out PAIRS of places per montage
(each place = up to 6 photos in a 2x3 grid, labels A..F / G..L, place header).
Montages go to scratch (not repo). Records montage->photo mapping JSON.
"""
from __future__ import annotations
import json, sys, time, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "data/v2/audits/discovery/scenic-v3-full-progress.json"
SCRATCH = Path("C:/Users/Dick_/AppData/Local/hermes/profiles/chaselights_manager/cache/scratch")
MDIR = SCRATCH / "d30_montages"
MDIR.mkdir(exist_ok=True)
UA = {"User-Agent": "ChaseLights-scenic-v3/1.0 (repo data research; read-only fetch)"}
PW, PH = 420, 320  # per-photo cell
HEAD = 34

def fetch_img(url, tries=2):
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=25) as r:
                data = r.read()
            from io import BytesIO
            return Image.open(BytesIO(data)).convert("RGB")
        except Exception:
            if a == tries - 1:
                return None
            time.sleep(1.2)

def place_strip(photos, prefix, name, place_row):
    # grid 3 cols x 2 rows
    strip = Image.new("RGB", (PW * 3, HEAD + PH * 2), "white")
    d = ImageDraw.Draw(strip)
    try:
        f = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 20)
    except Exception:
        f = ImageFont.load_default()
    d.text((6, 5), f"{place_row}: {name}", fill="black", font=f)
    failed = []
    for i, p in enumerate(photos[:6]):
        img = fetch_img(p.get("thumb") or p.get("url"))
        if img is None:
            failed.append(i)
            img = Image.new("RGB", (PW, PH), "gray")
        img.thumbnail((PW, PH))
        x, y = (i % 3) * PW, HEAD + (i // 3) * PH
        strip.paste(img, (x, y))
        d.rectangle([x, y, x + 34, y + 26], fill="yellow")
        d.text((x + 6, y + 4), f"{prefix}{chr(65 + i)}", fill="black", font=f)
    return strip, failed

def main():
    prog = json.loads(OUT.read_text(encoding="utf-8"))
    photos_stage = prog["stage_photos"]
    for pid, e in photos_stage.items():
        if e.get("pilot_seed") and not e.get("_montaged"):
            e["_montaged"] = True  # pilot places reuse CL-DATA-27 scores, no montage needed
            print("skip pilot", pid)
    todo = [pid for pid in photos_stage if not photos_stage[pid].get("_montaged") and len(photos_stage[pid].get("photos") or []) >= 1]
    PER = 4
    groups = [todo[i:i + PER] for i in range(0, len(todo), PER)]
    mapping = {}
    mf = MDIR / "mapping.json"
    if mf.exists():
        mapping = json.loads(mf.read_text(encoding="utf-8"))
    print(f"todo={len(todo)} montages={len(groups)}", flush=True)
    for k, grp in enumerate(groups):
        mid = f"g{grp[0]}"
        if mid in mapping:
            continue
        strips = []
        fail = {}
        for j, pid in enumerate(grp):
            s, f = place_strip(photos_stage[pid]["photos"][:6], "", photos_stage[pid]["name"], j + 1)
            strips.append(s)
            fail[pid] = f
        H = sum(s.height for s in strips)
        canvas = Image.new("RGB", (max(s.width for s in strips), H), "white")
        y = 0
        for s in strips:
            canvas.paste(s, (0, y))
            y += s.height
        path = MDIR / f"{mid}.jpg"
        canvas.save(path, quality=82)
        mapping[mid] = {"places": grp, "path": str(path),
                        "photo_order": {pid: [ph.get("title") for ph in photos_stage[pid]["photos"][:6]] for pid in grp},
                        "failed_dl": {p: f for p, f in fail.items() if f}}
        mf.write_text(json.dumps(mapping, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[{k+1}/{len(groups)}] {mid} ok", flush=True)
        for pid in grp:
            photos_stage[pid]["_montaged"] = True
        tmp = OUT.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(prog, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(OUT)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
