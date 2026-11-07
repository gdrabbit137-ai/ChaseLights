import json
cat = json.load(open('runtime_catalog_v004_r4_2.json', encoding='utf-8'))
ids = {sp['spot_id'] for sp in cat['spots']}
for sid in ('jp-050', 'tw-090', 'tw-092', 'tw-096', 'tw-097'):
    sps = [sp for sp in cat['spots'] if sp['spot_id'] == sid]
    if not sps:
        print(sid, 'ABSENT from catalog')
        continue
    for op in sps[0]['opportunities']:
        print(sid, op['opportunity_id'], 'name_zh=', op.get('name_zh'), 'best_time=', op.get('best_time'), 'name_i18n=', bool(op.get('name_i18n')), 'bt_i18n=', bool(op.get('best_time_i18n')))
