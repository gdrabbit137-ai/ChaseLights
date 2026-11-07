#!/usr/bin/env python3
"""CL-DATA-25R regions.py rollback (corrected): remove the 5 v2-rejected CL-DATA-25 spots."""
import re
from pathlib import Path

ROOT = Path(r'D:/tmp/cl-data-25r')
REMOVE = {'jp-050': '安比高原雲海ゴンドラ', 'tw-090': '加路蘭海岸遊憩區',
          'tw-092': '北關海潮公園', 'tw-096': '半天寮好望角', 'tw-097': '擎天崗草原'}
zh = [re.escape(n) for n in REMOVE.values()]
rp = ROOT / 'regions.py'
text = rp.read_bytes().decode('utf-8').replace('\r\n', '\n')
out, skip = [], 0
for ln in text.split('\n'):
    if skip:
        # SPOT_OVERRIDES entry is exactly 5 lines: opener + 4 body lines (last ends with '},')
        skip -= 1
        continue
    if re.match(r'\s*"(?:%s)": \[' % '|'.join(REMOVE), ln):
        continue  # admin area entry
    if re.match(r'\s*\(\d+\.\d+, \d+\.\d+, "(?:%s)"' % '|'.join(zh), ln):
        continue  # spot tuple
    if re.match(r'\s*"(?:%s)": \d+,\s*$' % '|'.join(zh), ln):
        continue  # elevation entry
    if re.match(r'\s*"(?:%s)": \{' % '|'.join(zh), ln):
        skip = 4  # opener + 4 following lines
        continue
    out.append(ln)
text2 = '\n'.join(out)
for name in REMOVE.values():
    assert name not in text2, name
for pid in REMOVE:
    assert pid not in text2, pid
rp.write_bytes(text2.encode('utf-8'))
print('regions.py rollback OK; lines removed OK')
