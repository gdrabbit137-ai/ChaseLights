"""Test Flask route directly - take 2"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from app import app

with app.test_client() as c:
    resp = c.get('/api/best-spots?region=tw')
    print('Status:', resp.status_code)
    if resp.status_code == 200:
        import json
        data = resp.get_json()
        print('Today:', len(data.get('today', [])), 'spots')
        for s in data['today'][:10]:
            print(f"  {s['name']}: {s['today']['score']} - {s['today'].get('best_genre','')}")
        print(f"\nTomorrow: {len(data.get('tomorrow', []))} spots")
        print(f"Day after: {len(data.get('dayafter', []))} spots")
    else:
        print('Error body:', resp.data[:2000].decode('utf-8', errors='replace'))
    print('Done!')