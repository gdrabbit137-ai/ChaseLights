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


def evaluate_tag_condition(tag, item_data, hour=None, lang="zh-TW"):
    c_low = float(item_data.get("c_low", 0) or 0)
    c_mid = float(item_data.get("c_mid", 0) or 0)
    c_high = float(item_data.get("c_high", 0) or 0)
    pop = float(item_data.get("pop", 0) or 0)
    vis = float(item_data.get("vis", 10000) or 10000)
    rh = float(item_data.get("rh", 50) or 50)
    wind = float(item_data.get("wind", 0) or 0)  # m/s; API explicitly requests ms

    if hour is None:
        hour = int(item_data.get("hour", 12))
    is_day = bool(item_data.get("is_day", not (hour >= 18 or hour < 6)))
    is_night = not is_day
    is_twilight = bool(item_data.get("is_twilight", False))

    score = 75
    status_key = "STABLE_WEATHER"
    indicator_key = "IND_DEFAULT"

    # 1. 星空 / 極光
    if tag in ["starlight", "aurora"]:
        if not is_night:
            ind_k = "IND_NO_STAR" if tag == "starlight" else "IND_DEFAULT"
            return 15, get_text("DAYLIGHT_ONLY", lang), get_text(ind_k, lang), "DAYLIGHT_ONLY", ind_k

        cloud_loss = (c_low * 0.9) + (c_mid * 0.7) + (c_high * 0.4)
        score = 100 - cloud_loss - (pop * 0.8)
        if rh > 85:
            score -= 15
        if vis < 15000:
            score -= ((15000 - vis) / 1000) * 1.2
        if wind > 7.0:
            score -= (wind - 7.0) * 2

        if tag == "aurora":
            kp_val = item_data.get("kp")
            try:
                kp_val = float(kp_val) if kp_val is not None else 0.0
            except (ValueError, TypeError):
                kp_val = 0.0
            if kp_val >= 5:
                score += 15
                if score >= 70:
                    status = f"🔥 Aurora Outbreak (Kp {kp_val:g})" if lang == "en" else (f"🔥 オーロラ大爆発 (Kp {kp_val:g})" if lang == "ja" else f"🔥 極光大爆發 (Kp {kp_val:g})")
                    indicator = get_text("IND_CLEAR_SKY", lang)
                    return max(15, min(99, int(score))), status, indicator, "AURORA_OUTBREAK", "IND_CLEAR_SKY"
                status = f"☁️ Storm but Cloudy (Kp {kp_val:g})" if lang == "en" else (f"☁️ 磁気嵐だが雲あり (Kp {kp_val:g})" if lang == "ja" else f"☁️ 磁暴強烈但有雲 (Kp {kp_val:g})")
                indicator = get_text("IND_NO_STAR", lang)
                return max(15, min(99, int(score))), status, indicator, "AURORA_STORM_CLOUDY", "IND_NO_STAR"
            elif score >= 85:
                status_key, indicator_key = "AURORA_CLEAR", "IND_CLEAR_SKY"
            elif score >= 60:
                status_key, indicator_key = "AURORA_FAIR", "IND_SOME_CLOUDS"
            else:
                status_key, indicator_key = "AURORA_POOR", "IND_NO_STAR"
        else:
            if score >= 85:
                status_key, indicator_key = "STARLIGHT_GREAT", "IND_CLEAR_SKY"
            elif score >= 60:
                status_key, indicator_key = "STARLIGHT_FAIR", "IND_SOME_CLOUDS"
            else:
                status_key, indicator_key = "STARLIGHT_POOR", "IND_NO_STAR"

    # 2. 雲海：仍是 heuristic，但風速單位、時區已修正。
    elif tag == "cloud_sea":
        if rh >= 75 and 30 <= c_low <= 85 and pop < 30:
            score = 95 - (wind * 2)
            status_key, indicator_key = "CLOUD_SEA_GOLD", "IND_CLOUD_SEA"
        elif rh >= 70 and (c_low > 85 or c_low < 30):
            score = 60
            status_key, indicator_key = "CLOUD_SEA_FAIR", "IND_CLOUD_SEA_SUB"
        else:
            score = 30
            status_key, indicator_key = "CLOUD_SEA_DRY", "IND_DRY_AIR"

    # 3. 森林
    elif tag == "forest":
        if rh >= 80 and vis <= 8000 and wind <= 5.0:
            score = 96 - (wind * 3) - (pop * 0.4)
            status_key, indicator_key = "FOREST_MIST", "IND_FOREST_MIST"
        elif vis >= 15000 and c_low <= 30 and pop < 20 and is_day:
            score = 90 - (wind * 2)
            status_key, indicator_key = "FOREST_LIGHT", "IND_FOREST_SUN"
        else:
            score = 65 - (pop * 0.5) - (c_low * 0.3)
            status_key, indicator_key = "FOREST_NORMAL", "IND_FOREST_NORM"

    # 4. 湖景
    elif tag == "lake":
        if wind <= 4.0:
            if rh >= 80 and vis <= 10000 and (is_twilight or 4 <= hour <= 8):
                score = 95
                status_key, indicator_key = "LAKE_MIST", "IND_LAKE_MIST"
            elif vis >= 15000 and (c_low + c_mid) < 30:
                score = 92
                status_key, indicator_key = "LAKE_MIRROR", "IND_LAKE_MIRROR"
            else:
                score = 80
                status_key, indicator_key = "LAKE_GOOD", "IND_LAKE_GOOD"
        else:
            score = 55 - (wind - 4.0) * 5
            status_key, indicator_key = "LAKE_WINDY", "IND_LAKE_WIND"

    # 5. 瀑布
    elif tag == "waterfall":
        if (c_low + c_mid) >= 40:
            score = 95 - (wind * 1.5)
            status_key, indicator_key = "WATERFALL_SOFT", "IND_WATERFALL_SOFT"
        elif (c_low + c_mid) < 15 and is_day:
            score = 65
            status_key, indicator_key = "WATERFALL_HARSH", "IND_WATERFALL_HARSH"
        else:
            score = 80
            status_key, indicator_key = "WATERFALL_NORMAL", "IND_WATERFALL_NORM"
        score -= (pop * 0.3)

    # 6. 海岸：使用實際日出/日落附近時段，不再硬編 05/06/17/18。
    elif tag == "coast":
        if is_twilight and 20 <= (c_high + c_mid) <= 75 and c_low < 35 and pop < 20:
            score = 95 - (wind * 1.5)
            status_key, indicator_key = "COAST_GLOW", "IND_COAST_GLOW"
        elif c_low >= 70:
            score = 45
            status_key, indicator_key = "COAST_LOW_CLOUD", "IND_COAST_BLOCK"
        else:
            score = 75 - (pop * 0.6)
            status_key, indicator_key = "COAST_NORMAL", "IND_COAST_NORM"

    # 7. 城市
    elif tag == "city":
        score = 90 - (c_low * 0.5) - (pop * 0.7)
        if vis >= 15000:
            score += 8
        else:
            score -= ((15000 - vis) / 1000) * 1.5
        score -= max(0, wind - 8.0) * 2

        if is_night:
            if score >= 85:
                status_key, indicator_key = "CITY_NIGHT_CLEAR", "IND_CITY_NIGHT_CLEAR"
            elif score >= 60:
                status_key, indicator_key = "CITY_NIGHT_FAIR", "IND_CITY_NIGHT_HAZE"
            else:
                status_key, indicator_key = "CITY_NIGHT_POOR", "IND_CITY_NIGHT_BLOCK"
        else:
            if score >= 85:
                status_key, indicator_key = "CITY_DAY_CLEAR", "IND_CITY_DAY_CLEAR"
            elif score >= 60:
                status_key, indicator_key = "CITY_DAY_FAIR", "IND_CITY_DAY_FAIR"
            else:
                status_key, indicator_key = "CITY_DAY_POOR", "IND_CITY_DAY_HAZE"

    # 8. 山景 / fallback
    else:
        score = 95 - (c_low * 0.6 + c_mid * 0.4) - (pop * 0.7)
        if vis >= 18000:
            score += 5
        else:
            score -= max(0, (15000 - vis) / 400)
        score -= max(0, wind - 8.0) * 2.5

        if is_night:
            if score >= 85:
                status_key, indicator_key = "MOUNTAIN_EXCELLENT_NIGHT", "IND_NIGHT_CLEAR"
            elif score >= 60:
                status_key, indicator_key = "MOUNTAIN_STABLE_NIGHT", "IND_SOME_CLOUDS"
            else:
                status_key, indicator_key = "MOUNTAIN_FOG_NIGHT", "IND_NO_STAR"
        else:
            if score >= 85:
                status_key, indicator_key = "MOUNTAIN_EXCELLENT_DAY", "IND_PEAKS"
            elif score >= 60:
                status_key, indicator_key = "MOUNTAIN_STABLE_DAY", "IND_SOME_CLOUDS"
            else:
                status_key, indicator_key = "MOUNTAIN_FOG_DAY", "IND_NO_STAR"

    if pop >= 50:
        score = min(score, 40)
        status_key, indicator_key = "RAIN_RISK", "IND_RAIN_RISK"

    return (
        max(15, min(99, int(score))),
        get_text(status_key, lang),
        get_text(indicator_key, lang),
        status_key,
        indicator_key,
    )


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

        def hv(name, i, default=0):
            arr = hourly.get(name, []) or []
            return arr[i] if i < len(arr) and arr[i] is not None else default

        hourly_forecast = []
        for i, ts in enumerate(timestamps):
            utc_dt = datetime.fromtimestamp(int(ts), timezone.utc)
            local_dt = utc_dt.astimezone(tz)
            temp = hv("temperature_2m", i, 0)
            dew = hv("dew_point_2m", i, temp)
            estimated_cloud_base = max(100, int((float(temp) - float(dew)) * 125))
            kp_val, kp_source = _kp_for_time(utc_dt, kp_rows)

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
                "is_twilight": _near_twilight(local_dt, twilight_lookup),
            }

            tag_scores = {}
            for tag in tags:
                score, status, indicator, status_key, indicator_key = evaluate_tag_condition(tag, item_data, local_dt.hour, lang)
                tag_scores[tag] = {
                    "score": score,
                    "status": status,
                    "status_key": status_key,
                    "key_indicator": indicator,
                    "indicator_key": indicator_key,
                }

            best_tag = max(tag_scores, key=lambda t: tag_scores[t]["score"]) if tag_scores else "mountain"
            best = tag_scores.get(best_tag, {
                "score": 50,
                "status": get_text("STABLE_WEATHER", lang),
                "key_indicator": get_text("IND_DEFAULT", lang),
                "status_key": "STABLE_WEATHER",
                "indicator_key": "IND_DEFAULT",
            })

            hourly_forecast.append({
                "time": local_dt.strftime("%Y-%m-%d %H:%M"),
                "time_utc": utc_dt.isoformat().replace("+00:00", "Z"),
                "local_date": local_dt.date().isoformat(),
                "timezone": tz_name,
                "score": best["score"],
                "status": best["status"],
                "status_key": best["status_key"],
                "key_indicator": best["key_indicator"],
                "indicator_key": best["indicator_key"],
                "best_tag": best_tag,
                "tag_scores": tag_scores,
                "kp": kp_val,
                "kp_source": kp_source,
                "cloud_base": estimated_cloud_base,
                "temp": temp,
                "rh": item_data["rh"],
                "c_low": item_data["c_low"],
                "c_mid": item_data["c_mid"],
                "c_high": item_data["c_high"],
                "wind": item_data["wind"],
                "wind_unit": "m/s",
                "visibility": round(float(item_data["vis"]) / 1000, 1),
                "is_day": item_data["is_day"],
                "is_twilight": item_data["is_twilight"],
                "is_past": utc_dt < now_utc,
            })

        future_items = [h for h in hourly_forecast if not h["is_past"]]
        search_pool = future_items if future_items else hourly_forecast
        best_item = max(search_pool, key=lambda x: x["score"]) if search_pool else {}

        return {
            "score": best_item.get("score", 50),
            "best_time": best_item.get("time", "N/A"),
            "best_time_utc": best_item.get("time_utc"),
            "reason": "Adaptive Weather Analysis",
            "position": best_item.get("status", get_text("STABLE_WEATHER", lang)),
            "key_indicator": best_item.get("key_indicator", get_text("IND_DEFAULT", lang)),
            "timezone": tz_name,
            "utc_offset_seconds": raw.get("utc_offset_seconds"),
            "api_elevation": raw.get("elevation"),
            "hourly_forecast": hourly_forecast,
        }
    except Exception as e:
        print(f"Fetch weather error for {spot.get('name_i18n', {}).get('zh-TW', spot.get('name'))}: {e}")
        return {}


def update_usa_weather():
    pass
