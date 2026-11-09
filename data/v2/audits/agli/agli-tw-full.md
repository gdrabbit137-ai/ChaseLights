# AGLI 台灣全量對帳（93 景點）最終版 — CL-DATA-47

方法：agli-method.md（8 維 100 分錨點制）。本檔為 batch1/45＋batch2/46＋pilot/44 之合併收尾。
重疊 8 景點中 7 處 AGli 差 >5 已重評（tw-027、tw-030、tw-031、tw-032、tw-033、tw-037、tw-042），缺口 12 景點已補評（tw-060、tw-073、tw-076、tw-082、tw-083、tw-084、tw-087、tw-089、tw-091、tw-094、tw-095、tw-098）。
L1 採 agli-tw-l1.json spot_level 權威映射（修正 5 處批次內映射差）。

## 分帶與信心
{"90+": 0, "80-89": 3, "70-79": 11, "60-69": 19, "50-59": 33, "40-49": 19, "<40": 8}
{"high": 37, "medium": 26, "low": 30}
0 個 90+（錨點紀律：無全球同型比較對象不給 95+）。

## Top 10

| # | id | 景點 | AGli | L1 | 信心 |
|---|-----|------|------|-----|------|
| 1 | tw-046 | 大霸尖山 | 83.1 | C2 | high |
| 2 | tw-045 | 嘉明湖 | 82.8 | B3 | high |
| 3 | tw-040 | 玉山主峰 | 81.7 | C4 | medium |
| 4 | tw-034 | 崇德 | 77.3 | C1 | low |
| 5 | tw-074 | 野柳地質公園 | 77.3 | A1 | medium |
| 6 | tw-019 | 合歡山主峰 | 76.4 | C3 | medium |
| 7 | tw-043 | 奇萊主峰 | 75.6 | C1 | medium |
| 8 | tw-069 | 蘭嶼東清灣 | 75.4 | F2 | high |
| 9 | tw-044 | 南湖大山 | 74.2 | C1 | medium |
| 10 | tw-041 | 雪山主峰 | 72.2 | C2 | high |

## 與 scenic-v3 對照
- 有 v3 對照值 88/93；Pearson r(v3×10, AGLI)=0.657，平均差 22.72 分。
- 主要位移（v3 高估的多為人氣但地形平淡的點，如關山/多良/抹茶山；v3 低估的為惡地/石滬類稀缺型地景）：
  - tw-071 小琉球花瓶岩: AGLI 64.2 vs v3×10 0
  - tw-080 帆船鼻大草原／海岬: AGLI 63.6 vs v3×10 0
  - tw-085 南子吝步道: AGLI 54.5 vs v3×10 0
  - tw-091 司馬庫斯部落觀景點: AGLI 52.8 vs v3×10 0
  - tw-034 崇德: AGLI 77.3 vs v3×10 30
  - tw-023 頂石棹: AGLI 44.2 vs v3×10 0

## 分區（L1）頂點

- A1 北海岸／東北角海岸線: tw-074 AGli 77.3
- A2 大台北都會河港帶（含桃園平原）: tw-004 AGli 53.2
- A3 桃竹苗丘陵海岸: tw-013 AGli 58.0
- B1 高屏平原／港區／惡地: tw-027 AGli 58.1
- B2 西海岸濕地帶: tw-015 AGli 65.5
- B3 南橫／嘉明湖山塊: tw-045 AGli 82.8
- B4 墾丁／恆春半島: tw-080 AGli 63.6
- B5 雲嘉南濱海與丘陵: tw-026 AGli 53.0
- C1 中央山脈北段（太魯閣／奇萊／南湖）: tw-034 AGli 77.3
- C2 雪山山塊: tw-046 AGli 83.1
- C3 合歡山塊與濁水溪源: tw-019 AGli 76.4
- C4 玉山山塊: tw-040 AGli 81.7
- C5 阿里山／中海拔森林帶: tw-053 AGli 59.6
- D1 宜蘭山區與湖泊: tw-056 AGli 62.6
- D2 花東縱谷: tw-039 AGli 57.9
- E1 蘇花／花蓮海岸: tw-077 AGli 68.0
- E2 台東海岸: tw-038 AGli 58.8
- F1 澎湖群島: tw-079 AGli 70.5
- F2 綠島／蘭嶼: tw-069 AGli 75.4
- F3 馬祖列島: tw-067 AGli 70.9
- F4 金門: tw-062 AGli 62.4

## 完整排名（93）

| # | id | 景點 | AGli | L1 | L1內 | 信心 | 來源 |
|---|-----|------|------|-----|------|------|------|
| 1 | tw-046 | 大霸尖山 | 83.1 | C2 | 1 | high | pilot-reuse |
| 2 | tw-045 | 嘉明湖 | 82.8 | B3 | 1 | high | pilot-reuse |
| 3 | tw-040 | 玉山主峰 | 81.7 | C4 | 1 | medium | pilot-reuse |
| 4 | tw-034 | 崇德 | 77.3 | C1 | 1 | low | pilot-reuse |
| 5 | tw-074 | 野柳地質公園 | 77.3 | A1 | 1 | medium | pilot-reuse |
| 6 | tw-019 | 合歡山主峰 | 76.4 | C3 | 1 | medium | pilot-reuse |
| 7 | tw-043 | 奇萊主峰 | 75.6 | C1 | 2 | medium | pilot-reuse |
| 8 | tw-069 | 蘭嶼東清灣 | 75.4 | F2 | 1 | high | pilot-reuse |
| 9 | tw-044 | 南湖大山 | 74.2 | C1 | 3 | medium | pilot-reuse |
| 10 | tw-041 | 雪山主峰 | 72.2 | C2 | 2 | high | batch1 |
| 11 | tw-067 | 北竿芹壁 | 70.9 | F3 | 1 | medium | pilot-reuse |
| 12 | tw-072 | 南雅奇岩 | 70.5 | A1 | 2 | low | batch2 |
| 13 | tw-079 | 池西柱狀玄武岩／池西岩瀑九孔池 | 70.5 | F1 | 1 | low | batch2 |
| 14 | tw-050 | 品田山 | 70.1 | C2 | 3 | low | batch2 |
| 15 | tw-077 | 石梯坪海蝕平台／壺穴群 | 68.0 | E1 | 1 | low | batch2 |
| 16 | tw-048 | 池有山 | 67.3 | C2 | 4 | low | batch2 |
| 17 | tw-070 | 蘭嶼青青草原 | 66.5 | F2 | 2 | low | batch2 |
| 18 | tw-047 | 北大武山 | 66.4 | B3 | 2 | low | batch2 |
| 19 | tw-042 | 雪山北峰 | 65.6 | C2 | 5 | high | re-eval-47 |
| 20 | tw-015 | 高美濕地 | 65.5 | B2 | 1 | high | pilot-reuse |
| 21 | tw-066 | 東引燈塔 | 65.4 | F3 | 2 | low | batch2 |
| 22 | tw-071 | 小琉球花瓶岩 | 64.2 | F2 | 3 | low | batch2 |
| 23 | tw-080 | 帆船鼻大草原／海岬 | 63.6 | B4 | 1 | low | batch2 |
| 24 | tw-049 | 桃山 | 63.2 | C2 | 6 | low | batch2 |
| 25 | tw-056 | 松蘿湖 | 62.6 | D1 | 1 | low | batch2 |
| 26 | tw-062 | 金門得月樓 | 62.4 | F4 | 1 | low | batch2 |
| 27 | tw-065 | 馬祖南竿 | 61.9 | F3 | 3 | low | batch2 |
| 28 | tw-057 | 加羅湖 | 61.2 | D1 | 2 | low | batch2 |
| 29 | tw-088 | 翠峰湖環山步道觀景點 | 61.1 | D1 | 3 | medium | pilot-reuse |
| 30 | tw-059 | 奎壁山 | 60.9 | F1 | 2 | medium | batch2 |
| 31 | tw-068 | 綠島朝日溫泉 | 60.8 | F2 | 4 | low | pilot-reuse |
| 32 | tw-078 | 建功嶼／退潮石板道 | 60.8 | F1 | 3 | medium | batch2 |
| 33 | tw-095 | 塔塔加夫妻樹／鹿林山觀景點 | 60.2 | C4 | 2 | high | gap-fill-47 |
| 34 | tw-053 | 杉林溪 | 59.6 | C5 | 1 | low | batch2 |
| 35 | tw-081 | 南竿鐵堡／海防礁岩 | 59.1 | F3 | 4 | low | batch2 |
| 36 | tw-064 | 金門慈湖 | 59.0 | F4 | 2 | low | batch2 |
| 37 | tw-076 | 龍磐公園／草原海岸 | 59.0 | B4 | 2 | high | gap-fill-47 |
| 38 | tw-029 | 鵝鑾鼻燈塔 | 58.8 | B4 | 3 | high | pilot-reuse |
| 39 | tw-038 | 三仙台 | 58.8 | E2 | 1 | high | batch1 |
| 40 | tw-075 | 外澳沙灘／龜山朝日 | 58.6 | A1 | 3 | low | batch2 |
| 41 | tw-027 | 田寮月世界 | 58.1 | B1 | 1 | high | re-eval-47 |
| 42 | tw-054 | 正濱漁港 | 58.1 | A1 | 4 | low | batch2 |
| 43 | tw-013 | 火炎山 | 58.0 | A3 | 1 | high | batch1 |
| 44 | tw-039 | 池上伯朗大道 | 57.9 | D2 | 1 | high | pilot-reuse |
| 45 | tw-055 | 五峰旗瀑布 | 57.4 | A1 | 5 | low | batch2 |
| 46 | tw-093 | 福壽山農場觀景點 | 57.4 | C3 | 2 | low | batch2 |
| 47 | tw-018 | 日月潭・水社壩湖景步道 | 56.8 | D2 | 2 | high | batch1 |
| 48 | tw-060 | 七美雙心石滬 | 56.0 | F1 | 4 | high | gap-fill-47 |
| 49 | tw-061 | 澎湖觀音亭 | 55.8 | F1 | 5 | low | batch2 |
| 50 | tw-010 | 和平島 | 55.3 | A1 | 6 | high | batch1 |
| 51 | tw-024 | 阿里山祝山觀日平台 | 54.7 | C5 | 2 | high | batch1 |
| 52 | tw-085 | 南子吝步道 | 54.5 | A1 | 7 | low | batch2 |
| 53 | tw-094 | 東莒燈塔（東犬燈塔） | 54.2 | F3 | 5 | high | gap-fill-47 |
| 54 | tw-035 | 六十石山 | 53.4 | D2 | 3 | high | batch1 |
| 55 | tw-004 | 不厭亭 | 53.2 | A2 | 1 | high | batch1 |
| 56 | tw-073 | 老梅綠石槽 | 53.2 | A1 | 8 | high | gap-fill-47 |
| 57 | tw-026 | 井仔腳瓦盤鹽田 | 53.0 | B5 | 1 | high | batch1 |
| 58 | tw-058 | 澎湖跨海大橋 | 52.9 | F1 | 6 | low | batch2 |
| 59 | tw-091 | 司馬庫斯部落觀景點 | 52.8 | C2 | 7 | medium | gap-fill-47 |
| 60 | tw-036 | 七星潭 | 52.1 | E1 | 2 | high | batch1 |
| 61 | tw-089 | 觀霧榛山步道觀景點 | 51.9 | C2 | 8 | medium | gap-fill-47 |
| 62 | tw-016 | 鳶嘴山 | 51.8 | C2 | 9 | high | batch1 |
| 63 | tw-022 | 二延平步道鋼構觀景平台 | 51.8 | C5 | 3 | high | batch1 |
| 64 | tw-087 | 大雪山森林遊樂區43K觀景台 | 51.0 | C2 | 10 | medium | gap-fill-47 |
| 65 | tw-002 | 象山六巨石攝影平台 | 50.4 | A2 | 2 | high | batch1 |
| 66 | tw-007 | 碧潭 | 50.1 | A2 | 3 | medium | pilot-reuse |
| 67 | tw-033 | 粉鳥林 | 49.9 | D1 | 4 | high | re-eval-47 |
| 68 | tw-030 | 屏東關山 | 49.7 | B4 | 4 | medium | re-eval-47 |
| 69 | tw-025 | 二寮觀日亭 | 49.4 | B5 | 2 | medium | batch1 |
| 70 | tw-098 | 渭水之丘／櫻花陵園 | 49.4 | D1 | 5 | medium | gap-fill-47 |
| 71 | tw-031 | 抹茶山（聖母山莊／三角崙） | 48.5 | D1 | 6 | high | re-eval-47 |
| 72 | tw-003 | 淡水漁人碼頭 | 48.4 | A2 | 4 | medium | pilot-reuse |
| 73 | tw-037 | 多良火車站觀景台 | 48.0 | E2 | 2 | high | re-eval-47 |
| 74 | tw-028 | 駁二藝術特區 | 47.8 | B1 | 2 | high | pilot-reuse |
| 75 | tw-021 | 武界部落 | 47.2 | C3 | 3 | high | batch1 |
| 76 | tw-032 | 見晴懷古步道 | 46.5 | D1 | 7 | low | re-eval-47 |
| 77 | tw-005 | 大稻埕碼頭 | 46.1 | A2 | 5 | high | batch1 |
| 78 | tw-009 | 望幽谷 | 45.7 | A1 | 9 | medium | batch1 |
| 79 | tw-051 | 大古山 | 45.6 | A2 | 6 | low | batch2 |
| 80 | tw-012 | 香山濕地賞蟹步道 | 45.2 | B2 | 2 | high | batch1 |
| 81 | tw-023 | 頂石棹 | 44.2 | C5 | 4 | medium | batch1 |
| 82 | tw-082 | 鯉魚潭 | 44.2 | E1 | 3 | high | gap-fill-47 |
| 83 | tw-008 | 觀音山硬漢嶺 | 44.0 | A2 | 7 | medium | batch1 |
| 84 | tw-017 | 王功漁港 | 42.7 | B2 | 3 | high | batch1 |
| 85 | tw-020 | 金龍山 | 42.5 | D2 | 4 | high | batch1 |
| 86 | tw-083 | 雲山水夢幻湖 | 39.9 | D2 | 5 | medium | gap-fill-47 |
| 87 | tw-052 | 小崗山雲臺 | 39.4 | B1 | 3 | medium | pilot-reuse |
| 88 | tw-014 | 雲洞山莊 | 39.3 | C3 | 4 | medium | batch1 |
| 89 | tw-006 | 關渡大橋 | 36.9 | A2 | 8 | medium | batch1 |
| 90 | tw-001 | 大屯山助航站 | 35.1 | A1 | 10 | medium | batch1 |
| 91 | tw-086 | 八里崁頭里・淡江大橋觀景點 | 32.0 | A2 | 9 | low | pilot-reuse |
| 92 | tw-011 | 永安漁港 | 31.6 | A3 | 2 | high | batch1 |
| 93 | tw-084 | 大農大富平地森林園區 | 31.6 | D2 | 6 | medium | gap-fill-47 |
