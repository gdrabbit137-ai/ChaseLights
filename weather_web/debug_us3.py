"""Debug US PHOTO_TIPS"""
from app import app, PHOTO_TIPS, get_time_aware_tip, extract_hr
print(f"Grand Canyon in PHOTO_TIPS: {'Grand Canyon' in PHOTO_TIPS}")
if 'Grand Canyon' in PHOTO_TIPS:
    print(f"Tip: {PHOTO_TIPS['Grand Canyon']}")

# Test get_time_aware_tip directly
result = get_time_aware_tip("Grand Canyon", 5, 19, 6)
print(f"get_time_aware_tip result: '{result}'")

# Test with API
with app.test_client() as c:
    resp = c.get('/api/best-spots?region=us')
    d = resp.get_json()
    if d['today']:
        s = d['today'][0]
        print(f"\nFirst US spot: {s['name']}")
        print(f"  tip_today: '{s.get('tip_today','EMPTY')}'")
        print(f"  tip_tomorrow: '{s.get('tip_tomorrow','EMPTY')}'")
        info = s.get('today', {})
        print(f"  best_time: {info.get('best_time','')}")
        print(f"  sunrise: {info.get('sunrise','')}")
        b = extract_hr(info.get('best_time'))
        sr = extract_hr(info.get('sunrise'))
        print(f"  best_hour={b}, sunrise_h={sr}")
    else:
        print("No US spots available today")
print("Done!")