import json
d = json.load(open('tw_weather.json', encoding='utf-8'))
for sp in d['spots']:
    if sp['spot_id'] == 'tw-086':
        op = sp['opportunities'][0]
        print({k: op[k] for k in op if 'i18n' in k or k in ('name_zh', 'best_time')})
        break
d = json.load(open('jp_weather.json', encoding='utf-8'))
for sp in d['spots']:
    if sp['spot_id'] == 'jp-037':
        op = sp['opportunities'][0]
        print('jp-037:', {k: op[k] for k in op if 'i18n' in k or k in ('name_zh', 'best_time')})
        break
