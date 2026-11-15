# ChaseLights brand assets (task CL-APP-05)

案5「主峰金頂」logo 定案（owner 2026-11）— 主峰最高、兩翼遞降、右上斜照太陽、
光楔、山稜 rim light。三層山體漸層疊色（#FDE9BE→#F3F6FA→#5A6A85 ＋ 金頂
#FDE68A→#F59E0B ＋ rim light 稜線）疊出「被照到」的雪山。

## 檔案
- `brand-512.svg` — 完整品牌圖（512 viewBox，圓角 96 方形底），favicon / Play Store / 各處通用。
- `icon-background.svg` — Android adaptive icon 背景層（108 viewBox，深底漸層）。
- `icon-foreground.svg` — Android adaptive icon 前景層（108 viewBox；安全區 66dp 內）。
- `icon-monochrome.svg` — Android adaptive icon monochrome（通知長按）層，currentColor。

## 授權 / 版權
- 版權 Copyright (c) ChaseLights project — 本 logo 為專案純手繪向量原創
  （Lucide 或任何第三方 icon 集皆未用於此 logo），授權隨專案整體發布。
- `@resvg/resvg-js`（devDependency，僅本機/CI 產生 PNG 光柵）為 ISC 授權，
  不隨 APP 散布，亦未嵌入任何產出的 PNG 內容。

## 產生光柵
`node scripts/gen-brand-assets.mjs`（apps/mobile 內執行）——產出 Android mipmap
全套、favicon PNG、Play Store 512 icon。改 SVG 後重跑即可。
