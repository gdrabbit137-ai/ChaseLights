#!/usr/bin/env python
"""CL-COPY-01: build data/v2/copy/fail_reason_overrides.json.

Owner ruling (2026-11-05): fail reasons are written per opportunity × metric
(spot-terrain-aware photographer language) as the STANDARD; the mechanical
metric→phrase map in assets/app.js stays as the fallback when no handwritten
entry exists.

Structure: opportunity_id -> metric -> {zh-TW, en, ja}.

The copy is authored through two layers in this script:
- BESPOKE: hand-written entries for the named showcase cases and any spot
  whose terrain warrants a line the archetype cannot express.
- ARCH_TEMPLATES: per-terrain-archetype phrases keyed by metric. Archetypes
  are classified per opportunity from its genre_template + subject/terrain
  keywords in the spot's name and navigation label, so 「山頭」 only appears
  where there really is a mountain, 「碼頭」 only at harbors, etc.

Usage:
  python data/v2/tools/build_fail_reason_overrides.py tw    # phase 1
  python data/v2/tools/build_fail_reason_overrides.py all   # phase 1+2
"""
import json
import glob
import os
import sys
import collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "data", "v2", "copy", "fail_reason_overrides.json")

# Metrics that can actually fail in the V2 evaluator (mirror of the renderer's
# V2_FAIL_PRIORITY). legacy_* contract stubs are not evaluated and get no copy.
EVAL_METRICS = [
    "precipitation", "visibility", "aod_550nm", "cloud_cover_low",
    "cloud_cover_mid", "cloud_cover_mid_and_high", "cloud_cover_total",
    "wind_speed_10m", "lcl_height_m_agl", "relative_humidity_925hpa",
    "relative_humidity_700hpa", "relative_humidity_600hpa",
    "relative_humidity_850hpa", "galactic_core_altitude",
    "sunrise_time_window", "sunset_window", "golden_hour_window",
    "blue_hour_window", "city_night_window", "light_window", "astronomical_darkness",
    "moon_illumination_fraction", "moon_illuminance_proxy", "moon_altitude",
    "moon_target_separation_deg", "wind_speed_850hpa", "wind_speed_600hpa",
    "temperature_delta_850_925_c", "temperature_delta_700_600_c",
    "water_surface_state", "seasonal_state", "river_flow_state",
    "landform_present",
]


# ---------------------------------------------------------------- bespoke ---
# CL-DATA-11: cloud-sea light window (owner ruling + clarification 2026-11-05:
# the cloud sea is visible ONLY in civil light — sun elevation > -6 deg; night
# hours never qualify regardless of the moon, no moon metric is consulted).
# Per-place wording, mountain/valley/lake/fog contexts.
_LIGHT_WINDOW_CL = {
    # CL-DATA-12 batch d/l/m: newly added light windows.
    # 祝山日出雲海 — viewed from the Zhushan sunrise platform.
    "tw-024-P02": ("已過民用光線，祝山平台下的雲海看不到",
                   "Outside civil light — the cloud sea below the Zhushan platform is invisible",
                   "市民光を過ぎて、祝山展望台下の雲海が見えません"),
    # 花東縱谷雲海 (tw-035-P06) — the East Rift valley floor.
    "tw-035-P06": ("已過民用光線，縱谷裡的雲海看不到",
                   "Outside civil light — the rift-valley cloud sea is invisible",
                   "市民光を過ぎて、縦谷の雲海が見えません"),
    # tw-047-P01 喜多麗雲海.
    "tw-047-P01": ("已過民用光線，山腳下的雲海看不到",
                   "Outside civil light — the cloud sea below the mountain is invisible",
                   "市民光を過ぎて、山裾の雲海が見えません"),
    # tw-049-P03 桃山雲海 — seen from the Taoshan summit.
    "tw-049-P03": ("已過民用光線，桃山望向的雲海一片黑",
                   "Outside civil light — the cloud sea from Taoshan is pitch dark",
                   "市民光を過ぎて、桃山から望む雲海は真っ暗です"),
    # tw-074-P01 野柳女王頭 — park daylight hours; unlit night is out of hours.
    "tw-074-P01": ("天色已暗，野柳女王頭在黑暗中看不到",
                   "After dark — the Queen's Head is invisible in darkness",
                   "日が落ちて、女王頭は闇の中で見えません"),
    "tw-001-P02": ("已過民用光線，盆地裡的雲海看不見",
                   "Outside civil light — the basin cloud sea is invisible",
                   "市民光を過ぎて、盆地の雲海が見えません"),
    "tw-004-P03": ("已過民用光線，山谷雲海一片漆黑看不到",
                   "Outside civil light — the valley cloud sea is pitch dark",
                   "市民光を過ぎて、谷の雲海は真っ暗で見えません"),
    "tw-008-P03": ("已過民用光線，看不到山谷裡的雲海",
                   "Outside civil light — no cloud sea over the valley",
                   "市民光を過ぎて、谷間の雲海が見えません"),
    "tw-014-P02": ("已過民用光線，雲瀑只剩黑漆漆一片",
                   "Outside civil light — the cloud waterfall is only darkness",
                   "市民光を過ぎて、雲の滝は真っ暗です"),
    "tw-019-P04": ("已過民用光線，群峰下的雲海看不見",
                   "Outside civil light — the cloud sea below the peaks is invisible",
                   "市民光を過ぎて、山々の下の雲海が見えません"),
    "tw-020-P02": ("已過民用光線，山谷雲海在黑暗中看不到",
                   "Outside civil light — the valley cloud sea disappears into darkness",
                   "市民光を過ぎて、谷の雲海は闇の中です"),
    "tw-021-P02": ("已過民用光線，山谷裡的雲海看不見",
                   "Outside civil light — the valley cloud sea is invisible",
                   "市民光を過ぎて、谷の雲海が見えません"),
    "tw-022-P02": ("已過民用光線，雲海與茶園山稜都看不見",
                   "Outside civil light — neither the cloud sea nor the tea ridges show",
                   "市民光を過ぎて、雲海も茶園の尾根も見えません"),
    "tw-023-P02": ("已過民用光線，山凹裡的雲海看不見",
                   "Outside civil light — the cloud sea in the hollow is invisible",
                   "市民光を過ぎて、くぼみの雲海が見えません"),
    "tw-032-P02": ("已過民用光線，露出山稜與雲海都看不到",
                   "Outside civil light — neither the emergent ridge nor the cloud sea shows",
                   "市民光を過ぎて、突き出た尾根も雲海も見えません"),
    "tw-040-P04": ("已過民用光線，山莊下方的雲海看不見",
                   "Outside civil light — the cloud sea below the hut is invisible",
                   "市民光を過ぎて、山小屋の下の雲海が見えません"),
    "tw-043-P03": ("已過民用光線，主稜下的雲海一片黑看不到",
                   "Outside civil light — the cloud sea under the main ridge is pitch dark",
                   "市民光を過ぎて、主稜下の雲海は真っ暗です"),
    "tw-082-P09": ("已過民用光線，湖面的低雲氛圍看不到",
                   "Outside civil light — the low-cloud mood over the lake is invisible",
                   "市民光を過ぎて、湖面の低雲の雰囲気が見えません"),
    "tw-086-P01": ("已過民用光線，霧中的橋影看不到",
                   "Outside civil light — the bridge in the fog is invisible",
                   "市民光を過ぎて、霧の中の橋は見えません"),
    # us-020-P02: redwood fog forest — the fog is only visible where light falls.
    "us-020-P02": ("已過民用光線，霧中的紅木森林看不到",
                   "Outside civil light — the fogged redwoods are invisible",
                   "市民光を過ぎて、霧のかかるレッドウッドの森は見えません"),
}
# Hand-written entries: opportunity_id -> metric -> {zh-TW, en, ja}.
BESPOKE = {
    # 淡水漁人碼頭 — harbor pier, no peaks: the low cloud reads as one grey mass.
    "tw-003-P01": {
        "cloud_cover_low": {
            "zh-TW": "低雲太厚，碼頭與水面灰成一片",
            "en": "Thick low cloud turns the wharf and the water into one grey mass",
            "ja": "低層雲が厚く、桟橋も水面も灰色に沈みます",
        },
    },
    # 大屯山雲海 — views down into the Taipei Basin; LCL decides the sea.
    "tw-001-P02": {
        "lcl_height_m_agl": {
            "zh-TW": "雲底太高，盆地裡沒有雲海",
            "en": "Cloud base too high — no sea of clouds fills the basin",
            "ja": "雲底が高すぎて、盆地に雲海がありません",
        },
        "cloud_cover_low": {
            "zh-TW": "低雲淹得太高，把該有的雲海蓋成一片白",
            "en": "Low cloud piled too high buries the would-be sea of clouds",
            "ja": "低層雲が高く積もり、雲海を白く覆ってしまいます",
        },
    },
    # 大屯山夕照山稜 — ridge sunset: low cloud swallows the ridge itself.
    "tw-001-P01": {
        "cloud_cover_low": {
            "zh-TW": "低雲太厚，山稜整條埋進雲裡",
            "en": "Thick low cloud buries the whole ridgeline",
            "ja": "低層雲が厚く、稜線全体が雲に埋もれます",
        },
    },
    # 象山 101 天際線夜景 — window fails while the sky is still too bright.
    "tw-002-P02": {
        "city_night_window": {
            "zh-TW": "還沒暗到夜景好看",
            "en": "Not dark enough yet for the skyline to look its best",
            "ja": "夜景がきれいに見えるほどまだ暗くなっていません",
        },
    },
    "tw-002-P03": {
        "city_night_window": {
            "zh-TW": "還沒暗到夜景好看",
            "en": "Not dark enough yet for the skyline to look its best",
            "ja": "夜景がきれいに見えるほどまだ暗くなっていません",
        },
    },
    # 合歡山主峰雲海／奇萊主稜雲海 — alpine cloud sea below the ridge.
    "tw-019-P02": {
        "lcl_height_m_agl": {
            "zh-TW": "雲底太高，山谷裡撐不起雲海",
            "en": "Cloud base too high — no sea of clouds holds in the valleys",
            "ja": "雲底が高すぎて、谷に雲海が張りません",
        },
    },
    # 七星潭海岸銀河 — seaside Milky Way, moonlight washes the horizon band.
    "tw-036-P02": {
        "moon_illumination_fraction": {
            "zh-TW": "月光太亮，海岸邊的銀河帶被洗掉",
            "en": "Moonlight too bright — it washes out the Milky Way over the coast",
            "ja": "月光が強く、海岸沿いの天の川が消えてしまいます",
        },
    },
}

# -------------------------------------------------------- archetype phrases --
# Per-terrain-archetype copy, keyed archetype -> metric -> (zh, en, ja).
# Archetype names the terrain a photographer stands in; phrases name the
# concrete photographic consequence there.
A = collections.defaultdict(dict)

# Mountain / ridge viewpoints (real peaks and ridgelines).
A["mountain"]["precipitation"] = ("山區下雨起霧，稜線整個被雨幕蓋住",
                                  "Rain and mist wrap the ridge — nothing shows through",
                                  "雨と霧で稜線がすっぽり包まれ、よく見えません")
A["mountain"]["visibility"] = ("大霧罩住整片山頭，什麼都看不見",
                               "Dense fog swallows the whole ridge — nothing is visible",
                               "濃霧が山全体を覆い、何も見えません")
A["mountain"]["aod_550nm"] = ("霾太重，遠山層次全部糊掉",
                              "Haze is heavy — the far ridgelines lose all their layers",
                              "霞がひどく、遠くの山の重なりがぼやけます")
A["mountain"]["cloud_cover_low"] = ("低雲太厚，山頭沒入雲中",
                                    "Thick low cloud swallows the peaks",
                                    "低層雲が厚く、山頂が雲に埋もれます")
A["mountain"]["cloud_cover_mid"] = ("中高雲太厚，山頭上空一片灰白",
                                    "Mid and high cloud cover the peaks in flat grey",
                                    "中・上層雲が厚く、山の上空が灰色一色です")
A["mountain"]["cloud_cover_mid_and_high"] = A["mountain"]["cloud_cover_mid"]
A["mountain"]["cloud_cover_total"] = ("雲層太厚，整個山景被蓋成灰白",
                                      "Thick cloud flattens the whole mountain view to grey",
                                      "雲が厚く、山景色が灰色に潰れます")
A["mountain"]["wind_speed_10m"] = ("風太大，稜線上腳架都快站不穩",
                                   "Too windy on the ridge — even the tripod struggles",
                                   "風が強すぎて、稜線上では三脚も安定しません")
A["mountain"]["relative_humidity_925hpa"] = ("水汽太重，山裡容易起霧",
                                             "Very moist air — fog builds up easily in the mountains",
                                             "湿気が多く、山は霧が出やすいです")
A["mountain"]["relative_humidity_850hpa"] = A["mountain"]["relative_humidity_925hpa"]
A["mountain"]["relative_humidity_700hpa"] = A["mountain"]["relative_humidity_925hpa"]
A["mountain"]["relative_humidity_600hpa"] = A["mountain"]["relative_humidity_925hpa"]
A["mountain"]["sunrise_time_window"] = ("現在不在日出時段，等不到第一道曙光打上山頭",
                                        "Outside the sunrise window — the first light has not reached the peaks",
                                        "日の出の時間帯ではないため、山頂に最初の光が届きません")
A["mountain"]["sunset_window"] = ("現在不在日落時段，山稜上的暖光已經（或還沒）出現",
                                  "Outside the sunset window — no warm light on the ridgeline now",
                                  "日の入りの時間帯ではないため、稜線に暖かい光が当たりません")
A["mountain"]["golden_hour_window"] = ("現在不在黃金時段，山景光線平淡",
                                       "Outside the golden hour — the light on the mountains is flat",
                                       "ゴールデンアワーではないため、山の光が平坦です")
A["mountain"]["blue_hour_window"] = ("現在不在藍調時段，山景色溫不對",
                                     "Outside the blue hour — the mountain tones are not there",
                                     "ブルーアワーではないため、山の色合いがまとまりません")
A["mountain"]["city_night_window"] = ("還沒暗到夜景好看，山下的燈火不明顯",
                                      "Not dark enough yet for the city lights below to show",
                                      "夜景がきれいに見えるほどまだ暗くなく、下界の灯りがぼんやりです")
A["mountain"]["astronomical_darkness"] = ("天還沒全暗（或已經天亮），星空不見了",
                                          "Not fully dark yet (or already dawn) — the stars are gone",
                                          "完全に暗くなっていない（または夜明け）ため、星空が見えません")
A["mountain"]["galactic_core_altitude"] = ("銀河核心還在地平線下，拍不到銀河帶",
                                           "The galactic core is still below the horizon — no Milky Way band to shoot",
                                           "銀河の中心はまだ地平線下で、天の川の帯が撮れません")
A["mountain"]["moon_illumination_fraction"] = ("月光太亮，星空被洗掉",
                                               "Moonlight too bright — it washes out the stars",
                                               "月光が強く、星空が消えてしまいます")
A["mountain"]["moon_illuminance_proxy"] = A["mountain"]["moon_illumination_fraction"]
A["mountain"]["moon_altitude"] = ("月亮位置不理想，月光干擾畫面",
                                  "The moon is poorly placed — its light interferes with the frame",
                                  "月の位置が良くなく、月光が写り込みます")
A["mountain"]["moon_target_separation_deg"] = ("月亮離拍攝方向太近，月光壓過星空",
                                               "The moon sits too close to the shooting direction — moonlight overpowers the stars",
                                               "月が撮影方向に近すぎて、月光が星空を押さえます")
A["mountain"]["wind_speed_850hpa"] = ("高空風太強，雲層被吹得變化太快",
                                      "Strong upper-level winds keep the cloud deck changing fast",
                                      "上空の風が強く、雲の動きが速すぎます")
A["mountain"]["wind_speed_600hpa"] = A["mountain"]["wind_speed_850hpa"]
A["mountain"]["temperature_delta_850_925_c"] = ("大氣不穩定，雲層可能整片翻掉",
                                                "Unstable atmosphere — the cloud deck may turn over wholesale",
                                                "大気が不安定で、雲の層が崩れやすいです")
A["mountain"]["temperature_delta_700_600_c"] = A["mountain"]["temperature_delta_850_925_c"]
A["mountain"]["seasonal_state"] = ("季節不對，山頭目前沒有該有的樣子",
                                   "Wrong season — the peaks lack their seasonal look",
                                   "季節が合わず、山頂に狙いの姿がありません")
A["mountain"]["landform_present"] = ("需要的地形條件（雪景、霧凇等）目前不成立",
                                     "The landform condition (snow, rime, etc.) is not met right now",
                                     "狙いの地形条件（雪や霧氷など）が今は整っていません")

# Cloud-sea opportunities (viewing DOWN onto a cloud deck).
A["cloudsea"]["precipitation"] = ("山區降雨，雲海條件整個亂掉",
                                  "Rain in the mountains wrecks the cloud-sea setup",
                                  "山の雨で雲海の条件が崩れています")
A["cloudsea"]["visibility"] = ("大霧混著雲，雲海邊界整片白",
                               "Fog blends into the deck — the cloud sea loses its edges",
                               "霧と雲が混ざり、雲海の境目が真っ白です")
A["cloudsea"]["aod_550nm"] = ("霾太重，雲海像蒙上一層灰",
                              "Haze is heavy — the cloud sea looks veiled in grey",
                              "霞がひどく、雲海が灰色ににじみます")
A["cloudsea"]["cloud_cover_low"] = ("低雲淹得太高，把該有的雲海蓋成一片白",
                                    "Low cloud piled too high buries the would-be sea of clouds",
                                    "低層雲が高く積もり、雲海を白く覆ってしまいます")
A["cloudsea"]["lcl_height_m_agl"] = ("雲底太高，山谷裡沒有雲海",
                                     "Cloud base too high — no sea of clouds sits in the valleys",
                                     "雲底が高すぎて、谷に雲海がありません")
A["cloudsea"]["relative_humidity_925hpa"] = ("水汽不夠，雲海凝不起來",
                                             "Air too dry — the sea of clouds will not condense",
                                             "湿気が足りず、雲海ができにくいです")
A["cloudsea"]["relative_humidity_850hpa"] = A["cloudsea"]["relative_humidity_925hpa"]
A["cloudsea"]["temperature_delta_850_925_c"] = ("大氣不穩定，雲海可能整片翻散",
                                                "Unstable atmosphere — the sea of clouds may break apart",
                                                "大気が不安定で、雲海が崩れやすいです")
A["cloudsea"]["wind_speed_850hpa"] = ("高空風太強，雲海被吹散撐不住",
                                      "Strong upper-level winds scatter the sea of clouds",
                                      "上空の風が強く、雲海が流されてしまいます")
A["cloudsea"]["sunrise_time_window"] = ("現在不在日出時段，雲海沒有染色的時刻",
                                        "Outside the sunrise window — the cloud sea is not catching color now",
                                        "日の出の時間帯ではなく、雲海が色づく時間ではありません")
A["cloudsea"]["galactic_core_altitude"] = ("銀河核心還在地平線下，拍不到銀河帶",
                                           "The galactic core is still below the horizon — no Milky Way band to shoot",
                                           "銀河の中心はまだ地平線下で、天の川の帯が撮れません")

# Harbor / pier / riverside wharf viewpoints.
A["harbor"]["precipitation"] = ("雨下個不停，碼頭與水面灰成一片",
                                "Steady rain turns the pier and the water into one grey wash",
                                "雨が降り続き、桟橋も水面も灰色にぼやけます")
A["harbor"]["visibility"] = ("大霧籠罩，碼頭對面的景都看不見",
                             "Dense fog — nothing across the water from the pier is visible",
                             "濃霧で、桟橋から対岸がまったく見えません")
A["harbor"]["aod_550nm"] = ("空氣混濁，對岸與海平線灰成一片",
                            "Hazy air blurs the far shore and the horizon into one grey band",
                            "大気が霞み、対岸も水平線も灰色にぼやけます")
A["harbor"]["cloud_cover_low"] = ("低雲太厚，碼頭與水面灰成一片",
                                  "Thick low cloud turns the pier and the water into one grey mass",
                                  "低層雲が厚く、桟橋も水面も灰色に沈みます")
A["harbor"]["cloud_cover_mid"] = ("中高雲太厚，港口上空一片灰白",
                                  "Mid and high cloud flatten the sky over the port",
                                  "中・上層雲が厚く、港の空が灰色一色です")
A["harbor"]["cloud_cover_mid_and_high"] = A["harbor"]["cloud_cover_mid"]
A["harbor"]["cloud_cover_total"] = ("雲層太厚，水面倒影也跟著灰掉",
                                    "Thick cloud kills the reflections on the water too",
                                    "雲が厚く、水面の反射も灰色になります")
A["harbor"]["wind_speed_10m"] = ("風太大，水面碎掉、映不出倒影",
                                 "Too windy — the water shatters and will not reflect",
                                 "風が強すぎて水面が荒れ、反射が写りません")
A["harbor"]["sunset_window"] = ("現在不在日落時段，港邊等不到晚霞",
                                "Outside the sunset window — no glow over the harbor now",
                                "日の入りの時間帯ではなく、港に夕焼けが届きません")
A["harbor"]["blue_hour_window"] = ("現在不在藍調時段，港邊的燈光還不成戲",
                                   "Outside the blue hour — the harbor lights do not sing yet",
                                   "ブルーアワーではなく、港の灯りが映えません")
A["harbor"]["city_night_window"] = ("還沒暗到夜景好看，港區的燈火不夠亮",
                                    "Not dark enough yet for the harbor lights to look their best",
                                    "夜景がきれいに見えるほど暗くなっておらず、港の灯りが弱いです")
A["harbor"]["water_surface_state"] = ("水面狀態不佳，倒影拍不成",
                                      "The water surface is wrong — no reflections to shoot",
                                      "水面の状態が良くなく、反射が撮れません")

# Coast / beach / cape viewpoints.
A["coast"]["precipitation"] = ("雨太大，海邊視線一片模糊",
                               "Heavy rain blurs the whole coastline",
                               "雨が強く、海岸の視界がぼやけます")
A["coast"]["visibility"] = ("海霧太重，遠處海平線整片白",
                            "Sea fog is heavy — the horizon is a wall of white",
                            "海霧が濃く、水平線が真っ白です")
A["coast"]["aod_550nm"] = ("空氣混濁，海平線看不清",
                           "Hazy air — the horizon is not readable",
                           "大気が霞み、水平線がはっきりしません")
A["coast"]["cloud_cover_low"] = ("低雲太厚，海面整片灰白",
                                 "Thick low cloud turns the sea into flat grey",
                                 "低層雲が厚く、海面が灰色に沈みます")
A["coast"]["cloud_cover_mid"] = ("中高雲太厚，海岸上空一片灰白",
                                 "Mid and high cloud flatten the sky over the coast",
                                 "中・上層雲が厚く、海岸の空が灰色一色です")
A["coast"]["cloud_cover_mid_and_high"] = A["coast"]["cloud_cover_mid"]
A["coast"]["cloud_cover_total"] = ("雲層太厚，海景被蓋成一片灰",
                                   "Thick cloud flattens the whole seascape to grey",
                                   "雲が厚く、海景色が灰色に潰れます")
A["coast"]["wind_speed_10m"] = ("風太大，浪花亂飛、畫面拍不穩",
                                "Too windy — spray blows everywhere and the frame shakes",
                                "風が強すぎて飛沫が乱れ、写真がぶれます")
A["coast"]["sunset_window"] = ("現在不在日落時段，海面上的火燒雲看不到",
                               "Outside the sunset window — no burning sky over the sea now",
                               "日の入りの時間帯ではなく、海に夕焼けが広がりません")
A["coast"]["sunrise_time_window"] = ("現在不在日出時段，等不到曙光打上海面",
                                     "Outside the sunrise window — the first light has not hit the water",
                                     "日の出の時間帯ではなく、海に最初の光が届きません")
A["coast"]["blue_hour_window"] = ("現在不在藍調時段，海岸色調不對",
                                  "Outside the blue hour — the coastal tones are not there",
                                  "ブルーアワーではなく、海岸の色合いがまとまりません")
A["coast"]["galactic_core_altitude"] = ("銀河核心還在地平線下，拍不到銀河帶",
                                        "The galactic core is still below the horizon — no Milky Way band over the sea",
                                        "銀河の中心はまだ地平線下で、海の上の天の川が撮れません")
A["coast"]["astronomical_darkness"] = ("天還沒全暗（或已經天亮），星空不見了",
                                       "Not fully dark yet (or already dawn) — the stars are gone",
                                       "完全に暗くなっていない（または夜明け）ため、星空が見えません")
A["coast"]["moon_illumination_fraction"] = ("月光太亮，海邊星空被洗掉",
                                            "Moonlight too bright — it washes out the coastal night sky",
                                            "月光が強く、海辺の星空が消えてしまいます")
A["coast"]["moon_illuminance_proxy"] = A["coast"]["moon_illumination_fraction"]
A["coast"]["moon_altitude"] = ("月亮位置不理想，月光干擾畫面",
                               "The moon is poorly placed — its light interferes with the frame",
                               "月の位置が良くなく、月光が写り込みます")
A["coast"]["moon_target_separation_deg"] = ("月亮離拍攝方向太近，月光壓過星空",
                                            "The moon sits too close to the shooting direction — moonlight overpowers the stars",
                                            "月が撮影方向に近すぎて、月光が星空を押さえます")

# Lake / pond / reservoir viewpoints (reflection matters).
A["lake"]["precipitation"] = ("雨落個不停，湖面與倒影都糊掉",
                              "Steady rain blurs the lake surface and its reflections",
                              "雨が降り続き、湖面も反射もぼやけます")
A["lake"]["visibility"] = ("大霧蓋住湖面，對岸看不見",
                           "Dense fog buries the lake — the far shore is gone",
                           "濃霧が湖面を覆い、対岸が見えません")
A["lake"]["aod_550nm"] = ("空氣混濁，遠景與湖面倒影都灰掉",
                          "Hazy air greys out the far view and the lake reflections",
                          "大気が霞み、遠景も湖面の反射も灰色です")
A["lake"]["cloud_cover_low"] = ("低雲太厚，湖面只映到一片灰",
                                "Thick low cloud leaves the lake reflecting bare grey",
                                "低層雲が厚く、湖面は灰色だけを映します")
A["lake"]["cloud_cover_mid"] = ("中高雲太厚，湖面上空一片灰白",
                                "Mid and high cloud flatten the sky above the lake",
                                "中・上層雲が厚く、湖の上空が灰色一色です")
A["lake"]["cloud_cover_mid_and_high"] = A["lake"]["cloud_cover_mid"]
A["lake"]["cloud_cover_total"] = ("雲層太厚，湖面倒影色調灰掉",
                                  "Thick cloud greys out the reflections on the lake",
                                  "雲が厚く、湖面の反射の色が濁ります")
A["lake"]["wind_speed_10m"] = ("風太大，湖面不平，倒影拍不成",
                               "Too windy — the lake surface ripples and will not mirror",
                               "風が強すぎて湖面がざわつき、反射が写りません")
A["lake"]["water_surface_state"] = ("水面狀態不佳，倒影拍不成",
                                    "The water surface is wrong — no reflections to shoot",
                                    "水面の状態が良くなく、反射が撮れません")
A["lake"]["sunset_window"] = ("現在不在日落時段，湖面染色的時刻不對",
                              "Outside the sunset window — the lake is not catching color now",
                              "日の入りの時間帯ではなく、湖面が色づきません")
A["lake"]["blue_hour_window"] = ("現在不在藍調時段，湖邊的色調不對",
                                 "Outside the blue hour — the lakeside tones are not there",
                                 "ブルーアワーではなく、湖畔の色合いがまとまりません")
A["lake"]["galactic_core_altitude"] = ("銀河核心還在地平線下，拍不到銀河倒影",
                                       "The galactic core is still below the horizon — no Milky Way to mirror",
                                       "銀河の中心はまだ地平線下で、湖に映る天の川が撮れません")
A["lake"]["astronomical_darkness"] = ("天還沒全暗（或已經天亮），星空倒影不見了",
                                      "Not fully dark yet (or already dawn) — the mirrored stars are gone",
                                      "完全に暗くなっていない（または夜明け）ため、映り込む星空が見えません")
A["lake"]["moon_illumination_fraction"] = ("月光太亮，星空與倒影都被洗掉",
                                           "Moonlight too bright — it washes out the stars and their reflection",
                                           "月光が強く、星空も湖面に映る星も消えます")
A["lake"]["moon_illuminance_proxy"] = A["lake"]["moon_illumination_fraction"]
A["lake"]["moon_altitude"] = ("月亮位置不理想，月光干擾畫面",
                              "The moon is poorly placed — its light interferes with the frame",
                              "月の位置が良くなく、月光が写り込みます")
A["lake"]["moon_target_separation_deg"] = ("月亮離拍攝方向太近，月光壓過星空",
                                           "The moon sits too close to the shooting direction — moonlight overpowers the stars",
                                           "月が撮影方向に近すぎて、月光が星空を押さえます")

# Waterfall / river / stream viewpoints.
A["river"]["precipitation"] = ("雨太大，水花與雨幕讓主體看不清",
                               "Heavy rain — spray and rain veils swallow the subject",
                               "雨が強く、水しぶきと雨で主体がよく見えません")
A["river"]["visibility"] = ("水霧太重，主體整個糊掉",
                            "Heavy mist from the falls blurs the whole subject",
                            "水霧が濃く、主体がぼやけて見えません")
A["river"]["aod_550nm"] = ("空氣混濁，遠景糊成一片",
                           "Hazy air blurs the distant view into a wash",
                           "大気が霞み、遠景がぼやけます")
A["river"]["cloud_cover_low"] = ("低雲太厚，溪谷光線整個悶掉",
                                 "Thick low cloud dulls the light in the gorge",
                                 "低層雲が厚く、渓谷の光がくすみます")
A["river"]["cloud_cover_mid"] = ("中高雲太厚，天空一片灰白",
                                 "Mid and high cloud flatten the sky to grey",
                                 "中・上層雲が厚く、空が灰色一色です")
A["river"]["cloud_cover_mid_and_high"] = A["river"]["cloud_cover_mid"]
A["river"]["cloud_cover_total"] = ("雲層太厚，光線平淡沒有層次",
                                   "Thick cloud makes the light flat and lifeless",
                                   "雲が厚く、光に表情が出ません")
A["river"]["wind_speed_10m"] = ("風太大，長曝容易晃",
                                "Too windy — long exposures shake",
                                "風が強すぎて、長時間露光でぶれます")
A["river"]["river_flow_state"] = ("河川水量不對，水流樣子不合拍攝條件",
                                  "The river level is wrong for the shot",
                                  "河川の水量が合わず、狙いの流れになりません")

# City / skyline / night viewpoints.
A["city"]["precipitation"] = ("下雨天際線全被雨幕蓋住",
                              "Rain veils the whole skyline",
                              "雨でスカイラインが雨幕に隠れます")
A["city"]["visibility"] = ("大霧讓遠處高樓只剩淡淡輪廓",
                           "Dense fog leaves the far towers as faint outlines",
                           "濃霧で遠くの高層ビルがうっすらとしか見えません")
A["city"]["aod_550nm"] = ("空氣混濁，天際線灰矇矇",
                          "Hazy air turns the skyline a murky grey",
                          "大気が霞み、スカイラインが灰色ににじみます")
A["city"]["cloud_cover_total"] = ("雲層太厚，天際線被壓得灰暗",
                                  "Thick cloud presses the skyline into dull grey",
                                  "雲が厚く、スカイラインが暗い灰色に潰れます")
A["city"]["cloud_cover_mid"] = ("中高雲太厚，暮色少了層次",
                                "Mid and high cloud strip the dusk of its layers",
                                "中・上層雲が厚く、夕暮れの表情が失われます")
A["city"]["cloud_cover_mid_and_high"] = A["city"]["cloud_cover_mid"]
A["city"]["cloud_cover_low"] = ("低雲太厚，天際線被蓋住",
                                "Thick low cloud caps the skyline",
                                "低層雲が厚く、スカイラインを覆います")
A["city"]["city_night_window"] = ("現在不是好看的夜景時段，天色還不對",
                                  "Not the right hour for the night view — the sky is still wrong",
                                  "夜景が映える時間帯ではなく、空の明るさが合いません")
A["city"]["blue_hour_window"] = ("現在不在藍調時段，天色還不對",
                                 "Outside the blue hour — the sky is not in its good color yet",
                                 "ブルーアワーではなく、空の色が合いません")
A["city"]["wind_speed_10m"] = ("風太大，燈光長曝容易晃",
                               "Too windy — long exposures of the lights shake",
                               "風が強すぎて、長時間露光でぶれます")

# Field / grassland / plantation viewpoints.
A["field"]["precipitation"] = ("下雨草原全濕，視線也模糊",
                               "Rain soaks the whole field and blurs the view",
                               "雨で一面の草原が濡れ、視界もぼやけます")
A["field"]["visibility"] = ("大霧讓整片草原變成一片白",
                            "Dense fog turns the whole grassland into white nothing",
                            "濃霧で草原全体が真っ白になります")
A["field"]["aod_550nm"] = ("空氣混濁，遠景像蒙上灰紗",
                           "Hazy air veils the distance like grey gauze",
                           "大気が霞み、遠景が灰色のベール越しのようです")
A["field"]["cloud_cover_low"] = ("低雲太厚，整片草原光線灰暗",
                                 "Thick low cloud dulls the light across the grassland",
                                 "低層雲が厚く、草原の光がくすみます")
A["field"]["cloud_cover_mid"] = ("中高雲太厚，天空一片灰白",
                                 "Mid and high cloud flatten the sky to grey",
                                 "中・上層雲が厚く、空が灰色一色です")
A["field"]["cloud_cover_mid_and_high"] = A["field"]["cloud_cover_mid"]
A["field"]["cloud_cover_total"] = ("雲層太厚，光線平淡沒有層次",
                                   "Thick cloud makes the light flat and lifeless",
                                   "雲が厚く、光に表情が出ません")
A["field"]["wind_speed_10m"] = ("風太大，草浪狂搖拍不穩",
                                "Too windy — the grass surges and the frame shakes",
                                "風が強すぎて草が激しく揺れ、写真がぶれます")
A["field"]["seasonal_state"] = ("季節不對，花季（或轉色期）還沒到",
                                "Wrong season — the bloom (or color turn) has not come yet",
                                "季節が合わず、花の季節（または色づき）がまだです")

# Geology / badland / rock formations.
A["geology"]["precipitation"] = ("雨中岩面濕滑，地貌細節全被雨幕蓋住",
                                 "Rain slicks the rock and veils the landform detail",
                                 "雨で岩面が濡れ、地形の細部が雨に隠れます")
A["geology"]["visibility"] = ("霧把岩層紋理整個糊掉",
                              "Fog blurs out all the rock texture",
                              "霧で岩の紋様がぼやけてしまいます")
A["geology"]["aod_550nm"] = ("空氣混濁，地貌細節像蒙上一層灰",
                             "Hazy air lays a grey film over the landform detail",
                             "大気が霞み、地形の細部が灰色ににじみます")
A["geology"]["cloud_cover_low"] = ("低雲太厚，岩面紋理看不出立體感",
                                   "Thick low cloud flattens the rock texture",
                                   "低層雲が厚く、岩面の立体感が出ません")
A["geology"]["cloud_cover_mid"] = ("中高雲太厚，天空一片灰白",
                                   "Mid and high cloud flatten the sky to grey",
                                   "中・上層雲が厚く、空が灰色一色です")
A["geology"]["cloud_cover_mid_and_high"] = A["geology"]["cloud_cover_mid"]
A["geology"]["cloud_cover_total"] = ("雲層太厚，地貌光線平淡",
                                     "Thick cloud makes the landform light flat",
                                     "雲が厚く、地形の光が平坦です")
A["geology"]["landform_present"] = ("主體地貌目前不在該有的狀態",
                                    "The landform is not in its shootable state right now",
                                    "地形が今は狙える状態にありません")

# Canyon / gorge overlooks.
A["canyon"]["precipitation"] = ("雨太大，峽谷整個被雨幕蓋住",
                                "Heavy rain veils the whole canyon",
                                "雨が強く、峡谷が雨に隠れます")
A["canyon"]["visibility"] = ("大霧灌進峽谷，谷底看不見",
                             "Fog pours into the canyon — the gorge floor is gone",
                             "霧が峡谷に流れ込み、谷底が見えません")
A["canyon"]["aod_550nm"] = ("霾太重，峽谷層次全部糊掉",
                            "Haze is heavy — the canyon loses all its layers",
                            "霞がひどく、峡谷の重なりがぼやけます")
A["canyon"]["cloud_cover_mid"] = ("中高雲太厚，峽谷光線灰暗",
                                  "Mid and high cloud dull the canyon light",
                                  "中・上層雲が厚く、峡谷の光がくすみます")
A["canyon"]["cloud_cover_mid_and_high"] = A["canyon"]["cloud_cover_mid"]
A["canyon"]["cloud_cover_total"] = ("雲層太厚，峽谷被蓋成灰白",
                                    "Thick cloud flattens the canyon to grey",
                                    "雲が厚く、峡谷が灰色に潰れます")
A["canyon"]["cloud_cover_low"] = ("低雲太厚，谷裡積著一層灰白",
                                  "Thick low cloud pools as a grey layer in the gorge",
                                  "低層雲が厚く、谷に灰色の層が溜まります")

# Generic fallback archetype (unclassified).
A["default"]["precipitation"] = ("下大雨視線不清",
                                 "Heavy rain — the view is not clear",
                                 "大雨で視界が悪く、よく見えません")
A["default"]["visibility"] = ("大霧看不到",
                              "Fog or haze — you cannot see clearly",
                              "霧や霞がひどく、よく見えません")
A["default"]["aod_550nm"] = ("空氣混濁，遠景看不清",
                             "Hazy air blurs the distant view",
                             "大気が霞み、遠景がよく見えません")
A["default"]["cloud_cover_low"] = ("低雲太厚，遮蔽景觀",
                                   "Thick low cloud hides the view",
                                   "低層雲が厚く、景色を覆います")
A["default"]["cloud_cover_mid"] = ("中高雲太厚，天空一片灰白",
                                   "Mid and high cloud flatten the sky to grey",
                                   "中・上層雲が厚く、空が灰色一色です")
A["default"]["cloud_cover_mid_and_high"] = A["default"]["cloud_cover_mid"]
A["default"]["cloud_cover_total"] = ("雲層太厚，天空被蓋成灰白",
                                     "Thick cloud flattens the sky to grey",
                                     "雲が厚く、空が灰色に潰れます")
A["default"]["wind_speed_10m"] = ("風太大，畫面容易晃",
                                  "Too windy — the camera shakes",
                                  "風が強すぎて、写真がブレます")
A["default"]["lcl_height_m_agl"] = ("雲底高度不合，雲況不對",
                                    "The cloud base is at the wrong height",
                                    "雲底の高さが合わず、雲の状態が良くありません")
A["default"]["relative_humidity_925hpa"] = ("水汽太重，容易起霧",
                                            "Very moist air — fog is likely",
                                            "湿気が多く、霧が出やすいです")
A["default"]["relative_humidity_850hpa"] = A["default"]["relative_humidity_925hpa"]
A["default"]["relative_humidity_700hpa"] = A["default"]["relative_humidity_925hpa"]
A["default"]["relative_humidity_600hpa"] = A["default"]["relative_humidity_925hpa"]
A["default"]["galactic_core_altitude"] = ("銀河核心還在地平線下，拍不到銀河帶",
                                          "The galactic core is still below the horizon — no Milky Way band to shoot",
                                          "銀河の中心はまだ地平線下で、天の川の帯が撮れません")
A["default"]["sunrise_time_window"] = ("現在不在日出時段",
                                       "Outside the sunrise window",
                                       "日の出の時間帯ではありません")
A["default"]["sunset_window"] = ("現在不在日落時段",
                                 "Outside the sunset window",
                                 "日の入りの時間帯ではありません")
A["default"]["golden_hour_window"] = ("現在不在黃金時段，光線不對",
                                      "Outside the golden hour — the light is wrong",
                                      "ゴールデンアワーではなく、光が合いません")
A["default"]["blue_hour_window"] = ("現在不在藍調時段，天色不對",
                                    "Outside the blue hour — the sky tone is wrong",
                                    "ブルーアワーではなく、空の色が合いません")
A["default"]["city_night_window"] = ("還沒暗到夜景好看",
                                     "Not dark enough yet for the night view to look its best",
                                     "夜景がきれいに見えるほど暗くなっていません")
A["default"]["astronomical_darkness"] = ("天還沒全暗（或已經天亮），星空不見了",
                                         "Not fully dark yet (or already dawn) — the stars are gone",
                                         "完全に暗くなっていない（または夜明け）ため、星空が見えません")
A["default"]["moon_illumination_fraction"] = ("月光太亮，星空不明顯",
                                              "Moonlight too bright for the stars",
                                              "月光が強く、星空が見えません")
A["default"]["moon_illuminance_proxy"] = A["default"]["moon_illumination_fraction"]
A["default"]["moon_altitude"] = ("月亮位置不理想",
                                 "The moon is not in the right position",
                                 "月の位置が良くありません")
A["default"]["moon_target_separation_deg"] = ("月亮離拍攝方向太近，月光干擾",
                                              "The moon sits too close to the shooting direction",
                                              "月が撮影方向に近すぎます")
A["default"]["wind_speed_850hpa"] = ("高空風太強，雲層變化快",
                                     "Strong upper-level winds — clouds move fast",
                                     "上空の風が強く、雲の動きが速いです")
A["default"]["wind_speed_600hpa"] = A["default"]["wind_speed_850hpa"]
A["default"]["temperature_delta_850_925_c"] = ("大氣不穩定",
                                               "Unstable atmosphere",
                                               "大気が不安定です")
A["default"]["temperature_delta_700_600_c"] = A["default"]["temperature_delta_850_925_c"]
A["default"]["water_surface_state"] = ("水面狀態不佳",
                                       "The water surface is not right",
                                       "水面の状態が良くありません")
A["default"]["seasonal_state"] = ("目前不是合適的季節",
                                  "Not the right season yet",
                                  "まだ適した季節ではありません")
A["default"]["river_flow_state"] = ("河川狀態不佳",
                                    "The river conditions are not right",
                                    "河川の状態が良くありません")
A["default"]["landform_present"] = ("地形條件不符",
                                    "The landform conditions are not met",
                                    "地形の条件を満たしていません")

# Window metrics shared by every archetype (one natural line, genre-neutral
# archetype overrides above take precedence when defined).
WINDOW_SHARED = {
    "light_window": ("已過民用光線，天色太暗看不到",
                     "Outside civil light — too dark to see anything",
                     "市民光を過ぎて、暗すぎて見えません"),
    "sunset_window": ("現在不在日落時段，晚霞時間不對",
                      "Outside the sunset window — the glow hour is not now",
                      "日の入りの時間帯ではなく、夕焼けの時間ではありません"),
    "sunrise_time_window": ("現在不在日出時段，曙光時間不對",
                            "Outside the sunrise window — the first-light hour is not now",
                            "日の出の時間帯ではなく、朝焼けの時間ではありません"),
    "golden_hour_window": ("現在不在黃金時段，光線太平",
                           "Outside the golden hour — the light is flat",
                           "ゴールデンアワーではなく、光が平坦です"),
    "blue_hour_window": ("現在不在藍調時段，天色不對",
                         "Outside the blue hour — the sky tone is wrong",
                         "ブルーアワーではなく、空の色が合いません"),
    "city_night_window": ("還沒暗到夜景好看",
                          "Not dark enough yet for the night view to look its best",
                          "夜景がきれいに見えるほど暗くなっていません"),
    "astronomical_darkness": ("天還沒全暗（或已經天亮），星空不見了",
                              "Not fully dark yet (or already dawn) — the stars are gone",
                              "完全に暗くなっていない（または夜明け）ため、星空が見えません"),
}

# Genre hints used when keywords cannot classify terrain.
GENRE_ARCH = {
    "sunset": "coast",           # overridden by keyword hits (mountain/harbor...)
    "sunrise": "coast",
    "mountain_view": "mountain",
    "overlook": "mountain",
    "blue_hour_city": "city",
    "city_night": "city",
    "geological_landform": "geology",
    "reflection": "lake",
    "seasonal_plant": "field",
    "night_sky": "coast",
    "cloud_sea": "cloudsea",
    "overcast_soft": "default",
    "golden_hour": "coast",
}

ARCH_KEYWS = [
    ("cloudsea", ["雲海"]),
    ("harbor", ["碼頭", "漁港", "港景", "港區", "漁人碼頭", "大棧橋", "漁港"]),
    ("lake", ["湖", "潭", "水庫"]),
    ("river", ["瀑布", "溪", "河岸", "河濱", "河"]),
    ("canyon", ["峽谷", "縱谷", "谷"]),
    ("coast", ["海岸", "海灘", "沙灘", "岬", "海灣", "灣", "島", "嶼", "燈塔",
               "潮間帶", "濕地", "鹽田", "石滬", "溫泉", "海岸", "斷崖", "海蝕",
               "玄武岩", "石槽", "奇岩", "石坪", "沙嘴", "漁港"]),
    ("geology", ["月世界", "岩", "地質", "惡地", "石門", "石筍", "化石"]),
    ("field", ["草原", "茶園", "田", "花", "芒", "公園", "梯田"]),
    ("mountain", ["山", "嶺", "峰", "稜", "主峰", "北大武", "太平", "Mount",
                  "Mountain", "Peak", "高山", "山脈", "氷河", "Glacier", "Alps"]),
    ("canyon", ["Canyon", "Gorge", "Valley"]),
    ("harbor", ["Pier", "Wharf", "Harbor", "Port", "橋"]),
    ("lake", ["Lake", "Lakes"]),
    ("river", ["River", "Falls", "Waterfall", "Creek"]),
    ("coast", ["Beach", "Bay", "Coast", "Point", "Spit", "Island"]),
    ("field", ["Dunes", "Sand", "Forest", "Meadow", "Grass"]),
    ("geology", ["Arch", "Rock", "Cactus", "Geolog", "Stone"]),
    ("city", ["101", "夜景", "天際線", "都市", "市區", "跨年"]),
]

# English/Japanese suffixes stripped from navigation labels to get a clean
# subject; only used for logging/debug — copy phrases are terrain-keyed.
GENERIC = "default"


def classify(genre, zh_text):
    text = zh_text or ""
    for arch, keys in ARCH_KEYWS:
        if any(k in text for k in keys):
            return arch
    return GENRE_ARCH.get(genre, GENERIC)


def phrase(arch, metric):
    tri = A[arch].get(metric) or A[GENERIC].get(metric) or WINDOW_SHARED.get(metric)
    if tri is None:
        return None
    return {"zh-TW": tri[0], "en": tri[1], "ja": tri[2]}


def build(regions):
    out = {}
    stats = collections.defaultdict(lambda: {"opps": 0, "covered": 0, "entries": 0})
    unauthored = collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "v2", "opportunities", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        oid = d["opportunity_id"]
        region = oid.split("-")[0]
        if region not in regions:
            continue
        cc = d.get("condition_contract") or {}
        zh_name = d["name_i18n"].get("zh-TW") or ""
        arch = classify(cc.get("genre_template"), zh_name)
        st = stats[region]
        st["opps"] += 1
        per = {}
        for c in cc.get("conditions") or []:
            m = c.get("metric")
            if m not in EVAL_METRICS:
                continue
            entry = (BESPOKE.get(oid) or {}).get(m) or phrase(arch, m)
            if entry:
                per[m] = entry
                st["entries"] += 1
            else:
                unauthored[m].append(oid)
        if per:
            out[oid] = per
            st["covered"] += 1
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False,
              indent=1, sort_keys=True)
    return out, stats, unauthored


# CL-DATA-11: per-place light-window wording merges into BESPOKE before build.
for _oid, (_zh, _en, _ja) in _LIGHT_WINDOW_CL.items():
    BESPOKE.setdefault(_oid, {})["light_window"] = {
        "zh-TW": _zh, "en": _en, "ja": _ja,
    }


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    regions = ["tw"] if arg == "tw" else ["tw", "jp", "us"]
    out, stats, unauthored = build(regions)
    for r in ("tw", "jp", "us"):
        if r in stats:
            s = stats[r]
            print(f"{r}: {s['covered']}/{s['opps']} opportunities, {s['entries']} metric entries")
    if unauthored:
        for m, ids in sorted(unauthored.items()):
            print("UNAUTHORED", m, len(ids), ids[:5])
    print("WROTE", OUT, os.path.getsize(OUT), "bytes,", len(out), "opportunities")


if __name__ == "__main__":
    main()