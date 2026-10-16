"""W1 reference/semantic validation only; no UI, resolver, provider or evaluator.

Evidence citations, approval inputs and IANA membership are not authentication.
Consumers must obtain approvals/bytes/capabilities from their authoritative source.
"""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from jsonschema import Draft202012Validator, FormatChecker
from validate_contract import validate_record

ROOT = Path(__file__).resolve().parents[1]
KINDS = ('place-index', 'date-query', 'topic-index', 'local-preferences',
         'browse-query', 'sort-capabilities')


def structural(kind, document):
    schema = json.loads((ROOT / f'schema/{kind}-v0.1.schema.json').read_text())
    Draft202012Validator.check_schema(schema)
    return sorted(f"schema:{'/'.join(map(str, e.absolute_path))}: {e.message}"
                  for e in Draft202012Validator(schema, format_checker=FormatChecker())
                  .iter_errors(document))


def keyed(rows, field, errors):
    result = {}
    for row in rows:
        key = row[field]
        if key in result:
            errors.append(f'duplicate {field}: {key}')
        result[key] = row
    return result


def zone_errors(zone):
    if zone['status'] == 'VERIFIED':
        try:
            ZoneInfo(zone['iana_id'])
        except (ZoneInfoNotFoundError, ValueError):
            return ['invalid IANA time zone']
    return []


def validate_index(doc, canonical_sources, approvals=None):
    errors = structural('place-index', doc)
    if errors:
        return errors
    approvals = approvals or {}
    regions = keyed(doc['regions'], 'region_id', errors)
    places = keyed(doc['places'], 'place_id', errors)
    keyed(doc['opportunities'], 'opportunity_id', errors)
    for r in regions.values():
        country = r['country_code']
        if r['level'] == 'COUNTRY':
            if (r['code_standard'], r['code'], r['region_id']) != (
                    'ISO_3166_1', country, f'country:{country}'):
                errors.append('country registry mismatch')
        elif (r['code_standard'] != 'ISO_3166_2' or
              not r['code'].startswith(country + '-') or
              r['region_id'] != 'admin1:' + r['code']):
            errors.append('admin1 registry mismatch')
    for p in places.values():
        errors.extend(zone_errors(p['time_zone']))
        if (p['metadata_status'] == 'COMPLETE' or p['admin_status'] == 'COMPLETE') and not p['evidence_refs']:
            errors.append('complete metadata needs sources')
        if p['semantic_review'] == 'APPROVED' and p['metadata_status'] != 'COMPLETE':
            errors.append('approved names must be complete')
        memberships = []
        for rid in p['region_ids']:
            if rid not in regions:
                errors.append('dangling region')
            else:
                memberships.append(regions[rid])
                if regions[rid]['country_code'] not in p['country_codes']:
                    errors.append('region country missing from Place')
        if p['admin_status'] == 'COMPLETE':
            if not p['country_codes']:
                errors.append('complete admin needs country')
            for country in p['country_codes']:
                if f'country:{country}' not in p['region_ids']:
                    errors.append('complete admin needs country membership')
                if country in ('TW', 'US', 'JP') and not any(
                        r['level'] == 'ADMIN1' and r['country_code'] == country for r in memberships):
                    errors.append('complete admin needs evidenced admin1')
    for b in doc['opportunities']:
        p = places.get(b['place_id'])
        if p is None:
            errors.append('dangling Place')
        expected_path = f"data/v2/opportunities/{b['opportunity_id']}.json"
        if b['source_path'] != expected_path:
            errors.append('canonical path mismatch')
        raw = canonical_sources.get((b['source_commit_sha'], b['source_path']))
        if raw is None:
            errors.append('missing pinned canonical bytes')
            continue
        blob = hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
        if blob != b['source_blob_sha']:
            errors.append('canonical byte hash mismatch')
        try:
            canonical = json.loads(raw)
            canonical_errors = validate_record(canonical)
        except (ValueError, TypeError, KeyError) as exc:
            errors.append(f'invalid canonical: {exc}')
            continue
        if canonical_errors:
            errors.append('canonical schema/reference failure')
        if any(canonical.get(k) != b[k] for k in ('opportunity_id', 'place_id', 'revision')):
            errors.append('canonical identity/revision mismatch')
        if b['publication'] == 'GUIDE_ELIGIBLE':
            approval = approvals.get(b['publication_approval_ref'])
            # An external release approval must be supplied, never synthesized
            # from schema success or the research-level number.
            expected = {k: b[k] for k in ('opportunity_id', 'revision', 'source_commit_sha', 'source_blob_sha')}
            if not approval or any(approval.get(k) != v for k, v in expected.items()) or approval.get('human_semantic_approved') is not True or approval.get('existence_verified') is not True or approval.get('crosswalk_approved') is not True:
                errors.append('missing exact human/evidence release approval')
            if canonical.get('lifecycle_status') != 'approved' or p is None or p['semantic_review'] != 'APPROVED' or p['metadata_status'] != 'COMPLETE':
                errors.append('guide publication prerequisites missing')
        elif b['publication_approval_ref'] is not None:
            errors.append('non-guide cannot carry guide approval')
    return sorted(errors)


def validate_date_query(doc, expected=None, index=None):
    errors = structural('date-query', doc)
    if errors:
        return errors
    errors.extend(zone_errors(doc['time_zone']))
    if index is not None:
        places = {p['place_id']: p for p in index['places']}
        place = places.get(doc['place_id'])
        if doc['index_revision'] != index['index_revision'] or place is None:
            errors.append('query index/Place mismatch')
        elif doc['time_zone'] != place['time_zone']:
            errors.append('query timezone differs from Place index')
        if doc['artifact'] is not None:
            artifact = doc['artifact']
            bindings = {b['opportunity_id']: b for b in index['opportunities']}
            binding = bindings.get(artifact['opportunity_id'])
            if (binding is None or binding['place_id'] != doc['place_id'] or
                    binding['revision'] != artifact['opportunity_revision'] or
                    binding['revision'] != artifact['contract_revision']):
                errors.append('artifact canonical binding mismatch')
    if expected:
        for key in ('query_id', 'generation', 'place_id', 'selected_date', 'time_zone', 'index_revision'):
            if doc[key] != expected[key]:
                errors.append(f'superseded query: {key}')
        if doc['artifact'] is not None and doc['artifact'] != expected.get('artifact'):
            errors.append('artifact version/identity mismatch')
    if doc['state'] in ('EMPTY', 'ERROR', 'STALE', 'NOT_EVALUABLE') and doc['reason_code'] is None:
        errors.append('terminal non-ready state needs reason')
    if doc['time_zone']['status'] == 'UNKNOWN':
        return sorted(errors)
    if doc['place_local_date'] is not None and doc['place_local_date'] != doc['selected_date']:
        errors.append('selected date is not Place-local date')
    day = doc['local_day']
    if day is not None and not zone_errors(doc['time_zone']):
        zone = ZoneInfo(doc['time_zone']['iana_id'])
        start = datetime.fromisoformat(day['start_utc'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(day['end_utc'].replace('Z', '+00:00'))
        target = doc['selected_date']
        epsilon = timedelta(microseconds=1)
        if start >= end:
            errors.append('reversed/empty local-day interval')
        elif (start.astimezone(zone).date().isoformat() != target or
              (start - epsilon).astimezone(zone).date().isoformat() == target or
              (end - epsilon).astimezone(zone).date().isoformat() != target or
              end.astimezone(zone).date().isoformat() == target):
            errors.append('local-day boundaries mismatch IANA date')
        if doc['place_local_date'] != target:
            errors.append('resolved interval needs Place-local date')
        for field, instant in [('start', start), ('end', end)]:
            if day[f'{field}_offset_seconds'] != int(instant.astimezone(zone).utcoffset().total_seconds()):
                errors.append('UTC offset mismatch')
    return sorted(errors)


def validate_topics(doc, index):
    errors = structural('topic-index', doc)
    if errors:
        return errors
    if doc['index_revision'] != index['index_revision']:
        errors.append('index revision mismatch')
    topics = keyed(doc['topics'], 'topic_id', errors)
    keyed(doc['opportunity_topics'], 'opportunity_id', errors)
    opportunities = {b['opportunity_id'] for b in index['opportunities']}
    for t in topics.values():
        replacement = t['replaced_by']
        if t['status'] == 'ACTIVE' and replacement is not None:
            errors.append('active topic has replacement')
        if replacement is not None and replacement not in topics:
            errors.append('dangling replacement')
        seen = {t['topic_id']}
        while replacement in topics:
            if replacement in seen:
                errors.append('cyclic topic replacement')
                break
            seen.add(replacement)
            replacement = topics[replacement]['replaced_by']
    for b in doc['opportunity_topics']:
        if b['opportunity_id'] not in opportunities:
            errors.append('dangling Opportunity topic binding')
        if not set(b['topic_ids']) <= topics.keys():
            errors.append('unknown topic binding')
    return sorted(errors)


def validate_preferences(doc):
    errors = structural('local-preferences', doc)
    if not errors:
        keys = [(f['entity_type'], f['entity_id']) for f in doc['favorites']]
        if len(keys) != len(set(keys)):
            errors.append('duplicate favorite entity key')
    return errors


def validate_browse(doc, index, topics, capabilities=None):
    errors = structural('browse-query', doc)
    if errors:
        return errors
    if doc['index_revision'] != index['index_revision'] or doc['taxonomy_revision'] != topics['taxonomy_revision']:
        errors.append('browse revision mismatch')
    if not set(doc['region_ids']) <= {r['region_id'] for r in index['regions']}:
        errors.append('INVALID_FILTER region')
    if not set(doc['topic_ids']) <= {t['topic_id'] for t in topics['topics']}:
        errors.append('INVALID_FILTER topic')
    if capabilities is None and doc['sort'] in ('SCORE', 'DISTANCE'):
        errors.append('UNSUPPORTED_SORT')
    elif capabilities is not None and not capabilities[doc['sort']]['enabled']:
        errors.append('UNSUPPORTED_SORT')
    return sorted(errors)


def validate_capabilities(doc, trusted_comparison_keys=None):
    errors = structural('sort-capabilities', doc)
    if not errors:
        trusted_comparison_keys = trusted_comparison_keys or {}
        for key in ('SCORE', 'DISTANCE'):
            if doc[key]['enabled'] and doc[key]['comparison_key'] != trusted_comparison_keys.get(key):
                errors.append(f'{key} lacks trusted comparable inputs')
    return sorted(errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fixture_dir', nargs='?', type=Path,
                        default=ROOT / 'tests/fixtures/task-w')
    args = parser.parse_args()
    data = {kind: json.loads((args.fixture_dir / f'{kind}.json').read_text()) for kind in KINDS}
    index = data['place-index']
    sources = {}
    for b in index['opportunities']:
        sources[(b['source_commit_sha'], b['source_path'])] = subprocess.check_output(
            ['git', 'show', f"{b['source_commit_sha']}:{b['source_path']}"], cwd=ROOT)
    checks = {
        'place-index': validate_index(index, sources),
        'date-query': validate_date_query(data['date-query'], index=index),
        'topic-index': validate_topics(data['topic-index'], index),
        'local-preferences': validate_preferences(data['local-preferences']),
        'browse-query': validate_browse(data['browse-query'], index, data['topic-index'], data['sort-capabilities']),
        'sort-capabilities': validate_capabilities(data['sort-capabilities']),
    }
    for kind, errors in checks.items():
        print(('FAIL ' + kind + ': ' + '; '.join(errors)) if errors else 'PASS ' + kind)
    return int(any(checks.values()))


if __name__ == '__main__':
    raise SystemExit(main())
