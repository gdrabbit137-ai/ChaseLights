#!/usr/bin/env python3
"""CL-DATA-73: mount the misty_forest-v0.1 genre onto cataloged high-humidity
forest spots (owner directive 2026-11-16, 必做 — fog is the photographic
subject and the ONLY genre allowed to invert the visibility logic).

Candidates are EXISTING catalog places (this ticket adds no places):
杉林溪 tw-053, 忘憂森林 tw-104, 太平山 tw-140 (+ 太平山區步道/湖 tw-088
翠峰湖環山步道、tw-032 見晴懷古步道), 明池 tw-173, 阿里山 tw-024 祝山
(+ 阿里山山脈雲霧林帶 tw-177 特富野古道), 武陵農場 tw-120, 內洞 tw-151,
觀霧 tw-089 榛山步道, 司馬庫斯 tw-091. 滿月圓 is NOT in the catalog — skipped
honestly (the mount tool never fabricates places; see the ticket report).

Mechanics follow the CL-DATA-65 mount precedent (mount_general_opportunities):
- per place, a NEW canonical opportunity <place_id>-P<n> (next free suffix),
  skeleton inheriting the place's own canonical camera geometry;
- apply_template.expand('misty_forest', ...) writes the condition contract
  (fresh expansion, never merged into an existing contract);
- elevation/terrain semantics are per-spot BESPOKE copy (terrain words only —
  no unverified numbers are shipped, per the fact-sourcing mandate);
- --write admits to data/v2/opportunities/; --admit --commit-sha <data-commit>
  extends source-lock canonical_records + curation (CL-DATA-01 repin pattern).

Idempotent: an existing opportunity file is never rewritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import apply_template as at  # noqa: E402

ROOT = HERE.parents[2]
INDEX = ROOT / 'data/v2/indexes/research'
CANONICAL = ROOT / 'data/v2/opportunities'

ACCESS_NOTES = {
    "zh-TW": "存取資訊沿用該遊樂區／步道既有入口記錄；清晨拍霧請先確認入園與道路開放時間。",
    "en": "Access reuses the recreation area / trail's existing entrance records; confirm park entry and road opening hours before pre-dawn fog shoots.",
    "ja": "アクセスは当該遊楽区・遊歩道の既存入口情報に従う。早朝の霧撮影の前に入園・道路開放時間を確認すること。",
}
SAFETY_NOTES = {
    "zh-TW": "霧中能見度低，請結伴、穿亮色衣物並攜照明；濕滑步道小心。",
    "en": "Visibility inside fog is low: hike in company, wear bright clothing, carry a light; beware slippery trail sections.",
    "ja": "霧中は視界が悪い。同行者を連れ、目立つ服装とライトを携行し、滑りやすい遊歩道に注意すること。",
}
CLAIM_SCOPE = ("CL-DATA-73 misty-forest mount from the canonical place record; "
               "owner-approved fog-subject genre (CL-DATA-73 ticket directive); "
               "no independent photographic evidence attached yet.")
GEOMETRY_NOTE = "Inherited from the place's existing canonical opportunity geometry (provisional)."
CLASSIFICATION_BASIS = "misty_forest_mount_v0.1 (CL-DATA-73)"

# Per-spot bespoke copy (elevation/terrain semantics in terrain WORDS, no
# unverified numbers): place_id -> {names, desc}.
SPOTS = {
    "tw-053": dict(  # 杉林溪（松瀧岩／青龍脊谷濕潤森林，中海拔溪谷霧）
        names={"zh-TW": "杉林溪晨霧森林", "en": "Sun Link Sea morning fog forest",
               "ja": "杉林渓の朝霧の森"},
        desc={
            "zh-TW": "杉林溪中海拔濕潤溪谷森林的晨霧——霧沿松瀧岩溪谷爬升、漫進針闊葉樹冠。霧是主角：能見度 50–500 m 的清晨斜光最優；本題材與松瀧岩瀑布（水流特寫）題材錯位——本點拍的是霧與樹影。",
            "en": "Morning fog in the humid mid-elevation valley forest of Sun Link Sea — mist climbs the Songluoyan ravine and drifts into the mixed canopy. The fog IS the subject: 50-500 m visibility in slanted morning light is prime; disjoint from the waterfall subject (this shoots fog and tree silhouettes).",
            "ja": "杉林渓の中標高・湿潤な渓谷林の朝霧——霧は松瀧岩の谷を這い上がり混生の樹冠へ。霧が主役：視程50-500mの朝の斜光が狙い目。滝の被写体とは別物（この題材は霧と樹影）。",
        }),
    "tw-104": dict(  # 忘憂森林（積水杉林，低中海拔濕地霧）
        names={"zh-TW": "忘憂森林迷霧杉林", "en": "Wangyou Forest in fog",
               "ja": "忘憂森林の霧の杉林"},
        desc={
            "zh-TW": "忘憂森林積水杉林是台灣最穩定的迷霧題材之一——沼澤水面讓霧貼著樹幹成形。霧是主角：能見度 50–500 m 加水面倒影；與既有水杉倒影題材（晴日倒影構圖）錯位——本點拍的是霧壓倒影的氛圍。",
            "en": "The flooded-pond cedar woods of Wangyou Forest are among Taiwan's most reliable fog subjects — the marsh water lets fog form right against the trunks. The fog IS the subject: 50-500 m visibility over mirror water; disjoint from the clear-day reflection subject (this shoots fog weighing on the reflections).",
            "ja": "忘憂森林の水没杉林は台湾で最も安定した霧の題材の一つ——湿地の水面が幹に沿って霧を形成させる。霧が主役：視程50-500mと鏡面。晴日の倒影被写体とは別物（この題材は霧がかかる倒影の雰囲気）。",
        }),
    "tw-140": dict(  # 太平山森林遊樂區（中海拔霧林帶）
        names={"zh-TW": "太平山迷霧森林", "en": "Taipingshan misty forest",
               "ja": "太平山の霧の森"},
        desc={
            "zh-TW": "太平山森林遊樂區的霧林帶——東北季風季晨霧沿中海拔稜谷翻進林間。霧是主角：能見度 50–500 m、微風、晨窗優先；與太平山雲海題材（望遠雲層）錯位——本點拍的是人在霧林裡的樹影。",
            "en": "The fog belt of Taipingshan NRA — monsoon-season morning mist rolls over the mid-elevation ridges into the woods. The fog IS the subject: 50-500 m visibility, calm wind, morning window priority; disjoint from the cloud-sea subject (this shoots tree silhouettes inside the fog).",
            "ja": "太平山森林遊楽区の霧林帯——季節風の朝、中標高の尾根から林へ霧が流れ込む。霧が主役：視程50-500m、微風、朝の窓を優先。雲海被写体とは別物（この題材は霧の中の樹影）。",
        }),
    "tw-088": dict(  # 翠峰湖環山步道（高山湖泊霧林）
        names={"zh-TW": "翠峰湖環山步道晨霧", "en": "Cuifeng Lake loop trail in fog",
               "ja": "翠峰湖環山遊歩道の朝霧"},
        desc={
            "zh-TW": "翠峰湖環山步道的晨霧——高山湖泊水汽與鐵杉林交會，霧沿湖面與步道杉林漂移。霧是主角：能見度 50–500 m 沿環湖步道；與湖景／雲海題材錯位——本點拍霧鎖湖畔林。",
            "en": "Morning fog on the Cuifeng Lake loop trail — lake moisture meets the hemlock woods, mist drifting over the water and the trailside forest. The fog IS the subject: 50-500 m visibility along the lakeside loop; disjoint from the lake/cloud-sea subjects (this shoots fog locked over the lakeside woods).",
            "ja": "翠峰湖環山遊歩道の朝霧——湖の水蒸気とツガの林が交わり、湖面と並木に霧が漂う。霧が主役：環湖歩道沿いで視程50-500m。湖景・雲海被写体とは別物（霧に鎖された湖畔の林）。",
        }),
    "tw-032": dict(  # 見晴懷古步道（苔蘚森林步道）
        names={"zh-TW": "見晴懷古步道迷霧", "en": "Jianqing Historic Trail in mist",
               "ja": "見晴懷古遊歩道の霧"},
        desc={
            "zh-TW": "見晴懷古步道的苔蘚森林霧——舊運材軌道穿進高濕林下，霧讓苔綠與杉幹半掩。霧是主角：能見度 50–500 m 的林內斜光；與見晴遠眺聖稜線題材（晴日遠景）錯位——本點拍霧中近景林。",
            "en": "Moss-forest fog on the Jianqing Historic Trail — the old logging rails run through the humid understorey, mist half-veiling moss and trunks. The fog IS the subject: 50-500 m visibility in slanted in-forest light; disjoint from the clear-day Hsuehshan-ridge vista subject (this shoots the fogged near forest).",
            "ja": "見晴懷古遊歩道の苔の森の霧——旧運材軌道が高湿の林床を走り、苔や幹を霧が半ば隠す。霧が主役：林内の斜光で視程50-500m。晴日の聖稜線展望被写体とは別物（霧の近景の森）。",
        }),
    "tw-173": dict(  # 明池（北橫高濕湖泊森林）
        names={"zh-TW": "明池晨霧森林", "en": "Mingchi morning fog forest",
               "ja": "明池の朝霧の森"},
        desc={
            "zh-TW": "明池的高濕湖泊森林霧——北橫高地的湖面水汽與柳杉林，霧常年在湖畔成形。霧是主角：能見度 50–500 m 環湖；與明池紅葉題材（秋季植物特寫）錯位——本點拍霧漫湖畔林。",
            "en": "The humid lake-forest fog of Mingchi — the high-cross-island pond's moisture meets the Japanese-cedar woods, fog forming at the shore most of the year. The fog IS the subject: 50-500 m visibility around the pond; disjoint from the maple-foliage subject (this shoots fog over the lakeside forest).",
            "ja": "明池の高湿・湖と森の霧——北部横貫公路の高地进行の池の水蒸気と杉の林が交わり、年間を通じて湖畔に霧ができる。霧が主役：環池で視程50-500m。紅葉被写体とは別物（霧の湖畔林）。",
        }),
    "tw-024": dict(  # 阿里山祝山（森林鐵路高點，霧林帶邊）
        names={"zh-TW": "阿里山祝山晨霧森林", "en": "Alishan Zhushan morning fog forest",
               "ja": "阿里山祝山の朝霧の森"},
        desc={
            "zh-TW": "阿里山祝山方向的晨霧森林——高山鐵路沿線的雲霧帶林，晨霧自塔山方向漫進林間。霧是主角：能見度 50–500 m；與祝山日出雲海題材（遠望中央山脈雲層）錯位——本點拍霧鎖林相。祝山平台地形開闊，林霧以望向林帶為主。",
            "en": "Morning fog forest toward Zhushan, Alishan — the cloud-belt woods along the forest railway, mist drifting in from the Tashan direction. The fog IS the subject: 50-500 m visibility; disjoint from the Zhushan sunrise cloud-sea subject (this shoots fog over the forested slopes; the Zhushan platform is open terrain, so the fog is shot across the forest belt).",
            "ja": "阿里山・祝山側の朝霧の森——森林鉄道沿いの雲霧帯の林に、塔山方面から霧が流れ込む。霧が主役：視程50-500m。祝山の日の出・雲海被写体とは別物（霧に鎖された林相）。祝山展望台は開けた地形のため、林帯越しに霧を撮る。",
        }),
    "tw-120": dict(  # 武陵農場（七家灣溪谷晨霧）
        names={"zh-TW": "武陵農場晨霧林", "en": "Wuling Farm morning fog woods",
               "ja": "武陵農場の朝霧の林"},
        desc={
            "zh-TW": "武陵農場七家灣溪谷的晨霧林——高冷谷地輻射冷卻讓霧沿溪床與林緣成形。霧是主角：能見度 50–500 m、晨窗優先；與武陵櫻花季題材（季節植物）錯位——本點拍霧鎖溪谷林。",
            "en": "Morning fog woods of the Qijiawan valley at Wuling Farm — radiative cooling in the cold basin forms fog along the stream bed and forest edge. The fog IS the subject: 50-500 m visibility, morning window priority; disjoint from the Wuling cherry-blossom subject (this shoots fog over the valley woods).",
            "ja": "武陵農場・七家湾渓谷の朝霧の林——高冷地の放射冷却が渓床と林縁に霧を形成。霧が主役：視程50-500m、朝の窓を優先。桜季節被写体とは別物（霧に鎖された渓谷の林）。",
        }),
    "tw-151": dict(  # 內洞（低海拔溪谷森林，全台高濕）
        names={"zh-TW": "內洞溪谷迷霧森林", "en": "Neidong valley fog forest",
               "ja": "内洞の渓谷霧の森"},
        desc={
            "zh-TW": "內洞低海拔溪谷森林的霧——烏來濕谷水汽重，陰濕天沿南勢溪支流谷地成形。霧是主角：能見度 50–500 m；與內洞三層瀑布題材（水流特寫）錯位——本點拍霧鎖溪谷林。低海拔霧需更高濕度，成霧機率較中海拔霧林帶低，誠實呈現。",
            "en": "Fog in the low-elevation valley forest of Neidong — the humid Wulai valley builds moisture that forms fog along the tributary ravine in wet weather. The fog IS the subject: 50-500 m visibility; disjoint from the triple-cascade subject (this shoots fog over the ravine woods). Low-elevation fog needs higher humidity and forms less often than the mid-elevation fog belt — stated honestly.",
            "ja": "内洞の低標高・渓谷林の霧——烏来の湿谷は水蒸気が多く、降水天候には支流の谷に沿って霧ができる。霧が主役：視程50-500m。三段滝被写体とは別物（霧の谷林）。低標高の霧はより高い湿度を要し、中標高霧林帯より出現頻度は低い——正直に明記。",
        }),
    "tw-089": dict(  # 觀霧榛山步道（名字即題材：觀霧）
        names={"zh-TW": "觀霧榛山步道迷霧", "en": "Guanwu Zhenshan trail in fog",
               "ja": "観霧・榛山遊歩道の霧"},
        desc={
            "zh-TW": "觀霧——地名即題材。榛山步道穿中海拔雲霧帶森林，霧沿檜木林與稜線翻湧。霧是主角：能見度 50–500 m；與觀霧雲海題材（望遠雲層）錯位——本點拍霧中林相。",
            "en": "Guanwu - the place name IS the subject. The Zhenshan trail runs through the mid-elevation cloud-belt forest, fog surging along the cypress woods and ridge. The fog IS the subject: 50-500 m visibility; disjoint from the Guanwu cloud-sea subject (this shoots the fogged forest itself).",
            "ja": "観霧——地名がそのまま題材。榛山遊歩道は中標高の雲霧帯の森を走り、檜の林と尾根に沿って霧が湧く。霧が主役：視程50-500m。観霧の雲海被写体とは別物（霧に鎖された林相）。",
        }),
    "tw-091": dict(  # 司馬庫斯（中海拔雲霧帶部落森林）
        names={"zh-TW": "司馬庫斯霧林部落", "en": "Smangus fog forest",
               "ja": "司馬庫斯の霧の森"},
        desc={
            "zh-TW": "司馬庫斯雲霧帶森林——中海拔部落周邊的檜木林與巨木群，晨霧沿溪谷上湧包住樹冠。霧是主角：能見度 50–500 m；與部落／巨木題材（晴日人文與樹身）錯位——本點拍霧漫林間。",
            "en": "The cloud-belt forest of Smangus — cypress woods and giant trees around the mid-elevation village, morning fog surging up the ravines to wrap the canopy. The fog IS the subject: 50-500 m visibility; disjoint from the village/giant-tree subjects (this shoots fog through the woods).",
            "ja": "司馬庫斯の雲霧帯の森——中標高部落周辺の檜林と巨木群に、朝の霧が渓谷を上り樹冠を包む。霧が主役：視程50-500m。部落・巨木被写体とは別物（霧の林間）。",
        }),
    "tw-177": dict(  # 特富野古道（阿里山山脈雲霧森林）
        names={"zh-TW": "特富野古道霧林", "en": "Tefuya Historic Trail fog forest",
               "ja": "特富野古道の霧林"},
        desc={
            "zh-TW": "特富野古道的雲霧森林——阿里山山脈中海拔檜木林帶，晨霧沿古道鐵道線爬升。霧是主角：能見度 50–500 m；與古道展望／雲海題材錯位——本點拍霧中林道。",
            "en": "The cloud-fog forest of the Tefuya Historic Trail — the mid-elevation cypress belt of the Alishan range, morning fog climbing along the old railway grade. The fog IS the subject: 50-500 m visibility; disjoint from the trail-vista/cloud-sea subjects (this shoots the fogged forest path).",
            "ja": "特富野古道の雲霧の森——阿里山山脈の中標高檜林帯を、朝の霧が旧鉄道の軌道敷に沿って這い上がる。霧が主役：視程50-500m。古道展望・雲海被写体とは別物（霧の林道）。",
        }),
}

SKIPPED_PLACES = {
    "滿月圓": "not_in_catalog",
}


def _encoded(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def _blob(raw: bytes) -> str:
    return hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_state():
    place_index = json.loads((INDEX / 'place-index.json').read_text(encoding='utf-8'))
    docs = {}
    for path in sorted(CANONICAL.glob('*.json')):
        d = json.loads(path.read_text(encoding='utf-8'))
        docs[d['opportunity_id']] = d
    return place_index, docs


def place_geometry(docs, place_id):
    """Inherit the place's own canonical camera geometry; fail loudly if absent."""
    for oid in sorted(docs):
        d = docs[oid]
        if d['place_id'] != place_id:
            continue
        for cz in d.get('camera_contexts') or []:
            geo = (cz.get('geometry') or {})
            gj = geo.get('geojson') or {}
            if gj.get('type') == 'Point' and gj.get('coordinates'):
                lon, lat = gj['coordinates'][0], gj['coordinates'][1]
                return lat, lon, oid
    raise ValueError(
        f'{place_id}: no canonical camera geometry found to inherit; the mount '
        f'tool never fabricates coordinates')


def next_suffix(docs, place_id):
    used = set()
    for oid, d in docs.items():
        if d['place_id'] != place_id:
            continue
        tail = oid.rsplit('-P', 1)
        if len(tail) == 2 and tail[1].isdigit():
            used.add(int(tail[1]))
    n = 1
    while n in used:
        n += 1
    return f'P{n:02d}'


def build_misty_opportunity(place, docs, place_id, imported_at):
    spec = SPOTS[place_id]
    lat, lon, from_oid = place_geometry(docs, place_id)
    oid = f'{place_id}-{next_suffix(docs, place_id)}'
    place_name = place.get('name_i18n') or {}

    def geo():
        return {
            'kind': 'point', 'status': 'provisional',
            'geojson': {'type': 'Point', 'coordinates': [lon, lat]},
            'uncertainty_m': None,
            'derivation_method': 'inherited_from_place_opportunity_geometry',
            'source_geometry_revision': None, 'reason_if_absent': None,
        }

    skeleton = {
        'schema_version': '2.1.0',
        'opportunity_id': oid,
        'place_id': place_id,
        'revision': 1,
        'lifecycle_status': 'draft',
        'name_i18n': dict(spec['names']),
        'description_i18n': dict(spec['desc']),
        'camera_contexts': [{
            'id': f'CZ-{oid}-01', 'kind': 'area', 'geometry': geo(),
            'verification_status': 'provisional', 'evidence_refs': [],
            'access_notes_i18n': ACCESS_NOTES, 'safety_notes_i18n': SAFETY_NOTES,
            'altitude_m': None,
        }],
        'targets': [{
            'id': f'SG-{oid}-01', 'kind': 'multi_component',
            'name_i18n': {
                'zh-TW': f"{spec['names']['zh-TW']}（霧）",
                'en': f"{spec['names']['en']} (fog)",
                'ja': f"{spec['names']['ja']}（霧）",
            },
            'geometry': geo(), 'phenomenon_model_id': None,
            'evidence_refs': [], 'components': [],
        }],
        'observation_relations': [{
            'id': f'VR-{oid}-01', 'camera_context_id': f'CZ-{oid}-01',
            'target_id': f'SG-{oid}-01', 'type': 'foreground_background',
            'geometry_mode': 'unknown', 'azimuth_deg': None,
            'elevation_deg': None, 'distance_m': None,
            'evidence_refs': [], 'derivation_method': None,
            'uncertainty_note': GEOMETRY_NOTE,
        }],
        'navigation_targets': [{
            'id': f'NAV-{oid}-01',
            'status': 'needs_review',
            'target_type': 'other',
            'lat': lat,
            'lon': lon,
            'label_i18n': {
                'zh-TW': place_name.get('zh-TW') or place_id,
                'en': place_name.get('en') or place_id,
                'ja': place_name.get('ja') or place_id,
            },
            'evidence_refs': [],
            'confidence': 'low',
        }],
        'evidence_claims': [{
            'claim_id': f'{oid}-claim-01', 'claim_type': 'existence',
            'evidence_refs': [], 'audit_status': 'UNKNOWN',
            'scope_note': CLAIM_SCOPE,
        }],
        'readiness': {'research_level': 'R0',
                      'gaps': ['RESEARCH_GAP', 'GEOMETRY_GAP']},
        'provenance': {
            'source_catalog': 'misty_forest_mount_v0.1',
            'source_revision': f'mount-misty-{place_id}-from-{from_oid}',
            'imported_at': imported_at,
            'review_status': 'pending',
            'reviewed_by': None,
        },
    }
    tmp = ROOT / 'data/v2/staging/misty-mount'
    tmp.mkdir(parents=True, exist_ok=True)
    skel_path = tmp / f'{oid}-skeleton.json'
    skel_path.write_bytes(_encoded(skeleton))
    tmp_out = tmp / f'{oid}-expanded.json'
    at.expand('misty_forest', oid, skel_path, None, tmp_out,
              claim_ref=f'{oid}-claim-01', print_only=False)
    doc = json.loads(tmp_out.read_text(encoding='utf-8'))
    doc['name_i18n'] = skeleton['name_i18n']
    doc['description_i18n'] = skeleton['description_i18n']
    doc['provenance'] = skeleton['provenance']
    doc['camera_contexts'] = skeleton['camera_contexts']
    doc['targets'] = skeleton['targets']
    doc['observation_relations'] = skeleton['observation_relations']
    doc['navigation_targets'] = skeleton['navigation_targets']
    doc['evidence_claims'] = skeleton['evidence_claims']
    doc['readiness'] = skeleton['readiness']
    doc['condition_contract'].pop('template_version', None)
    skel_path.unlink()
    tmp_out.unlink()
    return doc, oid


def admit(pin_commit_sha, oids, write=False):
    """Extend source-lock canonical_records + curation classifications."""
    lock_path = INDEX / 'source-lock.json'
    curation_path = INDEX / 'curation.json'
    lock = json.loads(lock_path.read_text(encoding='utf-8'))
    curation = json.loads(curation_path.read_text(encoding='utf-8'))
    _, docs = load_state()
    pinned = {p['opportunity_id'] for p in lock['canonical_records']}
    new_pins, new_class = [], []
    for oid in oids:
        if oid in pinned:
            continue
        rel = f'data/v2/opportunities/{oid}.json'
        raw = (ROOT / rel).read_bytes()
        pin = {'opportunity_id': oid, 'path': rel, 'blob_sha': _blob(raw),
               'sha256': _sha256(raw), 'commit_sha': pin_commit_sha}
        if pin_commit_sha is None:
            new_pins.append({**pin, 'commit_sha': 'PENDING_DATA_COMMIT'})
        else:
            new_pins.append(pin)
        d = docs[oid]
        claim = next(c for c in d['evidence_claims']
                     if c['claim_type'] == 'existence')
        new_class.append(oid)
        if write:
            curation['classifications'][oid] = {
                'topic_ids': [],
                'canonical_pointers': ['/targets/0/name_i18n',
                                       '/description_i18n'],
                'evidence_claim_id': claim['claim_id'],
                'evidence_refs': [],
                'classification_basis': CLASSIFICATION_BASIS,
            }
    if write:
        if new_pins and pin_commit_sha:
            lock['canonical_records'].extend(new_pins)
            for pin in new_pins:
                recs = lock['canonical_records']
                recs.remove(pin)
                idx = next(i for i, r in enumerate(recs)
                           if r['opportunity_id'] > pin['opportunity_id'])
                recs.insert(idx, pin)
            lock_path.write_bytes(_encoded(lock))
            curation_path.write_bytes(_encoded(curation))
    return {'new_pins': [p['opportunity_id'] for p in new_pins],
            'new_classifications': new_class,
            'commit_sha': pin_commit_sha}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--write', action='store_true',
                    help='write mounted opportunities (default dry-run)')
    ap.add_argument('--admit', action='store_true',
                    help='extend source-lock/curation for mounted files')
    ap.add_argument('--commit-sha', default=None,
                    help='data commit carrying the mounted bytes')
    ap.add_argument('--imported-at', default=None,
                    help='ISO timestamp for provenance (default: fixed determinism stamp)')
    ap.add_argument('--place-id', action='append', default=None,
                    help='restrict to one place_id (repeatable)')
    args = ap.parse_args(argv)
    imported_at = args.imported_at or '2026-11-16T00:00:00Z'
    if not imported_at.endswith('Z') or 'T' not in imported_at:
        ap.error('--imported-at must be an explicit ISO UTC stamp (determinism)')
    place_index, docs = load_state()
    by_id = {p['place_id']: p for p in place_index['places']}
    targets = sorted(SPOTS)
    if args.place_id:
        targets = [p for p in targets if p in args.place_id]
    report = {'mounted': [], 'skipped': {}, 'bytes': {}}
    # Idempotency: skip a place once ANY misty_forest opportunity exists for
    # it (the CL-DATA-73 admit rerun re-enters main() and must never mount a
    # second batch).
    already = {d['place_id'] for d in docs.values()
               if (d.get('condition_contract') or {}).get('genre_template')
               == 'misty_forest'}
    for pid in targets:
        if pid not in by_id:
            report['skipped'][pid] = 'place_not_found'
            continue
        if pid in already:
            report['skipped'][pid] = 'misty_forest_already_mounted'
            continue
        oid_candidate = f"{pid}-{next_suffix(docs, pid)}"
        out = CANONICAL / f'{oid_candidate}.json'
        if out.exists():
            report['skipped'][pid] = 'already_mounted'
            continue
        doc, oid = build_misty_opportunity(by_id[pid], docs, pid, imported_at)
        raw = _encoded(doc)
        report['mounted'].append({'opportunity_id': oid})
        report['bytes'][oid] = len(raw)
        if args.write:
            out.write_bytes(raw)
    for name, reason in SKIPPED_PLACES.items():
        report['skipped'][name] = reason
    if args.admit:
        report['admit'] = admit(args.commit_sha,
                                [m['opportunity_id'] for m in report['mounted']],
                                write=args.write)
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    print(json.dumps({'status': 'OK',
                      'mode': 'write' if args.write else 'dry-run',
                      'now': now, **report}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
