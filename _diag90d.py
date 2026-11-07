import json, re, subprocess, os
p = 'D:/tmp/audit90.json'
d = json.load(open(p, encoding='utf-8'))
spots = sorted({m['key'].split(':')[1] for m in d['new_or_modified_debt']})
print(len(d['new_or_modified_debt']), 'regressions across', spots)
print('fields:', sorted({m['field'] for m in d['new_or_modified_debt']}))
