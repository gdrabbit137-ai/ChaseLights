"""
ChaseLights — 區域與景點分類與主題標籤完整定義設定
"""

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
            (23.0020, 120.4130, "二寮觀日亭", "Erliao Sunrise Pavilion", "二寮観日亭", "二寮", "本島", ["mountain", "cloud_sea"]),
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
        ],
    },
    "us": {
        "name_zh": "美國",
        "name_en": "United States",
        "categories": ["全部", "美西", "美中", "美東", "阿拉斯加"],
        "spots": [
            (36.1070, -112.1130, "大峽谷國家公園", "Grand Canyon National Park", "グランド・キャニオン国立公園", "Grand Canyon NP", "美西", ["mountain", "starlight"]),
            (36.8790, -111.5100, "馬蹄灣", "Horseshoe Bend", "ホースシュー・ベンド", "Horseshoe Bend", "美西", ["mountain", "coast"]),
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
        ],
    },
}

# Known summit / high-elevation camera points.  Passing the real shooting
# elevation helps Open-Meteo select/downscale to a terrain height closer to
# the photographer instead of relying only on the grid-cell DEM.
ELEVATION_OVERRIDES = {
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
ACCESS_RULE_OVERRIDES = {
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

    if has("濕地", "湿原", "wetland", "marsh", "沼澤", "沼"):
        scenes.add("wetland")
    if has("河", "溪", "川", "river", "canal", "運河"):
        scenes.add("river")
    if has("峽谷", "canyon", "月世界", "火炎山", "地質", "奇岩", "arches", "arch", "mesa", "monument valley"):
        scenes.add("geology")
    if has("death valley", "white sands", "沙漠", "沙丘", "desert", "dune"):
        scenes.add("desert")
    if has("冰河", "冰川", "glacier", "氷河", "雪山", "雪景"):
        scenes.add("snow_ice")
    if has("草原", "青青草原", "grassland", "prairie"):
        scenes.add("grassland")
    if has("伯朗大道", "梯田", "稻田", "農場", "farm", "rice"):
        scenes.add("rural")
    if has("大橋", "bridge", "塔", "tower", "城", "castle", "寺", "神社", "市場", "market", "皇居", "大佛", "pier", "碼頭", "車站"):
        scenes.add("architecture")

    # Photographic-condition themes. These are intentionally broader than the
    # original tag list so filters describe a photographer's actual intent.
    if "mountain" in scenes or "geology" in scenes or "desert" in scenes or "grassland" in scenes:
        themes.update({"mountain_view", "sunrise", "sunset"})
    if "coast" in scenes:
        themes.update({"sunrise", "sunset", "sky_glow", "blue_hour", "long_exposure"})
    if "lake" in scenes or "wetland" in scenes:
        themes.update({"sunrise", "sunset", "fog_mist", "reflection"})
    if "river" in scenes:
        themes.update({"fog_mist", "long_exposure"})
    if "forest" in scenes:
        themes.update({"fog_mist", "sunbeam"})
    if "waterfall" in scenes:
        themes.add("long_exposure")
    if "city" in scenes or "architecture" in scenes:
        themes.update({"blue_hour", "city_night"})
    if "snow_ice" in scenes:
        themes.update({"snow_scene", "mountain_view"})

    if "cloud_sea" in tags:
        themes.add("cloud_sea")
    if "starlight" in tags:
        themes.add("milky_way")
    # Aurora is deliberately only a theme for Alaska. Taiwan/Japan and the
    # contiguous-US category filters therefore never expose an Aurora button.
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

        scenes, themes = _derive_scenes_themes(name_zh, legacy_tags, category, region_key)
        item["scenes"] = scenes
        item["themes"] = themes

        elevation = ELEVATION_OVERRIDES.get(name_zh)
        if elevation is not None:
            item["elevation"] = elevation
        view = VIEW_AZIMUTH_OVERRIDES.get(name_zh)
        if view is not None:
            item["view_azimuth"] = view[0]
            item["view_tolerance"] = view[1]
        access = ACCESS_RULE_OVERRIDES.get(name_zh)
        if access:
            item.update(access)
        formatted_spots.append(item)
    return formatted_spots
