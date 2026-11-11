"""
ChaseLights — 區域與景點分類與主題標籤完整定義設定
"""

from opportunities import get_opportunities, merge_legacy_themes
from taxonomy_v004 import product_status, active_in_catalog

SCENE_TYPES = {
    "mountain", "coast", "lake", "river", "waterfall", "forest", "wetland",
    "geology", "desert", "grassland", "rural", "snow_ice", "city", "architecture",
}

THEME_TYPES = {
    "mountain_view", "sunrise", "sunset", "blue_hour", "sky_glow", "cloud_sea",
    "fog_mist", "reflection", "sunbeam", "milky_way", "long_exposure",
    "city_night", "snow_scene", "aurora",
}

# Legacy tags are retained inside REGIONS for backward compatibility. get_spots()
# converts them into the V5 two-layer model: scenes describe what is there;
# themes describe the photographic condition the weather engine predicts.
AVAILABLE_TAGS = {
    "lake", "mountain", "cloud_sea", "forest", "starlight", "coast",
    "waterfall", "aurora", "city",
}

# B104 administrative-area metadata for Taiwan filtering.
#
# Values are arrays by design so border/summit Places may belong to more than
# one county/city without forcing a false single-jurisdiction claim.  The UI
# treats a Place as matching when any selected administrative area intersects
# this list.
TW_ADMIN_AREAS = {
    "tw-001": ["台北市"],
    "tw-002": ["台北市"],
    "tw-003": ["新北市"],
    "tw-004": ["新北市"],
    "tw-005": ["台北市"],
    "tw-006": ["台北市"],
    "tw-007": ["新北市"],
    "tw-008": ["新北市"],
    "tw-009": ["基隆市"],
    "tw-010": ["基隆市"],
    "tw-011": ["桃園市"],
    "tw-012": ["新竹市"],
    "tw-013": ["苗栗縣"],
    "tw-014": ["苗栗縣"],
    "tw-015": ["台中市"],
    "tw-016": ["台中市"],
    "tw-017": ["彰化縣"],
    "tw-018": ["南投縣"],
    "tw-019": ["南投縣", "花蓮縣"],
    "tw-020": ["南投縣"],
    "tw-021": ["南投縣"],
    "tw-022": ["嘉義縣"],
    "tw-023": ["嘉義縣"],
    "tw-024": ["嘉義縣"],
    "tw-025": ["台南市"],
    "tw-026": ["台南市"],
    "tw-027": ["高雄市"],
    "tw-028": ["高雄市"],
    "tw-029": ["屏東縣"],
    "tw-030": ["屏東縣"],
    "tw-031": ["宜蘭縣"],
    "tw-032": ["宜蘭縣"],
    "tw-033": ["宜蘭縣"],
    "tw-034": ["花蓮縣"],
    "tw-035": ["花蓮縣"],
    "tw-036": ["花蓮縣"],
    "tw-037": ["台東縣"],
    "tw-038": ["台東縣"],
    "tw-039": ["台東縣"],
    "tw-040": ["嘉義縣", "南投縣"],
    "tw-041": ["台中市", "苗栗縣"],
    "tw-042": ["台中市", "苗栗縣"],
    "tw-043": ["南投縣", "花蓮縣"],
    "tw-044": ["台中市", "花蓮縣"],
    "tw-045": ["台東縣"],
    "tw-046": ["新竹縣", "苗栗縣"],
    "tw-047": ["屏東縣", "台東縣"],
    "tw-048": ["台中市"],
    "tw-049": ["台中市"],
    "tw-050": ["台中市"],
    "tw-051": ["桃園市"],
    "tw-052": ["高雄市"],
    "tw-053": ["南投縣"],
    "tw-054": ["基隆市"],
    "tw-055": ["宜蘭縣"],
    "tw-056": ["宜蘭縣"],
    "tw-057": ["宜蘭縣"],
    "tw-058": ["澎湖縣"],
    "tw-059": ["澎湖縣"],
    "tw-060": ["澎湖縣"],
    "tw-061": ["澎湖縣"],
    "tw-062": ["金門縣"],
    "tw-063": ["金門縣"],
    "tw-064": ["金門縣"],
    "tw-065": ["連江縣"],
    "tw-066": ["連江縣"],
    "tw-067": ["連江縣"],
    "tw-068": ["台東縣"],
    "tw-069": ["台東縣"],
    "tw-070": ["台東縣"],
    "tw-071": ["屏東縣"],
    "tw-072": ["新北市"],
    "tw-073": ["新北市"],
    "tw-074": ["新北市"],
    "tw-075": ["宜蘭縣"],
    "tw-076": ["屏東縣"],
    "tw-077": ["花蓮縣"],
    "tw-078": ["金門縣"],
    "tw-079": ["澎湖縣"],
    "tw-080": ["台東縣"],
    "tw-081": ["連江縣"],
    "tw-082": ["花蓮縣"],
    "tw-083": ["花蓮縣"],
    "tw-084": ["花蓮縣"],
    "tw-085": ["新北市"],
    "tw-086": ["新北市"],
    # CL-DATA-32 admission admin areas
    # CL-DATA-25 admission admin areas
    "tw-087": ["台中市"],
    "tw-088": ["宜蘭縣"],
    "tw-089": ["新竹縣"],
    "tw-090": ["台東縣"],
    "tw-091": ["新竹縣"],
    "tw-092": ["宜蘭縣"],
    "tw-093": ["台中市"],
    "tw-094": ["連江縣"],
    "tw-095": ["南投縣"],
    "tw-098": ["宜蘭縣"],
    "tw-096": ["苗栗縣"],
    "tw-097": ["台北市"],
    "tw-099": ["新北市"],
    "tw-100": ["新北市"],
    "tw-101": ["新北市"],
    "tw-102": ["新北市"],
    "tw-103": ["南投縣"],
    "tw-104": ["南投縣"],
    "tw-105": ["嘉義縣"],
    "tw-106": ["雲林縣"],
    "tw-107": ["屏東縣"],
    "tw-108": ["高雄市"],
    "tw-109": ["台南市"],
    "tw-110": ["台南市"],
    "tw-111": ["高雄市"],
    "tw-112": ["花蓮縣"],
    "tw-113": ["花蓮縣"],
    "tw-114": ["花蓮縣"],
    "tw-115": ["台東縣"],
    "tw-116": ["台東縣"],
    "tw-117": ["澎湖縣"],
    "tw-118": ["台東縣"],
    "tw-119": ["苗栗縣"],
    "tw-120": ["台中市"],
    "tw-125": ["南投縣"],  # CL-DATA-66
    "tw-126": ["新北市"],  # CL-DATA-66
    "tw-127": ["苗栗縣"],  # CL-DATA-66
    "tw-128": ["苗栗縣"],  # CL-DATA-66
    "tw-129": ["基隆市"],  # CL-DATA-66
    "tw-130": ["新竹縣"],  # CL-DATA-66
    "tw-131": ["新竹縣"],  # CL-DATA-66
    "tw-132": ["新北市"],  # CL-DATA-66
    "tw-133": ["南投縣"],  # CL-DATA-66
    "tw-134": ["嘉義縣"],  # CL-DATA-66
    "tw-135": ["新北市"],  # CL-DATA-66
    "tw-136": ["南投縣"],  # CL-DATA-66
    "tw-137": ["新北市"],  # CL-DATA-66
    "tw-138": ["新北市"],  # CL-DATA-66
    "tw-139": ["基隆市"],  # CL-DATA-66
    "tw-140": ["宜蘭縣"],  # CL-DATA-66
    "tw-141": ["南投縣"],  # CL-DATA-66
    "tw-142": ["台南市"],  # CL-DATA-66
    "tw-143": ["新北市"],  # CL-DATA-66
    "tw-144": ["桃園市"],  # CL-DATA-66
    "tw-145": ["新北市"],  # CL-DATA-66
    "tw-146": ["高雄市"],  # CL-DATA-66
    "tw-121": ["連江縣"],  # CL-DATA-64
    "tw-122": ["連江縣"],  # CL-DATA-64
    "tw-123": ["連江縣"],  # CL-DATA-64
    "tw-124": ["連江縣"],  # CL-DATA-64
}

# B137 country-neutral first-level administrative-area metadata.
#
# Every supported country uses the same contract: admin_areas is a non-empty
# list of first-level administrative units appropriate to that country
# (county/city, prefecture, state, province, region, canton, etc.). A Place that
# genuinely crosses a boundary lists every intersected unit. A precise
# viewpoint inside a larger cross-boundary destination lists only the unit(s)
# occupied by that viewpoint. The browser matches when any selected area
# intersects this list; macro-regions remain presentation-only groupings.
#
# Japan and the United States are defined below; Taiwan is defined above.
JP_ADMIN_AREAS = {
    "jp-001": ["北海道"],
    "jp-002": ["北海道"],
    "jp-003": ["北海道"],
    "jp-004": ["北海道"],
    "jp-005": ["北海道"],
    "jp-006": ["北海道"],
    "jp-007": ["青森県", "秋田県"],
    "jp-008": ["宮城県"],
    "jp-009": ["福島県"],
    "jp-010": ["山梨県"],
    "jp-011": ["東京都"],
    "jp-012": ["神奈川県"],
    "jp-013": ["長野県"],
    "jp-014": ["東京都"],
    "jp-015": ["東京都"],
    "jp-016": ["神奈川県"],
    "jp-017": ["石川県"],
    "jp-018": ["愛知県"],
    "jp-019": ["静岡県"],
    "jp-020": ["神奈川県"],
    "jp-021": ["岐阜県"],
    "jp-022": ["新潟県"],
    "jp-023": ["京都府"],
    "jp-024": ["大阪府"],
    "jp-025": ["山口県"],
    "jp-026": ["島根県"],
    "jp-027": ["兵庫県"],
    "jp-028": ["和歌山県"],
    "jp-029": ["三重県"],
    "jp-030": ["徳島県"],
    "jp-031": ["岡山県"],
    "jp-032": ["福岡県"],
    "jp-033": ["佐賀県"],
    "jp-034": ["長崎県"],
    "jp-035": ["福岡県"],
    "jp-036": ["宮崎県"],
    # CL-DATA-25R additions (CL-INT-90): prefectures verified from spot coordinates
    "jp-037": ["北海道"],
    "jp-038": ["山形県"],
    "jp-039": ["北海道"],
    "jp-040": ["北海道"],
    "jp-041": ["北海道"],
    "jp-042": ["秋田県"],
    "jp-043": ["北海道"],
    "jp-044": ["青森県"],
    "jp-045": ["北海道"],
    "jp-046": ["北海道"],
    "jp-047": ["青森県"],
    "jp-048": ["岩手県"],
    "jp-049": ["宮城県"],
    "jp-050": ["岩手県"],
    # CL-DATA-32 additions (jp-051..064): prefectures verified from the spot
    # coordinates in data/v2/tools/discovery/cl_data_32_candidates.json
    # (web-verified against ja.wikipedia article coordinates, 2026-11-08).
    "jp-051": ["広島県"],  # 嚴島神社・宮島大鳥居 (34.29602,132.31989, 廿日市市宮島)
    "jp-052": ["岡山県"],  # 備中松山城・雲海 (34.80909,133.62233, 高梁市)
    "jp-053": ["京都府"],  # 天橋立 (35.56936,135.19153, 宮津市)
    "jp-054": ["京都府"],  # 伊根的舟屋 (35.67572,135.28744, 伊根町)
    "jp-055": ["鳥取県"],  # 鳥取砂丘 (35.5425,134.23028)
    "jp-056": ["鳥取県"],  # 大山（剣ヶ峰） (35.3711,133.5464)
    "jp-057": ["長崎県"],  # 稻佐山夜景 (32.75336,129.84933, 長崎市)
    "jp-058": ["鹿児島県"],  # 櫻島・湯之平展望所 (31.5915,130.6299)
    "jp-059": ["熊本県"],  # 阿蘇山・草千里ヶ浜 (32.88417,131.10389, 阿蘇市)
    "jp-060": ["山口県"],  # 角島大橋 (34.35277,130.88616, 下関市)
    "jp-061": ["山口県"],  # 錦帯橋 (34.1676,132.17837, 岩国市)
    "jp-062": ["徳島県"],  # 祖谷的藤橋 (33.87528,133.83528, 三好市)
    "jp-063": ["愛媛県"],  # 松山城（伊予） (33.84554,132.76572)
    "jp-064": ["山口県"],  # 元乃隅稻成神社 (34.41972,131.06278, 長門市)
    "jp-065": ["静岡県"],
    "jp-066": ["山梨県"],
    "jp-067": ["長野県"],
    "jp-068": ["富山県"],
    "jp-069": ["北海道"],
    "jp-070": ["青森県"],
    "jp-071": ["青森県"],
    "jp-072": ["岐阜県"],
    "jp-073": ["長野県"],
    "jp-074": ["兵庫県"],
    "jp-075": ["埼玉県"],
    "jp-076": ["熊本県"],
    "jp-077": ["滋賀県"],
    "jp-078": ["香川県"],
    "jp-079": ["福島県"],
    "jp-080": ["静岡県"],
    "jp-081": ["熊本県"],
    "jp-082": ["高知県"],
    "jp-083": ["群馬県"],
    "jp-084": ["島根県"],
    "jp-085": ["宮崎県"],
    "jp-086": ["長崎県"],
    "jp-087": ["茨城県"],
    "jp-088": ["静岡県"],
    "jp-089": ["長野県"],
    "jp-090": ["沖縄県"],
    "jp-091": ["鹿児島県"],
    "jp-092": ["大分県"],  # CL-DATA-64
    "jp-093": ["大分県"],  # CL-DATA-64
    "jp-094": ["群馬県"],  # CL-DATA-64
    "jp-095": ["長野県"],  # CL-DATA-64
}

US_ADMIN_AREAS = {
    "us-001": ["Arizona"],
    "us-002": ["Arizona"],
    "us-003": ["Arizona"],
    "us-004": ["Arizona"],
    "us-005": ["Utah"],
    "us-006": ["Utah"],
    "us-007": ["Utah"],
    "us-008": ["California"],
    "us-009": ["California"],
    "us-010": ["Wyoming"],
    "us-011": ["Wyoming"],
    "us-012": ["Washington"],
    "us-013": ["Oregon"],
    "us-014": ["California", "Nevada"],
    "us-015": ["California"],
    "us-016": ["Nevada"],
    "us-017": ["Washington"],
    "us-018": ["Montana"],
    "us-019": ["Washington"],
    "us-020": ["California"],
    "us-021": ["Utah"],
    "us-022": ["California"],
    "us-023": ["Arizona"],
    "us-024": ["Washington"],
    "us-025": ["California"],
    "us-026": ["Washington"],
    "us-027": ["Idaho"],
    "us-028": ["California"],
    "us-029": ["New Mexico"],
    "us-030": ["Illinois"],
    "us-031": ["Colorado"],
    "us-032": ["Louisiana"],
    "us-033": ["Colorado"],
    "us-034": ["Missouri"],
    "us-035": ["Texas"],
    "us-036": ["New York"],
    "us-037": ["New York"],
    "us-038": ["Tennessee", "North Carolina"],
    "us-039": ["Florida"],
    "us-040": ["Massachusetts"],
    "us-041": ["Alaska"],
    "us-042": ["Alaska"],
    "us-043": ["Alaska"],
    "us-044": ["Alaska"],
    "us-045": ["Alaska"],
    "us-046": ["Alaska"],
    "us-047": ["Alaska"],
    "us-048": ["Alaska"],
    "us-049": ["Alaska"],
    "us-050": ["Alaska"],
    "us-051": ["Alaska"],
    "us-052": ["Alaska"],
    "us-053": ["Alaska"],
    "us-054": ["Alaska"],
    "us-055": ["Alaska"],
    "us-056": ["Alaska"],
    "us-057": ["Alaska"],
    "us-058": ["Alaska"],
    "us-059": ["Alaska"],
    "us-060": ["Alaska"],
    "us-061": ["Alaska"],
    "us-062": ["Alaska"],
    "us-063": ["Alaska"],
    "us-064": ["Alaska"],
    "us-065": ["Alaska"],
    "us-066": ["Alaska"],
    "us-067": ["Alaska"],
    "us-068": ["Alaska"],
    "us-069": ["Alaska"],
    "us-070": ["Alaska"],
    "us-071": ["Washington"],
    "us-072": ["Washington"],
    "us-073": ["Washington"],
    "us-074": ["Washington"],
    "us-075": ["Washington"],
    "us-076": ["Washington"],
    "us-077": ["Washington"],
    "us-078": ["Washington"],
    "us-079": ["Washington"],
    "us-080": ["Washington"],
    "us-081": ["Washington"],
    "us-082": ["Washington"],
    "us-083": ["Washington"],
    "us-084": ["Washington"],
    "us-085": ["Washington"],
    "us-086": ["Washington"],
    "us-087": ["Washington"],
    "us-088": ["Washington"],
    "us-089": ["Washington"],
    "us-090": ["Washington"],
    "us-091": ["Washington"],
    "us-092": ["Washington"],
    "us-093": ["Washington"],
    "us-094": ["Washington"],
    "us-095": ["Washington"],
    "us-096": ["Washington"],
    "us-097": ["South Dakota"],  # CL-DATA-42 (43.78477,-101.89985, South Dakota)
    "us-098": ["Maine"],  # CL-DATA-42 (44.3526,-68.226, Maine)
    "us-099": ["Virginia"],  # CL-DATA-42 (38.555,-78.395, Virginia)
    "us-100": ["California"],  # CL-DATA-42 (37.940344,-119.028063, California)
    "us-101": ["Oregon"],  # CL-DATA-42 (44.278421,-124.113499, Oregon)
    "us-102": ["Oregon"],  # CL-DATA-42 (45.57595,-122.11536, Oregon)
    "us-103": ["Oregon"],  # CL-DATA-42 (45.88444,-123.96806, Oregon)
    "us-104": ["New Hampshire"],  # CL-DATA-42 (44.180566,-71.695286, New Hampshire)
    "us-105": ["Michigan"],  # CL-DATA-42 (46.4955,-86.5518, Michigan)
    "us-106": ["Texas"],  # CL-DATA-42 (29.1679,-103.6106, Texas)
    "us-107": ["Alaska"],  # CL-DATA-43 (60.1782633,-149.6494389, Alaska)
    "us-108": ["Alaska"],  # CL-DATA-43 (64.9525,-148.3569444, Alaska)
    "us-109": ["Alaska"],  # CL-DATA-43 (61.00527778,-149.69416667, Alaska)
    "us-110": ["Alaska"],  # CL-DATA-43 (61.12861111,-145.72972222, Alaska)
    "us-111": ["Alaska"],  # CL-DATA-43 (58.555,-155.7915, Alaska)
    "us-112": ["Hawaii"],  # CL-DATA-43 (19.40527778,-155.28194444, Hawaii)
    "us-113": ["Hawaii"],  # CL-DATA-43 (20.70972222,-156.25333333, Hawaii)
    "us-114": ["Hawaii"],  # CL-DATA-43 (22.15055,-159.64505, Hawaii)
    "us-115": ["Hawaii"],  # CL-DATA-43 (19.75917,-155.45611, Hawaii)
    "us-116": ["Hawaii"],  # CL-DATA-43 (20.1177,-155.5836, Hawaii)
    "us-117": ["Hawaii"],  # CL-DATA-43 (21.309889,-157.649748, Hawaii)
    "us-118": ["Hawaii"],  # CL-DATA-43 (21.664,-158.054, Hawaii)
    "us-119": ["Arizona"],  # CL-DATA-53
    "us-120": ["Oregon"],  # CL-DATA-53
    "us-121": ["California"],  # CL-DATA-53
    "us-122": ["California"],  # CL-DATA-53
    "us-123": ["Colorado"],  # CL-DATA-53
    "us-124": ["Alaska"],  # CL-DATA-53
    "us-125": ["New Hampshire"],  # CL-DATA-53
    "us-126": ["North Carolina"],  # CL-DATA-53
    "us-127": ["Arizona"],  # CL-DATA-53
    "us-128": ["Utah"],  # CL-DATA-53
    "us-129": ["Utah"],  # CL-DATA-53
    "us-130": ["Arizona"],  # CL-DATA-53
    "us-131": ["New Mexico"],  # CL-DATA-53
    "us-132": ["Nevada"],  # CL-DATA-53
    "us-133": ["California"],  # CL-DATA-53
    "us-134": ["Wisconsin"],  # CL-DATA-53
    "us-135": ["Texas"],  # CL-DATA-53
    "us-136": ["Texas"],  # CL-DATA-53
    "us-137": ["New York"],  # CL-DATA-53
    "us-138": ["Tennessee"],  # CL-DATA-53
    "us-139": ["Colorado"],  # CL-DATA-53
    "us-140": ["Colorado"],  # CL-DATA-53
    "us-141": ["Colorado"],  # CL-DATA-53
    "us-142": ["Colorado"],  # CL-DATA-53
    "us-143": ["Oregon"],  # CL-DATA-53
    "us-144": ["Oregon"],  # CL-DATA-53
    "us-145": ["Oregon"],  # CL-DATA-53
    "us-146": ["Oregon"],  # CL-DATA-53
    "us-147": ["Utah"],  # CL-DATA-53
    "us-148": ["Utah"],  # CL-DATA-53
    "us-149": ["California"],  # CL-DATA-53
    "us-150": ["California"],  # CL-DATA-53
    "us-151": ["California"],  # CL-DATA-53
    "us-152": ["Idaho"],  # CL-DATA-53
    "us-153": ["Idaho"],  # CL-DATA-53
    "us-154": ["Idaho"],  # CL-DATA-53
    "us-155": ["Florida"],  # CL-DATA-53
    "us-156": ["North Carolina"],  # CL-DATA-53
    "us-157": ["Virginia"],  # CL-DATA-53
    "us-158": ["Alaska"],  # CL-DATA-53
    "us-159": ["Wyoming"],  # CL-DATA-64
    "us-160": ["Wyoming"],  # CL-DATA-64
    "us-161": ["Hawaii"],  # CL-DATA-64
    "us-162": ["Hawaii"],  # CL-DATA-64
    "us-163": ["Hawaii"],  # CL-DATA-64

}

ADMIN_AREAS_BY_REGION = {
    "tw": TW_ADMIN_AREAS,
    "jp": JP_ADMIN_AREAS,
    "us": US_ADMIN_AREAS,
}



REGIONS = {
    "tw": {
        "name_zh": "台灣",
        "name_en": "Taiwan",
        "categories": ["全部", "本島", "澎湖", "金門", "馬祖", "綠島/蘭嶼/小琉球"],
        # 格式: (lat, lon, name_zh, name_en, name_ja, name_local, category, tags)
        "spots": [
            (25.1869, 121.5208, "大屯山助航站", "Datunshan Navigation Station", "大屯山助航駅", "大屯山助航站", "本島", ["mountain", "cloud_sea", "city", "starlight"]),
            (25.02688, 121.57419, "象山六巨石攝影平台", "Xiangshan Six Boulders Viewpoint", "象山六巨石展望台", "象山六巨石", "本島", ["city", "mountain"]),
            (25.1761, 121.4103, "淡水漁人碼頭", "Tamsui Fisherman's Wharf", "淡水フィッシャーマンズワーフ", "淡水漁人碼頭", "本島", ["coast", "city"]),
            (25.1058, 121.8403, "九份不厭亭", "Jiufen Buyan Pavilion", "九份不厭亭", "九份不厭亭", "本島", ["mountain", "coast", "cloud_sea"]),
            (25.0508, 121.5050, "大稻埕碼頭", "Dadaocheng Wharf", "大稻埕埠頭", "大稻埕碼頭", "本島", ["coast", "city"]),
            (25.1270, 121.4600, "關渡大橋", "Guandu Bridge", "関渡大橋", "關渡大橋", "本島", ["coast", "city"]),
            (24.9590, 121.5340, "碧潭", "Bitan Scenic Area", "碧潭", "碧潭", "本島", ["lake", "city"]),
            (25.1410, 121.4210, "觀音山硬漢嶺", "Guanyin Mountain Yinghan Peak", "観音山硬漢嶺", "觀音山硬漢嶺", "本島", ["mountain", "cloud_sea", "city"]),
            (25.1550, 121.7830, "望幽谷", "Wangyou Valley", "望幽谷", "望幽谷", "本島", ["coast", "mountain"]),
            (25.1620, 121.7690, "和平島", "Heping Island Park", "和平島", "和平島", "本島", ["coast"]),
            (24.9850, 121.0190, "永安漁港", "Yongan Fishing Port", "永安漁港", "永安漁港", "本島", ["coast"]),
            (24.7610, 120.9090, "香山濕地", "Xiangshan Wetland", "香山湿地", "香山濕地", "本島", ["coast"]),
            (24.3630, 120.7400, "火炎山", "Huoyan Mountain", "火炎山", "火炎山", "本島", ["mountain"]),
            (24.4040, 120.8200, "雲洞山莊", "Yundong Villa", "雲洞山荘", "雲洞山莊", "本島", ["mountain", "cloud_sea"]),
            (24.3120, 120.5500, "高美濕地", "Gaomei Wetlands", "高美湿地", "高美濕地", "本島", ["coast"]),
            (24.2440, 120.9790, "鳶嘴山", "Yuanzui Mountain", "鳶嘴山", "鳶嘴山", "本島", ["mountain", "cloud_sea"]),
            (23.9670, 120.3340, "王功漁港", "Wanggong Fishing Port", "王功漁港", "王功漁港", "本島", ["coast"]),
            (23.8560, 120.9370, "日月潭", "Sun Moon Lake", "日月潭", "日月潭", "本島", ["lake", "cloud_sea", "starlight"]),
            (24.1426, 121.2712, "合歡山主峰", "Mt. Hehuan Main Peak", "合歓山主峰", "合歡山主峰", "本島", ["mountain", "cloud_sea", "starlight"]),
            (23.9120, 120.9310, "金龍山", "Jinlong Mountain", "金龍山", "金龍山", "本島", ["mountain", "cloud_sea", "starlight"]),
            (23.8930, 121.0140, "武界部落", "Wujie Tribe", "武界集落", "武界部落", "本島", ["mountain", "forest", "cloud_sea"]),
            (23.4720, 120.6830, "二延平步道", "Eryanping Trail", "二延平歩道", "二延平步道", "本島", ["mountain", "cloud_sea"]),
            (23.4750, 120.6850, "頂石棹", "Dingfazhao Trail", "頂石棹", "頂石棹", "本島", ["mountain", "forest", "cloud_sea"]),
            (23.5100, 120.8020, "阿里山", "Alishan National Scenic Area", "阿里山", "阿里山", "本島", ["mountain", "forest", "cloud_sea", "starlight"]),
            (23.0020, 120.4130, "二寮觀日亭", "Erliao Sunrise Pavilion", "二寮観日亭", "二寮觀日亭", "本島", ["mountain", "cloud_sea"]),
            (23.2820, 120.1160, "井仔腳鹽田", "Jingzijiao Tile-paved Salt Fields", "井仔脚瓦盤塩田", "井仔腳鹽田", "本島", ["coast"]),
            (22.8910, 120.3930, "田寮月世界", "Tianliao Moon World", "田寮月世界", "田寮月世界", "本島", ["mountain"]),
            (22.6200, 120.2810, "駁二藝術特區", "Pier-2 Art Center", "駁二芸術特区", "駁二藝術特區", "本島", ["city", "coast"]),
            (21.9010, 120.8530, "墾丁鵝鑾鼻", "Eluanbi Lighthouse", "鵝鑾鼻灯台", "墾丁鵝鑾鼻", "本島", ["coast", "starlight"]),
            (21.9670, 120.7240, "屏東關山", "Pingtung Guanshan Sunset", "屏東関山", "屏東關山", "本島", ["coast", "mountain"]),
            (24.8220, 121.7270, "抹茶山", "Matcha Mountain (Marian Hiking Trail)", "抹茶山", "抹茶山", "本島", ["mountain", "cloud_sea"]),
            (24.4820, 121.4930, "見晴懷古步道", "Jianqing Historic Trail", "見晴懐古歩道", "見晴懷古步道", "本島", ["forest", "mountain"]),
            (24.4420, 121.7800, "粉鳥林", "Fenniaolin Fish Harbor", "粉鳥林漁港", "粉鳥林", "本島", ["coast"]),
            (24.191966, 121.661332, "崇德清水斷崖展望點", "Chongde Qingshui Cliff Viewpoint", "崇徳清水断崖展望所", "崇德清水斷崖", "本島", ["coast", "mountain"]),
            (23.2310, 121.3250, "六十石山", "Liushidan Mountain", "六十石山", "六十石山", "本島", ["mountain", "cloud_sea", "starlight"]),
            (24.0260, 121.6320, "七星潭", "Qixingtan Beach", "七星潭", "七星潭", "本島", ["coast", "starlight"]),
            (22.4440, 120.9920, "多良車站", "Duoliang Station", "多良駅", "多良車站", "本島", ["coast"]),
            (23.1260, 121.4200, "三仙台", "Sanxiantai Bridge", "三仙台", "三仙台", "本島", ["coast", "starlight"]),
            (23.1010, 121.2210, "池上伯朗大道", "Chishang Mr. Brown Avenue", "池上ブラウンロード", "池上伯朗大道", "本島", ["mountain", "starlight"]),
            (23.470018, 120.95727, "玉山主峰", "Mt. Jade Main Peak", "玉山主峰", "玉山主峰", "本島", ["mountain", "cloud_sea", "starlight"]),
            (24.3830, 121.2330, "雪山主峰", "Mt. Xueshan Main Peak", "雪山主峰", "雪山主峰", "本島", ["mountain", "starlight"]),
            (24.4230, 121.2400, "雪山北峰", "Mt. Xueshan North Peak", "雪山北峰", "雪山北峰", "本島", ["mountain", "starlight"]),
            (24.1160, 121.3250, "奇萊主峰", "Mt. Qilai Main Peak", "奇莱主峰", "奇萊主峰", "本島", ["mountain", "cloud_sea", "starlight"]),
            (24.3620, 121.4390, "南湖大山", "Nanhu Mountain", "南湖大山", "南湖大山", "本島", ["mountain", "starlight"]),
            (23.2830, 120.9830, "嘉明湖", "Jiaming Lake", "嘉明湖", "嘉明湖", "本島", ["lake", "mountain", "starlight"]),
            (24.4610, 121.2580, "大霸尖山", "Dabajian Mountain", "大覇尖山", "大霸尖山", "本島", ["mountain", "starlight"]),
            (22.6170, 120.7500, "北大武山", "Beidawu Mountain", "北大武山", "北大武山", "本島", ["mountain", "cloud_sea", "starlight"]),
            (24.4320, 121.2860, "池有山", "Mt. Chiyou", "池有山", "池有山", "本島", ["mountain", "starlight"]),
            (24.4320, 121.3050, "桃山", "Mt. Tao", "桃山", "桃山", "本島", ["mountain", "starlight"]),
            (24.4370, 121.2640, "品田山", "Mt. Pintian", "品田山", "品田山", "本島", ["mountain", "starlight"]),
            (25.0830, 121.2930, "大古山", "Dagushan Lookout", "大古山", "大古山", "本島", ["mountain", "city"]),
            (22.8290, 120.3520, "小崗山雲臺", "Xiaogangshan Yuntai", "小崗山雲台", "小崗山雲臺", "本島", ["mountain", "city"]),
            (23.6320, 120.7920, "杉林溪", "Sun Link Sea Forest Recreation Area", "杉林渓", "杉林溪", "本島", ["forest", "waterfall", "starlight"]),
            (25.1520, 121.7680, "正濱漁港", "Zhengbin Fishing Port", "正浜漁港", "正濱漁港", "本島", ["coast", "city"]),
            (24.8320, 121.7340, "五峰旗瀑布", "Wufengqi Waterfall", "五峰旗の滝", "五峰旗瀑布", "本島", ["waterfall", "forest"]),
            (24.6757, 121.5732, "松蘿湖", "Songluo Lake", "松蘿湖", "松蘿湖", "本島", ["lake", "forest", "starlight"]),
            (24.5218, 121.4645, "加羅湖", "Jialuo Lake", "加羅湖", "加羅湖", "本島", ["lake", "mountain", "starlight"]),
            (23.6160, 119.5300, "澎湖跨海大橋", "Penghu Great Bridge", "澎湖跨海大橋", "澎湖跨海大橋", "澎湖", ["coast"]),
            (23.5810, 119.7200, "奎壁山", "Kuibishan Moses Sea Parting", "奎壁山モーゼの海割り", "奎壁山", "澎湖", ["coast", "starlight"]),
            (23.1940, 119.4340, "七美雙心石滬", "Qimei Twin-Hearts Stone Weir", "七美ダブルハート石滬", "七美雙心石滬", "澎湖", ["coast"]),
            (23.5560, 119.5620, "澎湖觀音亭", "Penghu Guanyinting", "澎湖観音亭", "澎湖觀音亭", "澎湖", ["coast", "city"]),
            (24.4490, 118.3360, "金門得月樓", "Kinmen Deyue Tower", "金門得月楼", "金門得月樓", "金門", ["city", "starlight"]),
            (24.4050, 118.3280, "翟山坑道", "Zhaishan Tunnel", "翟山坑道", "翟山坑道", "金門", ["coast"]),
            (24.4620, 118.2990, "金門慈湖", "Kinmen Cihu Lake", "金門慈湖", "金門慈湖", "金門", ["lake", "coast"]),
            (26.1580, 119.9420, "馬祖南竿", "Matsu Nangan", "馬祖南竿", "馬祖南竿", "馬祖", ["coast", "starlight"]),
            (26.3670, 120.5080, "東引燈塔", "Dongyin Lighthouse", "東引灯台", "東引燈塔", "馬祖", ["coast", "starlight"]),
            (26.2230, 119.9780, "北竿芹壁", "Beigan Qinbi Village", "北竿芹壁集落", "北竿芹壁", "馬祖", ["coast"]),
            (22.6400, 121.4910, "綠島朝日溫泉", "Green Island Zhaori Hot Spring", "緑島朝日温泉", "綠島朝日溫泉", "綠島/蘭嶼/小琉球", ["coast", "starlight"]),
            (22.0670, 121.5560, "蘭嶼東清灣", "Lanyu Dongqing Bay", "蘭嶼東清湾", "蘭嶼東清灣", "綠島/蘭嶼/小琉球", ["coast", "starlight"]),
            (22.0370, 121.5370, "蘭嶼青青草原", "Lanyu Qingqing Grassland", "蘭嶼青青草原", "蘭嶼青青草原", "綠島/蘭嶼/小琉球", ["coast", "starlight"]),
            (22.3430, 120.3800, "小琉球花瓶岩", "Liuqiu Vase Rock", "小琉球花瓶岩", "小琉球花瓶岩", "綠島/蘭嶼/小琉球", ["coast"]),
            (25.11982, 121.89314, "南雅奇岩", "Nanya Rock Formations", "南雅奇岩", "南雅奇岩", "本島", ["coast"]),
            (25.29242, 121.54446, "老梅綠石槽", "Laomei Green Reef", "老梅緑石槽", "老梅綠石槽", "本島", ["coast"]),
            (25.20886, 121.69314, "野柳地質公園", "Yehliu Geopark", "野柳地質公園", "野柳地質公園", "本島", ["coast"]),
            (24.87516, 121.84257, "外澳沙灘", "Waiao Beach", "外澳ビーチ", "外澳沙灘", "本島", ["coast"]),
            (21.92900, 120.84800, "龍磐公園", "Longpan Park", "龍磐公園", "龍磐公園", "本島", ["coast", "starlight"]),
            (23.49073, 121.51086, "石梯坪", "Shihtiping", "石梯坪", "石梯坪", "本島", ["coast"]),
            (24.426386, 118.304369, "建功嶼", "Jiangong Islet", "建功嶼", "建功嶼", "金門", ["coast"]),
            (23.60345, 119.50265, "池西岩瀑", "Chixi Columnar Basalt", "池西柱状玄武岩", "池西岩瀑", "澎湖", ["coast"]),
            (22.63366, 121.5069, "帆船鼻大草原", "Fanchuanbi Grassland", "帆船鼻大草原", "帆船鼻大草原", "綠島/蘭嶼/小琉球", ["coast", "starlight"]),
            (26.141922, 119.921072, "南竿鐵堡", "Iron Fort Nangan", "南竿鉄堡", "鐵堡", "馬祖", ["coast"]),
            (23.93493, 121.50803, "鯉魚潭", "Liyu Lake · North Shore", "鯉魚潭・北岸", "鯉魚潭", "本島", ["lake", "mountain"]),
            (23.827018, 121.51548, "雲山水夢幻湖", "Yun Shan Shui Dream Lake", "雲山水夢幻湖", "雲山水夢幻湖", "本島", ["lake", "forest"]),
            (23.6143836, 121.4159714, "大農大富平地森林園區", "Danongdafu Forest Park", "大農大富平地森林園区", "大農大富平地森林園區", "本島", ["forest"]),
            (25.1201398, 121.887539, "南子吝步道", "Nanzilin Trail", "南子吝歩道", "南子吝步道", "本島", ["mountain", "coast"]),
            (25.140639, 121.420333, "八里崁頭里・淡水大橋觀景點", "Bali Kantou Guandu Bridge Viewpoint", "八里崁頭・淡水大橋展望地", "八里崁頭里・淡水大橋觀景點", "本島", ["coast", "city", "cloud_sea"]),
            (24.1833, 121.0167, "大雪山森林遊樂區43K觀景台", "Daxueshan 43K Cloud-sea Viewpoint", "大雪山43K展望台", "大雪山國家森林遊樂區 43K 遊客中心", "本島", ["cloud_sea", "mountain"]),
            (24.514583, 121.606889, "翠峰湖環山步道觀景點", "Cuifeng Lake Viewpoints", "翠峰湖", "翠峰湖", "本島", ["lake", "forest"]),
            (24.506139, 121.113833, "觀霧榛山步道觀景點", "Guanwu Zhenshan Trail Viewpoint", "観霧榛山步道", "觀霧國家森林遊樂區 榛山步道", "本島", ["cloud_sea", "mountain"]),
            (22.7864, 121.1839, "加路蘭海岸遊憩區", "Jialulan Recreation Area", "加路蘭遊憩区", "加路蘭遊憩區", "本島", ["coast", "starlight"]),
            (24.5976, 121.3246, "司馬庫斯部落觀景點", "Smangus, Jianshi", "スマングス部落", "司馬庫斯部落", "本島", ["mountain", "starlight"]),
            (24.793, 121.875, "北關海潮公園", "Beiguan Tide Park", "北関海潮公園", "北關海潮公園", "本島", ["coast", "mountain"]),
            (24.23, 121.318, "福壽山農場觀景點", "Fushoushan Farm", "福寿山農場", "福壽山農場", "本島", ["cloud_sea", "starlight"]),
            (25.9672, 119.9856, "東莒燈塔（東犬燈塔）", "Dongju (Dongquan) Lighthouse", "東莒島灯塔（東犬灯塔）", "東莒島燈塔", "馬祖", ["coast", "starlight"]),
            (23.475, 120.875, "塔塔加夫妻樹／鹿林山觀景點", "Tataka Couple Trees & Lulinshan", "塔塔加夫妻樹", "塔塔加夫妻樹", "本島", ["mountain", "starlight"]),
            (24.603, 120.745, "半天寮好望角", "Haowanjiao Cape, Houlong", "半天寮好望角", "半天寮好望角", "本島", ["coast", "city"]),
            (25.1664, 121.5743, "擎天崗草原", "Qingtiangang Grassland", "擎天崗草原", "擎天崗", "本島", ["mountain", "starlight"]),
            (24.823055, 121.7025, "渭水之丘／櫻花陵園", "Weishui Hill, Jiaoxi", "渭水の丘", "渭水之丘", "本島", ["mountain", "city"]),
            (24.974556, 121.910444, "桃源谷（灣坑頭山草原）", "Taoyuan Valley Grassland", "桃源谷の草原", "桃源谷", "本島", ["mountain"]),
            (24.9326, 121.666, "石碇千島湖／鱷魚潭", "Shiding Qiandao Lake / Crocodile Islet", "石碇千島湖・鰐魚潭", "石碇千島湖", "本島", ["lake", "mountain", "cloud_sea"]),
            (25.119684, 121.318558, "林口水牛坑（林口大峽谷）", "Linkou Shuiniukeng Badlands", "林口水牛坑（リンコウ峡谷）", "林口水牛坑", "本島", ["coast", "mountain"]),
            (25.007, 122.001, "三貂角燈塔", "Sandiaojiao Lighthouse", "三貂角灯台", "三貂角燈塔", "本島", ["coast"]),
            (24.0586, 121.1639, "清境農場", "Qingjing Farm", "清境農場", "清境農場", "本島", ["mountain", "cloud_sea", "starlight"]),
            (23.651305, 120.794012, "忘憂森林", "Wangyou Forest", "忘憂の森", "忘憂森林", "本島", ["forest", "lake"]),
            (23.5599, 120.5978, "太平雲梯／梅山36彎", "Taiping Suspension Bridge / Meishan 36 Bends", "太平雲梯・梅山36彎", "太平雲梯", "本島", ["mountain", "cloud_sea"]),
            (23.6024363, 120.6679, "萬年峽谷", "Wannian Canyon", "万年峡谷", "萬年峽谷", "本島", ["mountain"]),
            (22.0028186, 120.873576, "佳樂水", "Jialeshui Scenic Area", "佳楽水", "佳樂水", "本島", ["coast"]),
            (22.882, 120.659, "龍頭山／多納環流丘", "Longtoushan Incised Meander", "龍頭山（多納の環流丘）", "龍頭山", "本島", ["mountain"]),
            (23.155276, 120.10535, "七股鹽山／潟湖", "Qigu Salt Mountain & Lagoon", "七股塩山・潟湖", "七股鹽山", "本島", ["coast", "city"]),
            (23.01959, 120.13633, "四草綠色隧道", "Sicao Green Tunnel", "四草グリーントンネル", "四草綠色隧道", "本島", ["forest", "lake"]),
            (22.678695, 120.29691, "蓮池潭龍虎塔", "Lotus Pond Dragon-Tiger Pagodas", "蓮池潭龍虎塔", "蓮池潭龍虎塔", "本島", ["city", "lake"]),
            (24.1717, 121.5767, "太魯閣燕子口／九曲洞", "Taroko Swallow Grotto & Jiuqudong", "太魯閣燕子口・九曲洞", "太魯閣燕子口", "本島", ["mountain"]),
            (24.1742639, 121.4744167, "白楊瀑布", "Baiyang Waterfall", "白楊滝", "白楊瀑布", "本島", ["waterfall", "mountain"]),
            (23.4433, 121.4587, "赤科山金針花海", "Chike Mountain Daylily Sea", "赤科山の金針花海", "赤科山", "本島", ["mountain"]),
            (22.913389, 121.119611, "鹿野高台", "Luye Highlands", "鹿野高台", "鹿野高台", "本島", ["mountain"]),
            (22.6113, 120.9959, "太麻里金針山", "Taimali Golden-Needle Mountain", "太麻里金針山", "太麻里金針山", "本島", ["mountain"]),
            (23.511225, 119.5185278, "桶盤嶼柱狀玄武岩", "Tongpan Island Basalt Columns", "桶盤嶼の柱状玄武岩", "桶盤嶼", "澎湖", ["coast"]),
            (23.1979087, 121.0371977, "栗松溫泉野溪峽谷", "Lisong Hot Spring Canyon", "栗松温泉の渓谷", "栗松溫泉", "本島", ["mountain"]),
            (24.5375, 120.9907, "加里山", "Jiali Mountain", "加里山", "加里山", "本島", ["mountain", "cloud_sea", "starlight"]),
            (24.364611, 121.31035, "武陵農場", "Wuling Farm", "武陵農場", "武陵農場", "本島", ["mountain", "starlight"]),
            (26.222827, 120.00476, "北竿塘后道沙灘藍眼淚", "Tanghou Beach blue tears (Beigan)", "塘后道ビーチの藍眼淚", "塘后道沙灘", "馬祖", ["coast", "starlight"]),  # CL-DATA-64
            (26.143015, 119.92881, "南竿北海坑道（夜間搖櫓藍眼淚）", "Beihai Tunnel night rowing blue tears (Nangan)", "北海坑道（夜間ローボート藍眼淚）", "北海坑道", "馬祖", ["coast", "starlight"]),  # CL-DATA-64
            (25.966231, 119.98215, "東莒福正沙灘藍眼淚（東犬燈塔旁）", "Fuzheng Beach blue tears (Dongju)", "福正ビーチの藍眼淚（東犬灯台）", "福正沙灘", "馬祖", ["coast", "starlight"]),  # CL-DATA-64
            (26.140628, 119.92906, "南竿大漢據點藍眼淚（鐵板海岸）", "Dahan stronghold blue tears (Tieban coast)", "大漢據点の藍眼淚（鉄板海岸）", "大漢據點", "馬祖", ["coast", "starlight"]),  # CL-DATA-64
            (23.681681, 120.76637, "大崙山觀光茶園/銀杏森林", "Dalunshan Tea Terraces / Ginkgo Forest", "大崙山茶園／銀杏の森", "大崙山觀光茶園", "本島", ["mountain", "starlight"]),  # CL-DATA-66
            (24.9675371, 121.7272531, "坪林南山寺仙公廟", "Nanshan Temple (Xianguangmiao), Pinglin", "坪林南山寺仙公廟", "南山寺仙公廟", "本島", ["mountain", "starlight"]),  # CL-DATA-66
            (24.5415154, 120.950373, "仙山靈洞宮後山", "Xianshan (Lingdong Temple back hill)", "仙山霊洞宮の後山", "仙山靈洞宮", "本島", ["mountain", "starlight"]),  # CL-DATA-66
            (24.5558111, 120.846273, "墨硯山琉璃光", "Moyanshan liuli-glow night", "墨硯山の琉璃光", "墨硯山", "本島", ["city", "starlight"]),  # CL-DATA-66
            (25.053278, 121.73011, "姜子寮山觀景台", "Jiangziliao Mountain viewing platform", "姜子寮山の展望台", "姜子寮山", "本島", ["mountain", "starlight"]),  # CL-DATA-66
            (24.6675183, 121.2820376, "宇老觀景台", "Yulao viewing platform (Jianshi)", "宇老観景台", "宇老觀景台", "本島", ["mountain", "starlight"]),  # CL-DATA-66
            (24.6047, 121.089, "山上人家農場", "Shanshang Renjia Forest Farm", "山上人家森林農場", "山上人家森林農場", "本島", ["mountain", "forest", "starlight"]),  # CL-DATA-66
            (24.9672358, 121.6196361, "石門二格山觀景台", "Ergeshan viewing platform (Shiding)", "二格山の展望台", "二格山", "本島", ["mountain", "starlight"]),  # CL-DATA-66
            (23.854861, 120.83806, "集集大山轉播站", "Jiji Dashan broadcast-station viewpoint", "集集大山の中継局展望", "集集大山", "本島", ["mountain", "starlight"]),  # CL-DATA-66
            (23.559532, 120.6789157, "1314觀景台", "1314 Observation Deck (Meishan Ruifeng)", "1314観景台", "1314觀景台", "本島", ["mountain", "starlight"]),  # CL-DATA-66
            (25.07278, 121.77278, "五分山雷達站", "Wufenshan Weather Radar Station", "五分山気象レーダー站", "五分山雷達站", "本島", ["mountain", "starlight"]),  # CL-DATA-66
            (23.964167, 120.989944, "埔里虎頭山虎嘯山莊", "Huxiao Farm, Hutoushan (Puli)", "虎嘯山荘（埔里虎頭山）", "虎嘯山莊", "本島", ["mountain", "starlight"]),  # CL-DATA-66
            (25.1136611, 121.8596306, "報時山觀景台", "Baoshishan viewing platform (Jinguashi)", "報時山の展望台", "報時山", "本島", ["coast", "starlight"]),  # CL-DATA-66
            (25.003363, 121.403214, "大同山/青龍嶺", "Datongshan / Qinglongling (Shulin)", "大同山・青龍嶺", "大同山/青龍嶺", "本島", ["city", "starlight"]),  # CL-DATA-66
            (25.1568, 121.7056, "大武崙白沙灘/外木山", "Waimushan coastal belt (Dawulun)", "外木山海濱（大武崙）", "大武崙白沙灘/外木山", "本島", ["coast", "starlight"]),  # CL-DATA-66
            (24.5242406, 121.6228895, "太平山森林遊樂區", "Taipingshan National Forest Recreation Area", "太平山国家森林遊楽区", "太平山", "本島", ["forest", "mountain", "starlight"]),  # CL-DATA-66
            (23.9489652, 121.1875001, "奧萬大楓林步道", "Aowanda maple trail", "奥万大の楓林古道", "奧萬大楓林步道", "本島", ["forest", "mountain"]),  # CL-DATA-66
            (22.9965428, 120.16379, "安平漁人碼頭/大魚的祝福", "Anping Fisherman's Wharf / The Blessing of the Big Fish", "安平漁人碼頭／大魚的祝福", "安平漁人碼頭", "本島", ["coast", "city"]),  # CL-DATA-66
            (25.298217, 121.536583, "富貴角風稜石", "Fuguijiao wind-cut stones", "富貴角の風稜石", "富貴角風稜石", "本島", ["coast", "geology"]),  # CL-DATA-66
            (24.818749, 121.4161228, "東眼山國家森林遊樂區三角點", "Dongyanshan tri-point (Fuxing)", "東眼山国家森林遊楽区の三角点", "東眼山", "本島", ["forest", "mountain", "starlight"]),  # CL-DATA-66
            (24.9379719, 121.5198804, "東華聖宮", "Donghua Shengong temple night", "東華聖宮", "東華聖宮", "本島", ["city", "starlight"]),  # CL-DATA-66
            (23.0657536, 120.7470591, "藤枝國家森林遊樂區", "Tengjhih National Forest Recreation Area", "藤枝国家森林遊楽区", "藤枝", "本島", ["forest", "mountain"]),  # CL-DATA-66
        ],
    },
    "jp": {
        "name_zh": "日本",
        "name_en": "Japan",
        "categories": ["全部", "北海道/東北", "關東/中部", "關西/中四國", "九州/沖繩"],
        "spots": [
            (43.6600, 142.8000, "美瑛青池", "Shirogane Blue Pond", "美瑛青い池", "白金青い池", "北海道/東北", ["lake", "forest"]),
            (43.7700, 142.3600, "旭岳", "Mt. Asahi", "旭岳", "旭岳", "北海道/東北", ["mountain", "starlight"]),
            (42.9700, 144.3700, "釧路濕原", "Kushiro Wetland", "釧路湿原", "釧路湿原", "北海道/東北", ["coast", "mountain"]),
            (41.8300, 140.1300, "函館山夜景", "Mt. Hakodate Night View", "函館山夜景", "函館山", "北海道/東北", ["city", "mountain"]),
            (43.1900, 141.0100, "小樽運河", "Otaru Canal", "小樽運河", "小樽運河", "北海道/東北", ["city", "coast"]),
            (43.0600, 144.3800, "摩周湖", "Lake Mashu", "摩周湖", "摩周湖", "北海道/東北", ["lake", "mountain"]),
            (40.8200, 140.7500, "十和田湖", "Lake Towada", "十和田湖", "十和田湖", "北海道/東北", ["lake", "forest"]),
            (38.2600, 140.8800, "松島", "Matsushima", "松島", "松島", "北海道/東北", ["coast"]),
            (38.7200, 139.8300, "磐梯山", "Mt. Bandai", "磐梯山", "磐梯山", "北海道/東北", ["mountain"]),
            (35.3600, 138.7300, "富士山 (河口湖)", "Mt. Fuji (Kawaguchiko)", "富士山 (河口湖)", "富士山", "關東/中部", ["mountain", "lake", "starlight"]),
            (35.6580, 139.7450, "東京鐵塔", "Tokyo Tower", "東京タワー", "東京タワー", "關東/中部", ["city"]),
            (35.2640, 139.1520, "鎌倉大佛", "Kamakura Great Buddha", "鎌倉大仏", "鎌倉大仏", "關東/中部", ["city"]),
            (36.1070, 138.0970, "諏訪湖", "Lake Suwa", "諏訪湖", "諏訪湖", "關東/中部", ["lake", "city"]),
            (35.6250, 139.6140, "等等力溪谷", "Todoroki Valley", "等々力渓谷", "等々力渓谷", "關東/中部", ["forest", "waterfall"]),
            (35.6700, 139.7500, "東京皇居", "Imperial Palace Tokyo", "皇居", "皇居", "關東/中部", ["city"]),
            (35.3150, 139.4950, "橫濱山下公園", "Yokohama Yamashita Park", "横浜山下公園", "山下公園", "關東/中部", ["city", "coast"]),
            (36.5600, 136.6600, "金澤兼六園", "Kanazawa Kenroku-en", "兼六園", "兼六園", "關東/中部", ["city", "lake"]),
            (35.1850, 136.9000, "名古屋城", "Nagoya Castle", "名古屋城", "名古屋城", "關東/中部", ["city"]),
            (34.7500, 137.9500, "濱名湖", "Lake Hamana", "浜名湖", "浜名湖", "關東/中部", ["lake", "coast"]),
            (35.4400, 139.6400, "橫濱港未來21", "Yokohama Minato Mirai 21", "横浜みなとみらい21", "みなとみらい", "關東/中部", ["city", "coast"]),
            (36.1600, 137.2600, "新穗高高空纜車", "Shinhotaka Ropeway", "新穂高ロープウェイ", "新穂高ロープウェイ", "關東/中部", ["mountain", "cloud_sea"]),
            (37.4500, 138.8600, "彌彥山", "Mt. Yahiko", "弥彦山", "弥彦山", "關東/中部", ["mountain"]),
            (35.0060, 135.7900, "京都清水寺", "Kiyomizu-dera Kyoto", "清水寺", "清水寺", "關西/中四國", ["city", "mountain"]),
            (34.6880, 135.5000, "大阪城公園", "Osaka Castle Park", "大阪城公園", "大阪城", "關西/中四國", ["city"]),
            (34.6550, 131.8000, "萩市城下町", "Hagi Castle Town", "萩城下町", "萩城下町", "關西/中四國", ["city"]),
            (35.4700, 133.0600, "出雲大社", "Izumo Taisha", "出雲大社", "出雲大社", "關西/中四國", ["city"]),
            (34.7760, 135.3400, "神戶六甲山", "Mt. Rokko Kobe", "六甲山", "六甲山", "關西/中四國", ["mountain", "city"]),
            (34.2600, 135.2200, "高野山", "Mt. Koya", "高野山", "高野山", "關西/中四國", ["mountain", "forest"]),
            (34.8900, 136.1000, "伊賀上野城", "Iga Ueno Castle", "伊賀上野城", "伊賀上野城", "關西/中四國", ["city"]),
            (34.0700, 134.6300, "鳴門海峽漩渦", "Naruto Whirlpools", "鳴門海峡", "鳴門海峡", "關西/中四國", ["coast"]),
            (34.6300, 133.8900, "倉敷美觀地區", "Kurashiki Bikan Historical Quarter", "倉敷美観地区", "倉敷美観地区", "關西/中四國", ["city", "lake"]),
            (33.5900, 130.5800, "福岡城跡", "Fukuoka Castle Ruins", "福岡城跡", "福岡城跡", "九州/沖繩", ["city"]),
            (33.4500, 129.9600, "唐津城", "Karatsu Castle", "唐津城", "唐津城", "九州/沖繩", ["city", "coast"]),
            (32.7500, 129.8700, "長崎哥拉巴園", "Glover Garden Nagasaki", "グラバー園", "グラバー園", "九州/沖繩", ["city", "coast"]),
            (33.5900, 130.3800, "福岡塔", "Fukuoka Tower", "福岡タワー", "福岡タワー", "九州/沖繩", ["city", "coast"]),
            (32.7016613, 131.3003766, "高千穗峽", "Takachiho Gorge", "高千穂峡", "高千穂峡", "九州/沖繩", ["waterfall", "forest", "mountain"]),
            (43.0617, 142.6228, "雲海テラス（トマム）", "Unkai Terrace (Hoshino Resorts TOMAMU)", "雲海テラス（星野リゾート トマム）", "星野リゾート トマム 雲海テラス", "北海道/東北", ["cloud_sea", "mountain"]),
            (38.154781, 140.431075, "蔵王樹氷（蔵王ロープウェイ・山形側）", "Zao Snow Monsters (Zao Ropeway, Yamagata)", "蔵王温泉の樹氷（蔵王ロープウェイ）", "蔵王ロープウェイ地蔵山頂駅", "北海道/東北", ["snow_ice", "mountain"]),
            (43.5769, 144.2242, "津別峠展望台（屈斜路湖雲海）", "Tsubetsu Pass Observatory", "津別峠展望台", "津別峠展望施設", "北海道/東北", ["cloud_sea", "mountain"]),
            (43.6483, 144.2461, "美幌峠展望台", "Bihoro Pass Observatory", "美幌峠展望台", "美幌峠 展望台", "北海道/東北", ["cloud_sea", "mountain"]),
            (44.0958, 145.0093, "知床ウトロ流氷（プユニ岬）", "Drift Ice at Utoro (Puyuni Cape), Shiretoko", "知床・ウトロの流氷（プユニ岬）", "プユニ岬", "北海道/東北", ["coast", "snow_ice"]),
            (39.955, 140.4919, "森吉山樹氷平（阿仁スキー場）", "Moriyoshi Juhyo Plain (Ani Ski Resort)", "森吉山の樹氷（阿仁スキー場）", "阿仁スキー場 樹氷平", "北海道/東北", ["snow_ice", "starlight"]),
            (43.4189, 142.4266, "富田農場ラベンダーイースト", "Farm Tomita Lavender East", "ラベンダーイースト（ファーム富田）", "ファーム富田 ラベンダーイースト", "北海道/東北", ["forest", "mountain"]),
            (40.5603, 139.9844, "十二湖・青池", "Aoike Pond (Juniko, Shirakami-Sanchi)", "十二湖・青池", "十二湖 青池", "北海道/東北", ["lake", "forest"]),
            (42.30272, 141.00067, "地球岬展望台", "Cape Chikyu (Earth Cape) Observatory", "地球岬展望台", "地球岬展望台", "北海道/東北", ["coast", "mountain"]),
            (43.4156, 143.1892, "タウシュベツ川橋梁（幻の橋）", "Taushubetsu River Bridge", "タウシュベツ川橋梁（幻の橋）", "タウシュベツ川橋梁", "北海道/東北", ["reflection", "lake"]),
            (40.6808, 140.8317, "八甲田山樹氷（八甲田ロープウェー）", "Hakkoda Snow Monsters (Hakkoda Ropeway)", "八甲田山の樹氷（八甲田ロープウェー）", "八甲田ロープウェー 山頂公園駅", "北海道/東北", ["snow_ice", "mountain"]),
            (39.97934, 141.953, "北山崎（三陸断崖）", "Kitayamazaki Cliffs (Sanriku)", "北山崎", "北山崎展望台", "北海道/東北", ["coast", "mountain"]),
            (38.1364, 140.4494, "蔵王御釜（五色湖）", "Zao Okama Crater Lake", "蔵王・御釜", "蔵王 御釜", "北海道/東北", ["lake", "mountain"]),
            (39.9944, 140.9642, "安比高原雲海ゴンドラ", "Appi Unkai (Sea of Clouds) Gondola", "安比高原 雲海ゴンドラ", "安比ゴンドラ UNKAIデッキ", "北海道/東北", ["cloud_sea", "mountain"]),
            (34.29602, 132.31989, "嚴島神社・宮島大鳥居", "Itsukushima Shrine Great Torii (Miyajima)", "厳島神社 大鳥居（宮島）", "厳島神社 大鳥居", "関西/中四國", ["coast", "city"]),
            (34.80909, 133.62233, "備中松山城・雲海（天空の城）", "Bitchu Matsuyama Castle cloud sea (castle in the sky)", "備中松山城の雲海（天空の城）", "備中松山城雲海展望台", "関西/中四國", ["cloud_sea", "mountain", "city"]),
            (35.56936, 135.19153, "天橋立", "Amanohashidate", "天橋立", "天橋立", "関西/中四國", ["coast", "forest", "mountain"]),
            (35.67572, 135.28744, "伊根的舟屋", "Ine no Funaya boathouses", "伊根の舟屋", "伊根の舟屋", "関西/中四國", ["coast", "city"]),
            (35.5425, 134.23028, "鳥取砂丘", "Tottori Sand Dunes", "鳥取砂丘", "鳥取砂丘", "関西/中四國", ["coast", "mountain"]),
            (35.3711, 133.5464, "大山（剣ヶ峰）", "Mt. Daisen (Kengamine)", "大山（剣ヶ峰）", "大山・剣ヶ峰", "関西/中四國", ["mountain", "forest"]),
            (32.75336, 129.84933, "稻佐山夜景", "Mt. Inasa night view", "稲佐山の夜景", "稲佐山展望台", "九州/沖繩", ["city", "mountain"]),
            (31.5915, 130.6299, "櫻島・湯之平展望所", "Sakurajima Yunohira Observatory", "桜島・湯之平展望所", "湯之平展望所", "九州/沖繩", ["mountain", "volcano"]),
            (32.88417, 131.10389, "阿蘇山・草千里ヶ浜", "Aso Kusasenri-ga-hama", "阿蘇山・草千里ヶ浜", "草千里ヶ浜", "九州/沖繩", ["mountain", "forest"]),
            (34.35277, 130.88616, "角島大橋", "Tsunoshima Ohashi Bridge", "角島大橋", "角島大橋", "関西/中四國", ["coast"]),
            (34.1676, 132.17837, "錦帯橋", "Kintaikyo Bridge", "錦帯橋", "錦帯橋", "関西/中四國", ["city", "coast"]),
            (33.87528, 133.83528, "祖谷的藤橋（祖谷渓）", "Iya Kazurabashi vine bridge", "祖谷のかずら橋", "祖谷のかずら橋", "関西/中四國", ["forest", "mountain"]),
            (33.84554, 132.76572, "松山城（伊予）", "Matsuyama Castle (Iyo)", "松山城（伊予松山城）", "松山城", "関西/中四國", ["city", "mountain"]),
            (34.41972, 131.06278, "元乃隅稻成神社", "Motonosumi Inari Shrine", "元乃隅稲成神社", "元乃隅稲成神社", "関西/中四國", ["coast", "mountain"]),
            (35.3606, 138.7274, "富士山頂（剣ヶ峰）", "Mount Fuji Summit (Kengamine)", "富士山頂（剣ヶ峰）", "富士山頂", "關東/中部", ["mountain", "cloud_sea"]),
            (35.3631, 138.6692, "新倉山淺間公園", "Arakurayama Sengen Park", "新倉山浅間公園", "新倉山浅間公園", "關東/中部", ["mountain"]),
            (36.2377, 137.6194, "上高地大正池／河童橋", "Kamikochi Taisho Pond & Kappa Bridge", "上高地・大正池／河童橋", "上高地", "關東/中部", ["lake", "mountain"]),
            (36.5702, 137.5964, "立山みくりが池／雪之大谷", "Mikuri-ga-ike & Yuki-no-Otani", "立山・みくりが池／雪の大谷", "みくりが池", "關東/中部", ["lake", "mountain"]),
            (43.6486, 142.5678, "美瑛拼布之路（名樹群）", "Biei Patchwork Road", "美瑛・パッチワークの路", "美瑛パッチワークの路", "北海道/東北", ["mountain"]),
            (39.7221, 141.0071, "奧入瀨溪流（阿修羅之瀧）", "Oirase Stream (Ashura Falls)", "奥入瀬渓流（阿修羅の滝）", "奥入瀬渓流", "北海道/東北", ["waterfall", "forest"]),
            (39.8808, 140.8748, "蔦沼", "Tsubo-numa", "蔦沼", "蔦沼", "北海道/東北", ["lake"]),
            (36.2585, 136.904, "白川鄉合掌村", "Shirakawa-go Gassho Village", "白川郷荻町集落", "白川郷", "關東/中部", ["mountain"]),
            (36.7236, 138.8837, "SORA terrace 龍王雲海", "SORA Terrace Ryuoo cloud sea", "SORA terrace・龍王の雲海", "SORA terrace", "關東/中部", ["mountain", "cloud_sea"]),
            (35.2945, 134.8392, "竹田城跡（天空之城）", "Takeda Castle Ruins", "竹田城跡", "竹田城跡", "關西/中四國", ["mountain", "cloud_sea"]),
            (36.0288, 138.9467, "秩父美之山公園雲海", "Chichibu Minoyama cloud sea", "秩父・美の山公園の霧海", "美の山公園", "關東/中部", ["mountain", "cloud_sea"]),
            (32.9056, 131.0756, "大觀峰（阿蘇五嶽）", "Daikanbo (Aso Five Peaks)", "大観峰（阿蘇五岳）", "大観峰", "九州/沖繩", ["mountain", "cloud_sea"]),
            (35.4829, 136.1229, "白鬚神社海上鳥居", "Shirahige Shrine Lake Torii", "白鬚神社の湖中鳥居", "白鬚神社", "關西/中四國", ["coast", "mountain"]),
            (33.8072, 133.2622, "父母之濱（天空之鏡）", "Fumotohama Sky Mirror", "父母ヶ浜（日本のウユニ塩湖）", "父母ヶ浜", "關西/中四國", ["coast"]),
            (37.7553, 140.1032, "五色沼（毘沙門沼）", "Goshiki-numa (Bishamon Pond)", "五色沼（毘沙門沼）", "五色沼", "北海道/東北", ["lake"]),
            (35.2192, 138.5594, "田貫湖（鑽石富士）", "Lake Tanuki (Diamond Fuji)", "田貫湖（ダイヤモンド富士）", "田貫湖", "關東/中部", ["lake", "mountain"]),
            (33.1373, 131.0357, "鍋瀑布（水簾洞）", "Nabegataki Falls", "鍋ヶ滝", "鍋ヶ滝", "九州/沖繩", ["waterfall", "forest"]),
            (33.75, 133.03, "仁淀川（仁淀藍）", "Niyodo River (Niyodo Blue)", "仁淀川（仁淀ブルー）", "仁淀川", "關西/中四國", ["lake", "forest"]),
            (36.9146, 139.2997, "吹割瀑布", "Fukiware Falls", "吹割の滝", "吹割の滝", "關東/中部", ["waterfall"]),
            (36.24, 132.956, "隱岐蠟燭島", "Rosoku-jima (Candle Rock), Oki", "蠟燭島（隠岐）", "蠟燭島", "關西/中四國", ["coast"]),
            (31.8106, 131.4556, "青島（鬼之洗衣板）", "Aoshima (Devil's Washboard)", "青島（鬼の洗濯板）", "青島", "九州/沖繩", ["coast"]),
            (33.0324, 129.5906, "九十九島群峰", "Kujukushima Islands", "九十九島", "九十九島", "九州/沖繩", ["coast"]),
            (36.0608, 140.5578, "常陸海濱公園", "Hitachi Seaside Park", "国営ひたち海浜公園", "国営ひたち海浜公園", "關東/中部", ["coast"]),
            (35.129, 138.583, "大淵笹場（茶田富士）", "Obuchi Sasaba (Tea Fields & Fuji)", "大淵笹場", "大淵笹場", "關東/中部", ["mountain"]),
            (35.5066, 137.8474, "阿智村（日本第一星空）", "Achi Village (Japan's #1 Starry Sky)", "阿智村（日本一の星空）", "阿智村", "關東/中部", ["mountain", "starlight"]),
            (24.2337, 123.7583, "波照間島（南十字星）", "Hateruma Island (Southern Cross)", "波照間島（南十字星）", "波照間島", "九州/沖繩", ["coast", "starlight"]),
            (30.3883, 130.6064, "屋久島白谷雲水峽", "Shiratani Unsuikyo Ravine", "白谷雲水峡", "白谷雲水峡", "九州/沖繩", ["forest", "waterfall"]),
            (33.316056, 131.4690056, "別府海地獄", "Umi Jigoku (Sea Hell, Beppu)", "海地獄（別府）", "海地獄", "九州/沖繩", ["mountain"]),  # CL-DATA-64
            (33.327125, 131.4782583, "別府血池地獄", "Chinoike Jigoku (Blood Pond Hell, Beppu)", "血の池地獄（別府）", "血の池地獄", "九州/沖繩", ["mountain"]),  # CL-DATA-64
            (36.622806, 138.596639, "草津湯畑", "Kusatsu Yubatake (hot-water field)", "草津湯畑", "草津湯畑", "關東/中部", ["mountain"]),  # CL-DATA-64
            (36.732806, 138.462694, "地獄谷野猿公苑", "Jigokudani Yaen-Koen (Snow Monkey Park)", "地獄谷野猿公苑", "地獄谷野猿公苑", "關東/中部", ["forest", "mountain"]),  # CL-DATA-64
        ],
    },
    "us": {
        "name_zh": "美國",
        "name_en": "United States",
        "categories": ["全部", "美西", "美中", "美東", "阿拉斯加", "夏威夷"],
        "spots": [
            (36.1070, -112.1130, "大峽谷國家公園", "Grand Canyon National Park", "グランド・キャニオン国立公園", "Grand Canyon NP", "美西", ["mountain", "starlight"]),
            (36.8790, -111.5100, "馬蹄灣", "Horseshoe Bend", "ホースシュー・ベンド", "Horseshoe Bend", "美西", ["mountain"]),
            (36.8620, -111.3740, "羚羊峽谷", "Antelope Canyon", "アンテロープ・キャニオン", "Antelope Canyon", "美西", ["mountain"]),
            (36.9830, -110.1130, "紀念碑谷", "Monument Valley", "モニュメント・バレー", "Monument Valley", "美西", ["mountain", "starlight"]),
            (38.7330, -109.5920, "拱門國家公園", "Arches National Park", "アーチズ国立公園", "Arches NP", "美西", ["mountain", "starlight"]),
            (37.5930, -112.1870, "布萊斯峽谷國家公園", "Bryce Canyon National Park", "ブライスキャニオン国立公園", "Bryce Canyon NP", "美西", ["mountain", "starlight"]),
            (37.3020, -113.0270, "錫安國家公園", "Zion National Park", "ザイオン国立公園", "Zion NP", "美西", ["mountain"]),
            (37.7310, -119.5230, "優勝美地半圓頂", "Yosemite Half Dome", "ヨセミテ ハーフドーム", "Yosemite Half Dome", "美西", ["mountain", "starlight"]),
            (37.7160, -119.6770, "優勝美地隧道觀景臺", "Yosemite Tunnel View", "ヨセミテ トンネルビュー", "Yosemite Tunnel View", "美西", ["mountain", "forest"]),
            (44.5250, -110.8380, "黃石國家公園 大稜鏡溫泉", "Yellowstone Grand Prismatic Spring", "イエローストーン グランド・プリズマティック", "Yellowstone Grand Prismatic", "美西", ["mountain", "lake"]),
            (43.7900, -110.6560, "大提頓國家公園", "Grand Teton National Park", "グランドティトン国立公園", "Grand Teton NP", "美西", ["mountain", "lake", "starlight"]),
            (46.8520, -121.7600, "雷尼爾山國家公園", "Mt. Rainier National Park", "マウント・レーニア国立公園", "Mount Rainier", "美西", ["mountain", "forest", "starlight"]),
            (42.9440, -122.1070, "火山口湖國家公園", "Crater Lake National Park", "クレーターレイク国立公園", "Crater Lake", "美西", ["lake", "mountain", "starlight"]),
            (36.4200, -116.8180, "死亡谷國家公園", "Death Valley National Park", "デスヴァレー国立公園", "Death Valley", "美西", ["mountain", "starlight"]),
            (37.8200, -122.4790, "舊金山金門大橋", "Golden Gate Bridge", "ゴールデン・ゲート・ブリッジ", "Golden Gate Bridge", "美西", ["city", "coast"]),
            (36.1150, -115.1730, "拉斯維加斯大道", "Las Vegas Strip", "ラスベガス・ストリップ", "Las Vegas Strip", "美西", ["city"]),
            (46.1910, -122.1960, "聖海倫斯火山", "Mount St. Helens", "セント・ヘレンズ山", "Mount St. Helens", "美西", ["mountain"]),
            (48.6490, -113.8000, "冰川國家公園", "Glacier National Park", "グレイシャー国立公園", "Glacier NP", "美西", ["mountain", "lake", "starlight"]),
            (47.7960, -123.6190, "奧林匹克國家公園", "Olympic National Park", "オリンピック国立公園", "Olympic NP", "美西", ["forest", "coast"]),
            (41.2920, -124.0560, "紅木國家公園", "Redwood National Park", "レッドウッド国立公園", "Redwood NP", "美西", ["forest"]),
            (38.3910, -109.8560, "峽谷地國家公園 梅薩拱門", "Canyonlands Mesa Arch", "キャニオンランズ メサアーチ", "Canyonlands Mesa Arch", "美西", ["mountain", "starlight"]),
            (33.9520, -115.9710, "約書亞樹國家公園", "Joshua Tree National Park", "ジョシュア・ツリー国立公園", "Joshua Tree NP", "美西", ["mountain", "starlight"]),
            (32.2500, -110.9420, "巨人柱國家公園", "Saguaro National Park", "サワロ国立公園", "Saguaro NP", "美西", ["mountain", "starlight"]),
            (47.6200, -122.3490, "西雅圖太空針塔", "Seattle Space Needle", "シアトル スペースニードル", "Space Needle", "美西", ["city"]),
            (34.0090, -118.4970, "聖莫尼卡碼頭", "Santa Monica Pier", "サンタモニカ・ピア", "Santa Monica Pier", "美西", ["coast", "city"]),
            (47.6080, -122.3410, "西雅圖派克市場", "Pike Place Market", "パイク・プレイス・マーケット", "Pike Place Market", "美西", ["city"]),
            (44.0680, -114.8520, "鋸齒山脈", "Sawtooth Mountains", "ソートゥース山脈", "Sawtooth Mountains", "美西", ["mountain", "starlight"]),
            (34.1610, -118.1670, "洛杉磯格里斐斯天文台", "Griffith Observatory LA", "グリフィス天文台", "Griffith Observatory", "美西", ["city", "starlight"]),
            (32.7790, -106.1710, "白沙國家公園", "White Sands National Park", "ホワイトサンズ国立公園", "White Sands", "美中", ["starlight", "mountain"]),
            (41.8830, -87.6240, "芝加哥天際線", "Chicago Skyline", "シカゴ スカイライン", "Chicago Skyline", "美中", ["city", "lake"]),
            (40.3770, -105.5210, "落磯山國家公園", "Rocky Mountain National Park", "ロッキー山脈国立公園", "Rocky Mountains", "美中", ["mountain", "starlight"]),
            (29.9580, -90.0650, "紐奧良法國區", "New Orleans French Quarter", "ニューオーリンズ フレンチ・クォーター", "French Quarter", "美中", ["city"]),
            (39.7390, -104.9920, "丹佛天際線", "Denver Skyline", "デンバー スカイライン", "Denver Skyline", "美中", ["city"]),
            (38.6250, -90.1910, "聖路易斯大拱門", "St. Louis Gateway Arch", "ゲートウェイ・アーチ", "Gateway Arch", "美中", ["city"]),
            (32.7550, -97.3310, "沃斯堡牲畜市場", "Fort Worth Stockyards", "フォートワース・ストックヤード", "Stockyards", "美中", ["city"]),
            (40.7480, -73.9860, "紐約曼哈頓天際線", "Manhattan Skyline NYC", "マンハッタン スカイライン", "Manhattan Skyline", "美東", ["city"]),
            (43.0800, -79.0710, "尼加拉瀑布", "Niagara Falls", "ナイアガラの滝", "Niagara Falls", "美東", ["waterfall", "city"]),
            (35.6110, -83.4920, "大霧山國家公園", "Great Smoky Mountains NP", "グレート・スモーキー山脈国立公園", "Great Smoky Mountains", "美東", ["mountain", "forest"]),
            (25.7930, -80.1390, "邁阿密海灘", "Miami Beach", "マイアミビーチ", "Miami Beach", "美東", ["coast", "city"]),
            (42.3600, -71.0580, "波士頓天際線", "Boston Skyline", "ボストン スカイライン", "Boston Skyline", "美東", ["city", "coast"]),
            (63.0690, -151.0080, "迪納利國家公園", "Denali National Park", "デナリ国立公園", "Denali NP", "阿拉斯加", ["mountain", "aurora", "starlight"]),
            (64.8410, -147.7180, "費爾班克斯極光", "Fairbanks Aurora", "フェアバンクス オーロラ", "Fairbanks", "阿拉斯加", ["aurora", "starlight"]),
            (65.0520, -146.0570, "珍娜溫泉", "Chena Hot Springs", "チェナ温泉", "Chena Hot Springs", "阿拉斯加", ["aurora", "starlight"]),
            (61.2180, -149.9000, "安克拉治", "Anchorage", "アンカレジ", "Anchorage", "阿拉斯加", ["city", "aurora"]),
            (60.1040, -149.4430, "蘇華德", "Seward", "スワード", "Seward", "阿拉斯加", ["coast", "aurora"]),
            (61.6400, -149.2870, "哈徹山口", "Hatcher Pass", "ハッチャーパス", "Hatcher Pass", "阿拉斯加", ["mountain", "aurora"]),
            (61.6530, -148.5970, "馬塔努斯卡冰河", "Matanuska Glacier", "マタヌスカ氷河", "Matanuska Glacier", "阿拉斯加", ["mountain", "aurora"]),
            (60.7830, -148.9070, "波蒂奇冰河", "Portage Glacier", "ポーテージ氷河", "Portage Glacier", "阿拉斯加", ["lake", "mountain"]),
            (61.1310, -146.3480, "瓦爾迪茲", "Valdez", "バルディーズ", "Valdez", "阿拉斯加", ["coast", "mountain"]),
            (58.3020, -134.4200, "朱諾", "Juneau", "ジュノー", "Juneau", "阿拉斯加", ["city", "coast"]),
            (58.4960, -134.5780, "門登霍爾冰河", "Mendenhall Glacier", "メンデンホール氷河", "Mendenhall Glacier", "阿拉斯加", ["lake", "mountain"]),
            (59.6430, -151.5380, "荷馬沙嘴", "Homer Spit", "ホーマー・スピット", "Homer Spit", "阿拉斯加", ["coast"]),
            (55.3430, -131.6470, "凱奇侃", "Ketchikan", "ケチカン", "Ketchikan", "阿拉斯加", ["coast"]),
            (59.4580, -135.3140, "史卡威", "Skagway", "スキャグウェイ", "Skagway", "阿拉斯加", ["coast", "mountain"]),
            (61.4520, -142.9690, "威朗格利-聖埃利亞斯國家公園", "Wrangell-St. Elias NP", "ランゲル・セントエライアス", "Wrangell-St. Elias", "阿拉斯加", ["mountain", "starlight"]),
            (68.1330, -149.4800, "布魯克斯山脈", "Brooks Range", "ブルックス山脈", "Brooks Range", "阿拉斯加", ["mountain", "aurora"]),
            (66.5620, -150.8130, "北極圈地標", "Arctic Circle Monument", "北極線標識", "Arctic Circle", "阿拉斯加", ["aurora", "starlight"]),
            (64.5010, -165.4060, "諾姆", "Nome", "ノーム", "Nome", "阿拉斯加", ["coast", "aurora"]),
            (58.5600, -155.1010, "卡特邁國家公園", "Katmai National Park", "カトマイ国立公園", "Katmai NP", "阿拉斯加", ["mountain", "forest"]),
            (58.4150, -135.7360, "冰河灣國家公園", "Glacier Bay National Park", "グレイシャーベイ国立公園", "Glacier Bay", "阿拉斯加", ["coast", "mountain"]),
            (57.7900, -152.4060, "柯迪亞克島", "Kodiak Island", "コディアック島", "Kodiak Island", "阿拉斯加", ["coast"]),
            (61.4070, -149.1220, "埃克盧特納湖", "Eklutna Lake", "エクルートナ湖", "Eklutna Lake", "阿拉斯加", ["lake", "aurora"]),
            (62.3230, -150.1070, "塔爾基特納", "Talkeetna", "タルキートナ", "Talkeetna", "阿拉斯加", ["mountain", "aurora"]),
            (60.9450, -149.1630, "艾利耶斯卡", "Alyeska Resort Girdwood", "アリエスカ リゾート", "Alyeska Girdwood", "阿拉斯加", ["mountain"]),
            (61.0660, -149.6500, "楚加奇州立公園", "Chugach State Park", "チュガッチ州立公園", "Chugach State Park", "阿拉斯加", ["mountain", "starlight"]),
            (66.0010, -166.6150, "白令陸橋國家保護區", "Bering Land Bridge National Preserve", "ベーリング陸橋", "Bering Land Bridge", "阿拉斯加", ["aurora"]),
            (64.7390, -156.8990, "育空河", "Yukon River", "ユーコン川", "Yukon River", "阿拉斯加", ["lake", "aurora"]),
            (68.5090, -161.0180, "諾阿塔克河", "Noatak River", "ノアタック川", "Noatak River", "阿拉斯加", ["lake", "aurora"]),
            (59.1050, -157.5500, "克拉克湖國家公園", "Lake Clark National Park", "レイククラーク国立公園", "Lake Clark", "阿拉斯加", ["lake", "aurora"]),
            (61.7890, -149.2730, "獨立礦山", "Independence Mine", "インデペンデンス鉱山", "Independence Mine", "阿拉斯加", ["mountain", "aurora"]),
            (47.62941, -122.35993, "凱瑞公園", "Kerry Park", "ケリー・パーク", "Kerry Park", "美西", ["city", "mountain"]),
            (47.69383, -122.40511, "金色花園公園", "Golden Gardens Park", "ゴールデン・ガーデンズ・パーク", "Golden Gardens", "美西", ["coast", "mountain"]),
            (47.58099, -122.40673, "阿爾基海灘公園", "Alki Beach Park", "アルカイ・ビーチ・パーク", "Alki Beach", "美西", ["coast", "mountain"]),
            (47.64630, -122.33600, "煤氣廠公園", "Gas Works Park", "ガス・ワークス・パーク", "Gas Works Park", "美西", ["city", "lake"]),
            (47.65730, -122.40550, "探索公園", "Discovery Park", "ディスカバリー・パーク", "Discovery Park", "美西", ["coast", "mountain"]),
            (47.59163, -122.38460, "漢密爾頓觀景公園", "Hamilton Viewpoint Park", "ハミルトン・ビューポイント・パーク", "Hamilton Viewpoint", "美西", ["city", "coast"]),
            (47.59250, -122.31806, "何塞・黎剎博士公園", "Dr. Jose Rizal Park", "ドクター・ホセ・リサール・パーク", "Dr. Jose Rizal Park", "美西", ["city", "coast"]),
            (47.61950, -122.36100, "默特爾・愛德華茲公園", "Myrtle Edwards Park", "マートル・エドワーズ・パーク", "Myrtle Edwards Park", "美西", ["coast", "mountain"]),
            (47.54170, -121.83770, "斯諾夸爾米瀑布", "Snoqualmie Falls", "スノコルミー滝", "Snoqualmie Falls", "美西", ["waterfall", "forest"]),
            (48.40570, -122.64480, "欺騙海峽州立公園", "Deception Pass State Park", "デセプション・パス州立公園", "Deception Pass", "美西", ["coast"]),
            (46.78600, -121.73500, "雷尼爾山・天堂區", "Mount Rainier — Paradise", "マウント・レーニア・パラダイス", "Rainier Paradise", "美西", ["mountain", "forest"]),
            (46.76920, -121.72490, "雷尼爾山・倒影湖", "Mount Rainier — Reflection Lakes", "マウント・レーニア・リフレクション・レイクス", "Rainier Reflection Lakes", "美西", ["lake", "mountain"]),
            (46.91400, -121.64200, "雷尼爾山・日出區", "Mount Rainier — Sunrise & Sunrise Point", "マウント・レーニア・サンライズ", "Rainier Sunrise", "美西", ["mountain"]),
            (46.86910, -121.51750, "雷尼爾山・蒂普蘇湖", "Mount Rainier — Tipsoo Lake", "マウント・レーニア・ティプソー湖", "Rainier Tipsoo Lake", "美西", ["lake", "mountain"]),
            (47.7105, -124.4155, "紅寶石海灘", "Ruby Beach", "ルビー・ビーチ", "Ruby Beach", "美西", ["coast"]),
            (47.917, -124.638, "里亞爾托海灘／牆中洞", "Rialto Beach / Hole-in-the-Wall", "リアルト・ビーチ", "Rialto Beach", "美西", ["coast"]),
            (47.969, -123.498, "颶風嶺", "Hurricane Ridge", "ハリケーン・リッジ", "Hurricane Ridge", "美西", ["mountain"]),
            (47.8609, -123.934, "霍雨林", "Hoh Rain Forest", "ホー・レインフォレスト", "Hoh Rain Forest", "美西", ["forest"]),
            (46.6636, -118.227, "帕盧斯瀑布", "Palouse Falls", "パルース滝", "Palouse Falls", "美西", ["waterfall"]),
            (48.713, -121.113, "迪亞布羅湖", "Diablo Lake", "ディアブロ湖", "Diablo Lake", "美西", ["lake","mountain"]),
            (48.525, -120.657, "華盛頓山口觀景點", "Washington Pass Observation Site", "ワシントン・パス", "Washington Pass", "美西", ["mountain"]),
            (48.8465, -121.6927, "藝術家角", "Artist Point", "アーティスト・ポイント", "Artist Point", "美西", ["mountain","starlight"]),
            (48.8682, -121.6777, "畫湖", "Picture Lake", "ピクチャー湖", "Picture Lake", "美西", ["lake","mountain"]),
            (47.032, -117.298, "斯特普托山丘", "Steptoe Butte State Park Heritage Site", "ステップトー・ビュート", "Steptoe Butte", "美西", ["mountain"]),
            (46.283, -124.054, "失望角州立公園", "Cape Disappointment State Park", "ケープ・ディサポイントメント州立公園", "Cape Disappointment", "美西", ["coast"]),
            (47.606672, -119.364385, "乾瀑布", "Sun Lakes–Dry Falls", "ドライ・フォールズ", "Dry Falls", "美西", ["mountain"]),
            (43.78477, -101.89985, "大惡地國家公園・大惡地觀景點", "Badlands NP – Big Badlands Overlook", "バッドランズ国立公園 ビッグ・バッドランズ展望台", "Big Badlands Overlook", "美中", ["mountain"]),

            (44.3526, -68.226, "阿卡迪亞國家公園・卡迪山", "Acadia NP – Cadillac Mountain", "アカディア国立公園 キャディラック山", "Cadillac Mountain", "美東", ["mountain"]),

            (38.555, -78.395, "謝南多厄國家公園・老鷹角", "Shenandoah NP – Hawksbill", "シェナンドー国立公園 ホークスビル", "Hawksbill", "美東", ["mountain"]),

            (37.940344, -119.028063, "莫諾湖・南方石灰華區", "Mono Lake – South Tufa", "モノ湖 サウス・テュファ", "South Tufa Area", "美西", ["mountain"]),

            (44.278421, -124.113499, "雷神之井", "Thor's Well", "トールズ・ウェル", "Thor's Well", "美西", ["mountain"]),

            (45.57595, -122.11536, "摩特諾瑪瀑布", "Multnomah Falls", "マルトノマ滝", "Multnomah Falls", "美西", ["mountain"]),

            (45.88444, -123.96806, "干草堆岩・坎農海灘", "Haystack Rock, Cannon Beach", "ヘイスタック・ロック", "Haystack Rock", "美西", ["mountain"]),

            (44.180566, -71.695286, "畫家堡・法蘭科尼亞峽", "Artists Bluff, Franconia Notch", "アーティスツ・ブラフ", "Artists Bluff", "美東", ["mountain"]),

            (46.4955, -86.5518, "畫岩國家湖岸・礦工堡", "Pictured Rocks NL – Miners Castle", "ピクチャード・ロックス マイナーズ・キャッスル", "Miners Castle", "美中", ["mountain"]),

            (29.1679, -103.6106, "大彎國家公園・聖埃倫娜峽谷", "Big Bend NP – Santa Elena Canyon", "ビッグベンド国立公園 サンタ・エレナ峡谷", "Santa Elena Canyon", "美中", ["mountain"]),
            (60.1782633, -149.6494389, "出口冰河・冰河舌谷景", "Exit Glacier – Glacier Tongue Valley", "出口氷河・氷河舌の谷", "Exit Glacier", "阿拉斯加", ["mountain", "snow_ice"]),  # CL-DATA-43 (60.1782633,-149.6494389, Alaska)
            (64.9525, -148.3569444, "墨菲穹丘極光", "Murphy Dome Aurora", "マーフィー・ドーム オーロラ", "Murphy Dome", "阿拉斯加", ["aurora", "starlight"]),  # CL-DATA-43 (64.9525,-148.3569444, Alaska)
            (61.00527778, -149.69416667, "白鯨角・特納甘灣夕照", "Beluga Point – Turnagain Arm Sunset", "ベルーガ・ポイント タナゲイン・アームの夕景", "Beluga Point", "阿拉斯加", ["coast"]),  # CL-DATA-43 (61.00527778,-149.69416667, Alaska)
            (61.12861111, -145.72972222, "湯普森山口雪牆", "Thompson Pass Snow Corridor", "トンプソン・パス 雪の回廊", "Thompson Pass", "阿拉斯加", ["mountain", "snow_ice"]),  # CL-DATA-43 (61.12861111,-145.72972222, Alaska)
            (58.555, -155.7915, "布魯克斯瀑布・鮭魚道水景", "Brooks Falls – Falls and Brooks River", "ブルックス滝とブルックス川", "Brooks Falls", "阿拉斯加", ["waterfall", "forest"]),  # CL-DATA-43 (58.555,-155.7915, Alaska)
            (19.40527778, -155.28194444, "哈雷茂茂火山口夜空", "Halemaʻumaʻu Crater Night Sky", "ハレマウマウ火口の夜空", "Halemaʻumaʻu", "夏威夷", ["geology", "starlight"]),  # CL-DATA-43 (19.40527778,-155.28194444, Hawaii)
            (20.70972222, -156.25333333, "哈雷阿卡拉山頂雲海日出", "Haleakalā Summit Cloud-Sea Sunrise", "ハレアカラ山頂の雲海と日の出", "Haleakalā Summit", "夏威夷", ["mountain", "cloud_sea"]),  # CL-DATA-43 (20.70972222,-156.25333333, Hawaii)
            (22.15055, -159.64505, "卡拉勞山谷雲霧眺望", "Kalalau Lookout – Nā Pali Valley", "カララウ展望台 ナーパリ渓谷", "Kalalau Lookout", "夏威夷", ["mountain", "coast"]),  # CL-DATA-43 (22.15055,-159.64505, Hawaii)
            (19.75917, -155.45611, "冒納凱亞遊客站銀河", "Maunakea VIS Milky Way", "マウナケア VISの天の川", "Maunakea VIS", "夏威夷", ["starlight", "mountain"]),  # CL-DATA-43 (19.75917,-155.45611, Hawaii)
            (20.1177, -155.5836, "威皮歐山谷晨光", "Waipiʻo Valley Lookout Morning Light", "ワイピオ渓谷の朝の光", "Waipiʻo Lookout", "夏威夷", ["mountain", "coast"]),  # CL-DATA-43 (20.1177,-155.5836, Hawaii)
            (21.309889, -157.649748, "馬卡普燈塔日出", "Makapuʻu Point Lighthouse Sunrise", "マカプウ灯台の日の出", "Makapuʻu Point", "夏威夷", ["coast"]),  # CL-DATA-43 (21.309889,-157.649748, Hawaii)
            (21.664, -158.054, "邦載管道夕照", "Banzai Pipeline Sunset", "バンザイ・パイプラインの夕景", "Banzai Pipeline", "夏威夷", ["coast"]),  # CL-DATA-43 (21.664,-158.054, Hawaii)
            (36.8617, -112.398, "波浪谷（The Wave）", "The Wave (Coyote Buttes North)", "ザ・ウェーブ", "The Wave", "美西", ["mountain"]),  # CL-DATA-53
            (45.6686, -121.4357, "哥倫比亞河峽谷（羅威娜岬）", "Columbia River Gorge (Rowena Crest)", "コロンビア渓谷（ロウェナ・クレスト）", "Rowena Crest", "美西", ["mountain", "coast"]),  # CL-DATA-53
            (36.0727, -121.9046, "比克斯比溪橋（大瑟爾）", "Bixby Creek Bridge (Big Sur)", "ビックスビー・ブリッジ（ビッグサー）", "Bixby Creek Bridge", "美西", ["coast"]),  # CL-DATA-53
            (36.3586, -121.9762, "麥克威瀑布（朱莉婭·菲佛州立公園）", "McWay Falls (Julia Pfeiffer Burns SP)", "マクウェイ滝（ジュリア・ファイファー・バーンズ州立公園）", "McWay Falls", "美西", ["coast", "waterfall"]),  # CL-DATA-53
            (39.0975, -106.9886, "褐鈴山（馬倫湖倒影）", "Maroon Bells (Maroon Lake mirror)", "マルーン・ベルズ", "Maroon Bells", "美西", ["mountain", "lake"]),  # CL-DATA-53
            (61.0414, -146.2389, "瓦爾迪茲基石峽谷瀑布", "Valdez Keystone Canyon falls", "バルディーズ・キーストーン峡谷の滝", "Keystone Canyon", "阿拉斯加", ["waterfall", "mountain"]),  # CL-DATA-53
            (44.0234, -71.365, "白山坎坎瑪格斯公路", "Kancamagus Highway (White Mountains)", "カンカマーガス・ハイウェイ（ホワイト山地）", "Kancamagus Highway", "美東", ["forest", "mountain"]),  # CL-DATA-53
            (36.0897, -81.7994, "藍嶺公路林恩灣高架橋", "Linn Cove Viaduct (Blue Ridge Parkway)", "リン・コーブ・バイアダクト（ブルーリッジ・パークウェイ）", "Linn Cove Viaduct", "美東", ["mountain", "forest"]),  # CL-DATA-53
            (36.9561, -111.9043, "白口袋（朱紅斷崖國家紀念地）", "White Pocket (Vermilion Cliffs NM)", "ホワイト・ポケット", "White Pocket", "美西", ["mountain"]),  # CL-DATA-53
            (37.1746, -110.9038, "反射峽谷（鮑威爾湖）", "Reflection Canyon (Lake Powell)", "リフレクション・キャニオン（レイク・パウエル）", "Reflection Canyon", "美西", ["lake", "mountain"]),  # CL-DATA-53
            (38.3767, -110.9003, "工廠台地（月球地貌）", "Factory Butte moonscape", "ファクトリー・ビュート", "Factory Butte", "美西", ["mountain"]),  # CL-DATA-53
            (36.0053, -111.0486, "煤礦峽谷（納瓦霍保留區）", "Coal Mine Canyon (Navajo Nation)", "コール・マイン峡谷", "Coal Mine Canyon", "美西", ["mountain"]),  # CL-DATA-53
            (36.0911, -108.2356, "比斯蒂/迪納津荒野", "Bisti/De-Na-Zin Wilderness", "ビスティ/デ・ナ・ジン荒野", "Bisti/De-Na-Zin", "美西", ["mountain"]),  # CL-DATA-53
            (39.0744, -120.0394, "太浩湖盆景岩", "Bonsai Rock (Lake Tahoe)", "ボンサイ・ロック", "Bonsai Rock", "美西", ["lake"]),  # CL-DATA-53
            (37.5917, -118.6111, "古狐尾松森林（舒爾曼林）", "Ancient Bristlecone Pine Forest (Schulman Grove)", "古いブリストルコーン松林（シュルマン・グローブ）", "Schulman Grove", "美西", ["forest", "mountain"]),  # CL-DATA-53
            (46.7389, -90.9978, "使徒群島海蝕洞（冰洞）", "Apostle Islands sea caves (ice caves)", "アポストル群島の海食洞（氷洞）", "Meyers Beach ice caves", "美中", ["coast", "mountain"]),  # CL-DATA-53
            (32.7236, -94.1531, "卡多湖（西班牙苔蘚）", "Caddo Lake (Spanish moss bayous)", "カドー湖", "Caddo Lake", "美中", ["lake", "forest"]),  # CL-DATA-53
            (34.97, -101.68, "帕洛杜羅峽谷（燈塔岩）", "Palo Duro Canyon (Lighthouse)", "パロ・デュロ峡谷（ライトハウス）", "Palo Duro Canyon", "美中", ["mountain"]),  # CL-DATA-53
            (42.3792, -76.7467, "沃特金斯格倫州立公園", "Watkins Glen State Park", "ワトキンス・グレン州立公園", "Watkins Glen", "美東", ["waterfall", "forest"]),  # CL-DATA-53
            (35.6114, -83.8192, "斯帕克斯小巷（凱德斯谷）", "Sparks Lane (Cades Cove)", "スパークス・レーン（ケイズ・コーブ）", "Sparks Lane", "美東", ["forest", "mountain"]),  # CL-DATA-53
            (39.05889, -107.10389, "水晶磨坊", "Crystal Mill", "クリスタル・ミル", "Crystal Mill", "美西", ["mountain", "forest"]),  # CL-DATA-53
            (37.8114, -107.7899, "冰湖盆地", "Ice Lakes Basin", "アイス・レイク盆地", "Ice Lake", "美西", ["lake", "mountain"]),  # CL-DATA-53
            (37.8836, -108.0053, "特柳賴德（Last Dollar Road）", "Telluride (Last Dollar Road)", "テリライド（Last Dollar Road）", "Last Dollar Road", "美西", ["mountain", "forest"]),  # CL-DATA-53
            (37.781, -105.531, "大沙丘國家公園", "Great Sand Dunes NP", "グレート・サンド・デューンズ国立公園", "Great Sand Dunes", "美西", ["mountain"]),  # CL-DATA-53
            (45.2617, -121.7417, "胡德山特里利姆湖", "Mount Hood (Trillium Lake)", "マウント・フッド（トリリウム湖）", "Trillium Lake", "美西", ["lake", "mountain"]),  # CL-DATA-53
            (44.9528, -122.2131, "阿比奎瀑布", "Abiqua Falls", "アビカ滝", "Abiqua Falls", "美西", ["waterfall", "forest"]),  # CL-DATA-53
            (44.1408, -122.2278, "普羅克斯瀑布", "Proxy Falls", "プロキシ滝", "Proxy Falls", "美西", ["waterfall", "forest"]),  # CL-DATA-53
            (44.6597, -120.1111, "彩繪山（約翰戴化石床）", "Painted Hills (John Day Fossil Beds)", "ペインテッド・ヒルズ", "Painted Hills", "美西", ["mountain"]),  # CL-DATA-53
            (37.661, -111.421, "斑馬狹縫峽谷", "Zebra Slot Canyon", "ゼブラ・スロット", "Zebra Slot", "美西", ["mountain"]),  # CL-DATA-53
            (38.3611, -111.1278, "膨潤土丘陵（大教堂谷）", "Bentonite Hills (Cathedral Valley)", "ベントナイト・ヒルズ", "Bentonite Hills", "美西", ["mountain"]),  # CL-DATA-53
            (33.8928, -116.1888, "約書亞樹國家公園（凱斯觀景台）", "Joshua Tree NP (Keys View)", "ジョシュアツリー国立公園（Keys View）", "Joshua Tree NP", "美西", ["mountain", "starlight"]),  # CL-DATA-53
            (35.6611, -117.3453, "特羅納石塔", "Trona Pinnacles", "トロナ・ピナクルズ", "Trona Pinnacles", "美西", ["mountain"]),  # CL-DATA-53
            (40.5264, -121.2722, "拉森火山（彩繪沙丘）", "Lassen Volcanic NP (Painted Dunes)", "ラッセン火山（ペインテッド・デューンズ）", "Painted Dunes", "美西", ["mountain"]),  # CL-DATA-53
            (43.9391, -114.9437, "愛達荷暗夜保護區（愛麗絲湖）", "Idaho Dark Sky Reserve (Alice Lake)", "アイダホ暗空保護区（アリス湖）", "Alice Lake", "美西", ["lake", "mountain", "starlight"]),  # CL-DATA-53
            (43.4169, -113.4977, "月球火山紀念地", "Craters of the Moon NM", "クレーターズ・オブ・ザ・ムーン", "Craters of the Moon", "美西", ["mountain", "starlight"]),  # CL-DATA-53
            (42.7547, -114.4214, "肖肖尼瀑布（西尼加拉）", "Shoshone Falls (Niagara of the West)", "ショショーニ滝", "Shoshone Falls", "美西", ["waterfall"]),  # CL-DATA-53
            (24.628, -82.8735, "乾龜國家公園（傑佛遜堡）", "Dry Tortugas NP (Fort Jefferson)", "ドライ・トルトゥガス国立公園", "Dry Tortugas", "美東", ["coast"]),  # CL-DATA-53
            (35.2113, -75.5213, "哈特拉斯角燈塔", "Cape Hatteras Lighthouse", "ケープ・ハテラス灯台", "Cape Hatteras Lighthouse", "美東", ["coast"]),  # CL-DATA-53
            (38.0111, -75.2814, "阿薩蒂格島野馬", "Assateague Island wild horses", "アサティーグ島の野生馬", "Assateague Island", "美東", ["coast"]),  # CL-DATA-53
            (59.995, -149.69, "哈丁冰原（奇奈峽灣）", "Harding Icefield (Kenai Fjords)", "ハーディング氷原（ケナイフィヨルド）", "Harding Icefield", "阿拉斯加", ["mountain"]),  # CL-DATA-53
            (44.46047, -110.82814, "老忠實間歇泉（黃石）", "Old Faithful Geyser (Yellowstone)", "オールド・フェイスフル・ガイザー", "Old Faithful", "美西", ["mountain"]),  # CL-DATA-64
            (44.4750325, -110.8435128, "牽牛花溫泉池（黃石上間歇泉盆地）", "Morning Glory Pool (Upper Geyser Basin)", "モーニンググロリー・プール", "Morning Glory Pool", "美西", ["mountain"]),  # CL-DATA-64
            (19.4071, -155.285, "基勞亞口熔岩紅光夜拍（基勞亞展望台）", "Kilauea crater lava-glow night (Kilauea Overlook)", "キラウエア火口の溶岩紅光夜景", "Kilauea Overlook", "夏威夷", ["geology", "starlight"]),  # CL-DATA-64
            (19.4134, -155.243, "那胡庫熔岩管（瑟斯頓熔岩洞）", "Nāhuku (Thurston Lava Tube)", "ナフク（サーストン溶岩トンネル）", "Nāhuku", "夏威夷", ["geology", "forest"]),  # CL-DATA-64
            (19.417, -155.244, "基勞亞伊奇火山口熔岩地表", "Kīlauea Iki crater lava floor", "キラウエア・イキ火口の溶岩地面", "Kīlauea Iki", "夏威夷", ["geology"]),  # CL-DATA-64
        ],
    },
}

# Known summit / high-elevation camera points.  Passing the real shooting
# elevation helps Open-Meteo select/downscale to a terrain height closer to
# the photographer instead of relying only on the grid-cell DEM.
ELEVATION_OVERRIDES = {
    # CL-DATA-16 2026-11-06 fact-check wave 1 (authoritative re-verification):
    # 九份不厭亭 531 (myjourney.tw/smilertaiwan), 觀音山硬漢嶺 616 (北觀處官方),
    # 火炎山 602 (林業署 forest.gov.tw/0007960), 鳶嘴山 2180 (recreation.forest.gov.tw tr_id=060),
    # 金龍山 820 (日月潭風管處), 武界部落 800 (通行引用 760-820 區間), 二寮觀日亭 185 (西拉雅風管處),
    # 墾丁鵝鑾鼻 56.4 (航港局燈高＝高潮面至燈火中心，焦點海拔語義, 非地面海拔),
    # 屏東關山 152 (大鵬灣風管處).
    "九份不厭亭": 531,
    "觀音山硬漢嶺": 616,
    "火炎山": 602,
    "鳶嘴山": 2180,
    "金龍山": 820,
    "武界部落": 800,
    "二寮觀日亭": 185,
    "墾丁鵝鑾鼻": 56.4,
    "屏東關山": 152,
    # CL-DATA-17 2026-11-06 fact-check wave (US coordinates/elevations, authoritative re-verification):
    # 大峽谷 Mather Point 2170 m (USGS GNIS 7,119 ft); 優勝美地 Sentinel Bridge 1208 m (OSM 3,963 ft).
    # CL-DATA-42 2026-11-09 (US expansion, authoritative web verification):
    # 卡迪山 466 m (NPS 1,530 ft); 老鷹角 1,235 m (NPS brochure 4,051 ft);
    # 莫諾湖石灰華 1,951 m (USFS 6,400 ft); 摩特諾瑪瀑布 191 m (Wikipedia 627 ft);
    # 畫家堡 702 m (PeakVisor 2,303 ft).
    "大峽谷國家公園": 2170,
    "阿卡迪亞國家公園・卡迪山": 466,
    "謝南多厄國家公園・老鷹角": 1235,
    "莫諾湖・南方石灰華區": 1951,
    "摩特諾瑪瀑布": 191,
    "畫家堡・法蘭科尼亞峽": 702,
    "優勝美地半圓頂": 1208,
    "合歡山主峰": 3417,
    "玉山主峰": 3952,
    "雪山主峰": 3886,
    "雪山北峰": 3703,
    "奇萊主峰": 3560,
    "南湖大山": 3742,
    "嘉明湖": 3310,
    "大霸尖山": 3492,
    "北大武山": 3092,
    "池有山": 3303,
    "桃山": 3325,
    "品田山": 3524,
    "旭岳": 2291,
    "富士山": 3776,
    # CL-DATA-25 discovery admission elevations (web-verified 2026-11-07; null elevations omitted honestly)
    "雲海テラス（トマム）": 1088,
    "蔵王樹氷（蔵王ロープウェイ・山形側）": 1661,
    "津別峠展望台（屈斜路湖雲海）": 947,
    "美幌峠展望台": 525,
    "知床ウトロ流氷（プユニ岬）": 125,
    "地球岬展望台": 100,
    "八甲田山樹氷（八甲田ロープウェー）": 1324,
    "安比高原雲海ゴンドラ": 1304,
    "大雪山森林遊樂區43K觀景台": 2450,
    "翠峰湖環山步道觀景點": 1840,
    "觀霧榛山步道觀景點": 2100,
    "加路蘭海岸遊憩區": 30,
    "司馬庫斯部落觀景點": 1600,
    "北關海潮公園": 15,
    "福壽山農場觀景點": 2600,
    "東莒燈塔（東犬燈塔）": 64,
    "塔塔加夫妻樹／鹿林山觀景點": 2478,
    "渭水之丘／櫻花陵園": 800,
    "半天寮好望角": 98,
    "擎天崗草原": 800,
    # CL-DATA-32 discovery admission elevations (web-verified 2026-11-08; null elevations omitted honestly)
    "備中松山城・雲海（天空の城）": 430,
    "大山（剣ヶ峰）": 1729,
    "稻佐山夜景": 333,
    "哈雷阿卡拉山頂雲海日出": 3055,  # CL-DATA-43 (Hawaii)
    # CL-DATA-53 admission elevations (web-verified 2026-11-09; null elevations omitted honestly)
    "The Wave": 1745,  # CL-DATA-53
    "Rowena Crest": 250,  # CL-DATA-53
    "Bixby Creek Bridge": 80,  # CL-DATA-53
    "McWay Falls": 30,  # CL-DATA-53
    "Maroon Bells": 2884,  # CL-DATA-53
    "Keystone Canyon": 200,  # CL-DATA-53
    "Kancamagus Highway": 926,  # CL-DATA-53
    "Linn Cove Viaduct": 1250,  # CL-DATA-53
    "White Pocket": 1860,  # CL-DATA-53
    "Reflection Canyon": 1330,  # CL-DATA-53
    "Factory Butte": 1480,  # CL-DATA-53
    "Coal Mine Canyon": 1780,  # CL-DATA-53
    "Bisti/De-Na-Zin": 1950,  # CL-DATA-53
    "Bonsai Rock": 1897,  # CL-DATA-53
    "Schulman Grove": 3000,  # CL-DATA-53
    "Meyers Beach ice caves": 183,  # CL-DATA-53
    "Caddo Lake": 52,  # CL-DATA-53
    "Palo Duro Canyon": 900,  # CL-DATA-53
    "Watkins Glen": 250,  # CL-DATA-53
    "Sparks Lane": 500,  # CL-DATA-53
    "Crystal Mill": 2710,  # CL-DATA-53
    "Ice Lake": 3735,  # CL-DATA-53
    "Last Dollar Road": 2650,  # CL-DATA-53
    "Great Sand Dunes": 2560,  # CL-DATA-53
    "Trillium Lake": 1160,  # CL-DATA-53
    "Abiqua Falls": 450,  # CL-DATA-53
    "Proxy Falls": 1220,  # CL-DATA-53
    "Painted Hills": 700,  # CL-DATA-53
    "Zebra Slot": 1590,  # CL-DATA-53
    "Bentonite Hills": 1980,  # CL-DATA-53
    "Joshua Tree NP": 1580,  # CL-DATA-53
    "Trona Pinnacles": 750,  # CL-DATA-53
    "Painted Dunes": 2400,  # CL-DATA-53
    "Alice Lake": 2622,  # CL-DATA-53
    "Craters of the Moon": 1850,  # CL-DATA-53
    "Shoshone Falls": 900,  # CL-DATA-53
    "Dry Tortugas": 3,  # CL-DATA-53
    "Cape Hatteras Lighthouse": 15,  # CL-DATA-53
    "Assateague Island": 2,  # CL-DATA-53
    "Harding Icefield": 1200,  # CL-DATA-53
    # CL-DATA-64 admission elevations (web-verified 2026-11-10; null elevations omitted honestly)
    # CL-DATA-66 wave-1 admission elevations (web-verified 2026-11-11; null elevations omitted honestly)
    "大崙山觀光茶園": 1300,  # CL-DATA-66
    "仙山靈洞宮": 967,  # CL-DATA-66
    "墨硯山": 157,  # CL-DATA-66
    "姜子寮山": 729,  # CL-DATA-66
    "宇老觀景台": 1450,  # CL-DATA-66
    "山上人家森林農場": 1200,  # CL-DATA-66
    "二格山": 678,  # CL-DATA-66
    "集集大山": 1392,  # CL-DATA-66
    "1314觀景台": 1314,  # CL-DATA-66
    "五分山雷達站": 740,  # CL-DATA-66
    "虎嘯山莊": 650,  # CL-DATA-66
    "報時山": 295,  # CL-DATA-66
    "大同山/青龍嶺": 256,  # CL-DATA-66
    "大武崙白沙灘/外木山": 231,  # CL-DATA-66
    "太平山": 1950,  # CL-DATA-66
    "奧萬大楓林步道": 1100,  # CL-DATA-66
    "東眼山": 1212,  # CL-DATA-66
    "藤枝": 1500,  # CL-DATA-66
    "塘后道沙灘": 3,  # CL-DATA-64
    "福正沙灘": 3,  # CL-DATA-64
    "Old Faithful": 2240,  # CL-DATA-64
    "草津湯畑": 1200,  # CL-DATA-64
    "地獄谷野猿公苑": 850,  # CL-DATA-64
    "Kilauea Overlook": 1227,  # CL-DATA-64
    # CL-DATA-52 admission elevations (web-verified 2026-11-09; null elevations omitted honestly)
    "富士山頂": 3776,
    "新倉山浅間公園": 410,
    "上高地": 1510,
    "みくりが池": 2405,
    "美瑛パッチワークの路": 560,
    "奥入瀬渓流": 500,
    "SORA terrace": 1933,
    "竹田城跡": 354,
    "美の山公園": 1038,
    "大観峰": 913,
    "白鬚神社": 86,
    "父母ヶ浜": 2,
    "五色沼": 805,
    "田貫湖": 800,
    "鍋ヶ滝": 600,
    "青島": 5,
    "阿智村": 800,
    "波照間島": 5,
    "白谷雲水峡": 620,
    # CL-DATA-51 admission elevations (web-verified 2026-11-09; null elevations omitted honestly)
    "桃源谷": 616,
    "石碇千島湖": 500,
    "林口水牛坑": 50,
    "清境農場": 1748,
    "太平雲梯": 1000,
    "佳樂水": 10,
    "龍頭山": 300,
    "七股鹽山": 5,
    "四草綠色隧道": 2,
    "蓮池潭龍虎塔": 5,
    "白楊瀑布": 480,
    "赤科山": 900,
    "鹿野高台": 350,
    "太麻里金針山": 1340,
    "桶盤嶼": 20,
    "栗松溫泉": 1075,
    "加里山": 2220,
    "武陵農場": 1900,
    "卡拉勞山谷雲霧眺望": 1219,  # CL-DATA-43 (Hawaii)
    "冒納凱亞遊客站銀河": 2804,  # CL-DATA-43 (Hawaii)

}

# Approximate primary shooting direction (degrees clockwise from true north).
# Only used when the composition direction is reasonably stable; omitted when
# a spot supports many directions. This allows sunrise/sunset alignment hints
# without pretending every landscape has one fixed composition.
VIEW_AZIMUTH_OVERRIDES = {
    "淡水漁人碼頭": (285, 55),
    "大稻埕碼頭": (270, 55),
    "高美濕地": (270, 60),
    "王功漁港": (270, 60),
    "井仔腳鹽田": (270, 60),
    "屏東關山": (270, 55),
    "崇德清水斷崖展望點": (155, 70),
    "七星潭": (90, 60),
    "三仙台": (90, 60),
    "龍磐公園": (90, 80),
    "石梯坪": (90, 80),
    "建功嶼": (270, 80),
    "池西岩瀑": (270, 80),
    "帆船鼻大草原": (90, 80),
    "綠島朝日溫泉": (90, 60),
    "蘭嶼東清灣": (90, 60),
    "小樽運河": (250, 80),
    "馬蹄灣": (250, 80),
    "紀念碑谷": (90, 85),
}


# Stable access constraints only. We intentionally avoid hard-coding seasonal
# business hours that may change. daylight_only means the photographic subject
# itself requires daylight; access_note_i18n warns the user to verify operator
# or facility hours separately.

# Estimated Bortle classes for astronomy-oriented locations.
# These are curated planning estimates, not live SQM measurements.  A confidence field
# is exported so the UI/score can distinguish a strong estimate from a fallback.
BORTLE_OVERRIDES = {
    '大屯山助航站': (6, 'medium'),
    '日月潭・水社壩湖景步道': (4, 'medium'),
    '日月潭': (4, 'medium'),
    '合歡山主峰': (2, 'high'),
    '金龍山': (4, 'medium'),
    '阿里山祝山觀日平台': (3, 'medium'),
    '阿里山': (3, 'medium'),
    '鵝鑾鼻燈塔': (3, 'medium'),
    '墾丁鵝鑾鼻': (3, 'medium'),
    '六十石山': (3, 'medium'),
    '龍磐公園': (3, 'medium'),
    '帆船鼻大草原': (3, 'medium'),
    '七星潭月牙灣': (5, 'medium'),
    '七星潭': (5, 'medium'),
    '三仙台': (3, 'medium'),
    '池上伯朗大道': (4, 'medium'),
    '玉山主峰': (2, 'high'),
    '雪山主峰': (2, 'high'),
    '雪山北峰': (2, 'high'),
    '奇萊主峰': (2, 'high'),
    '南湖大山': (1, 'high'),
    '嘉明湖': (2, 'high'),
    '大霸尖山': (2, 'high'),
    '北大武山': (2, 'high'),
    '池有山': (2, 'high'),
    '桃山': (2, 'high'),
    '品田山': (2, 'high'),
    '杉林溪': (4, 'medium'),
    '松蘿湖': (4, 'medium'),
    '加羅湖': (3, 'medium'),
    '奎壁山': (4, 'medium'),
    '金門得月樓': (5, 'medium'),
    '馬祖南竿': (4, 'medium'),
    '東引燈塔': (3, 'medium'),
    '綠島朝日溫泉': (3, 'medium'),
    '蘭嶼東清灣': (2, 'high'),
    '蘭嶼青青草原': (2, 'high'),
    '旭岳': (2, 'high'),
    '富士山 (河口湖)': (4, 'medium'),
    '大峽谷國家公園': (1, 'high'),
    '紀念碑谷': (2, 'high'),
    '拱門國家公園': (2, 'high'),
    '布萊斯峽谷國家公園': (2, 'high'),
    '優勝美地半圓頂': (2, 'high'),
    '大提頓國家公園': (2, 'high'),
    '雷尼爾山國家公園': (2, 'high'),
    '火山口湖國家公園': (1, 'high'),
    '死亡谷國家公園': (1, 'high'),
    '冰川國家公園': (2, 'high'),
    '峽谷地國家公園 梅薩拱門': (1, 'high'),
    '約書亞樹國家公園': (2, 'high'),
    '巨人柱國家公園': (4, 'medium'),
    '鋸齒山脈': (2, 'high'),
    '洛杉磯格里斐斯天文台': (9, 'high'),
    '白沙國家公園': (2, 'high'),
    '落磯山國家公園': (3, 'medium'),
    '迪納利國家公園': (1, 'high'),
    '費爾班克斯極光': (6, 'medium'),
    '珍娜溫泉': (3, 'medium'),
    '安克拉治': (8, 'high'),
    '蘇華德': (4, 'medium'),
    '哈徹山口': (2, 'high'),
    '馬塔努斯卡冰河': (2, 'high'),
    '威朗格利-聖埃利亞斯國家公園': (1, 'high'),
    '布魯克斯山脈': (1, 'high'),
    '北極圈地標': (1, 'high'),
    '諾姆': (4, 'medium'),
    '埃克盧特納湖': (3, 'medium'),
    '塔爾基特納': (3, 'medium'),
    '楚加奇州立公園': (3, 'medium'),
    '白令陸橋國家保護區': (1, 'high'),
    '育空河': (1, 'high'),
    '諾阿塔克河': (1, 'high'),
    '克拉克湖國家公園': (1, 'high'),
    '獨立礦山': (2, 'high')
}

def _dark_sky_meta(region_key, name_zh, category, scenes, themes):
    if not ({"milky_way", "aurora"} & set(themes or [])):
        return None
    if name_zh in BORTLE_OVERRIDES:
        cls, confidence = BORTLE_OVERRIDES[name_zh]
        source = "curated_estimate"
    else:
        # Conservative fallback for newly-added astronomy spots.  It is deliberately
        # approximate and marked low-confidence so it cannot masquerade as measured data.
        if region_key == "us" and category == "阿拉斯加":
            cls = 2 if "city" not in scenes else 7
        elif region_key == "us":
            cls = 3 if "city" not in scenes else 8
        elif region_key == "jp":
            cls = 3 if "mountain" in scenes else (8 if "city" in scenes else 5)
        else:
            if category in {"綠島/蘭嶼/小琉球", "馬祖"}:
                cls = 3
            elif "city" in scenes:
                cls = 7
            elif "mountain" in scenes:
                cls = 3
            else:
                cls = 4
        confidence = "low"
        source = "heuristic_fallback"
    cls = max(1, min(9, int(cls)))
    dark_sky_score = {1:100,2:94,3:86,4:74,5:60,6:45,7:30,8:18,9:8}[cls]
    return {
        "bortle_class": cls,
        "dark_sky_score": dark_sky_score,
        "light_pollution_source": source,
        "light_pollution_confidence": confidence,
    }

ACCESS_RULE_OVERRIDES = {
    "雲山水夢幻湖": {
        "access_mode": "opening_hours_private_park",
        "access_hours": ["08:30", "17:00"],
        "access_hours_source": "East Rift Valley National Scenic Area official attraction listing; verified 2026-09-25",
        "access_note_i18n": {
            "zh-TW": "雲山水植物農場目前官方列出的開放時間為每日 08:30–17:00；屬私人景觀園區，入園、票價與攝影區域以現場最新公告為準。",
            "en": "The official attraction listing currently gives daily hours of 08:30–17:00. This is a private landscaped park; follow current on-site admission and photography-area rules.",
            "ja": "公式観光案内の現在の営業時間は毎日08:30〜17:00です。私設景観園区のため、入園・料金・撮影範囲は現地の最新案内に従ってください。",
        },
    },
    "大農大富平地森林園區": {
        "access_mode": "opening_hours",
        "access_hours": ["08:00", "17:00"],
        "access_hours_source": "Forestry and Nature Conservation Agency official recreation page; verified 2026-09-25",
        "access_note_i18n": {
            "zh-TW": "推薦時段採官方服務時間 08:00–17:00。園區全年開放；遊客中心除夕及每週一休館，寒暑假與國定假日例外。步道與自行車道遇落葉、潮濕或青苔可能濕滑。",
            "en": "Recommendations use the official 08:00–17:00 service window. The park is open year-round; the visitor center closes on Lunar New Year's Eve and Mondays, except school vacations and national holidays. Paths may be slippery when wet or covered by leaves or moss.",
            "ja": "推奨時間は公式サービス時間08:00〜17:00です。園区は通年開放で、ビジターセンターは旧暦大晦日と月曜休館（長期休暇・祝日を除く）。落葉・湿気・苔で路面が滑る場合があります。",
        },
    },
    "唐津城": {
        "access_mode": "opening_hours",
        "access_hours": ["05:00", "22:00"],
        "access_hours_source": "Karatsu Tourism Association flower map for Karatsu Castle / Maizuru Park; verified 2026-09-27",
        "access_note_i18n": {
            "zh-TW": "舞鶴公園官方花巡資料列 05:00–22:00；天守內部另為 09:00–17:00、16:40 最終入館且可能季節調整。外部公園時段不可當作天守內部已開放。",
            "en": "Official Maizuru Park guidance lists 05:00–22:00. The castle keep is separately 09:00–17:00 with last entry 16:40 and may change seasonally; park access does not prove keep access.",
            "ja": "舞鶴公園は公式案内で05:00〜22:00。天守閣内部は別契約で09:00〜17:00（最終入館16:40、季節変更あり）。公園が開いていても天守開館を意味しません。",
        },
    },
    "長崎哥拉巴園": {
        "access_mode": "opening_hours",
        "access_hours": ["08:00", "18:00"],
        "access_hours_source": "Glover Garden official 2026 opening schedule; conservative baseline verified 2026-09-27",
        "access_note_i18n": {
            "zh-TW": "全年保守基準採 08:00–18:00；2026 多個期間有延長夜間開園，且貸切／天候可改變時段。夜間題材只依當年度官方夜間公告，不把18:00後永久視為開放。",
            "en": "A conservative 08:00–18:00 baseline is used. Several 2026 periods have extended night opening, and private events/weather may alter hours. Night Opportunities rely on current-year official notices rather than assuming permanent after-hours access.",
            "ja": "通年の保守的な基準は08:00〜18:00。2026年は複数期間で夜間延長があり、貸切・天候で変更されます。夜間撮影は当年の公式案内に限定し、18時以降を恒常開園とは扱いません。",
        },
    },
    "福岡塔": {
        "access_mode": "opening_hours",
        "access_hours": ["09:30", "21:30"],
        "access_hours_source": "Fukuoka Tower official hours; last admission cutoff verified 2026-09-27",
        "access_note_i18n": {
            "zh-TW": "展望室官方營業 09:30–22:00，最終入館 21:30；推薦進入截止採21:30，若已在館內可停留至22:00，臨時營運調整仍以官方為準。",
            "en": "Observation rooms are officially open 09:30–22:00 with last admission at 21:30. Recommendations use 21:30 as the entry cutoff; guests already inside may remain until closing.",
            "ja": "展望室は公式09:30〜22:00、最終入館21:30。推奨入館締切は21:30とし、入館済みの場合は閉館22:00まで滞在できます。",
        },
    },
    "神戶六甲山": {
        "access_mode": "opening_hours",
        "access_hours": ["07:10", "21:00"],
        "access_hours_source": "Kobe Mt. Rokko official Tenrandai page; verified 2026-09-27",
        "access_note_i18n": {
            "zh-TW": "天覽台官方目前開放 07:10–21:00、無固定休息日；停車場24小時開放不代表展望台24小時可進入。",
            "en": "Tenrandai is currently listed open 07:10–21:00 with no regular closing day. The 24-hour parking lot does not mean the observation deck is open 24 hours.",
            "ja": "天覧台の現在の公式開放時間は07:10〜21:00、定休日なし。駐車場が24時間開放でも、展望台自体が24時間開放という意味ではありません。",
        },
    },
    "出雲大社": {
        "access_mode": "opening_hours",
        "access_hours": ["06:00", "19:00"],
        "access_hours_source": "Izumo Oyashiro official 2026-05-03 visiting-hours notice; checked 2026-09-25",
        "access_note_i18n": {
            "zh-TW": "境內一般參拜 06:00–19:00；其他時段僅能在銅鳥居前參拜。私人紀念攝影應避免妨礙參拜；超出私人鑑賞的公開／商業拍攝須事先向神社申請。",
            "en": "General precinct visiting hours are 06:00–19:00; outside those hours worship is from before the bronze torii. Personal photography should respect worshippers; public or commercial filming beyond personal use requires prior shrine permission.",
            "ja": "境内の通常参拝時間は06:00～19:00。時間外は銅鳥居前からの参拝です。個人撮影は参拝者に配慮し、個人鑑賞の範囲を超える公開・業務撮影は事前許可が必要です。",
        },
    },
    "東京鐵塔": {
        "access_mode": "opening_hours",
        "access_hours": ["09:00", "22:30"],
        "access_hours_source": "Tokyo Tower official Main Deck hours/last admission; verified 2026-09-25",
        "access_note_i18n": {
            "zh-TW": "Main Deck 官方營業 09:00–23:00，最終入場 22:30；推薦抵達時間以 22:30 為截止，臨時營運調整仍以官方公告為準。",
            "en": "Main Deck is officially open 09:00–23:00 with last admission at 22:30; recommendations use 22:30 as the arrival cutoff. Verify same-day operational notices.",
            "ja": "メインデッキは公式09:00〜23:00、最終入場22:30。推奨到着時刻は22:30を締切とし、当日の運営変更は公式案内を確認してください。",
        },
    },
    "鎌倉大佛": {
        "access_mode": "opening_hours",
        "access_hours_seasonal": [
            {"start_mmdd": "04-01", "end_mmdd": "09-30", "windows": [["08:00", "17:15"]]},
            {"start_mmdd": "10-01", "end_mmdd": "03-31", "windows": [["08:00", "16:45"]]},
        ],
        "access_hours_source": "Kotoku-in official grounds hours and 15-minute-before-closing last-entry rule; verified 2026-09-25",
        "access_note_i18n": {
            "zh-TW": "高德院 4–9 月開門 08:00–17:30、最終入場 17:15；10–3 月 08:00–17:00、最終入場 16:45。個人用途可於境內拍攝，但大佛胎內禁止攝影。",
            "en": "Kotoku-in grounds: Apr–Sep 08:00–17:30 (last entry 17:15); Oct–Mar 08:00–17:00 (last entry 16:45). Personal-use photography is allowed on the grounds, but photography inside the Great Buddha is prohibited.",
            "ja": "高徳院は4〜9月08:00〜17:30（最終入場17:15）、10〜3月08:00〜17:00（最終入場16:45）。境内での個人利用撮影は可能ですが、大仏胎内の撮影は禁止です。",
        },
    },
    "金澤兼六園": {
        "access_mode": "opening_hours",
        "access_hours_seasonal": [
            {"start_mmdd": "03-01", "end_mmdd": "03-31", "windows": [["05:00", "06:30"], ["07:00", "17:30"]]},
            {"start_mmdd": "04-01", "end_mmdd": "08-31", "windows": [["04:00", "06:30"], ["07:00", "17:30"]]},
            {"start_mmdd": "09-01", "end_mmdd": "10-15", "windows": [["05:00", "06:30"], ["07:00", "17:30"]]},
            {"start_mmdd": "10-16", "end_mmdd": "10-31", "windows": [["05:00", "07:30"], ["08:00", "16:30"]]},
            {"start_mmdd": "11-01", "end_mmdd": "02-29", "windows": [["06:00", "07:30"], ["08:00", "16:30"]]},
        ],
        "access_hours_source": "Kenroku-en Tourism Association official paid/early-morning opening and last-entry schedule; verified 2026-09-25",
        "access_note_i18n": {
            "zh-TW": "兼六園另有季節性早朝免費入園與一般入園時段；網站推薦以官方各時段最終入園時間作抵達截止。早朝僅開放指定入口，出發前仍請確認最新公告。",
            "en": "Kenroku-en has seasonal early-morning free-entry and regular paid-entry windows. Recommendations use each official last-entry time as the arrival cutoff; early entry uses designated gates only.",
            "ja": "兼六園は季節別の早朝無料入園と通常入園があります。推奨到着時刻は各公式最終入園時刻を締切とし、早朝入園は指定入口のみです。",
        },
    },
    "名古屋城": {
        "access_mode": "opening_hours",
        "access_hours": ["09:00", "16:30"],
        "access_closed_mmdd_ranges": [
            {"start_mmdd": "12-29", "end_mmdd": "01-01"},
        ],
        "access_hours_source": "Nagoya Castle official normal opening hours and fixed year-end closure; verified 2026-09-25",
        "access_note_i18n": {
            "zh-TW": "一般開園 09:00–16:30；12/29–1/1 固定休園。特別活動可能延長開園，但夜間延長不視為全年常態。",
            "en": "Normal opening is 09:00–16:30; closed Dec 29–Jan 1. Special events may extend hours, but event-only night access is not treated as year-round.",
            "ja": "通常開園は09:00〜16:30、12/29〜1/1は休園。特別催事で延長される場合がありますが、夜間延長は通年扱いしません。",
        },
    },
    "京都清水寺": {
        "access_mode": "opening_hours",
        "access_hours_seasonal": [
            {"start_mmdd": "01-01", "end_mmdd": "06-30", "windows": [["06:00", "18:00"]]},
            {"start_mmdd": "07-01", "end_mmdd": "08-31", "windows": [["06:00", "18:30"]]},
            {"start_mmdd": "09-01", "end_mmdd": "12-31", "windows": [["06:00", "18:00"]]},
        ],
        "access_hours_source": "Kiyomizu-dera official baseline opening schedule; verified 2026-09-25. Annual special night-viewing extensions are intentionally not repeated as a permanent rule.",
        "access_note_i18n": {
            "zh-TW": "一般拝觀基準為 06:00–18:00，7–8 月通常至 18:30；年度夜間特別拝觀依官方當年日期另行公告，不視為全年夜間開放。境內禁止三腳架、單腳架與無人機，請僅手持拍攝且勿妨礙參拜動線。",
            "en": "Baseline visiting hours are 06:00–18:00, usually to 18:30 in Jul–Aug. Annual special night viewing is date-specific and is not treated as year-round access. Tripods, monopods and drones are prohibited; use handheld photography without obstructing visitors.",
            "ja": "通常拝観は06:00〜18:00、7〜8月は通常18:30まで。夜間特別拝観は年度ごとの指定日に限り、通年夜間開放とは扱いません。三脚・一脚・ドローンは禁止です。",
        },
    },
    "綠島朝日溫泉": {
        "access_mode": "opening_hours",
        "access_hours_windows": [["05:00", "10:00"], ["16:00", "23:00"]],
        "access_hours_effective_from": "2026-08-01",
        "access_hours_verified_on": "2026-09-24",
        "access_hours_source": "East Coast National Scenic Area official attraction page",
        "access_note_i18n": {
            "zh-TW": "官方 2026/08/01 起目前時段為 05:00–10:00、16:00–23:00；營運時間會隨季節調整，出發前仍應確認最新公告。",
            "en": "Current official hours from 2026-08-01 are 05:00–10:00 and 16:00–23:00; hours change seasonally, so verify the latest notice before departure.",
            "ja": "公式の現行時間（2026/08/01〜）は05:00–10:00、16:00–23:00。季節により変更されるため、出発前に最新情報を確認してください。",
        },
    },
    "南竿鐵堡": {
        "access_mode": "opening_hours_and_weather_control",
        "access_hours": ["08:00", "17:00"],
        "access_hours_source": "Matsu NSA official attraction page; verified 2026-09-24",
        "access_note_i18n": {
            "zh-TW": "官方目前列每日 08:00–17:00；長浪或強風時可能關閉。夜間不可假設可進入。",
            "en": "Official hours are currently 08:00–17:00 daily; long-period waves or strong winds may trigger closure. Do not assume night access.",
            "ja": "現在の公式営業時間は毎日08:00〜17:00。長周期波や強風時は閉鎖される場合があります。夜間入場を前提にしないでください。",
        },
    },
    "野柳地質公園": {
        "access_mode": "opening_hours",
        # Conservative all-year contract. The official site also states a
        # summer extension to 18:00, but does not define the seasonal date
        # range on the hours page; do not infer dates. A future authoritative
        # hours provider may override this 17:00 default when the active summer
        # period is explicitly known.
        "access_hours": ["08:00", "17:00"],
        "access_hours_source": "Yehliu Geopark official hours page; verified 2026-09-24",
        "access_note_i18n": {
            "zh-TW": "一般開園 08:00–17:00，夏季通常至 18:00；特殊活動可能調整，拍攝前請查官方公告",
            "en": "Normally open 08:00–17:00, usually to 18:00 in summer; verify official notices for event changes",
            "ja": "通常08:00〜17:00、夏季は通常18:00まで。イベント時は公式案内を確認してください",
        },
    },
    "馬蹄灣": {
        "access_mode": "daylight_only",
        "access_hours_source": "U.S. National Park Service Horseshoe Bend Overlook page; verified 2026-09-27",
        "access_note_i18n": {
            "zh-TW": "NPS明確規定步道與觀景台僅日出至日落開放；停車場位於Page市有土地，繁忙時可能採接駁措施。",
            "en": "NPS states the trail and overlook are open sunrise to sunset only. The parking lot is on City of Page land and busy periods may use shuttle controls.",
            "ja": "NPSでは遊歩道・展望台は日の出から日没までのみ開放。駐車場はPage市管理で、混雑時はシャトル運用の場合があります。",
        },
    },
    "紀念碑谷": {
        "access_mode": "opening_hours",
        "access_hours": ["08:00", "17:00"],
        "access_hours_seasonal": [
            {"start_mmdd": "03-08", "end_mmdd": "04-30", "windows": [["07:00", "20:00"]]},
            {"start_mmdd": "05-01", "end_mmdd": "09-30", "windows": [["07:00", "19:00"]]},
            {"start_mmdd": "10-01", "end_mmdd": "01-31", "windows": [["08:00", "17:00"]]},
        ],
        "access_closed_mmdd_ranges": [
            {"start_mmdd": "12-25", "end_mmdd": "12-25"},
            {"start_mmdd": "01-01", "end_mmdd": "01-01"},
        ],
        "access_hours_source": "Navajo Nation Parks Monument Valley official park/hours pages; verified 2026-09-27",
        "access_note_i18n": {
            "zh-TW": "依Navajo Tribal Park官方季節營運時段；2/1–3/7採官方一般08:00–17:00保守基準。感恩節與Navajo Family Day屬浮動日期，網站尚未自動建模，出發前仍須查官方公告。Scenic Drive另有更早的最後車輛進入限制。",
            "en": "Uses published Navajo Tribal Park seasonal hours; Feb 1–Mar 7 falls back conservatively to the official regular 08:00–17:00 window. Thanksgiving/Family Day are moving-date closures not yet auto-modeled. Scenic Drive also has an earlier last-vehicle-entry cutoff.",
            "ja": "Navajo Tribal Park公式の季節営業時間を使用。2/1〜3/7は公式の一般08:00〜17:00を保守的に適用。感謝祭・Family Dayの変動休園日は未自動化のため公式確認が必要です。Scenic Driveは最終車両入場がさらに早い場合があります。",
        },
    },
    "羚羊峽谷": {
        "access_mode": "daylight_only",
        "access_note_i18n": {
            "zh-TW": "需參加授權導覽，實際入場時段請以營運商公告為準",
            "en": "Authorized tour required; verify current operator entry times",
            "ja": "認可ツアー参加が必要です。最新の入場時間を運営会社で確認してください",
        },
    },
    "西雅圖太空針塔": {
        "access_note_i18n": {
            "zh-TW": "觀景台有營業時間與票券限制，出發前請確認",
            "en": "Observation deck has ticketed opening hours; verify before visiting",
            "ja": "展望台は営業時間・チケット制です。訪問前に確認してください",
        },
    },
    "西雅圖派克市場": {
        "access_note_i18n": {
            "zh-TW": "市場各店營業時間不同，夜間部分區域氣氛與白天不同",
            "en": "Vendor hours vary; the market experience differs after hours",
            "ja": "店舗ごとに営業時間が異なり、夜間は雰囲気が変わります",
        },
    },
}

# B32 Japan Batch12: Todoroki Valley reopened on 2026-03-24, but the
# current Setagaya City notice explicitly says photography is not being accepted
# because of expected congestion. Keep the researched Place visible while
# failing closed for photographic recommendation until the notice is lifted or
# its scope is authoritatively clarified.
ACCESS_RULE_OVERRIDES["等等力溪谷"] = {
    "access_mode": "daylight_current_photography_hold",
    "access_note_i18n": {
        "zh-TW": "等々力溪谷川沿步道已於2026/3/24重新開放，但世田谷區目前公告因預期壅擠『不受理拍攝』；公告解除或範圍正式釐清前，ChaseLights不啟用攝影推薦。官方另要求天黑後勿進入，豪雨時遠離河道。",
        "en": "The riverside path reopened on 2026-03-24, but Setagaya City currently states that photography is not being accepted because of expected congestion. ChaseLights keeps photographic recommendations on hold until that notice is lifted or formally clarified. Do not enter after dark, and stay away from the river during heavy rain.",
        "ja": "川沿い園路は2026年3月24日に再開しましたが、世田谷区は混雑対策として現在『撮影は受け付けておりません』と案内しています。解除または範囲が公式に明確化されるまで撮影推薦は保留します。暗くなってからは立ち入らず、大雨時は川に近づかないでください。",
    },
}

# B32 Japan Batch11: Mt. Yahiko summit photography uses multi-route access.
# Ropeway, seasonal Skyline road and walking routes are not interchangeable;
# the annual Night View & Stargazing Cruise is a separate date-limited contract.
ACCESS_RULE_OVERRIDES["彌彥山"] = {
    "access_mode": "dynamic_multi_route_summit_status",
    "access_note_i18n": {
        "zh-TW": "彌彥山頂可由纜車、季節性彌彥山Skyline或步行路線到達，各路線限制不同；夜間纜車僅官方年度「夜景＆星空Cruise」指定日期運行，不可把一般晴朗夜晚視為可達。",
        "en": "Mt. Yahiko summit access is multi-modal: ropeway, seasonal Skyline road and hiking routes have different constraints. Night ropeway access is limited to official annual Night View & Stargazing Cruise dates; ordinary clear nights are not assumed accessible.",
        "ja": "弥彦山頂へのアクセスはロープウェイ、季節運用の弥彦山スカイライン、登山道で条件が異なります。夜間ロープウェイは公式の年間「夜景＆星空クルーズ」実施日に限り、通常の晴天夜を入場可能とは扱いません。",
    },
}

# B32 Japan Batch10: Shinhotaka summit photography anchor and access note.
# The legacy 36.1600,137.2600 coordinate is not the summit observation area.
ACCESS_RULE_OVERRIDES["新穗高高空纜車"] = {
    "access_mode": "dynamic_transport_status",
    "access_note_i18n": {
        "zh-TW": "西穗高口山頂區須搭乘新穗高纜車；營運可能因惡劣天候或定期維修停駛。夜間僅官方年度「星空觀賞便」指定日期可進入，不可把一般晴朗夜晚視為可達。",
        "en": "The Nishi-Hotakaguchi summit area depends on Shinhotaka Ropeway operation, which may be suspended for adverse weather or maintenance. Night access is limited to official annual Stargazing Service dates; ordinary clear nights are not assumed accessible.",
        "ja": "西穂高口の山頂エリアは新穂高ロープウェイの運行が前提で、悪天候や点検で運休する場合があります。夜間入場は公式の年間「星空観賞便」実施日に限り、通常の晴天夜を入場可能とは扱いません。",
    },
}

# V5.2: explicit photo-point / POI corrections.  Exact overrides win over
# broad legacy coordinates and name-derived scene heuristics.  map_query is
# also sent to the frontend so navigation can resolve the named POI even if
# a mountain/park covers a large area.
SPOT_OVERRIDES = {
    # CL-DATA-66 wave-1 admission (web-verified 2026-11-11; keyed to full display names per get_spots contract)
 "大崙山觀光茶園/銀杏森林": {"lat": 23.681681,
           "lon": 120.76637,
           "map_query": "大崙山觀光茶園",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: 玩全台灣旅遊網 大崙山觀光茶園 GoogleMap座標 23.681681,120.766370；海拔1250-1500m 帶（南投旅遊網官方頁）",
           "coordinate_confidence": "high"},
 "坪林南山寺仙公廟": {"lat": 24.9675371,
           "lon": 121.7272531,
           "map_query": "南山寺仙公廟",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: OSM Nominatim 南山寺（坪林漁光里樟空子路）；海拔查無權威源誠實留空",
           "coordinate_confidence": "medium"},
 "仙山靈洞宮後山": {"lat": 24.5415154,
           "lon": 120.950373,
           "map_query": "仙山靈洞宮",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: OSM Nominatim 協靈宮（仙山登山步道，獅潭新店村）；海拔967m（交通部觀光署多媒體開放資料：仙山海拔967公尺）",
           "coordinate_confidence": "medium"},
 "墨硯山琉璃光": {"lat": 24.5558111,
           "lon": 120.846273,
           "map_query": "墨硯山",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: OSM Nominatim 墨硯山南峰；海拔約157m（健行筆記/vocus 攻略）",
           "coordinate_confidence": "high"},
 "姜子寮山觀景台": {"lat": 25.053278,
           "lon": 121.73011,
           "map_query": "姜子寮山",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: zh.wikipedia 姜子寮山（25°03′11.8″N 121°43′48.4″E；海拔729m，小百岳）",
           "coordinate_confidence": "high"},
 "宇老觀景台": {"lat": 24.6675183,
           "lon": 121.2820376,
           "map_query": "宇老觀景台",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: OSM Nominatim 宇老觀景台（新竹60縣道20K）；海拔1450m（新竹尖石原住民文化館/拉美公司資料）",
           "coordinate_confidence": "high"},
 "山上人家農場": {"lat": 24.6047,
           "lon": 121.089,
           "map_query": "山上人家森林農場",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: iot-sky 開放資料（經度121.089 緯度24.6047）＋交通部觀光署多媒體開放資料（海拔約1200m）",
           "coordinate_confidence": "medium"},
 "石門二格山觀景台": {"lat": 24.9672358,
           "lon": 121.6196361,
           "map_query": "二格山",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: OSM Nominatim 二格山（石碇格頭里）；海拔678m（zh.wikipedia 二格山，小百岳）",
           "coordinate_confidence": "medium"},
 "集集大山轉播站": {"lat": 23.854861,
           "lon": 120.83806,
           "map_query": "集集大山",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: zh.wikipedia 集集大山（23°51′17.5″N 120°50′17″E；主峰1,390m；南投旅遊網記1,392m）",
           "coordinate_confidence": "high"},
 "1314觀景台": {"lat": 23.559532,
           "lon": 120.6789157,
           "map_query": "1314觀景台",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: OSM Nominatim 海鼠山（嘉義梅山）＋阿里山國家風景區管理處官方（海鼠山最高點海拔1,311m＋觀景台=1,314m）",
           "coordinate_confidence": "high"},
 "五分山雷達站": {"lat": 25.07278,
           "lon": 121.77278,
           "map_query": "五分山雷達站",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: 中央氣象署官方站況頁（東經121.77305 北緯25.07305 海拔740m）＋zh.wikipedia 五分山氣象雷達站",
           "coordinate_confidence": "high"},
 "埔里虎頭山虎嘯山莊": {"lat": 23.964167,
           "lon": 120.989944,
           "map_query": "虎嘯山莊",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: 虎嘯山莊官方對位座標 N23°57′51 E120°59′24（easycamp 登錄）＋ddnews（虎頭山約650m）",
           "coordinate_confidence": "medium"},
 "報時山觀景台": {"lat": 25.1136611,
           "lon": 121.8596306,
           "map_query": "報時山",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: zh.wikipedia 報時山（25°6′49.18″N 121°51′34.67″E；海拔295m；新北觀光局記260m 為步道口帶——取山頂295m 並註記）",
           "coordinate_confidence": "high"},
 "大同山/青龍嶺": {"lat": 25.003363,
           "lon": 121.403214,
           "map_query": "大同山/青龍嶺",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: 台灣66 全景資料（座標 25.003363, 121.403214；青龍嶺海拔約256m）＋新北觀光局（大同山237m）",
           "coordinate_confidence": "high"},
 "大武崙白沙灘/外木山": {"lat": 25.1568,
           "lon": 121.7056,
           "map_query": "大武崙白沙灘/外木山",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: 1968 開放資料 大武崙砲台（經度121.7056 緯度25.1568）＋基隆市文化局（大武崙山標高231m）；本點主題為外木山濱海大道日落海岸帶（非戲水）",
           "coordinate_confidence": "high"},
 "太平山森林遊樂區": {"lat": 24.5242406,
           "lon": 121.6228895,
           "map_query": "太平山",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: OSM Nominatim 太平山國家森林遊樂區；太平山帶海拔1,950-2,000m（林業保育署太平山官方頁/TPS）",
           "coordinate_confidence": "medium"},
 "奧萬大楓林步道": {"lat": 23.9489652,
           "lon": 121.1875001,
           "map_query": "奧萬大楓林步道",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: OSM Nominatim 奧萬大國家森林遊樂區；園區海拔1,100-2,600m（南投旅遊網/林業保育署）——楓林區帶取1,100m",
           "coordinate_confidence": "medium"},
 "安平漁人碼頭/大魚的祝福": {"lat": 22.9965428,
           "lon": 120.16379,
           "map_query": "安平漁人碼頭",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: OSM Nominatim 安平漁人碼頭（安億路）＋台南市政府（大魚的祝福裝置藝術）；海拔查無獨立權威值誠實留空",
           "coordinate_confidence": "medium"},
 "富貴角風稜石": {"lat": 25.298217,
           "lon": 121.536583,
           "map_query": "富貴角風稜石",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: 交通部航港局 富貴角燈塔官方（WGS84 北緯25°17.893′ 東經121°32.195′）；海拔誠實留空",
           "coordinate_confidence": "high"},
 "東眼山國家森林遊樂區三角點": {"lat": 24.818749,
           "lon": 121.4161228,
           "map_query": "東眼山",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: OSM Nominatim 東眼山國家森林遊樂區；東眼山海拔1,212m（林業保育署官方）",
           "coordinate_confidence": "medium"},
 "東華聖宮": {"lat": 24.9379719,
           "lon": 121.5198804,
           "map_query": "東華聖宮",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: OSM Nominatim 東華聖宮（新店華城里）＋廟宇登錄——知名琉璃光/百萬夜景點為新店東華聖宮（mook/欣傳媒列名）；候選清單 region 欄『南投魚池』疑為誤植，座標以新店東華聖宮對位；海拔誠實留空",
           "coordinate_confidence": "medium"},
 "藤枝國家森林遊樂區": {"lat": 23.0657536,
           "lon": 120.7470591,
           "map_query": "藤枝",
           "coordinate_source": "CL-DATA-66 wave-1 admission web verification 2026-11-11: OSM Nominatim 藤枝（桃源區）＋林業保育署官方（園區海拔500-1,804m；主要遊憩帶1,500-1,804m）",
           "coordinate_confidence": "medium"},
    # CL-DATA-64 admission (web-verified 2026-11-10; keyed to full display names per get_spots contract)
 "北竿塘后道沙灘藍眼淚": {"lat": 26.222827,
           "lon": 120.00476,
           "map_query": "塘后道沙灘",
           "coordinate_source": "CL-DATA-64 admission web verification 2026-11-10: 交通部觀光署 塘后道沙灘（120.00476/26.222827；北竿機場旁連島沙洲「糖沙」）",
           "coordinate_confidence": "medium"},
 "南竿北海坑道（夜間搖櫓藍眼淚）": {"lat": 26.143015,
           "lon": 119.92881,
           "map_query": "北海坑道",
           "coordinate_source": "CL-DATA-64 admission web verification 2026-11-10: 交通部觀光署 南竿北海坑道（119.92881/26.143015；坑道口少光害、夜間搖櫓賞淚官方遊程）",
           "coordinate_confidence": "high"},
 "東莒福正沙灘藍眼淚（東犬燈塔旁）": {"lat": 25.966231,
           "lon": 119.98215,
           "map_query": "福正沙灘",
           "coordinate_source": "CL-DATA-64 admission web verification 2026-11-10: 交通部觀光署 福正聚落（119.98215/25.966231；沙灘在聚落旁、東犬燈塔下）",
           "coordinate_confidence": "medium"},
 "南竿大漢據點藍眼淚（鐵板海岸）": {"lat": 26.140628,
           "lon": 119.92906,
           "map_query": "大漢據點",
           "coordinate_source": "CL-DATA-64 admission web verification 2026-11-10: 交通部觀光署 大漢據點（119.92906/26.140628；南竿南方鐵板海岸線，官方追淚點列名）",
           "coordinate_confidence": "high"},
 "老忠實間歇泉（黃石）": {"lat": 44.46047,
           "lon": -110.82814,
           "map_query": "Old Faithful",
           "coordinate_source": "CL-DATA-64 admission web verification 2026-11-10: Wikipedia Old Faithful（44°27′38″N 110°49′41″W；標高 7,349 ft/2,240 m）+ NPS Old Faithful Geyser（平均間隔約90分鐘，變動50–127分鐘；2025-01 起中位數 102±10 分鐘——NPS 預測僅供現場參考，非本系統預報）",
           "coordinate_confidence": "high"},
 "牽牛花溫泉池（黃石上間歇泉盆地）": {"lat": 44.4750325,
           "lon": -110.8435128,
           "map_query": "Morning Glory Pool",
           "coordinate_source": "CL-DATA-64 admission web verification 2026-11-10: Wikipedia Morning Glory Pool（44°28′30″N 110°50′37″W；Upper Geyser Basin 深緣藍心熱泉）",
           "coordinate_confidence": "high"},
 "別府海地獄": {"lat": 33.316056,
           "lon": 131.4690056,
           "map_query": "海地獄",
           "coordinate_source": "CL-DATA-64 admission web verification 2026-11-10: ja.wikipedia 別府地獄めぐり（海地獄：北緯33度18分57.8秒 東経131度28分8.42秒；98°C 鈷藍熱泉池，國指定名勝）",
           "coordinate_confidence": "high"},
 "別府血池地獄": {"lat": 33.327125,
           "lon": 131.4782583,
           "map_query": "血の池地獄",
           "coordinate_source": "CL-DATA-64 admission web verification 2026-11-10: ja.wikipedia 別府地獄めぐり（血の池地獄：北緯33度19分37.65秒 東経131度28分41.73秒；紅色熱泥池，日本最古の天然地獄）",
           "coordinate_confidence": "high"},
 "草津湯畑": {"lat": 36.622806,
           "lon": 138.596639,
           "map_query": "草津湯畑",
           "coordinate_source": "CL-DATA-64 admission web verification 2026-11-10: ja.wikipedia 草津温泉（湯畑：北緯36度37分22秒 東経138度35分48秒；溫泉街中心，每分約4,000L 湧出，國指定名勝・特別名勝；標高約1,200 m 帶——溫泉街廣域值，medium）",
           "coordinate_confidence": "high"},
 "地獄谷野猿公苑": {"lat": 36.732806,
           "lon": 138.462694,
           "map_query": "地獄谷野猿公苑",
           "coordinate_source": "CL-DATA-64 admission web verification 2026-11-10: ja.wikipedia 地獄谷野猿公苑（北緯36度43分58.1秒 東経138度27分45.7秒；海拔約850 m——zh.wikipedia；上信越高原國立公園橫湯川峽谷，冬期積雪約4個月）",
           "coordinate_confidence": "high"},
 "基勞亞口熔岩紅光夜拍（基勞亞展望台）": {"lat": 19.4071,
           "lon": -155.285,
           "map_query": "Kilauea Overlook",
           "coordinate_source": "CL-DATA-64 admission web verification 2026-11-10: NPS Hawaiʻi Volcanoes NP / Wikipedia Kīlauea（基勞亞展望台，口緣 rim；山頂標高約 1,227 m 帶；座標 medium（展望台對位））",
           "coordinate_confidence": "medium"},
 "那胡庫熔岩管（瑟斯頓熔岩洞）": {"lat": 19.4134,
           "lon": -155.243,
           "map_query": "Nāhuku",
           "coordinate_source": "CL-DATA-64 admission web verification 2026-11-10: NPS Nāhuku Lava Tube（Kīlauea summit 區 Crater Rim Drive；座標 medium（tube 對位））",
           "coordinate_confidence": "medium"},
 "基勞亞伊奇火山口熔岩地表": {"lat": 19.417,
           "lon": -155.244,
           "map_query": "Kīlauea Iki",
           "coordinate_source": "CL-DATA-64 admission web verification 2026-11-10: NPS Hawaiʻi Volcanoes NP（Kīlauea Iki Overlook 與環線步道；1959 年噴發熔岩湖面；座標 medium（Overlook 對位））",
           "coordinate_confidence": "medium"},
    # CL-DATA-53 admission (web-verified 2026-11-09; keyed to full display names per get_spots contract)
 "波浪谷（The Wave）": {"lat": 36.8617,
           "lon": -112.398,
           "map_query": "The Wave",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: BLM/recreation.gov Coyote Buttes North（The Wave，Vermilion Cliffs NM，亞利桑那側；Coyote Buttes 北區約5,700 ft 帶）；座標 medium（波浪窪地中心推定）",
           "coordinate_confidence": "medium"},
 "哥倫比亞河峽谷（羅威娜岬）": {"lat": 45.6686,
           "lon": -121.4357,
           "map_query": "Rowena Crest",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: Friends of the Columbia Gorge / Wikipedia 哥倫比亞河峽谷（羅威娜岬觀景台， historic Columbia River Highway 對位）；座標 medium（觀景台推定）",
           "coordinate_confidence": "medium"},
 "比克斯比溪橋（大瑟爾）": {"lat": 36.0727,
           "lon": -121.9046,
           "map_query": "Bixby Creek Bridge",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: Wikipedia Bixby Creek Bridge（36°04′22″N 121°54′17″W，1932年拱橋橋面高約85 m；加州 Big Sur 海岸）",
           "coordinate_confidence": "high"},
 "麥克威瀑布（朱莉婭·菲佛州立公園）": {"lat": 36.3586,
           "lon": -121.9762,
           "map_query": "McWay Falls",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: California State Parks / Wikipedia 麥克威瀑布（80呎（約24m）落於海灘；36°21′30″N 121°58′37″W 對位）",
           "coordinate_confidence": "high"},
 "褐鈴山（馬倫湖倒影）": {"lat": 39.0975,
           "lon": -106.9886,
           "map_query": "Maroon Bells",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: USGS/USFS White River NF（Maroon Lake 約2,884 m；北峰4,317 m/南峰4,270 m；39°05′51″N 106°59′15″W 對位）",
           "coordinate_confidence": "high"},
 "瓦爾迪茲基石峽谷瀑布": {"lat": 61.0414,
           "lon": -146.2389,
           "map_query": "Keystone Canyon",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: Wikipedia Keystone Canyon（瓦爾迪茲公路沿理查森峽谷，Bridal Veil/Horsetail 瀑布；座標 medium（谷段對位））",
           "coordinate_confidence": "medium"},
 "白山坎坎瑪格斯公路": {"lat": 44.0234,
           "lon": -71.365,
           "map_query": "Kancamagus Highway",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: USFS White Mountain NF（Kancamagus Highway，NH 112；Kancamagus Pass 約3,037 ft 為公路最高點；座標 medium（Pass 對位））",
           "coordinate_confidence": "medium"},
 "藍嶺公路林恩灣高架橋": {"lat": 36.0897,
           "lon": -81.7994,
           "map_query": "Linn Cove Viaduct",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: NPS Blue Ridge Parkway / Wikipedia 林恩灣高架橋（1987年 S 形高架繞大霧山東緣格蘭德father山，橋面高約1,250 m 帶；座標 medium）",
           "coordinate_confidence": "medium"},
 "白口袋（朱紅斷崖國家紀念地）": {"lat": 36.9561,
           "lon": -111.9043,
           "map_query": "White Pocket",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: BLM White Pocket Trailhead（36.955011,-111.893296）+ Wikipedia White Pocket（36°27′28″N 111°42′15″W 中心帶，6,100 ft 帶）",
           "coordinate_confidence": "medium"},
 "反射峽谷（鮑威爾湖）": {"lat": 37.1746,
           "lon": -110.9038,
           "map_query": "Reflection Canyon",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: Glen Canyon NRA 產業級徒步記錄（Reflection Canyon overlook，peak 約4,466 ft/1,361 m；座標 medium（展望台推定））",
           "coordinate_confidence": "medium"},
 "工廠台地（月球地貌）": {"lat": 38.3767,
           "lon": -110.9003,
           "map_query": "Factory Butte",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: recreation.gov Factory Butte Recreation Area（38.365881,-110.915269）+ Capitol Reef Country（staging area 38.376667,-110.900278）；Butte 峰 6,302 ft/1,921 m（Wikipedia）",
           "coordinate_confidence": "high"},
 "煤礦峽谷（納瓦霍保留區）": {"lat": 36.0053,
           "lon": -111.0486,
           "map_query": "Coal Mine Canyon",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: thewave.info Coal Mine Canyon guide（rim 5,800 ft/1,768 m，Tuba City 東南 15 mi；座標 medium（rim 對位））+ Wikipedia Coalmine Canyon",
           "coordinate_confidence": "medium"},
 "比斯蒂/迪納津荒野": {"lat": 36.0911,
           "lon": -108.2356,
           "map_query": "Bisti/De-Na-Zin",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: Wikipedia Bisti/De-Na-Zin（36°05′N 108°14′W 帶；BLM 荒野，入口停車場與次級路對位）",
           "coordinate_confidence": "medium"},
 "太浩湖盆景岩": {"lat": 39.0744,
           "lon": -120.0394,
           "map_query": "Bonsai Rock",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: Lake Tahoe shoreline 推定（盆景岩，東岸靜水區；座標 medium；湖面 1,897 m）",
           "coordinate_confidence": "medium"},
 "古狐尾松森林（舒爾曼林）": {"lat": 37.5917,
           "lon": -118.6111,
           "map_query": "Schulman Grove",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: USFS Inyo NF（Schulman Grove 約9,847 ft/3,001 m，白山白山公路盡頭；座標 high）",
           "coordinate_confidence": "high"},
 "使徒群島海蝕洞（冰洞）": {"lat": 46.7389,
           "lon": -90.9978,
           "map_query": "Meyers Beach ice caves",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: NPS Apostle Islands（Meyers Beach 冰洞路線，蘇必略湖面約183 m；座標 medium（岸線對位））",
           "coordinate_confidence": "medium"},
 "卡多湖（西班牙苔蘚）": {"lat": 32.7236,
           "lon": -94.1531,
           "map_query": "Caddo Lake",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: Wikipedia Caddo Lake（32°43′N 94°09′W 帶；最大南方淡水湖，沼澤地與柏樹）",
           "coordinate_confidence": "high"},
 "帕洛杜羅峽谷（燈塔岩）": {"lat": 34.97,
           "lon": -101.68,
           "map_query": "Palo Duro Canyon",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: Texas Parks & Wildlife / Wikipedia 帕洛杜羅峽谷（全美第二大峽谷；Lighthouse 岩區約34°58′N 101°41′W 帶；座標 medium）",
           "coordinate_confidence": "medium"},
 "沃特金斯格倫州立公園": {"lat": 42.3792,
           "lon": -76.7467,
           "map_query": "Watkins Glen",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: Wikipedia/NY State Parks 沃特金斯格倫（Glen Creek 19 瀑與峽谷步道；42°22′N 76°45′W 帶）",
           "coordinate_confidence": "high"},
 "斯帕克斯小巷（凱德斯谷）": {"lat": 35.6114,
           "lon": -83.8192,
           "map_query": "Sparks Lane",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: NPS Great Smoky Mountains（Cades Cove Loop 環線，Sparks Lane 對位；座標 medium）",
           "coordinate_confidence": "medium"},
 "水晶磨坊": {"lat": 39.05889,
           "lon": -107.10389,
           "map_query": "Crystal Mill",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: Wikipedia/NRHP Crystal Mill（1892年木造水力廠，39°03′32″N 107°06′14″W；NRHP 85001493）",
           "coordinate_confidence": "high"},
 "冰湖盆地": {"lat": 37.8114,
           "lon": -107.7899,
           "map_query": "Ice Lake",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: USFS/Colorado Lakes（Ice Lake 約12,260 ft/3,735 m；trailhead 37.8119,-107.7925；San Juan NF）",
           "coordinate_confidence": "high"},
 "特柳賴德（Last Dollar Road）": {"lat": 37.8836,
           "lon": -108.0053,
           "map_query": "Last Dollar Road",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: Telluride tourism / San Miguel County（Last Dollar Road，特柳賴德西北；座標 medium（路脊推定））",
           "coordinate_confidence": "medium"},
 "大沙丘國家公園": {"lat": 37.781,
           "lon": -105.531,
           "map_query": "Great Sand Dunes",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: NPS Great Sand Dunes（全美最高沙丘；Sangre de Cristo 山腳，37°47′N 105°31′W 帶）",
           "coordinate_confidence": "high"},
 "胡德山特里利姆湖": {"lat": 45.2617,
           "lon": -121.7417,
           "map_query": "Trillium Lake",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: USFS Mt Hood NF / Wikipedia Trillium Lake（3,812 ft/1,162 m；胡德山南眺定番）",
           "coordinate_confidence": "high"},
 "阿比奎瀑布": {"lat": 44.9528,
           "lon": -122.2131,
           "map_query": "Abiqua Falls",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: Marion County/Wikipedia 網摘（Abiqua Falls，哥倫比亞玄武岩圓頂兩側瀑布；座標 medium）",
           "coordinate_confidence": "medium"},
 "普羅克斯瀑布": {"lat": 44.1408,
           "lon": -122.2278,
           "map_query": "Proxy Falls",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: USFS McKenzie Ranger District（Proxy Falls，麥肯齊通道三姐妹荒野；座標 medium）",
           "coordinate_confidence": "medium"},
 "彩繪山（約翰戴化石床）": {"lat": 44.6597,
           "lon": -120.1111,
           "map_query": "Painted Hills",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: NPS John Day Fossil Beds（Painted Hills unit，44°39′N 120°06′W 帶）",
           "coordinate_confidence": "high"},
 "斑馬狹縫峽谷": {"lat": 37.661,
           "lon": -111.421,
           "map_query": "Zebra Slot",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: Hiking Project/REXBY（Zebra Slot，Hole-in-the-Rock Rd；slot 段約5,200 ft 帶；座標 medium）",
           "coordinate_confidence": "medium"},
 "膨潤土丘陵（大教堂谷）": {"lat": 38.3611,
           "lon": -111.1278,
           "map_query": "Bentonite Hills",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: NPS Bentonite Hills page（38°21′N 111°08′W 帶；Cathedral Valley Loop；Hartnet Rd 高底盤車）+ Wilderness Portal 座標 38.36109,-111.12776",
           "coordinate_confidence": "medium"},
 "約書亞樹國家公園（凱斯觀景台）": {"lat": 33.8928,
           "lon": -116.1888,
           "map_query": "Joshua Tree NP",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: NPS Joshua Tree（Keys View 5,185 ft/1,580 m；33°53′N 116°11′W 帶）",
           "coordinate_confidence": "high"},
 "特羅納石塔": {"lat": 35.6611,
           "lon": -117.3453,
           "map_query": "Trona Pinnacles",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: BLM Trona Pinnacles（tufa spires，National Natural Landmark；座標 medium（石塔群對位））",
           "coordinate_confidence": "medium"},
 "拉森火山（彩繪沙丘）": {"lat": 40.5264,
           "lon": -121.2722,
           "map_query": "Painted Dunes",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: NPS Lassen（Cinder Cone Painted Dunes，Butte Lake 區；座標 medium（沙丘對位））",
           "coordinate_confidence": "medium"},
 "愛達荷暗夜保護區（愛麗絲湖）": {"lat": 43.9391,
           "lon": -114.9437,
           "map_query": "Alice Lake",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: Wikipedia Alice Lake (Sawtooth Wilderness)（43°56′21″N 114°56′37″W；surface 8,602 ft/2,622 m）",
           "coordinate_confidence": "high"},
 "月球火山紀念地": {"lat": 43.4169,
           "lon": -113.4977,
           "map_query": "Craters of the Moon",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: NPS Craters of the Moon（43°25′N 113°30′W 帶；國際暗夜公園）",
           "coordinate_confidence": "high"},
 "肖肖尼瀑布（西尼加拉）": {"lat": 42.7547,
           "lon": -114.4214,
           "map_query": "Shoshone Falls",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: City of Twin Falls / Wikipedia Shoshone Falls（212 呎高、900 呎寬；42°45′N 114°25′W 帶）",
           "coordinate_confidence": "high"},
 "乾龜國家公園（傑佛遜堡）": {"lat": 24.628,
           "lon": -82.8735,
           "map_query": "Dry Tortugas",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: NPS Dry Tortugas（Garden Key Fort Jefferson；24°37′41″N 82°52′25″W 對位）",
           "coordinate_confidence": "high"},
 "哈特拉斯角燈塔": {"lat": 35.2113,
           "lon": -75.5213,
           "map_query": "Cape Hatteras Lighthouse",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: NPS Cape Hatteras（美國最高的磚砌燈塔 198 呎；35°12′41″N 75°31′17″W）",
           "coordinate_confidence": "high"},
 "阿薩蒂格島野馬": {"lat": 38.0111,
           "lon": -75.2814,
           "map_query": "Assateague Island",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: NPS Assateague Island NS（障壁島野馬；38°00′N 75°17′W 帶；座標 medium）",
           "coordinate_confidence": "medium"},
 "哈丁冰原（奇奈峽灣）": {"lat": 59.995,
           "lon": -149.69,
           "map_query": "Harding Icefield",
           "coordinate_source": "CL-DATA-53 admission web verification 2026-11-09: NPS Kenai Fjords（Harding Icefield Trail，Exit Glacier 上方冰原展望；座標 medium（trail viewpoint 推定））",
           "coordinate_confidence": "medium"},
    # CL-DATA-52 admission (web-verified 2026-11-09; keyed to full display names per get_spots contract)
 "富士山頂（剣ヶ峰）": {"lat": 35.3606,
           "lon": 138.7274,
           "map_query": "富士山頂",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 富士山（山頂剣ヶ峰 35°21′38″N 138°43′39″E；標高3,776 m）",
           "coordinate_confidence": "high"},
 "新倉山淺間公園": {"lat": 35.3631,
           "lon": 138.6692,
           "map_query": "新倉山浅間公園",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 新倉山浅間公園（展望台・忠霊塔，山腹展望台約410 m；山梨県富士吉田市）",
           "coordinate_confidence": "high"},
 "上高地大正池／河童橋": {"lat": 36.2377,
           "lon": 137.6194,
           "map_query": "上高地",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 大正池（36°14′16″N 137°37′10″E；1915年燒岳噴火形成，標高約1,510 m）＋上高地官方（河童橋）",
           "coordinate_confidence": "high"},
 "立山みくりが池／雪之大谷": {"lat": 36.5702,
           "lon": 137.5964,
           "map_query": "みくりが池",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia みくりが池（室堂平，標高約2,405–2,450 m 帯）＋立山黒部貫光官方（雪の大谷）",
           "coordinate_confidence": "medium"},
 "美瑛拼布之路（名樹群）": {"lat": 43.6486,
           "lon": 142.5678,
           "map_query": "美瑛パッチワークの路",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 美瑛（パッチワークの路，ケンとメリーの木一帶丘陵）；座標 medium（名樹群中心推定）",
           "coordinate_confidence": "medium"},
 "奧入瀨溪流（阿修羅之瀧）": {"lat": 39.7221,
           "lon": 141.0071,
           "map_query": "奥入瀬渓流",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 奥入瀬渓流（阿修羅の滝，十和田湖畔子ノ口至燒山）；座標 medium（渓流步道中段推定）",
           "coordinate_confidence": "medium"},
 "蔦沼": {"lat": 39.8808,
           "lon": 140.8748,
           "map_query": "蔦沼",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 蔦七沼（蔦沼，八戸_lp…）；座標 medium（蔦沼畔推定）；海拔無權威單一值——誠實留空",
           "coordinate_confidence": "medium"},
 "白川鄉合掌村": {"lat": 36.2585,
           "lon": 136.904,
           "map_query": "白川郷",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 白川郷（荻町 36°15′31″N 136°54′14″E；UNESCO世界遺產）；海拔無單一）；海拔無單一權威值——誠實留空",
           "coordinate_confidence": "high"},
 "SORA terrace 龍王雲海": {"lat": 36.7236,
           "lon": 138.8837,
           "map_query": "SORA terrace",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: 候選清單提供座標（138.8837,36.7236）＋龍王纜車官方（SORA terrace 標高1,933 m）",
           "coordinate_confidence": "high"},
 "竹田城跡（天空之城）": {"lat": 35.2945,
           "lon": 134.8392,
           "map_query": "竹田城跡",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 竹田城（天守台標高353.6 m；兵庫県朝来市）",
           "coordinate_confidence": "high"},
 "秩父美之山公園雲海": {"lat": 36.0288,
           "lon": 138.9467,
           "map_query": "美の山公園",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 美の山（みの山，約1,038 m；埼玉県秩父郡）；座標 medium（山頂展望台推定）",
           "coordinate_confidence": "medium"},
 "大觀峰（阿蘇五嶽）": {"lat": 32.9056,
           "lon": 131.0756,
           "map_query": "大観峰",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 大観峰（北外輪山，標高913 m；熊本県阿蘇市）；座標 medium（展望台推定）",
           "coordinate_confidence": "medium"},
 "白鬚神社海上鳥居": {"lat": 35.4829,
           "lon": 136.1229,
           "map_query": "白鬚神社",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 白鬚神社（湖中鳥居，琵琶湖西岸）；琵琶湖面標高約85 m",
           "coordinate_confidence": "high"},
 "父母之濱（天空之鏡）": {"lat": 33.8072,
           "lon": 133.2622,
           "map_query": "父母ヶ浜",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 父母ヶ浜（香川県三豊市仁尾町；海濱岸線）",
           "coordinate_confidence": "high"},
 "五色沼（毘沙門沼）": {"lat": 37.7553,
           "lon": 140.1032,
           "map_query": "五色沼",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 五色沼（磐梯高原，毘沙門沼 37°45′20″N 140°06′10″E；標高約800 m帯）",
           "coordinate_confidence": "medium"},
 "田貫湖（鑽石富士）": {"lat": 35.2192,
           "lon": 138.5594,
           "map_query": "田貫湖",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 田貫湖（富士山麓堰止湖，標高約800 m；静岡県富士市）",
           "coordinate_confidence": "high"},
 "鍋瀑布（水簾洞）": {"lat": 33.1373,
           "lon": 131.0357,
           "map_query": "鍋ヶ滝",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 鍋ヶ滝（33°8′14.4″N 131°2′8.5″E；落差12m 幅20m；熊本県小国町）",
           "coordinate_confidence": "high"},
 "仁淀川（仁淀藍）": {"lat": 33.75,
           "lon": 133.03,
           "map_query": "仁淀川",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 仁淀川（四国第二長河，上流域仁淀川町）；座標 low——「仁淀ブルー」最佳淵位無單一權威點，以村域錨點誠實標註，待 field survey 校正",
           "coordinate_confidence": "low"},
 "吹割瀑布": {"lat": 36.9146,
           "lon": 139.2997,
           "map_query": "吹割の滝",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 吹割の滝（沼田市片品町，片品川30m落差如海割裂）；座標 medium（觀瀑台推定）；海拔無單一權威值——誠實留空",
           "coordinate_confidence": "medium"},
 "隱岐蠟燭島": {"lat": 36.24,
           "lon": 132.956,
           "map_query": "蠟燭島",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: 日本國家旅遊局/島根觀光官方（蠟燭島，島後岸外約500m，高約20m，夕陽對準時如點燃蠟燭；觀光船 3/15–11/30 需預約）；座標 low——岸外岩礁無精確權威點，以岬角錨點推定",
           "coordinate_confidence": "low"},
 "青島（鬼之洗衣板）": {"lat": 31.8106,
           "lon": 131.4556,
           "map_query": "青島",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 青島 (宮崎県)（周囲約860m 小島與隆起海蝕波状岩帯）；座標 high（青島神社前灘）",
           "coordinate_confidence": "high"},
 "九十九島群峰": {"lat": 33.0324,
           "lon": 129.5906,
           "map_query": "九十九島",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: 佐世保觀光官方（九十九島，208島群，展海峰展望台）；座標 medium（展海峰推定）；海拔無單一權威值——誠實留空",
           "coordinate_confidence": "medium"},
 "常陸海濱公園": {"lat": 36.0608,
           "lon": 140.5578,
           "map_query": "国営ひたち海浜公園",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 国営ひたち海浜公園（36°03′38″N 140°33′27″E；みはらしの丘粉蝶花/掃帚草）",
           "coordinate_confidence": "high"},
 "大淵笹場（茶田富士）": {"lat": 35.129,
           "lon": 138.583,
           "map_query": "大淵笹場",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: 富士市官方（大淵笹場，富士市大淵1445，無電線茶園越し富士）；座標 medium（茶畑中心推定，地址對位）；海拔無單一權威值——誠實留空",
           "coordinate_confidence": "medium"},
 "阿智村（日本第一星空）": {"lat": 35.5066,
           "lon": 137.8474,
           "map_query": "阿智村",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 阿智村（環境省「星のうみ」認定日本一星空，昼神溫泉一帶）；座標 medium（村域・晝神溫泉對位）",
           "coordinate_confidence": "medium"},
 "波照間島（南十字星）": {"lat": 24.2337,
           "lon": 123.7583,
           "map_query": "波照間島",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 波照間島（日本最南端有人島，高那崎）；座標 medium（高那崎對位）；日本唯一可見南十字星全貌",
           "coordinate_confidence": "medium"},
 "屋久島白谷雲水峽": {"lat": 30.3883,
           "lon": 130.6064,
           "map_query": "白谷雲水峡",
           "coordinate_source": "CL-DATA-52 admission web verification 2026-11-09: ja.wikipedia 白谷雲水峡（屋久島安房川支流，入口標高約620 m；宮崎駿もののけ姫の森）；座標 medium（入口遊歩道對位）",
           "coordinate_confidence": "medium"},
    # CL-DATA-51 admission (web-verified 2026-11-09)
 "桃源谷（灣坑頭山草原）": {"lat": 24.974556,
           "lon": 121.910444,
           "map_query": "桃源谷",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: zh.wikipedia 灣坑頭山（桃源谷所在，24°58′28.4″N 121°54′37.6″E，山頂觀景平台）",
           "coordinate_confidence": "high"},
 "石碇千島湖／鱷魚潭": {"lat": 24.9326,
           "lon": 121.666,
           "map_query": "石碇千島湖",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: 新北市觀光旅遊網官方（石碇永安里，翡翠水庫上游北勢溪集水區；鱷魚島/土虱頭觀景台）；海拔推定約500 m（北宜公路沿線山頭），座標 medium",
           "coordinate_confidence": "medium"},
 "林口水牛坑（林口大峽谷）": {"lat": 25.119684,
           "lon": 121.318558,
           "map_query": "林口水牛坑",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: zh.wikipedia 林口大峽谷（座標 25°07′11″N 121°19′07″E）",
           "coordinate_confidence": "high"},
 "三貂角燈塔": {"lat": 25.007,
           "lon": 122.001,
           "map_query": "三貂角燈塔",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: zh.wikipedia 三貂角燈塔（25°00′25″N 122°00′04″E）＋交通部航港局（1935年啟用，台灣本島最東燈塔）；海拔無權威單一值——誠實留空",
           "coordinate_confidence": "high"},
 "清境農場": {"lat": 24.0586,
           "lon": 121.1639,
           "map_query": "清境農場",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: zh.wikipedia 清境農場（24°03′31″N 121°09′50″E；海拔約1,700–2,000m）＋南投縣旅遊網官方（1,748m）",
           "coordinate_confidence": "high"},
 "忘憂森林": {"lat": 23.651305,
           "lon": 120.794012,
           "map_query": "忘憂森林",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: 臺灣蹓蹓 VR 實景（座標 23.651305, 120.794012；南投縣竹山鎮）；海拔無權威值（921地震堰塞沼澤，各源 1,500–2,000m 說法分歧）——誠實留空",
           "coordinate_confidence": "medium"},
 "太平雲梯／梅山36彎": {"lat": 23.5599,
           "lon": 120.5978,
           "map_query": "太平雲梯",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: zh.wikipedia 太平雲梯（23°33′36″N 120°35′52″E；全長281m；海拔約1,000m，台灣海拔最高景觀吊橋）＋阿里山國家風景區管理處官方",
           "coordinate_confidence": "high"},
 "萬年峽谷": {"lat": 23.6024363,
           "lon": 120.6679,
           "map_query": "萬年峽谷",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: wanniancanyon.com 官方導覽站（座標 23.6024363, 120.6679；雲林縣古坑鄉草嶺，149甲縣道）；海拔無權威單一值——誠實留空",
           "coordinate_confidence": "high"},
 "佳樂水": {"lat": 22.0028186,
           "lon": 120.873576,
           "map_query": "佳樂水",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: zh.wikipedia 佳樂水（座標 22°00′10″N 120°52′25″E）＋大鵬灣國家風景區管理處官方（台26線盡頭，滿州鄉）",
           "coordinate_confidence": "high"},
 "龍頭山／多納環流丘": {"lat": 22.882,
           "lon": 120.659,
           "map_query": "龍頭山",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: 茂林國家風景區管理處官方（龍頭山遊憩區，高132線12K附近，約22公頃環流丘地形，三面環山溪流蜿蜒）；座標 medium（高132線12K推定）",
           "coordinate_confidence": "medium"},
 "七股鹽山／潟湖": {"lat": 23.155276,
           "lon": 120.10535,
           "map_query": "七股鹽山",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: zh.wikipedia 七股鹽山（座標 23°09′19″N 120°06′19″E）＋雲嘉南濱海國家風景區管理處官方",
           "coordinate_confidence": "high"},
 "四草綠色隧道": {"lat": 23.01959,
           "lon": 120.13633,
           "map_query": "四草綠色隧道",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: 交通部觀光署官方（經度/緯度 120.13633/23.019590；臺南市安南區大眾路360號）＋雲嘉南風管處",
           "coordinate_confidence": "high"},
 "蓮池潭龍虎塔": {"lat": 22.678695,
           "lon": 120.29691,
           "map_query": "蓮池潭龍虎塔",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: 交通部觀光署官方（經度/緯度 120.29691/22.678695；高雄市左營區蓮潭路）",
           "coordinate_confidence": "high"},
 "太魯閣燕子口／九曲洞": {"lat": 24.1717,
           "lon": 121.5767,
           "map_query": "太魯閣燕子口",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: 太魯閣國家公園管理處官方（燕子口步道至靳珩橋大理石峽谷段、九曲洞步道）；海拔無單一權威值——誠實留空；座標 medium（燕子口靳珩橋段推定）",
           "coordinate_confidence": "medium"},
 "白楊瀑布": {"lat": 24.1742639,
           "lon": 121.4744167,
           "map_query": "白楊瀑布",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: zh.wikipedia 白楊瀑布（座標 24°10′27.35″N 121°28′27.90″E，太魯閣族語『達歐拉斯＝斷崖瀑布』）；海拔推定約480m（白楊步道沿線）medium",
           "coordinate_confidence": "medium"},
 "赤科山金針花海": {"lat": 23.4433,
           "lon": 121.4587,
           "map_query": "赤科山",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: zh.wikipedia 赤科山（花蓮縣玉里鎮，海拔約900m）；座標 medium（玉里鎮竹田村山區推定）",
           "coordinate_confidence": "medium"},
 "鹿野高台": {"lat": 22.913389,
           "lon": 121.119611,
           "map_query": "鹿野高台",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: en.wikipedia Luye Highlands（Elevation 350 m; Coordinates 22°54′48.2″N 121°07′10.6″E）",
           "coordinate_confidence": "high"},
 "太麻里金針山": {"lat": 22.6113,
           "lon": 120.9959,
           "map_query": "太麻里金針山",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: 太麻里鄉公所官方（金針山休閒農業區，462公頃）＋太麻里山小百岳1,340m（samejantravel）；座標 low_medium（雙乳峰一帶推定）——誠實標註",
           "coordinate_confidence": "medium"},
 "桶盤嶼柱狀玄武岩": {"lat": 23.511225,
           "lon": 119.5185278,
           "map_query": "桶盤嶼",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: zh.wikipedia 桶盤嶼（座標 23°30′40.41″N 119°31′06.70″E）＋澎湖國家風景區管理處官方（桶盤地質公園，柱狀節理澎湖之最）",
           "coordinate_confidence": "high"},
 "栗松溫泉野溪峽谷": {"lat": 23.1979087,
           "lon": 121.0371977,
           "map_query": "栗松溫泉",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: zh.wikipedia 栗松溫泉（座標 23°11′52″N 121°02′14″E；台東縣海端鄉新武呂溪支流峽谷，海拔1,075m）",
           "coordinate_confidence": "high"},
 "加里山": {"lat": 24.5375,
           "lon": 120.9907,
           "map_query": "加里山",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: zh.wikipedia 加里山（標高2,220m，台灣小百岳，苗栗縣山）＋林務局步道官方（recreation.forest.gov.tw）＋萌芽三角點庫（一等三角點 2220m）；座標 medium（一等三角點山頂推定）",
           "coordinate_confidence": "medium"},
 "武陵農場": {"lat": 24.364611,
           "lon": 121.31035,
           "map_query": "武陵農場",
           "coordinate_source": "CL-DATA-51 admission web verification 2026-11-09: zh.wikipedia 武陵農場（座標 24°21′52.6″N 121°18′37.26″E）＋交通部觀光署櫻花季頁（海拔1,740–2,200m，1993年起種櫻）",
           "coordinate_confidence": "high"},
 # CL-DATA-32 discovery admission (web-verified 2026-11-08)
 "嚴島神社・宮島大鳥居": {"lat": 34.29602,
           "lon": 132.31989,
           "map_query": "厳島神社 大鳥居",
           "coordinate_source": "CL-DATA-32 admission web verification 2026-11-08: ja.wikipedia 厳島神社 (article coordinate 34.29602,132.31989); UNESCO World Heritage shrine area",
           "coordinate_confidence": "high"},
 "備中松山城・雲海（天空の城）": {"lat": 34.80909,
           "lon": 133.62233,
           "map_query": "備中松山城雲海展望台",
           "coordinate_source": "CL-DATA-32 admission web verification 2026-11-08: ja.wikipedia 備中松山城 (article coordinate 34.80909,133.62233); elevation 430 m 高梁市公式雲海展望台ページ",
           "coordinate_confidence": "high"},
 "天橋立": {"lat": 35.56936,
           "lon": 135.19153,
           "map_query": "天橋立",
           "coordinate_source": "CL-DATA-32 admission web verification 2026-11-08: ja.wikipedia 天橋立 (article coordinate 35.56936,135.19153); sandbar anchor",
           "coordinate_confidence": "high"},
 "伊根的舟屋": {"lat": 35.67572,
           "lon": 135.28744,
           "map_query": "伊根の舟屋",
           "coordinate_source": "CL-DATA-32 admission web verification 2026-11-08: ja.wikipedia 伊根の舟屋 (article coordinate 35.67572,135.28744)",
           "coordinate_confidence": "high"},
 "鳥取砂丘": {"lat": 35.5425,
           "lon": 134.23028,
           "map_query": "鳥取砂丘",
           "coordinate_source": "CL-DATA-32 admission web verification 2026-11-08: ja.wikipedia 鳥取砂丘 (article coordinate 35.5425,134.23028)",
           "coordinate_confidence": "high"},
 "大山（剣ヶ峰）": {"lat": 35.3711,
           "lon": 133.5464,
           "map_query": "大山・剣ヶ峰",
           "coordinate_source": "CL-DATA-32 admission web verification 2026-11-08: ja.wikipedia 大山 (鳥取県) (article coordinate 35.3711,133.5464); elevation 1729 m (剣ヶ峰, 中国地方最高峰)",
           "coordinate_confidence": "high"},
 "稻佐山夜景": {"lat": 32.75336,
           "lon": 129.84933,
           "map_query": "稲佐山展望台",
           "coordinate_source": "CL-DATA-32 admission web verification 2026-11-08: ja.wikipedia 稲佐山 (article coordinate 32.75336,129.84933); elevation 333 m",
           "coordinate_confidence": "high"},
 "櫻島・湯之平展望所": {"lat": 31.5915,
           "lon": 130.6299,
           "map_query": "湯之平展望所",
           "coordinate_source": "CL-DATA-32 admission web verification 2026-11-08: Wikidata Q110582222 (Yunohira Observatory 31.5915,130.6299)",
           "coordinate_confidence": "high"},
 "阿蘇山・草千里ヶ浜": {"lat": 32.88417,
           "lon": 131.10389,
           "map_query": "草千里ヶ浜",
           "coordinate_source": "CL-DATA-32 admission web verification 2026-11-08: ja.wikipedia 阿蘇山 (article coordinate 32.88417,131.10389); grassland anchor within the caldera",
           "coordinate_confidence": "high"},
 "角島大橋": {"lat": 34.35277,
           "lon": 130.88616,
           "map_query": "角島大橋",
           "coordinate_source": "CL-DATA-32 admission web verification 2026-11-08: ja.wikipedia 角島大橋 (article coordinate 34.35277,130.88616)",
           "coordinate_confidence": "high"},
 "錦帯橋": {"lat": 34.1676,
           "lon": 132.17837,
           "map_query": "錦帯橋",
           "coordinate_source": "CL-DATA-32 admission web verification 2026-11-08: Wikidata Q1196460 (Kintai Bridge 34.16760,132.17837)",
           "coordinate_confidence": "high"},
 "祖谷的藤橋（祖谷渓）": {"lat": 33.87528,
           "lon": 133.83528,
           "map_query": "祖谷のかずら橋",
           "coordinate_source": "CL-DATA-32 admission web verification 2026-11-08: ja.wikipedia かずら橋 (article coordinate 33.87528,133.83528)",
           "coordinate_confidence": "high"},
 "松山城（伊予）": {"lat": 33.84554,
           "lon": 132.76572,
           "map_query": "松山城",
           "coordinate_source": "CL-DATA-32 admission web verification 2026-11-08: Wikidata Q981357 (Matsuyama Castle 33.84554,132.76572)",
           "coordinate_confidence": "high"},
 "元乃隅稻成神社": {"lat": 34.41972,
           "lon": 131.06278,
           "map_query": "元乃隅稲成神社",
           "coordinate_source": "CL-DATA-32 admission web verification 2026-11-08: ja.wikipedia 元乃隅神社 (article coordinate 34.41972,131.06278)",
           "coordinate_confidence": "high"},
 "渭水之丘／櫻花陵園": {"lat": 24.823055,
           "lon": 121.7025,
           "map_query": "渭水之丘",
           "coordinate_source": "CL-DATA-25R admission web verification 2026-11-07: zh.wikipedia 櫻花陵園 (24°49′23″N 121°42′9″E = 24.8231,121.7025；渭水之丘在園區最高丘地) — CL-DATA-23 dossier approx 24.636,121.64 與實際位置偏差大，依 web 證據修正；海拔約750–800 m（zh.wikipedia：海拔約750至800公尺，取 dossier 800）",
           "coordinate_confidence": "medium_high"},
 # CL-DATA-25 discovery admission (web-verified 2026-11-07)
 "雲海テラス（トマム）": {"lat": 43.0617,
           "lon": 142.6228,
           "map_query": "星野リゾート トマム 雲海テラス",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: ja.wikipedia 星野リゾート トマム (resort-area coordinate; terrace on Mt Tomamu gondola top station); elevation 1088 m official snowtomamu.jp/summer/unkai/",
           "coordinate_confidence": "medium_high"},
 "蔵王樹氷（蔵王ロープウェイ・山形側）": {"lat": 38.154781,
           "lon": 140.431075,
           "map_query": "蔵王ロープウェイ地蔵山頂駅",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: 山形県公式景観物語（緯度・経度情報 38.154781,140.431075 地蔵山頂駅）; elevation 地蔵岳1,661 m zaoropeway.co.jp",
           "coordinate_confidence": "high"},
 "津別峠展望台（屈斜路湖雲海）": {"lat": 43.5769,
           "lon": 144.2242,
           "map_query": "津別峠展望施設",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: yamareco 津別峠展望台 (北緯43度34分37秒 東経144度13分27秒 = 43.5769,144.2242); elevation 947 m official HOKKAIDO LOVE! / shortlist 951 m yamareco",
           "coordinate_confidence": "high"},
 "美幌峠展望台": {"lat": 43.6483,
           "lon": 144.2461,
           "map_query": "美幌峠 展望台",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: yamareco 美幌峠 (43度38分54秒/144度14分46秒 = 43.6483,144.2461; roadtabi 43.648569,144.248497); elevation 525 m 川湯エコミュージアン公式",
           "coordinate_confidence": "high"},
 "知床ウトロ流氷（プユニ岬）": {"lat": 44.0958,
           "lon": 145.0093,
           "map_query": "プユニ岬",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: mapion プユニ岬 (44.0958,145.0093); cape max elevation ~125 m 北海道の岬カタログ（国土地理院標高データ）",
           "coordinate_confidence": "medium_high"},
 "森吉山樹氷平（阿仁スキー場）": {"lat": 39.955,
           "lon": 140.4919,
           "map_query": "阿仁スキー場 樹氷平",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: ja.wikipedia 阿仁スキー場 (北緯39度57分18秒 東経140度29分31秒 = 39.9550,140.4919); elevation not verified (gondola top area) — left null honestly",
           "coordinate_confidence": "high"},
 "富田農場ラベンダーイースト": {"lat": 43.4189,
           "lon": 142.4266,
           "map_query": "ファーム富田 ラベンダーイースト",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: ja.wikipedia ファーム富田 (43.4189,142.4266; 中富良野町 base farm area — Lavender East field is on the hillside east of the base farm); elevation unverified — null",
           "coordinate_confidence": "medium"},
 "十二湖・青池": {"lat": 40.5603,
           "lon": 139.9844,
           "map_query": "十二湖 青池",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: yamareco 青池（十二湖）(北緯40度33分37秒 東経139度59分04秒 = 40.5603,139.9844); elevation unverified — null",
           "coordinate_confidence": "high"},
 "地球岬展望台": {"lat": 42.30272,
           "lon": 141.00067,
           "map_query": "地球岬展望台",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: MapFan 地球岬展望台 (42.3027208,141.0006723); 100 m cliff 室蘭市公式",
           "coordinate_confidence": "high"},
 "タウシュベツ川橋梁（幻の橋）": {"lat": 43.4156,
           "lon": 143.1892,
           "map_query": "タウシュベツ川橋梁",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: ja.wikipedia タウシュベツ川橋梁 (43.4156,143.1892); lake surface level (505 m 浸水→515 m 全没) per taushubetsu-journal水位紀錄 — spot elevation left null",
           "coordinate_confidence": "medium_high"},
 "八甲田山樹氷（八甲田ロープウェー）": {"lat": 40.6808,
           "lon": 140.8317,
           "map_query": "八甲田ロープウェー 山頂公園駅",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: ja.wikipedia 八甲田ロープウェー (40.6808,140.8317, dim~1km 山頂公園駅周辺); elevation 1,324 m 山頂公園駅 official hakkoda-ropeway.jp",
           "coordinate_confidence": "medium_high"},
 "北山崎（三陸断崖）": {"lat": 39.97934,
           "lon": 141.953,
           "map_query": "北山崎展望台",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: mapion 北山崎（第一展望台）(39.97934,141.95300); cliff height 200 m 田野畑村公式 — viewpoint elevation unverified (null)",
           "coordinate_confidence": "medium_high"},
 "蔵王御釜（五色湖）": {"lat": 38.1364,
           "lon": 140.4494,
           "map_query": "蔵王 御釜",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: ja.wikipedia 御釜 (蔵王連峰) waterbody coordinate 38.1364,140.4494 (dim~10km; viewing point 38.1277,140.4462 per jmapcode mapcode 569 428 898*66); lake elevation unverified (null)",
           "coordinate_confidence": "medium_high"},
 "安比高原雲海ゴンドラ": {"lat": 39.9944,
           "lon": 140.9642,
           "map_query": "安比ゴンドラ UNKAIデッキ",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: ja.wikipedia 安比高原スキー場 (39.9944,140.9642 resort area; UNKAIデッキ山頂 1,304 m official appi.co.jp APPI1304); verifiability lowest of the admitted set (official press fragment only)",
           "coordinate_confidence": "medium"},
 "大雪山森林遊樂區43K觀景台": {"lat": 24.1833,
           "lon": 121.0167,
           "map_query": "大雪山國家森林遊樂區 43K 遊客中心",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: CL-DATA-23 dossier approx (林道43K遊客中心一帶, 中海拔雪山山脈東側); elevation 2,450 m dossier/林業署園區資料; precise 43K 樁點座標未取得一手 → approx + medium confidence",
           "coordinate_confidence": "medium"},
 "翠峰湖環山步道觀景點": {"lat": 24.514583,
           "lon": 121.606889,
           "map_query": "翠峰湖",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: zh.wikipedia 翠峰湖 (24°30′52.5″N 121°36′24.8″E = 24.514583,121.606889); elevation 1,840 m dossier/太平山園區資料",
           "coordinate_confidence": "high"},
 "觀霧榛山步道觀景點": {"lat": 24.506139,
           "lon": 121.113833,
           "map_query": "觀霧國家森林遊樂區 榛山步道",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: zh.wikipedia 觀霧國家森林遊樂區 (24°30′22.1″N 121°06′49.8″E = 24.506139,121.113833, 園區/管理站代表點; 榛山步道觀景點在園區內約1.5 km 範圍) — area anchor + medium-high",
           "coordinate_confidence": "medium_high"},
 "加路蘭海岸遊憩區": {"lat": 22.7864,
           "lon": 121.1839,
           "map_query": "加路蘭遊憩區",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: 東部海岸國家風景區管理處官網（台11線155K 加路蘭遊憩區）＋dossier座標 22.7864,121.1839；2027(民115)2/23起園區整修全年不開放 — 需在 access note 標示",
           "coordinate_confidence": "medium_high"},
 "司馬庫斯部落觀景點": {"lat": 24.5976,
           "lon": 121.3246,
           "map_query": "司馬庫斯部落",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: CL-DATA-23 dossier approx (司馬庫斯部落, 海拔約1,500–1,600 m zh.wikipedia); 部落代表點座標未一手核實 → approx + medium",
           "coordinate_confidence": "medium"},
 "北關海潮公園": {"lat": 24.793,
           "lon": 121.875,
           "map_query": "北關海潮公園",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: 東北角及宜蘭海岸國家風景區官網（頭城鎮更新里, 台2線129.9K）＋dossier座標 24.793,121.875；龜山島朝日夏季方位",
           "coordinate_confidence": "medium_high"},
 "福壽山農場觀景點": {"lat": 24.23,
           "lon": 121.318,
           "map_query": "福壽山農場",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: 福壽山農場官網（台中市和平區梨山村福壽路29號, 台7甲線）＋dossier座標 24.23,121.318；農場代表點座標未一手核實 → approx + medium",
           "coordinate_confidence": "medium"},
 "東莒燈塔（東犬燈塔）": {"lat": 25.9672,
           "lon": 119.9856,
           "map_query": "東莒島燈塔",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: zh.wikipedia 東莒島燈塔 (25°58′02″N 119°59′08″E = 25.9672,119.9856); 塔高19.5 m / 焦點 64 m (dossier elev 64 m = 燈焦點語義)",
           "coordinate_confidence": "high"},
 "塔塔加夫妻樹／鹿林山觀景點": {"lat": 23.475,
           "lon": 120.875,
           "map_query": "塔塔加夫妻樹",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: 玉山國家公園管理處官方（夫妻樹位於新中橫台21線141.2K, 海拔約2,478 m）；座標為 141.2K 里程碑近似值（23.475,120.875 approx）→ medium",
           "coordinate_confidence": "medium"},
 "半天寮好望角": {"lat": 24.603,
           "lon": 120.745,
           "map_query": "半天寮好望角",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: 苗栗縣政府旅遊網（後龍鎮半天寮好望角）＋dossier座標 24.603,120.745；海線日落缺口",
           "coordinate_confidence": "medium_high"},
 "擎天崗草原": {"lat": 25.1664,
           "lon": 121.5743,
           "map_query": "擎天崗",
           "coordinate_source": "CL-DATA-25 admission web verification 2026-11-07: zh.wikipedia 擎天崗 (25°09′59″N 121°34′27″E = 25.1664,121.5743) — shortlist值 25.1169,121.5549 偏差約6km 已修正",
           "coordinate_confidence": "high"},
 '六十石山': {'lat': 23.219472,
          'lon': 121.308056,
          'scenes': ['mountain', 'rural'],
          'themes': ['mountain_view', 'sunset', 'sunbeam'],
          'map_query': '23.219472,121.308056',
          'coordinate_source': 'B34 Huanghua Pavilion parking/arrival anchor; Camera Zones modeled separately',
          'coordinate_confidence': 'medium_high'},
 '鯉魚潭': {'lat': 23.93493,
          'lon': 121.50803,
          'scenes': ['lake', 'mountain'],
          'themes': ['reflection'],
          'map_query': '23.93493,121.50803',
          'coordinate_source': 'Taiwan Tourism official north-shore visitor-center coordinate and public lakeside evidence',
          'coordinate_confidence': 'high'},
 '雲山水夢幻湖': {'lat': 23.827018,
          'lon': 121.51548,
          'scenes': ['lake', 'forest', 'rural'],
          'themes': ['reflection'],
          'map_query': '23.827018,121.51548',
          'coordinate_source': 'East Rift Valley official Place evidence; mapped Dream Lake area coordinate cross-check',
          'coordinate_confidence': 'medium_high'},
 '大農大富平地森林園區': {'lat': 23.6143836,
          'lon': 121.4159714,
          'scenes': ['forest', 'rural'],
          'themes': ['mountain_view'],
          'map_query': '23.6151728,121.4146215',
          'coordinate_source': 'Forestry and Nature Conservation Agency official forest-road feature and visitor-center coordinates',
          'coordinate_confidence': 'high'},
 '南雅奇岩': {'lat': 25.11982,
          'lon': 121.89314,
          'scenes': ['coast', 'geology'],
          'themes': ['sunrise', 'sunset', 'sky_glow', 'blue_hour'],
          'map_query': '南雅奇岩地質步道 新北市瑞芳區',
          'coordinate_source': 'B28 geotagged-photo Camera Zone; official Place anchor cross-check',
          'coordinate_confidence': 'high'},
 '老梅綠石槽': {'lat': 25.29242,
           'lon': 121.54446,
           'scenes': ['coast', 'geology'],
           'themes': ['sunrise', 'sky_glow', 'blue_hour'],
           'map_query': '老梅綠石槽 新北市石門區',
           'coordinate_source': 'B28 geotagged-photo Camera Zone; official Place anchor cross-check',
           'coordinate_confidence': 'high'},
 '野柳地質公園': {'lat': 25.20886,
           'lon': 121.69314,
           'scenes': ['coast', 'geology'],
           'themes': ['mountain_view'],
           'map_query': '野柳地質公園 女王頭 新北市萬里區',
           'coordinate_source': 'B28 geotagged Queen Head Camera Zone; official park access cross-check',
           'coordinate_confidence': 'high'},
 '外澳沙灘': {'lat': 24.87516,
         'lon': 121.84257,
         'scenes': ['coast'],
         'themes': ['sunrise', 'sky_glow', 'blue_hour'],
         'map_query': '外澳沙灘 宜蘭縣頭城鎮',
         'coordinate_source': 'B28 geotagged beach Camera Zone; official Waiao/Gueishan cross-check',
         'coordinate_confidence': 'high'},
 '龍磐公園': {'lat': 21.929,
         'lon': 120.848,
         'scenes': ['coast', 'grassland', 'geology'],
         'themes': ['sunrise', 'milky_way', 'mountain_view'],
         'map_query': '龍磐公園 屏東縣恆春鎮',
         'coordinate_source': 'B28 broad Camera Zone from official Place anchor + geotagged photo evidence',
         'coordinate_confidence': 'medium'},
 '石梯坪': {'lat': 23.49073,
        'lon': 121.51086,
        'scenes': ['coast', 'geology'],
        'themes': ['sunrise', 'mountain_view'],
        'map_query': '石梯坪 花蓮縣豐濱鄉',
        'coordinate_source': 'B28 geotagged-photo Camera Zone; Tourism Administration Place anchor cross-check',
        'coordinate_confidence': 'high'},
 '建功嶼': {'lat': 24.426386,
        'lon': 118.304369,
        'scenes': ['coast', 'architecture'],
        'themes': ['sunset', 'mountain_view'],
        'map_query': '建功嶼 金門縣金城鎮',
        'coordinate_source': 'B28 geotagged tidal-causeway Camera Zone; Taiwan Tourism official Place anchor cross-check',
        'coordinate_confidence': 'high'},
 '池西岩瀑': {'lat': 23.60345,
         'lon': 119.50265,
         'scenes': ['coast', 'geology'],
         'themes': ['sunset', 'mountain_view'],
         'map_query': '池西岩瀑 澎湖縣西嶼鄉',
         'coordinate_source': 'B28 multiple geotagged-photo Camera Zone; Penghu NSA official Place anchor cross-check',
         'coordinate_confidence': 'high'},
 '帆船鼻大草原': {'lat': 22.63366,
            'lon': 121.5069,
            'scenes': ['coast', 'grassland'],
            'themes': ['sunrise', 'milky_way'],
            'map_query': '帆船鼻大草原 綠島',
            'coordinate_source': 'B28 Tourism Administration official Place anchor; broad grassland Camera Zone',
            'coordinate_confidence': 'high'},
 '南竿鐵堡': {'lat': 26.141922,
          'lon': 119.921072,
          'scenes': ['coast', 'architecture'],
          'themes': ['mountain_view'],
          'map_query': '鐵堡 南竿',
          'coordinate_source': 'B28 Wikimedia/Panoramio camera geotag; Matsu NSA official Place anchor cross-check',
          'coordinate_confidence': 'high'},
 '大屯山助航站': {'lat': 25.17614,
            'lon': 121.52244,
            'map_query': '大屯山助航站 台北',
            'coordinate_source': 'OSM/Mapcarta POI',
            'coordinate_confidence': 'medium'},
 '象山六巨石攝影平台': {'lat': 25.02688,
               'lon': 121.57419,
               'map_query': '象山六巨石 台北',
               'coordinate_source': 'curated camera point',
               'coordinate_confidence': 'high'},
 '淡水漁人碼頭': {'lat': 25.18339,
            'lon': 121.41147,
            'map_query': '淡水漁人碼頭 情人橋',
            'coordinate_source': 'Taiwan scenic POI',
            'coordinate_confidence': 'high'},
 '九份不厭亭': {'lat': 25.08923,
           'lon': 121.84752,
           'scenes': ['mountain'],
           'themes': ['mountain_view', 'sunrise', 'sunset', 'cloud_sea'],
           'map_query': '不厭亭 新北市雙溪區',
           'coordinate_source': 'New Taipei Tourism + direct photography GPS',
           'coordinate_confidence': 'high'},
 '大稻埕碼頭': {'lat': 25.0564,
           'lon': 121.50761,
           'map_query': '大稻埕碼頭 台北',
           'coordinate_source': 'curated camera point',
           'coordinate_confidence': 'high'},
 '關渡大橋': {'lat': 25.125428,
          'lon': 121.45751,
          'map_query': '關渡大橋 台北',
          'coordinate_source': 'geographic POI',
          'coordinate_confidence': 'high'},
 '碧潭': {'lat': 24.95599,
        'lon': 121.5365,
        'map_query': '碧潭風景區 新店',
        'coordinate_source': 'Taiwan tourism POI',
        'coordinate_confidence': 'high'},
 '觀音山硬漢嶺': {'lat': 25.128356,
            'lon': 121.42433,
            'map_query': '硬漢嶺 觀音山',
            'coordinate_source': 'Taiwan tourism POI',
            'coordinate_confidence': 'high'},
 '望幽谷': {'lat': 25.146003,
         'lon': 121.797514,
         'map_query': '望幽谷 基隆',
         'coordinate_source': 'curated camera point',
         'coordinate_confidence': 'high'},
 '和平島': {'lat': 25.158066,
         'lon': 121.768055,
         'map_query': '和平島地質公園',
         'coordinate_source': 'curated camera point',
         'coordinate_confidence': 'high'},
 '永安漁港': {'lat': 24.98828,
          'lon': 121.01451,
          'map_query': '永安漁港 桃園',
          'coordinate_source': 'curated camera point',
          'coordinate_confidence': 'high'},
 '香山濕地': {'lat': 24.783421,
          'lon': 120.91431,
          'scenes': ['wetland', 'coast'],
          'themes': ['sunrise', 'sunset', 'sky_glow', 'blue_hour', 'fog_mist', 'reflection'],
          'map_query': '香山濕地賞蟹步道',
          'coordinate_source': 'Taiwan tourism POI',
          'coordinate_confidence': 'high'},
 '火炎山': {'lat': 24.369396,
         'lon': 120.72806,
         'scenes': ['mountain', 'geology'],
         'themes': ['mountain_view', 'sunrise', 'sunset'],
         'map_query': '火炎山自然保留區',
         'coordinate_source': 'official natural reserve',
         'coordinate_confidence': 'high'},
 '雲洞山莊': {'lat': 24.388806,
          'lon': 120.822056,
          'map_query': '雲洞山莊 苗栗',
          'coordinate_source': 'official site DMS',
          'coordinate_confidence': 'high'},
 '高美濕地': {'lat': 24.31195,
          'lon': 120.54981,
          'scenes': ['wetland', 'coast'],
          'themes': ['sunset', 'sky_glow', 'blue_hour', 'reflection'],
          'map_query': '高美濕地木棧道',
          'coordinate_source': 'curated camera point',
          'coordinate_confidence': 'high'},
 '鳶嘴山': {'lat': 24.241111,
         'lon': 120.955028,
         'map_query': '鳶嘴山 山頂',
         'coordinate_source': 'curated summit/camera point',
         'coordinate_confidence': 'high'},
 '王功漁港': {'lat': 23.969796,
          'lon': 120.326592,
          'map_query': '王功漁港 燈塔',
          'coordinate_source': 'curated camera point',
          'coordinate_confidence': 'high'},
 '日月潭': {'lat': 23.85495,
         'lon': 120.90546,
         'scenes': ['lake', 'mountain'],
         'themes': ['sunrise', 'sunset', 'fog_mist', 'reflection', 'cloud_sea', 'milky_way'],
         'map_query': '向山眺望平台 日月潭',
         'coordinate_source': 'curated camera point (Xiangshan lookout)',
         'coordinate_confidence': 'high'},
 '合歡山主峰': {'lat': 24.1426,
           'lon': 121.2712,
           'map_query': '合歡山主峰',
           'coordinate_source': 'national park summit waypoint',
           'coordinate_confidence': 'high',
           'elevation': 3417},
 '金龍山': {'lat': 23.90023,
         'lon': 120.90869,
         'map_query': '金龍山曙光亭',
         'coordinate_source': 'curated camera point',
         'coordinate_confidence': 'high'},
 '武界部落': {'lat': 23.90874,
          'lon': 121.03959,
          'map_query': '武界部落 南投',
          'coordinate_source': 'National Cultural Memory POI',
          'coordinate_confidence': 'medium'},
 '二延平步道': {'lat': 23.422951,
           'lon': 120.651379,
           'scenes': ['mountain', 'rural'],
           'themes': ['mountain_view', 'sunrise', 'sunset', 'cloud_sea'],
           'map_query': '二延平步道 觀景平台',
           'coordinate_source': 'curated camera platform',
           'coordinate_confidence': 'high'},
 '頂石棹': {'lat': 23.474492,
         'lon': 120.701277,
         'scenes': ['mountain', 'forest', 'rural'],
         'themes': ['mountain_view', 'sunrise', 'sunset', 'cloud_sea', 'fog_mist', 'sunbeam'],
         'map_query': '頂石棹觀景臺',
         'coordinate_source': 'viewpoint coordinate',
         'coordinate_confidence': 'high'},
 '阿里山': {'lat': 23.512215,
         'lon': 120.822892,
         'scenes': ['mountain', 'forest'],
         'themes': ['mountain_view', 'sunrise', 'cloud_sea', 'milky_way'],
         'map_query': '祝山觀日平台 阿里山',
         'coordinate_source': 'Zhushan sunrise platform',
         'coordinate_confidence': 'high'},
 '二寮觀日亭': {'lat': 22.9928,
           'lon': 120.40972,
           'name_local': '二寮觀日亭',
           'scenes': ['mountain', 'rural'],
           'themes': ['sunrise', 'cloud_sea', 'mountain_view'],
           'map_query': '二寮觀日亭 台南',
           'coordinate_source': 'viewpoint POI',
           'coordinate_confidence': 'high'},
 '井仔腳鹽田': {'lat': 23.25883,
           'lon': 120.10757,
           'map_query': '井仔腳瓦盤鹽田',
           'coordinate_source': 'curated camera point',
           'coordinate_confidence': 'high'},
 '田寮月世界': {'lat': 22.886,
           'lon': 120.38898,
           'scenes': ['geology'],
           'themes': ['mountain_view', 'sunrise', 'sunset'],
           'map_query': '田寮月世界',
           'coordinate_source': 'curated geology POI',
           'coordinate_confidence': 'high'},
 '駁二藝術特區': {'lat': 22.62033,
            'lon': 120.2817,
            'scenes': ['city', 'architecture', 'coast'],
            'themes': ['blue_hour', 'city_night', 'sunset'],
            'map_query': '駁二藝術特區',
            'coordinate_source': 'POI',
            'coordinate_confidence': 'medium'},
 '墾丁鵝鑾鼻': {'lat': 21.902214,
           'lon': 120.85264,
           'map_query': '鵝鑾鼻燈塔',
           'coordinate_source': 'Taiwan Tourism lighthouse POI',
           'coordinate_confidence': 'high'},
 '屏東關山': {'lat': 21.964933,
          'lon': 120.719517,
          'map_query': '關山夕照 墾丁',
          'coordinate_source': 'curated sunset viewpoint',
          'coordinate_confidence': 'high'},
 '抹茶山': {'lat': 24.8225,
         'lon': 121.735,
         'map_query': '聖母山莊 抹茶山',
         'coordinate_source': 'best-effort camera area',
         'coordinate_confidence': 'medium'},
 '見晴懷古步道': {'lat': 24.505468,
            'lon': 121.525794,
            'map_query': '見晴懷古步道',
            'coordinate_source': 'trail POI',
            'coordinate_confidence': 'medium'},
 '粉鳥林': {'lat': 24.49792,
         'lon': 121.84276,
         'map_query': '粉鳥林漁港 宜蘭',
         'coordinate_source': 'OSM marina POI',
         'coordinate_confidence': 'high'},
 '崇德清水斷崖展望點': {'lat': 24.191966,
               'lon': 121.661332,
               'map_query': '崇德休憩據點 清水斷崖',
               'coordinate_source': 'curated camera point',
               'coordinate_confidence': 'high'},
 '六十石山': {'lat': 23.21907,
          'lon': 121.3176,
          'map_query': '六十石山 金針花',
          'coordinate_source': 'curated camera point',
          'coordinate_confidence': 'high'},
 '七星潭': {'lat': 24.031426,
         'lon': 121.62717,
         'map_query': '七星潭月牙灣',
         'coordinate_source': 'Taiwan tourism / curated camera point',
         'coordinate_confidence': 'high'},
 '多良車站': {'lat': 22.50753,
          'lon': 120.95888,
          'map_query': '多良車站',
          'coordinate_source': 'curated camera point',
          'coordinate_confidence': 'high'},
 '三仙台': {'lat': 23.12331,
         'lon': 121.40826,
         'scenes': ['coast', 'geology', 'architecture'],
         'themes': ['sunrise', 'sunset', 'sky_glow', 'blue_hour', 'long_exposure', 'milky_way'],
         'map_query': '三仙台跨海步橋',
         'coordinate_source': 'curated camera point',
         'coordinate_confidence': 'high'},
 '池上伯朗大道': {'lat': 23.09878,
            'lon': 121.2126,
            'scenes': ['rural', 'mountain'],
            'themes': ['mountain_view', 'sunrise', 'sunset', 'milky_way'],
            'map_query': '伯朗大道 金城武樹',
            'coordinate_source': 'curated camera point',
            'coordinate_confidence': 'high'},
 '玉山主峰': {'lat': 23.470018,
          'lon': 120.95727,
          'map_query': '玉山主峰',
          'coordinate_source': 'national park summit waypoint',
          'coordinate_confidence': 'high',
          'elevation': 3952},
 '雪山主峰': {'lat': 24.383401,
          'lon': 121.231754,
          'map_query': '雪山主峰',
          'coordinate_source': 'OSM summit / baiyue data',
          'coordinate_confidence': 'high',
          'elevation': 3886},
 '雪山北峰': {'lat': 24.415,
          'lon': 121.24,
          'map_query': '雪山北峰',
          'coordinate_source': 'baiyue coordinate',
          'coordinate_confidence': 'high',
          'elevation': 3703},
 '奇萊主峰': {'lat': 24.086,
          'lon': 121.323,
          'map_query': '奇萊主峰',
          'coordinate_source': 'summit coordinate',
          'coordinate_confidence': 'high',
          'elevation': 3560},
 '南湖大山': {'lat': 24.362,
          'lon': 121.439,
          'map_query': '南湖大山',
          'coordinate_source': 'summit coordinate',
          'coordinate_confidence': 'high',
          'elevation': 3742},
 '嘉明湖': {'lat': 23.292921,
         'lon': 121.03451,
         'map_query': '嘉明湖',
         'coordinate_source': 'Taiwan landscape official',
         'coordinate_confidence': 'high',
         'elevation': 3310},
 '大霸尖山': {'lat': 24.458196,
          'lon': 121.258157,
          'map_query': '大霸尖山',
          'coordinate_source': 'Taiwan landscape official',
          'coordinate_confidence': 'high',
          'elevation': 3492},
 '北大武山': {'lat': 22.627,
          'lon': 120.752,
          'map_query': '北大武山 三角點',
          'coordinate_source': 'best-effort summit coordinate',
          'coordinate_confidence': 'medium',
          'elevation': 3092},
 '池有山': {'lat': 24.431129,
         'lon': 121.28816,
         'map_query': '池有山 三角點',
         'coordinate_source': 'Shei-Pa waypoint',
         'coordinate_confidence': 'high',
         'elevation': 3303},
 '桃山': {'lat': 24.4325,
        'lon': 121.305,
        'map_query': '桃山 三角點 武陵四秀',
        'coordinate_source': 'summit coordinate',
        'coordinate_confidence': 'high',
        'elevation': 3325},
 '品田山': {'lat': 24.4282,
         'lon': 121.2668,
         'map_query': '品田山',
         'coordinate_source': 'summit coordinate',
         'coordinate_confidence': 'high',
         'elevation': 3524},
 '大古山': {'lat': 25.10525,
         'lon': 121.290025,
         'map_query': '大古山觀景平台 桃園',
         'coordinate_source': 'viewpoint coordinate',
         'coordinate_confidence': 'high'},
 '小崗山雲臺': {'lat': 22.8229,
           'lon': 120.3497,
           'map_query': '小崗山天空迴廊',
           'coordinate_source': 'best-effort viewpoint',
           'coordinate_confidence': 'medium'},
 '杉林溪': {'lat': 23.632,
         'lon': 120.792,
         'map_query': '松瀧岩瀑布 杉林溪',
         'coordinate_source': 'existing recreation-area coordinate',
         'coordinate_confidence': 'medium'},
 '正濱漁港': {'lat': 25.152506,
          'lon': 121.768994,
          'map_query': '正濱漁港彩色屋',
          'coordinate_source': 'curated camera point',
          'coordinate_confidence': 'high'},
 '五峰旗瀑布': {'lat': 24.833,
           'lon': 121.746,
           'map_query': '五峰旗瀑布 第一層',
           'coordinate_source': 'official landscape/POI',
           'coordinate_confidence': 'high'},
 '松蘿湖': {'lat': 24.69222,
         'lon': 121.53364,
         'map_query': '松蘿湖',
         'coordinate_source': 'OSM waterbody',
         'coordinate_confidence': 'high'},
 '加羅湖': {'lat': 24.5218,
         'lon': 121.4645,
         'map_query': '加羅湖',
         'coordinate_source': 'existing; trail lake',
         'coordinate_confidence': 'medium'},
 '澎湖跨海大橋': {'lat': 23.657823,
            'lon': 119.55453,
            'map_query': '澎湖跨海大橋 西嶼端',
            'coordinate_source': 'Taiwan tourism POI',
            'coordinate_confidence': 'high'},
 '奎壁山': {'lat': 23.59968,
         'lon': 119.67137,
         'map_query': '奎壁山摩西分海',
         'coordinate_source': 'curated sunrise/tidal point',
         'coordinate_confidence': 'high'},
 '七美雙心石滬': {'lat': 23.22022,
            'lon': 119.44697,
            'map_query': '七美雙心石滬',
            'coordinate_source': 'curated camera point',
            'coordinate_confidence': 'high'},
 '澎湖觀音亭': {'lat': 23.568645,
           'lon': 119.56243,
           'map_query': '澎湖觀音亭海濱公園',
           'coordinate_source': 'Taiwan tourism POI',
           'coordinate_confidence': 'high'},
 '金門得月樓': {'lat': 24.40971,
           'lon': 118.29849,
           'map_query': '得月樓 金門',
           'coordinate_source': 'official POI',
           'coordinate_confidence': 'high'},
 '翟山坑道': {'lat': 24.390301,
          'lon': 118.32061,
          'scenes': ['architecture', 'coast'],
          'themes': ['blue_hour', 'city_night', 'long_exposure'],
          'map_query': '翟山坑道',
          'coordinate_source': 'Taiwan Tourism POI',
          'coordinate_confidence': 'high'},
 '金門慈湖': {'lat': 24.46897,
          'lon': 118.30675,
          'map_query': '慈湖 金門',
          'coordinate_source': 'curated camera point',
          'coordinate_confidence': 'high'},
 '馬祖南竿': {'lat': 26.159,
          'lon': 119.949,
          'map_query': '鐵堡 南竿 馬祖',
          'coordinate_source': 'best-effort representative camera POI',
          'coordinate_confidence': 'medium'},
 '東引燈塔': {'lat': 26.36542,
          'lon': 120.51049,
          'map_query': '東湧燈塔 馬祖',
          'coordinate_source': 'curated lighthouse',
          'coordinate_confidence': 'high'},
 '北竿芹壁': {'lat': 26.22478,
          'lon': 119.98366,
          'map_query': '芹壁聚落',
          'coordinate_source': 'curated village point',
          'coordinate_confidence': 'high'},
 '綠島朝日溫泉': {'lat': 22.63703,
            'lon': 121.50418,
            'map_query': '綠島朝日溫泉',
            'coordinate_source': 'Taiwan Tourism POI',
            'coordinate_confidence': 'high'},
 '蘭嶼東清灣': {'lat': 22.05299,
           'lon': 121.56363,
           'map_query': '東清灣 蘭嶼',
           'coordinate_source': 'Taiwan tourism open data',
           'coordinate_confidence': 'high'},
 '蘭嶼青青草原': {'lat': 22.0055,
            'lon': 121.57489,
            'scenes': ['grassland', 'coast'],
            'themes': ['sunrise', 'sunset', 'sky_glow', 'blue_hour', 'milky_way'],
            'map_query': '青青草原 蘭嶼',
            'coordinate_source': 'curated camera point',
            'coordinate_confidence': 'high'},
 '小琉球花瓶岩': {'lat': 22.355647,
            'lon': 120.380753,
            'map_query': '花瓶岩 小琉球',
            'coordinate_source': 'live camera / official area',
            'coordinate_confidence': 'high'},
 '美瑛青池': {'lat': 43.493611,
          'lon': 142.614167,
          'map_query': '白金青い池 北海道',
          'coordinate_source': 'Tokachidake Geopark official',
          'coordinate_confidence': 'high'},
 '旭岳': {'lat': 43.6620489,
        'lon': 142.8250911,
        'scenes': ['mountain', 'snow_ice'],
        'themes': ['mountain_view', 'sunrise', 'sunset', 'milky_way', 'snow_scene'],
        'map_query': '旭岳ロープウェイ 姿見駅',
        'coordinate_source': 'B32 official Sugatami scenic course + mapped Sugatami Station coordinate',
        'coordinate_confidence': 'high',
        'elevation': 1600},
 '釧路濕原': {'lat': 43.0980769,
          'lon': 144.4492556,
          'scenes': ['wetland'],
          'themes': ['sunrise', 'sunset', 'fog_mist', 'reflection'],
          'map_query': '細岡展望台 釧路湿原',
          'coordinate_source': 'B32 Environment Ministry Hosooka sunset viewpoint + MapFan mapped coordinate',
          'coordinate_confidence': 'high'},
 '函館山夜景': {'lat': 41.7594502,
           'lon': 140.7044467,
           'map_query': '函館山展望台',
           'coordinate_source': 'B32 official summit night-view destination + MapFan observatory coordinate',
           'coordinate_confidence': 'high'},
 '小樽運河': {'lat': 43.197887,
          'lon': 141.003034,
          'scenes': ['city', 'river', 'architecture'],
          'themes': ['blue_hour', 'city_night', 'reflection', 'long_exposure'],
          'map_query': '浅草橋街園 小樽運河',
          'coordinate_source': 'B32 official photo-spot identification + NAVITIME mapped POI coordinate',
          'coordinate_confidence': 'high'},
 '摩周湖': {'lat': 43.556947,
         'lon': 144.507319,
         'map_query': '摩周湖第一展望台',
         'coordinate_source': 'first observation deck',
         'coordinate_confidence': 'high'},
 '十和田湖': {'lat': 40.426538,
          'lon': 140.894325,
          'map_query': '十和田湖 休屋',
          'coordinate_source': 'Yasumiya lakeside',
          'coordinate_confidence': 'high'},
 '松島': {'lat': 38.3525784,
        'lon': 141.0623503,
        'scenes': ['coast', 'mountain'],
        'themes': ['sunrise'],
        'map_query': '双観山 松島',
        'coordinate_source': 'B32 Matsushima Town official Sokanzan viewpoint + official linked map coordinate',
        'coordinate_confidence': 'high'},
 '磐梯山': {'lat': 37.6727759,
         'lon': 140.0689901,
         'scenes': ['lake', 'forest', 'mountain'],
         'themes': ['mountain_view'],
         'map_query': '中瀬沼展望台',
         'coordinate_source': 'B32 Fukushima Prefecture View Point 04 official linked map coordinate',
         'coordinate_confidence': 'high'},
 '富士山 (河口湖)': {'lat': 35.5230652,
               'lon': 138.7461483,
               'scenes': ['lake', 'mountain'],
               'themes': ['mountain_view', 'reflection'],
               'map_query': '大石公園 河口湖',
               'coordinate_source': 'B32 Fujikawaguchiko official Oishi Park photo spot + MapFan coordinate',
               'coordinate_confidence': 'high'},
 '東京鐵塔': {'lat': 35.658656,
          'lon': 139.745364,
          'scenes': ['city', 'architecture'],
          'themes': ['mountain_view', 'city_night'],
          'map_query': '東京タワー MAIN DECK',
          'coordinate_source': 'Tokyo Tower official Main Deck identity + existing high-confidence tower POI',
          'coordinate_confidence': 'high',
          'elevation': 150},
 '鎌倉大佛': {'lat': 35.31685,
          'lon': 139.53572,
          'scenes': ['architecture'],
          'themes': ['mountain_view'],
          'map_query': '鎌倉大仏 高徳院',
          'coordinate_source': 'Kotoku-in official subject/access rules + cross-checked Great Buddha artwork coordinate',
          'coordinate_confidence': 'high'},
 '諏訪湖': {'lat': 36.053326,
         'lon': 138.122711,
         'scenes': ['lake', 'city', 'mountain'],
         'themes': ['sunrise', 'sunset', 'fog_mist', 'reflection', 'city_night', 'mountain_view'],
         'map_query': '立石公園 諏訪',
         'coordinate_source': 'Tateishi Park photo point',
         'coordinate_confidence': 'high'},
 '等等力溪谷': {'lat': 35.603738,
           'lon': 139.646533,
           'scenes': ['forest', 'river', 'waterfall'],
           'themes': ['fog_mist', 'sunbeam', 'long_exposure'],
           'map_query': '等々力渓谷 不動の滝',
           'coordinate_source': 'Wikimedia camera point',
           'coordinate_confidence': 'high'},
 '等等力溪谷': {'lat': 35.607857,
           'lon': 139.646545,
           'scenes': ['forest', 'river'],
           'themes': ['mountain_view'],
           'map_query': '等々力渓谷 ゴルフ橋',
           'coordinate_source': 'B32 Setagaya official Golf Bridge / Todoroki Valley research + cross-checked bridge coordinate',
           'coordinate_confidence': 'high'},
 '東京皇居': {'lat': 35.678475,
          'lon': 139.754897,
          'scenes': ['architecture', 'city'],
          'themes': ['mountain_view'],
          'map_query': '皇居外苑 二重橋 皇居前広場',
          'coordinate_source': 'B32 Kokyo Gaien official photo guidance + cross-checked Nijubashi camera location',
          'coordinate_confidence': 'high',
          'name_i18n_override': {
              'zh-TW': '皇居外苑二重橋',
              'en': 'Nijubashi, Kokyo Gaien',
              'ja': '皇居外苑 二重橋'
          },
          'name_local': '二重橋'},
 '橫濱山下公園': {'lat': 35.447738,
            'lon': 139.646791,
            'scenes': ['coast', 'city'],
            'themes': ['mountain_view', 'city_night'],
            'map_query': 'インド水塔 山下公園 横浜',
            'coordinate_source': 'B32 Yokohama official recommended India Water Tower area + cross-checked POI coordinate',
            'coordinate_confidence': 'high'},
 '金澤兼六園': {'lat': 36.563367,
           'lon': 136.662817,
           'scenes': ['forest', 'lake', 'architecture'],
           'themes': ['mountain_view'],
           'map_query': '兼六園 徽軫灯籠',
           'coordinate_source': 'B32 official Kotoji-toro photo-spot guidance + cross-checked Kasumigaike camera location',
           'coordinate_confidence': 'high'},
 '名古屋城': {'lat': 35.185181,
          'lon': 136.89865,
          'scenes': ['architecture', 'city'],
          'themes': ['mountain_view'],
          'map_query': '名古屋城 西之丸 西南隅櫓',
          'coordinate_source': 'B32 Nagoya Castle official photo spot #1 + cross-checked Southwest Corner Watchtower camera location',
          'coordinate_confidence': 'high'},
 '濱名湖': {'lat': 34.688461,
         'lon': 137.603753,
         'scenes': ['lake', 'coast'],
         'themes': ['sunrise', 'sunset', 'sky_glow', 'blue_hour', 'reflection', 'long_exposure'],
         'map_query': '弁天島海浜公園 浜名湖',
         'coordinate_source': 'Bentenjima camera point',
         'coordinate_confidence': 'high'},
 '橫濱港未來21': {'lat': 35.45099,
             'lon': 139.6467,
             'scenes': ['city', 'coast', 'architecture'],
             'themes': ['city_night'],
             'map_query': 'OSANBASHI VIEWPOINT 横浜港大さん橋',
             'coordinate_source': 'Yokohama official Osanbashi rooftop + OSM scenic viewpoint node',
             'coordinate_confidence': 'high'},
 '新穗高高空纜車': {'lat': 36.268335,
             'lon': 137.60158,
             'elevation': 2156,
             'scenes': ['mountain'],
             'themes': ['mountain_view', 'milky_way'],
             'map_query': '西穂高口駅 新穂高ロープウェイ',
             'coordinate_source': 'B32 official Nishi-Hotakaguchi rooftop viewpoint + MapFan station coordinate + geotagged camera cross-check',
             'coordinate_confidence': 'high',
             'name_i18n_override': {'zh-TW': '新穗高・西穗高口展望台',
                                    'en': 'Shinhotaka · Nishi-Hotakaguchi Observatory',
                                    'ja': '新穂高・西穂高口展望台'},
             'name_local': '西穂高口駅展望台'},
 '彌彥山': {'lat': 37.710125,
         'lon': 138.809994,
         'scenes': ['mountain', 'coast', 'city'],
         'themes': ['mountain_view', 'sunset', 'city_night'],
         'map_query': '弥彦山 パノラマタワー',
         'coordinate_source': 'B32 Niigata/Yahiko official summit-park photography evidence + cross-checked Panorama Tower Geo URI',
         'coordinate_confidence': 'high',
         'name_i18n_override': {'zh-TW': '彌彥山頂公園・Panorama Tower',
                                'en': 'Mt. Yahiko Summit Park · Panorama Tower',
                                'ja': '弥彦山頂公園・パノラマタワー'},
         'name_local': '弥彦山頂公園 パノラマタワー'},
 '京都清水寺': {'lat': 34.994444,
           'lon': 135.785556,
           'scenes': ['architecture', 'city', 'mountain'],
           'themes': ['mountain_view'],
           'map_query': '清水寺 奥の院 京都',
           'coordinate_source': 'B32 Kiyomizu-dera official photo opportunity + Kyoto City designated Okuno-in viewpoint',
           'coordinate_confidence': 'high'},
 '大阪城公園': {'lat': 34.6892,
           'lon': 135.52675,
           'scenes': ['architecture', 'city'],
           'themes': ['mountain_view'],
           'map_query': '大阪城 極楽橋',
           'coordinate_source': 'B32 Osaka Castle official Gokurakubashi photo spot + cross-checked camera location',
           'coordinate_confidence': 'high'},
 '萩市城下町': {'lat': 34.4119363,
           'lon': 131.3932271,
           'scenes': ['architecture', 'city'],
           'themes': ['mountain_view', 'city_night'],
           'map_query': '菊屋横町 萩市',
           'coordinate_source': 'B32 Hagi City/JNTO Kikuya Yokocho research + MapFan lane anchor + geotagged camera cross-check',
           'coordinate_confidence': 'high',
           'name_i18n_override': {'zh-TW': '萩城下町・菊屋橫町',
                                  'en': 'Hagi Castle Town · Kikuya Yokocho',
                                  'ja': '萩城下町・菊屋横町'},
           'name_local': '萩城下町 菊屋横町'},
 '出雲大社': {'lat': 35.402083,
          'lon': 132.685556,
          'scenes': ['architecture'],
          'themes': ['mountain_view'],
          'map_query': '出雲大社',
          'coordinate_source': 'legacy shrine-area weather anchor; not a road destination or a tripod point',
          'coordinate_confidence': 'medium'},
 '神戶六甲山': {'lat': 34.752011,
           'lon': 135.237428,
           'scenes': ['mountain', 'city'],
           'themes': ['mountain_view', 'city_night'],
           'map_query': '六甲山 天覧台',
           'coordinate_source': 'B50 Kobe Mt. Rokko official Tenrandai research + existing mapped observation-deck anchor',
           'coordinate_confidence': 'high'},
 '高野山': {'lat': 34.213056,
         'lon': 135.579583,
         'scenes': ['forest', 'architecture'],
         'themes': ['mountain_view'],
         'map_query': '高野山 壇上伽藍',
         'coordinate_source': 'B50 Wakayama/Kongobuji official Danjo Garan research + existing mapped precinct anchor',
         'coordinate_confidence': 'high'},
 '伊賀上野城': {'lat': 34.7702,
           'lon': 136.127174,
           'scenes': ['architecture', 'city'],
           'themes': ['mountain_view'],
           'map_query': '伊賀上野城',
           'coordinate_source': 'B50 Mie Prefecture official castle/park research',
           'coordinate_confidence': 'high'},
 '鳴門海峽漩渦': {'lat': 34.24,
            'lon': 134.651,
            'scenes': ['coast', 'geology'],
            'themes': ['sunrise', 'sunset', 'long_exposure'],
            'map_query': '渦の道 鳴門',
            'coordinate_source': 'best-effort Uzu-no-Michi viewpoint',
            'coordinate_confidence': 'medium'},
 '倉敷美觀地區': {'lat': 34.595688,
            'lon': 133.771619,
            'scenes': ['city', 'architecture', 'river'],
            'themes': ['blue_hour', 'city_night', 'reflection', 'long_exposure'],
            'map_query': '倉敷美観地区 中橋',
            'coordinate_source': 'MapFan district POI',
            'coordinate_confidence': 'high'},
 '福岡城跡': {'lat': 33.5844,
          'lon': 130.3831,
          'scenes': ['architecture', 'city'],
          'themes': ['mountain_view'],
          'map_query': '福岡城跡 下之橋御門',
          'coordinate_source': 'B51 official castle-area research; legacy castle-center anchor retained only as a broad map reference while Tenshudai is closed',
          'coordinate_confidence': 'low'},
 '唐津城': {'lat': 33.453529,
         'lon': 129.97818,
         'scenes': ['architecture', 'city', 'coast'],
         'themes': ['mountain_view'],
         'map_query': '唐津城',
         'coordinate_source': 'B51 Karatsu Tourism Association castle research + existing POI',
         'coordinate_confidence': 'high'},
 '長崎哥拉巴園': {'lat': 32.734389,
            'lon': 129.869083,
            'scenes': ['architecture', 'city', 'coast'],
            'themes': ['mountain_view', 'city_night'],
            'map_query': 'グラバー園 長崎',
            'coordinate_source': 'B51 Glover Garden official research + existing POI',
            'coordinate_confidence': 'high'},
 '福岡塔': {'lat': 33.593274,
         'lon': 130.351467,
         'scenes': ['architecture', 'city', 'coast'],
         'themes': ['mountain_view', 'sunset', 'city_night'],
         'map_query': '福岡タワー',
         'coordinate_source': 'B51 Fukuoka Tower official research + existing POI',
         'coordinate_confidence': 'high'},
 '大峽谷國家公園': {'lat': 36.0616,
             'lon': -112.108,
             'map_query': 'Mather Point Grand Canyon',
             'coordinate_source': 'USGS GNIS Mather Point 36.0616,-112.1080 (CL-DATA-17 2026-11-06 re-verified; elevation 2,170 m per GNIS/USGS)',
             'coordinate_confidence': 'high'},
 '馬蹄灣': {'lat': 36.879,
         'lon': -111.51,
         'map_query': 'Horseshoe Bend Overlook',
         'coordinate_source': 'existing viewpoint coordinate',
         'coordinate_confidence': 'high'},
 '羚羊峽谷': {'lat': 36.8619,
          'lon': -111.3743,
          'scenes': ['geology'],
          'themes': ['mountain_view', 'sunbeam'],
          'map_query': 'Upper Antelope Canyon',
          'coordinate_source': 'canyon POI',
          'coordinate_confidence': 'medium'},
 '紀念碑谷': {'lat': 36.982436,
          'lon': -110.112158,
          'scenes': ['geology', 'desert'],
          'themes': ['mountain_view', 'sunrise', 'sunset', 'milky_way'],
          'map_query': 'The View Hotel Monument Valley',
          'coordinate_source': 'The View official GPS',
          'coordinate_confidence': 'high'},
 '拱門國家公園': {'lat': 38.74402,
            'lon': -109.49973,
            'scenes': ['geology', 'desert'],
            'themes': ['mountain_view', 'sunrise', 'sunset', 'milky_way'],
            'map_query': 'Delicate Arch',
            'coordinate_source': 'NPS Delicate Arch coordinate',
            'coordinate_confidence': 'high'},
 '布萊斯峽谷國家公園': {'lat': 37.628216,
               'lon': -112.163029,
               'scenes': ['geology', 'mountain'],
               'themes': ['mountain_view', 'sunrise', 'sunset', 'milky_way'],
               'map_query': 'Sunrise Point Bryce Canyon',
               'coordinate_source': 'USGS/Peakbagger camera point',
               'coordinate_confidence': 'high'},
 '錫安國家公園': {'lat': 37.2133,
            'lon': -112.9401,
            'scenes': ['geology', 'mountain'],
            'themes': ['mountain_view', 'sunrise', 'sunset'],
            'map_query': 'Canyon Overlook Zion National Park',
            'coordinate_source': 'Canyon Overlook camera area',
            'coordinate_confidence': 'medium'},
 '優勝美地半圓頂': {'lat': 37.7434,
             'lon': -119.5897,
             'scenes': ['mountain', 'forest'],
             'themes': ['mountain_view', 'sunrise', 'sunset', 'milky_way'],
             'map_query': 'Sentinel Bridge Yosemite',
             'coordinate_source': 'Sentinel Bridge OSM 37.7434,-119.5897 (CL-DATA-17 2026-11-06 re-verified; replaced Glacier Point / Half Dome viewpoint; elevation 1,208 m per OSM 3,963 ft)',
             'coordinate_confidence': 'high'},
 '優勝美地隧道觀景臺': {'lat': 37.715553,
               'lon': -119.676861,
               'map_query': 'Tunnel View Yosemite',
               'coordinate_source': 'Wikidata viewpoint',
               'coordinate_confidence': 'high'},
 '黃石國家公園 大稜鏡溫泉': {'lat': 44.523693,
                  'lon': -110.839979,
                  'scenes': ['geology', 'lake'],
                  'themes': ['mountain_view', 'fog_mist', 'reflection'],
                  'map_query': 'Grand Prismatic Spring Overlook',
                  'coordinate_source': '2026 Wikimedia camera point',
                  'coordinate_confidence': 'high'},
 '大提頓國家公園': {'lat': 43.8662,
             'lon': -110.5472,
             'scenes': ['mountain', 'river'],
             'themes': ['mountain_view', 'sunrise', 'sunset', 'reflection', 'fog_mist', 'milky_way'],
             'map_query': 'Oxbow Bend Grand Teton',
             'coordinate_source': 'Oxbow Bend overlook 43.8662,-110.5472 (CL-DATA-17 2026-11-06 re-verified; replaced Schwabacher Landing coordinate)',
             'coordinate_confidence': 'high'},
 '雷尼爾山國家公園': {'lat': 46.769167,
              'lon': -121.723889,
              'scenes': ['mountain', 'lake', 'forest', 'snow_ice'],
              'themes': ['mountain_view', 'sunrise', 'sunset', 'reflection', 'fog_mist', 'milky_way', 'snow_scene'],
              'map_query': 'Reflection Lakes Mount Rainier',
              'coordinate_source': 'Reflection Lakes waypoint',
              'coordinate_confidence': 'high'},
 '火山口湖國家公園': {'lat': 42.911253,
              'lon': -122.146719,
              'map_query': 'Rim Village Crater Lake',
              'coordinate_source': 'Rim Village camera point',
              'coordinate_confidence': 'high'},
 '死亡谷國家公園': {'lat': 36.42002,
             'lon': -116.8122,
             'scenes': ['desert', 'geology'],
             'themes': ['mountain_view', 'sunrise', 'sunset', 'milky_way'],
             'map_query': 'Zabriskie Point Death Valley',
             'coordinate_source': 'Zabriskie Point POI',
             'coordinate_confidence': 'high'},
 '舊金山金門大橋': {'lat': 37.82802,
             'lon': -122.48187,
             'map_query': 'Battery Spencer Golden Gate Bridge',
             'coordinate_source': 'classic bridge viewpoint',
             'coordinate_confidence': 'high'},
 '聖海倫斯火山': {'lat': 46.2753,
            'lon': -122.2174,
            'map_query': 'Johnston Ridge Observatory Mount St Helens',
            'coordinate_source': 'classic volcano viewpoint',
            'coordinate_confidence': 'medium'},
 '冰川國家公園': {'lat': 48.527,
            'lon': -113.997,
            'scenes': ['mountain', 'lake', 'forest', 'snow_ice'],
            'themes': ['mountain_view', 'sunrise', 'sunset', 'reflection', 'milky_way', 'snow_scene'],
            'map_query': 'Lake McDonald Apgar Glacier National Park',
            'coordinate_source': 'Lake McDonald camera area',
            'coordinate_confidence': 'medium'},
 '奧林匹克國家公園': {'lat': 47.710912,
              'lon': -124.415477,
              'scenes': ['coast', 'forest', 'geology'],
              'themes': ['sunset', 'sky_glow', 'blue_hour', 'long_exposure', 'fog_mist'],
              'map_query': 'Ruby Beach Olympic National Park',
              'coordinate_source': 'NGA Ruby Beach coordinate',
              'coordinate_confidence': 'high'},
 '紅木國家公園': {'lat': 41.30408,
            'lon': -124.018237,
            'scenes': ['forest'],
            'themes': ['fog_mist', 'sunbeam'],
            'map_query': 'Lady Bird Johnson Grove',
            'coordinate_source': 'NPS event location',
            'coordinate_confidence': 'high'},
 '峽谷地國家公園 梅薩拱門': {'lat': 38.388869,
                  'lon': -109.866796,
                  'scenes': ['geology', 'desert'],
                  'themes': ['sunrise', 'mountain_view', 'milky_way'],
                  'map_query': 'Mesa Arch Canyonlands',
                  'coordinate_source': 'Wikimedia sunrise camera point',
                  'coordinate_confidence': 'high'},
 '約書亞樹國家公園': {'lat': 33.926463,
              'lon': -116.187726,
              'scenes': ['desert', 'mountain'],
              'themes': ['mountain_view', 'sunset', 'milky_way'],
              'map_query': 'Keys View Joshua Tree',
              'coordinate_source': 'Wikimedia Keys View camera point',
              'coordinate_confidence': 'high'},
 '巨人柱國家公園': {'lat': 32.292297,
             'lon': -111.207879,
             'scenes': ['desert', 'mountain'],
             'themes': ['mountain_view', 'sunset', 'milky_way'],
             'map_query': 'Signal Hill Saguaro National Park',
             'coordinate_source': 'Signal Hill coordinate',
             'coordinate_confidence': 'high'},
 '鋸齒山脈': {'lat': 44.142,
          'lon': -114.923,
          'scenes': ['mountain', 'lake'],
          'themes': ['mountain_view', 'sunrise', 'sunset', 'reflection', 'milky_way'],
          'map_query': 'Redfish Lake Sawtooth',
          'coordinate_source': 'representative lake viewpoint',
          'coordinate_confidence': 'medium'},
 '芝加哥天際線': {'lat': 41.86636,
            'lon': -87.60663,
            'scenes': ['city', 'lake'],
            'themes': ['sunrise', 'sunset', 'blue_hour', 'city_night', 'reflection'],
            'map_query': 'Adler Planetarium Skyline Walk Chicago',
            'coordinate_source': 'Adler lakefront skyline camera area',
            'coordinate_confidence': 'high'},
 '落磯山國家公園': {'lat': 40.31324,
             'lon': -105.648222,
             'scenes': ['mountain', 'lake', 'forest'],
             'themes': ['mountain_view', 'sunrise', 'sunset', 'reflection', 'milky_way'],
             'map_query': 'Bear Lake Rocky Mountain National Park',
             'coordinate_source': 'Bear Lake camera point',
             'coordinate_confidence': 'high'},
 '丹佛天際線': {'lat': 39.7475,
           'lon': -104.9507,
           'map_query': 'City Park Pavilion Denver Skyline',
           'coordinate_source': 'representative skyline point',
           'coordinate_confidence': 'medium'},
 '紐約曼哈頓天際線': {'lat': 40.70438,
              'lon': -73.99059,
              'scenes': ['city', 'coast'],
              'themes': ['sunrise', 'sunset', 'blue_hour', 'city_night', 'reflection'],
              'map_query': 'Pebble Beach Brooklyn Bridge Park',
              'coordinate_source': 'Brooklyn skyline camera point',
              'coordinate_confidence': 'high'},
 '大霧山國家公園': {'lat': 35.5629,
             'lon': -83.4985,
             'map_query': 'Kuwohi Clingmans Dome',
             'coordinate_source': 'summit observation camera point',
             'coordinate_confidence': 'medium'},
 '波士頓天際線': {'lat': 42.35466,
            'lon': -71.04675,
            'map_query': 'Fan Pier Park Boston Skyline',
            'coordinate_source': 'Fan Pier camera point',
            'coordinate_confidence': 'high'},
 '馬塔努斯卡冰河': {'lat': 61.653,
             'lon': -148.597,
             'scenes': ['snow_ice', 'mountain'],
             'themes': ['mountain_view', 'snow_scene', 'aurora'],
             'map_query': 'Matanuska Glacier',
             'coordinate_source': 'existing glacier area',
             'coordinate_confidence': 'medium'},
 '塔爾基特納': {'lat': 62.323,
           'lon': -150.107,
           'scenes': ['mountain', 'rural'],
           'themes': ['mountain_view', 'sunrise', 'sunset', 'aurora'],
           'map_query': 'Talkeetna Alaska',
           'coordinate_source': 'town/Denali-view area',
           'coordinate_confidence': 'medium'},
 '育空河': {'lat': 64.739,
         'lon': -156.899,
         'scenes': ['river'],
         'themes': ['fog_mist', 'long_exposure', 'aurora'],
         'map_query': 'Yukon River Alaska',
         'coordinate_source': 'existing regional coordinate',
         'coordinate_confidence': 'low'},
 '諾阿塔克河': {'lat': 68.509,
           'lon': -161.018,
           'scenes': ['river'],
           'themes': ['fog_mist', 'long_exposure', 'aurora'],
           'map_query': 'Noatak River Alaska',
           'coordinate_source': 'existing regional coordinate',
           'coordinate_confidence': 'low'},
 '克拉克湖國家公園': {'lat': 59.105,
              'lon': -157.55,
              'scenes': ['lake', 'mountain'],
              'themes': ['mountain_view', 'reflection', 'sunrise', 'sunset', 'aurora'],
              'map_query': 'Lake Clark National Park',
              'coordinate_source': 'existing regional coordinate',
              'coordinate_confidence': 'low'}}


# Additional high-confidence US POI/viewpoint corrections added in V5.2.
SPOT_OVERRIDES.update({
    "約書亞樹國家公園": {"lat": 33.8270493, "lon": -115.8600998, "map_query": "Cholla Cactus Garden Joshua Tree National Park", "coordinate_source": "NPS Cholla Cactus Garden photo/location metadata", "coordinate_confidence": "high"},
    "巨人柱國家公園": {"lat": 32.183867, "lon": -110.710873, "map_query": "Cactus Forest Loop Drive sunset pull-off Saguaro National Park", "coordinate_source": "NPS exact Scenic View/Photo Spot coordinate", "coordinate_confidence": "high"},
    "拉斯維加斯大道": {"lat": 36.113264, "lon": -115.176372, "map_query": "Bellagio Las Vegas Strip", "coordinate_source": "Wikimedia camera/object location", "coordinate_confidence": "high"},
    "西雅圖太空針塔": {"lat": 47.620510, "lon": -122.349300, "map_query": "Space Needle Seattle", "coordinate_source": "OSM/Mapcarta POI", "coordinate_confidence": "high"},
    "聖莫尼卡碼頭": {"lat": 34.008611, "lon": -118.498611, "map_query": "Santa Monica Pier", "coordinate_source": "Wikidata POI", "coordinate_confidence": "high"},
    "西雅圖派克市場": {"lat": 47.609570, "lon": -122.342010, "map_query": "Pike Place Market Seattle", "coordinate_source": "OSM/Mapcarta POI cross-checked to official Pike Place Market district", "coordinate_confidence": "high"},
    "鋸齒山脈": {"lat": 44.138889, "lon": -114.924444, "map_query": "North Shore Picnic Area Redfish Lake", "coordinate_source": "North Shore Picnic Area cross-mapped to Recreation.gov/USFS Redfish Lake site", "coordinate_confidence": "medium_high"},
    "洛杉磯格里斐斯天文台": {"lat": 34.118210, "lon": -118.300370, "map_query": "Griffith Observatory Los Angeles", "coordinate_source": "OSM/Mapcarta POI", "coordinate_confidence": "high"},
    "白沙國家公園": {"lat": 32.811370, "lon": -106.265010, "map_query": "White Sands Sunset Stroll Parking Area", "coordinate_source": "NPS 2026 Sunset Stroll exact event coordinate", "coordinate_confidence": "high"},
    "芝加哥天際線": {"lat": 41.866360, "lon": -87.606630, "map_query": "Adler Planetarium Chicago skyline view", "coordinate_source": "Choose Chicago official skyline camera-area evidence + OSM/Mapcarta Adler POI", "coordinate_confidence": "high"},
    "落磯山國家公園": {"lat": 40.320586, "lon": -105.604813, "map_query": "Sprague Lake Rocky Mountain National Park", "coordinate_source": "NPS Sprague Lake exact event/location coordinate + Scenic View/Photo Spot evidence", "coordinate_confidence": "high"},
    "丹佛天際線": {"lat": 39.7461222, "lon": -104.9490116, "map_query": "Ferril Lake City Park Denver skyline", "coordinate_source": "Visit Denver City Park skyline subject + USGS/GeoNames Ferril Lake anchor", "coordinate_confidence": "medium_high"},
    "紐奧良法國區": {"lat": 29.958611, "lon": -90.065000, "map_query": "French Quarter New Orleans", "coordinate_source": "Wikidata/Wikipedia district center", "coordinate_confidence": "high"},
    "聖路易斯大拱門": {"lat": 38.624600, "lon": -90.185000, "map_query": "Gateway Arch St Louis", "coordinate_source": "official geographic POI", "coordinate_confidence": "high"},
    "沃斯堡牲畜市場": {"lat": 32.789330, "lon": -97.346720, "map_query": "Livestock Exchange Building Fort Worth Stockyards", "coordinate_source": "Fort Worth Stockyards official 131 East Exchange address + OSM/Mapcarta building POI", "coordinate_confidence": "high"},
    "紐約曼哈頓天際線": {"lat": 40.746370, "lon": -73.957750, "map_query": "Gantry Plaza State Park Manhattan skyline", "coordinate_source": "New York State Parks official skyline subject + OSM/GeoNames Gantry Plaza anchor", "coordinate_confidence": "high"},
    "大霧山國家公園": {"lat": 35.611092, "lon": -83.425007, "map_query": "Newfound Gap Overlook Great Smoky Mountains", "coordinate_source": "NPS Newfound Gap Scenic View/Photo Spot + published overlook coordinate", "coordinate_confidence": "high"},
    "波士頓天際線": {"lat": 42.364590, "lon": -71.037200, "map_query": "Piers Park East Boston skyline", "coordinate_source": "Massport official Piers Park skyline evidence + OSM park anchor", "coordinate_confidence": "high"},
    "尼加拉瀑布": {"lat": 43.080080, "lon": -79.074430, "map_query": "Terrapin Point Niagara Falls State Park", "coordinate_source": "Niagara Falls State Park official Terrapin Point overlook evidence + OSM/GeoNames viewpoint anchor", "coordinate_confidence": "high"},
    "邁阿密海灘": {"lat": 25.765840, "lon": -80.134020, "map_query": "South Pointe Park Miami Beach", "coordinate_source": "City of Miami Beach South Pointe Park identity + official destination photo subject + OSM park anchor", "coordinate_confidence": "high"},
    "迪納利國家公園": {"lat": 63.732090, "lon": -148.902730, "map_query": "Mountain Vista Denali National Park", "coordinate_source": "NPS Mountain Vista Scenic View/Photo Spot + NPS published event/location coordinate", "coordinate_confidence": "medium_high"},
    "費爾班克斯極光": {"lat": 64.864170, "lon": -147.737780, "map_query": "Creamer's Field Fairbanks Alaska", "coordinate_source": "Explore Fairbanks official aurora-location evidence + Alaska ADF&G refuge identity + NRHP/USGS area coordinate", "coordinate_confidence": "high"},
    "珍娜溫泉": {"lat": 65.053040, "lon": -146.055600, "map_query": "Chena Hot Springs Resort", "coordinate_source": "Alaska DEC", "coordinate_confidence": "high"},
    "安克拉治": {"lat": 61.204200, "lon": -150.018710, "map_query": "Point Woronzof Anchorage", "coordinate_source": "Visit Anchorage official sunset/aurora subject + USGS/GeoNames point anchor", "coordinate_confidence": "high"},
    "蘇華德": {"lat": 60.103141, "lon": -149.434574, "map_query": "Seward Waterfront Park Alaska", "coordinate_source": "Visit Seward official waterfront subject + City of Seward published facility coordinate", "coordinate_confidence": "high"},
    "哈徹山口": {"lat": 61.766100, "lon": -149.321370, "map_query": "Summit Lake Hatcher Pass Alaska", "coordinate_source": "Alaska State Parks Summit Lake photography subject + GeoNames/OSM lake cross-check", "coordinate_confidence": "medium_high"},
    "馬塔努斯卡冰河": {"lat": 61.7994722, "lon": -147.8180444, "map_query": "Matanuska Glacier State Recreation Site", "coordinate_source": "Alaska DNR published recreation-site GPS and public glacier-viewing evidence", "coordinate_confidence": "high"},
    "波蒂奇冰河": {"lat": 60.784520, "lon": -148.842000, "map_query": "Begich Boggs Visitor Center Portage", "coordinate_source": "USFS/Travel Alaska Portage Valley subject + existing Begich Boggs anchor", "coordinate_confidence": "high"},
    "瓦爾迪茲": {"lat": 61.127260, "lon": -146.338080, "map_query": "Dock Point Trail Valdez", "coordinate_source": "City of Valdez official Dock Point photo/harbor-view subject + OSM trail cross-check", "coordinate_confidence": "medium_high"},
    "朱諾": {"lat": 58.299130, "lon": -134.406170, "map_query": "Marine Park Juneau Alaska", "coordinate_source": "Travel Juneau downtown waterfront subject + OSM Marine Park cross-check", "coordinate_confidence": "medium_high"},
    "門登霍爾冰河": {"lat": 58.417180, "lon": -134.545560, "map_query": "Mendenhall Glacier Visitor Center", "coordinate_source": "OSM/Mapcarta visitor center", "coordinate_confidence": "high"},
    "荷馬沙嘴": {"lat": 59.620000, "lon": -151.454720, "map_query": "Homer Spit Alaska", "coordinate_source": "Travel Alaska official Spit subject + Wikidata/GeoNames landform anchor", "coordinate_confidence": "medium_high"},
    "凱奇侃": {"lat": 55.343000, "lon": -131.647000, "map_query": "Historic Creek Street Ketchikan", "coordinate_source": "Ketchikan Visitors Bureau official Creek Street subject + existing downtown anchor", "coordinate_confidence": "medium_high"},
    "史卡威": {"lat": 59.458000, "lon": -135.314000, "map_query": "Arctic Brotherhood Hall 205 Broadway Skagway", "coordinate_source": "Municipality of Skagway official visitor-center photo subject/address + existing downtown anchor", "coordinate_confidence": "medium_high"},
    "威朗格利-聖埃利亞斯國家公園": {"lat": 61.481048, "lon": -142.885231, "map_query": "Kennecott Mines National Historic Landmark Alaska", "coordinate_source": "NPS exact Kennecott Mines Scenic View/Photo Spot coordinate", "coordinate_confidence": "high"},
    "布魯克斯山脈": {"lat": 68.133000, "lon": -149.480000, "map_query": "Atigun Pass Dalton Highway Alaska", "coordinate_source": "BLM official Atigun Pass subject + existing mapped pass anchor", "coordinate_confidence": "medium_high"},
    "北極圈地標": {"lat": 66.556010, "lon": -150.810700, "map_query": "Arctic Circle Wayside Dalton Highway", "coordinate_source": "BLM official Arctic Circle Wayside + Travel Alaska official sign photo-op + cross-mapped sign coordinate", "coordinate_confidence": "high"},
    "諾姆": {"lat": 64.501000, "lon": -165.406000, "map_query": "Middle Beach Front Street Nome Alaska", "coordinate_source": "Travel Alaska official Middle Beach / Nome coastal subject + existing downtown anchor", "coordinate_confidence": "medium_high"},
    "卡特邁國家公園": {"lat": 58.554760, "lon": -155.791930, "map_query": "Brooks Falls Platform Katmai", "coordinate_source": "NPS official Brooks Falls Scenic View/Photo Spot + OSM/Mapcarta platform cross-check", "coordinate_confidence": "medium_high"},
    "冰河灣國家公園": {"lat": 58.455543092, "lon": -135.886147445, "map_query": "Bartlett Cove Public Use Dock Glacier Bay", "coordinate_source": "NPS exact Bartlett Cove Public Use Dock Scenic View/Photo Spot coordinate", "coordinate_confidence": "high"},
    "柯迪亞克島": {"lat": 57.827590, "lon": -152.356640, "map_query": "Fort Abercrombie State Historical Park Kodiak", "coordinate_source": "Alaska State Parks official facility GPS + scenic coastal/history subject", "coordinate_confidence": "high"},
    "埃克盧特納湖": {"lat": 61.409750, "lon": -149.134550, "map_query": "Eklutna Lakeside Trail Alaska", "coordinate_source": "Alaska State Parks official photography subject + OSM/Mapcarta Lakeside Trailhead cross-check", "coordinate_confidence": "medium_high"},
    "塔爾基特納": {"lat": 62.322846, "lon": -150.121177, "map_query": "Talkeetna Riverfront Park Alaska", "coordinate_source": "Travel Alaska official Denali/Susitna view subject + Alaska.org/OSM riverfront cross-check", "coordinate_confidence": "medium_high"},
    "艾利耶斯卡": {"lat": 60.961540, "lon": -149.079370, "map_query": "Alyeska Mountain Station Aerial Tram", "coordinate_source": "Alyeska Resort official Mountain Station panorama subject + OSM/Mapcarta upper tram cross-check", "coordinate_confidence": "medium_high"},
    "楚加奇州立公園": {"lat": 61.104890, "lon": -149.684610, "map_query": "Glen Alps Overlook Chugach State Park", "coordinate_source": "Alaska State Parks official Glen Alps/Anchorage Overlook subject + OSM/Mapcarta viewpoint cross-check", "coordinate_confidence": "medium_high"},
    "白令陸橋國家保護區": {"lat": 65.856900, "lon": -164.714200, "map_query": "Serpentine Hot Springs Bering Land Bridge", "coordinate_source": "NPS exact Serpentine Hot Springs coordinate", "coordinate_confidence": "high"},
    "育空河": {"lat": 65.876650, "lon": -149.721000, "map_query": "Yukon Crossing Visitor Contact Station Dalton Highway", "coordinate_source": "BLM official Yukon Crossing river-view subject + Alaska.org coordinate cross-check", "coordinate_confidence": "medium_high"},
    "諾阿塔克河": {"lat": 68.1814422607422, "lon": -159.394500732422, "map_query": "Noatak River Noatak National Preserve", "coordinate_source": "NPS Gallery audited Noatak River asset location", "coordinate_confidence": "high"},
    "克拉克湖國家公園": {"lat": 60.1973667, "lon": -154.3226167, "map_query": "Port Alsworth Lake Clark", "coordinate_source": "NPS published Port Alsworth coordinate + Lake Clark/aurora subject evidence", "coordinate_confidence": "high"},
    "獨立礦山": {"lat": 61.790493, "lon": -149.283392, "map_query": "Independence Mine State Historical Park", "coordinate_source": "Alaska State Parks official Mile 17.3 subject/access + existing cross-mapped park anchor", "coordinate_confidence": "medium_high"},
 '八里崁頭里・淡水大橋觀景點': {'lat': 25.140639,
                  'lon': 121.420333,
                  'scenes': ['coast', 'city'],
                  'themes': ['fog_mist', 'cloud_sea', 'mountain_view', 'sunset'],
                  'map_query': '八里崁頭里 淡水大橋觀景點 新北市八里區',
                  'coordinate_source': 'owner-provided Google Maps link resolved @25.140639,121.420333 (2026-11-02); viewpoint bearing and practical arrival not independently verified',
                  'coordinate_confidence': 'medium'},
})


# V5.2 location/content corrections. These coordinates are Place / Camera-Zone
# anchors. R4.2 no longer assumes they are road-navigation destinations.
# Navigation is modeled separately by NAVIGATION_TARGET_OVERRIDES below.
# Taiwan corrections are based on the curated camera-position audit used by
# ChaseLights plus official/photo-point references where available.

# More precise display labels for broad-area entries whose navigation coordinate
# is now an actual shooting position. spot_id remains stable because the source
# tuple order is unchanged.
DISPLAY_NAME_OVERRIDES = {
    "外澳沙灘": {"zh-TW": "外澳沙灘／龜山朝日", "en": "Waiao Beach · Gueishan Sunrise", "ja": "外澳ビーチ・亀山島朝日", "local": "外澳沙灘"},
    "龍磐公園": {"zh-TW": "龍磐公園／草原海岸", "en": "Longpan Park · Grassland Coast", "ja": "龍磐公園・草原海岸", "local": "龍磐公園"},
    "石梯坪": {"zh-TW": "石梯坪海蝕平台／壺穴群", "en": "Shihtiping Marine Terraces · Potholes", "ja": "石梯坪・海食台と甌穴群", "local": "石梯坪"},
    "建功嶼": {"zh-TW": "建功嶼／退潮石板道", "en": "Jiangong Islet · Tidal Causeway", "ja": "建功嶼・干潮石畳道", "local": "建功嶼"},
    "池西岩瀑": {"zh-TW": "池西柱狀玄武岩／池西岩瀑九孔池", "en": "Chixi Columnar Basalt · Tidal Pools", "ja": "池西柱状玄武岩・九孔池", "local": "池西岩瀑"},
    "帆船鼻大草原": {"zh-TW": "帆船鼻大草原／海岬", "en": "Fanchuanbi Grassland · Headland", "ja": "帆船鼻大草原・海岬", "local": "帆船鼻大草原"},
    "南竿鐵堡": {"zh-TW": "南竿鐵堡／海防礁岩", "en": "Iron Fort · Coastal Stronghold", "ja": "南竿鉄堡・海防岩礁", "local": "鐵堡"},
    "九份不厭亭": {"zh-TW": "不厭亭", "en": "Buyan Pavilion Viewpoint", "ja": "不厭亭展望所", "local": "不厭亭"},
    "日月潭": {"zh-TW": "日月潭・水社壩湖景步道", "en": "Sun Moon Lake · Shuishe Dam Viewpoint", "ja": "日月潭・水社ダム湖畔", "local": "日月潭 水社壩"},
    "二延平步道": {"zh-TW": "二延平步道鋼構觀景平台", "en": "Eryanping Trail Viewing Platform", "ja": "二延平歩道展望台", "local": "二延平步道觀景平台"},
    "阿里山": {"zh-TW": "阿里山祝山觀日平台", "en": "Alishan Zhushan Sunrise Platform", "ja": "阿里山祝山観日平台", "local": "祝山觀日平台"},
    "七星潭": {"zh-TW": "七星潭月牙灣", "en": "Qixingtan Crescent Bay", "ja": "七星潭月牙湾", "local": "七星潭月牙灣"},
    "香山濕地": {"zh-TW": "香山濕地賞蟹步道", "en": "Xiangshan Wetland Crab Boardwalk", "ja": "香山湿地カニ観察歩道", "local": "香山濕地賞蟹步道"},
    "井仔腳鹽田": {"zh-TW": "井仔腳瓦盤鹽田", "en": "Jingzijiao Tile-paved Salt Fields", "ja": "井仔脚瓦盤塩田", "local": "井仔腳瓦盤鹽田"},
    "墾丁鵝鑾鼻": {"zh-TW": "鵝鑾鼻燈塔", "en": "Eluanbi Lighthouse", "ja": "鵝鑾鼻灯台", "local": "鵝鑾鼻燈塔"},
    "多良車站": {"zh-TW": "多良火車站觀景台", "en": "Duoliang Station Viewpoint", "ja": "多良駅展望台", "local": "多良火車站"},
}

# R4.2 Navigation Target contract.
#
# Camera Zone / Place anchor and practical arrival point are intentionally
# separate. map_query is search/display metadata only and MUST NOT be used to
# build a production Navigation URL.
NAVIGATION_TARGET_OVERRIDES = {
    "南子吝步道": {
        "status": "verified",
        "lat": 25.1201398,
        "lon": 121.887539,
        "target_type": "trailhead",
        "label_i18n": {
            "zh-TW": "南子吝步道官方到達點",
            "en": "Nanzilin Trail official arrival point",
            "ja": "南子吝歩道 公式到着地点",
        },
        "source": "New Taipei City Travel official How to Get There Google Maps destination (25.1201398, 121.887539); reviewed 2026-10-03",
        "confidence": "high",
        "note_i18n": {
            "zh-TW": "此點是官方旅遊頁提供的實際到達／步道入口導航點，不是山稜 Camera Zone；攝影機位仍沿合法步道與觀景平台選擇。",
            "en": "This is the official tourism arrival/trail-access destination, not the ridge Camera Zone. Photography positions remain along the legal trail and viewing platform.",
            "ja": "公式観光ページの到着・登山口ナビ地点であり、稜線のCamera Zoneではありません。撮影位置は合法な歩道・展望台内で選びます。",
        },
    },
    "高千穗峽": {
        "status": "multiple_access_routes",
        "target_type": "camera_zone_or_place_anchor",
        "label_i18n": {
            "zh-TW": "高千穗峽有多個停車／步行／租船進入方式",
            "en": "Takachiho Gorge has multiple parking, walking and boat access routes",
            "ja": "高千穂峡は駐車・徒歩・貸しボートで複数のアクセス経路があります",
        },
        "source": "Takachiho Tourism Association documents multiple official parking/access options and separately managed rental-boat access; #1 Oshioi public parking is independently mapped at 32.7016613, 131.3003766; reviewed 2026-10-03",
        "confidence": "high",
        "note_i18n": {
            "zh-TW": "真名井瀑布步道、三橋攝影點與租船視角的實際到達方式不同；第1御塩井停車場只作 Place／天氣 anchor，在 route-selection 資料完成前不指定單一 Directions 終點。",
            "en": "Manai Falls walking access, the Three Bridges photo point and the rental-boat perspective use different arrival modes. #1 Oshioi Parking is only the Place/weather anchor; no single Directions target is chosen until route selection is modeled.",
            "ja": "真名井の滝の遊歩道、三橋撮影点、貸しボートでは到着方法が異なります。第1御塩井駐車場はPlace／天気アンカーのみとし、ルート選択モデル完成前は単一のDirections目的地を指定しません。",
        },
    },
    "馬塔努斯卡冰河": {
        "status": "verified",
        "lat": 61.7994722,
        "lon": -147.8180444,
        "target_type": "entrance",
        "label_i18n": {
            "zh-TW": "Matanuska Glacier State Recreation Site",
            "en": "Matanuska Glacier State Recreation Site",
            "ja": "マタヌスカ氷河州立レクリエーションサイト",
        },
        "source": "Alaska DNR published Matanuska Glacier recreation-site GPS; reviewed 2026-09-27",
        "confidence": "high",
        "note_i18n": {
            "zh-TW": "導航終點為Mile 101公共State Recreation Site，不是私人冰河入口；此處提供冰河展望但不能直接進入冰河。",
            "en": "Directions use the public Mile 101 State Recreation Site, not the private glacier entrance. This area provides glacier views but no direct glacier access.",
            "ja": "ナビはMile 101の公共State Recreation Siteを使用し、私有の氷河入口ではありません。ここは氷河展望地ですが氷河へ直接入る場所ではありません。",
        },
    },
    "哈徹山口": {
        "status": "verified",
        "lat": 61.767130,
        "lon": -149.323040,
        "target_type": "parking",
        "label_i18n": {
            "zh-TW": "Hatcher Pass・Summit Lake Parking",
            "en": "Hatcher Pass · Summit Lake Parking",
            "ja": "ハッチャー・パス・Summit Lake Parking",
        },
        "source": "Alaska State Parks Summit Lake site + OSM parking cross-check; reviewed 2026-09-27",
        "confidence": "medium",
        "note_i18n": {
            "zh-TW": "此導航點僅代表Summit Lake夏季Camera Zone的停車到達點；冬季極光題材不得使用此點推定summit road可通行，須依當下道路／冬季公共停車狀態。",
            "en": "This navigation point is only the summer Summit Lake Camera-Zone arrival. Do not use it to imply winter summit-road access for aurora photography; current road and winter public-parking status must be checked.",
            "ja": "このナビ地点は夏季Summit Lake Camera Zoneの到着点のみです。冬季オーロラ撮影でサミット道路が通行可能と推定せず、当日の道路・冬季公共駐車状況を確認してください。",
        },
    },
    "迪納利國家公園": {
        "status": "verified",
        "lat": 63.732090,
        "lon": -148.902730,
        "target_type": "viewpoint",
        "label_i18n": {
            "zh-TW": "Denali・Mountain Vista",
            "en": "Denali · Mountain Vista",
            "ja": "デナリ・Mountain Vista",
        },
        "source": "NPS Mountain Vista Scenic View/Photo Spot and published location coordinate; reviewed 2026-09-27",
        "confidence": "medium",
        "note_i18n": {
            "zh-TW": "導航終點為Mountain Vista公共休息／觀景區；Denali Park Road當下道路狀態優先於導航與天氣，封路時不得視為可達。",
            "en": "Directions use the public Mountain Vista rest/scenic area. Current Denali Park Road status overrides navigation and weather; a road closure means this Camera Zone is not reachable.",
            "ja": "ナビはMountain Vista公共休憩・展望エリアを使用します。Denali Park Roadの当日道路状況が天候・ナビより優先され、閉鎖時は到達可能と扱いません。",
        },
    },
    "蘇華德": {
        "status": "verified",
        "lat": 60.103141,
        "lon": -149.434574,
        "target_type": "viewpoint",
        "label_i18n": {
            "zh-TW": "Seward Waterfront Park",
            "en": "Seward Waterfront Park",
            "ja": "スワード・ウォーターフロントパーク",
        },
        "source": "City of Seward published waterfront facility coordinate + Visit Seward subject evidence; reviewed 2026-09-27",
        "confidence": "high",
        "note_i18n": {
            "zh-TW": "導航終點為Seward Waterfront公共區域代表點；實際構圖可沿waterfront trail與合法shoreline步行調整。",
            "en": "Directions use a representative public Seward Waterfront arrival point; refine the composition on foot along the waterfront trail and legal shoreline.",
            "ja": "ナビはSeward Waterfrontの公共エリア代表点を使用し、構図はwaterfront trailと合法な海岸沿いで徒歩調整します。",
        },
    },
    "大霧山國家公園": {
        "status": "verified",
        "lat": 35.611092,
        "lon": -83.425007,
        "target_type": "viewpoint",
        "label_i18n": {
            "zh-TW": "Great Smoky Mountains・Newfound Gap Overlook",
            "en": "Great Smoky Mountains · Newfound Gap Overlook",
            "ja": "グレート・スモーキー山脈・Newfound Gap Overlook",
        },
        "source": "NPS Newfound Gap Scenic View/Photo Spot and overlook access; reviewed 2026-09-27",
        "confidence": "high",
        "note_i18n": {
            "zh-TW": "此點為Newfound Gap公共觀景／停車到達區，可作本題材Camera Zone與導航參考；但US 441／Newfound Gap Road當下封閉公告優先於導航與天氣。",
            "en": "This is the public Newfound Gap overlook/parking arrival area and may serve as the Camera Zone and navigation reference. Current US 441 / Newfound Gap Road closure notices override navigation and weather.",
            "ja": "Newfound Gapの公共展望・駐車到着エリアで、本題材のCamera Zoneとナビ参照に使用できます。ただしUS 441 / Newfound Gap Roadの当日閉鎖情報が天候・ナビより優先されます。",
        },
    },
    "落磯山國家公園": {
        "status": "verified",
        "lat": 40.320324,
        "lon": -105.609000,
        "target_type": "trailhead",
        "label_i18n": {
            "zh-TW": "Rocky Mountain NP・Sprague Lake Trailhead",
            "en": "Rocky Mountain NP · Sprague Lake Trailhead",
            "ja": "ロッキーマウンテン国立公園・Sprague Lake Trailhead",
        },
        "source": "Colorado DNR / CPW COTREX Sprague Lake Trailhead coordinate; reviewed 2026-09-27",
        "confidence": "high",
        "note_i18n": {
            "zh-TW": "導航終點是Sprague Lake Trailhead／停車到達點，與湖邊Camera Zone約數百公尺分離；2026特定日期05:00–18:00進入Bear Lake Road仍需Timed Entry + Bear Lake Road reservation。",
            "en": "Directions use the Sprague Lake Trailhead arrival point, separate from the lakeshore Camera Zone. During applicable 2026 dates, Bear Lake Road entry from 05:00–18:00 still requires Timed Entry + Bear Lake Road.",
            "ja": "ナビはSprague Lake Trailhead到着点を使用し、湖岸Camera Zoneとは分離します。2026年の対象日は05:00–18:00のBear Lake Road入場にTimed Entry + Bear Lake Road予約が必要です。",
        },
    },
    "白沙國家公園": {
        "status": "verified",
        "lat": 32.811370,
        "lon": -106.265010,
        "target_type": "parking",
        "label_i18n": {
            "zh-TW": "White Sands・Sunset Stroll 停車區",
            "en": "White Sands · Sunset Stroll parking area",
            "ja": "ホワイトサンズ・Sunset Stroll 駐車エリア",
        },
        "source": "NPS 2026 Sunset Stroll exact event coordinate; reviewed 2026-09-27",
        "confidence": "high",
        "note_i18n": {
            "zh-TW": "NPS目前活動頁直接公布此停車區座標；導航與此批次Camera Zone／weather sample可共用，但仍須遵守當日園區與Dunes Drive關閉公告。",
            "en": "NPS currently publishes this exact parking-area coordinate. It may serve as navigation, Camera Zone reference, and weather sample for this batch, subject to current park and Dunes Drive closures.",
            "ja": "NPS が現在この駐車エリアの正確な座標を公開しています。本バッチではナビ・Camera Zone 参照・weather sample を兼用できますが、当日の園内・Dunes Drive 閉鎖情報が優先されます。",
        },
    },
    "福岡城跡": {
        "status": "needs_review",
        "target_type": "entrance",
        "label_i18n": {
            "zh-TW": "福岡城跡：天守台封閉中，導航入口待獨立確認",
            "en": "Fukuoka Castle Ruins: Tenshudai closed; arrival point pending verification",
            "ja": "福岡城跡：天守台閉鎖中、到着地点は確認待ち",
        },
        "source": "Fukuoka Castle official notice: Tenshudai closed 2026-05-26 through end of Dec (planned); reviewed 2026-09-27",
        "confidence": "high",
        "note_i18n": {
            "zh-TW": "目前不把舊天守台座標當道路導航或 Camera Zone。多聞櫓、下之橋御門等仍可研究拍攝，但到達／停車點須另行查證。",
            "en": "The legacy Tenshudai coordinate is not used for directions or as a Camera Zone during the closure. Tamon Yagura / Shimonohashi Gate remain valid subjects; arrival/parking needs separate verification.",
            "ja": "閉鎖中は旧天守台座標をナビ目的地や Camera Zone にしません。多聞櫓・下之橋御門は撮影対象ですが、到着・駐車地点は別途確認が必要です。",
        },
    },
    "六十石山": {
        "status": "verified",
        "lat": 23.219472,
        "lon": 121.308056,
        "target_type": "parking",
        "label_i18n": {
            "zh-TW": "六十石山・黃花亭停車場",
            "en": "Liushishishan · Huanghua Pavilion parking",
            "ja": "六十石山・黄花亭駐車場",
        },
        "source": "B34 official venue evidence identifies Huanghua Pavilion parking; reviewed 2026-09-26",
        "confidence": "medium",
        "parking_options": [
            {"name_zh": "黃花亭停車場", "lat": 23.219472, "lon": 121.308056, "status": "verified_primary"},
            {"name_zh": "忘憂亭停車／抵達點", "lat": 23.222194, "lon": 121.317056, "status": "verified_secondary"},
        ],
        "camera_zone_parking_constraints": {
            "小瑞士觀景台": "花季交通管制資料明列小瑞士旁禁止停車；Camera Zone 不得作停車導航終點。",
            "鹿蔥亭": "未查得官方正式停車場，不宣稱可直接停車。",
        },
        "note_i18n": {
            "zh-TW": "主導航先導向黃花亭停車場；忘憂亭另有可用停車／抵達點。小瑞士與鹿蔥亭是攝影 Camera Zone，不等同停車場。",
            "en": "Primary directions use Huanghua Pavilion parking. Wangyou Pavilion has a separate arrival/parking point. Little Switzerland and Lucong Pavilion are photography zones, not parking destinations.",
            "ja": "主ナビは黄花亭駐車場へ案内します。忘憂亭には別の到着・駐車ポイントがあります。小瑞士と鹿蔥亭は撮影 Camera Zone で、駐車場ではありません。",
        },
    },
    "出雲大社": {
        "status": "multiple_access_routes",
        "target_type": "camera_zone_or_place_anchor",
        "label_i18n": {
            "zh-TW": "出雲大社：參道入口或停車場須擇一",
            "en": "Izumo Taisha: choose approach entrance or parking",
            "ja": "出雲大社：参道入口・駐車場を選択",
        },
        "source": "Izumo Oyashiro official approach map and Izumo Tourism Association parking/access guide; reviewed 2026-09-25",
        "confidence": "high",
        "note_i18n": {
            "zh-TW": "徒步自勢溜參道進入，開車可用大停車場等不同入口；本殿區座標不能作為道路導航目的地，待支援路線選擇後再提供導航。",
            "en": "The Seidamari walking approach and shrine parking areas are distinct arrivals. The main-sanctuary coordinate is not a road destination; route selection is needed before offering directions.",
            "ja": "勢溜からの徒歩参道と大駐車場などの車での到着地点は異なります。本殿付近の座標を道路案内の目的地にせず、経路選択実装後にナビを提供します。",
        },
    },
    "加羅湖": {
        "status": "needs_review",
        "target_type": "trailhead",
        "label_i18n": {
            "zh-TW": "加羅湖登山入口待查證",
            "en": "Jialuo Lake trail access pending verification",
            "ja": "加羅湖登山口は確認待ち",
        },
        "source": "R4.2 navigation audit: legacy keyword produced ambiguous Google Maps results",
        "confidence": "low",
        "note_i18n": {
            "zh-TW": "加羅湖為步行登山目的地；在登山口／停車或接駁點完成查證前，不提供關鍵字導航。",
            "en": "Jialuo Lake is reached by hiking. No keyword navigation is offered until the trailhead / parking or transfer point is verified.",
            "ja": "加羅湖は徒歩登山で到達するため、登山口・駐車／乗換地点の確認完了までキーワードナビを提供しません。",
        },
    },
    "新穗高高空纜車": {
        "status": "needs_review",
        "target_type": "station",
        "label_i18n": {
            "zh-TW": "新穗高纜車山麓進入點待查證",
            "en": "Shinhotaka Ropeway base access pending verification",
            "ja": "新穂高ロープウェイ山麓アクセスは確認待ち",
        },
        "source": "B32: Camera Zone is Nishi-Hotakaguchi summit observatory; arrival target must be researched separately",
        "confidence": "medium",
        "note_i18n": {
            "zh-TW": "攝影 Camera Zone 位於西穗高口山頂區，不可直接把山頂座標當成道路導航終點。",
            "en": "The Camera Zone is at the Nishi-Hotakaguchi summit area; the summit coordinate must not be treated as a road-routing destination.",
            "ja": "撮影 Camera Zone は西穂高口山頂エリアのため、山頂座標を道路ナビの目的地として扱いません。",
        },
    },
    "彌彥山": {
        "status": "multiple_access_routes",
        "target_type": "camera_zone_or_place_anchor",
        "label_i18n": {
            "zh-TW": "彌彥山多種進入路線",
            "en": "Mt. Yahiko has multiple access routes",
            "ja": "弥彦山は複数のアクセス経路があります",
        },
        "source": "B32 Yahiko research: ropeway, seasonal skyline road and hiking routes differ",
        "confidence": "high",
        "note_i18n": {
            "zh-TW": "纜車、季節性彌彥山 Skyline 與登山路線的進入點不同；在路線選擇 UI 完成前不指定單一導航終點。",
            "en": "Ropeway, seasonal skyline-road and hiking access use different arrival points. No single destination is chosen until route selection exists.",
            "ja": "ロープウェイ、季節運用の弥彦山スカイライン、登山道で到着地点が異なるため、ルート選択 UI 実装前は単一目的地を指定しません。",
        },
    },
    "等等力溪谷": {
        "status": "verified",
        "lat": 35.607857,
        "lon": 139.646545,
        "target_type": "street_access",
        "label_i18n": {
            "zh-TW": "等等力溪谷・Golf Bridge",
            "en": "Todoroki Valley · Golf Bridge",
            "ja": "等々力渓谷・ゴルフ橋",
        },
        "source": "B32 Setagaya official Golf Bridge entrance landmark + cross-checked bridge coordinate",
        "confidence": "high",
        "note_i18n": {
            "zh-TW": "此點是公共街道／溪谷入口錨點；導航與 Camera Zone 可共用。",
            "en": "This is a public-street / valley-entrance anchor and is suitable as both navigation target and Camera Zone reference.",
            "ja": "公共道路・渓谷入口の基準点で、ナビ目的地と Camera Zone 参照点を兼用できます。",
        },
    },
    "萩市城下町": {
        "status": "verified",
        "lat": 34.4119363,
        "lon": 131.3932271,
        "target_type": "street_access",
        "label_i18n": {
            "zh-TW": "萩城下町・菊屋橫町",
            "en": "Hagi Castle Town · Kikuya Yokocho",
            "ja": "萩城下町・菊屋横町",
        },
        "source": "B32 Hagi City/JNTO historic-lane research + mapped Kikuya Yokocho street anchor",
        "confidence": "high",
        "note_i18n": {
            "zh-TW": "此點為公共歷史街巷的代表進入錨點，可作為步行導航目的地。",
            "en": "This is a representative public historic-lane access anchor suitable for walking navigation.",
            "ja": "公共の歴史街路への代表的なアクセス基準点で、徒歩ナビの目的地として使用できます。",
        },
    },
}


def _navigation_confidence(value):
    """Map legacy coordinate-confidence granularity into the R4.2 navigation enum."""
    if value in (None, ""):
        return "low"
    if value == "medium_high":
        return "medium"
    if value in {"high", "medium", "low"}:
        return value
    raise ValueError(f"unsupported navigation confidence: {value}")


def _navigation_target_for_spot(name_zh, item):
    """Return explicit navigation metadata without inventing a route.

    Existing exact Place/Camera coordinates remain useful as map pins, but they
    are not promoted to verified Directions unless an explicit override says so.
    """
    override = NAVIGATION_TARGET_OVERRIDES.get(name_zh)
    if override:
        target = dict(override)
        target["confidence"] = _navigation_confidence(target.get("confidence"))
        status = target.get("status")
        if status == "verified":
            lat = target.get("lat")
            lon = target.get("lon")
            if lat is None or lon is None:
                raise ValueError(f"{name_zh}: verified navigation target missing coordinates")
            target["lat"] = float(lat)
            target["lon"] = float(lon)
        return target

    lat = item.get("lat")
    lon = item.get("lon")
    if lat is None or lon is None:
        return {
            "status": "needs_review",
            "target_type": "camera_zone_or_place_anchor",
            "label_i18n": dict(item.get("name_i18n") or {}),
            "source": "no exact Place/Camera coordinate available",
            "confidence": "low",
        }

    return {
        "status": "provisional_camera_anchor",
        "lat": float(lat),
        "lon": float(lon),
        "target_type": "camera_zone_or_place_anchor",
        "label_i18n": dict(item.get("name_i18n") or {}),
        "source": item.get("coordinate_source") or "legacy Place/Camera coordinate",
        "confidence": _navigation_confidence(item.get("coordinate_confidence")),
        "note_i18n": {
            "zh-TW": "此座標尚未獨立查證為實際抵達／停車／登山入口，只能先作精準地圖定位，不視為已驗證導航。",
            "en": "This coordinate has not been independently verified as the practical arrival / parking / trail access point. It is shown only as an exact map pin, not verified navigation.",
            "ja": "この座標は実際の到着・駐車・登山口として未検証のため、正確な地図ピンとしてのみ表示し、検証済みナビとは扱いません。",
        },
    }


def _derive_scenes_themes(name_zh, legacy_tags, category, region_key):
    tags = set(legacy_tags or [])
    scenes = set()
    themes = set()

    scene_map = {
        "mountain": "mountain", "coast": "coast", "lake": "lake",
        "forest": "forest", "waterfall": "waterfall", "city": "city",
    }
    for old, new in scene_map.items():
        if old in tags:
            scenes.add(new)

    text = f"{name_zh} {category}".lower()
    def has(*words):
        return any(str(w).lower() in text for w in words)

    if has("濕地", "湿原", "wetland", "marsh", "沼澤"):
        scenes.add("wetland")

    # Avoid substring false positives such as 河口湖 -> river.
    river_terms = ("運河", "溪谷", "溪", "河川", "river", "canal")
    if has(*river_terms) or name_zh.endswith(("河", "川")):
        scenes.add("river")

    if has("峽谷", "canyon", "月世界", "火炎山", "地質", "奇岩", "arches", "arch", "mesa", "monument valley"):
        scenes.add("geology")
    if has("death valley", "white sands", "沙漠", "沙丘", "desert", "dune"):
        scenes.add("desert")
    if has("冰河", "冰川", "glacier", "氷河", "雪景"):
        scenes.add("snow_ice")
    if has("草原", "青青草原", "grassland", "prairie"):
        scenes.add("grassland")
    if has("伯朗大道", "梯田", "稻田", "農場", "farm", "rice"):
        scenes.add("rural")

    # Do not classify every name containing the character 「塔」 as architecture
    # (e.g. Matanuska / Talkeetna transliterations). Use explicit architectural terms.
    architecture_terms = (
        "大橋", "橋", "鐵塔", "鉄塔", "燈塔", "灯台", "tower", "castle",
        "城", "寺", "神社", "市場", "market", "皇居", "大佛", "大仏",
        "pier", "碼頭", "埠頭", "車站", "駅", "樓", "館"
    )
    if has(*architecture_terms) or name_zh.endswith("塔"):
        scenes.add("architecture")

    if "mountain" in scenes or "geology" in scenes or "desert" in scenes or "grassland" in scenes:
        themes.update({"mountain_view", "sunrise", "sunset"})
    if "coast" in scenes:
        themes.update({"sunrise", "sunset", "sky_glow", "blue_hour"})
    if "lake" in scenes or "wetland" in scenes:
        themes.update({"sunrise", "sunset", "fog_mist", "reflection"})
    if "river" in scenes:
        themes.update({"fog_mist", "long_exposure"})
    if "forest" in scenes:
        themes.update({"fog_mist", "sunbeam"})
    if "waterfall" in scenes:
        themes.add("long_exposure")
    # Blue hour can suit architecture, but architecture alone is not evidence of
    # a city-light night scene. Only an explicit city scene may auto-enable
    # city_night; this prevents lighthouses, bridges and isolated landmarks from
    # receiving city-light hints.
    if "city" in scenes:
        themes.update({"blue_hour", "city_night"})
    elif "architecture" in scenes:
        themes.add("blue_hour")
    if "snow_ice" in scenes:
        themes.update({"snow_scene", "mountain_view"})

    if "cloud_sea" in tags:
        themes.add("cloud_sea")
    if "starlight" in tags:
        themes.add("milky_way")
    if "aurora" in tags and region_key == "us" and category == "阿拉斯加":
        themes.add("aurora")

    if not scenes:
        scenes.add("mountain")
    if not themes:
        themes.add("mountain_view")
    return sorted(scenes), sorted(themes)

def get_spots(region="tw"):
    region_key = region.lower()
    region_data = REGIONS.get(region_key, REGIONS["tw"])

    formatted_spots = []
    for idx, spot in enumerate(region_data.get("spots", []), start=1):
        if len(spot) >= 8:
            name_zh = spot[2]
            category = spot[6]
            legacy_tags = list(spot[7])
            item = {
                "spot_id": f"{region_key}-{idx:03d}",
                "lat": spot[0],
                "lon": spot[1],
                "name_i18n": {"zh-TW": name_zh, "en": spot[3], "ja": spot[4]},
                "name_local": spot[5],
                "category": category,
                "tags": legacy_tags,
            }
        else:
            name_zh = spot[2]
            category = spot[3] if len(spot) > 3 else "本島"
            legacy_tags = list(spot[4]) if len(spot) > 4 else ["mountain"]
            item = {
                "spot_id": f"{region_key}-{idx:03d}",
                "lat": spot[0], "lon": spot[1],
                "name_i18n": {"zh-TW": name_zh, "en": name_zh, "ja": name_zh},
                "name_local": name_zh, "category": category, "tags": legacy_tags,
            }

        override = SPOT_OVERRIDES.get(name_zh, {}) if region_key == "tw" else {}
        if override:
            item["lat"] = override.get("lat", item["lat"])
            item["lon"] = override.get("lon", item["lon"])
            if "tags" in override:
                legacy_tags = list(override["tags"])
                item["tags"] = legacy_tags
        display_override = DISPLAY_NAME_OVERRIDES.get(name_zh) if region_key == "tw" else None
        if display_override:
            item["name_i18n"] = {k: display_override[k] for k in ("zh-TW", "en", "ja")}
            item["name_local"] = display_override.get("local", item["name_local"])

        scenes, themes = _derive_scenes_themes(name_zh, legacy_tags, category, region_key)
        item["scenes"] = scenes
        item["themes"] = themes

        # V5.2 explicit location/scene correction layer.
        override = SPOT_OVERRIDES.get(name_zh, {})
        if "lat" in override:
            item["lat"] = float(override["lat"])
        if "lon" in override:
            item["lon"] = float(override["lon"])
        if "scenes" in override:
            item["scenes"] = list(override["scenes"])
        if "themes" in override:
            item["themes"] = list(override["themes"])
        if override.get("name_i18n_override"):
            item["name_i18n"].update(override["name_i18n_override"])
        if override.get("name_local"):
            item["name_local"] = override["name_local"]
        item["map_query"] = override.get("map_query") or item.get("name_local") or name_zh
        item["coordinate_source"] = override.get("coordinate_source", "legacy Place/Camera coordinate; navigation target not independently verified")
        item["coordinate_confidence"] = override.get("coordinate_confidence", "medium")
        item["navigation_target"] = _navigation_target_for_spot(name_zh, item)
        if override.get("elevation") is not None:
            item["elevation"] = override["elevation"]

        elevation = ELEVATION_OVERRIDES.get(name_zh)
        if elevation is not None and item.get("elevation") is None:
            item["elevation"] = elevation
        view = VIEW_AZIMUTH_OVERRIDES.get(name_zh)
        if view is not None:
            item["view_azimuth"] = view[0]
            item["view_tolerance"] = view[1]
        access = ACCESS_RULE_OVERRIDES.get(name_zh)
        if access:
            item.update(access)

        # v0.04 R3 compatibility adapter: attach only manually reviewed
        # Photography Opportunities. Legacy themes remain additive so the
        # current V5.4 UI/scoring path continues to work unchanged.
        opportunities = get_opportunities(region_key, item["spot_id"])
        if opportunities:
            item["opportunities"] = opportunities
            item["themes"] = merge_legacy_themes(item.get("themes", []), opportunities)

        dark_sky = _dark_sky_meta(region_key, name_zh, category, item.get("scenes", []), item.get("themes", []))
        if dark_sky:
            item.update(dark_sky)
        admin_area_map = ADMIN_AREAS_BY_REGION.get(region_key, {})
        item["admin_areas"] = list(admin_area_map.get(item["spot_id"], []))
        item["product_status"] = product_status(item["spot_id"])
        item["active_in_catalog"] = active_in_catalog(item["spot_id"])
        formatted_spots.append(item)
    return formatted_spots
