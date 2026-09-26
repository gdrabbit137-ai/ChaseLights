# B39 Final High-Risk Evidence Audit

B39 completes the remaining high-risk Opportunity provenance review.

## Final audit result

- total Opportunities: 251
- documented high-risk: 61
- narrow_scope: 9
- insufficient_evidence: 6
- remove_or_rewrite: 0
- review_required: 0
- lower-risk legacy: 175

This means every currently detected high-risk Opportunity is now explicitly classified.

## Final batch highlights

### Verified — event

- tw-002-P03 象山六巨石／攝影平台 台北101跨年煙火
  - Taipei City official guidance explicitly recommends 六巨石、攝影平台等象山 points for 101 fireworks.

### Verified — snow / ice

- tw-019-P06 合歡主峰雪覆山稜
- tw-040-P03 玉山主峰雪覆岩稜
- tw-041-P05 雪山一號圈谷冬季雪景

### Narrow scope — snow / ice

- tw-044-P03 南湖圈谷霧淞／雪景
  - official evidence directly verifies winter snow cover
  - current evidence does not independently verify rime (霧淞)
  - therefore snow is valid but the combined claim remains narrow_scope

### Verified — Liushishishan seasonal subjects

- tw-035-P01 六十石山花東縱谷層巒＋季節花田
- tw-035-P02 六十石山午後雲隙光＋縱谷／花田
- tw-035-P07 黃花亭金針花田與山景
- tw-035-P08 小瑞士金針花坡與丘陵曲線
- tw-035-P10 鹿蔥亭金針花丘陵與縱谷層次

Notably, P02 is now supported by direct official evidence: the official live-camera page explicitly lists the best crepuscular-ray window and the official album calls it a signature Liushishishan scene. This is no longer a terrain/weather inference.

### Verified — waterfalls

- tw-053-P01 杉林溪松瀧岩瀑布＋水濂洞
- tw-053-P02 杉林溪青龍瀑布＋森林水景
- tw-055-P01 五峰旗中層瀑布＋山谷

For tw-053-P02, mist was an audit false positive caused by secondary wording. The registry now overrides the risk class to waterfall only.

### Verified — wildlife / fireflies

- tw-064-P01 金門慈湖冬候鳥
- tw-082-P04 鯉魚潭春季螢火蟲
- tw-082-P05 鯉魚潭鳥類／水鳥／自然生態
- tw-084-P05 大農大富春季螢火蟲
- tw-084-P07 大農大富鳥類／森林野生動物

Presence remains explicitly non-forecastable where appropriate. Weather may affect observation conditions, but it does not guarantee an animal will appear.

### Verified — seasonal flora

- tw-084-P04 大農大富春節季節花海
- Liushishishan P01/P07/P08/P10 as above

Season/month information is not itself proof of bloom. Official flower evidence establishes the subject; annual flower condition still requires current official updates.

## Project-wide evidence boundary

The final classification does not mean every high-risk Opportunity is fully certified at identical precision.

- `documented`: claim is supported at current scope.
- `narrow_scope`: evidence supports only part of the current claim or a broader area than the current Camera Zone/composition.
- `insufficient_evidence`: current evidence is not strong enough to certify the claim.
- `remove_or_rewrite`: reserved for contradicted or materially unsupported claims requiring product change.
- `review_required`: unreviewed queue. Final count is now zero.

## Next enforcement step

With the legacy high-risk backlog classified, CI can next move from discovery-only mode toward:

1. rejecting newly added high-risk Opportunities without evidence-registry provenance;
2. preventing `insufficient_evidence` claims from being promoted to stronger runtime certainty;
3. requiring explicit review when a high-risk Opportunity changes subject scope, Camera Zone, or composition semantics.
