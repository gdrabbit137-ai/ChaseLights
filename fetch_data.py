import json
import urllib.request
import os
from datetime import datetime, timezone, timedelta
from bisect import bisect_right
from zoneinfo import ZoneInfo

# 後端多國語言狀態與指標字典
I18N_MESSAGES = {
    # 狀態 (Status)
    "MOUNTAIN_EXCELLENT_DAY": {"zh-TW": "☀️ 山景展望極佳", "en": "☀️ Excellent Mountain View", "ja": "☀️ 最高の山岳展望"},
    "MOUNTAIN_STABLE_DAY": {"zh-TW": "⛅ 山景氣象平穩", "en": "⛅ Stable Mountain Weather", "ja": "⛅ 安定した山岳気象"},
    "MOUNTAIN_FOG_DAY": {"zh-TW": "☁️ 山區濃霧雲覆", "en": "☁️ Heavy Fog / Clouds", "ja": "☁️ 山間部の濃霧・雲覆"},
    "MOUNTAIN_EXCELLENT_NIGHT": {"zh-TW": "🌙 夜間大氣清透", "en": "🌙 Clear Night Sky", "ja": "🌙 清透な夜間大気"},
    "MOUNTAIN_STABLE_NIGHT": {"zh-TW": "🌙 夜間氣象平穩", "en": "🌙 Stable Night Weather", "ja": "🌙 穏やかな夜間気象"},
    "MOUNTAIN_FOG_NIGHT": {"zh-TW": "☁️ 夜間濃霧雲覆", "en": "☁️ Night Fog / Clouds", "ja": "☁️ 夜間の濃霧・雲覆"},
    "CLOUD_SEA_GOLD": {"zh-TW": "☁️ 翻騰雲海黃金期", "en": "☁️ Prime Sea of Clouds", "ja": "☁️ 黄金の雲海期"},
    "CLOUD_SEA_FAIR": {"zh-TW": "⛅ 雲霧條件普通", "en": "⛅ Moderate Cloud & Fog", "ja": "⛅ 普通の雲霧条件"},
    "CLOUD_SEA_DRY": {"zh-TW": "☀️ 乾燥無雲海條件", "en": "☀️ Dry / No Sea of Clouds", "ja": "☀️ 乾燥・雲海条件なし"},
    "FOREST_MIST": {"zh-TW": "🌫️ 夢幻迷霧森林", "en": "🌫️ Mystical Mist Forest", "ja": "🌫️ 幻想的な霧の森林"},
    "FOREST_LIGHT": {"zh-TW": "☀️ 森林斜射光極佳", "en": "☀️ Great Forest Sunbeams", "ja": "☀️ 最高の光線・木漏れ日"},
    "FOREST_NORMAL": {"zh-TW": "🌲 森林一般氣象", "en": "🌲 Normal Forest Weather", "ja": "🌲 通常の森林気象"},
    "LAKE_MIST": {"zh-TW": "🌫️ 湖面夢幻晨霧", "en": "🌫️ Misty Lake Morning", "ja": "🌫️ 幻想的な湖畔の朝霧"},
    "LAKE_MIRROR": {"zh-TW": "🪞 靜止鏡面倒影", "en": "🪞 Mirror Reflection", "ja": "🪞 鏡面の水面倒影"},
    "LAKE_GOOD": {"zh-TW": "🌊 湖景條件良好", "en": "🌊 Good Lake Conditions", "ja": "🌊 良好な湖畔条件"},
    "LAKE_WINDY": {"zh-TW": "🌬️ 湖面風大波浪興起", "en": "🌬️ Windy Lake / Waves", "ja": "🌬️ 強風による波立ち"},
    "WATERFALL_SOFT": {"zh-TW": "🌊 瀑布漫射柔光", "en": "🌊 Soft Light Waterfall", "ja": "🌊 拡散光の滝景"},
    "WATERFALL_HARSH": {"zh-TW": "☀️ 頂光強烈反差大", "en": "☀️ Harsh Direct Sunlight", "ja": "☀️ 強い直射光・高コントラスト"},
    "WATERFALL_NORMAL": {"zh-TW": "💦 瀑布條件平穩", "en": "💦 Stable Waterfall Weather", "ja": "💦 安定した滝条件"},
    "COAST_GLOW": {"zh-TW": "🌅 暮光彩霞絕佳", "en": "🌅 Stunning Sunset Glow", "ja": "🌅 素晴らしい夕焼け"},
    "COAST_LOW_CLOUD": {"zh-TW": "☁️ 海面低雲壓頂", "en": "☁️ Low Coastal Clouds", "ja": "☁️ 沿岸の低雲覆蓋"},
    "COAST_NORMAL": {"zh-TW": "🌊 海景氣象常規", "en": "🌊 Normal Coastal Weather", "ja": "🌊 通常の沿岸気象"},
    "CITY_NIGHT_CLEAR": {"zh-TW": "🏙️ 璀璨夜景通透", "en": "🏙️ Clear City Night View", "ja": "🏙️ 清晰な都市夜景"},
    "CITY_NIGHT_FAIR": {"zh-TW": "🌃 夜景條件普通", "en": "🌃 Fair City Night View", "ja": "🌃 普通の夜景条件"},
    "CITY_NIGHT_POOR": {"zh-TW": "☁️ 夜景視線受阻", "en": "☁️ Obstructed Night View", "ja": "☁️ 視界不順の夜景"},
    "CITY_DAY_CLEAR": {"zh-TW": "🏙️ 城市遠眺極佳", "en": "🏙️ Excellent City Panorama", "ja": "🏙️ 最高の都市遠望"},
    "CITY_DAY_FAIR": {"zh-TW": "🏙️ 城市景觀普通", "en": "🏙️ Normal City View", "ja": "🏙️ 普通の都市景觀"},
    "CITY_DAY_POOR": {"zh-TW": "🌫️ 城市視線受阻", "en": "🌫️ Obstructed City View", "ja": "🌫️ 視界不順の都市景觀"},
    "STARLIGHT_GREAT": {"zh-TW": "🌌 銀河觀星極佳", "en": "🌌 Excellent Stargazing", "ja": "🌌 最高の星空・天の川"},
    "STARLIGHT_FAIR": {"zh-TW": "✨ 星空條件普通", "en": "✨ Moderate Stargazing", "ja": "✨ 普通の星空条件"},
    "STARLIGHT_POOR": {"zh-TW": "☁️ 雲層過厚無視線", "en": "☁️ Heavy Cloud Cover", "ja": "☁️ 厚い雲（視界不可）"},
    "AURORA_CLEAR": {"zh-TW": "🌌 夜間極光視野清透", "en": "🌌 Clear Aurora View", "ja": "🌌 清透なオーロラ視界"},
    "AURORA_FAIR": {"zh-TW": "🌌 極光觀察條件普通", "en": "🌌 Fair Aurora Conditions", "ja": "🌌 普通のオーロラ条件"},
    "AURORA_POOR": {"zh-TW": "☁️ 雲層過厚無視線", "en": "☁️ Heavy Cloud Cover", "ja": "☁️ 厚い雲（視界不可）"},
    "DAYLIGHT_ONLY": {"zh-TW": "☀️ 白天日光強烈", "en": "☀️ Bright Daylight", "ja": "☀️ 強烈な日光（昼間）"},
    "RAIN_RISK": {"zh-TW": "🌧️ 降雨風險高", "en": "🌧️ High Rain Risk", "ja": "🌧️ 高い降雨リスク"},
    "STABLE_WEATHER": {"zh-TW": "⛅ 氣象平穩", "en": "⛅ Stable Weather", "ja": "⛅ 安定した気象"},

    # 關鍵指標 (Indicator)
    "IND_PEAKS": {"zh-TW": "🏔️ 遠眺群峰通透無瑕", "en": "Clear View of Distant Peaks", "ja": "遠くの連峰まで超高透明度"},
    "IND_CLEAR_SKY": {"zh-TW": "💎 零雲量大氣極通透", "en": "💎 Clear Sky & High Visibility", "ja": "💎 快晴・極めて高い透明度"},
    "IND_SOME_CLOUDS": {"zh-TW": "⛅ 些許薄雲干擾", "en": "⛅ Slight Cloud Interference", "ja": "⛅ 薄雲による僅かな影響"},
    "IND_NO_STAR": {"zh-TW": "☁️ 不宜觀星攝影", "en": "☁️ Not Suitable for Stargazing", "ja": "☁️ 星空撮影に不適"},
    "IND_CLOUD_SEA": {"zh-TW": "☁️ 水氣與低雲完美配合", "en": "☁️ Perfect Moisture & Low Clouds", "ja": "☁️ 水蒸気と低雲の最適な調和"},
    "IND_CLOUD_SEA_SUB": {"zh-TW": "⛅ 低雲高度或雲量稍偏", "en": "⛅ Suboptimal Cloud Height/Amount", "ja": "⛅ 雲量または高度がやや偏斜"},
    "IND_DRY_AIR": {"zh-TW": "☀️ 大氣乾燥或無低雲", "en": "☀️ Dry Air / No Low Clouds", "ja": "☀️ 乾燥大氣・低雲なし"},
    "IND_FOREST_MIST": {"zh-TW": "🌲 濃郁霧氣瀰漫林間", "en": "🌲 Dense Mist Through Forest", "ja": "🌲 森林に立ち込める濃霧"},
    "IND_FOREST_SUN": {"zh-TW": "🌲 大氣通透耶穌光強", "en": "🌲 Clear Air & Strong Sunbeams", "ja": "🌲 高透明度・強い木漏れ日"},
    "IND_FOREST_NORM": {"zh-TW": "🌲 無特別霧氣或強光", "en": "🌲 Regular Forest Lighting", "ja": "🌲 特段の霧や強光なし"},
    "IND_LAKE_MIST": {"zh-TW": "🌊 湖面水氣飄渺極美", "en": "🌊 Ethereal Lake Mist", "ja": "🌊 湖面上に漂う幻想的な朝霧"},
    "IND_LAKE_MIRROR": {"zh-TW": "🌊 無風微波鏡面絕佳", "en": "🌊 Calm Water & Perfect Reflection", "ja": "🌊 無風・鏡面の絶景"},
    "IND_LAKE_GOOD": {"zh-TW": "🌊 風速微弱適合拍攝", "en": "🌊 Gentle Wind / Good Shooting", "ja": "🌊 微風・撮影に最適"},
    "IND_LAKE_WIND": {"zh-TW": "🌊 風速過強無倒影", "en": "🌊 High Winds / No Reflection", "ja": "🌊 強風・倒影なし"},
    "IND_WATERFALL_SOFT": {"zh-TW": "💦 陰天無強光高反差", "en": "💦 Overcast / Soft Lighting", "ja": "💦 曇天・拡散光で撮影好適"},
    "IND_WATERFALL_HARSH": {"zh-TW": "☀️ 陽光過強對比過高", "en": "☀️ Harsh Sunlight / High Contrast", "ja": "☀️ 直射日光・高コントラスト"},
    "IND_WATERFALL_NORM": {"zh-TW": "💦 水流與光線良好", "en": "💦 Good Water Flow & Lighting", "ja": "💦 水流と光の條件良好"},
    "IND_COAST_GLOW": {"zh-TW": "🌅 中高雲形成壯麗彩霞", "en": "🌅 Sunset Glow with Mid/High Clouds", "ja": "🌅 中高層雲による見事な夕焼け"},
    "IND_COAST_BLOCK": {"zh-TW": "☁️ 遮蔽地平線視線", "en": "☁️ Obstructed Horizon View", "ja": "☁️ 地平線視界の遮蔽"},
    "IND_COAST_NORM": {"zh-TW": "🌊 大氣狀況平穩", "en": "🌊 Stable Atmospheric Conditions", "ja": "🌊 安定した大気状態"},
    "IND_CITY_NIGHT_CLEAR": {"zh-TW": "💎 城市燈火清晰無霧", "en": "💎 Clear City Lights", "ja": "💎 霧なし・クリアな街の灯り"},
    "IND_CITY_NIGHT_HAZE": {"zh-TW": "⛅ 些許霧氣或輕微低雲", "en": "⛅ Slight Haze / Low Clouds", "ja": "⛅ 僅かな霧または低雲"},
    "IND_CITY_NIGHT_BLOCK": {"zh-TW": "☁️ 低雲壓頂或濃霧", "en": "☁️ Low Clouds / Dense Fog", "ja": "☁️ 低雲または濃霧覆蓋"},
    "IND_CITY_DAY_CLEAR": {"zh-TW": "💎 城市全景清晰通透", "en": "💎 Crystal Clear City Panorama", "ja": "💎 クリアな都市パノラマ"},
    "IND_CITY_DAY_FAIR": {"zh-TW": "⛅ 大氣能見度平穩", "en": "⛅ Fair Atmospheric Visibility", "ja": "⛅ 安定した視程"},
    "IND_CITY_DAY_HAZE": {"zh-TW": "🌫️ 霾害或能見度差", "en": "🌫️ Haze or Poor Visibility", "ja": "🌫️ 煙霧または不鮮明な視程"},
    "IND_NIGHT_CLEAR": {"zh-TW": "🌌 高空無視線阻礙", "en": "🌌 Clear High-Altitude View", "ja": "🌌 上空の視界良好"},
    "IND_RAIN_RISK": {"zh-TW": "🌧️ 雨勢明顯不宜外拍", "en": "🌧️ Significant Rain / Avoid Shooting", "ja": "🌧️ 明らかな雨・屋外撮影不適"},
    "IND_DEFAULT": {"zh-TW": "✅ 風和日麗良好", "en": "✅ Good Weather Conditions", "ja": "✅ 良好な天候"}
}

def get_text(key, lang="zh-TW"):
    return I18N_MESSAGES.get(key, {}).get(lang, I18N_MESSAGES.get(key, {}).get("zh-TW", ""))


_NOAA_KP_CACHE = None
_WEATHER_RESPONSE_CACHE = {}


def _request_json(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": "ChaseLights/2.0 (+weather photography)"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_noaa_kp_series(force=False):
    """Return NOAA 3-hour planetary Kp rows with UTC-aware datetimes.

    The NOAA product mixes observed / estimated / predicted rows.  Keeping the
    source on each row prevents a predicted Kp from being presented as an
    observation in the UI.
    """
    global _NOAA_KP_CACHE
    if _NOAA_KP_CACHE is not None and not force:
        return _NOAA_KP_CACHE

    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json"
    try:
        data = _request_json(url)
        rows = []
        start = 1 if data and isinstance(data[0], list) and data[0] and str(data[0][0]).lower() == "time_tag" else 0
        for row in data[start:]:
            if not isinstance(row, list) or len(row) < 2:
                continue
            try:
                dt = datetime.strptime(str(row[0]), "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc)
            except ValueError:
                try:
                    dt = datetime.fromisoformat(str(row[0]).replace("Z", "+00:00"))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    else:
                        dt = dt.astimezone(timezone.utc)
                except Exception:
                    continue
            try:
                kp = float(row[1])
            except (TypeError, ValueError):
                continue
            rows.append({
                "time": dt,
                "kp": kp,
                "source": str(row[2]).lower() if len(row) > 2 and row[2] else "unknown",
                "noaa_scale": row[3] if len(row) > 3 else None,
            })
        rows.sort(key=lambda x: x["time"])
        _NOAA_KP_CACHE = rows
        return rows
    except Exception as e:
        print(f"Failed to fetch NOAA Kp forecast: {e}")
        _NOAA_KP_CACHE = []
        return []


def fetch_noaa_kp():
    """Backward-compatible latest Kp helper."""
    rows = fetch_noaa_kp_series()
    if not rows:
        return None
    now = datetime.now(timezone.utc)
    past_rows = [r for r in rows if r["time"] <= now and r["source"] in {"observed", "estimated"}]
    row = past_rows[-1] if past_rows else min(rows, key=lambda r: abs((r["time"] - now).total_seconds()))
    return {"kp_index": row["kp"], "time": row["time"].isoformat(), "source": row["source"]}


def _kp_for_time(target_utc, kp_rows):
    if not kp_rows:
        return None, "unavailable"
    times = [r["time"] for r in kp_rows]
    idx = bisect_right(times, target_utc) - 1
    candidates = []
    if 0 <= idx < len(kp_rows):
        candidates.append(kp_rows[idx])
    if idx + 1 < len(kp_rows):
        candidates.append(kp_rows[idx + 1])
    if not candidates:
        return None, "unavailable"
    row = min(candidates, key=lambda r: abs((r["time"] - target_utc).total_seconds()))
    if abs((row["time"] - target_utc).total_seconds()) > 4 * 3600:
        return None, "unavailable"
    return row["kp"], row["source"]


def _parse_unix_list(values):
    result = []
    for value in values or []:
        try:
            result.append(datetime.fromtimestamp(int(value), timezone.utc))
        except Exception:
            result.append(None)
    return result


def _twilight_dates(raw, tz):
    daily = raw.get("daily", {}) or {}
    sunrise_utc = _parse_unix_list(daily.get("sunrise", []))
    sunset_utc = _parse_unix_list(daily.get("sunset", []))
    lookup = {}
    for rise, setting in zip(sunrise_utc, sunset_utc):
        if rise is None or setting is None:
            continue
        rise_local = rise.astimezone(tz)
        set_local = setting.astimezone(tz)
        lookup[rise_local.date().isoformat()] = (rise_local, set_local)
    return lookup



def _near_twilight(local_dt, twilight_lookup, minutes=90):
    pair = twilight_lookup.get(local_dt.date().isoformat())
    if not pair:
        return False
    sunrise, sunset = pair
    return min(abs((local_dt - sunrise).total_seconds()), abs((local_dt - sunset).total_seconds())) <= minutes * 60


# ---------------------------------------------------------------------------
# Astronomy helpers (low-cost, dependency-free approximations suitable for
# photography planning; not intended for navigation or scientific astrometry)
# ---------------------------------------------------------------------------
def _norm_deg(value):
    return float(value) % 360.0


def _angle_diff(a, b):
    return abs((float(a) - float(b) + 180.0) % 360.0 - 180.0)


def _julian_day(dt):
    return dt.astimezone(timezone.utc).timestamp() / 86400.0 + 2440587.5


def _gmst_deg(dt):
    jd = _julian_day(dt)
    t = (jd - 2451545.0) / 36525.0
    return _norm_deg(
        280.46061837
        + 360.98564736629 * (jd - 2451545.0)
        + 0.000387933 * t * t
        - (t * t * t) / 38710000.0
    )


def _radec_to_altaz(ra_deg, dec_deg, dt, lat_deg, lon_deg):
    import math
    lat = math.radians(float(lat_deg))
    dec = math.radians(float(dec_deg))
    hour_angle = math.radians((_gmst_deg(dt) + float(lon_deg) - float(ra_deg) + 540.0) % 360.0 - 180.0)

    sin_alt = math.sin(dec) * math.sin(lat) + math.cos(dec) * math.cos(lat) * math.cos(hour_angle)
    alt = math.asin(max(-1.0, min(1.0, sin_alt)))
    # Azimuth: 0=N, 90=E, 180=S, 270=W
    y = -math.sin(hour_angle) * math.cos(dec)
    x = math.sin(dec) * math.cos(lat) - math.cos(dec) * math.sin(lat) * math.cos(hour_angle)
    az = math.atan2(y, x)
    return _norm_deg(math.degrees(az)), math.degrees(alt)


def _sun_radec(dt):
    import math
    n = _julian_day(dt) - 2451545.0
    L = _norm_deg(280.460 + 0.9856474 * n)
    g = math.radians(_norm_deg(357.528 + 0.9856003 * n))
    ecl_lon = math.radians(_norm_deg(L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)))
    obliq = math.radians(23.439 - 0.0000004 * n)
    ra = math.atan2(math.cos(obliq) * math.sin(ecl_lon), math.cos(ecl_lon))
    dec = math.asin(math.sin(obliq) * math.sin(ecl_lon))
    return _norm_deg(math.degrees(ra)), math.degrees(dec)


def _sun_position(dt, lat, lon):
    ra, dec = _sun_radec(dt)
    az, alt = _radec_to_altaz(ra, dec, dt, lat, lon)
    return {"azimuth": round(az, 1), "elevation": round(alt, 1)}


def _moon_radec(dt):
    """Approximate lunar RA/Dec from classical orbital elements.

    Accuracy is normally within a few degrees, adequate for showing whether the
    Moon is above the horizon and estimating its direction for photo planning.
    """
    import math
    d = _julian_day(dt) - 2451543.5
    N = math.radians(_norm_deg(125.1228 - 0.0529538083 * d))
    inc = math.radians(5.1454)
    w = math.radians(_norm_deg(318.0634 + 0.1643573223 * d))
    a = 60.2666
    e = 0.054900
    M = math.radians(_norm_deg(115.3654 + 13.0649929509 * d))
    E = M + e * math.sin(M) * (1.0 + e * math.cos(M))
    for _ in range(3):
        E = E - (E - e * math.sin(E) - M) / (1.0 - e * math.cos(E))
    xv = a * (math.cos(E) - e)
    yv = a * math.sqrt(1.0 - e * e) * math.sin(E)
    v = math.atan2(yv, xv)
    r = math.sqrt(xv * xv + yv * yv)
    lon_ecl = v + w
    xh = r * (math.cos(N) * math.cos(lon_ecl) - math.sin(N) * math.sin(lon_ecl) * math.cos(inc))
    yh = r * (math.sin(N) * math.cos(lon_ecl) + math.cos(N) * math.sin(lon_ecl) * math.cos(inc))
    zh = r * math.sin(lon_ecl) * math.sin(inc)
    ecl = math.radians(23.4393 - 3.563e-7 * d)
    xe = xh
    ye = yh * math.cos(ecl) - zh * math.sin(ecl)
    ze = yh * math.sin(ecl) + zh * math.cos(ecl)
    ra = math.atan2(ye, xe)
    dec = math.atan2(ze, math.sqrt(xe * xe + ye * ye))
    return _norm_deg(math.degrees(ra)), math.degrees(dec)


def _angular_separation(ra1, dec1, ra2, dec2):
    import math
    r1, d1, r2, d2 = map(math.radians, [ra1, dec1, ra2, dec2])
    cos_sep = math.sin(d1) * math.sin(d2) + math.cos(d1) * math.cos(d2) * math.cos(r1 - r2)
    return math.degrees(math.acos(max(-1.0, min(1.0, cos_sep))))


def _moon_phase_name(illum, lang):
    if illum < 0.05:
        key = ("新月", "New Moon", "新月")
    elif illum < 0.35:
        key = ("眉月", "Crescent", "三日月")
    elif illum < 0.65:
        key = ("半月", "Quarter Moon", "半月")
    elif illum < 0.95:
        key = ("凸月", "Gibbous", "凸月")
    else:
        key = ("滿月", "Full Moon", "満月")
    return key[{"zh-TW": 0, "en": 1, "ja": 2}.get(lang, 0)]


def _astronomy(dt, lat, lon, lang="zh-TW"):
    sun_ra, sun_dec = _sun_radec(dt)
    sun_az, sun_alt = _radec_to_altaz(sun_ra, sun_dec, dt, lat, lon)
    moon_ra, moon_dec = _moon_radec(dt)
    moon_az, moon_alt = _radec_to_altaz(moon_ra, moon_dec, dt, lat, lon)
    elong = _angular_separation(sun_ra, sun_dec, moon_ra, moon_dec)
    illumination = (1.0 - __import__("math").cos(__import__("math").radians(elong))) / 2.0
    gc_az, gc_alt = _radec_to_altaz(266.41683, -29.00781, dt, lat, lon)
    return {
        "sun_azimuth": round(sun_az, 1),
        "sun_elevation": round(sun_alt, 1),
        "moon_azimuth": round(moon_az, 1),
        "moon_elevation": round(moon_alt, 1),
        "moon_illumination": round(illumination * 100.0, 1),
        "moon_phase": _moon_phase_name(illumination, lang),
        "galactic_core_azimuth": round(gc_az, 1),
        "galactic_core_elevation": round(gc_alt, 1),
        "astronomical_dark": sun_alt <= -18.0,
        "civil_dark": sun_alt <= -6.0,
        "galactic_core_visible": gc_alt >= 8.0 and sun_alt <= -12.0,
    }


def _factor(kind, text):
    return {"type": kind, "text": text}


def _fmt_factor(lang, key, value=None):
    templates = {
        "vis_good": {"zh-TW": "能見度 {v} km", "en": "Visibility {v} km", "ja": "視程 {v} km"},
        "vis_low": {"zh-TW": "能見度僅 {v} km", "en": "Visibility only {v} km", "ja": "視程 {v} km のみ"},
        "low_cloud": {"zh-TW": "低雲僅 {v}%", "en": "Low cloud {v}%", "ja": "下層雲 {v}%"},
        "low_cloud_high": {"zh-TW": "低雲高達 {v}%", "en": "Low cloud {v}%", "ja": "下層雲 {v}%"},
        "calm": {"zh-TW": "風速僅 {v} m/s", "en": "Wind only {v} m/s", "ja": "風速 {v} m/s"},
        "windy": {"zh-TW": "風速 {v} m/s", "en": "Wind {v} m/s", "ja": "風速 {v} m/s"},
        "dry": {"zh-TW": "降雨機率 {v}%", "en": "Rain chance {v}%", "ja": "降水確率 {v}%"},
        "rain": {"zh-TW": "降雨機率達 {v}%", "en": "Rain chance {v}%", "ja": "降水確率 {v}%"},
        "twilight": {"zh-TW": "晨昏光線進入黃金窗口", "en": "Golden/twilight light window", "ja": "朝夕のゴールデンタイム"},
        "cloud_color": {"zh-TW": "中高雲量適合彩霞", "en": "Mid/high clouds favor color", "ja": "中・上層雲が焼けやすい"},
        "astro_dark": {"zh-TW": "已進入天文黑夜", "en": "Astronomical darkness", "ja": "天文薄明終了後"},
        "not_dark": {"zh-TW": "尚未進入天文黑夜", "en": "Not astronomically dark", "ja": "まだ天文薄明中"},
        "moon_good": {"zh-TW": "月光干擾低（{v}%）", "en": "Low moonlight ({v}%)", "ja": "月光影響小（{v}%）"},
        "moon_bad": {"zh-TW": "月光干擾高（{v}%）", "en": "Strong moonlight ({v}%)", "ja": "月光影響大（{v}%）"},
        "mw_core": {"zh-TW": "銀河核心在地平線上", "en": "Galactic core above horizon", "ja": "銀河中心が地平線上"},
        "kp_good": {"zh-TW": "Kp {v} 地磁活動偏強", "en": "Kp {v} geomagnetic activity", "ja": "Kp {v} 地磁気活動"},
        "kp_low": {"zh-TW": "Kp {v} 極光活動偏弱", "en": "Kp {v} weak aurora activity", "ja": "Kp {v} オーロラ活動弱め"},
        "cloud_below": {"zh-TW": "估算雲底低於機位約 {v} m", "en": "Est. cloud base ~{v} m below camera", "ja": "推定雲底は撮影地点より約 {v} m低い"},
        "in_cloud": {"zh-TW": "估算雲底接近機位，入霧風險", "en": "Cloud base near camera; fog risk", "ja": "推定雲底が撮影地点付近・霧リスク"},
        "sun_align": {"zh-TW": "太陽方向與主要構圖吻合", "en": "Sun aligns with main composition", "ja": "太陽方向が主構図と一致"},
        "sun_miss": {"zh-TW": "太陽方向偏離主要構圖", "en": "Sun off the main composition", "ja": "太陽方向が主構図から外れる"},
    }
    text = templates.get(key, {}).get(lang) or templates.get(key, {}).get("zh-TW") or key
    return text.format(v=value) if value is not None else text


def _calibrate_score(raw_score, tag, item_data):
    """Compress routine good weather and reserve 90+ for genuinely exceptional windows."""
    raw = max(0.0, min(100.0, float(raw_score)))
    score = 50.0 + (raw - 50.0) * 0.84

    vis_km = float(item_data.get("vis", 10000) or 10000) / 1000.0
    wind = float(item_data.get("wind", 0) or 0)
    pop = float(item_data.get("pop", 0) or 0)
    low = float(item_data.get("c_low", 0) or 0)

    # Small exceptional-condition bonuses. They are intentionally limited.
    if tag in {"mountain", "city", "starlight", "aurora"} and vis_km >= 30:
        score += 2.0
    if pop <= 5:
        score += 1.0
    if wind <= 2.0:
        score += 1.5
    if tag in {"mountain", "city", "starlight", "aurora", "coast"} and low <= 8:
        score += 1.5
    if tag == "starlight" and item_data.get("astronomical_dark"):
        score += 2.0
    if tag == "starlight" and item_data.get("galactic_core_visible"):
        score += 1.5
    if tag == "coast" and item_data.get("is_twilight"):
        score += 2.0
    if tag == "cloud_sea" and item_data.get("cloud_below_camera"):
        score += 3.0

    return int(round(max(10.0, min(97.0, score))))


def _build_factors(tag, d, lang):
    plus, minus = [], []
    vis_km = round(float(d.get("vis", 0) or 0) / 1000.0, 1)
    wind = round(float(d.get("wind", 0) or 0), 1)
    pop = round(float(d.get("pop", 0) or 0))
    low = round(float(d.get("c_low", 0) or 0))

    if vis_km >= 20:
        plus.append(_factor("plus", _fmt_factor(lang, "vis_good", vis_km)))
    elif vis_km < 8 and tag not in {"forest", "lake"}:
        minus.append(_factor("minus", _fmt_factor(lang, "vis_low", vis_km)))
    if low <= 15 and tag in {"mountain", "city", "coast", "starlight", "aurora"}:
        plus.append(_factor("plus", _fmt_factor(lang, "low_cloud", low)))
    elif low >= 65 and tag in {"mountain", "city", "coast", "starlight", "aurora"}:
        minus.append(_factor("minus", _fmt_factor(lang, "low_cloud_high", low)))
    if wind <= 2.5:
        plus.append(_factor("plus", _fmt_factor(lang, "calm", wind)))
    elif wind >= 6:
        minus.append(_factor("minus", _fmt_factor(lang, "windy", wind)))
    if pop <= 10:
        plus.append(_factor("plus", _fmt_factor(lang, "dry", pop)))
    elif pop >= 40:
        minus.append(_factor("minus", _fmt_factor(lang, "rain", pop)))

    if tag == "coast":
        if d.get("is_twilight"):
            plus.insert(0, _factor("plus", _fmt_factor(lang, "twilight")))
        mid_high = float(d.get("c_mid", 0) or 0) + float(d.get("c_high", 0) or 0)
        if 20 <= mid_high <= 75 and low < 35:
            plus.append(_factor("plus", _fmt_factor(lang, "cloud_color")))
        if d.get("sun_alignment") == "good":
            plus.append(_factor("plus", _fmt_factor(lang, "sun_align")))
        elif d.get("sun_alignment") == "poor":
            minus.append(_factor("minus", _fmt_factor(lang, "sun_miss")))
    elif tag == "starlight":
        if d.get("astronomical_dark"):
            plus.insert(0, _factor("plus", _fmt_factor(lang, "astro_dark")))
        else:
            minus.insert(0, _factor("minus", _fmt_factor(lang, "not_dark")))
        moon_illum = round(float(d.get("moon_illumination", 0) or 0))
        moon_alt = float(d.get("moon_elevation", -90) or -90)
        if moon_alt <= 0 or moon_illum <= 25:
            plus.append(_factor("plus", _fmt_factor(lang, "moon_good", moon_illum)))
        elif moon_alt > 10 and moon_illum >= 60:
            minus.append(_factor("minus", _fmt_factor(lang, "moon_bad", moon_illum)))
        if d.get("galactic_core_visible"):
            plus.append(_factor("plus", _fmt_factor(lang, "mw_core")))
    elif tag == "aurora":
        kp = d.get("kp")
        if kp is not None:
            if float(kp) >= 4:
                plus.append(_factor("plus", _fmt_factor(lang, "kp_good", f"{float(kp):g}")))
            else:
                minus.append(_factor("minus", _fmt_factor(lang, "kp_low", f"{float(kp):g}")))
    elif tag == "cloud_sea":
        delta = d.get("cloud_base_delta")
        if delta is not None and delta >= 80:
            plus.insert(0, _factor("plus", _fmt_factor(lang, "cloud_below", int(delta))))
        elif d.get("cloud_base_near_camera"):
            minus.insert(0, _factor("minus", _fmt_factor(lang, "in_cloud")))

    return (plus[:2] + minus[:2])[:3]


def evaluate_tag_condition(tag, item_data, hour=None, lang="zh-TW"):
    c_low = float(item_data.get("c_low", 0) or 0)
    c_mid = float(item_data.get("c_mid", 0) or 0)
    c_high = float(item_data.get("c_high", 0) or 0)
    pop = float(item_data.get("pop", 0) or 0)
    vis = float(item_data.get("vis", 10000) or 10000)
    rh = float(item_data.get("rh", 50) or 50)
    wind = float(item_data.get("wind", 0) or 0)
    sun_alt = float(item_data.get("sun_elevation", 0) or 0)

    if hour is None:
        hour = int(item_data.get("hour", 12))
    is_day = bool(item_data.get("is_day", sun_alt > -0.8))
    civil_dark = bool(item_data.get("civil_dark", sun_alt <= -6))
    astro_dark = bool(item_data.get("astronomical_dark", sun_alt <= -18))
    is_twilight = bool(item_data.get("is_twilight", -8 <= sun_alt <= 8))

    raw = 60.0
    status_key = "STABLE_WEATHER"
    indicator_key = "IND_DEFAULT"

    if tag == "starlight":
        if sun_alt > -6:
            raw = 10
            status_key, indicator_key = "DAYLIGHT_ONLY", "IND_NO_STAR"
        else:
            cloud_loss = c_low * 0.55 + c_mid * 0.35 + c_high * 0.18
            raw = 94 - cloud_loss - pop * 0.45 - max(0, wind - 5) * 2.0
            if not astro_dark:
                raw = min(raw, 55)
            moon_alt = float(item_data.get("moon_elevation", -90) or -90)
            moon_illum = float(item_data.get("moon_illumination", 0) or 0)
            if moon_alt > 0:
                raw -= (moon_illum / 100.0) * min(24.0, 8.0 + moon_alt * 0.35)
            if item_data.get("galactic_core_visible"):
                raw += 5
            if vis < 15000:
                raw -= max(0, (15000 - vis) / 1500)
            if raw >= 86:
                status_key, indicator_key = "STARLIGHT_GREAT", "IND_CLEAR_SKY"
            elif raw >= 62:
                status_key, indicator_key = "STARLIGHT_FAIR", "IND_SOME_CLOUDS"
            else:
                status_key, indicator_key = "STARLIGHT_POOR", "IND_NO_STAR"

    elif tag == "aurora":
        if sun_alt > -6:
            raw = 10
            status_key, indicator_key = "DAYLIGHT_ONLY", "IND_DEFAULT"
        else:
            kp_val = float(item_data.get("kp") or 0)
            cloud_loss = c_low * 0.60 + c_mid * 0.35 + c_high * 0.15
            raw = 45 + kp_val * 7.0 - cloud_loss - pop * 0.35 - max(0, wind - 8) * 1.2
            if sun_alt > -12:
                raw -= 15
            if kp_val >= 5 and raw >= 72:
                status_key, indicator_key = "AURORA_CLEAR", "IND_CLEAR_SKY"
            elif raw >= 58:
                status_key, indicator_key = "AURORA_FAIR", "IND_SOME_CLOUDS"
            else:
                status_key, indicator_key = "AURORA_POOR", "IND_NO_STAR"

    elif tag == "cloud_sea":
        delta = item_data.get("cloud_base_delta")
        near = item_data.get("cloud_base_near_camera")
        below = item_data.get("cloud_below_camera")
        raw = 50 + (rh - 65) * 0.7 + min(c_low, 70) * 0.28 - pop * 0.35 - wind * 2.4
        if below:
            raw += 15
        if near and c_low >= 55:
            raw -= 22
        if delta is not None and delta < -150:
            raw -= 12
        if raw >= 86:
            status_key, indicator_key = "CLOUD_SEA_GOLD", "IND_CLOUD_SEA"
        elif raw >= 60:
            status_key, indicator_key = "CLOUD_SEA_FAIR", "IND_CLOUD_SEA_SUB"
        else:
            status_key, indicator_key = "CLOUD_SEA_DRY", "IND_DRY_AIR"

    elif tag == "forest":
        if not is_day and not is_twilight:
            raw = 35
            status_key, indicator_key = "FOREST_NORMAL", "IND_FOREST_NORM"
        elif rh >= 82 and vis <= 9000 and wind <= 4.0:
            raw = 92 - wind * 2.2 - pop * 0.25
            status_key, indicator_key = "FOREST_MIST", "IND_FOREST_MIST"
        elif vis >= 16000 and c_low <= 30 and pop < 20 and sun_alt > 5:
            raw = 88 - wind * 1.5
            status_key, indicator_key = "FOREST_LIGHT", "IND_FOREST_SUN"
        else:
            raw = 65 - pop * 0.3 - c_low * 0.15
            status_key, indicator_key = "FOREST_NORMAL", "IND_FOREST_NORM"

    elif tag == "lake":
        if not is_day and not is_twilight:
            raw = 48
            status_key, indicator_key = "LAKE_GOOD", "IND_LAKE_GOOD"
        elif wind <= 1.8 and rh >= 80 and (is_twilight or 4 <= hour <= 9):
            raw = 94 - pop * 0.25
            status_key, indicator_key = "LAKE_MIST", "IND_LAKE_MIST"
        elif wind <= 2.2 and vis >= 15000 and (c_low + c_mid) < 35:
            raw = 90 - pop * 0.2
            status_key, indicator_key = "LAKE_MIRROR", "IND_LAKE_MIRROR"
        elif wind <= 4.0:
            raw = 77 - pop * 0.25
            status_key, indicator_key = "LAKE_GOOD", "IND_LAKE_GOOD"
        else:
            raw = 62 - (wind - 4.0) * 5
            status_key, indicator_key = "LAKE_WINDY", "IND_LAKE_WIND"

    elif tag == "waterfall":
        if not is_day and not is_twilight:
            raw = 25
            status_key, indicator_key = "WATERFALL_NORMAL", "IND_WATERFALL_NORM"
        elif (c_low + c_mid) >= 45:
            raw = 90 - wind * 1.0 - pop * 0.2
            status_key, indicator_key = "WATERFALL_SOFT", "IND_WATERFALL_SOFT"
        elif (c_low + c_mid) < 15 and sun_alt > 25:
            raw = 58
            status_key, indicator_key = "WATERFALL_HARSH", "IND_WATERFALL_HARSH"
        else:
            raw = 75 - pop * 0.25
            status_key, indicator_key = "WATERFALL_NORMAL", "IND_WATERFALL_NORM"

    elif tag == "coast":
        mid_high = c_mid + c_high
        if is_twilight and 18 <= mid_high <= 80 and c_low < 40 and pop < 25:
            raw = 96 - wind * 1.4 - abs(mid_high - 48) * 0.08
            if item_data.get("sun_alignment") == "good":
                raw += 4
            elif item_data.get("sun_alignment") == "poor":
                raw -= 6
            status_key, indicator_key = "COAST_GLOW", "IND_COAST_GLOW"
        elif c_low >= 70:
            raw = 43
            status_key, indicator_key = "COAST_LOW_CLOUD", "IND_COAST_BLOCK"
        elif is_day or is_twilight:
            raw = 71 - pop * 0.4 - max(0, wind - 6) * 1.4
            status_key, indicator_key = "COAST_NORMAL", "IND_COAST_NORM"
        else:
            raw = 42
            status_key, indicator_key = "COAST_NORMAL", "IND_COAST_NORM"

    elif tag == "city":
        if sun_alt > -2:
            raw = 60 - pop * 0.3
            status_key, indicator_key = "CITY_DAY_FAIR", "IND_CITY_DAY_FAIR"
        else:
            raw = 88 - c_low * 0.32 - pop * 0.45 - max(0, wind - 8) * 1.5
            if vis >= 20000:
                raw += 5
            elif vis < 10000:
                raw -= (10000 - vis) / 1000 * 2.0
            if raw >= 85:
                status_key, indicator_key = "CITY_NIGHT_CLEAR", "IND_CITY_NIGHT_CLEAR"
            elif raw >= 60:
                status_key, indicator_key = "CITY_NIGHT_FAIR", "IND_CITY_NIGHT_HAZE"
            else:
                status_key, indicator_key = "CITY_NIGHT_POOR", "IND_CITY_NIGHT_BLOCK"

    else:  # mountain
        if sun_alt <= -6:
            raw = 45 - pop * 0.2
            status_key, indicator_key = "MOUNTAIN_STABLE_NIGHT", "IND_NIGHT_CLEAR"
        else:
            raw = 91 - c_low * 0.42 - c_mid * 0.22 - pop * 0.42 - max(0, wind - 4) * 2.0
            if vis >= 30000:
                raw += 7
            elif vis >= 20000:
                raw += 4
            elif vis < 10000:
                raw -= (10000 - vis) / 700
            if raw >= 86:
                status_key, indicator_key = "MOUNTAIN_EXCELLENT_DAY", "IND_PEAKS"
            elif raw >= 60:
                status_key, indicator_key = "MOUNTAIN_STABLE_DAY", "IND_SOME_CLOUDS"
            else:
                status_key, indicator_key = "MOUNTAIN_FOG_DAY", "IND_NO_STAR"

    if pop >= 55:
        raw = min(raw, 42)
        status_key, indicator_key = "RAIN_RISK", "IND_RAIN_RISK"

    score = _calibrate_score(raw, tag, item_data)
    factors = _build_factors(tag, item_data, lang)
    return score, get_text(status_key, lang), get_text(indicator_key, lang), status_key, indicator_key, factors


def _build_open_meteo_url(spot):
    lat = spot.get("lat")
    lon = spot.get("lon")
    params = [
        f"latitude={lat}",
        f"longitude={lon}",
        "hourly=temperature_2m,dew_point_2m,relative_humidity_2m,cloud_cover_low,cloud_cover_mid,cloud_cover_high,wind_speed_10m,visibility,precipitation_probability,is_day",
        "daily=sunrise,sunset",
        "past_hours=24",
        "forecast_hours=72",
        "timezone=auto",
        "timeformat=unixtime",
        "wind_speed_unit=ms",
    ]
    elevation = spot.get("elevation")
    if elevation is not None:
        params.append(f"elevation={float(elevation):.1f}")
    return "https://api.open-meteo.com/v1/forecast?" + "&".join(params)


def _fetch_weather_response(spot):
    key = (round(float(spot.get("lat")), 6), round(float(spot.get("lon")), 6), spot.get("elevation"))
    if key in _WEATHER_RESPONSE_CACHE:
        return _WEATHER_RESPONSE_CACHE[key]
    raw = _request_json(_build_open_meteo_url(spot))
    _WEATHER_RESPONSE_CACHE[key] = raw
    return raw


def fetch_weather_for_spot(spot, lang="zh-TW", kp_rows=None):
    lat = spot.get("lat")
    lon = spot.get("lon")
    tags = spot.get("tags", ["mountain"])
    if lat is None or lon is None:
        return {}

    try:
        raw = _fetch_weather_response(spot)
        hourly = raw.get("hourly", {}) or {}
        timestamps = hourly.get("time", [])
        if not timestamps:
            return {}

        tz_name = raw.get("timezone") or "UTC"
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = timezone(timedelta(seconds=int(raw.get("utc_offset_seconds", 0) or 0)))

        twilight_lookup = _twilight_dates(raw, tz)
        kp_rows = fetch_noaa_kp_series() if kp_rows is None else kp_rows
        now_utc = datetime.now(timezone.utc)
        api_elevation = float(raw.get("elevation") or 0)
        camera_elevation = float(spot.get("elevation") if spot.get("elevation") is not None else api_elevation)
        view_azimuth = spot.get("view_azimuth")
        view_tolerance = float(spot.get("view_tolerance", 45) or 45)

        def hv(name, i, default=0):
            arr = hourly.get(name, []) or []
            return arr[i] if i < len(arr) and arr[i] is not None else default

        hourly_forecast = []
        for i, ts in enumerate(timestamps):
            utc_dt = datetime.fromtimestamp(int(ts), timezone.utc)
            local_dt = utc_dt.astimezone(tz)
            temp = float(hv("temperature_2m", i, 0))
            dew = float(hv("dew_point_2m", i, temp))
            cloud_base_agl = max(60, int((temp - dew) * 125))
            cloud_base_asl = int(round(api_elevation + cloud_base_agl))
            cloud_base_delta = int(round(camera_elevation - cloud_base_asl))
            kp_val, kp_source = _kp_for_time(utc_dt, kp_rows)
            astro = _astronomy(utc_dt, lat, lon, lang)

            is_twilight = -8.0 <= astro["sun_elevation"] <= 8.0 or _near_twilight(local_dt, twilight_lookup, minutes=75)
            sun_alignment = "unknown"
            if view_azimuth is not None and is_twilight:
                diff = _angle_diff(astro["sun_azimuth"], float(view_azimuth))
                sun_alignment = "good" if diff <= view_tolerance else ("poor" if diff >= min(100, view_tolerance + 35) else "neutral")

            item_data = {
                "c_low": hv("cloud_cover_low", i, 0),
                "c_mid": hv("cloud_cover_mid", i, 0),
                "c_high": hv("cloud_cover_high", i, 0),
                "pop": hv("precipitation_probability", i, 0),
                "vis": hv("visibility", i, 10000),
                "rh": hv("relative_humidity_2m", i, 50),
                "wind": hv("wind_speed_10m", i, 0),
                "kp": kp_val,
                "hour": local_dt.hour,
                "is_day": bool(hv("is_day", i, 1)),
                "is_twilight": is_twilight,
                "cloud_base_agl": cloud_base_agl,
                "cloud_base_asl": cloud_base_asl,
                "cloud_base_delta": cloud_base_delta,
                "cloud_below_camera": cloud_base_delta >= 80,
                "cloud_base_near_camera": abs(cloud_base_delta) <= 180,
                "sun_alignment": sun_alignment,
                **astro,
            }

            tag_scores = {}
            for tag in tags:
                score, status, indicator, status_key, indicator_key, factors = evaluate_tag_condition(tag, item_data, local_dt.hour, lang)
                tag_scores[tag] = {
                    "score": score,
                    "status": status,
                    "status_key": status_key,
                    "key_indicator": indicator,
                    "indicator_key": indicator_key,
                    "factors": factors,
                }

            best_tag = max(tag_scores, key=lambda t: tag_scores[t]["score"]) if tag_scores else "mountain"
            best = tag_scores.get(best_tag, {
                "score": 50,
                "status": get_text("STABLE_WEATHER", lang),
                "key_indicator": get_text("IND_DEFAULT", lang),
                "status_key": "STABLE_WEATHER",
                "indicator_key": "IND_DEFAULT",
                "factors": [],
            })

            hourly_forecast.append({
                "time": local_dt.strftime("%Y-%m-%d %H:%M"),
                "time_utc": utc_dt.isoformat().replace("+00:00", "Z"),
                "local_date": local_dt.date().isoformat(),
                "timezone": tz_name,
                "timezone_abbr": local_dt.tzname() or tz_name,
                "score": best["score"],
                "status": best["status"],
                "status_key": best["status_key"],
                "key_indicator": best["key_indicator"],
                "indicator_key": best["indicator_key"],
                "factors": best.get("factors", []),
                "best_tag": best_tag,
                "tag_scores": tag_scores,
                "kp": kp_val,
                "kp_source": kp_source,
                "cloud_base": cloud_base_agl,  # backward compatibility
                "cloud_base_agl": cloud_base_agl,
                "cloud_base_asl": cloud_base_asl,
                "cloud_base_delta": cloud_base_delta,
                "camera_elevation": round(camera_elevation),
                "temp": round(temp, 1),
                "rh": item_data["rh"],
                "c_low": item_data["c_low"],
                "c_mid": item_data["c_mid"],
                "c_high": item_data["c_high"],
                "wind": item_data["wind"],
                "wind_unit": "m/s",
                "visibility": round(float(item_data["vis"]) / 1000, 1),
                "is_day": item_data["is_day"],
                "is_twilight": is_twilight,
                "sun_azimuth": astro["sun_azimuth"],
                "sun_elevation": astro["sun_elevation"],
                "sun_alignment": sun_alignment,
                "moon_azimuth": astro["moon_azimuth"],
                "moon_elevation": astro["moon_elevation"],
                "moon_illumination": astro["moon_illumination"],
                "moon_phase": astro["moon_phase"],
                "galactic_core_azimuth": astro["galactic_core_azimuth"],
                "galactic_core_elevation": astro["galactic_core_elevation"],
                "astronomical_dark": astro["astronomical_dark"],
                "galactic_core_visible": astro["galactic_core_visible"],
                "is_past": utc_dt < now_utc,
            })

        future_items = [h for h in hourly_forecast if not h["is_past"]]
        search_pool = future_items if future_items else hourly_forecast
        best_item = max(search_pool, key=lambda x: x["score"]) if search_pool else {}

        return {
            "score": best_item.get("score", 50),
            "best_tag": best_item.get("best_tag"),
            "best_time": best_item.get("time", "N/A"),
            "best_time_utc": best_item.get("time_utc"),
            "reason": "Photography Weather Score V3",
            "position": best_item.get("status", get_text("STABLE_WEATHER", lang)),
            "key_indicator": best_item.get("key_indicator", get_text("IND_DEFAULT", lang)),
            "timezone": tz_name,
            "timezone_abbr": best_item.get("timezone_abbr"),
            "utc_offset_seconds": raw.get("utc_offset_seconds"),
            "api_elevation": raw.get("elevation"),
            "view_azimuth": view_azimuth,
            "view_tolerance": view_tolerance if view_azimuth is not None else None,
            "hourly_forecast": hourly_forecast,
        }
    except Exception as e:
        print(f"Fetch weather error for {spot.get('name_i18n', {}).get('zh-TW', spot.get('name'))}: {e}")
        return {}


def update_usa_weather():
    pass
