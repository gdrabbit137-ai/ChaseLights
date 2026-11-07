#!/usr/bin/env python3
"""CL-DATA-25R: rubric-v2 alignment rollback + 渭水之丘 admission (one-shot builder)."""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(r'D:/tmp/cl-data-25r')
REMOVE = {'jp-050': '安比高原雲海ゴンドラ', 'tw-090': '加路蘭海岸遊憩區',
          'tw-092': '北關海潮公園', 'tw-096': '半天寮好望角', 'tw-097': '擎天崗草原'}
REMOVE_OPPS = ['jp-050-P01', 'tw-090-P01', 'tw-090-P02', 'tw-092-P01', 'tw-096-P01', 'tw-097-P01', 'tw-097-P02']
DISC = ROOT / 'data/v2/tools/discovery'

def load(p): return json.loads((ROOT / p).read_bytes().decode('utf-8'))
def dump(v): return json.dumps(v, ensure_ascii=False, indent=2) + '\n'
def write(p, text): (ROOT / p).write_bytes(text.encode('utf-8'))

# ---------- 1) remove the 7 V2 opportunity docs (git rm) ----------
for oid in REMOVE_OPPS:
    subprocess.run(['git', 'rm', '-q', f'data/v2/opportunities/{oid}.json'], cwd=str(ROOT), check=True)
print('opportunity docs removed')

# ---------- 2) source-lock: drop canonical records + add rollback note ----------
sl_path = 'data/v2/indexes/research/source-lock.json'
sl = load(sl_path)
before = len(sl['canonical_records'])
sl['canonical_records'] = [r for r in sl['canonical_records'] if r['opportunity_id'] not in REMOVE_OPPS]
assert len(sl['canonical_records']) == before - 7, (before, len(sl['canonical_records']))
sl['rollback_note_cl_data_25r_20261107'] = (
    'CL-DATA-25R (2026-11-07): rubric-v2 alignment — owner ruling: weighted_total_v2 >= 3.8 admits '
    'directly; below 3.8 goes to the Excel side list only. Rolled back the full legacy+V2+runtime catalog '
    'entries of the 5 v1-built but v2-rejected places (jp-050 安比雲海 3.30, tw-090 加路蘭 3.70, '
    'tw-092 北關海潮 3.60, tw-096 好望角 3.70, tw-097 擎天崗 3.20); their canonical_records are removed and '
    'their dossiers remain under data/v2/audits/discovery/ for the Excel side list. jp-041 流氷 is kept '
    '(v2 4.8 passes the line; drift_ice stays not_evaluatable).')
write(sl_path, dump(sl))
print('source-lock canonical_records:', len(sl['canonical_records']))

# ---------- 3) curation: exact coverage of remaining canonical docs ----------
cu_path = 'data/v2/indexes/research/curation.json'
cu = load(cu_path)
for pid in REMOVE:
    cu['names'].pop(pid, None)
for oid in REMOVE_OPPS:
    cu['classifications'].pop(oid, None)
write(cu_path, dump(cu))
print('curation pruned')

# ---------- 4) seasonal calendar: prune removed opp ids ----------
cal_path = 'data/v2/seasonal-calendar.json'
cal = load(cal_path)
keep = []
removed_plants = []
for e in cal['entries']:
    e['spots'] = [s for s in e['spots'] if s not in REMOVE_OPPS]
    if e['spots']:
        keep.append(e)
    else:
        removed_plants.append(e['plant_id'])
cal['entries'] = keep
write(cal_path, dump(cal))
print('calendar pruned, entries dropped:', removed_plants)

# ---------- 5) legacy weather json ----------
for reg, ids in (('jp', ['jp-050']), ('tw', ['tw-090', 'tw-092', 'tw-096', 'tw-097'])):
    p = f'{reg}_weather.json'
    doc = load(p)
    doc['spots'] = [s for s in doc['spots'] if s['spot_id'] not in ids]
    doc['total_spots'] = len(doc['spots'])
    doc['stale_spot_ids'] = [i for i in doc.get('stale_spot_ids', []) if i not in ids]
    doc['stale_spot_count'] = len(doc['stale_spot_ids'])
    write(p, dump(doc))
    print(p, 'spots =', len(doc['spots']))

# ---------- 6) runtime catalog ----------
cat = load('runtime_catalog_v004_r4_2.json')
cat['spots'] = [s for s in cat['spots'] if s['spot_id'] not in REMOVE]
cat['counts'] = {
    'spots': len({s['spot_id'] for s in cat['spots']}),
    'opportunities': sum(len(s['opportunities']) for s in cat['spots']),
    'condition_variants': sum(sum(len(o.get('condition_variants', [])) for o in s['opportunities']) for s in cat['spots']),
    'profile_viewpoint_relations': sum(sum(len(o.get('viewpoints', [])) for o in s['opportunities']) for s in cat['spots']),
}
write('runtime_catalog_v004_r4_2.json', dump(cat))
print('runtime catalog counts:', cat['counts'])

# ---------- 7) runtime manifest ----------
mf = load('runtime_catalog_manifest_r4_2.json')
import opportunities as _O
for reg, ids in (('jp', ['jp-050']), ('tw', ['tw-090', 'tw-092', 'tw-096', 'tw-097'])):
    spots = [s for s in cat['spots'] if s['spot_id'].startswith(reg + '-')]
    opps = [o for s in spots for o in s['opportunities']]
    retired = sorted(set(mf['regions'][reg].get('retired_spot_ids', [])) | set(ids))
    mf['regions'][reg]['retired_spot_ids'] = retired
    mf['regions'][reg]['counts'] = {
        'spots': len(spots), 'opportunities': len(opps),
        'condition_variants': sum(len(o.get('condition_variants', [])) for o in opps),
        'profile_viewpoint_relations': sum(len(o.get('viewpoints', [])) for o in opps)}
from collections import Counter
pol = Counter()
for s in cat['spots']:
    for o in s['opportunities']:
        pol[_O.runtime_policy(o)] += 1
mf['totals'] = dict(cat['counts'])
mf['runtime_policy_counts'] = dict(pol)
write('runtime_catalog_manifest_r4_2.json', dump(mf))
print('manifest updated:', mf['regions']['tw']['counts'], mf['regions']['jp']['counts'])

# ---------- 8) regions.py line-based rollback ----------
rp = ROOT / 'regions.py'
text = rp.read_bytes().decode('utf-8').replace('\r\n', '\n')
lines = text.split('\n')
out, skipping = [], 0
zh_names = list(REMOVE.values())
for ln in lines:
    if skipping:  # continuation of a removed SPOT_OVERRIDES block
        skipping -= 1
        continue
    stripped = ln.strip()
    hit = stripped.startswith('"%s":' % '') and False
    if any(stripped.startswith('"%s": [' % pid) for pid in REMOVE):
        continue  # admin area entry
    if any(zh in ln for zh in zh_names) and (
            re.match(r'\s*\(\d+\.\d+, \d+\.\d+, "(%s)"' % '|'.join(map(re.escape, zh_names)), ln)
            or re.match(r'\s*"(?:%s)": \d+,\s*$' % '|'.join(map(re.escape, zh_names)), ln)
            or re.match(r'\s*"(?:%s)": \{' % '|'.join(map(re.escape, zh_names)), ln)):
        if ln.rstrip().endswith('{'):
            # multi-line SPOT_OVERRIDES block: skip until closing '},'
            skipping = 5
        continue
    out.append(ln)
text2 = '\n'.join(out)
for zh in zh_names:
    assert zh not in text2, f'regions.py still references {zh}'
for pid in REMOVE:
    assert pid not in text2, f'regions.py still references {pid}'
write('regions.py', text2)
print('regions.py patched')

# ---------- 9) runtime_dependencies.py: strip removed opportunity ids ----------
dep = ROOT / 'runtime_dependencies.py'
td = dep.read_bytes().decode('utf-8').replace('\r\n', '\n')
lines = td.split('\n')
out = []
for ln in lines:
    if re.match(r'\s*"(?:%s)",?\s*$' % '|'.join(REMOVE_OPPS), ln):
        continue
    out.append(ln)
td2 = '\n'.join(out)
for oid in REMOVE_OPPS:
    assert oid not in td2, f'runtime_dependencies still has {oid}'
# dedupe consecutive duplicate lines left by the v1 batch inserts
lines = td2.split('\n'); dedup = []
for ln in lines:
    if dedup and ln.strip() != '' and dedup[-1] == ln and re.match(r'\s*"[a-z]{2}-\d{3}-P\d\d",$', ln):
        continue
    dedup.append(ln)
td2 = '\n'.join(dedup)
write('runtime_dependencies.py', td2)
print('runtime_dependencies.py patched')

# ---------- 10) opportunity_runtime.py star-field overrides ----------
ort = ROOT / 'opportunity_runtime.py'
to = ort.read_bytes().decode('utf-8').replace('\r\n', '\n')
for oid in ('"tw-090-P01"', '"tw-097-P01"'):
    lines = to.split('\n')
    to = '\n'.join(l for l in lines if not l.strip().startswith(oid + ':'))
assert 'tw-090-P01' not in to and 'tw-097-P01' not in to
write('opportunity_runtime.py', to)
print('opportunity_runtime.py patched')

# ---------- 11) fail_reason_overrides ----------
fr = load('data/v2/copy/fail_reason_overrides.json')
for oid in REMOVE_OPPS:
    fr.pop(oid, None)
write('data/v2/copy/fail_reason_overrides.json', dump(fr))
print('fail_reason_overrides pruned')

# ---------- 12) weather_details files for removed spots ----------
for f in ['weather_details/jp/jp-050.json', 'weather_details/tw/tw-090.json',
          'weather_details/tw/tw-092.json', 'weather_details/tw/tw-096.json', 'weather_details/tw/tw-097.json']:
    subprocess.run(['git', 'rm', '-q', f], cwd=str(ROOT), check=True)
print('weather_details removed')

# ---------- 13) 5km dedupe check (remaining catalog + the tw-098 candidate) ----------
import math
def dist_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, (lat1, lon1, lat2, lon2))
    x = (lo2 - lo1) * math.cos((la1 + la2) / 2)
    y = la2 - la1
    return R * math.sqrt(x * x + y * y)

tw = load('tw_weather.json')
spots = {s['spot_id']: (s['lat'], s['lon'], s['name_i18n']['zh-TW']) for s in tw['spots']}
cand = (24.823055, 121.7025, '渭水之丘')  # zh.wikipedia 櫻花陵園 24°49′23″N 121°42′9″E
d031 = dist_km(*cand[:2], *spots['tw-031'][:2])
report = {'candidates_checked': [], 'min_distance_km': {}, 'conflicts': []}
all_spots = list(spots.items())
near = sorted((round(dist_km(cand[0], cand[1], v[0], v[1]), 3), k) for k, v in all_spots)
report['candidates_checked'].append({'place_id': 'tw-098', 'name': '渭水之丘／櫻花陵園',
                                     'lat': cand[0], 'lon': cand[1],
                                     'nearest_existing': near[0], 'nearest_three': near[:3]})
report['min_distance_km']['tw-098'] = near[0]
# 5km rule check across all remaining spots (duplicate detection)
conf = []
for i in range(len(tw['spots'])):
    for j in range(i + 1, len(tw['spots'])):
        a, b = tw['spots'][i], tw['spots'][j]
        d = dist_km(a['lat'], a['lon'], b['lat'], b['lon'])
        if d < 5.0:
            conf.append((a['spot_id'], b['spot_id'], round(d, 3)))
jp = load('jp_weather.json')
jsp = jp['spots']
for i in range(len(jsp)):
    for j in range(i + 1, len(jsp)):
        a, b = jsp[i], jsp[j]
        d = dist_km(a['lat'], a['lon'], b['lat'], b['lon'])
        if d < 5.0:
            conf.append((a['spot_id'], b['spot_id'], round(d, 3)))
report['within_5km_pairs'] = conf
rep_path = ROOT / 'data/v2/audits/cl-data-25r_dedupe_report.json'
rep_path.write_bytes(dump(report).encode('utf-8'))
print('dedupe report written; within-5km pairs (pre-existing, differentiated by genre):', len(conf))
print('tw-098 vs tw-031 distance km:', round(d031, 3))
