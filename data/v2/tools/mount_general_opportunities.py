#!/usr/bin/env python3
"""CL-DATA-65: auto-mount the general-v0.1 genre onto zero-curated-subject places.

Owner ruling 2026-11-10: every place keeps at least one "general subject" -
subject unobstructed (adequate visibility), shootable without heavy rain or
heavy fog. This tool scans the canonical place-index/opportunities and, for
every place with zero curated (genre_template-carrying, non-retired)
opportunities, expands data/v2/templates/general.json into a new canonical
opportunity <place_id>-P99 via apply_template.expand.

Choices (documented, honest):
- Retired places are SKIPPED. A place whose every opportunity carries
  lifecycle_status "retired" is hidden as a whole by the retirement ruling
  (CL-DATA-62); mounting a fresh general opportunity would resurrect a
  deliberately retired place through the back door. They stay retired.
- view_scale_km is derived from the place's existing genre distribution
  (vista 8 / near 3 / general 5) - see scale_for_place().
- Geometry is inherited from the place's own canonical opportunity geometry
  (provisional points); a place with no opportunity geometry fails LOUDLY -
  the tool never fabricates coordinates (612 minor candidates must bring
  their own geometry at intake time).
- Idempotent and never overwriting: an existing <place_id>-P99.json is never
  rewritten. Dry-run is the default; --write commits changes to disk.

After --write, pass --commit-sha <data-commit> in a second run to extend
source-lock.json canonical_records pins and curation.json classifications
(the pinned bytes must already be committed, precedent: CL-DATA-01 repin).
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
GENERAL_SUFFIX = 'P99'

VISTA_GENRES = {'overlook', 'mountain_view', 'cloud_sea', 'night_sky'}
NEAR_GENRES = {'waterfall', 'tidal', 'geological_landform', 'reflection'}

ACCESS_NOTES = {
    "zh-TW": "存取資訊尚未核實；請依現場公告與規定。",
    "en": "Access information not yet verified; follow on-site notices and rules.",
    "ja": "アクセス情報は未確認。現地の告知と規定に従ってください。",
}
SAFETY_NOTES = {
    "zh-TW": "請依現場安全指示行動。",
    "en": "Follow on-site safety guidance.",
    "ja": "現地の安全指示に従ってください。",
}
CLAIM_SCOPE = ("CL-DATA-65 general-genre auto-mount from the canonical place "
               "record; no independent photographic evidence attached yet.")
GEOMETRY_NOTE = "Inherited from the place's existing canonical opportunity geometry (provisional)."
CLASSIFICATION_BASIS = "general_genre_auto_mount_v0.1"

DESC_I18N = {
    "zh-TW": ("一般拍攝題材（owner 裁決 2026-11-10 零題材兜底）：主體不被遮擋（能見度足夠）、"
              "無大雨大霧即可拍攝。此為可拍性下限保證，非策展題材；顯示層以「一般拍攝」標籤區分。"),
    "en": ("General shooting subject (CL-DATA-65 zero-curated-subject fallback, owner ruling "
           "2026-11-10): the subject is unobstructed (adequate visibility) and shootable "
           "without heavy rain or heavy fog. This is a shootability floor, not a curated "
           "genre; the display layer labels it General shooting."),
    "ja": ("一般撮影題材（2026-11-10 オーナー裁定によるゼロ題材フォールバック）：主題が遮られず"
           "（視程十分）、大雨・濃霧がなければ撮影できる。撮影可能性の下限保証であり、"
           "キュレーション題材ではない。表示層は「一般撮影」ラベルで区別する。"),
}

SCALE_I18N = {
    "zh-TW": {"8": "遠景型（8km）", "5": "一般（5km）", "3": "近景型（3km）"},
    "en": {"8": "vista-type (8km)", "5": "general (5km)", "3": "close-range (3km)"},
    "ja": {"8": "遠景型（8km）", "5": "一般（5km）", "3": "近景型（3km）"},
}


def _encoded(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def _blob(raw: bytes) -> str:
    return hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _i18n_verbatim(zh_text):
    """CL-UI-07 rule: carry the reviewed zh-TW value verbatim to en/ja."""
    return {"zh-TW": zh_text, "en": zh_text, "ja": zh_text}


def scale_for_place(genres) -> int:
    """8 vista / 3 near / 5 general, from the place's existing genre ids."""
    g = set(genres)
    if g & VISTA_GENRES:
        return 8
    if g & NEAR_GENRES:
        return 3
    return 5


def load_state():
    place_index = json.loads((INDEX / 'place-index.json').read_text(encoding='utf-8'))
    docs = {}
    for path in sorted(CANONICAL.glob('*.json')):
        d = json.loads(path.read_text(encoding='utf-8'))
        docs[d['opportunity_id']] = d
    return place_index, docs


def curated_place_genres(docs):
    by_place = {}
    for d in docs.values():
        genre = (d.get('condition_contract') or {}).get('genre_template')
        retired = d.get('lifecycle_status') == 'retired'
        by_place.setdefault(d['place_id'], []).append((genre, retired))
    return by_place


def places_to_mount(place_index, docs):
    """Return ({place_id: skip_reason}, {place_id: genres}) for the mount scan.

    skip_reason None means the place qualifies for a general mount.
    """
    by_place = curated_place_genres(docs)
    skip, targets = {}, {}
    for place in place_index['places']:
        pid = place['place_id']
        entries = by_place.get(pid, [])
        curated = [g for g, retired in entries if g and not retired]
        if curated:
            skip[pid] = 'curated_subject_present'
            continue
        if entries and all(retired for _, retired in entries):
            # Fully retired place: hidden as a whole by the retirement ruling.
            # Mounting a fresh general opportunity would resurrect it back door.
            skip[pid] = 'retired_hidden'
            continue
        targets[pid] = [g for g, _ in entries if g]
    return skip, targets


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
        f'tool never fabricates coordinates - supply geometry at intake time')


def build_general_opportunity(place, docs, place_id, imported_at):
    lat, lon, from_oid = place_geometry(docs, place_id)
    genres = [g for g, _ in curated_place_genres(docs).get(place_id, [])]
    km = scale_for_place(genres)
    oid = f'{place_id}-{GENERAL_SUFFIX}'
    name = place.get('name_i18n') or {}
    zh_name = name.get('zh-TW') or place_id
    scale_note = {
        'zh-TW': SCALE_I18N['zh-TW'][str(km)],
        'en': SCALE_I18N['en'][str(km)],
        'ja': SCALE_I18N['ja'][str(km)],
    }

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
        'name_i18n': {
            'zh-TW': f'{zh_name}・一般拍攝',
            'en': f'{name.get("en") or zh_name} · General shooting',
            'ja': f'{name.get("ja") or zh_name}・一般撮影',
        },
        'description_i18n': {
            'zh-TW': DESC_I18N['zh-TW'] + '能見度門檻：' + scale_note['zh-TW'] + '。',
            'en': DESC_I18N['en'] + 'Visibility threshold: ' + scale_note['en'] + '.',
            'ja': DESC_I18N['ja'] + '視程閾値：' + scale_note['ja'] + '。',
        },
        'camera_contexts': [{
            'id': f'CZ-{oid}-01', 'kind': 'area', 'geometry': geo(),
            'verification_status': 'provisional', 'evidence_refs': [],
            'access_notes_i18n': ACCESS_NOTES, 'safety_notes_i18n': SAFETY_NOTES,
            'altitude_m': None,
        }],
        'targets': [{
            'id': f'SG-{oid}-01', 'kind': 'multi_component',
            'name_i18n': {
                'zh-TW': f'{zh_name}（一般拍攝）',
                'en': f'{name.get("en") or zh_name} (general shooting)',
                'ja': f'{name.get("ja") or zh_name}（一般撮影）',
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
        'navigation_targets': [],
        'evidence_claims': [{
            'claim_id': f'{oid}-claim-01', 'claim_type': 'existence',
            'evidence_refs': [], 'audit_status': 'UNKNOWN',
            'scope_note': CLAIM_SCOPE,
        }],
        'readiness': {'research_level': 'R0', 'gaps': ['RESEARCH_GAP', 'GEOMETRY_GAP']},
        'provenance': {
            'source_catalog': 'general_genre_mount_v0.1',
            'source_revision': f'mount-general-{place_id}-from-{from_oid}',
            'imported_at': imported_at,
            'review_status': 'pending',
            'reviewed_by': None,
        },
    }
    params_path = ROOT / f'data/v2/staging/general-mount/{oid}-params.json'
    params_path.parent.mkdir(parents=True, exist_ok=True)
    params_path.write_bytes(_encoded({'view_scale_km': km}))
    skel_path = params_path.with_name(f'{oid}-skeleton.json')
    skel_path.write_bytes(_encoded(skeleton))
    tmp_out = params_path.with_name(f'{oid}-expanded.json')
    at.expand('general', oid, skel_path, params_path, tmp_out,
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
    # expand() sets contract_version; keep the schema-minimal contract keys only
    doc['condition_contract'].pop('template_version', None)
    params_path.unlink()
    skel_path.unlink()
    tmp_out.unlink()
    return doc, km


def admit(pin_commit_sha: str | None, place_ids: list[str] | None = None,
          write: bool = False):
    """Extend source-lock canonical_records + curation classifications."""
    lock_path = INDEX / 'source-lock.json'
    curation_path = INDEX / 'curation.json'
    lock = json.loads(lock_path.read_text(encoding='utf-8'))
    curation = json.loads(curation_path.read_text(encoding='utf-8'))
    _, docs = load_state()
    pinned = {p['opportunity_id'] for p in lock['canonical_records']}
    mounted = sorted(oid for oid, d in docs.items()
                     if oid.endswith('-' + GENERAL_SUFFIX)
                     and (place_ids is None or d['place_id'] in place_ids))
    new_pins, new_class = [], []
    for oid in mounted:
        if oid in pinned:
            continue
        rel = f'data/v2/opportunities/{oid}.json'
        raw = (ROOT / rel).read_bytes()
        pin = {'opportunity_id': oid, 'path': rel, 'blob_sha': _blob(raw),
               'sha256': _sha256(raw), 'commit_sha': pin_commit_sha}
        if pin_commit_sha is None:
            # Pre-commit dry run: pin without commit_sha is invalid for the gate.
            new_pins.append({**pin, 'commit_sha': 'PENDING_DATA_COMMIT'})
        else:
            new_pins.append(pin)
        d = docs[oid]
        claim = next(c for c in d['evidence_claims'] if c['claim_type'] == 'existence')
        new_class.append(oid)
        if write:
            curation['classifications'][oid] = {
                'topic_ids': [],
                'canonical_pointers': ['/targets/0/name_i18n', '/description_i18n'],
                'evidence_claim_id': claim['claim_id'],
                'evidence_refs': [],
                'classification_basis': CLASSIFICATION_BASIS,
            }
    if write:
        if new_pins and pin_commit_sha:
            lock['canonical_records'].extend(new_pins)
            lock['canonical_records'].sort(key=lambda p: p['opportunity_id'])
            lock_path.write_bytes(_encoded(lock))
            curation_path.write_bytes(_encoded(curation))
    return {'new_pins': [p['opportunity_id'] for p in new_pins],
            'new_classifications': new_class,
            'commit_sha': pin_commit_sha}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--write', action='store_true', help='write mounted opportunities (default dry-run)')
    ap.add_argument('--admit', action='store_true', help='extend source-lock/curation for mounted files')
    ap.add_argument('--commit-sha', default=None, help='data commit carrying the mounted bytes')
    ap.add_argument('--imported-at', default=None,
                    help='ISO timestamp for provenance (default: fixed determinism stamp)')
    ap.add_argument('--place-id', action='append', default=None,
                    help='restrict to one place_id (repeatable)')
    args = ap.parse_args(argv)
    imported_at = args.imported_at or '2026-11-10T00:00:00Z'
    if not imported_at.endswith('Z') or 'T' not in imported_at:
        ap.error('--imported-at must be an explicit ISO UTC stamp (determinism)')
    place_index, docs = load_state()
    skip, targets = places_to_mount(place_index, docs)
    if args.place_id:
        targets = {k: v for k, v in targets.items() if k in args.place_id}
        skip = {k: v for k, v in skip.items() if k in args.place_id}
    report = {'skipped': skip, 'mounted': [], 'bytes': {}}
    for pid, genres in sorted(targets.items()):
        oid = f'{pid}-{GENERAL_SUFFIX}'
        out = CANONICAL / f'{oid}.json'
        if out.exists():
            report['skipped'][pid] = 'p99_already_exists'
            continue
        place = next(p for p in place_index['places'] if p['place_id'] == pid)
        doc, km = build_general_opportunity(place, docs, pid, imported_at)
        raw = _encoded(doc)
        report['mounted'].append({'opportunity_id': oid, 'view_scale_km': km})
        report['bytes'][oid] = len(raw)
        if args.write:
            out.write_bytes(raw)
    if args.admit:
        report['admit'] = admit(args.commit_sha,
                                place_ids=args.place_id, write=args.write)
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    print(json.dumps({'status': 'OK', 'mode': 'write' if args.write else 'dry-run',
                      'now': now, **report}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
