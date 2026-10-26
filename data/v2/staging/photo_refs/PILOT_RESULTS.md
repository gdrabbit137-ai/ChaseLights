# mountain_view triage 試點報告 — 照片證據分析（2026-10-26）

照片來源：Wikimedia Commons（授權明確、來源頁可查）。22 張分析、10 筆機會。
清單：`_manifest.csv`（檔名 ↔ Commons 來源頁）。照片存於本目錄。

## 逐筆結論

| 機會 | 照片證據 | 建議裁定 | 條件提案 |
|---|---|---|---|
| tw-035-P01 六十石山 | 金針花海全景＋縱谷層巒（01/02/03/04）；04 有日落斜射光＋裂雲 | B:seasonal_plant+mountain_view | seasonal: 季節窗＋precip<0.2＋wind<5（沿用已審）；mountain_view: low cloud<=30＋visibility>=20；日落變體：sunset 模板（裂雲 30–70%） |
| tw-035-P07 黃花亭 | 金針花田坡面＋產業道路＋縱谷（22） | B:seasonal_plant+mountain_view | 同上 |
| us-010 Grand Prismatic Overlook | 兩張均為 overlook trail 高點俯瞰彩色地熱池（06 柔光／21 晴空＋蒸汽） | B:overlook | 沿用已審 overlook 門檻：low cloud<=30、visibility>=min(24km,場域上限)；蒸汽為現場條件不影響評分 |
| us-002 馬蹄灣 | 07 黃金時刻暖光＋月出；08 白天全景（高能見度）；09 日落逆光薄霧 | B:overlook（日落變體成立） | overlook 門檻＋sunset 變體：cloud 30–70% 裂雲、日落方位對位（午後光打亮峽谷壁） |
| jp-002 姿見池・旭岳 | 10/11：火山山體＋噴氣＋高山池；**池面僅映天空，倒影證據弱** | B:mountain_view（reflection 降為 [uncertain] 次要） | mountain_view 門檻；倒影若保留需 wind<3 [provisional] |
| jp-009 中瀬沼・磐梯山 | 12 為橋樑照片（題材不符，證據無效）；13 為山頂俯瞰湖沼平原 | B:mountain_view（reflection 證據不足，round-2 補圖） | mountain_view 門檻 |
| us-013 Crater Lake Rim Village | 15 為經典 rim 全景：Wizard Island＋湖面倒影清晰；14 僅樹隙局部（弱） | B:overlook（+reflection 次要，倒影證據明確） | overlook 門檻；倒影變體 wind<3 [provisional] |
| jp-006 摩周湖第一展望台 | 16：展望台高點俯瞰藍湖＋霧島，能見度佳 | B:overlook | overlook 門檻；**visibility>=20km 為關鍵門檻**（摩周霧/海霧頻繁，藍湖色依賴能見度） |
| tw-020 金龍山 | 18：霧霾中的層疊山巒（層次感證據）；17b：冬季晴天層巒；17 為林道照片（無效） | B:mountain_view（sunrise 變體 [uncertain]，照片均日間） | mountain_view 門檻；visibility>=15（霾害直接破壞層次） |
| us-027 Redfish Lake 北岸 | 19 空拍湖＋Sawtooth 峰群（無倒影）；20 海灘風面湖（水面皺） | B:mountain_view（reflection 需靜風：wind<2 [provisional]） | mountain_view 門檻；倒影變體 wind<2 |

## 跨筆觀察（可校訂模板門檻）

1. **倒影的風速門檻有照片證據支持**：us-027-20 風面湖無倒影 vs us-013-15 靜水鏡面 → reflection 題材 wind 門檻應設在 ~2–3 m/s，比通用 5 m/s 嚴
2. **overlook 的能見度門檻在不同地景差異大**：Crater Lake/摩周湖屬「遠眺藍色水體」，能見度是主判據；Grand Prismatic 主體在近景，能見度次要 → 建議 overlook 模板後續允許 per-opportunity 覆寫 visibility 權重
3. **日落/黃金時刻變體常與 overlook 併掛**（馬蹄灣、六十石山）→ 模板 merge 機制已支援，屬正常用法
4. **Commons 檢索命中率**：10/10 筆至少 1 張有效證據；2 張題材不符（橋樑、林道）、2 張倒影證據弱 → 每筆 2 張的達成率約 82%，不符的會在報告標 not_found 不硬湊

## 方法備註
- 搜尋：Commons API 文字搜尋＋座標 geo 搜尋，1600px 縮圖下載（授權合規）
- 分析：每張親自視覺判讀（視角/主體/光線/季節/倒影元素）
- 限流：Wikimedia 對連續下載 429，已用間隔重試解決；全量 111 筆估需 2–3 小時批次作業
