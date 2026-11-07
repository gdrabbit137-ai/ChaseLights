import json, sys
cat = json.load(open('runtime_catalog_v004_r4_2.json', encoding='utf-8'))
for sp in cat['spots']:
    if sp['spot_id'] in ('jp-037', 'tw-087', 'jp-001'):
        for op in sp.get('opportunities', [])[:1]:
            print(sp['spot_id'], {k: op[k] for k in op if 'i18n' in k or k in ('name_zh', 'best_time')})
