"""Check US and AK cache data"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, TW
from datetime import datetime, timedelta

now = datetime.now(TW)
today_str = now.strftime("%Y-%m-%d")
print(f"Server time (TW): {now}")
print(f"Today: {today_str}")

for region in ["us", "ak"]:
    with app.test_client() as c:
        resp = c.get(f'/api/best-spots?region={region}')
        data = resp.get_json()
        print(f"\n=== {region.upper()} ===")
        print(f"Today spots: {len(data['today'])}")
        print(f"Tomorrow spots: {len(data['tomorrow'])}")
        if data['today']:
            for s in data['today'][:5]:
                info = s['today']
                print(f"  {info['score']:3d} | {s['name']:25s} | {info.get('best_time',''):20s} | {info.get('best_genre','')}")
        elif resp.status_code != 200:
            print(f"  API error: {resp.status_code}")
        else:
            # No spots - check first spot's hourly data
            cache = __import__('app').get_cached_forecast(region)
            spots = [p for p in cache['points'] if p['type'] == 'spot']
            if spots:
                p = spots[0]
                h = p['hourly']
                times = h.get('time', [])
                days = sorted(set(t[:10] for t in times))
                print(f"  First spot: {p.get('name')}")
                print(f"  Hourly time range: {times[0]} to {times[-1]}")
                print(f"  Days in data: {days}")
                print(f"  Looking for: {today_str}")
                todays = [t for t in times if t.startswith(today_str)]
                print(f"  Matches for '{today_str}': {len(todays)}")
print("Done!")