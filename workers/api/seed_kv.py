import json, subprocess, os, tempfile
from pathlib import Path
d = json.load(open('/tmp/distilled.json'))
NS = '330ba59f50bc47e7b5aef11d7da059c6'
def wr(key, value):
    f = tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8')
    f.write(value); f.close()
    path = Path(f.name).as_posix()
    r = subprocess.run(['npx', 'wrangler', 'kv', 'key', 'put', key, '--path', path,
                        f'--namespace-id={NS}', '--remote'],
                       capture_output=True, text=True, shell=True)
    os.unlink(f.name)
    if r.returncode != 0:
        print('FAIL', key, r.stderr[-200:]); return False
    return True
ok = wr('v1:evals:index', json.dumps(d['index'], ensure_ascii=False, separators=(',', ':')))
n = 0
for pid, rec in d['places'].items():
    n += 1
    if n > 50: break
    ok += wr(f'v1:evals:{pid}', json.dumps(rec, ensure_ascii=False, separators=(',', ':')))
print('uploaded keys:', ok)
