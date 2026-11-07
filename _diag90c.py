import json
cat = json.load(open('runtime_catalog_v004_r4_2.json', encoding='utf-8'))
n = 0
for sp in cat['spots']:
    for op in sp['opportunities']:
        if isinstance(op.get('best_time_i18n'), dict) and op['best_time_i18n']:
            print(sp['spot_id'], op['opportunity_id'], 'best_time=', op.get('best_time'), '->', op['best_time_i18n'])
            n += 1
            if n >= 5:
                raise SystemExit
print('total with best_time_i18n:', n)
