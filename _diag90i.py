import json
a = open('D:/tmp/cat_before.json', encoding='utf-8').read()
b = open('runtime_catalog_v004_r4_2.json', encoding='utf-8').read()
d = json.loads(a)
print('equal parsed:', json.loads(a) == json.loads(b))
print('a has CRLF:', '\r\n' in a, 'b has CRLF:', '\r\n' in b)
print('a repr start:', repr(a[:40]))
print('b repr start:', repr(b[:40]))
print('roundtrip same as a:', json.dumps(d, ensure_ascii=False, indent=1) + "\n" == a)
