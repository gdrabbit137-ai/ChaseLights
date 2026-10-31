#!/usr/bin/env python3
"""Export the full place/opportunity catalog to a trilingual-ready Excel workbook.

Purpose (owner directive 2026-10-31): every time places/opportunities are added
or removed, produce an xlsx containing ALL places' labels and every subject's
shooting conditions — colloquial rationale AND numeric thresholds — with one
sheet per country.

Sheets:
  總覽      — generation info + per-country counts
  景點清單  — one row per place: id, names, subject count, genre labels
  台灣/日本/美國 — one row per condition (place × opportunity × condition)

Usage:
  python data/v2/tools/export_catalog_xlsx.py [--out exports/catalog_YYYYMMDD.xlsx]

Data sources (regenerate before running if canonical data changed):
  apps/web-v2/catalog.v2.json            — places + opportunities
  apps/web-v2/opportunity-contracts.json — conditions (metric/role/threshold/rationale_i18n)
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[3]

# trilingual genre labels (mirror of assets/app.js V2_GENRES)
GENRES = {
    'mountain_view': ('山景視野', 'Mountain view', '山の眺望'),
    'overlook': ('制高點展望', 'Overlook', '高所展望'),
    'reflection': ('水面倒影', 'Water reflection', '水面反射'),
    'cloud_sea': ('雲海', 'Sea of clouds', '雲海'),
    'sunrise': ('日出', 'Sunrise', '日の出'),
    'sunset': ('日落夕景', 'Sunset', '夕景'),
    'golden_hour': ('黃金時刻', 'Golden hour', 'ゴールデンアワー'),
    'blue_hour_city': ('城市藍調', 'City blue hour', '都市ブルーアワー'),
    'overcast_soft': ('陰天柔光', 'Overcast soft light', '曇天ソフトライト'),
    'city_night': ('城市夜景', 'City night', '都市夜景'),
    'night_sky': ('夜空星空', 'Night sky', '星空'),
    'seasonal_plant': ('季節植物', 'Seasonal flora', '季節の植物'),
    'geological_landform': ('地質地景', 'Geological landform', '地形・地質'),
    'waterfall': ('瀑布', 'Waterfall', '滝'),
}

# trilingual metric labels (mirror of assets/app.js V2_EVAL_METRICS)
METRICS = {
    'cloud_cover_low': ('低雲', 'Low cloud', '下層雲'),
    'cloud_cover_mid': ('中雲', 'Mid cloud', '中層雲'),
    'cloud_cover_high': ('高雲', 'High cloud', '上層雲'),
    'cloud_cover_mid_and_high': ('中高雲', 'Mid & high cloud', '中上層雲'),
    'cloud_cover_total': ('總雲量', 'Total cloud', '全雲量'),
    'wind_speed_10m': ('風速', 'Wind', '風速'),
    'wind_speed_850hpa': ('850hPa風速', 'Wind 850hPa', '850hPa風速'),
    'precipitation': ('降水', 'Precipitation', '降水'),
    'aod_550nm': ('氣膠光學厚度', 'AOD 550nm', 'エアロゾル光学的厚さ'),
    'visibility': ('能見度', 'Visibility', '視程'),
    'relative_humidity_2m': ('相對濕度', 'Rel. humidity', '相対湿度'),
    'relative_humidity_925hpa': ('相對濕度925hPa', 'RH 925hPa', '相対湿度925hPa'),
    'relative_humidity_850hpa': ('相對濕度850hPa', 'RH 850hPa', '相対湿度850hPa'),
    'lcl_height_m_agl': ('抬升凝結高度', 'LCL height', 'LCL高度'),
    'temperature_delta_850_925_c': ('T850−T925溫差', 'T850−T925 delta', 'T850−T925温度差'),
    'sunrise_time_window': ('日出時段', 'Sunrise window', '日の出時間帯'),
    'sunset_window': ('日落時段', 'Sunset window', '日の入り時間帯'),
    'golden_hour_window': ('黃金時段', 'Golden hour', 'ゴールデンアワー'),
    'blue_hour_window': ('藍調時段', 'Blue hour', 'ブルーアワー'),
    'astronomical_darkness': ('天文黑暗', 'Astronomical darkness', '天文学的薄明'),
    'moon_illumination_fraction': ('月照亮百分比', 'Moon illumination', '月照亮率'),
    'moon_altitude': ('月亮高度', 'Moon altitude', '月高度'),
    'moon_target_separation_deg': ('月目標角距', 'Moon separation', '月角距離'),
    'moon_illuminance_proxy': ('月光照度代理', 'Moon illuminance proxy', '月光照度プロキシ'),
    'galactic_core_altitude': ('銀河核心高度', 'Galactic core altitude', '銀河中心高度'),
    'water_surface_state': ('水面狀態', 'Water surface state', '水面状態'),
    'seasonal_state': ('季節狀態', 'Seasonal state', '季節状態'),
    'landform_present': ('地形地貌存在', 'Landform presence', '地形の存在'),
    'river_flow_state': ('河川流量狀態', 'River flow state', '河川流量状態'),
}

ROLES = {'REQUIRED': '成立條件', 'QUALITY': '加分條件', 'BLOCKER': '不利條件'}
OP_SYMBOL = {'lte': '≤', 'gte': '≥', 'lt': '<', 'gt': '>'}

COUNTRY_SHEETS = {
    'tw': ('台灣',),
    'jp': ('日本',),
    'us': ('美國（含阿拉斯加）',),
    'ak': ('美國（含阿拉斯加）',),
}

TH = ('景點ID', '景點名稱', '題材ID', '題材名稱', '題材類別', '條件分類',
      '條件指標', '數值化條件', '口語化說明')
PH = ('景點ID', '名稱', '英文名稱', '日文名稱', '題材數', '題材類別標籤')


def fmt_threshold(cond) -> str:
    op, th = cond.get('operator'), cond.get('threshold')
    unit = cond.get('unit') or ''
    suffix = f' {unit}' if unit else ''
    if th is None:
        return '（宣告型，無數值門檻）' if op in (None, 'none') else '—'
    if op == 'between' and isinstance(th, list):
        return f'{th[0]}–{th[1]}{suffix}'
    sym = OP_SYMBOL.get(op, '=')
    return f'{sym} {th}{suffix}'


def label3(table, key) -> tuple[str, str, str]:
    tri = table.get(key)
    return tri if tri else (key, key, key)


def style_header(ws, ncols, fill='2F4F6F'):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor=fill)
        cell.alignment = Alignment(vertical='center')
    ws.freeze_panes = 'A2'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    catalog = json.loads((ROOT / 'apps/web-v2/catalog.v2.json').read_text(encoding='utf-8'))
    contracts = json.loads((ROOT / 'apps/web-v2/opportunity-contracts.json').read_text(encoding='utf-8'))
    con_map = contracts['opportunities']

    places = {p['place_id']: p for p in catalog['places']}
    opps_by_place: dict[str, list[dict]] = {}
    for o in catalog['opportunities']:
        opps_by_place.setdefault(o['place_id'], []).append(o)

    today = datetime.date.today().isoformat()
    out = Path(args.out) if args.out else ROOT / 'exports' / f'catalog_{today.replace("-", "")}.xlsx'
    out.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()

    # ---- 總覽 ----
    ws = wb.active
    ws.title = '總覽'
    rows = [
        ('產生日期', today),
        ('來源 index_revision', catalog.get('source_index_revision')),
        ('來源 commit', catalog.get('source_index_commit_sha')),
        ('景點總數', len(places)),
        ('題材總數', len(catalog['opportunities'])),
    ]
    counts: dict[str, int] = {}
    opp_counts: dict[str, int] = {}
    for o in catalog['opportunities']:
        c = o['place_id'].split('-')[0]
        counts[c] = counts.get(c, 0) + 1
    for r in rows:
        ws.append(r)
    ws.append([])
    ws.append(['國家', '景點數', '題材數'])
    for c, (label,) in COUNTRY_SHEETS.items():
        n_p = sum(1 for p in places if p.split('-')[0] == c)
        ws.append([label, n_p, counts.get(c, 0)])
    style_header(ws, 3)
    ws.column_dimensions['A'].width = 24
    for col in 'BC':
        ws.column_dimensions[col].width = 40

    # ---- 景點清單 ----
    ws = wb.create_sheet('景點清單')
    ws.append(PH)
    for pid in sorted(places):
        p = places[pid]
        opps = opps_by_place.get(pid, [])
        labels = []
        for o in opps:
            con = con_map.get(o['opportunity_id'])
            if con and con.get('genre_template'):
                labels.append(label3(GENRES, con['genre_template'])[0])
        ws.append([pid, p['name_i18n'].get('zh-TW', ''), p['name_i18n'].get('en', ''),
                   p['name_i18n'].get('ja', ''), len(opps), '、'.join(sorted(set(labels)))])
    style_header(ws, len(PH))
    for i, w in enumerate([12, 28, 28, 28, 8, 40], 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # ---- per-country condition sheets (ak merged into the US sheet) ----
    created: dict[str, object] = {}
    for prefix, (sheet_name,) in COUNTRY_SHEETS.items():
        ws = created.get(sheet_name)
        if ws is None:
            ws = wb.create_sheet(sheet_name)
            ws.append(TH)
            created[sheet_name] = ws
        ws.append(TH)
        for pid in sorted(places):
            if pid.split('-')[0] != prefix:
                continue
            pname = places[pid]['name_i18n'].get('zh-TW', '')
            for o in sorted(opps_by_place.get(pid, []), key=lambda x: x['opportunity_id']):
                oid = o['opportunity_id']
                oname = (con_map.get(oid, o))['name_i18n'].get('zh-TW', '')
                con = con_map.get(oid)
                if con and con.get('genre_template'):
                    genre = label3(GENRES, con['genre_template'])[0]
                else:
                    genre = '（未分類）'
                conds = (con or {}).get('conditions') or []
                if not conds:
                    ws.append([pid, pname, oid, oname, genre, '（無條件契約）', '', '', ''])
                    continue
                for c in conds:
                    role = ROLES.get(c.get('role'), c.get('role') or '')
                    metric = label3(METRICS, c.get('metric', ''))[0]
                    rationale = (c.get('rationale_i18n') or {}).get('zh-TW', '')
                    ws.append([pid, pname, oid, oname, genre, role, metric,
                               fmt_threshold(c), rationale])
        style_header(ws, len(TH))
        widths = [12, 26, 14, 30, 12, 10, 18, 16, 90]
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.auto_filter.ref = f'A1:{get_column_letter(len(TH))}1'
        for row in ws.iter_rows(min_row=2, min_col=9, max_col=9):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical='top')

    wb.save(out)
    print(json.dumps({'written': str(out), 'places': len(places),
                      'opportunities': len(catalog['opportunities']),
                      'sheets': wb.sheetnames}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
