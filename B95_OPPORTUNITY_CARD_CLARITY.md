# B95 — Opportunity 卡片顯示當日最佳窗口與信心

## 問題

Place 詳細視窗的 Opportunity 卡片原本同時顯示：

- 「當日評分」
- 研究階段的通用「適合時間」

但沒有顯示產生這個「當日評分」的實際 forecast window，也沒有顯示 `score_confidence`。

這會讓使用者把一天之中的最佳分數誤解成目前時段的狀態。例如 B94 後，合歡山主峰 `tw-019-P04` 的 2026-09-29 當日雲海分數為 72，但真正的最佳窗口是 18:00–18:07；06:00 的同一 Opportunity 實際只有 36，而且 spatial runtime 判定 lower-cloud evidence 未成立。

## B95 UI

每張有當日分數的 Opportunity 卡片新增：

- 「今日最佳窗口」：直接使用該 Opportunity 的 `window_start/window_end/timezone_abbr`。
- 「信心」：顯示 `score_confidence`（高 / 中 / 低）。

保留原有：

- 「適合時間」：研究資料中的一般拍攝時段。
- 「當日評分」：選定日期內該 Opportunity 的最佳 forecast score。

因此產品語意變成：

1. 研究上通常什麼時段適合；
2. 今天實際是哪個 forecast window 得到這個分數；
3. 這個判斷的信心水準。

## 合歡山例子

2026-09-29 最新 production weather refresh：

- `tw-019-P03` 360° 群峰全景：93，高信心，最佳窗口 06:00–15:00。
- `tw-019-P04` 主峰下方雲海：72，中信心，最佳窗口 18:00–18:07。
- 06:00 的 P04 並沒有 lower-cloud spatial evidence，因此只有 36，狀態是專屬條件未符合。

B95 讓使用者不必進入 96H 時序頁面才能理解上述差異。
