#!/usr/bin/env python3
"""CL-DATA-25R rollback continuation: steps 7-13 (manifest, python files, dedupe)."""
import json, re, subprocess, sys
from pathlib import Path
from collections import Counter

ROOT = Path(r'D:/tmp/cl-data-25r')
sys.path.insert(0, str(ROOT))

REMOVE = {'jp-050': '安比高原雲海ゴンドラ', 'tw-090': '加路蘭海岸遊憩區',
          'tw-092': '北關海潮公園', 'tw-096': '半天寮好望角', 'tw-097': '擎天崗草原'}
REMOVE_OPPS = ['jp-050-P01', 'tw-090-P01', 'tw-090-P02', 'tw-092-P01', 'tw-096-P01', 'tw-097-P01', 'tw-097-P02']

def load(p): return json.loads((ROOT / p).read_bytes().decode('utf-8'))
def dump(v): return json.dumps(v, ensure_ascii=False, indent=2) + '\n'
def write(p, text): (ROOT / p).write_bytes(text.encode('utf-8'))

cat = load('runtime_catalog_v004_r4_2.json')

# ---------- 7) runtime manifest (write totals first so opportunities.py import validates) ----------
mf = load('runtime_catalog_manifest_r4_2.json')
for reg, ids in (('jp', ['jp-050']), ('tw', ['tw-090', 'tw-092', 'tw-096', 'tw-097'])):
    spots = [s for s in cat['spots'] if s['spot_id'].startswith(reg + '-')]
    opps = [o for s in spots for o in s['opportunities']]
    retired = sorted(set(mf['regions'][reg].get('retired_spot_ids', [])) | set(ids))
    mf['regions'][reg]['retired_spot_ids'] = retired
    mf['regions'][reg]['counts'] = {
        'spots': len(spots), 'opportunities': len(opps),
        'condition_variants': sum(len(o.get('condition_variants', [])) for o in opps),
        'profile_viewpoint_relations': sum(len(o.get('viewpoints', [])) for o in opps)}
mf['totals'] = dict(cat['counts'])
write('runtime_catalog_manifest_r4_2.json', dump(mf))

import opportunities as _O
pol = Counter()
for s in cat['spots']:
    for o in s['opportunities']:
        pol[_O.runtime_policy(o)] += 1
mf['runtime_policy_counts'] = dict(pol)
write('runtime_catalog_manifest_r4_2.json', dump(mf))
print('manifest updated:', mf['regions']['tw']['counts'], mf['regions']['jp']['counts'], mf['runtime_policy_counts'])

# ---------- 8) regions.py line-based rollback ----------
rp = ROOT / 'regions.py'
text = rp.read_bytes().decode('utf-8').replace('\r\n', '\n')
zh_names = list(REMOVE.values())
pat_tuple = re.compile(r'\s*\(\d+\.\d+, \d+\.\d+, "(?:%s)"' % '|'.join(map(re.escape, zh_names)))
pat_elev = re.compile(r'\s*"(?:%s)": \d+,\s*$' % '|'.join(map(re.escape, zh_names)))
pat_block = re.compile(r'\s*"(?:%s)": \{' % '|'.join(map(re.escape, zh_names)))
pat_admin = re.compile(r'\s*"(?:%s)": \[' % '|'.join(REMOVE))
out, skip = [], 0
for ln in text.split('\n'):
    if skip:
        skip -= 1
        continue
    if pat_admin.match(ln):
        continue
    if pat_tuple.match(ln) or pat_elev.match(ln):
        continue
    if pat_block.match(ln):
        # multi-line SPOT_OVERRIDES block: skip until closing line '},'
        while out and not out[-1].rstrip().endswith('},'):
            skip = 99
            break
        # simpler: mark mode to skip following lines until '},' seen
        skip_block = True
        out.append(None)  # marker
        continue
    out.append(ln)
# redo block skipping properly
out, skip = [], False
for ln in text.split('\n'):
    if skip:
        if re.match(r'\s*\},', ln):
            skip = False
        continue
    if pat_admin.match(ln) or pat_tuple.match(ln) or pat_elev.match(ln):
        continue
    if pat_block.match(ln):
        skip = True
        continue
    out.append(ln)
text2 = '\n'.join(out)
for zh in zh_names:
    assert zh not in text2, f'regions.py still references {zh}'
for pid in REMOVE:
    assert pid not in text2, f'regions.py still references {pid}'
write('regions.py', text2)
print('regions.py patched')

# ---------- 9) runtime_dependencies.py ----------
dep = ROOT / 'runtime_dependencies.py'
td = dep.read_bytes().decode('utf-8').replace('\r\n', '\n')
pat_oid = re.compile(r'\s*"(?:%s)",?\s*$' % '|'.join(REMOVE_OPPS))
lines = [l for l in td.split('\n') if not pat_oid.match(l)]
td2 = '\n'.join(lines)
for oid in REMOVE_OPPS:
    assert oid not in td2, f'runtime_dependencies still has {oid}'
# dedupe adjacent duplicate id lines
lines, dedup = td2.split('\n'), []
for ln in lines:
    if dedup and dedup[-1] == ln and re.match(r'\s*"[a-z]{2}-\d{3}-P\d\d",$', ln):
        continue
    dedup.append(ln)
td2 = '\n'.join(dedup)
write('runtime_dependencies.py', td2)
print('runtime_dependencies.py patched')

# ---------- 10) opportunity_runtime.py ----------
ort = ROOT / 'opportunity_runtime.py'
to = ort.read_bytes().decode('utf-8').replace('\r\n', '\n')
to2 = '\n'.join(l for l in to.split('\n') if not l.strip().startswith(('"tw-090-P01"', '"tw-097-P01"')))
assert 'tw-090-P01' not in to2 and 'tw-097-P01' not in to2
write('opportunity_runtime.py', to2)
print('opportunity_runtime.py patched')

# ---------- 11) fail_reason_overrides ----------
fr = load('data/v2/copy/fail_reason_overrides.json')
for oid in REMOVE_OPPS:
    fr.pop(oid, None)
write('data/v2/copy/fail_reason_overrides.json', dump(fr))
print('fail_reason_overrides pruned')

# ---------- 12) weather_details for removed spots ----------
for f in ['weather_details/jp/jp-050.json', 'weather_details/tw/tw-090.json',
          'weather_details/tw/tw-092.json', 'weather_details/tw/tw-096.json', 'weather_details/tw/tw-097.json']:
    subprocess.run(['git', 'rm', '-q', f], cwd=str(ROOT), check=True)
print('weather_details removed')

# ---------- 13) 5km dedupe check ----------
import math
def dist_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, (lat1, lon1, lat2, lon2))
    x = (lo2 - lo1) * math.cos((la1 + la2) / 2)
    y = la2 - la1
    return R * math.sqrt(x * x + y * y)

tw = load('tw_weather.json')
jp = load('jp_weather.json')
spots = {s['spot_id']: (s['lat'], s['lon'], s['name_i18n']['zh-TW']) for s in jp['spots'] + tw['spots']}
cand = (24.823055, 121.7025)  # zh.wikipedia 櫻花陵園 24°49′23″N 121°42′9″E
near = sorted((round(dist_km(cand[0], cand[1], v[0], v[1]), 3), k, v[2]) for k, v in spots.items())
d031 = next(d for d in near if d[1] == 'tw-031')
conf = []
for reg_spots in (jp['spots'], tw['spots']):
    for i in range(len(reg_spots)):
        for j in range(i + 1, len(reg_spots)):
            a, b = reg_spots[i], reg_spots[j]
            d = dist_km(a['lat'], a['lon'], b['lat'], b['lon'])
            if d < 5.0:
                conf.append({'a': a['spot_id'], 'b': b['spot_id'], 'km': round(d, 3)})
report = {'ticket': 'CL-DATA-25R', 'checked': 'all catalog spots pairwise (legacy json) + tw-098 candidate',
          'tw_098_candidate': {'name': '渭水之丘／櫻花陵園', 'lat': cand[0], 'lon': cand[1],
                               'nearest_existing': near[:3], 'vs_tw_031_km': round(d031[0], 3)},
          'within_5km_pairs': conf}
(ROOT / 'data/v2/audits/cl-data-25r_dedupe_report.json').write_bytes(dump(report).encode('utf-8'))
print('tw-098 nearest:', near[:3])
print('within-5km pairs in catalog:', conf)
