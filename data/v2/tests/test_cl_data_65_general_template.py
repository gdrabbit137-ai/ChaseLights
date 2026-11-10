"""CL-DATA-65: general-v0.1 genre template + zero-curated-subject auto-mount.

Covers: template registry semantics (all REQUIRED, no BONUS), schema-valid
mounted opportunity, mount scan classification (curated present / retired
hidden / mount), scale parameterization, no-overwrite idempotency.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'data/v2/tools'))
sys.path.insert(0, str(ROOT / 'data/v2/migration'))

import apply_template as at  # noqa: E402
import mount_general_opportunities as mg  # noqa: E402

TEMPLATES = ROOT / 'data/v2/templates'
SCHEMA = ROOT / 'specs/v2/schema/opportunity-v2.1.schema.json'
P99 = ROOT / 'data/v2/opportunities/jp-030-P99.json'


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bs = _load_module('build_skeletons_cl65', ROOT / 'data/v2/migration/build_skeletons.py')


class RegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = json.loads((TEMPLATES / 'general.json').read_text(encoding='utf-8'))
        cls.vocab = at.load_vocabulary()
        cls.templates = {x['template_id']: x for x in at.validate_registry()}

    def test_general_defined_and_registered(self):
        self.assertEqual(self.t['template_id'], 'general')
        self.assertEqual(self.t['version'], '0.1')
        self.assertEqual(self.templates['general']['status'], 'defined')

    def test_all_conditions_required_no_bonus(self):
        conds = self.t['conditions']
        self.assertEqual(len(conds), 4)
        for c in conds:
            self.assertEqual(c['role'], 'REQUIRED', c['template_ref'])
            self.assertNotIn(c['role'], ('QUALITY', 'BLOCKER'), c['template_ref'])
            self.assertEqual(c.get('condition_tier'), 'MAIN')
            self.assertNotIn('activate_when', c, 'no BONUS/modifier semantics')
        self.assertEqual([c['metric'] for c in conds],
                         ['visibility', 'precipitation',
                          'relative_humidity_925hpa', 'light_window'])

    def test_metrics_in_vocabulary(self):
        for c in self.t['conditions']:
            self.assertIn(c['metric'], self.vocab['metrics'])

    def test_visibility_threshold_parameterized_by_scale(self):
        v = next(c for c in self.t['conditions'] if c['metric'] == 'visibility')
        self.assertEqual(v['operator'], 'gte')
        self.assertEqual(v['threshold'], {'expr': 'view_scale_km'})
        self.assertEqual(v['threshold_source'], 'computed')
        params = [p['name'] for p in self.t['params']]
        self.assertEqual(params, ['view_scale_km'])

    def test_scale_semantics_documented(self):
        desc = self.t['params'][0]['description_i18n']['zh-TW']
        for token in ('8', '5', '3'):
            self.assertIn(token, desc)
        owner = self.t['owner_review']
        self.assertIn('view_scale_km', owner)

    def test_three_language_rationales(self):
        for c in self.t['conditions']:
            for lang in ('zh-TW', 'en', 'ja'):
                self.assertTrue((c['rationale_i18n'] or {}).get(lang, '').strip(),
                                f"{c['template_ref']}/{lang}")

    def test_evaluation_pipeline_compat(self):
        # light_window is a known time-window metric (EVALGATE stands down);
        # visibility/precipitation/relative_humidity_925hpa are open-meteo
        # batch mapped (threshold_observations METRIC_FIELDS).
        p = (ROOT / 'packages/core-v2/tools/evaluate_batch.py').read_text(encoding='utf-8')
        self.assertIn('"light_window"', p)
        t = (ROOT / 'packages/core-v2/adapters/threshold_observations.py').read_text(encoding='utf-8')
        for metric in ('"visibility"', '"precipitation"', '"relative_humidity_925hpa"'):
            self.assertIn(metric, t)


class ScaleTests(unittest.TestCase):
    def test_scale_for_place(self):
        self.assertEqual(mg.scale_for_place(['overlook', 'sunset']), 8)
        self.assertEqual(mg.scale_for_place(['mountain_view']), 8)
        self.assertEqual(mg.scale_for_place(['waterfall', 'tidal']), 3)
        self.assertEqual(mg.scale_for_place(['geological_landform']), 3)
        self.assertEqual(mg.scale_for_place(['reflection']), 3)
        self.assertEqual(mg.scale_for_place([]), 5)
        self.assertEqual(mg.scale_for_place(['sunrise', 'seasonal_plant']), 5)


class MountScanTests(unittest.TestCase):
    def test_scan_classification(self):
        place_index = {'places': [{'place_id': 'a'}, {'place_id': 'b'}, {'place_id': 'c'},
                                  {'place_id': 'd'}]}
        docs = {
            'a-P01': {'opportunity_id': 'a-P01', 'place_id': 'a',
                      'condition_contract': {'genre_template': 'overlook'},
                      'lifecycle_status': 'draft'},
            'b-P01': {'opportunity_id': 'b-P01', 'place_id': 'b',
                      'condition_contract': {'genre_template': 'sunset'},
                      'lifecycle_status': 'retired'},
            'c-P01': {'opportunity_id': 'c-P01', 'place_id': 'c',
                      'condition_contract': {'genre_template': None},
                      'lifecycle_status': 'draft'},
        }
        skip, targets = mg.places_to_mount(place_index, docs)
        self.assertEqual(skip['a'], 'curated_subject_present')
        self.assertEqual(skip['b'], 'retired_hidden')
        self.assertEqual(targets, {'c': [], 'd': []})


class MountedOpportunityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not P99.exists():
            raise unittest.SkipTest('jp-030-P99 not mounted yet')
        cls.doc = json.loads(P99.read_text(encoding='utf-8'))
        cls.schema = json.loads(SCHEMA.read_text(encoding='utf-8'))

    def test_schema_valid(self):
        self.assertEqual([], bs.validate_document(self.doc, self.schema))

    def test_identity_and_genre(self):
        self.assertEqual(self.doc['opportunity_id'], 'jp-030-P99')
        self.assertEqual(self.doc['place_id'], 'jp-030')
        self.assertEqual(self.doc['lifecycle_status'], 'draft')
        cc = self.doc['condition_contract']
        self.assertEqual(cc['genre_template'], 'general')
        self.assertEqual(len(cc['conditions']), 4)
        for c in cc['conditions']:
            self.assertEqual(c['role'], 'REQUIRED')

    def test_honest_provenance_and_geometry(self):
        prov = self.doc['provenance']
        self.assertEqual(prov['review_status'], 'pending')
        self.assertEqual(prov['source_catalog'], 'general_genre_mount_v0.1')
        geo = self.doc['camera_contexts'][0]['geometry']
        self.assertEqual(geo['derivation_method'],
                         'inherited_from_place_opportunity_geometry')
        self.assertEqual(geo['status'], 'provisional')

    def test_no_overwrite_idempotent(self):
        before = P99.read_bytes()
        rc = mg.main(['--write', '--place-id', 'jp-030'])
        self.assertEqual(rc, 0)
        self.assertEqual(P99.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
