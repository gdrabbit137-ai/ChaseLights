import json
d = json.load(open('jp_weather.json', encoding='utf-8'))
for sp in d['spots']:
    if sp['spot_id'] in ('jp-037', 'jp-001'):
        print(sp['spot_id'], 'admin_areas=', sp.get('admin_areas'), 'keys sample:', 'name_i18n' in sp)
