import json
for tag, path in (('25', 'D:/tmp/cat25.json'), ('25R', 'D:/tmp/cat25r.json'), ('main-wt', 'runtime_catalog_v004_r4_2.json')):
    cat = json.load(open(path, encoding='utf-8'))
    for sp in cat['spots']:
        if sp['spot_id'] in ('jp-037', 'tw-087'):
            for op in sp['opportunities'][:1]:
                print(tag, sp['spot_id'], 'name_zh=', op.get('name_zh'), 'name_i18n=', op.get('name_i18n'), 'best_time=', op.get('best_time'), 'best_time_i18n=', op.get('best_time_i18n'))
