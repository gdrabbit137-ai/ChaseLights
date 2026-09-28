# B97 — 所選日期分數／窗口文案一致化

Date: 2026-09-28 (Asia/Taipei)

## 編號更正

本工作最初在 main 上以 `B96_SELECTED_DATE_LABELS.md` 記錄，但同一時間線中，合歡山高度基準／LCL 文案修正已先正式更正為 B96（`B96_HEHUAN_ELEVATION_LCL_WORDING.md`）。

為避免兩個不同工作共用同一 batch ID，本文件正式改編為 **B97**。既有 Git commit 訊息不重寫；此後所有 handoff、規格引用與追蹤均以 B97 為準。

## 問題

B95 已讓 Opportunity 卡片顯示「每日最佳 forecast window」與信心，但部分文案仍硬寫成「今日／當日」。

當使用者切到「明天」或「後天」時，可能同時看到：

- 明天的預報資料；
- 「今日最佳窗口」；
- 「今日較適合」；
- 「當日評分」。

雖然資料本身來自所選日期，文字仍容易讓人誤以為是目前今天或目前時段。

## B97 修正

將與 day filter 綁定的文案改成明確的「所選日期」語意：

- 中文
  - 當日評分 → 所選日期最佳評分
  - 今日最佳窗口 → 所選日期最佳窗口
  - 今日較適合 → 所選日期較適合
  - 依當日最佳拍攝機會排序 → 依所選日期最佳拍攝機會排序
- 英文
  - Day score → Best score for selected date
  - Day best window → Best window for selected date
  - Best today → Best for selected date
- 日文同樣改為「選択日」語意。

## 為什麼不直接寫「目前」

Opportunity 卡片顯示的是「所選日期內的最佳 forecast score/window」，不是使用者目前所在小時的 hourly score。

因此產品上應維持四個概念分離：

1. 一般研究建議時段；
2. 所選日期最佳窗口；
3. 所選日期最佳分數；
4. 96H 時序中每一個小時的實際分數。

這樣可避免像合歡山 2026-09-29 P04：每日最佳 72（18:00–18:07），但 06:00 實際僅 36 的情境再次被文字混淆。
