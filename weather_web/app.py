"""
PhotoWeather Web — Flask 主程式

提供：
- 台灣全島能見度預報動態地圖（24小時，每小時一幀）
- 今日/明日最佳攝影點摘要
- 靜態檔案服務
"""

import json, os, sys, time, tempfile
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, jsonify, request

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
REGIONS_DIR = os.path.dirname(os.path.abspath(__file__))
if REGIONS_DIR not in sys.path:
    sys.path.insert(0, REGIONS_DIR)

from regions import REGIONS

app = Flask(__name__)

TW = timezone(timedelta(hours=8))  # 台灣時區

# ─── 真 實 海 拔 對 照 表 ──────────────────────────────────
# Open-Meteo 用 7km 網格，山區高程誤差大，此表覆蓋校正
TRUE_ELEVATIONS = {
    "大屯山助航站": 1082, "象山": 183,
    "九份不厭亭": 490, "觀音山硬漢嶺": 616,
    "火炎山": 602, "鳶嘴山": 2180, "合歡山主峰": 3417,
    "金龍山": 820, "武界部落": 760,
    "二延平步道": 1248, "頂石棹": 1650, "阿里山": 2216,
    "二寮": 220, "抹茶山": 900,
    "見晴懷古步道": 900, "清水斷崖": 100, "六十石山": 960,
    "玉山主峰": 3952, "雪山主峰": 3886,
    "雪山北峰": 3703, "奇萊主峰": 3560, "南湖大山": 3742,
    "嘉明湖": 3310, "大霸尖山": 3492, "北大武山": 3092,
    "池有山": 3303, "桃山": 3325, "品田山": 3524,
    "杉林溪": 1600, "雲洞山莊": 800,
    "五峰旗瀑布": 200, "小崗山雲臺": 100, "大古山": 100,
    "墾丁鵝鑾鼻": 60, "屏東關山": 152,
}

# ─── 攝 影 提 示 辭 典 ────────────────────────────────────
# 每個景點簡短的拍攝題材說明（顯示在摘要頁卡片上）
# tip 會依最佳時間自動調整（日出/日落/通用）
PHOTO_TIPS = {
    "大屯山助航站": "夕陽雲海琉璃光 · 廣角16-35mm · 日落前卡位",
    "象山": "101日出城市景 · 70-200mm壓縮 · 日出前30分鐘到",
    "淡水漁人碼頭": "金色夕陽情人橋 · 16-35mm+CPL · 日落前40分鐘",
    "九份不厭亭": "山海S彎道夕陽 · 70-200mm壓縮 · 雨後雲海機率高",
    "金瓜石茶壺山": "陰陽海全景 · 16-35mm+70-200mm · 晴天最適合",
    "大稻埕碼頭": "淡水河夕陽+飛機 · 長焦追飛機 · 日落前1小時",
    "關渡大橋": "夕陽車軌倒影 · ND減光鏡長曝 · 日落後藍調時段",
    "碧潭": "吊橋城市倒影 · 無風出鏡面 · 16-35mm低角度",
    "觀音山硬漢嶺": "台北盆地夜景 · 雨後雲海 · 廣角16-35mm",
    "高美濕地": "夕陽風車天空之鏡 · 退潮+無風 · CPL偏光鏡",
    "合歡山主峰": "雲海星空絕景 · 16-35mm f/2.8 · 雨後放晴必衝",
    "二延平步道": "雲海夕陽茶園 · 冬季午後雨轉晴 · 廣角+長焦",
    "頂石棹": "琉璃光雲海霞光 · 雨後放晴 · 低雲40-70%最美",
    "阿里山": "日出雲海森林小火車 · 冬季清晨 · 祝山觀日平台",
    "二寮": "日出雲海(三大日出地) · 清晨積雲>60% · 廣角16-35mm",
    "抹茶山": "抹茶色山巒雲霧 · 雨後放晴晨霧 · 聖母山莊展望台",
    "見晴懷古步道": "森林鐵道雲霧 · 全球最美小路 · 雨後晨霧漫射光",
    "清水斷崖": "斷崖太平洋日出 · 能見度>20km · 廣角大景",
    "六十石山": "金針花海(8-9月) · 日出雲海縱谷 · 花季清晨",
    "七星潭": "月牙灣日出 · 浪花前景 · 廣角16-35mm+CPL",
    "多良車站": "最美車站太平洋日出 · 火車+海景 · 清晨順光",
    "三仙台": "日出拱橋岩石 · 能見度>20km · 漲潮時浪花前景",
    "池上伯朗大道": "金黃稻田晨霧 · 秋收10-11月 · 無風出鏡面",
    "玉山主峰": "台灣最高峰日出雲海 · 排雲山莊過夜 · 冬季雪景",
    "雪山主峰": "圈谷雲海星軌 · 黑森林 · 冬季雪景夢幻",
    "奇萊主峰": "金色晨光稜線 · 70-200mm壓縮 · 天氣多變注意安全",
    "南湖大山": "審馬陣草原遠眺帝王山形 · 上圈谷冰河地形 · 70-200mm · 4-5天行程",
    "嘉明湖": "天使眼淚銀河倒影 · 16-35mm f/2.8 · 新月+無風",
    "大霸尖山": "世紀奇峰酒桶狀 · 大小霸連稜 · 70-200mm壓縮",
    "北大武山": "南台雲海日出 · 冬春最佳 · 16-35mm大景",
    "池有山": "池有名樹+雪山背景 · 70-200mm壓縮 · 武陵農場出發",
    "桃山": "金色日出稜線 · 聖稜線全景 · 武陵方向經典視角",
    "品田山": "皺褶岩層V型斷崖 · 新達山屋或池有山腰遠眺 · 70-200mm壓縮",
    "澎湖跨海大橋": "夕陽橋拱剪影 · 能見度>15km · 廣角橋下構圖",
    "奎壁山": "摩西分海奇景 · 退潮時段 · 空拍/高角度",
    "七美雙心石滬": "經典雙心造型 · 退潮+晴天 · 空拍或崖上俯拍",
    "金門得月樓": "洋樓建築倒影 · 雨後積水拍鏡面 · 16-35mm低角度",
    "翟山坑道": "軍事坑道光影 · 水道倒影 · 不受天氣影響",
    "馬祖南竿": "藍眼淚4-9月 · 無月+無風 · 北海坑道搖櫓",
    "東引燈塔": "燈塔懸崖日出 · 能見度>20km · 藍眼淚季兼拍",
    "北竿芹壁": "石頭聚落海灣 · 晴藍天最美 · 藍眼淚季",
    "綠島朝日溫泉": "海上日出溫泉 · 能見度>15km · 晨曦剪影",
    "蘭嶼東清灣": "拼板舟日出剪影 · 經典蘭嶼 · 清晨05:00卡位",
    "蘭嶼青青草原": "蘭嶼日落最佳點 · 草原+海景 · 高雲30-60%夕陽",
    "小琉球花瓶岩": "珊瑚礁岩夕陽 · 晴天+高雲 · 廣角帶海景",
    "日月潭": "晨霧日出湖面倒影 · 無風如鏡 · 涵碧樓方向",
    "金龍山": "日出雲海琉璃光 · 台灣三大日出地 · 清晨低雲>60%",
    "武界部落": "雲海晨霧茶園 · 雨後清晨 · 布農部落文化",
    "火炎山": "惡地景觀夕陽 · 雨後山脊最紅 · 70-200mm壓縮",
    "雲洞山莊": "雲海夕陽夜景 · 雨後放晴 · 苗栗經典雲海點",
    "鳶嘴山": "稜線雲海杜鵑 · 雨後放晴 · 稍來山步道",
    "香山濕地": "夕陽風車蚵架 · 高雲30-50%火燒雲 · 退潮倒影",
    "永安漁港": "夕陽彩虹橋 · 能見度>15km · 橋墩倒影構圖",
    "井仔腳鹽田": "鹽田夕陽天空之鏡 · 無風+高雲 · 低角度貼水面",
    "田寮月世界": "惡地夕陽奇景 · 雨後最紅 · 廣角16-35mm",
    "駁二藝術特區": "碼頭夕陽藝術裝置 · 雨後積水倒影 · 廣角",
    "墾丁鵝鑾鼻": "鵝鑾鼻燈塔日出 · 星空 · 晴天+無雲",
    "屏東關山": "恆春半島日落最佳 · 高雲30-60%火燒雲 · 廣角",
    "王功漁港": "夕陽蚵架風車 · 退潮潮間帶倒影 · 無風出鏡面",
    "望幽谷": "海天一色日出 · 能見度>15km · 基隆海景",
    "和平島": "奇岩地質日出 · 退潮+晴天 · 豆腐岩前景",
    "正濱漁港": "彩色屋倒影 · 晴天或雨後 · 童話風格",
    "大古山": "夕陽飛機起降 · 夜景海景 · 長焦追飛機",
    "小崗山雲臺": "夕陽水庫倒影 · 夜景 · 晴天能見度佳",
    "杉林溪": "瀑布楓葉霧氣森林 · 秋季漫射光 · ND+CPL",
    "五峰旗瀑布": "瀑布溪流森林 · 陰天漫射光最佳 · ND慢速快門",
    "粉鳥林": "日出奇岩海灣 · 能見度>15km · 秘境海灘",
    "雪山北峰": "聖稜線日出金色稜線 · 70-200mm壓縮 · 雪北—大霸經典視角",

    # ─── 🇯🇵 日本 ─────────────────────────────────────
    "富士山(山梨)": "富士山日出雲海 · 冬季空氣最通透 · 70-200mm壓縮山景",
    "東京鐵塔": "東京城市全景 · 黃昏藍調 · 16-35mm+三腳架",
    "清水寺(京都)": "清水舞台紅葉/櫻花 · 春秋最美 · 16-35mm+CPL",
    "大阪城": "天守閣日出剪影 · 能見度>15km · 70-200mm壓縮",
    "萩市城下町": "武家屋敷街道 · 雨後積水倒影 · 24-70mm",
    "福岡城跡": "舞鶴公園櫻花+古城 · 春日清晨 · 24-70mm",
    "鎌倉大仏": "大佛+紫陽花(6月) · 陰天漫射光 · 24-70mm",
    "諏訪湖": "湖面晨霧富士山遠眺 · 冬季清晨 · 70-200mm",
    "等々力渓谷(東京)": "都市秘境溪谷楓葉 · 秋季漫射光 · ND+CPL慢速",
    "出雲大社": "大社造建築晨光 · 晴天藍天 · 16-35mm對稱構圖",
    "六甲山(神戶)": "神戶港百萬夜景 · 藍調時段 · 70-200mm壓縮",
    "高野山": "奧之院參天杉林 · 晨霧漫射光 · 24-70mm",
    "皇居(東京)": "皇居護城河倒影 · 無風清晨 · 16-35mm低角度",
    "横浜山下公園": "港未來+冰川丸夕陽 · 16-35mm+CPL",
    "伊賀上野城": "忍者之城+天守閣 · 晴天藍天 · 24-70mm",
    "金沢兼六園": "日本庭園雪吊/紅葉 · 冬季雪景或秋楓 · 24-70mm",
    "名古屋城": "金鯱天守日出 · 能見度>15km · 16-35mm",
    "浜名湖": "湖面夕陽+橋景 · 高雲30-60% · 16-35mm+CPL",
    "鳴門海峡(徳島)": "鳴門漩渦+夕陽 · 滿潮前後 · 70-200mm+長焦",
    "唐津城": "舞鶴橋+天守閣夕陽 · 高雲30-60% · 70-200mm",
    "長崎グラバー園": "洋館+長崎港夕陽 · 晴天+高雲 · 24-70mm",
    "福岡タワー": "福岡城市夜景 · 藍調時段 · 16-35mm+三腳架",
    "倉敷美観地区": "白牆倉庫+運河倒影 · 無風清晨 · 16-35mm低角度",
    "みなとみらい(横浜)": "橫濱港未來夜景 · 藍調+摩天輪 · 16-35mm",
    "新穂高ロープウェイ": "北阿爾卑斯全景 · 冬季雪景 · 70-200mm壓縮",
    "弥彦山": "日本海夕陽+神社 · 晴天高雲 · 16-35mm",
    "松島": "松島灣夕陽+奇岩 · 能見度>15km · 70-200mm",
    "磐梯山": "豬苗代湖+磐梯山倒影 · 無風清晨 · 70-200mm",
    "十和田湖": "湖面晨霧+紅葉(秋季) · 清晨無風 · 16-35mm+CPL",
    "摩周湖": "摩周藍+湖面霧 · 清晨能見度佳 · 16-35mm+CPL",
    "美瑛青い池": "青池藍色幻境 · 晴天正午順光 · 16-35mm+CPL",
    "旭岳(北海道)": "北海道最高峰登山纜車 · 夏季高山植物 · 24-70mm",
    "釧路湿原": "濕原晨霧+丹頂鶴 · 冬季清晨 · 70-200mm長焦",
    "函館山": "函館百萬夜景 · 日落後藍調 · 70-200mm壓縮",
    "小樽運河": "運河倉庫雪景燈飾 · 冬季傍晚 · 16-35mm+三腳架",

    # ─── 🏔️ 阿拉斯加 ─────────────────────────────────
    "Denali National Park": "Denali雪峰+馴鹿 · 夏季清晨 · 70-200mm壓縮山景",
    "Fairbanks Aurora": "北極光舞動 · 夜間21:00-03:00 · 14-24mm f/2.8+三腳架",
    "Chena Hot Springs": "溫泉+極光冰雕 · 冬季夜間 · 16-35mm+保暖裝備",
    "Anchorage": "Turnagain Arm海灣日落 · 能見度>20km · 16-35mm+CPL",
    "Seward": "Resurrection海灣+冰川 · 清晨順光 · 24-70mm+CPL",
    "Hatcher Pass": "高山草原野花(7-8月) · 夏季午後 · 16-35mm大景",
    "Matanuska Glacier": "冰川冰藍裂隙 · 陰天漫射光 · 16-35mm+冰爪",
    "Portage Glacier": "冰川湖面浮冰 · 清晨靜止 · 70-200mm壓縮",
    "Valdez": "峽灣瀑布+雪山 · 能見度>15km · 16-35mm大景",
    "Juneau": "門登霍爾冰河+海峽 · 清晨順光 · 24-70mm+CPL",
    "Mendenhall Glacier": "冰川冰瀑+湖面 · 陰天最佳 · 16-35mm+ND",
    "Homer Spit": "海峽夕陽+釣魚碼頭 · 高雲30-60% · 70-200mm壓縮",
    "Ketchikan": "海灣水上機場 · 晴天清晨 · 24-70mm+CPL",
    "Skagway": "White Pass窄軌火車+秋色 · 9月 · 16-35mm+CPL",
    "Wrangell-St.Elias": "北美最大冰河區 · 夏季午後 · 70-200mm壓縮冰河",
    "Brooks Range": "北極圈苔原山脈 · 夏季午夜太陽 · 16-35mm廣角",
    "Arctic Circle": "北極圈標示牌 · 午夜太陽或極光 · 16-35mm",
    "Nome": "白令海日落+雪撬狗 · 冬季 · 24-70mm+保暖",
    "Katmai National Park": "棕熊捕鮭+瀑布 · 7-9月 · 70-200mm+長焦安全距離",
    "Glacier Bay": "冰河峽灣+冰山 · 清晨順光 · 16-35mm+70-200mm",
    "Kodiak Island": "Kodiak棕熊+海岸 · 夏季清晨 · 70-200mm長焦",
    "Eklutna Lake": "湖水土耳其藍+雪山 · 清晨無風 · 16-35mm+CPL",
    "Talkeetna": "Denali南面遠眺+小鎮 · 晴天 · 70-200mm壓縮",
    "Alyeska Girdwood": "Alyeska纜車山頂全景 · 秋季彩葉 · 16-35mm",
    "Chugach State Park": "安克拉治城市+海灣背景 · 黃昏 · 70-200mm",
    "Bering Land Bridge": "白令海海岸苔原 · 夏季午夜太陽 · 16-35mm",
    "Yukon River": "育空河日落+針葉林 · 晚秋 · 16-35mm+CPL",
    "Noatak River": "北極圈內河流苔原 · 夏季 · 16-35mm+防蚊",
    "Lake Clark": "湖水倒映火山 · 清晨無風 · 16-35mm+CPL",
    "Independence Mine": "廢棄金礦遺跡 · 夏季午後 · 24-70mm+廣角",

    # ─── 🇺🇸 美國 ────────────────────────────────────
    "Grand Canyon": "大峽谷日出日落 · 能見度>30km · 16-35mm+Mather Point",
    "Horseshoe Bend": "馬蹄灣日落 · 中午後順光 · 16-35mm超廣角",
    "Antelope Canyon": "羚羊峽谷光束 · 中午11-13時 · 16-35mm+三腳架禁帶",
    "Monument Valley": "紀念碑谷日落剪影 · 高雲30-60% · 70-200mm壓縮",
    "Arches NP": "精緻拱門日落 · 冬季最佳 · 16-35mm+三腳架",
    "Bryce Canyon": "Bryce岩柱日出 · 低角度陽光 · 70-200mm壓縮",
    "Zion NP": "Zion峽谷+天使降臨步道 · 春季/秋季 · 16-35mm",
    "Yosemite Half Dome": "Half Dome+鏡面湖 · 春季融雪 · 16-35mm+CPL",
    "Yosemite Tunnel View": "Tunnel View經典全景 · 冬季雪景 · 16-35mm+三腳架",
    "Yellowstone Grand Prismatic": "大稜鏡溫泉空拍/步道 · 中午順光 · 24-70mm+偏光鏡",
    "Grand Teton NP": "Schwabacher湖倒映Teton · 清晨無風 · 70-200mm",
    "Mount Rainier": "野花+Rainier倒影 · 7-8月清晨 · 16-35mm+CPL",
    "Crater Lake": "火山口湖純藍 · 夏季清晨無風 · 16-35mm+CPL",
    "Death Valley": "Zabriskie Point日落 · 冬季涼爽 · 16-35mm+長焦",
    "White Sands": "白色沙丘日落+剪影 · 日落前1hr · 16-35mm低角度",
    "Golden Gate Bridge SF": "金門大橋日出+霧 · 夏季清晨 · 70-200mm壓縮",
    "Manhattan Skyline": "曼哈頓天際線夕陽 · 能見度>20km · 70-200mm",
    "Niagara Falls": "尼加拉瀑布彩虹 · 上午順光 · 16-35mm+ND慢速",
    "Chicago Skyline": "芝加哥天際線+湖面 · 藍調時段 · 70-200mm壓縮",
    "Las Vegas Strip": "賭城大道夜景霓虹 · 夜間 · 24-70mm+三腳架",
    "Great Smoky Mountains": "大煙山晨霧+秋色 · 10月清晨 · 70-200mm壓縮",
    "Mount St. Helens": "聖海倫火山口+湖 · 夏季清晨 · 70-200mm",
    "Rocky Mountains": "落磯山脈+高山湖 · 清晨無風 · 16-35mm+CPL",
    "Glacier NP": "冰川國家公園+野花 · 7-8月 · 16-35mm+70-200mm",
    "Olympic NP": "Hoh雨林苔蘚+霧 · 陰天漫射光 · 24-70mm+CPL",
    "Redwood NP": "紅木森林參天巨木 · 陰天漫射光 · 16-35mm仰角",
    "Canyonlands Mesa Arch": "Mesa Arch日出框景 · 日出前30min · 16-35mm",
    "Joshua Tree NP": "Joshua Tree+星空 · 新月+無雲 · 14-24mm f/2.8",
    "Saguaro NP": "仙人掌日落剪影 · 高雲30-60% · 70-200mm壓縮",
    "Miami Beach": "邁阿密海灘日出 · 清晨順光 · 24-70mm+CPL",
    "Seattle Space Needle": "Space Needle+Mt Rainier · 晴天清晨 · 70-200mm",
    "New Orleans French Quarter": "French Quarter街景+鐵雕 · 陰天漫射光 · 24-70mm",
    "Boston Skyline": "波士頓天際線+查爾斯河 · 夕陽 · 16-35mm+CPL",
    "Santa Monica Pier": "聖塔摩尼卡碼頭夕陽 · 高雲30-60% · 16-35mm",
    "Pike Place Market": "派克市場飛魚秀+海景 · 上午 · 24-70mm",
    "Denver Skyline": "丹佛天際線+山背景 · 清晨順光 · 70-200mm",
    "St Louis Gateway Arch": "Gateway Arch+倒影 · 清晨無風 · 16-35mm低角度",
    "Fort Worth Stockyards": "西部牛仔趕牛+木造建築 · 午後 · 24-70mm",
    "Sawtooth Mountains": "Sawtooth湖面倒影 · 秋季清晨 · 16-35mm+CPL",
    "Los Angeles Observatory": "Griffith Obs+LA日落 · 藍調時段 · 70-200mm壓縮",
}

# ─── 時 段 感 知 tip ─────────────────────────────────────
# 當最佳時間與 tip 文字衝突時自動切換日出/日落版本
TIME_AWARE_TIPS = {
    "淡水漁人碼頭": {"sunrise": "金色晨光情人橋 · 16-35mm+CPL · 日出後30分鐘", "sunset": "金色夕陽情人橋 · 16-35mm+CPL · 日落前40分鐘"},
    "大屯山助航站": {"sunrise": "晨光雲海琉璃光 · 廣角16-35mm · 日出前卡位", "sunset": "夕陽雲海琉璃光 · 廣角16-35mm · 日落前卡位"},
    "關渡大橋": {"sunrise": "晨光車軌倒影 · ND減光鏡長曝 · 日出後藍調時段", "sunset": "夕陽車軌倒影 · ND減光鏡長曝 · 日落後藍調時段"},
    "大稻埕碼頭": {"sunrise": "晨光河景+飛機 · 長焦追飛機 · 日出前30分鐘", "sunset": "淡水河夕陽+飛機 · 長焦追飛機 · 日落前1小時"},
    "高美濕地": {"sunrise": "晨光風車天空之鏡 · 退潮+無風 · CPL偏光鏡", "sunset": "夕陽風車天空之鏡 · 退潮+無風 · CPL偏光鏡"},
    "九份不厭亭": {"sunrise": "山海S彎道晨光 · 70-200mm壓縮 · 雨後雲海機率高", "sunset": "山海S彎道夕陽 · 70-200mm壓縮 · 雨後雲海機率高"},
    "小琉球花瓶岩": {"sunrise": "珊瑚礁岩晨光 · 晴天+高雲 · 廣角帶海景", "sunset": "珊瑚礁岩夕陽 · 晴天+高雲 · 廣角帶海景"},
    "火炎山": {"sunrise": "惡地晨光 · 雨後山脊最紅 · 70-200mm壓縮", "sunset": "惡地景觀夕陽 · 雨後山脊最紅 · 70-200mm壓縮"},
    "雲洞山莊": {"sunrise": "雲海晨光 · 雨後放晴 · 苗栗經典雲海點", "sunset": "雲海夕陽夜景 · 雨後放晴 · 苗栗經典雲海點"},
    "香山濕地": {"sunrise": "晨光風車蚵架 · 高雲30-50%火燒雲 · 退潮倒影", "sunset": "夕陽風車蚵架 · 高雲30-50%火燒雲 · 退潮倒影"},
    "永安漁港": {"sunrise": "彩虹橋晨光 · 能見度>15km · 橋墩倒影構圖", "sunset": "夕陽彩虹橋 · 能見度>15km · 橋墩倒影構圖"},
    "井仔腳鹽田": {"sunrise": "鹽田晨光天空之鏡 · 無風+高雲 · 低角度貼水面", "sunset": "鹽田夕陽天空之鏡 · 無風+高雲 · 低角度貼水面"},
    "田寮月世界": {"sunrise": "惡地晨光 · 雨後最紅 · 廣角16-35mm", "sunset": "惡地夕陽奇景 · 雨後最紅 · 廣角16-35mm"},
    "屏東關山": {"sunrise": "恆春半島晨光 · 高雲30-60%火燒雲 · 廣角", "sunset": "恆春半島日落最佳 · 高雲30-60%火燒雲 · 廣角"},
    "王功漁港": {"sunrise": "晨光蚵架風車 · 退潮潮間帶倒影 · 無風出鏡面", "sunset": "夕陽蚵架風車 · 退潮潮間帶倒影 · 無風出鏡面"},
    "大古山": {"sunrise": "晨景飛機起降 · 海景 · 長焦追飛機", "sunset": "夕陽飛機起降 · 夜景海景 · 長焦追飛機"},
    "小崗山雲臺": {"sunrise": "水庫晨光倒影 · 晴天能見度佳", "sunset": "夕陽水庫倒影 · 夜景 · 晴天能見度佳"},
    "二延平步道": {"sunrise": "雲海晨光茶園 · 冬季清晨雨轉晴 · 廣角+長焦", "sunset": "雲海夕陽茶園 · 冬季午後雨轉晴 · 廣角+長焦"},
    "蘭嶼青青草原": {"sunrise": "蘭嶼晨光最佳點 · 草原+海景 · 高雲30-60%朝霞", "sunset": "蘭嶼日落最佳點 · 草原+海景 · 高雲30-60%夕陽"},
    "頂石棹": {"sunrise": "琉璃光雲海晨光 · 雨後放晴 · 低雲40-70%最美", "sunset": "琉璃光雲海霞光 · 雨後放晴 · 低雲40-70%最美"},
    "桃山": {"sunrise": "金色日出稜線 · 聖稜線全景 · 武陵方向經典視角", "sunset": "金色夕照稜線 · 聖稜線全景 · 武陵方向經典視角"},
    "蘭嶼東清灣": {"sunrise": "拼板舟日出剪影 · 經典蘭嶼 · 清晨05:00卡位", "sunset": "拼板舟夕照剪影 · 經典蘭嶼 · 傍晚經典光線"},
    "綠島朝日溫泉": {"sunrise": "海上日出溫泉 · 能見度>15km · 晨曦剪影", "sunset": "海上夕照溫泉 · 能見度>15km · 暮色剪影"},
    "東引燈塔": {"sunrise": "燈塔懸崖日出 · 能見度>20km · 藍眼淚季兼拍", "sunset": "燈塔懸崖夕照 · 能見度>20km · 藍眼淚季兼拍"},
    "澎湖跨海大橋": {"sunrise": "橋拱晨光剪影 · 能見度>15km · 廣角橋下構圖", "sunset": "夕陽橋拱剪影 · 能見度>15km · 廣角橋下構圖"},
    "駁二藝術特區": {"sunrise": "碼頭晨光藝術裝置 · 雨後積水倒影 · 廣角", "sunset": "碼頭夕陽藝術裝置 · 雨後積水倒影 · 廣角"},
}

# ─── 季 節 限 定 規 則 ──────────────────────────────────────
# 哪些關鍵詞對應哪些月份，超出月份時自動過濾
SEASON_RULES = [
    (["金針花", "六十石山"], 8, 9, "🍂 金針花季為8-9月，目前為縱谷風光"),
    (["櫻花", "sakura"], 2, 4, "🌸 櫻花季已過，目前為庭園景觀"),
    (["螢火蟲"], 4, 5, "🪲 螢火蟲季為4-5月"),
    (["藍眼淚"], 4, 9, "🌌 藍眼淚季為4-9月"),
    (["鮭魚", "棕熊捕", "Katmai"], 7, 9, "🐻 棕熊捕鮭季為7-9月"),
    (["極光", "Aurora"], 8, 4, "🌌 極光季為8月～4月"),
    (["午夜太陽"], 5, 8, "☀️ 午夜太陽季為5-8月"),
    (["銀河"], 4, 9, "🌌 銀河季為4-9月"),
    (["紅葉", "楓葉"], 9, 11, "🍁 紅葉季為9-11月"),
    (["雪景", "雪吊", "冠雪", "雪稜"], 12, 3, "❄️ 冬季雪景"),
    (["夏季高山植物"], 6, 8, "🏔️ 夏季高山植物"),
    (["秋色", "彩葉", "白楊"], 9, 11, "🍂 秋季彩葉"),
    (["野花", "杜鵑"], 4, 7, "🌸 野花季"),
    (["晨霧"], 10, 4, "🌫️ 晨霧季（秋冬清晨）"),
]


def _filter_tip_season(tip, name, month):
    """過期季節性的關鍵詞，回傳替代文字"""
    has_season = False
    for keywords, start_m, end_m, alt in SEASON_RULES:
        match = any(kw in tip or kw in name for kw in keywords)
        if not match:
            continue
        has_season = True
        if start_m <= end_m:
            if start_m <= month <= end_m:
                return tip  # 在季節內，維持原樣
            return alt
        else:
            # 跨年區間（如極光 8~4）
            if month >= start_m or month <= end_m:
                return tip
            return alt
    return tip  # 無季節限制


GENERIC_GENRES = {
    "🏔️ 晴空山景", "🏔️ 山巒層次", "🌊 海岸風光",
    "🌊 碧海藍天", "🏙️ 晴空城市", "🏙️ 城市風光",
    "🏙️ 城市景觀", "🌿 瀑布景觀", "🌲 森林浴",
}


def weather_tip(info, name, month=None):
    """天氣+季節感知 tip，取代舊 tip_for_day + get_time_aware_tip"""
    if month is None:
        month = datetime.now(TW).month

    # 無資料：回退靜態 tip
    if not info:
        tip = PHOTO_TIPS.get(name, "")
        return _filter_tip_season(tip, name, month)

    genre = info.get("best_genre", "")
    best_hour = extract_hr(info.get("best_time"))
    sunrise_h = extract_hr(info.get("sunrise"))
    sunset_h = extract_hr(info.get("sunset"))

    # — 若 genre 是特定天氣（非通用）→ 直接用天氣感知標題
    if genre and genre not in GENERIC_GENRES:
        return _filter_tip_season(genre, name, month)

    # — 通用天氣 → 用時段感知靜態 tip
    if best_hour is not None and name:
        is_near_sunrise = sunrise_h is not None and abs(best_hour - sunrise_h) <= 2
        is_near_sunset = sunset_h is not None and abs(best_hour - sunset_h) <= 2
        ts = TIME_AWARE_TIPS.get(name)
        if ts:
            if is_near_sunrise and "sunrise" in ts:
                return _filter_tip_season(ts["sunrise"], name, month)
            if is_near_sunset and "sunset" in ts:
                return _filter_tip_season(ts["sunset"], name, month)

    tip = PHOTO_TIPS.get(name, "")
    return _filter_tip_season(tip, name, month)


def extract_hr(time_str):
    """從 ISO 時間字串取出小時"""
    if not time_str or "T" not in time_str:
        return None
    try:
        return int(time_str.split("T")[1].split(":")[0])
    except:
        return None


# ─── 知 識 庫 資 料 ──────────────────────────────────────────
# 從知識庫檔案載入景點分類（共用型 + 地區型）
KNOWLEDGE_SPOTS = {}
_kb_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Knowledge Base")
for fname in ["共用型_攝影知識庫.md", "台灣攝影景點指南.md",
              "日本攝影景點指南.md", "阿拉斯加攝影景點指南.md",
              "美國攝影景點指南.md"]:
    try:
        fp = os.path.join(_kb_dir, fname)
        if os.path.exists(fp):
            with open(fp, "r", encoding="utf-8") as f:
                key = fname.replace(".md", "").replace("_", " ")
                KNOWLEDGE_SPOTS[key] = f.read()
    except:
        pass


# ─── 輔 助 函 數 ──────────────────────────────────────────────

def get_cached_forecast(region="tw"):
    """讀取特定區域的快取天氣資料"""
    cache_file = os.path.join(CACHE_DIR, f"forecast_{region}.json")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"points": [], "error": f"No cache for region '{region}'. Run: python weather_web/build_cache.py {region}"}


def classify_visibility(v):
    """能見度分類（給前端顏色用）"""
    if v is None or v <= 0:
        return "nodata"
    if v < 5000:
        return "very_poor"
    elif v < 10000:
        return "poor"
    elif v < 15000:
        return "fair"
    elif v < 20000:
        return "good"
    elif v < 30000:
        return "very_good"
    else:
        return "excellent"


def classify_scene(name):
    """
    依景點名稱判斷適合的拍攝題材類型（可回傳多種）

    某些景點天生跨題材，例如：
    大屯山 → 雲海(山區) + 夕陽大景(海岸向) + 琉璃光(城市)
    象山   → 101日出(城市) + 火燒雲(海岸向)
    日月潭 → 晨霧(森林) + 日出倒影(湖岸)
    """
    # ── 明確指定多重題材的景點 ──────────────
    multi_scene = {
        "大屯山助航站": ["mountain", "coastal", "general"],
        "九份不厭亭":   ["mountain", "coastal"],
        "金瓜石茶壺山": ["mountain", "coastal"],
        "象山":         ["coastal", "general"],
        "觀音山硬漢嶺": ["mountain", "coastal"],
        "日月潭":       ["mountain", "coastal", "forest"],
        "碧潭":         ["coastal", "general"],
        "關渡大橋":     ["coastal", "general"],
        "大稻埕碼頭":   ["coastal", "general"],
        "望幽谷":       ["coastal", "mountain"],
        "火炎山":       ["mountain", "coastal"],
        "鳶嘴山":       ["mountain", "general"],
        "武界部落":     ["mountain", "forest"],
        "金龍山":       ["mountain", "forest"],
        "二延平步道":   ["mountain", "forest"],
        "頂石棹":       ["mountain", "general"],
        "阿里山":       ["mountain", "forest"],
        "二寮":         ["mountain", "forest"],
        "清水斷崖":     ["coastal", "mountain"],
        "六十石山":     ["mountain"],
        "七星潭":       ["coastal", "general"],
        "三仙台":       ["coastal", "general"],
        "池上伯朗大道": ["general", "forest"],
        "綠島朝日溫泉": ["coastal", "general"],
        "蘭嶼東清灣":   ["coastal", "mountain"],
        "抹茶山":       ["mountain", "forest"],
        "杉林溪":       ["forest", "waterfall"],
        # 國際自然景點（英文，無法靠關鍵詞匹配）
        "Horseshoe Bend":       ["coastal", "mountain"],
        "Yosemite Half Dome":   ["mountain", "general"],
        "Yosemite Tunnel View": ["mountain"],
        "Yellowstone Grand Prismatic": ["mountain", "general"],
        "White Sands":          ["mountain", "general"],
        "Golden Gate Bridge SF": ["coastal", "general"],
        # 日本自然景點
        "等々力渓谷(東京)": ["forest", "waterfall"],
        "美瑛青い池":      ["mountain", "coastal"],
        "釧路湿原":        ["coastal", "forest"],
        "新穂高ロープウェイ": ["mountain"],
        # 阿拉斯加自然景點
        "Fairbanks Aurora":  ["mountain", "general"],
        "Chena Hot Springs": ["mountain", "general"],
        "Hatcher Pass":      ["mountain"],
        "Wrangell-St.Elias": ["mountain"],
        "Eklutna Lake":      ["mountain", "coastal"],
        "Lake Clark":        ["mountain", "coastal"],
        "Chugach State Park":["mountain", "general"],
    }
    if name in multi_scene:
        return multi_scene[name]

    # ── 關鍵詞自動分類 ──────────────
    scene_map = [
        (["瀑布", "溪", "五峰旗", "Falls", "Waterfall", "Creek", "River",
          "渓谷", "沢", "滝"], "waterfall"),
        (["見晴", "森林", "Forest", "Rainforest", "Woods", "Grove",
          "湿原", "湿地", "Trees", "Redwood"], "forest"),
        (["山", "峰", "湖", "嶺", "百岳", "主峰", "尖山", "大山",
          "合歡", "玉山", "雪山", "奇萊", "南湖", "大霸", "北大武",
          "池有", "桃山", "品田", "嘉明", "二延平", "頂石棹", "金龍山",
          "武界", "鳶嘴", "火炎", "雲洞", "阿里山", "杉林溪", "二寮",
          "硬漢嶺", "大屯山", "抹茶山", "觀音山", "望幽谷", "金瓜石",
          # 日本山區
          "岳", "高原", "山頂", "ロープウェイ", "青い池",
          # 國際景點（英文）— 自然地貌
          "Canyon", "Valley", "Arch", "Butte", "Mesa", "Desert", "Dunes",
          " NP", "National Park", "Mount ", "Mt. ", "Mountain",
          "Glacier", "Range", "Rocky", "Teton", "Rainier", "Denali",
          "Brooks Range", "Crater Lake", "Death Valley", "Sawtooth",
          "Hot Springs", "Pass", "State Park", "Lake", "Aurora",
          "Mendenhall", "Matanuska"], "mountain"),
        (["漁港", "碼頭", "濕地", "海", "灘", "橋", "島", "燈塔",
          "漁人", "大稻埕", "關渡", "碧潭", "王功", "香山", "永安",
          "井仔腳", "鵝鑾鼻", "關山", "三仙台", "七星潭", "粉鳥林",
          "多良", "跨海大橋", "奎壁山", "雙心", "東清灣", "青青草原",
          "花瓶岩", "芹壁", "東引", "慈湖", "大古山", "小崗山", "正濱",
          "和平島", "月世界", "駁二", "鹽田",
          # 國際海岸
          "Beach", "Coast", "Bay", "Island", "Shore", "Pier", "Harbor",
          "Spit", "Strait", "Sound", "Inlet", "Miami", "Santa Monica",
          "Bering Land", "Bridge", "Lighthouse", "Port", "Marina"], "coastal"),
        (["步道", "古道"], "forest"),
    ]

    types = []
    for keywords, scene_type in scene_map:
        for kw in keywords:
            if kw in name:
                types.append(scene_type)
                break
    if not types:
        types.append("general")
    # 去重但保持順序
    return list(dict.fromkeys(types))


def get_genre_label(scene_type, cond):
    """依天氣條件回傳中文拍攝題材說明"""
    low_cc = cond.get("low_cc", 0)
    max_cloud = cond.get("max_cloud", 0)
    rh = cond.get("rh", 50)
    wind = cond.get("wind", 10)
    high_cc = cond.get("high_cc", 0)
    t_h = cond.get("t_h", 12)
    sunrise_h = cond.get("sunrise_h", 6)
    sunset_h = cond.get("sunset_h", 18)
    wcode = cond.get("wcode", 0)
    is_golden = abs(t_h - sunrise_h) <= 1 or abs(t_h - sunset_h) <= 1

    if scene_type == "mountain":
        if low_cc > 60 and rh > 85 and wind < 15:
            return "☁️ 雲海大景"
        if is_golden and max_cloud < 30:
            return "🏔️ 金色山脈"
        if max_cloud < 30:
            return "🏔️ 晴空山景"
        if low_cc > 50:
            return "🌫️ 山巒雲霧"
        return "🏔️ 山巒層次"

    if scene_type == "coastal":
        if 30 <= high_cc <= 70 and low_cc < 20 and is_golden:
            if abs(t_h - sunset_h) <= 1:
                return "🔥 火燒雲夕陽"
            elif abs(t_h - sunrise_h) <= 1:
                return "🔥 火燒雲日出"
        if is_golden:
            return "🌅 金色海岸"
        if max_cloud < 30:
            return "🌊 碧海藍天"
        return "🌊 海岸風光"

    if scene_type == "waterfall":
        if max_cloud > 70 and wcode < 60:
            return "🌿 絲絹流水"
        if max_cloud > 50:
            return "🌿 瀑布漫射光"
        return "🌿 瀑布景觀"

    if scene_type == "forest":
        if rh > 85 and max_cloud > 50:
            return "🌲 夢幻晨霧"
        if max_cloud > 40:
            return "🌲 森林漫射光"
        return "🌲 森林浴"

    # general
    if is_golden:
        return "🌆 城市晨昏"
    if max_cloud < 30:
        return "🏙️ 晴空城市"
    if max_cloud < 60:
        return "🏙️ 城市風光"
    return "🏙️ 城市景觀"


def score_spot_for_photography(hourly, daily, spot_name):
    """
    對單一景點進行攝影評分（0-100）

    評分架構（四項合計）：
      能見度 30分  — 空氣通透度
      雲量   20分  — 依題材類型不同標準
      降雨   20分  — 降雨機率
      時段   30分  — 黃金時段 + 白天優先

    題材分類影響雲量評分標準：
      mountain  → 晴天/雲海 (低雲>60%+RH>85%=雲海高分)
      coastal   → 晴天+高雲30-70%=火燒雲
      waterfall → 陰天漫射光高分
      forest    → 陰天/晨霧高分
      general   → 通用評分
    """
    if not hourly or not daily:
        return None

    now = datetime.now(TW)
    today_str = now.strftime("%Y-%m-%d")
    tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    dayafter_str = (now + timedelta(days=2)).strftime("%Y-%m-%d")
    scene_types = classify_scene(spot_name)

    results = {}
    for day_label, target_date in [("today", today_str), ("tomorrow", tomorrow_str), ("dayafter", dayafter_str)]:
        indices = [i for i, t in enumerate(hourly["time"]) if t.startswith(target_date)]
        if not indices:
            results[day_label] = None
            continue

        # 日出日落
        sunrise = sunset = None
        if daily and "sunrise" in daily:
            for i, d in enumerate(daily["time"]):
                if d == target_date:
                    if i < len(daily.get("sunrise", [])):
                        sunrise = daily["sunrise"][i]
                    if i < len(daily.get("sunset", [])):
                        sunset = daily["sunset"][i]
                    break

        sunrise_h = int(sunrise.split("T")[1].split(":")[0]) if sunrise else 6
        sunset_h = int(sunset.split("T")[1].split(":")[0]) if sunset else 18

        # 對每種題材分別評分，取最佳題材和時段
        best_scene = scene_types[0]
        best_score = 0
        best_hour_idx = indices[0]
        best_genre = "📷 一般攝影"

        for scene_type in scene_types:
            for idx in indices:
                if idx >= len(hourly.get("visibility", [])):
                    continue
                vis = hourly["visibility"][idx] or 0
                low_cc = hourly["cloud_cover_low"][idx] or 0
                mid_cc = hourly["cloud_cover_mid"][idx] or 0
                high_cc = hourly["cloud_cover_high"][idx] or 0
                pop = hourly["precipitation_probability"][idx] or 0
                wcode = hourly["weather_code"][idx] or 0
                temp = hourly["temperature_2m"][idx] or 0
                dew = hourly["dew_point_2m"][idx] or 0
                wind = hourly["wind_speed_10m"][idx] or 0
                rh = hourly["relative_humidity_2m"][idx] or 0
                time_str = hourly["time"][idx]
                t_h = int(time_str.split("T")[1].split(":")[0]) if "T" in time_str else 0

                # 排除大雨/雷雨時段（小雨毛毛雨可以接受）
                heavy_rain_codes = (61, 63, 65, 82, 95, 96, 99)
                if wcode in heavy_rain_codes and pop > 70:
                    continue
                if wcode == 81 and pop > 85:
                    continue

                # 排除深夜時段（自然景觀型題材夜間拍不到）
                is_night = t_h < 5 or t_h >= 19
                night_exempt = {"general"}  # 只有城市/建築夜景可行
                if is_night and scene_type not in night_exempt:
                    continue

                score = 0

                # ─── ① 能見度（最高30分） ─────────────────────
                if vis > 30000:
                    score += 30
                elif vis > 20000:
                    score += 25
                elif vis > 15000:
                    score += 20
                elif vis > 10000:
                    score += 15
                elif vis > 5000:
                    score += 8
                elif vis > 2000:
                    score += 4
                else:
                    score += 1

                # ─── ② 雲量（最高20分，依題材不同標準） ─────
                max_cloud = max(low_cc, mid_cc, high_cc)

                if scene_type == "mountain":
                    if low_cc > 60 and rh > 85 and wind < 15:
                        score += 20  # 🔥 雲海絕佳
                    elif max_cloud < 30:
                        score += 18  # 晴空萬里
                    elif max_cloud < 50:
                        score += 12
                    elif low_cc > 70:
                        score += 10
                    else:
                        score += 5

                elif scene_type == "coastal":
                    if high_cc >= 30 and high_cc <= 70 and low_cc < 20:
                        score += 20  # 🔥 火燒雲
                    elif max_cloud < 30:
                        score += 18
                    elif max_cloud < 60:
                        score += 12
                    else:
                        score += 5

                elif scene_type == "waterfall":
                    if max_cloud > 70 and low_cc > 50 and wcode < 60:
                        score += 20  # ✅ 漫射光完美
                    elif max_cloud > 50:
                        score += 15
                    elif max_cloud < 20:
                        score += 8
                    else:
                        score += 12

                elif scene_type == "forest":
                    if rh > 85 and max_cloud > 50:
                        score += 20  # ✅ 晨霧夢幻
                    elif max_cloud > 40:
                        score += 15
                    elif max_cloud < 20:
                        score += 5
                    else:
                        score += 12

                else:  # general
                    if max_cloud < 30:
                        score += 20
                    elif max_cloud < 60:
                        score += 15
                    elif max_cloud < 85:
                        score += 8
                    else:
                        score += 3

                # ─── ③ 降雨機率（最高20分） ────────────────
                if pop < 10:
                    score += 20
                elif pop < 30:
                    score += 15
                elif pop < 50:
                    score += 10
                elif pop < 70:
                    score += 5
                else:
                    score += 2

                # ─── ④ 時段（最高30分：白天+黃金時段） ────
                is_night = t_h < 5 or t_h >= 19
                is_golden = abs(t_h - sunrise_h) <= 1 or abs(t_h - sunset_h) <= 1

                if is_golden:
                    score += 20
                elif not is_night:
                    score += 10
                else:
                    score += 2

                # 鏡像倒影加分
                if wind < 5 and (wcode in (51, 53, 61, 80) or rh > 85):
                    score += 5

                # 題材中文說明
                genre = get_genre_label(scene_type, {
                    "low_cc": low_cc, "max_cloud": max_cloud,
                    "rh": rh, "wind": wind, "high_cc": high_cc,
                    "t_h": t_h, "sunrise_h": sunrise_h, "sunset_h": sunset_h,
                    "wcode": wcode,
                })

                if score > best_score:
                    best_score = score
                    best_hour_idx = idx
                    best_scene = scene_type
                    best_genre = genre

        results[day_label] = {
            "score": min(best_score, 100),
            "scene_type": best_scene,
            "best_genre": best_genre if best_genre else "📷 一般攝影",
            "best_time": hourly["time"][best_hour_idx] if best_hour_idx < len(hourly["time"]) else None,
            "best_visibility": hourly["visibility"][best_hour_idx] if best_hour_idx < len(hourly.get("visibility", [])) else None,
            "best_temp": hourly["temperature_2m"][best_hour_idx] if best_hour_idx < len(hourly.get("temperature_2m", [])) else None,
            "best_pop": hourly["precipitation_probability"][best_hour_idx] if best_hour_idx < len(hourly.get("precipitation_probability", [])) else None,
            "sunrise": sunrise,
            "sunset": sunset,
        }

    return results


# ─── Flask 路 由 ────────────────────────────────────────────────

@app.route("/")
def home():
    """首頁：地區選單"""
    return render_template("home.html")


@app.route("/summary")
def summary():
    """最佳景點摘要頁，支援 ?region=xx 參數"""
    region = request.args.get("region", "tw") or "tw"
    return render_template("summary.html", region=region)


@app.route("/weather-guide")
def weather_guide():
    """天氣對策指南"""
    return render_template("weather_guide.html")


@app.route("/api/update-status")
def api_update_status():
    """回傳各區域上次/下次更新時間"""
    status_path = os.path.join(CACHE_DIR, "update_status.json")
    if os.path.exists(status_path):
        with open(status_path, "r", encoding="utf-8") as f:
            status = json.load(f)
        return jsonify(status)
    return jsonify({})


@app.route("/api/forecast")
def api_forecast():
    """回傳指定區域的天氣資料（給前端地圖用）"""
    region = request.args.get("region", "tw") or "tw"
    data = get_cached_forecast(region)
    return jsonify(data)


@app.route("/api/best-spots")
def api_best_spots():
    """回傳今日與明日最佳攝影點排名，支援 ?region=jp 參數"""
    region = request.args.get("region", "tw") or "tw"
    if region not in REGIONS:
        return jsonify({"error": f"Unknown region: {region}", "available": list(REGIONS.keys())})
    data = get_cached_forecast(region)
    now = datetime.now(TW)
    today_str = now.strftime("%Y-%m-%d")
    tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    dayafter_str = (now + timedelta(days=2)).strftime("%Y-%m-%d")
    scored = []
    for p in data["points"]:
        if p["type"] != "spot":
            continue
        hourly = p.get("hourly")
        daily = p.get("daily")
        if not hourly or not hourly.get("time"):
            continue
        try:
            s = score_spot_for_photography(hourly, daily, p.get("name", ""))
        except Exception as e:
            import traceback
            with open(os.path.join(tempfile.gettempdir(), "pw_error.log"), "a") as ef:
                ef.write(f"ERROR scoring {p.get('name')}: {e}\n")
                ef.write(traceback.format_exc() + "\n")
            continue
        if s:
            scored.append({
                "name": p["name"],
                "tip_today": weather_tip(s.get("today"), p["name"]),
                "tip_tomorrow": weather_tip(s.get("tomorrow"), p["name"]),
                "tip_dayafter": weather_tip(s.get("dayafter"), p["name"]),
                "lat": p["lat"],
                "lon": p["lon"],
                "elevation": TRUE_ELEVATIONS.get(p["name"], p.get("elevation")),
                "today": s.get("today"),
                "tomorrow": s.get("tomorrow"),
                "dayafter": s.get("dayafter"),
            })

    # 今日排名
    today_scored = [s for s in scored if s.get("today") and s["today"].get("score", 0) > 0]
    today_scored.sort(key=lambda x: x["today"]["score"], reverse=True)
    # 明日排名
    tomorrow_scored = [s for s in scored if s.get("tomorrow") and s["tomorrow"].get("score", 0) > 0]
    tomorrow_scored.sort(key=lambda x: x["tomorrow"]["score"], reverse=True)
    # 後天排名
    dayafter_scored = [s for s in scored if s.get("dayafter") and s["dayafter"].get("score", 0) > 0]
    dayafter_scored.sort(key=lambda x: x["dayafter"]["score"], reverse=True)
    print(f"DEBUG: dayafter_scored count = {len(dayafter_scored)}", flush=True)

    return jsonify({
        "generated_at": now.isoformat(),
        "today": today_scored[:30],
        "tomorrow": tomorrow_scored[:30],
        "dayafter": dayafter_scored[:30],
    })


@app.route("/api/refresh")
def api_refresh():
    """重新抓取指定區域的天氣資料（預設 tw）"""
    region = request.args.get("region", "tw") or "tw"
    import subprocess, sys as _sys
    result = subprocess.run(
        [_sys.executable, os.path.join(os.path.dirname(__file__), "build_cache.py"), region],
        capture_output=True, text=True, timeout=180,
        cwd=os.path.dirname(os.path.dirname(__file__))
    )
    return jsonify({"status": "ok" if result.returncode == 0 else "error", "region": region, "output": result.stdout[-200:]})


# ─── 啟 動 ────────────────────────────────────────────────────

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    print("""
╔══════════════════════════════════════════╗
║  📷 PhotoWeather — 攝影天氣地圖          ║
║                                          ║
║  🌐 http://localhost:5000                ║
║     → 能見度動態地圖                     ║
║  📋 http://localhost:5000/summary        ║
║     → 今日/明日最佳攝影點                ║
║                                          ║
║  🔄 資料更新：python build_cache.py      ║
╚══════════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=5000, debug=False)