# -*- coding: utf-8 -*-
"""Per-spot labeled 2x2 contact sheets: sheets/<oid>.jpg (stable names)."""
import json, os
from PIL import Image, ImageDraw, ImageFont

OUTDIR = r"D:/Dick/Project/ChaseLights/data/v2/staging/photo_refs"
SHEETS = os.path.join(OUTDIR, "sheets")
os.makedirs(SHEETS, exist_ok=True)

st = os.path.join(OUTDIR, "harvest_state.json")
state = json.load(open(st, encoding="utf-8")) if os.path.exists(st) else {}
files = []
for oid, v in state.items():
    for f in v.get("files", []):
        p = os.path.join(OUTDIR, f["file"])
        if os.path.exists(p) and os.path.getsize(p) > 30000:
            files.append((oid, f["file"]))

CELL_W, CELL_H, LABEL_H = 640, 426, 26
font = None
try:
    font = ImageFont.truetype("arial.ttf", 16)
except Exception:
    font = ImageFont.load_default()

by_oid = {}
for oid, fn in files:
    by_oid.setdefault(oid, []).append(fn)

n = 0
for oid, fns in sorted(by_oid.items()):
    outp = os.path.join(SHEETS, f"{oid}.jpg")
    if os.path.exists(outp) and os.path.getsize(outp) > 10000:
        continue
    sheet = Image.new("RGB", (CELL_W*2, (CELL_H+LABEL_H)*2), (24,24,24))
    d = ImageDraw.Draw(sheet)
    for k, fn in enumerate(fns[:4]):
        try:
            im = Image.open(os.path.join(OUTDIR, fn)).convert("RGB")
            im.thumbnail((CELL_W, CELL_H))
        except Exception:
            continue
        x = (k % 2)*CELL_W; y = (k//2)*(CELL_H+LABEL_H)
        sheet.paste(im, (x, y+LABEL_H))
        d.text((x+4, y+4), f"{k}: {fn}", fill=(255,255,120), font=font)
    sheet.save(outp, quality=82)
    n += 1
print(f"new sheets: {n}; total spots with photos: {len(by_oid)}")
