"""Check 雪山北峰 in cache"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from app import app

with app.test_client() as c:
    resp = c.get('/api/forecast?region=tw')
    data = resp.get_json()
    spots = [p for p in data['points'] if p['type'] == 'spot']
    names = [p['name'] for p in spots]
    print(f"Total spots: {len(spots)}")
    print(f"雪山北峰 in list: {'雪山北峰' in names}")
    if not names:
        print("NO SPOTS FOUND!")
    else:
        print(f"First 10: {names[:10]}")
    
    # Also check if the API returns it in best-spots
    resp2 = c.get('/api/best-spots?region=tw')
    data2 = resp2.get_json()
    today_names = [s['name'] for s in data2.get('today', [])]
    print(f"\nToday top spots ({len(data2.get('today',[]))}):")
    print(f"雪山北峰 in today: {'雪山北峰' in today_names}")
    for s in data2.get('today', [])[:5]:
        info = s.get('today', {})
        print(f"  {info.get('score','?'):3s} | {s['name']}")