import json
import urllib.request
import urllib.error
import time
import os
from datetime import datetime, timezone, timedelta
from bisect import bisect_right
from zoneinfo import ZoneInfo

from opportunity_runtime import (
    evaluate_opportunity_modules,
    evaluate_minimum_sufficient_visibility,
)
from spatial_weather import (
    build_spatial_request_plan,
    index_spatial_response,
    spatial_observations_for_timestamp,
)
from marine_state import (
    index_marine_response,
    marine_sample_for_timestamp,
    spot_requires_marine_state,
)
from tide_state import (
    index_tide_response,
    tide_sample_for_timestamp,
    spot_requires_tide_state,
)
from shinhotaka_access import (
    build_shinhotaka_access_state,
    fetch_shinhotaka_homepage_status,
    unknown_shinhotaka_provider_state,
)

# 後端多國語言狀態與指標字典
I18N_MESSAGES = {
    # 狀態 (Status)
    "MOUNTAIN_EXCELLENT_DAY": {"zh-TW": "☀️ 日間能見度條件良好", "en": "☀️ Good Daytime Visibility Conditions", "ja": "☀️ 日中の視程条件良好"},
    "MOUNTAIN_STABLE_DAY": {"zh-TW": "⛅ 日間能見度條件普通", "en": "⛅ Moderate Daytime Visibility", "ja": "⛅ 日中の視程条件は普通"},
    "MOUNTAIN_FOG_DAY": {"zh-TW": "☁️ 低雲或低能見度影響視野", "en": "☁️ Low Clouds or Reduced Visibility", "ja": "☁️ 低雲または低視程で視界に影響"},
    "MOUNTAIN_EXCELLENT_NIGHT": {"zh-TW": "🌙 夜間大氣清透", "en": "🌙 Clear Night Sky", "ja": "🌙 清透な夜間大気"},
    "MOUNTAIN_STABLE_NIGHT": {"zh-TW": "🌙 夜間氣象平穩", "en": "🌙 Stable Night Weather", "ja": "🌙 穏やかな夜間気象"},
    "MOUNTAIN_FOG_NIGHT": {"zh-TW": "☁️ 夜間濃霧雲覆", "en": "☁️ Night Fog / Clouds", "ja": "☁️ 夜間の濃霧・雲覆"},
    "CLOUD_SEA_GOLD": {"zh-TW": "☁️ 雲海模型條件較符合", "en": "☁️ Conditions Match the Cloud-Sea Model Well", "ja": "☁️ 雲海モデル条件に比較的合致"},
    "CLOUD_SEA_FAIR": {"zh-TW": "⛅ 雲海模型條件部分符合", "en": "⛅ Cloud-Sea Model Partially Matched", "ja": "⛅ 雲海モデル条件に一部合致"},
    "CLOUD_SEA_DRY": {"zh-TW": "☀️ 雲海模型條件不足", "en": "☀️ Cloud-Sea Model Conditions Not Met", "ja": "☀️ 雲海モデル条件が不足"},
    "CLOUD_SEA_OUTSIDE": {"zh-TW": "🕒 目前非可見雲海拍攝時段", "en": "🕒 Outside Visible Cloud-Sea Shooting Window", "ja": "🕒 現在は雲海を撮影できる明るさの時間外"},
    "FOREST_MIST": {"zh-TW": "🌫️ 霧景模型條件較符合", "en": "🌫️ Conditions Match the Mist Model", "ja": "🌫️ 霧景モデル条件に合致"},
    "FOREST_LIGHT": {"zh-TW": "🌤️ 光束模型條件較符合", "en": "🌤️ Conditions Match the Sunbeam Model", "ja": "🌤️ 光芒モデル条件に合致"},
    "FOREST_NORMAL": {"zh-TW": "⛅ 光霧條件一般", "en": "⛅ Ordinary Light/Mist Conditions", "ja": "⛅ 光・霧条件は通常"},
    "LAKE_MIST": {"zh-TW": "🌫️ 湖面夢幻晨霧", "en": "🌫️ Misty Lake Morning", "ja": "🌫️ 幻想的な湖畔の朝霧"},
    "LAKE_MIRROR": {"zh-TW": "🪞 低風速，倒影條件較穩定", "en": "🪞 Low Wind; Reflection Conditions More Stable", "ja": "🪞 弱風で反射条件が比較的安定"},
    "LAKE_GOOD": {"zh-TW": "🌊 水面風速條件較低", "en": "🌊 Lower Wind over the Water", "ja": "🌊 水面付近の風が弱め"},
    "LAKE_WINDY": {"zh-TW": "🌬️ 風速較高，倒影穩定度下降", "en": "🌬️ Higher Wind; Reflection Stability Reduced", "ja": "🌬️ 風が強く反射の安定度が低下"},
    "WATERFALL_SOFT": {"zh-TW": "💧 中低雲較多，光線較柔和", "en": "💧 More Low/Mid Cloud; Softer Light", "ja": "💧 中低層雲が多く光が柔らかい"},
    "WATERFALL_HARSH": {"zh-TW": "☀️ 太陽高度高且雲量少，反差較高", "en": "☀️ High Sun and Low Cloud; Higher Contrast", "ja": "☀️ 太陽高度が高く雲が少ないため高コントラスト"},
    "WATERFALL_NORMAL": {"zh-TW": "💧 長曝光線條件一般", "en": "💧 Ordinary Long-Exposure Light Conditions", "ja": "💧 長時間露光の光条件は通常"},
    "COAST_GLOW": {"zh-TW": "🌈 彩霞模型條件較符合", "en": "🌈 Conditions Match the Sky-Glow Model", "ja": "🌈 朝夕焼けモデル条件に合致"},
    "FIRE_CLOUD_LIKELY": {"zh-TW": "🔥 雲量組合符合火燒雲模型門檻", "en": "🔥 Cloud Pattern Meets Fire-Cloud Model Threshold", "ja": "🔥 雲量構成が焼け雲モデル閾値に合致"},
    "COAST_LOW_CLOUD": {"zh-TW": "☁️ 低雲量較高", "en": "☁️ Higher Low-Cloud Cover", "ja": "☁️ 低層雲量が多め"},
    "COAST_NORMAL": {"zh-TW": "🌅 晨昏雲量條件一般", "en": "🌅 Ordinary Dawn/Dusk Cloud Conditions", "ja": "🌅 朝夕の雲量条件は通常"},
    "BLUE_HOUR_CLEAR": {"zh-TW": "🔵 藍調時刻視野清透", "en": "🔵 Clear Blue-Hour View", "ja": "🔵 ブルーアワーの視界良好"},
    "BLUE_HOUR_FAIR": {"zh-TW": "🔵 藍調時刻條件普通", "en": "🔵 Fair Blue-Hour Conditions", "ja": "🔵 ブルーアワーの条件は普通"},
    "BLUE_HOUR_POOR": {"zh-TW": "☁️ 藍調時刻視野受雲霧影響", "en": "☁️ Blue-Hour View Affected by Clouds/Haze", "ja": "☁️ 雲・霞でブルーアワーの視界に影響"},
    "BLUE_HOUR_OUTSIDE": {"zh-TW": "🕒 目前非藍調時段", "en": "🕒 Outside Blue-Hour Window", "ja": "🕒 現在はブルーアワー外"},
    "BLUE_HOUR_DATA_LIMITED": {"zh-TW": "⚠️ 藍調時段可判定，但能見度資料不足", "en": "⚠️ Blue-Hour Timing Known, Visibility Data Limited", "ja": "⚠️ ブルーアワー判定可・視程データ不足"},
    "CITY_NIGHT_CLEAR": {"zh-TW": "🏙️ 城市夜景能見度佳", "en": "🏙️ Good Visibility for City Night View", "ja": "🏙️ 都市夜景の視程良好"},
    "CITY_NIGHT_FAIR": {"zh-TW": "🌃 夜景條件普通", "en": "🌃 Fair City Night View", "ja": "🌃 普通の夜景条件"},
    "CITY_NIGHT_POOR": {"zh-TW": "☁️ 夜景視線受阻", "en": "☁️ Obstructed Night View", "ja": "☁️ 視界不順の夜景"},
    "CITY_DAY_CLEAR": {"zh-TW": "🏙️ 城市遠眺極佳", "en": "🏙️ Excellent City Panorama", "ja": "🏙️ 最高の都市遠望"},
    "CITY_DAY_FAIR": {"zh-TW": "🏙️ 城市景觀普通", "en": "🏙️ Normal City View", "ja": "🏙️ 普通の都市景觀"},
    "CITY_DAY_POOR": {"zh-TW": "🌫️ 城市視線受阻", "en": "🌫️ Obstructed City View", "ja": "🌫️ 視界不順の都市景觀"},
    "NIGHT_SCENE_CLEAR": {"zh-TW": "🌙 夜間景觀能見度佳", "en": "🌙 Good Visibility for Night Scene", "ja": "🌙 夜景の視程良好"},
    "NIGHT_SCENE_FAIR": {"zh-TW": "🌙 夜間景觀條件普通", "en": "🌙 Fair Night-Scene Conditions", "ja": "🌙 夜景条件は普通"},
    "NIGHT_SCENE_POOR": {"zh-TW": "☁️ 夜間景觀受低雲或低能見度影響", "en": "☁️ Night Scene Affected by Low Clouds/Visibility", "ja": "☁️ 低雲・低視程で夜景に影響"},
    "NIGHT_SCENE_OUTSIDE": {"zh-TW": "🕒 目前非夜間景觀時段", "en": "🕒 Outside Night-Scene Window", "ja": "🕒 現在は夜景時間外"},
    "STARLIGHT_GREAT": {"zh-TW": "🌌 星空拍攝條件良好", "en": "🌌 Good Stargazing Conditions", "ja": "🌌 星空撮影条件良好"},
    "STARLIGHT_FAIR": {"zh-TW": "✨ 星空條件普通", "en": "✨ Moderate Stargazing", "ja": "✨ 普通の星空条件"},
    "STARLIGHT_POOR": {"zh-TW": "☁️ 星空條件不佳", "en": "☁️ Poor Stargazing Conditions", "ja": "☁️ 星空条件が不良"},
    "STARLIGHT_LIGHT_POLLUTION": {"zh-TW": "🌃 光害限制銀河細節", "en": "🌃 Light Pollution Limits Milky Way Detail", "ja": "🌃 光害で天の川の細部が見えにくい"},
    "AURORA_CLEAR": {"zh-TW": "🌌 夜間極光視野清透", "en": "🌌 Clear Aurora View", "ja": "🌌 清透なオーロラ視界"},
    "AURORA_FAIR": {"zh-TW": "🌌 極光觀察條件普通", "en": "🌌 Fair Aurora Conditions", "ja": "🌌 普通のオーロラ条件"},
    "AURORA_POOR": {"zh-TW": "☁️ 極光觀測條件不佳", "en": "☁️ Poor Aurora Viewing Conditions", "ja": "☁️ オーロラ観測条件が不良"},
    "AURORA_LIGHT_POLLUTION": {"zh-TW": "🌃 光害降低極光對比", "en": "🌃 Light Pollution Reduces Aurora Contrast", "ja": "🌃 光害でオーロラのコントラストが低下"},
    "AURORA_NO_KP": {"zh-TW": "🌌 天空可觀測，但缺少 Kp 預報", "en": "🌌 Sky is observable, but Kp forecast is unavailable", "ja": "🌌 空は観測可能ですが Kp 予報がありません"},
    "ASTRO_DATA_UNAVAILABLE": {"zh-TW": "⚠️ 天文資料暫時不可用", "en": "⚠️ Astronomy data unavailable", "ja": "⚠️ 天文データを取得できません"},
    "ACCESS_TIME_LIMITED": {"zh-TW": "⏰ 非建議／可拍攝時段", "en": "⏰ Outside the recommended/access window", "ja": "⏰ 推奨・撮影可能時間外"},
    "DAYLIGHT_ONLY": {"zh-TW": "☀️ 白天日光強烈", "en": "☀️ Bright Daylight", "ja": "☀️ 強烈な日光（昼間）"},
    "RAIN_RISK": {"zh-TW": "🌧️ 降雨風險高", "en": "🌧️ High Rain Risk", "ja": "🌧️ 高い降雨リスク"},
    "STABLE_WEATHER": {"zh-TW": "⛅ 氣象平穩", "en": "⛅ Stable Weather", "ja": "⛅ 安定した気象"},
    "WEATHER_DATA_LIMITED": {"zh-TW": "⚠️ 必要氣象資料不足，暫不判定", "en": "⚠️ Required Weather Data Missing; No Verdict", "ja": "⚠️ 必要な気象データ不足・判定保留"},
    "OPPORTUNITY_MATCH": {"zh-TW": "✅ 此拍攝題材的關鍵條件目前符合", "en": "✅ Key conditions for this opportunity currently match", "ja": "✅ この撮影機会の主要条件が一致"},
    "OPPORTUNITY_CONDITION_MISS": {"zh-TW": "⚠️ 此拍攝題材的專屬條件目前未符合", "en": "⚠️ Opportunity-specific conditions do not currently match", "ja": "⚠️ この撮影機会の固有条件が未達"},
    "OPPORTUNITY_RUNTIME_DATA_MISSING": {"zh-TW": "⚠️ 此拍攝題材缺少必要預報資料", "en": "⚠️ Required opportunity forecast data is missing", "ja": "⚠️ この撮影機会に必要な予報データが不足"},
    "OPPORTUNITY_PARTIAL": {"zh-TW": "ℹ️ 僅能判斷部分條件，分數已限制", "en": "ℹ️ Only part of the conditions can be evaluated; score is capped", "ja": "ℹ️ 条件の一部のみ判定可能なためスコア上限あり"},
    "OPPORTUNITY_PROTOTYPE": {"zh-TW": "ℹ️ 題材已查證，但完整專屬公式仍在驗證", "en": "ℹ️ Opportunity is researched; full dedicated formula is still being validated", "ja": "ℹ️ 撮影機会は調査済みだが専用式は検証中"},
    "OPPORTUNITY_HOLD": {"zh-TW": "⛔ 此拍攝題材目前暫停推薦", "en": "⛔ This opportunity is currently on hold", "ja": "⛔ この撮影機会は現在推奨停止"},
    "OPPORTUNITY_DATA_INSUFFICIENT": {"zh-TW": "⚠️ 此拍攝題材資料不足，暫不高分推薦", "en": "⚠️ Insufficient data for a high-confidence recommendation", "ja": "⚠️ 高信頼の推奨に必要なデータ不足"},
    "NO_VIABLE_OPPORTUNITY": {"zh-TW": "🕒 今天剩餘時段沒有合適的已研究拍攝機會", "en": "🕒 No researched shooting opportunity remains viable today", "ja": "🕒 本日の残り時間に適した調査済み撮影機会はありません"},
    "OPPORTUNITY_SIMPLE_MATCH": {"zh-TW": "✅ 此景點的基本好拍條件已成立", "en": "✅ The Place's basic good-shoot conditions are met", "ja": "✅ この場所の基本的な好条件が成立"},
    "OPPORTUNITY_OUTSIDE_TIME_WINDOW": {"zh-TW": "🕒 天氣條件可用，但目前不在此題材的建議拍攝時段", "en": "🕒 Weather conditions are usable, but this is outside the recommended shooting time for this opportunity", "ja": "🕒 天候条件は利用可能ですが、この撮影機会の推奨時間帯ではありません"},
    "OPPORTUNITY_SIMPLE_MISS": {"zh-TW": "⚠️ 能見度、低雲或降雨條件目前不理想", "en": "⚠️ Visibility, low cloud, or precipitation is currently unfavorable", "ja": "⚠️ 視程・低雲・降水条件が現在不利"},

    # 關鍵指標 (Indicator)
    "IND_PEAKS": {"zh-TW": "💎 雲量、降雨與能見度符合高分門檻", "en": "💎 Cloud, Rain and Visibility Meet the High-Score Threshold", "ja": "💎 雲量・降水・視程が高スコア基準を満たす"},
    "IND_CLEAR_SKY": {"zh-TW": "💎 雲量與能見度符合觀星高分門檻", "en": "💎 Cloud and Visibility Meet the Stargazing Threshold", "ja": "💎 雲量と視程が星空撮影の高スコア基準を満たす"},
    "IND_SOME_CLOUDS": {"zh-TW": "⛅ 些許薄雲干擾", "en": "⛅ Slight Cloud Interference", "ja": "⛅ 薄雲による僅かな影響"},
    "IND_NO_STAR": {"zh-TW": "☁️ 不宜觀星攝影", "en": "☁️ Not Suitable for Stargazing", "ja": "☁️ 星空撮影に不適"},
    "IND_CLOUD_SEA": {"zh-TW": "☁️ 濕度與低雲條件符合雲海模型門檻", "en": "☁️ Humidity and Low Cloud Meet the Cloud-Sea Model Threshold", "ja": "☁️ 湿度と低層雲が雲海モデル閾値を満たす"},
    "IND_CLOUD_SEA_SUB": {"zh-TW": "⛅ 低雲高度或雲量稍偏", "en": "⛅ Suboptimal Cloud Height/Amount", "ja": "⛅ 雲量または高度がやや偏斜"},
    "IND_DRY_AIR": {"zh-TW": "☀️ 濕度或低雲條件未達雲海模型門檻", "en": "☀️ Humidity or Low Cloud Does Not Meet the Cloud-Sea Threshold", "ja": "☀️ 湿度または低層雲が雲海モデル閾値未満"},
    "IND_CLOUD_SEA_OUTSIDE": {"zh-TW": "🕒 太陽已低於可見雲海拍攝時段", "en": "🕒 Sun Is Below the Visible Cloud-Sea Shooting Range", "ja": "🕒 太陽高度が雲海撮影可能な範囲外"},
    "IND_FOREST_MIST": {"zh-TW": "🌫️ 濕度、風速與能見度符合霧景模型門檻", "en": "🌫️ Humidity, Wind and Visibility Meet the Mist Threshold", "ja": "🌫️ 湿度・風速・視程が霧景モデル閾値を満たす"},
    "IND_FOREST_SUN": {"zh-TW": "🌤️ 日照、雲量與濕度符合光束模型門檻", "en": "🌤️ Sun, Cloud and Humidity Meet the Sunbeam Threshold", "ja": "🌤️ 日照・雲量・湿度が光芒モデル閾値を満たす"},
    "IND_FOREST_NORM": {"zh-TW": "⛅ 光霧條件未達高分門檻", "en": "⛅ Light/Mist Conditions Below the High-Score Threshold", "ja": "⛅ 光・霧条件が高スコア基準未満"},
    "IND_LAKE_MIST": {"zh-TW": "🌊 湖面水氣飄渺極美", "en": "🌊 Ethereal Lake Mist", "ja": "🌊 湖面上に漂う幻想的な朝霧"},
    "IND_LAKE_MIRROR": {"zh-TW": "🌬️ 風速低，有利水面維持平穩", "en": "🌬️ Low Wind Favors a Calmer Water Surface", "ja": "🌬️ 弱風で水面が穏やかになりやすい"},
    "IND_LAKE_GOOD": {"zh-TW": "🌬️ 風速偏低", "en": "🌬️ Lower Wind Speed", "ja": "🌬️ 風速は低め"},
    "IND_LAKE_WIND": {"zh-TW": "🌬️ 風速較高", "en": "🌬️ Higher Wind Speed", "ja": "🌬️ 風速は高め"},
    "IND_WATERFALL_SOFT": {"zh-TW": "☁️ 中低雲較多，直射光反差較低", "en": "☁️ More Low/Mid Cloud; Lower Direct-Light Contrast", "ja": "☁️ 中低層雲が多く直射光のコントラストが低め"},
    "IND_WATERFALL_HARSH": {"zh-TW": "☀️ 太陽高度高且中低雲少", "en": "☀️ High Sun with Little Low/Mid Cloud", "ja": "☀️ 太陽高度が高く中低層雲が少ない"},
    "IND_WATERFALL_NORM": {"zh-TW": "💧 長曝光線條件一般", "en": "💧 Ordinary Long-Exposure Light Conditions", "ja": "💧 長時間露光の光条件は通常"},
    "IND_COAST_GLOW": {"zh-TW": "🌈 中高雲量適中、低雲較少", "en": "🌈 Moderate Mid/High Cloud with Less Low Cloud", "ja": "🌈 中高層雲が適度で低層雲が少なめ"},
    "IND_FIRE_CLOUD": {"zh-TW": "🔥 中高雲量與低雲量符合火燒雲模型門檻", "en": "🔥 Mid/High and Low Cloud Meet the Fire-Cloud Model Threshold", "ja": "🔥 中高層雲と低層雲が焼け雲モデル閾値を満たす"},
    "IND_COAST_BLOCK": {"zh-TW": "☁️ 遮蔽地平線視線", "en": "☁️ Obstructed Horizon View", "ja": "☁️ 地平線視界の遮蔽"},
    "IND_COAST_NORM": {"zh-TW": "🌅 晨昏雲量條件一般", "en": "🌅 Ordinary Dawn/Dusk Cloud Conditions", "ja": "🌅 朝夕の雲量条件は通常"},
    "IND_BLUE_HOUR_CLEAR": {"zh-TW": "💎 低雲少、能見度良好", "en": "💎 Low Cloud Cover and Good Visibility", "ja": "💎 低雲が少なく視程良好"},
    "IND_BLUE_HOUR_FAIR": {"zh-TW": "⛅ 雲量或能見度普通", "en": "⛅ Moderate Clouds or Visibility", "ja": "⛅ 雲量または視程は普通"},
    "IND_BLUE_HOUR_BLOCK": {"zh-TW": "☁️ 低雲或低能見度影響視野", "en": "☁️ Low Clouds or Reduced Visibility", "ja": "☁️ 低雲または低視程で視界に影響"},
    "IND_BLUE_HOUR_OUTSIDE": {"zh-TW": "🕒 太陽高度不在藍調時段", "en": "🕒 Sun Altitude Outside Blue-Hour Range", "ja": "🕒 太陽高度がブルーアワー範囲外"},
    "IND_BLUE_HOUR_DATA_LIMITED": {"zh-TW": "⚠️ 缺少能見度或低雲資料", "en": "⚠️ Visibility or Low-Cloud Data Missing", "ja": "⚠️ 視程または低雲データ不足"},
    "IND_CITY_NIGHT_CLEAR": {"zh-TW": "💎 城市燈火能見度良好", "en": "💎 Good Visibility for City Lights", "ja": "💎 街明かりの視程良好"},
    "IND_CITY_NIGHT_HAZE": {"zh-TW": "⛅ 低雲或能見度稍受影響", "en": "⛅ Low Cloud or Visibility Slightly Affected", "ja": "⛅ 低雲または視程にやや影響"},
    "IND_CITY_NIGHT_BLOCK": {"zh-TW": "☁️ 低雲或低能見度影響視野", "en": "☁️ Low Cloud or Reduced Visibility Affects the View", "ja": "☁️ 低雲または低視程で視界に影響"},
    "IND_CITY_DAY_CLEAR": {"zh-TW": "💎 城市場景能見度良好", "en": "💎 Good Visibility for the City Scene", "ja": "💎 都市場景の視程良好"},
    "IND_CITY_DAY_FAIR": {"zh-TW": "⛅ 大氣能見度平穩", "en": "⛅ Fair Atmospheric Visibility", "ja": "⛅ 安定した視程"},
    "IND_CITY_DAY_HAZE": {"zh-TW": "🌫️ 霾害或能見度差", "en": "🌫️ Haze or Poor Visibility", "ja": "🌫️ 煙霧または不鮮明な視程"},
    "IND_NIGHT_SCENE_CLEAR": {"zh-TW": "💎 低雲少、夜間能見度良好", "en": "💎 Low Clouds and Good Night Visibility", "ja": "💎 低雲が少なく夜間視程良好"},
    "IND_NIGHT_SCENE_FAIR": {"zh-TW": "⛅ 夜間雲量或能見度普通", "en": "⛅ Moderate Night Clouds or Visibility", "ja": "⛅ 夜間の雲量または視程は普通"},
    "IND_NIGHT_SCENE_BLOCK": {"zh-TW": "☁️ 低雲或低能見度影響夜間視野", "en": "☁️ Low Clouds or Reduced Night Visibility", "ja": "☁️ 低雲または低視程で夜間視界に影響"},
    "IND_NIGHT_SCENE_OUTSIDE": {"zh-TW": "🕒 太陽高度尚未進入夜間條件", "en": "🕒 Sun Altitude Not Yet in Night Range", "ja": "🕒 太陽高度が夜間条件外"},
    "IND_NIGHT_CLEAR": {"zh-TW": "🌌 高空無視線阻礙", "en": "🌌 Clear High-Altitude View", "ja": "🌌 上空の視界良好"},
    "IND_RAIN_RISK": {"zh-TW": "🌧️ 雨勢明顯不宜外拍", "en": "🌧️ Significant Rain / Avoid Shooting", "ja": "🌧️ 明らかな雨・屋外撮影不適"},
    "IND_KP_UNAVAILABLE": {"zh-TW": "⚠️ Kp 資料不足，僅評估天空條件", "en": "⚠️ Kp unavailable; sky conditions only", "ja": "⚠️ Kp データなし・空の条件のみ評価"},
    "IND_ASTRO_UNAVAILABLE": {"zh-TW": "⚠️ 天文資料不足", "en": "⚠️ Astronomy data unavailable", "ja": "⚠️ 天文データ不足"},
    "IND_ACCESS_LIMITED": {"zh-TW": "⏰ 請確認開放／入場時段", "en": "⏰ Check access/opening hours", "ja": "⏰ 営業・入場時間を確認"},
    "IND_WEATHER_DATA_LIMITED": {"zh-TW": "⚠️ 缺少此主題必要的氣象欄位", "en": "⚠️ Required Weather Fields Are Missing", "ja": "⚠️ このテーマに必要な気象項目が不足"},
    "IND_DEFAULT": {"zh-TW": "ℹ️ 目前無特定出景訊號", "en": "ℹ️ No Specific Photographic Signal", "ja": "ℹ️ 現時点で特定の撮影シグナルなし"}
}

def get_text(key, lang="zh-TW"):
    return I18N_MESSAGES.get(key, {}).get(lang, I18N_MESSAGES.get(key, {}).get("zh-TW", ""))


_NOAA_KP_CACHE = None
_WEATHER_RESPONSE_CACHE = {}
_SPATIAL_WEATHER_RESPONSE_CACHE = {}
_MARINE_RESPONSE_CACHE = {}
_TIDE_RESPONSE_CACHE = {}
_SHINHOTAKA_ACCESS_CACHE = None


def _fetch_shinhotaka_access_provider():
    """Fetch jp-021 official access status once per generator process."""
    global _SHINHOTAKA_ACCESS_CACHE
    if _SHINHOTAKA_ACCESS_CACHE is not None:
        return _SHINHOTAKA_ACCESS_CACHE
    try:
        _SHINHOTAKA_ACCESS_CACHE = fetch_shinhotaka_homepage_status()
    except Exception as exc:
        print(f"Shinhotaka access fetch error: {exc}")
        _SHINHOTAKA_ACCESS_CACHE = unknown_shinhotaka_provider_state(
            reason=f"provider_exception:{type(exc).__name__}"
        )
    return _SHINHOTAKA_ACCESS_CACHE


def _request_json(url, timeout=12, attempts=3):
    """Fetch JSON with bounded retries for transient network/TLS failures."""
    req = urllib.request.Request(url, headers={"User-Agent": "ChaseLights/2.0 (+weather photography)"})
    last_error = None
    for attempt in range(max(1, int(attempts))):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            # Retrying client errors only wastes time and can hide a bad request.
            if 400 <= int(getattr(exc, "code", 0) or 0) < 500:
                raise
            last_error = exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
        if attempt + 1 < max(1, int(attempts)):
            time.sleep(1.25 * (attempt + 1))
    if last_error is not None:
        raise last_error
    raise RuntimeError("weather request failed without an exception")


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
    values = [sun_az, sun_alt, moon_az, moon_alt, illumination, gc_az, gc_alt]
    if not all(__import__("math").isfinite(float(v)) for v in values):
        raise ValueError("non-finite astronomy result")
    return {
        "astronomy_valid": True,
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


def _safe_astronomy(dt, lat, lon, lang="zh-TW"):
    try:
        return _astronomy(dt, lat, lon, lang)
    except Exception:
        return {
            "astronomy_valid": False,
            "sun_azimuth": None,
            "sun_elevation": None,
            "moon_azimuth": None,
            "moon_elevation": None,
            "moon_illumination": None,
            "moon_phase": None,
            "galactic_core_azimuth": None,
            "galactic_core_elevation": None,
            "astronomical_dark": False,
            "civil_dark": False,
            "galactic_core_visible": False,
        }


FACTOR_TEMPLATES = {
    "vis_good": {"zh-TW": "能見度 {v} km", "en": "Visibility {v} km", "ja": "視程 {v} km"},
    "vis_low": {"zh-TW": "能見度僅 {v} km", "en": "Visibility only {v} km", "ja": "視程 {v} km のみ"},
    "low_cloud": {"zh-TW": "低雲僅 {v}%", "en": "Low cloud {v}%", "ja": "下層雲 {v}%"},
    "low_cloud_high": {"zh-TW": "低雲高達 {v}%", "en": "Low cloud {v}%", "ja": "下層雲 {v}%"},
    "calm": {"zh-TW": "風速僅 {v} m/s", "en": "Wind only {v} m/s", "ja": "風速 {v} m/s"},
    "windy": {"zh-TW": "風速 {v} m/s", "en": "Wind {v} m/s", "ja": "風速 {v} m/s"},
    "dry": {"zh-TW": "降雨機率 {v}%", "en": "Rain chance {v}%", "ja": "降水確率 {v}%"},
    "rain": {"zh-TW": "降雨機率達 {v}%", "en": "Rain chance {v}%", "ja": "降水確率 {v}%"},
    "twilight": {"zh-TW": "太陽高度進入晨昏時段", "en": "Sun altitude is in the twilight range", "ja": "太陽高度が朝夕の薄明範囲"},
    "cloud_color": {"zh-TW": "中高雲量位於彩霞模型範圍", "en": "Mid/high cloud is within the sky-color model range", "ja": "中高層雲量が朝夕焼けモデル範囲内"},
    "dark_sky_bortle": {"zh-TW": "估計 Bortle {v}，暗空良好", "en": "Est. Bortle {v} dark sky", "ja": "推定 Bortle {v} の暗い空"},
    "light_pollution_bortle": {"zh-TW": "估計 Bortle {v}，光害影響", "en": "Est. Bortle {v} light pollution", "ja": "推定 Bortle {v} の光害影響"},
    "fire_cloud": {"zh-TW": "雲量組合符合火燒雲模型門檻", "en": "Cloud pattern meets the fire-cloud model threshold", "ja": "雲量構成が焼け雲モデル閾値に合致"},
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
    "kp_unavailable": {"zh-TW": "Kp 預報目前不可用", "en": "Kp forecast unavailable", "ja": "Kp 予報を取得できません"},
    "astro_unavailable": {"zh-TW": "天文位置資料暫時不可用", "en": "Astronomy position data unavailable", "ja": "天文位置データを取得できません"},
    "access_limited": {"zh-TW": "此時段可能無法進入／不適合拍攝", "en": "This time may be inaccessible or unsuitable", "ja": "この時間帯は入場不可・撮影不適の可能性"},
    "fog_good": {"zh-TW": "濕度與風速符合霧景模型門檻", "en": "Humidity and wind meet the mist-model threshold", "ja": "湿度と風速が霧景モデル閾値を満たす"},
    "reflection_good": {"zh-TW": "風速低，水面受風擾動較小", "en": "Low wind means less wind-driven water disturbance", "ja": "弱風で風による水面擾乱が少ない"},
    "blue_hour": {"zh-TW": "太陽高度進入藍調時段", "en": "Sun altitude is in blue-hour range", "ja": "太陽高度がブルーアワー帯"},
    "sunbeam_good": {"zh-TW": "日照、雲量與濕度符合光束模型門檻", "en": "Sun, cloud and humidity meet the sunbeam-model threshold", "ja": "日照・雲量・湿度が光芒モデル閾値を満たす"},
    "snow_cold": {"zh-TW": "氣溫 {v}°C", "en": "Temperature {v}°C", "ja": "気温 {v}°C"},
}


def _fmt_factor(lang, key, value=None):
    text = FACTOR_TEMPLATES.get(key, {}).get(lang) or FACTOR_TEMPLATES.get(key, {}).get("zh-TW") or key
    return text.format(v=value) if value is not None else text


def _factor(kind, key, value=None, lang="zh-TW"):
    return {"type": kind, "key": key, "value": value, "text": _fmt_factor(lang, key, value)}


def _canonical_theme(theme):
    return {
        "mountain_view": "mountain",
        "milky_way": "starlight",
        "city_night": "city",
        "sunrise": "coast",
        "sunset": "coast",
        "sky_glow": "coast",
        "blue_hour": "twilight",
        "fog_mist": "forest",
        "reflection": "lake",
        "sunbeam": "forest",
        "long_exposure": "waterfall",
        "snow_scene": "mountain",
    }.get(theme, theme)


THEME_REQUIRED_WEATHER_INPUTS = {
    "mountain_view": ("c_low", "c_mid", "pop", "wind", "vis"),
    "sunrise": ("c_low", "c_mid", "c_high", "pop", "wind"),
    "sunset": ("c_low", "c_mid", "c_high", "pop", "wind"),
    "sky_glow": ("c_low", "c_mid", "c_high", "pop", "wind"),
    "blue_hour": ("c_low", "pop", "wind", "vis"),
    "fog_mist": ("rh", "wind", "vis", "pop"),
    "reflection": ("wind", "pop", "c_low"),
    "sunbeam": ("c_low", "c_mid", "rh", "vis", "pop", "wind"),
    "long_exposure": ("c_low", "c_mid", "pop", "wind"),
    "snow_scene": ("c_low", "c_mid", "pop", "wind", "vis", "temp"),
    "milky_way": ("c_low", "c_mid", "c_high", "pop", "wind", "vis"),
    "city_night": ("c_low", "pop", "wind", "vis"),
    "cloud_sea": ("rh", "c_low", "pop", "wind", "temp", "dew"),
    "aurora": ("c_low", "c_mid", "c_high", "pop", "wind"),
}

def _field_available(d, key):
    marker = f"{key}_available"
    if marker in d:
        return bool(d.get(marker))
    return d.get(key) is not None

def _missing_required_weather_inputs(theme, d):
    return tuple(
        key for key in THEME_REQUIRED_WEATHER_INPUTS.get(theme, ())
        if not _field_available(d, key)
    )

def _calibrate_score(raw_score, theme, item_data):
    raw = max(0.0, min(100.0, float(raw_score)))
    score = raw if raw <= 50 else 50.0 + (raw - 50.0) * 0.78
    tag = _canonical_theme(theme)
    vis_km = float(item_data.get("vis", 10000) or 10000) / 1000.0
    wind = float(item_data.get("wind", 0) or 0)
    pop = float(item_data.get("pop", 0) or 0)
    low = float(item_data.get("c_low", 0) or 0)
    if tag in {"mountain", "city", "starlight", "aurora"} and vis_km >= 30: score += 2.0
    if pop <= 5: score += 1.0
    if wind <= 2.0: score += 1.5
    if tag in {"mountain", "city", "starlight", "aurora", "coast"} and low <= 8: score += 1.5
    if theme == "milky_way" and item_data.get("astronomical_dark"): score += 2.0
    if theme == "milky_way" and item_data.get("galactic_core_visible"): score += 1.0
    if theme in {"sunrise", "sunset", "sky_glow"} and item_data.get("is_twilight"): score += 2.0
    if theme == "cloud_sea" and item_data.get("cloud_below_camera"): score += 2.5
    return int(round(max(10.0, min(96.0, score))))


def _temporal_eligibility(theme, d):
    """Whether this Theme is photographically possible at this timestamp.

    This is intentionally separate from weather quality. A low score may mean
    poor conditions; temporal_eligible=False means the photographic opportunity
    itself is not possible at that hour and must not become a daily winner.
    None means the astronomy/time evidence is insufficient for a hard verdict.
    """
    astro_valid = bool(d.get("astronomy_valid"))
    sun_alt = d.get("sun_elevation")
    hour = int(d.get("hour", 12))
    is_day = bool(d.get("is_day"))
    is_twilight = bool(d.get("is_twilight"))
    tag = _canonical_theme(theme)

    if theme == "sunrise":
        if hour >= 12:
            return False, "sunrise_after_noon"
        if astro_valid and sun_alt is not None:
            return (-10 <= float(sun_alt) <= 10), "sunrise_sun_altitude"
        return None, "astronomy_unavailable"

    if theme == "sunset":
        if hour < 12:
            return False, "sunset_before_noon"
        if astro_valid and sun_alt is not None:
            return (-10 <= float(sun_alt) <= 10), "sunset_sun_altitude"
        return None, "astronomy_unavailable"

    if theme == "sky_glow":
        if astro_valid and sun_alt is not None:
            return (-12 <= float(sun_alt) <= 10), "sky_glow_sun_altitude"
        return None, "astronomy_unavailable"

    if theme == "blue_hour":
        if astro_valid and sun_alt is not None:
            return (-10 <= float(sun_alt) <= -2), "blue_hour_sun_altitude"
        return None, "astronomy_unavailable"

    if theme == "fog_mist":
        return bool(is_day or is_twilight), "fog_visible_light"

    if theme == "reflection":
        if astro_valid and sun_alt is not None:
            return float(sun_alt) >= -8, "reflection_visible_light"
        return bool(is_day or is_twilight), "reflection_visible_light"

    if theme == "sunbeam":
        if astro_valid and sun_alt is not None:
            return bool(is_day) and float(sun_alt) >= 3, "sunbeam_sun_altitude"
        return bool(is_day), "sunbeam_daylight"

    if theme == "snow_scene":
        if astro_valid and sun_alt is not None:
            return float(sun_alt) >= -8, "snow_visible_light"
        return bool(is_day or is_twilight), "snow_visible_light"

    if theme == "cloud_sea":
        if astro_valid and sun_alt is not None:
            return float(sun_alt) >= -6, "cloud_sea_visible_light"
        return bool(is_day or is_twilight), "cloud_sea_visible_light"

    if theme == "city_night":
        if astro_valid and sun_alt is not None:
            return float(sun_alt) <= -2, "city_night_darkness"
        return (not is_day), "city_night_darkness"

    if tag == "starlight":
        if astro_valid and sun_alt is not None:
            return float(sun_alt) <= -12, "starlight_darkness"
        return None, "astronomy_unavailable"

    if tag == "aurora":
        if astro_valid and sun_alt is not None:
            return float(sun_alt) <= -12, "aurora_darkness"
        return None, "astronomy_unavailable"

    if tag == "mountain":
        if astro_valid and sun_alt is not None:
            return float(sun_alt) > -6, "landscape_visible_light"
        return bool(is_day or is_twilight), "landscape_visible_light"

    # Technique-like or generic themes that do not yet have a strict time gate.
    return True, "no_temporal_gate"


def _eligibility_cap(theme, d):
    if d.get("access_open") is False:
        return 15
    astro_valid = bool(d.get("astronomy_valid"))
    sun_alt = d.get("sun_elevation")
    hour = int(d.get("hour", 12))
    is_day = bool(d.get("is_day"))
    is_twilight = bool(d.get("is_twilight"))
    tag = _canonical_theme(theme)

    if theme == "sunrise":
        if hour >= 12: return 18
        if astro_valid and sun_alt is not None and not (-10 <= sun_alt <= 10): return 42
    elif theme == "sunset":
        if hour < 12: return 18
        if astro_valid and sun_alt is not None and not (-10 <= sun_alt <= 10): return 42
    elif theme == "sky_glow":
        if astro_valid and sun_alt is not None and not (-12 <= sun_alt <= 10): return 45
    elif theme == "blue_hour":
        if not astro_valid: return 55
        if sun_alt is None or not (-10 <= sun_alt <= -2): return 30
    elif theme == "fog_mist":
        if not is_day and not is_twilight: return 45
    elif theme == "reflection":
        if astro_valid and sun_alt is not None and sun_alt < -8: return 55
    elif theme == "sunbeam":
        if not is_day or (astro_valid and sun_alt is not None and sun_alt < 3): return 30
    elif theme == "long_exposure":
        if astro_valid and sun_alt is not None and sun_alt < -8: return 55
    elif theme == "snow_scene":
        if astro_valid and sun_alt is not None and sun_alt < -8: return 45
    elif tag == "mountain":
        if astro_valid and sun_alt is not None:
            if sun_alt <= -6: return 38
            if sun_alt <= 0: return 78
        elif not is_day and not is_twilight: return 45
    elif theme == "cloud_sea":
        if astro_valid and sun_alt is not None and sun_alt < -8: return 62
        if not astro_valid and not is_day and not is_twilight: return 65
    elif tag == "city":
        if astro_valid and sun_alt is not None and sun_alt > -2: return 68
        if not astro_valid and is_day: return 68
    elif tag == "starlight":
        if not astro_valid: return 55
        if sun_alt is not None and sun_alt > -12: return 45
        if sun_alt is not None and sun_alt > -18: return 72
    elif tag == "aurora":
        if not astro_valid: return 55
        if d.get("kp") is None: return 60
        if sun_alt is not None and sun_alt > -12: return 35
        if sun_alt is not None and sun_alt > -18: return 70
    return 96


def _fire_cloud_likely(d):
    """Conservative signal for intense red/orange illuminated cloud.

    This is deliberately stricter than generic sky-glow: the sun must be close
    to the horizon, low clouds should not block it, and enough mid/high cloud
    must exist to catch the low-angle light. It is a potential flag, not a
    guarantee of a fire-cloud display.
    """
    if not d.get("astronomy_valid"):
        return False
    sun_alt = d.get("sun_elevation")
    if sun_alt is None or not (-7.0 <= float(sun_alt) <= 4.0):
        return False
    low = float(d.get("c_low", 0) or 0)
    mid = float(d.get("c_mid", 0) or 0)
    high = float(d.get("c_high", 0) or 0)
    pop = float(d.get("pop", 0) or 0)
    wind = float(d.get("wind", 0) or 0)
    colored = mid + high
    return low <= 22 and pop <= 25 and wind <= 8 and 45 <= colored <= 135 and max(mid, high) >= 25


def _apply_light_pollution(score, theme, d):
    b = d.get("bortle_class")
    if b is None:
        return int(score)
    try:
        b = max(1, min(9, int(b)))
    except Exception:
        return int(score)
    tag = _canonical_theme(theme)
    score = float(score)
    if tag == "starlight":
        penalty = {1:0,2:0,3:2,4:6,5:12,6:20,7:28,8:38,9:48}[b]
        cap = {1:96,2:96,3:94,4:88,5:80,6:70,7:58,8:42,9:30}[b]
        score = min(score - penalty, cap)
    elif tag == "aurora":
        # Aurora is less sensitive than Milky Way imaging, especially during strong displays.
        penalty = {1:0,2:0,3:0,4:2,5:4,6:7,7:10,8:15,9:20}[b]
        cap = {1:96,2:96,3:96,4:94,5:92,6:88,7:82,8:72,9:62}[b]
        score = min(score - penalty, cap)
    return int(round(max(10, score)))


def _build_factors(theme, d, lang):
    plus, minus = [], []
    tag = _canonical_theme(theme)
    vis_km = round(float(d.get("vis", 0) or 0) / 1000.0, 1)
    wind = round(float(d.get("wind", 0) or 0), 1)
    pop = round(float(d.get("pop", 0) or 0))
    low = round(float(d.get("c_low", 0) or 0))
    if _field_available(d, "vis"):
        if vis_km >= 20: plus.append(_factor("plus", "vis_good", vis_km, lang))
        elif vis_km < 8 and theme not in {"fog_mist"}: minus.append(_factor("minus", "vis_low", vis_km, lang))
    if _field_available(d, "c_low"):
        if low <= 15 and tag in {"mountain", "city", "coast", "twilight", "starlight", "aurora"}: plus.append(_factor("plus", "low_cloud", low, lang))
        elif low >= 65 and tag in {"mountain", "city", "coast", "twilight", "starlight", "aurora"}: minus.append(_factor("minus", "low_cloud_high", low, lang))
    if _field_available(d, "wind"):
        if wind <= 2.5: plus.append(_factor("plus", "calm", wind, lang))
        elif wind >= 6: minus.append(_factor("minus", "windy", wind, lang))
    if _field_available(d, "pop"):
        if pop <= 10: plus.append(_factor("plus", "dry", pop, lang))
        elif pop >= 40: minus.append(_factor("minus", "rain", pop, lang))

    if theme in {"sunrise", "sunset", "sky_glow"}:
        if d.get("is_twilight"): plus.insert(0, _factor("plus", "twilight", None, lang))
        mid_high = float(d.get("c_mid", 0) or 0) + float(d.get("c_high", 0) or 0)
        if _fire_cloud_likely(d): plus.insert(0, _factor("plus", "fire_cloud", None, lang))
        elif 20 <= mid_high <= 90 and low < 35: plus.append(_factor("plus", "cloud_color", None, lang))
        if d.get("sun_alignment") == "good": plus.append(_factor("plus", "sun_align", None, lang))
        elif d.get("sun_alignment") == "poor": minus.append(_factor("minus", "sun_miss", None, lang))
    elif theme == "blue_hour":
        plus.insert(0, _factor("plus", "blue_hour", None, lang))
    elif theme == "fog_mist":
        if float(d.get("rh",0) or 0) >= 80 and wind <= 4: plus.insert(0, _factor("plus", "fog_good", None, lang))
    elif theme == "reflection":
        if wind <= 2.2: plus.insert(0, _factor("plus", "reflection_good", None, lang))
    elif theme == "sunbeam":
        plus.insert(0, _factor("plus", "sunbeam_good", None, lang))
    elif theme == "snow_scene":
        if _field_available(d, "temp") and float(d.get("temp", 99) or 99) <= 4: plus.insert(0, _factor("plus", "snow_cold", round(float(d.get("temp")), 1), lang))
    elif theme == "milky_way":
        b=d.get("bortle_class")
        if b is not None:
            if int(b) <= 3: plus.insert(0, _factor("plus", "dark_sky_bortle", int(b), lang))
            elif int(b) >= 5: minus.insert(0, _factor("minus", "light_pollution_bortle", int(b), lang))
        if d.get("astronomical_dark"): plus.insert(0, _factor("plus", "astro_dark", None, lang))
        else: minus.insert(0, _factor("minus", "not_dark", None, lang))
        moon_illum = round(float(d.get("moon_illumination", 0) or 0)); moon_alt = float(d.get("moon_elevation", -90) or -90)
        if moon_alt <= 0 or moon_illum <= 25: plus.append(_factor("plus", "moon_good", moon_illum, lang))
        elif moon_alt > 10 and moon_illum >= 60: minus.append(_factor("minus", "moon_bad", moon_illum, lang))
        if d.get("galactic_core_visible"): plus.append(_factor("plus", "mw_core", None, lang))
    elif theme == "aurora":
        b=d.get("bortle_class")
        if b is not None:
            if int(b) <= 3: plus.insert(0, _factor("plus", "dark_sky_bortle", int(b), lang))
            elif int(b) >= 7: minus.insert(0, _factor("minus", "light_pollution_bortle", int(b), lang))
        kp=d.get("kp")
        if kp is not None:
            key="kp_good" if float(kp)>=4 else "kp_low"
            (plus if float(kp)>=4 else minus).append(_factor("plus" if float(kp)>=4 else "minus", key, f"{float(kp):g}", lang))
    elif theme == "cloud_sea":
        delta=d.get("cloud_base_delta")
        if delta is not None and delta>=80: plus.insert(0,_factor("plus","cloud_below",int(delta),lang))
        elif d.get("cloud_base_near_camera"): minus.insert(0,_factor("minus","in_cloud",None,lang))

    if d.get("access_open") is False: minus.insert(0,_factor("minus","access_limited",None,lang))
    if theme in {"milky_way","aurora","sunrise","sunset","sky_glow","blue_hour"} and not d.get("astronomy_valid"):
        minus.insert(0,_factor("minus","astro_unavailable",None,lang))
    if theme=="aurora" and d.get("kp") is None: minus.insert(0,_factor("minus","kp_unavailable",None,lang))
    return (plus[:2]+minus[:2])[:3]

def evaluate_tag_condition(theme, item_data, hour=None, lang="zh-TW"):
    missing_inputs = _missing_required_weather_inputs(theme, item_data)
    if missing_inputs:
        factors = _build_factors(theme, item_data, lang)
        if item_data.get("access_open") is False:
            return 15, get_text("ACCESS_TIME_LIMITED", lang), get_text("IND_ACCESS_LIMITED", lang), "ACCESS_TIME_LIMITED", "IND_ACCESS_LIMITED", factors
        return 35, get_text("WEATHER_DATA_LIMITED", lang), get_text("IND_WEATHER_DATA_LIMITED", lang), "WEATHER_DATA_LIMITED", "IND_WEATHER_DATA_LIMITED", factors

    c_low=float(item_data.get("c_low",0) or 0); c_mid=float(item_data.get("c_mid",0) or 0); c_high=float(item_data.get("c_high",0) or 0)
    pop=float(item_data.get("pop",0) or 0); vis=float(item_data.get("vis",10000) or 10000); rh=float(item_data.get("rh",50) or 50); wind=float(item_data.get("wind",0) or 0)
    temp=float(item_data.get("temp",10) if item_data.get("temp") is not None else 10)
    astro_valid=bool(item_data.get("astronomy_valid")); sun_raw=item_data.get("sun_elevation")
    sun_alt=float(sun_raw) if sun_raw is not None else (10.0 if item_data.get("is_day") else -10.0)
    if hour is None: hour=int(item_data.get("hour",12))
    is_day=bool(item_data.get("is_day",sun_alt>-0.8)); astro_dark=bool(item_data.get("astronomical_dark",astro_valid and sun_alt<=-18)); is_twilight=bool(item_data.get("is_twilight",-8<=sun_alt<=8))
    tag=_canonical_theme(theme)
    raw=60.0; status_key="STABLE_WEATHER"; indicator_key="IND_DEFAULT"

    if theme in {"sunrise","sunset","sky_glow"}:
        morning=hour<12
        if (theme=="sunrise" and not morning) or (theme=="sunset" and morning):
            raw=12; status_key,indicator_key="DAYLIGHT_ONLY","IND_DEFAULT"
        elif not astro_valid:
            raw=48; status_key,indicator_key="ASTRO_DATA_UNAVAILABLE","IND_ASTRO_UNAVAILABLE"
        else:
            mid_high=c_mid+c_high
            if -10<=sun_alt<=10:
                raw=88 - c_low*0.45 - pop*0.45 - max(0,wind-5)*1.2
                if 20<=mid_high<=80: raw += 8 - abs(mid_high-48)*0.08
                if item_data.get("sun_alignment")=="good": raw+=4
                elif item_data.get("sun_alignment")=="poor": raw-=6
                if _fire_cloud_likely(item_data) and raw >= 82:
                    status_key,indicator_key="FIRE_CLOUD_LIKELY","IND_FIRE_CLOUD"
                elif raw>=78:
                    status_key,indicator_key="COAST_GLOW","IND_COAST_GLOW"
                else:
                    status_key,indicator_key="COAST_NORMAL","IND_COAST_NORM"
            else:
                raw=42; status_key,indicator_key="COAST_NORMAL","IND_COAST_NORM"
    elif theme=="blue_hour":
        blue_hour_data_complete = all(
            item_data.get(f"{key}_available", item_data.get(key) is not None)
            for key in ("vis", "c_low", "pop", "wind")
        )
        if not astro_valid:
            raw=45; status_key,indicator_key="ASTRO_DATA_UNAVAILABLE","IND_ASTRO_UNAVAILABLE"
        elif -10<=sun_alt<=-2:
            raw=88-c_low*0.35-pop*0.4-max(0,wind-7)*1.2
            if vis>=18000: raw+=5
            if not blue_hour_data_complete:
                raw=min(raw,55)
                status_key,indicator_key="BLUE_HOUR_DATA_LIMITED","IND_BLUE_HOUR_DATA_LIMITED"
            elif vis>=18000 and c_low<=20 and pop<=25:
                status_key,indicator_key="BLUE_HOUR_CLEAR","IND_BLUE_HOUR_CLEAR"
            elif raw>=60 and vis>=8000 and c_low<=60:
                status_key,indicator_key="BLUE_HOUR_FAIR","IND_BLUE_HOUR_FAIR"
            else:
                status_key,indicator_key="BLUE_HOUR_POOR","IND_BLUE_HOUR_BLOCK"
        else:
            raw=25; status_key,indicator_key="BLUE_HOUR_OUTSIDE","IND_BLUE_HOUR_OUTSIDE"
    elif theme=="fog_mist":
        if not is_day and not is_twilight:
            raw=35; status_key,indicator_key="FOREST_NORMAL","IND_FOREST_NORM"
        else:
            # Photogenic mist needs moisture and reduced visibility, but not a total whiteout.
            vis_km=vis/1000.0
            raw=45+(rh-70)*1.1-max(0,wind-2.5)*5-pop*0.2
            if 1.0<=vis_km<=10: raw+=14
            elif vis_km>18: raw-=15
            if is_twilight: raw+=5
            status_key,indicator_key=("FOREST_MIST","IND_FOREST_MIST") if raw>=72 else ("FOREST_NORMAL","IND_FOREST_NORM")
    elif theme=="reflection":
        if not is_day and not is_twilight:
            raw=42; status_key,indicator_key="LAKE_GOOD","IND_LAKE_GOOD"
        else:
            raw=92-pop*0.35-c_low*0.12-max(0,wind-1.0)*8
            if is_twilight: raw+=3
            if wind<=2.0: status_key,indicator_key="LAKE_MIRROR","IND_LAKE_MIRROR"
            elif wind<=4.0: status_key,indicator_key="LAKE_GOOD","IND_LAKE_GOOD"
            else: status_key,indicator_key="LAKE_WINDY","IND_LAKE_WIND"
    elif theme=="sunbeam":
        if not is_day or sun_alt<3:
            raw=25; status_key,indicator_key="FOREST_NORMAL","IND_FOREST_NORM"
        else:
            cloud_mix=c_low+c_mid
            raw=72-pop*0.35-max(0,wind-5)*1.5
            if 15<=cloud_mix<=75: raw+=12
            if 70<=rh<=95: raw+=7
            if vis<3000: raw-=12
            status_key,indicator_key=("FOREST_LIGHT","IND_FOREST_SUN") if raw>=78 else ("FOREST_NORMAL","IND_FOREST_NORM")
    elif theme=="long_exposure":
        if not is_day and not is_twilight:
            raw=42; status_key,indicator_key="WATERFALL_NORMAL","IND_WATERFALL_NORM"
        else:
            raw=78-pop*0.25-max(0,wind-8)*1.0
            if c_low+c_mid>=40: raw+=10; status_key,indicator_key="WATERFALL_SOFT","IND_WATERFALL_SOFT"
            elif sun_alt>25 and c_low+c_mid<15: raw-=12; status_key,indicator_key="WATERFALL_HARSH","IND_WATERFALL_HARSH"
            else: status_key,indicator_key="WATERFALL_NORMAL","IND_WATERFALL_NORM"
    elif theme=="snow_scene":
        if not is_day and not is_twilight:
            raw=35; status_key,indicator_key="MOUNTAIN_STABLE_NIGHT","IND_NIGHT_CLEAR"
        else:
            raw=82-c_low*0.32-c_mid*0.15-pop*0.3-max(0,wind-5)*1.8
            if vis>=20000: raw+=6
            if temp<=4: raw+=5
            elif temp>10: raw-=12
            status_key,indicator_key=("MOUNTAIN_EXCELLENT_DAY","IND_PEAKS") if raw>=82 else ("MOUNTAIN_STABLE_DAY","IND_SOME_CLOUDS")
    elif tag=="starlight":
        if not astro_valid:
            raw=45; status_key,indicator_key="ASTRO_DATA_UNAVAILABLE","IND_ASTRO_UNAVAILABLE"
        elif sun_alt>-6:
            raw=10; status_key,indicator_key="DAYLIGHT_ONLY","IND_NO_STAR"
        else:
            cloud_loss=c_low*0.55+c_mid*0.35+c_high*0.18
            raw=94-cloud_loss-pop*0.45-max(0,wind-5)*2.0
            if not astro_dark: raw=min(raw,55)
            moon_alt=float(item_data.get("moon_elevation",-90) or -90); moon_illum=float(item_data.get("moon_illumination",0) or 0)
            if moon_alt>0: raw-=(moon_illum/100.0)*min(24.0,8.0+moon_alt*0.35)
            if item_data.get("galactic_core_visible"): raw+=5
            if vis<15000: raw-=max(0,(15000-vis)/1500)
            status_key,indicator_key=("STARLIGHT_GREAT","IND_CLEAR_SKY") if raw>=86 else (("STARLIGHT_FAIR","IND_SOME_CLOUDS") if raw>=62 else ("STARLIGHT_POOR","IND_NO_STAR"))
    elif tag=="aurora":
        kp_raw=item_data.get("kp")
        if not astro_valid:
            raw=45; status_key,indicator_key="ASTRO_DATA_UNAVAILABLE","IND_ASTRO_UNAVAILABLE"
        elif sun_alt>-6:
            raw=10; status_key,indicator_key="DAYLIGHT_ONLY","IND_DEFAULT"
        elif kp_raw is None:
            raw=58-(c_low*0.45+c_mid*0.25+c_high*0.10)-pop*0.25; status_key,indicator_key="AURORA_NO_KP","IND_KP_UNAVAILABLE"
        else:
            kp_val=float(kp_raw); raw=45+kp_val*7.0-(c_low*0.60+c_mid*0.35+c_high*0.15)-pop*0.35-max(0,wind-8)*1.2
            if sun_alt>-12: raw-=15
            status_key,indicator_key=("AURORA_CLEAR","IND_CLEAR_SKY") if kp_val>=5 and raw>=72 else (("AURORA_FAIR","IND_SOME_CLOUDS") if raw>=58 else ("AURORA_POOR","IND_NO_STAR"))
    elif theme=="cloud_sea":
        if (astro_valid and sun_alt < -6.0) or (not astro_valid and not is_day and not is_twilight):
            # A cloud layer may physically exist after dark, but a normal visible
            # cloud-sea landscape Opportunity needs at least civil-twilight light.
            # The broader UI twilight helper is intentionally NOT used here.
            raw=25
            status_key,indicator_key="CLOUD_SEA_OUTSIDE","IND_CLOUD_SEA_OUTSIDE"
        else:
            delta=item_data.get("cloud_base_delta"); near=item_data.get("cloud_base_near_camera"); below=item_data.get("cloud_below_camera")
            raw=50+(rh-65)*0.7+min(c_low,70)*0.28-pop*0.35-wind*2.4
            if below: raw+=15
            if near and c_low>=55: raw-=22
            if delta is not None and delta<-150: raw-=12
            status_key,indicator_key=("CLOUD_SEA_GOLD","IND_CLOUD_SEA") if raw>=86 else (("CLOUD_SEA_FAIR","IND_CLOUD_SEA_SUB") if raw>=60 else ("CLOUD_SEA_DRY","IND_DRY_AIR"))
    elif tag=="city":
        city_scene = "city" in set(item_data.get("scenes") or [])
        if sun_alt>-2:
            raw=30
            status_key,indicator_key="NIGHT_SCENE_OUTSIDE","IND_NIGHT_SCENE_OUTSIDE"
        else:
            raw=88-c_low*0.32-pop*0.45-max(0,wind-8)*1.5
            if vis>=20000: raw+=5
            elif vis<10000: raw-=(10000-vis)/1000*2.0
            if city_scene:
                status_key,indicator_key=("CITY_NIGHT_CLEAR","IND_CITY_NIGHT_CLEAR") if raw>=85 else (("CITY_NIGHT_FAIR","IND_CITY_NIGHT_HAZE") if raw>=60 else ("CITY_NIGHT_POOR","IND_CITY_NIGHT_BLOCK"))
            else:
                status_key,indicator_key=("NIGHT_SCENE_CLEAR","IND_NIGHT_SCENE_CLEAR") if raw>=85 else (("NIGHT_SCENE_FAIR","IND_NIGHT_SCENE_FAIR") if raw>=60 else ("NIGHT_SCENE_POOR","IND_NIGHT_SCENE_BLOCK"))
    else:  # mountain_view / mountain
        if sun_alt<=-6:
            raw=45-pop*0.2; status_key,indicator_key="MOUNTAIN_STABLE_NIGHT","IND_NIGHT_CLEAR"
        else:
            raw=91-c_low*0.42-c_mid*0.22-pop*0.42-max(0,wind-4)*2.0
            if vis>=30000: raw+=7
            elif vis>=20000: raw+=4
            elif vis<10000: raw-=(10000-vis)/700
            status_key,indicator_key=("MOUNTAIN_EXCELLENT_DAY","IND_PEAKS") if raw>=86 else (("MOUNTAIN_STABLE_DAY","IND_SOME_CLOUDS") if raw>=60 else ("MOUNTAIN_FOG_DAY","IND_NO_STAR"))

    if pop>=55:
        raw=min(raw,42); status_key,indicator_key="RAIN_RISK","IND_RAIN_RISK"
    score=_calibrate_score(raw,theme,item_data); score=min(score,_eligibility_cap(theme,item_data)); score=_apply_light_pollution(score,theme,item_data)
    b=item_data.get("bortle_class")
    if tag=="starlight":
        if score>=86: status_key,indicator_key="STARLIGHT_GREAT","IND_CLEAR_SKY"
        elif score>=62: status_key,indicator_key="STARLIGHT_FAIR","IND_SOME_CLOUDS"
        elif b is not None and int(b)>=6: status_key,indicator_key="STARLIGHT_LIGHT_POLLUTION","IND_LIGHT_POLLUTION"
        else: status_key,indicator_key="STARLIGHT_POOR","IND_NO_STAR"
    elif tag=="aurora" and item_data.get("kp") is not None:
        kp_val=float(item_data.get("kp") or 0)
        if kp_val>=5 and score>=72: status_key,indicator_key="AURORA_CLEAR","IND_CLEAR_SKY"
        elif score>=58: status_key,indicator_key="AURORA_FAIR","IND_SOME_CLOUDS"
        elif b is not None and int(b)>=7: status_key,indicator_key="AURORA_LIGHT_POLLUTION","IND_LIGHT_POLLUTION"
        else: status_key,indicator_key="AURORA_POOR","IND_NO_STAR"
    if item_data.get("access_open") is False: status_key,indicator_key="ACCESS_TIME_LIMITED","IND_ACCESS_LIMITED"
    factors=_build_factors(theme,item_data,lang)
    return score,get_text(status_key,lang),get_text(indicator_key,lang),status_key,indicator_key,factors

def _build_opportunity_runtime_diagnostics(spot, item_data):
    """Return runtime diagnostics for all researched Opportunities.

    Only preview_module_available Opportunities execute dedicated runtime modules.
    Other policies remain explicit so the scoring layer can cap confidence instead
    of silently falling back to a generic Theme score.
    """
    diagnostics = {}
    for opportunity in spot.get("opportunities", []) or []:
        oid = opportunity.get("opportunity_id")
        if not oid:
            continue
        policy = opportunity.get("runtime_policy") or "unclassified"
        if policy == "preview_module_available":
            result = evaluate_opportunity_modules(opportunity, item_data)
        elif policy == "minimum_sufficient_available":
            simple = evaluate_minimum_sufficient_visibility(opportunity, item_data)
            result = {
                "available": simple.get("available", False),
                "eligible": simple.get("eligible", False),
                "reason": simple.get("reason"),
                "runtime_policy": policy,
                "minimum_sufficient": True,
                "modules": {"minimum_sufficient_visibility": simple},
            }
        else:
            result = {
                "available": False,
                "eligible": False,
                "reason": policy,
                "runtime_policy": policy,
                "modules": {},
            }
        diagnostics[oid] = result
    return diagnostics


def _score_opportunity(opportunity, theme_metric, runtime_diagnostic, lang="zh-TW"):
    """Score one researched Photography Opportunity.

    The legacy Theme score is only the weather/time baseline. A score may enter
    the 80+ recommendation band only when the Opportunity has a complete
    place-specific runtime contract and every required module is available and
    eligible. Pending/prototype/insufficient policies are deliberately capped.
    """
    policy = opportunity.get("runtime_policy") or "unclassified"
    base = int(round(float((theme_metric or {}).get("score", 0) or 0)))
    factors = list((theme_metric or {}).get("factors", []) or [])
    status_key = (theme_metric or {}).get("status_key") or "STABLE_WEATHER"
    indicator_key = (theme_metric or {}).get("indicator_key") or "IND_DEFAULT"
    condition_state = "theme_baseline_only"
    score_confidence = "low"
    temporal_eligible = (theme_metric or {}).get("temporal_eligible")

    if policy == "hold":
        score = 0
        status_key = indicator_key = "OPPORTUNITY_HOLD"
        condition_state = "hold"
    elif policy == "data_insufficient":
        score = min(base, 35)
        status_key = indicator_key = "OPPORTUNITY_DATA_INSUFFICIENT"
        condition_state = "data_insufficient"
    elif policy == "module_pending":
        score = min(base, 64)
        status_key = indicator_key = "OPPORTUNITY_PARTIAL"
        condition_state = "partial_runtime_contract"
        score_confidence = "low"
    elif policy == "minimum_sufficient_available":
        diag = runtime_diagnostic or {}
        if not diag.get("available"):
            score = min(base, 45)
            status_key = indicator_key = "OPPORTUNITY_RUNTIME_DATA_MISSING"
            condition_state = "minimum_sufficient_data_missing"
        elif not diag.get("eligible"):
            score = min(base, 54)
            status_key = indicator_key = "OPPORTUNITY_SIMPLE_MISS"
            condition_state = "minimum_sufficient_conditions_miss"
            score_confidence = "medium"
        else:
            score = base
            if temporal_eligible is False:
                status_key = indicator_key = "OPPORTUNITY_OUTSIDE_TIME_WINDOW"
                condition_state = "minimum_sufficient_weather_match_outside_time_window"
                score_confidence = "medium"
            else:
                status_key = indicator_key = "OPPORTUNITY_SIMPLE_MATCH"
                condition_state = "minimum_sufficient_conditions_match"
                score_confidence = "high"
    elif policy == "prototype_pending_certification":
        score = min(base, 79)
        status_key = indicator_key = "OPPORTUNITY_PROTOTYPE"
        condition_state = "researched_prototype"
        score_confidence = "medium"
    elif policy == "preview_module_available":
        diag = runtime_diagnostic or {}
        if not diag.get("available"):
            score = min(base, 45)
            status_key = indicator_key = "OPPORTUNITY_RUNTIME_DATA_MISSING"
            condition_state = "runtime_data_missing"
        elif not diag.get("eligible"):
            score = min(base, 54)
            status_key = indicator_key = "OPPORTUNITY_CONDITION_MISS"
            condition_state = "dedicated_conditions_miss"
            score_confidence = "medium"
        else:
            score = base
            if temporal_eligible is False:
                status_key = indicator_key = "OPPORTUNITY_OUTSIDE_TIME_WINDOW"
                condition_state = "dedicated_weather_match_outside_time_window"
                score_confidence = "medium"
            else:
                status_key = indicator_key = "OPPORTUNITY_MATCH"
                condition_state = "dedicated_conditions_match"
                score_confidence = "high"
    else:
        score = min(base, 35)
        status_key = indicator_key = "OPPORTUNITY_DATA_INSUFFICIENT"
        condition_state = "unclassified"

    score = max(0, min(100, int(round(score))))
    return {
        "opportunity_id": opportunity.get("opportunity_id"),
        "opportunity_name": opportunity.get("name_zh"),
        "theme": opportunity.get("legacy_theme"),
        "score": score,
        "base_theme_score": base,
        "status_key": status_key,
        "indicator_key": indicator_key,
        "status": get_text(status_key, lang),
        "key_indicator": get_text(indicator_key, lang),
        "factors": factors,
        "runtime_policy": policy,
        "condition_state": condition_state,
        "score_confidence": score_confidence,
        "formula_confidence": opportunity.get("formula_confidence"),
        "temporal_eligible": (theme_metric or {}).get("temporal_eligible"),
        "temporal_reason": (theme_metric or {}).get("temporal_reason"),
        "runtime": runtime_diagnostic or {},
    }


def _minute_in_access_window(local_dt, hours):
    if not isinstance(hours, (list, tuple)) or len(hours) != 2:
        return None
    try:
        sh, sm = map(int, str(hours[0]).split(":"))
        eh, em = map(int, str(hours[1]).split(":"))
        cur = local_dt.hour * 60 + local_dt.minute
        start = sh * 60 + sm
        end = eh * 60 + em
        return start <= cur < end if start <= end else (cur >= start or cur < end)
    except Exception:
        return None


def _parse_mmdd(value):
    try:
        month, day = map(int, str(value).split("-"))
        datetime(2000, month, day)  # leap-year reference permits 02-29
        return month, day
    except Exception:
        return None


def _access_date_closed(spot, local_dt):
    """Return True when a Place-local calendar date is inside a curated closure range."""
    ranges = spot.get("access_closed_mmdd_ranges")
    if not isinstance(ranges, (list, tuple)) or not ranges:
        return False

    current = (local_dt.month, local_dt.day)
    for rule in ranges:
        if not isinstance(rule, dict):
            raise ValueError("invalid closed access date rule")
        start = _parse_mmdd(rule.get("start_mmdd"))
        end = _parse_mmdd(rule.get("end_mmdd"))
        if start is None or end is None:
            raise ValueError("invalid closed access date range")
        in_range = start <= current <= end if start <= end else (current >= start or current <= end)
        if in_range:
            return True
    return False


def _seasonal_access_open(spot, local_dt):
    schedule = spot.get("access_hours_seasonal")
    if not isinstance(schedule, (list, tuple)) or not schedule:
        return None

    current = (local_dt.month, local_dt.day)
    matches = []
    for rule in schedule:
        if not isinstance(rule, dict):
            raise ValueError("invalid seasonal access rule")
        start = _parse_mmdd(rule.get("start_mmdd"))
        end = _parse_mmdd(rule.get("end_mmdd"))
        if start is None or end is None:
            raise ValueError("invalid seasonal access date range")
        in_range = start <= current <= end if start <= end else (current >= start or current <= end)
        if in_range:
            matches.append(rule)

    if not matches:
        return None
    if len(matches) != 1:
        raise ValueError("overlapping seasonal access date ranges")

    windows = matches[0].get("windows")
    if not isinstance(windows, (list, tuple)) or not windows:
        raise ValueError("seasonal access rule missing windows")
    results = [_minute_in_access_window(local_dt, window) for window in windows]
    if any(result is None for result in results):
        raise ValueError("invalid seasonal access time window")
    return any(results)


def _access_open_for_spot(spot, local_dt, is_day, is_twilight):
    if _access_date_closed(spot, local_dt):
        return False

    mode = spot.get("access_mode")
    if mode == "daylight_only":
        return bool(is_day or is_twilight)

    seasonal = _seasonal_access_open(spot, local_dt)
    if seasonal is not None:
        return seasonal

    windows = spot.get("access_hours_windows")
    if isinstance(windows, (list, tuple)) and windows:
        results = [_minute_in_access_window(local_dt, window) for window in windows]
        valid = [result for result in results if result is not None]
        if valid:
            return any(valid)

    result = _minute_in_access_window(local_dt, spot.get("access_hours"))
    if result is not None:
        return result
    return True


def _build_open_meteo_url(spot):
    lat = spot.get("lat")
    lon = spot.get("lon")
    params = [
        f"latitude={lat}",
        f"longitude={lon}",
        "hourly=temperature_2m,dew_point_2m,relative_humidity_2m,cloud_cover_low,cloud_cover_mid,cloud_cover_high,wind_speed_10m,visibility,precipitation,precipitation_probability,snowfall,snow_depth,direct_normal_irradiance,is_day",
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



def _build_spatial_open_meteo_url(plan):
    points = plan.get("points", []) if plan else []
    if not points:
        return None
    latitudes = ",".join(f"{float(p['lat']):.6f}" for p in points)
    longitudes = ",".join(f"{float(p['lon']):.6f}" for p in points)
    params = [
        f"latitude={latitudes}",
        f"longitude={longitudes}",
        "hourly=relative_humidity_2m,cloud_cover_low,visibility,precipitation,wind_speed_10m",
        "past_hours=24",
        "forecast_hours=72",
        "timezone=auto",
        "timeformat=unixtime",
        "wind_speed_unit=ms",
    ]
    return "https://api.open-meteo.com/v1/forecast?" + "&".join(params)


def _fetch_spatial_weather_response(spot):
    plan = build_spatial_request_plan(spot)
    if not plan.get("points"):
        return None
    key = tuple(
        (round(float(p["lat"]), 5), round(float(p["lon"]), 5))
        for p in plan["points"]
    )
    if key in _SPATIAL_WEATHER_RESPONSE_CACHE:
        return _SPATIAL_WEATHER_RESPONSE_CACHE[key]
    raw = _request_json(_build_spatial_open_meteo_url(plan))
    indexed = index_spatial_response(plan, raw)
    _SPATIAL_WEATHER_RESPONSE_CACHE[key] = indexed
    return indexed


def _build_marine_open_meteo_url(spot):
    lat = spot.get("lat")
    lon = spot.get("lon")
    params = [
        f"latitude={lat}",
        f"longitude={lon}",
        "hourly=wave_height,wave_direction,wave_period,wind_wave_height,wind_wave_direction,wind_wave_period,swell_wave_height,swell_wave_direction,swell_wave_period,swell_wave_peak_period",
        "past_hours=24",
        "forecast_hours=72",
        "timezone=auto",
        "timeformat=unixtime",
        "cell_selection=sea",
    ]
    return "https://marine-api.open-meteo.com/v1/marine?" + "&".join(params)


def _fetch_marine_response(spot):
    if not spot_requires_marine_state(spot):
        return None
    key = (round(float(spot.get("lat")), 5), round(float(spot.get("lon")), 5))
    if key in _MARINE_RESPONSE_CACHE:
        return _MARINE_RESPONSE_CACHE[key]
    raw = _request_json(_build_marine_open_meteo_url(spot))
    indexed = index_marine_response(raw)
    _MARINE_RESPONSE_CACHE[key] = indexed
    return indexed


def _build_tide_open_meteo_url(spot):
    lat = spot.get("lat")
    lon = spot.get("lon")
    params = [
        f"latitude={lat}",
        f"longitude={lon}",
        "hourly=sea_level_height_msl",
        "past_hours=24",
        "forecast_hours=72",
        "timezone=auto",
        "timeformat=unixtime",
        "cell_selection=sea",
    ]
    return "https://marine-api.open-meteo.com/v1/marine?" + "&".join(params)


def _fetch_tide_response(spot):
    if not spot_requires_tide_state(spot):
        return None
    key = (round(float(spot.get("lat")), 5), round(float(spot.get("lon")), 5))
    if key in _TIDE_RESPONSE_CACHE:
        return _TIDE_RESPONSE_CACHE[key]
    raw = _request_json(_build_tide_open_meteo_url(spot))
    indexed = index_tide_response(raw)
    _TIDE_RESPONSE_CACHE[key] = indexed
    return indexed


def fetch_weather_for_spot(spot, lang="zh-TW", kp_rows=None):
    lat = spot.get("lat")
    lon = spot.get("lon")
    themes = spot.get("themes") or spot.get("tags", ["mountain_view"])
    if lat is None or lon is None:
        return {}

    try:
        raw = _fetch_weather_response(spot)
        hourly = raw.get("hourly", {}) or {}
        timestamps = hourly.get("time", [])
        if not timestamps:
            return {}

        try:
            spatial_index = _fetch_spatial_weather_response(spot)
        except Exception as spatial_error:
            print(f"Spatial weather fetch error for {spot.get('spot_id')}: {spatial_error}")
            spatial_index = None

        try:
            marine_index = _fetch_marine_response(spot)
        except Exception as marine_error:
            print(f"Marine weather fetch error for {spot.get('spot_id')}: {marine_error}")
            marine_index = None

        try:
            tide_index = _fetch_tide_response(spot)
        except Exception as tide_error:
            print(f"Tide fetch error for {spot.get('spot_id')}: {tide_error}")
            tide_index = None

        shinhotaka_access_provider = (
            _fetch_shinhotaka_access_provider()
            if spot.get("spot_id") == "jp-021"
            else None
        )

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
            astro = _safe_astronomy(utc_dt, lat, lon, lang)

            near_twilight = _near_twilight(local_dt, twilight_lookup, minutes=75)
            is_twilight = near_twilight or (astro["astronomy_valid"] and -8.0 <= astro["sun_elevation"] <= 8.0)
            sun_alignment = "unknown"
            if view_azimuth is not None and is_twilight and astro["astronomy_valid"] and astro["sun_azimuth"] is not None:
                diff = _angle_diff(astro["sun_azimuth"], float(view_azimuth))
                sun_alignment = "good" if diff <= view_tolerance else ("poor" if diff >= min(100, view_tolerance + 35) else "neutral")

            spatial_weather = (
                spatial_observations_for_timestamp(spatial_index, int(ts))
                if spatial_index is not None else {}
            )
            marine_forecast = (
                marine_sample_for_timestamp(marine_index, int(ts))
                if marine_index is not None else None
            )
            tide_forecast = (
                tide_sample_for_timestamp(tide_index, int(ts))
                if tide_index is not None else None
            )

            item_data = {
                "spot_id": spot.get("spot_id"),
                "timestamp": int(ts),
                "scenes": list(spot.get("scenes") or []),
                "c_low": hv("cloud_cover_low", i, 0),
                "c_low_available": hv("cloud_cover_low", i, None) is not None,
                "c_mid": hv("cloud_cover_mid", i, 0),
                "c_mid_available": hv("cloud_cover_mid", i, None) is not None,
                "c_high": hv("cloud_cover_high", i, 0),
                "c_high_available": hv("cloud_cover_high", i, None) is not None,
                "pop": hv("precipitation_probability", i, 0),
                "pop_available": hv("precipitation_probability", i, None) is not None,
                "precipitation": hv("precipitation", i, 0),
                "snowfall": hv("snowfall", i, None),
                "snow_depth": hv("snow_depth", i, None),
                "direct_normal_irradiance": hv("direct_normal_irradiance", i, None),
                "vis": hv("visibility", i, 10000),
                "vis_available": hv("visibility", i, None) is not None,
                "rh": hv("relative_humidity_2m", i, 50),
                "rh_available": hv("relative_humidity_2m", i, None) is not None,
                "wind": hv("wind_speed_10m", i, 0),
                "wind_available": hv("wind_speed_10m", i, None) is not None,
                "temp": temp,
                "temp_available": hv("temperature_2m", i, None) is not None,
                "dew": dew,
                "dew_available": hv("dew_point_2m", i, None) is not None,
                "kp": kp_val,
                "hour": local_dt.hour,
                "is_day": bool(hv("is_day", i, 1)),
                "is_twilight": is_twilight,
                "access_open": _access_open_for_spot(spot, local_dt, bool(hv("is_day", i, 1)), is_twilight),
                "cloud_base_agl": cloud_base_agl,
                "cloud_base_asl": cloud_base_asl,
                "cloud_base_delta": cloud_base_delta,
                "cloud_below_camera": cloud_base_delta >= 80,
                "cloud_base_near_camera": abs(cloud_base_delta) <= 180,
                "sun_alignment": sun_alignment,
                "bortle_class": spot.get("bortle_class"),
                "dark_sky_score": spot.get("dark_sky_score"),
                "spatial_weather": spatial_weather,
                "marine_forecast": marine_forecast,
                "tide_forecast": tide_forecast,
                **astro,
            }
            if spot.get("spot_id") == "jp-021":
                item_data["access_state"] = build_shinhotaka_access_state(
                    int(ts), shinhotaka_access_provider
                )

            opportunity_runtime = _build_opportunity_runtime_diagnostics(spot, item_data)

            theme_scores = {}
            for theme in themes:
                score, status, indicator, status_key, indicator_key, factors = evaluate_tag_condition(theme, item_data, local_dt.hour, lang)
                temporal_eligible, temporal_reason = _temporal_eligibility(theme, item_data)
                theme_scores[theme] = {
                    "score": score,
                    "status": status,
                    "status_key": status_key,
                    "key_indicator": indicator,
                    "indicator_key": indicator_key,
                    "factors": factors,
                    "temporal_eligible": temporal_eligible,
                    "temporal_reason": temporal_reason,
                }

            opportunity_scores = {}
            for opportunity in spot.get("opportunities", []) or []:
                oid = opportunity.get("opportunity_id")
                theme = opportunity.get("legacy_theme")
                if not oid or not theme:
                    continue
                theme_metric = theme_scores.get(theme)
                if theme_metric is None:
                    score, status, indicator, status_key, indicator_key, factors = evaluate_tag_condition(theme, item_data, local_dt.hour, lang)
                    temporal_eligible, temporal_reason = _temporal_eligibility(theme, item_data)
                    theme_metric = {
                        "score": score,
                        "status": status,
                        "status_key": status_key,
                        "key_indicator": indicator,
                        "indicator_key": indicator_key,
                        "factors": factors,
                        "temporal_eligible": temporal_eligible,
                        "temporal_reason": temporal_reason,
                    }
                    theme_scores[theme] = theme_metric
                opportunity_scores[oid] = _score_opportunity(
                    opportunity,
                    theme_metric,
                    opportunity_runtime.get(oid),
                    lang,
                )

            if opportunity_scores:
                best_opportunity_id = max(opportunity_scores, key=lambda oid: opportunity_scores[oid]["score"])
                best = opportunity_scores[best_opportunity_id]
                best_theme = best.get("theme") or "mountain_view"
            else:
                best_opportunity_id = None
                best_theme = max(theme_scores, key=lambda t: theme_scores[t]["score"]) if theme_scores else "mountain_view"
                best = theme_scores.get(best_theme, {
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
                "best_theme": best_theme,
                "best_opportunity_id": best_opportunity_id,
                "best_opportunity_name": best.get("opportunity_name"),
                "theme_scores": theme_scores,
                "opportunity_scores": opportunity_scores,
                "best_tag": best_theme,  # V4 compatibility
                "tag_scores": theme_scores,  # V4 compatibility
                "opportunity_runtime": opportunity_runtime,
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
                "precipitation": item_data["precipitation"],
                "precipitation_probability": item_data["pop"],
                "snowfall": item_data["snowfall"],
                "snow_depth": item_data["snow_depth"],
                "direct_normal_irradiance": item_data["direct_normal_irradiance"],
                "marine_forecast": item_data["marine_forecast"],
                "tide_forecast": item_data["tide_forecast"],
                "visibility": round(float(item_data["vis"]) / 1000, 1),
                "is_day": item_data["is_day"],
                "is_twilight": is_twilight,
                "access_open": item_data["access_open"],
                "astronomy_valid": astro["astronomy_valid"],
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
            "best_theme": best_item.get("best_theme", best_item.get("best_tag")),
            "best_opportunity_id": best_item.get("best_opportunity_id"),
            "best_opportunity_name": best_item.get("best_opportunity_name"),
            "best_tag": best_item.get("best_theme", best_item.get("best_tag")),
            "best_time": best_item.get("time", "N/A"),
            "best_time_utc": best_item.get("time_utc"),
            "reason": "Photography Weather Score V5.4",
            "position": best_item.get("status", get_text("STABLE_WEATHER", lang)),
            "key_indicator": best_item.get("key_indicator", get_text("IND_DEFAULT", lang)),
            "timezone": tz_name,
            "timezone_abbr": best_item.get("timezone_abbr"),
            "utc_offset_seconds": raw.get("utc_offset_seconds"),
            "api_elevation": raw.get("elevation"),
            "view_azimuth": view_azimuth,
            "view_tolerance": view_tolerance if view_azimuth is not None else None,
            "access_mode": spot.get("access_mode"),
            "access_note_i18n": spot.get("access_note_i18n"),
            "hourly_forecast": hourly_forecast,
        }
    except Exception as e:
        print(f"Fetch weather error for {spot.get('name_i18n', {}).get('zh-TW', spot.get('name'))}: {e}")
        return {}


def update_usa_weather():
    pass
