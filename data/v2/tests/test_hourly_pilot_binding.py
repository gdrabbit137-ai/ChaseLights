"""W2 single-place evidence bindings, not live-provider or legal-access evidence."""
import hashlib
import json
from pathlib import Path
import unittest
from zoneinfo import ZoneInfo
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[3]
PATH=ROOT/'data/v2/weather-pilots/tw-036-open-meteo.json'

class HourlyPilotBinding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binding=json.loads(PATH.read_text())

    def test_real_existing_place_and_canonical_blob_binding(self):
        b=self.binding;p=ROOT/b['canonical_binding']['path'];raw=p.read_bytes();c=json.loads(raw)
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        self.assertEqual(blob,b['canonical_binding']['blob_sha'])
        self.assertEqual(c['place_id'],b['place_id']);self.assertEqual(c['opportunity_id'],b['opportunity_context_id'])

    def test_official_sample_has_explicit_role_not_camera_or_navigation(self):
        s=self.binding['sample']
        self.assertEqual((s['latitude'],s['longitude']),(24.031426,121.62717))
        self.assertEqual(s['coordinate_role'],'representative_place_weather_sample')
        self.assertIsNone(s['coordinate_uncertainty_m'])
        self.assertFalse(s['camera_coordinate_verified']);self.assertFalse(s['navigation_eligible'])
        evidence={x['id']:x for x in self.binding['evidence']}
        self.assertIn('taiwan.net.tw',evidence[s['coordinate_source_ref']]['url'])

    def test_place_specific_timezone_has_geography_standard_time_and_iana_evidence(self):
        b=self.binding;self.assertEqual(b['time_zone']['status'],'VERIFIED')
        self.assertEqual(b['time_zone']['iana_id'],'Asia/Taipei')
        self.assertEqual(set(b['time_zone']['evidence_ids']),{x['id'] for x in b['evidence']})
        self.assertEqual(len(b['time_zone']['evidence_ids']),3)
        local=datetime(2026,10,19,16,tzinfo=timezone.utc).astimezone(ZoneInfo(b['time_zone']['iana_id']))
        self.assertEqual(local.date().isoformat(),'2026-10-20')

    def test_sidecar_does_not_promote_existing_index_or_geometry(self):
        c=json.loads((ROOT/self.binding['canonical_binding']['path']).read_text())
        self.assertTrue(all(x['geometry']['geojson'] is None for x in c['camera_contexts']))
        self.assertTrue(all(x['lat'] is None and x['lon'] is None and x['status']!='verified' for x in c['navigation_targets']))
        idx=json.loads((ROOT/'data/v2/indexes/research/place-index.json').read_text())
        place=next(x for x in idx['places'] if x['place_id']=='tw-036')
        self.assertEqual(place['time_zone']['status'],'UNKNOWN')
        self.assertFalse(self.binding['usage_admission']['public_release_authorized'])

    def test_noncommercial_budget_locale_and_unperformed_capture_are_explicit(self):
        b=self.binding;u=b['usage_admission']
        self.assertEqual(u['scope'],'NONCOMMERCIAL_RESEARCH_PILOT_ONLY')
        self.assertEqual(u['max_captures_per_day']*u['max_http_attempts_per_capture'],24)
        self.assertEqual(u['min_refresh_interval_seconds'],10800)
        self.assertEqual(set(b['limitations_i18n']),{'zh-TW','en','ja'})
        self.assertTrue(all(b['limitations_i18n'].values()))
        self.assertEqual(b['review']['live_provider_capture'],'NOT_PERFORMED')
        self.assertEqual(b['review']['external_human_signoff'],'PENDING')

if __name__=='__main__':unittest.main()
