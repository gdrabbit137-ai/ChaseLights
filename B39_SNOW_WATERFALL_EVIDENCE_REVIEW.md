# B39 Snow / Ice / Waterfall Evidence Review

## Snow / ice

### Verified — Grade A
- tw-019-P06 合歡主峰雪覆山稜
- tw-040-P03 玉山主峰雪覆岩稜
- tw-041-P05 雪山一號圈谷冬季雪景

這三項都有官方資料直接描述指定 Place 的冬季雪景；不是因為高海拔或冬季低溫而推導。

### Narrow scope — Grade A
- tw-044-P03 南湖圈谷霧淞／雪景

太魯閣官方可直接證明南湖山區／圈谷冬季常有白雪覆蓋，雪景成立；但目前沒有同等直接證據把「霧淞」精確鎖定南湖圈谷，因此保留 narrow_scope。

## Waterfall

### Verified — Grade A
- tw-053-P01 杉林溪松瀧岩瀑布＋水濂洞水景
- tw-053-P02 杉林溪青龍瀑布＋森林水景
- tw-055-P01 五峰旗中層瀑布＋山谷

三者都有官方景點級資料直接描述瀑布本體、可視場域與景觀組合。

## Audit correction

tw-053-P02 原本因資料中的「山嵐」字樣同時被分類為 mist + waterfall。
但核心 subject 是青龍瀑布＋森林水景；山嵐只是環境描述，不是獨立 admission claim。

因此 B39 使用：
`risk_override: ["waterfall"]`

規則：
- 有瀑布地形 ≠ 自動建立瀑布攝影 Opportunity。
- 降雨／高水量只能影響瀑布品質，不能證明題材存在。
- 雪景必須有 Place-specific evidence；高海拔＋低溫本身不夠。
- 雪景證據不能自動證明霧淞。
