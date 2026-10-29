# 任務：攝影景點代表性照片蒐集（ChaseLights V2）

你是攝影景點研究員。附件 CSV 是 111 筆攝影機會（opportunity），每筆有
opportunity_id、name_zh（中文名）、name_en（若有）、screen、status、lat/lon（座標）。

請對**每一筆**執行以下流程。全部完成前不要輸出結果。

## 步驟（每筆）

1. **搜尋景點**：以名稱（英文名優先，無英文名就用中文名＋座標所在國家）搜尋
   Google，找出這個景點實際存在的攝影題材（facets/subjects），通常 1–3 個，
   例如：湖面倒影、高處俯瞰全景、金針花季節花海、夜間點燈、星空、雲海。
   常見資料來源：官方/旅遊局網站、攝影攻略、500px、Flickr。
2. **每個題材挑 2 張具代表性照片**：
   - 用 Google 圖片搜尋「景點名（英文）+ 題材關鍵詞（英文）」
   - 「具代表性」= 清楚展示該題材的構圖特徵（如倒影要有明顯鏡面反射、
     俯瞰要有明確高視角），不要選雜湊的旅遊快照
   - 每張照片記錄**圖片直連 URL**（圖檔本身，.jpg/.jpeg/.png/.webp 結尾，
     不是 Google 圖片搜尋結果頁）與**來源頁 URL**（刊登該圖的網頁）
3. 題材名稱用英文小寫底線格式（如 `reflection`、`overlook_pano`、
   `daylily_field`、`night_illumination`、`autumn_foliage`、`cloud_sea`）

## 輸出格式

輸出一份 CSV（一行一張照片），欄位：

```
opportunity_id,subject,image_url,source_page_url
```

在最前面加一行 header。最後附一段總計說明：幾筆完成、幾筆有題材找不到照片。

## 誠實規則（最高優先）

- 某題材找不到具代表性的照片：該行 image_url 填 `not_found`，不要用
  不相干的圖湊數
- URL 必須是真實搜尋結果，不得編造或猜測 URL
- 若某景點完全搜尋不到，整筆輸出 `opportunity_id,<空>,not_found,<空>`
  並在總計說明列出
- 這份清單會被程式下載並由另一個 AI 逐張分析，URL 的正確性比數量重要

## 範圍

只處理 CSV 中 status 為「未決」或「懸置」的列（共 111 筆，全部）。
每批處理完立即輸出該批 CSV，避免一次輸出過長被截斷（建議每批 20 筆）。
輸出語言：題材名與 CSV 內容用英文，說明文字用繁體中文。
