"""Debug US cache dates"""
import json, os
from datetime import datetime

cache_file = os.path.join(os.path.dirname(__file__), ".cache", "forecast_us.json")
with open(cache_file, "r") as f:
    data = json.load(f)

points = [p for p in data["points"] if p["type"] == "spot"]
print(f"US spots in cache: {len(points)}")
if points:
    p = points[0]
    h = p["hourly"]
    times = h.get("time", [])
    print(f"First spot '{p.get('name')}': {len(times)} hourly slots")
    print(f"Time range: {times[0]} to {times[-1]}")
    days = sorted(set(t[:10] for t in times))
    print(f"Days: {days}")
    
    # All hourly keys
    print(f"Hourly keys: {list(h.keys())}")
    
    # check daily
    d = p.get("daily", {})
    print(f"Daily keys: {list(d.keys())}")
    print(f"Daily times: {d.get('time', [])}")

# Count spots by day
print(f"\nTotal spot points: {len(points)}")
print(f"Total all points: {len(data['points'])}")

import sys
sys.path.insert(0, os.path.dirname(__file__))
from app import score_spot_for_photography

# Test all spots
today_str = "2026-09-13"
spots_with_today = 0
for p in points:
    s = score_spot_for_photography(p.get("hourly",{}), p.get("daily",{}), p.get("name",""))
    if s and s.get("today") and s["today"].get("score",0) > 0:
        spots_with_today += 1
    elif s:
        # Check why no score
        info = s.get("today")
        if info:
            print(f"  {p.get('name','?'):25s} score={info.get('score',0)}")
        else:
            # No hourly data for today
            h = p.get("hourly",{})
            times = h.get("time",[])
            if times:
                todays = [t for t in times if t.startswith(today_str)]
                print(f"  {p.get('name','?'):25s} no today data, hours for {today_str}: {len(todays)}")
            else:
                print(f"  {p.get('name','?'):25s} no hourly data at all")

print(f"\nSpots with today score > 0: {spots_with_today} / {len(points)}")