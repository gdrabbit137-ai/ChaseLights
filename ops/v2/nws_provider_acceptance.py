"""Opt-in, bounded W5 acceptance; never publishes data or changes W3 transport.

Two independent TLS requests, then the unchanged W3 runtime (at most two more).
Archives are evidence of this Actions run; parser replay remains TEST_FIXTURE.
"""
import argparse
from base64 import b64decode
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.error import HTTPError
from urllib.request import Request, HTTPRedirectHandler, build_opener
from zoneinfo import ZoneInfo

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'packages/core-v2'))
import forecast_runtime as runtime
from adapters import nws_snapshot

POINTS = 'https://api.weather.gov/points/47.6,-122.33'
GRID = re.compile(r'https://api\.weather\.gov/gridpoints/([A-Z]{3})/(\d+),(\d+)\Z')
LIMIT = 8 * 1024 * 1024
POLICY = {'approved': True, 'max_age_seconds': 86400,
          'source': 'W5 one-shot research acceptance only; not production/scientific approval; #467/#506'}
UNITS = {'skyCover': {'wmoUnit:percent': (0, 100)},
         'windSpeed': {'wmoUnit:km_h-1': (0, 400), 'wmoUnit:m_s-1': (0, 112)},
         'probabilityOfPrecipitation': {'wmoUnit:percent': (0, 100)}}


def stamp():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def instant(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.utcoffset() is None:
        raise ValueError('naive timestamp')
    return result.astimezone(timezone.utc)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(out, name, value):
    (out / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def require(condition, message):
    if not condition:
        raise ValueError(message)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def capture(out, label, url):
    """Default TLS/proxy settings; no retries, no redirects, 12s and 8MiB bounds."""
    require(url == POINTS or GRID.fullmatch(url), 'nonofficial provider URL')
    meta = {'url': url, 'started_at_utc': stamp(), 'status': None,
            'body_file': label + '.body', 'headers_file': label + '.headers',
            'transport': 'HTTPS_TLS', 'timeout_seconds': 12, 'max_bytes': LIMIT}
    try:
        req = Request(url, headers={'User-Agent': 'ChaseLights-W5-Acceptance/0.1 (https://github.com/gdrabbit137-ai/ChaseLights)',
                                    'Accept': 'application/geo+json, application/json'})
        try:
            response = build_opener(NoRedirect).open(req, timeout=12)
        except HTTPError as error:
            response = error
        with response:
            meta['status'] = response.code
            meta['final_url'] = response.geturl()
            meta['http_version'] = response.version
            (out / meta['headers_file']).write_bytes(response.headers.as_bytes())
            raw = response.read(LIMIT + 1)
            (out / meta['body_file']).write_bytes(raw)
            meta.update(sha256=digest(raw), size_bytes=len(raw))
            require(len(raw) <= LIMIT, 'response exceeds bound (archived prefix only)')
            require(response.geturl() == url and response.code == 200, 'HTTP capture failed')
            return json.loads(raw)
    except Exception as error:
        meta['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        meta['completed_at_utc'] = stamp()
        save(out, label + '.http.json', meta)


def interval(text):
    start, duration = text.split('/')
    match = re.fullmatch(r'P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?)?', duration)
    require(match is not None, 'unsupported native interval')
    days, hours, minutes = (int(v or 0) for v in match.groups())
    delta = timedelta(days=days, hours=hours, minutes=minutes)
    require(timedelta(minutes=1) <= delta <= timedelta(days=8), 'invalid native duration')
    return instant(start), instant(start) + delta


def verify_documents(points, grid, grid_url):
    """Independent geography/time checks, without W3 normalizer helpers."""
    match = GRID.fullmatch(grid_url)
    require(match is not None, 'invalid grid endpoint')
    p, g = points['properties'], grid['properties']
    require(points['geometry']['type'] == 'Point' and
            points['geometry']['coordinates'][:2] == [-122.33, 47.6], 'regional coordinates mismatch')
    require(p['timeZone'] == 'America/Los_Angeles', 'provider regional zone mismatch')
    require(p['forecastGridData'] == grid_url, 'mapping URL mismatch')
    for obj in (p, g):
        require((obj['gridId'], obj['gridX'], obj['gridY']) ==
                (match[1], int(match[2]), int(match[3])), 'body grid identity mismatch')


def safe_evaluation(result):
    require(result['research_only'] is True and result['recommendation_eligible'] is False and
            result['directions_eligible'] is False and result['photography_verdict'] == 'NOT_EVALUABLE',
            'runtime escaped research boundary')
    require(result['evaluation']['decision'] == 'UNKNOWN', 'raw data became photo verdict')
    require(all(c['state'] == 'UNKNOWN' and c['threshold'] is None and c['model_binding'] is None
                for c in result['evaluation']['conditions']), 'unapproved condition passed')
    def walk(value):
        if isinstance(value, dict):
            require(not any(k.lower() in ('score', 'probability', 'photography_score') for k in value),
                    'unexpected score/probability field')
            for v in value.values():
                walk(v)
        elif isinstance(value, list):
            for v in value:
                walk(v)
    walk(result)


def event_instant(serialized, solar_time):
    """W3 serializes seconds; retain the exact solar instant for coverage checks."""
    actual = instant(solar_time)
    require(instant(serialized) == actual.replace(microsecond=0),
            'solar/weather time differs beyond documented second serialization')
    return actual


def verify_runtime(out, result):
    safe_evaluation(result)
    weather = result['weather']
    require(weather['retrieval_mode'] == 'HTTPS_TLS', 'runtime was not live default TLS')
    require(len(weather['documents']) == 2, 'missing live original bodies')
    raw = [b64decode(d['body_base64'], validate=True) for d in weather['documents']]
    for n, (body, doc) in enumerate(zip(raw, weather['documents'])):
        require(digest(body) == doc['sha256'], 'runtime body hash mismatch')
        (out / ('runtime-' + str(n) + '.body')).write_bytes(body)
    points, grid = map(json.loads, raw)
    verify_documents(points, grid, weather['documents'][1]['url'])
    require(weather['documents'][0]['url'] == POINTS, 'wrong runtime sample')
    retrieved, checked, valid = map(instant, (weather['retrieved_at_utc'],
                                            weather['checked_at_utc'], weather['valid_at_utc']))
    updated = instant(grid['properties']['updateTime'])
    require(updated <= retrieved <= checked <= valid, 'invalid time order')
    require((checked - updated).total_seconds() <= POLICY['max_age_seconds'], 'stale source')
    require(instant(weather['expires_at_utc']) == updated + timedelta(seconds=86400), 'age cutoff mismatch')
    event = result['solar_window'][result['selected_event']]
    serialized_valid = valid
    valid = event_instant(weather['valid_at_utc'], event['time_utc'])
    local = instant(event['time_utc']).astimezone(ZoneInfo('America/Los_Angeles'))
    require(local.isoformat() == event['time_local'] and
            str(local.date()) == result['selected_local_date'], 'local date/UTC offset mismatch')
    canonical = (ROOT / 'data/v2/opportunities/us-071-P01.json').read_bytes()
    require(digest(canonical) == result['canonical_sha256'] ==
            '74c2284bbd1a2aa153330accea265e86fca27fcb23420512d112d750ac7779fc', 'R2 Canonical drift')
    schema = json.loads((ROOT / 'specs/v2/schema/weather-source-record-v0.1.schema.json').read_text())
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    fields = {}
    for field, allowed in UNITS.items():
        layer = grid['properties'].get(field, {})
        values = layer.get('values', [])
        selected = [(v, interval(v['validTime'])) for v in values
                    if interval(v['validTime'])[0] <= valid < interval(v['validTime'])[1]]
        fields[field] = {'uom': layer.get('uom'), 'interval_count': len(values),
                         'null_count': sum(v.get('value') is None for v in values),
                         'matching_intervals': [v for v, _ in selected],
                         'runtime_reasons': weather['fields'][field]['reasons'],
                         'coverage_start_utc': min((interval(v['validTime'])[0].isoformat() for v in values), default=None),
                         'coverage_end_utc': max((interval(v['validTime'])[1].isoformat() for v in values), default=None)}
        record = weather['fields'][field]['record']
        lo, hi = allowed.get(layer.get('uom'), (1, 0))
        usable = (len(selected) == 1 and type(selected[0][0].get('value')) in (int, float)
                  and math.isfinite(selected[0][0]['value']) and lo <= selected[0][0]['value'] <= hi)
        require((record is not None) == usable, 'independent field availability disagrees: ' + field)
        if record is not None:
            validator.validate(record)
            native, (start, end) = selected[0]
            require(record['raw_value'] == native['value'] and record['uom'] == layer['uom'] and
                    instant(record['valid_from_utc']) == start and instant(record['valid_until_utc']) == end,
                    'native field/interval differs: ' + field)
            require(start <= serialized_valid < end and start <= valid < end,
                    'subsecond serialization changed native interval')
            require(record['source_sha256'] == digest(raw[1]) and record['retrieval_mode'] == 'HTTPS_TLS',
                    'record provenance differs')
            rg = record['grid']
            gp = grid['properties']
            require(record['mapping_url'] == POINTS and
                    record['source_url'] == weather['documents'][1]['url'] and
                    instant(record['source_update_time_utc']) == updated and
                    instant(record['retrieved_at_utc']) == retrieved and
                    (rg['office'], rg['grid_x'], rg['grid_y']) == (gp['gridId'], gp['gridX'], gp['gridY']) and
                    (rg['sample_lat'], rg['sample_lon']) == (47.6, -122.33),
                    'record grid/time/sample provenance differs')
    require(len(weather['records']) > 0, 'all fields unavailable')
    save(out, 'independent-verification.json', {'status': 'PASS', 'fields': fields,
         'updated_at_utc': updated.isoformat(), 'retrieved_at_utc': retrieved.isoformat(),
         'valid_at_utc': valid.isoformat(), 'expires_at_utc': weather['expires_at_utc'],
         'serialized_weather_valid_at_utc': weather['valid_at_utc'],
         'event_subsecond_precision_retained_for_coverage': True,
         'refresh_required_before_event': instant(weather['expires_at_utc']) < valid,
         'zone_scope': 'regional sample only; W2 Place zone remains UNKNOWN',
         'provider_issued_at_utc': None, 'provider_run_id': None, 'native_resolution_m': None,
         'model_id': None, 'scientific_admission': 'NOT_GRANTED'})
    args = dict(valid_at=weather['valid_at_utc'], retrieved_at=weather['retrieved_at_utc'],
                as_of=weather['checked_at_utc'], coordinate_source=runtime.SAMPLE['coordinate_source'],
                freshness_policy=POLICY, expected_time_zone=runtime.ZONE)
    replay = nws_snapshot.replay_nws_snapshot(weather['documents'], **args)
    require(replay['retrieval_mode'] == 'TEST_FIXTURE', 'replay falsely live')
    stale = nws_snapshot.replay_nws_snapshot(weather['documents'], **{**args,
        'as_of': (instant(weather['expires_at_utc']) + timedelta(seconds=1)).isoformat(),
        'valid_at': (instant(weather['expires_at_utc']) + timedelta(hours=1)).isoformat()})
    require(stale['source_state'] == 'UNKNOWN' and 'STALE_SOURCE' in stale['reasons'], 'expiry failed open')
    wrong_zone = nws_snapshot.replay_nws_snapshot(weather['documents'], **{**args, 'expected_time_zone': 'Asia/Taipei'})
    require(wrong_zone['source_state'] == 'UNKNOWN', 'zone mismatch failed open')
    damaged = [dict(d) for d in weather['documents']]
    damaged[1]['sha256'] = '0' * 64
    corrupt = nws_snapshot.replay_nws_snapshot(damaged, **args)
    require(corrupt['source_state'] == 'UNKNOWN', 'corrupt hash failed open')
    save(out, 'negative-replay-checks.json', {'replay_mode': replay['retrieval_mode'],
         'stale': stale, 'wrong_zone': wrong_zone, 'corrupt_hash': corrupt,
         'note': 'Archive replays are TEST_FIXTURE, never new real provider evidence.'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--verify-archive', type=Path,
                        help='Offline verification of the original Actions archive; no new HTTPS claim')
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    report = {'status': 'FAIL', 'started_at_utc': stamp(), 'max_requests': 4,
              'retry_count': 0, 'redirects_allowed': False, 'deployment_allowed': False,
              'scientific_admission': 'NOT_GRANTED', 'research_only': True,
              'policy': POLICY, 'run_id': os.environ.get('GITHUB_RUN_ID'),
              'run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT'),
              'candidate_head': os.environ.get('ACCEPTANCE_HEAD_SHA'),
              'checkout_sha': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()}
    try:
        if args.verify_archive is not None:
            archive = args.verify_archive
            original = json.loads((archive / 'acceptance.json').read_text())
            require(original['run_id'] == '39156798749' and
                    original['candidate_head'] == 'ff4742de89004217eb3f8fef1982b252b24d4939',
                    'archive is not the explicitly pinned original Actions capture')
            hashes = json.loads((archive / 'sha256.json').read_text())
            for name, expected in hashes.items():
                require(Path(name).name == name and digest((archive / name).read_bytes()) == expected,
                        'archive digest differs: ' + name)
            points, grid = (json.loads((archive / (label + '.body')).read_bytes())
                            for label in ('points', 'gridpoints'))
            metadata = [json.loads((archive / (label + '.http.json')).read_text())
                        for label in ('points', 'gridpoints')]
            for meta in metadata:
                body = (archive / meta['body_file']).read_bytes()
                require(meta['status'] == 200 and meta['url'] == meta['final_url'] and
                        digest(body) == meta['sha256'] and len(body) == meta['size_bytes'],
                        'original HTTP metadata/body mismatch')
            require(metadata[0]['url'] == POINTS, 'wrong independent sample')
            verify_documents(points, grid, metadata[1]['url'])
            result = json.loads((archive / 'runtime.json').read_text())
            verify_runtime(out, result)
            report.update(status='PASS', mode='OFFLINE_VERIFICATION_OF_ACTIONS_CAPTURE',
                          capture_run_id=original['run_id'], capture_head=original['candidate_head'],
                          capture_completed_at_utc=original['completed_at_utc'], new_http_requests=0,
                          photography_verdict='NOT_EVALUABLE', evaluation_decision='UNKNOWN')
            return 0
        points = capture(out, 'points', POINTS)
        grid_url = points['properties']['forecastGridData']
        require(GRID.fullmatch(grid_url) is not None, 'unsafe mapped URL')
        grid = capture(out, 'gridpoints', grid_url)
        verify_documents(points, grid, grid_url)
        # Tomorrow at Seattle, based on one real UTC clock; never device/UTC civil date.
        local_date = str(datetime.now(timezone.utc).astimezone(ZoneInfo(runtime.ZONE)).date() + timedelta(days=1))
        result = runtime.run_forecast((ROOT / 'data/v2/opportunities/us-071-P01.json').read_bytes(),
                                      local_date=local_date, freshness_policy=POLICY)
        save(out, 'runtime.json', result)
        safe_evaluation(result)
        verify_runtime(out, result)
        report['status'] = 'PASS'
        report['photography_verdict'] = 'NOT_EVALUABLE'
        report['evaluation_decision'] = 'UNKNOWN'
    except Exception as error:
        report['error'] = type(error).__name__ + ': ' + str(error)
    finally:
        report['completed_at_utc'] = stamp()
        save(out, 'acceptance.json', report)
        save(out, 'sha256.json', {p.name: digest(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()})
    print(json.dumps(report, ensure_ascii=False))
    return int(report['status'] != 'PASS')


if __name__ == '__main__':
    raise SystemExit(main())
