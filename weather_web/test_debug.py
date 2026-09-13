"""Quick debug: test score_spot_for_photography directly"""
import json, os, sys, traceback

# Setup paths
sys.path.insert(0, os.path.dirname(__file__))
from regions import REGIONS

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
cache_file = os.path.join(CACHE_DIR, "forecast_tw.json")

if not os.path.exists(cache_file):
    print(f"Cache file not found: {cache_file}")
    sys.exit(1)

with open(cache_file, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Loaded {len(data.get('points', []))} points")
print(f"Keys in data: {list(data.keys())}")

# Import the score function
from app import score_spot_for_photography, classify_scene, get_genre_label

# Test with first spot
spots = [p for p in data.get("points", []) if p.get("type") == "spot"]
print(f"\nFound {len(spots)} spots")

if spots:
    for spot in spots[:3]:
        name = spot.get("name", "?")
        hourly = spot.get("hourly", {})
        daily = spot.get("daily", {})
        print(f"\n--- Testing: {name} ---")
        print(f"  Hourly keys: {list(hourly.keys())}")
        print(f"  Daily keys: {list(daily.keys())}")
        if "sunrise" in daily:
            print(f"  Sunrise: {daily['sunrise']}")
            print(f"  Sunset: {daily['sunset']}")
        
        try:
            result = score_spot_for_photography(hourly, daily, name)
            print(f"  Result: {json.dumps(result, ensure_ascii=False, default=str)[:500]}")
        except Exception as e:
            print(f"  ERROR: {e}")
            traceback.print_exc()

print("\nDone!")