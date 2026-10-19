"""W1 contract/negative examples only. No weather transport, model or live evidence."""
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import unittest
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / 'specs/v2/schema/hourly-weather-info-v0.1.schema.json'
FIXTURE = ROOT / 'specs/v2/tests/fixtures/hourly/synthetic-partial.json'
BINDING = ROOT / 'data/v2/weather-pilots/tw-036-open-meteo.json'


def example():
    return json.loads(FIXTURE.read_text())


def instant(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def contract_errors(payload):
    """Test-only executable semantic examples for the written W3 acceptance gate.

    This does not normalize provider data or authenticate a live capture.
    """
    validator = Draft202012Validator(json.loads(SCHEMA.read_text()), format_checker=FormatChecker())
    errors = [e.message for e in validator.iter_errors(payload)]
    if errors:
        return errors
    def finite_tree(value):
        if isinstance(value, float) and not math.isfinite(value):
            errors.append('nonfinite JSON number')
        elif isinstance(value, dict):
            for child in value.values(): finite_tree(child)
        elif isinstance(value, list):
            for child in value: finite_tree(child)
    finite_tree(payload)
    if payload['pilot_binding_sha256'] != hashlib.sha256(BINDING.read_bytes()).hexdigest():
        errors.append('pilot hash')
    params = {k: [str(v)] for k, v in payload['request'].items() if k != 'coordinate_role'}
    if parse_qs(urlsplit(payload['source']['source_url']).query) != params:
        errors.append('request identity')
    source = payload['source']; policy = payload['retrieval_age_policy']
    retrieved = instant(source['retrieved_at_utc']); normalized = instant(source['normalized_at_utc'])
    checked = instant(policy['checked_at_utc'])
    if not retrieved <= normalized <= checked:
        errors.append('clock order')
    stale = (checked - retrieved).total_seconds() > policy['max_age_seconds']
    if stale != (payload['availability'] == 'STALE'):
        errors.append('stale state')
    previous = None
    all_available = True
    for row in payload['hours']:
        t = instant(row['valid_at_utc']); interval = row['preceding_hour']
        if t.minute or t.second or t.microsecond or (previous and (t-previous).total_seconds() != 3600):
            errors.append('hour axis')
        if instant(interval['end_utc']) != t or instant(interval['start_utc']) != t-timedelta(hours=1):
            errors.append('previous hour')
        previous = t
        for cell in row['values'].values():
            all_available &= cell['state'] == 'AVAILABLE'
            if cell['value'] is not None and not math.isfinite(cell['value']):
                errors.append('nonfinite')
    complete = len(payload['hours']) == 72 and all_available
    if not stale and (payload['availability'] == 'COMPLETE') != complete:
        errors.append('complete state')
    return errors


class HourlyWeatherPilotContract(unittest.TestCase):
    def test_strict_additive_schema_and_synthetic_partial_example(self):
        Draft202012Validator.check_schema(json.loads(SCHEMA.read_text()))
        self.assertEqual(contract_errors(example()), [])
        self.assertEqual(example()['source']['retrieval_mode'], 'TEST_FIXTURE')

    def test_missing_is_null_and_genuine_zero_is_distinct(self):
        x = example(); cell = x['hours'][0]['values']['precipitation']
        self.assertIsNone(cell['value'])
        cell.update(value=0, state='AVAILABLE', reason_code=None, source_unit='mm')
        self.assertEqual(contract_errors(x), [])
        cell.update(state='UNAVAILABLE', reason_code='MISSING_FIELD')
        self.assertTrue(contract_errors(x))

    def test_every_requested_field_is_required_but_nullable(self):
        original = example()
        for key in original['hours'][0]['values']:
            x = copy.deepcopy(original); del x['hours'][0]['values'][key]
            with self.subTest(key=key): self.assertTrue(contract_errors(x))

    def test_unit_boolean_range_and_nonfinite_cannot_be_available(self):
        for key, value, unit in [('cloud_cover_low',101,'%'), ('wind_speed_10m',-1,'m/s'),
                                 ('visibility',True,'m'), ('precipitation',float('nan'),'mm'),
                                 ('temperature_2m',10,'°F')]:
            x = example(); x['hours'][0]['values'][key].update(value=value,state='AVAILABLE',reason_code=None,source_unit=unit)
            with self.subTest(key=key): self.assertTrue(contract_errors(x))

    def test_no_score_navigation_favorable_or_forged_model_update(self):
        for key, value in [('score',100), ('recommendation_eligible',True), ('photography_verdict','FAVORABLE'), ('directions','https://maps.invalid')]:
            x=example();x[key]=value
            with self.subTest(key=key):self.assertTrue(contract_errors(x))
        for key, value in [('source_update_time_utc','2026-10-19T09:00:00Z'),('provider_run_id','guessed'),('native_time_resolution_seconds',3600)]:
            x=example();x['source'][key]=value
            with self.subTest(key=key):self.assertTrue(contract_errors(x))

    def test_binding_place_sample_timezone_and_request_identity(self):
        for key,value in [('pilot_binding_sha256','0'*64),('place_id','us-071'),('time_zone','UTC')]:
            x=example();x[key]=value
            with self.subTest(key=key):self.assertTrue(contract_errors(x))
        x=example();x['request']['latitude']=121.62717;self.assertTrue(contract_errors(x))
        x=example();x['source']['source_url']+='&models=guessed';self.assertTrue(contract_errors(x))

    def test_previous_hour_is_not_shifted_forward_or_used_for_instant_fields(self):
        x=example(); row=x['hours'][0]
        self.assertEqual(instant(row['valid_at_utc'])-instant(row['preceding_hour']['start_utc']),timedelta(hours=1))
        row['preceding_hour']['start_utc']=row['valid_at_utc']
        row['preceding_hour']['end_utc']='2026-10-19T17:00:00Z'
        self.assertTrue(contract_errors(x))

    def test_taipei_midnight_has_next_local_date_and_previous_hour_support(self):
        row=example()['hours'][0];zone=ZoneInfo('Asia/Taipei')
        t=instant(row['valid_at_utc']).astimezone(zone)
        self.assertEqual(t.isoformat(),'2026-10-20T00:00:00+08:00')
        self.assertEqual(instant(row['preceding_hour']['start_utc']).astimezone(zone).date().isoformat(),'2026-10-19')
        self.assertNotEqual(t.date(),instant(row['valid_at_utc']).date())

    def test_duplicate_gapped_descending_and_nonhourly_times_rejected(self):
        for t in ['2026-10-19T16:00:00Z','2026-10-19T18:00:00Z','2026-10-19T15:00:00Z','2026-10-19T17:30:00Z']:
            x=example();second=copy.deepcopy(x['hours'][0]);second['valid_at_utc']=t;x['hours'].append(second)
            with self.subTest(time=t):self.assertTrue(contract_errors(x))

    def test_stale_boundary_and_future_or_reversed_clocks(self):
        x=example();x['retrieval_age_policy']['checked_at_utc']='2026-10-19T15:00:00Z'
        self.assertEqual(contract_errors(x),[])
        x['retrieval_age_policy']['checked_at_utc']='2026-10-19T15:00:01Z';self.assertTrue(contract_errors(x))
        x['availability']='STALE';self.assertEqual(contract_errors(x),[])
        x['retrieval_age_policy']['checked_at_utc']='2026-10-19T08:00:00Z';self.assertTrue(contract_errors(x))

    def test_partial_cannot_claim_complete_and_no_hidden_locale_fallback(self):
        x=example();x['availability']='COMPLETE';self.assertTrue(contract_errors(x))
        x=example();del x['limitations_i18n']['ja'];self.assertTrue(contract_errors(x))
        x=example();x['hours']=[];self.assertTrue(contract_errors(x))

    def test_other_existing_provider_and_date_query_contracts_remain_separate(self):
        nws=json.loads((ROOT/'specs/v2/schema/weather-source-record-v0.1.schema.json').read_text())
        self.assertEqual(nws['properties']['provider']['const'],'NOAA_NWS')
        validator=Draft202012Validator(nws,format_checker=FormatChecker())
        self.assertTrue(list(validator.iter_errors(example())))
        query=json.loads((ROOT/'specs/v2/schema/date-query-v0.1.schema.json').read_text())
        self.assertTrue(list(Draft202012Validator(query,format_checker=FormatChecker()).iter_errors(example())))


if __name__ == '__main__':
    unittest.main()
