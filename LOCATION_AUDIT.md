# ChaseLights V5.2 Location Audit

## What changed

- Navigation and weather coordinates are now separated conceptually from broad-area names.
- `regions.py` has an explicit `SPOT_OVERRIDES` layer with named POI / viewpoint / camera-position corrections.
- Google Maps navigation prefers `map_query` (named POI) and falls back to raw coordinates only when necessary.
- Exact duplicate coordinates were checked within Taiwan, Japan, and the United States: none remain.
- All coordinates pass valid WGS84 latitude / longitude bounds.

## Coverage after V5.2 audit

- Taiwan: 71 spots; 61 high-confidence, 10 medium-confidence coordinate targets.
- Japan: 35 spots; 31 high-confidence, 4 medium-confidence coordinate targets.
- United States: 70 spots; 41 high-confidence, 26 medium-confidence, 3 low-confidence broad regional points.

The remaining low-confidence US entries are very large natural areas rather than a single built POI:
- Yukon River
- Noatak River
- Lake Clark National Park

Their navigation still uses a named Google Maps query rather than relying only on the broad coordinate.

## Key Taiwan corrections

- 不厭亭 → direct photography/viewpoint GPS around `25.08923, 121.84752`; removed Coast scene and Long Exposure theme.
- 觀音山硬漢嶺 → official tourism viewpoint coordinate.
- 香山濕地 → crab-boardwalk / tourism POI coordinate.
- 高美濕地 → boardwalk / camera area coordinate.
- 鳶嘴山 → summit rock-ridge camera point.
- 日月潭 → representative named lookout rather than generic lake centroid.
- 二延平 → actual viewing platform.
- 阿里山 → Zhushan sunrise platform rather than broad Alishan centroid.
- 二寮 → sunrise pavilion/viewpoint coordinate.
- 井仔腳 → official salt-field POI.
- 鵝鑾鼻 → official lighthouse POI.
- 清水斷崖 → Chongde overlook.
- 七星潭 → Crescent Bay camera area.
- 多良 → station viewpoint.
- 三仙台 / 伯朗大道 / 正濱漁港 / 奎壁山 / 雙心石滬 / 慈湖 / 東引燈塔 / 芹壁 / 青青草原 / 花瓶岩 → corrected POI or camera-point coordinates.

## Theme correction

`coast` no longer automatically receives `long_exposure`. Long Exposure is now reserved for river/waterfall locations or explicitly reviewed coastal locations where long-exposure water photography is actually meaningful.
