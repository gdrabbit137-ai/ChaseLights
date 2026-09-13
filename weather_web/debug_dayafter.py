"""Debug dayafter scoring"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, get_cached_forecast, score_spot_for_photography, TW
from datetime import datetime, timedelta

region = "tw"
data = get_cached_forecast(region)
now = datetime.now(TW)
dayafter_str = (now + timedelta(days=2)).strftime("%Y-%m-%d")
print(f"Today: {now.strftime('%Y-%m-%d')}")
print(f"Day after: {dayafter_str}")
print(f"Total points: {len(data['points'])}")
print(f"First spot hourly times (first 3 + last 3):")

spots = [p for p in data["points"] if p["type"] == "spot"]
print(f"Spots: {len(spots)}")

# Check first spot
p = spots[0]
hourly = p.get("hourly", {})
times = hourly.get("time", [])
print(f"\nFirst spot '{p.get('name')}': {len(times)} hourly slots")
print(f"Time range: {times[0]} to {times[-1]}")

# Count how many days
days_seen = set()
for t in times:
    days_seen.add(t[:10])
print(f"Days in data: {sorted(days_seen)}")

# Check if dayafter data exists
dayafter_indices = [i for i, t in enumerate(times) if t.startswith(dayafter_str)]
print(f"Dayafter indices: {len(dayafter_indices)}")

# Test scoring
daily = p.get("daily", {})
print(f"Daily keys: {list(daily.keys())}")
if "time" in daily:
    print(f"Daily times: {daily['time']}")
    print(f"Daily sunrise: {daily.get('sunrise', [])}")
    print(f"Daily sunset: {daily.get('sunset', [])}")

# Score
s = score_spot_for_photography(hourly, daily, p.get("name", ""))
if s:
    print(f"\nScored: today={s.get('today',{}).get('score','N/A')}, "
          f"tomorrow={s.get('tomorrow',{}).get('score','N/A')}, "
          f"dayafter={s.get('dayafter',{}).get('score','N/A')}")
else:
    print("No score returned")

# Test API
with app.test_client() as c:
    resp = c.get('/api/best-spots?region=tw')
    data = resp.get_json()
    print(f"\nAPI - today: {len(data['today'])}, tomorrow: {len(data['tomorrow'])}, dayafter: {len(data['dayafter'])}")
    
print("Done!")