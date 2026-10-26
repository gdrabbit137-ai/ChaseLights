"""Genre template registry + expansion mechanism tests (GENRE_CONDITION_TEMPLATES.md 2.6)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'data/v2/tools'))

import apply_template as at  # noqa: E402

TEMPLATES = REPO / 'data/v2/templates'
PROTOTYPE_SPOTS = {
    'cloud_sea': 'tw-001-P02',
    'sunrise': 'tw-036-P01',
    'blue_hour_city': 'tw-002-P01',
    'mountain_view': 'tw-016-P01',
}


class RegistryTests(unittest.TestCase):
    def test_registry_validates(self):
        templates = at.validate_registry()
        statuses = {t['template_id']: t['status'] for t in templates}
        for tid in PROTOTYPE_SPOTS:
            self.assertEqual(statuses[tid], 'defined', tid)
        for tid in ('seasonal_plant',):
            self.assertEqual(statuses[tid], 'scaffold', tid)
        for tid in ('reflection', 'milky_way'):
            self.assertEqual(statuses[tid], 'draft', tid)

    def test_every_metric_in_templates_is_in_vocabulary(self):
        vocab = at.load_vocabulary()
        for path in sorted(TEMPLATES.glob('*.json')):
            if path.name == 'metric-vocabulary.json':
                continue
            t = json.loads(path.read_text(encoding='utf-8'))
            for c in t.get('conditions', []):
                self.assertIn(c['metric'], vocab['metrics'], f'{path.name}/{c["template_ref"]}')

    def test_scaffold_has_owner_todo_and_no_conditions(self):
        for tid in ('seasonal_plant',):
            t = json.loads((TEMPLATES / f'{tid}.json').read_text(encoding='utf-8'))
            self.assertEqual(t['status'], 'scaffold')
            self.assertEqual(t['conditions'], [])
            self.assertTrue(t.get('todo', '').strip())
            self.assertTrue(t.get('purpose_i18n', {}).get('zh-TW', '').strip())

    def test_draft_templates_are_complete_but_refused(self):
        draft_ids = {'milky_way', 'reflection', 'sunset'}
        for tid in draft_ids:
            t = json.loads((TEMPLATES / f'{tid}.json').read_text(encoding='utf-8'))
            self.assertEqual(t['status'], 'draft', tid)
            self.assertTrue(t['conditions'], tid)
            self.assertTrue((t.get('review_note_i18n') or {}).get('zh-TW', '').strip(), tid)
            for c in t['conditions']:
                self.assertIn(c['threshold_source'],
                              ('formula_derived', 'computed', 'evidence_review'),
                              f'{tid}/{c["template_ref"]}')
                for lang in ('zh-TW', 'en', 'ja'):
                    self.assertTrue((c['rationale_i18n'] or {}).get(lang, '').strip(),
                                    f'{tid}/{c["template_ref"]}/{lang}')


class BindingGrammarTests(unittest.TestCase):
    def test_valid_strings(self):
        parsed = at.lint_binding_string(
            'dataset:cwa_wrf3|field:relative_humidity_925hpa_percent|role:SHORT_HQ|level:925hpa')
        self.assertEqual(parsed['dataset'], 'cwa_wrf3')
        self.assertEqual(parsed['role'], 'SHORT_HQ')

    def test_invalid_strings_fail_closed(self):
        for bad in (
            'dataset:cwa_wrf3',                                        # missing field
            'field:x|role:MID',                                        # missing dataset
            'dataset:cwa_wrf3|field:x|role:NO_SUCH_ROLE',              # bad role
            'dataset:cwa_wrf3|field:x|role:MID|bogus:1',               # unknown key
            'dataset:cwa_wrf3|field:x|role:MID|dataset:cams_global',   # duplicate key
            'dataset cwa_wrf3|field:x|role:MID',                       # missing colon
        ):
            with self.assertRaises(SystemExit, msg=bad):
                at.lint_binding_string(bad)

    def test_canonical_bindings_all_lint_clean(self):
        self.assertEqual(at.binding_lint(), 0)


class ExpressionTests(unittest.TestCase):
    def test_arithmetic(self):
        self.assertEqual(at._eval_expr('viewpoint_altitude_m - 200', {'viewpoint_altitude_m': 1090}), 890)
        self.assertEqual(at._eval_expr('(a + b) * 2', {'a': 10, 'b': 15}), 50)

    def test_undeclared_param_fails(self):
        with self.assertRaises(SystemExit):
            at._eval_expr('undeclared - 1', {})

    def test_disallowed_syntax_fails(self):
        with self.assertRaises(SystemExit):
            at._eval_expr('__import__("os")', {})


class ExpansionTests(unittest.TestCase):
    def _expand(self, template_id, opp, params=None, claim_ref=None):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / f'{opp}.json'
            skeleton = REPO / 'data/v2/opportunities' / f'{opp}.json'
            if params is not None:
                pfile = Path(td) / 'params.json'
                pfile.write_text(json.dumps(params), encoding='utf-8')
                at.expand(template_id, opp, skeleton, pfile, out, claim_ref, False)
            else:
                at.expand(template_id, opp, skeleton, None, out, claim_ref, False)
            return json.loads(out.read_text(encoding='utf-8'))

    def test_round_trip_matches_reviewed_canonical(self):
        # rationale_i18n is owner-refinable per spot (e.g. tw-036-P01's DEM
        # horizon fact is spot-level evidence); the template carries the
        # generic wording. Everything else must stay byte-equal.
        RATIONALE_REFINABLE = {'sunrise'}
        for template_id, opp in PROTOTYPE_SPOTS.items():
            expanded = self._expand(template_id, opp,
                                    {'viewpoint_altitude_m': 1090} if template_id == 'cloud_sea' else None,
                                    'tw-036-P01-condition-1' if opp == 'tw-036-P01' else None)
            canonical = json.loads((REPO / 'data/v2/opportunities' / f'{opp}.json').read_text(encoding='utf-8'))
            ec = expanded['condition_contract']['conditions']
            cc = canonical['condition_contract']['conditions']
            self.assertEqual(len(ec), len(cc), opp)
            for e, c in zip(ec, cc):
                self.assertEqual(e['id'], c['id'])
                for key in set(e) | set(c):
                    if key == 'model_binding':
                        self.assertIsNone(c.get(key), f'{opp}: canonical binding should be null')
                        continue
                    if key == 'rationale_i18n' and template_id in RATIONALE_REFINABLE:
                        continue
                    self.assertEqual(e.get(key), c.get(key), f'{opp}/{c["id"]}/{key}')
            meta = expanded['condition_contract']
            self.assertEqual(meta['genre_template'], template_id)
            self.assertEqual(meta['template_version'], f'{template_id}-v0.1')

    def test_expanded_model_binding_strings_lint(self):
        expanded = self._expand('cloud_sea', 'tw-001-P02', {'viewpoint_altitude_m': 1090})
        for c in expanded['condition_contract']['conditions']:
            mb = c['model_binding']
            if mb is not None:
                at.lint_binding_string(mb)

    def test_scaffold_expansion_refused(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(SystemExit):
                at.expand('reflection', 'tw-001-P01',
                          REPO / 'data/v2/migration/skeletons/tw-001-P01.json',
                          None, Path(td) / 'x.json', None, False)

    def test_draft_expansion_refused(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(SystemExit):
                at.expand('sunset', 'tw-016-P01',
                          REPO / 'data/v2/opportunities/tw-016-P01.json',
                          None, Path(td) / 'x.json', None, False)

    def test_undeclared_param_refused(self):
        with tempfile.TemporaryDirectory() as td:
            pfile = Path(td) / 'params.json'
            pfile.write_text(json.dumps({'bogus_param': 1}), encoding='utf-8')
            with self.assertRaises(SystemExit):
                at.expand('cloud_sea', 'tw-001-P02',
                          REPO / 'data/v2/opportunities/tw-001-P02.json',
                          pfile, Path(td) / 'x.json', None, False)

    def test_expansion_never_touches_canonical(self):
        canonical = REPO / 'data/v2/opportunities/tw-001-P02.json'
        before = canonical.read_bytes()
        self._expand('cloud_sea', 'tw-001-P02', {'viewpoint_altitude_m': 1090})
        self.assertEqual(canonical.read_bytes(), before)


class MergeTests(unittest.TestCase):
    def _skeleton(self, td, conditions):
        d = {'opportunity_id': 'tw-999-P99', 'name_i18n': {'zh-TW': '測試', 'en': 'test', 'ja': 'テスト'},
             'condition_contract': {'contract_id': 'CC-tw-999-P99-v1', 'status': 'draft',
                                    'genre_template': 'sunrise', 'template_version': 'sunrise-v0.1',
                                    'recommendation_policy_version': None, 'conditions': conditions}}
        p = Path(td) / 'skeleton.json'
        p.write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8')
        return p

    def _cond(self, mid, metric, op='lte', thr=10, fetch=None):
        c = {'id': f'C-tw-999-P99-{mid}', 'role': 'REQUIRED', 'domain': 'WEATHER',
             'evaluation_mode': 'GUIDANCE', 'capability': 'CONDITIONS', 'condition_tier': 'MAIN',
             'metric': metric, 'operator': op, 'threshold': thr, 'unit': None,
             'unknown_policy': 'propagate_unknown', 'claim_refs': ['tw-999-P99-claim-01'],
             'model_binding': None, 'validation_status': 'provisional',
             'condition_tier': 'MAIN', 'threshold_source': 'formula_derived',
             'calibration_status': 'provisional',
             'rationale_i18n': {'zh-TW': 'x', 'en': 'x', 'ja': 'x'}}
        if fetch:
            c['binding'] = fetch
        return c

    def _merge(self, skeleton_path, template_id, params=None, expect_fail=False):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / 'out.json'
            pfile = None
            if params is not None:
                pfile = Path(td) / 'params.json'
                pfile.write_text(json.dumps(params), encoding='utf-8')
            if expect_fail:
                with self.assertRaises(SystemExit):
                    at.expand(template_id, 'tw-999-P99', skeleton_path, pfile, out, None, False, merge=True)
                return None
            at.expand(template_id, 'tw-999-P99', skeleton_path, pfile, out, None, False, merge=True)
            return json.loads(out.read_text(encoding='utf-8'))

    def test_merge_scoped_overlap_is_allowed(self):
        with tempfile.TemporaryDirectory() as td:
            sk = self._skeleton(td, [self._cond('01', 'cloud_cover_low', 'lte', 55,
                                                fetch={'strategy': 'nearest_gridpoint',
                                                       'gridpoint_selector': 'sun_azimuth_sector'})])
            out = self._merge(sk, 'cloud_sea', {'viewpoint_altitude_m': 1090})
            cc = out['condition_contract']
            metrics = [(c['metric'], (c.get('binding') or {}).get('gridpoint_selector')) for c in cc['conditions']]
            self.assertIn(('cloud_cover_low', 'sun_azimuth_sector'), metrics)
            self.assertIn(('cloud_cover_low', 'basin_cells_below_viewpoint'), metrics)
            self.assertEqual(cc['genre_template'], 'sunrise')  # primary unchanged
            appended = [c for c in cc['conditions'] if c.get('genre_template') == 'cloud_sea']
            self.assertTrue(all(c['template_version'] == 'cloud_sea-v0.1' for c in appended))
            self.assertTrue(all(c['id'].startswith('C-tw-999-P99-') for c in cc['conditions']))

    def test_merge_point_conflict_refused(self):
        with tempfile.TemporaryDirectory() as td:
            sk = self._skeleton(td, [self._cond('01', 'visibility', 'gte', 5)])
            self._merge(sk, 'cloud_sea', {'viewpoint_altitude_m': 1090}, expect_fail=True)
            # cloud_sea T6 visibility >=1, same point scope, different threshold -> refuse

    def test_merge_exact_duplicate_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            sk = self._skeleton(td, [self._cond('01', 'aod_550nm', 'lte', 0.4)])
            out = self._merge(sk, 'cloud_sea', {'viewpoint_altitude_m': 1090})
            aods = [c for c in out['condition_contract']['conditions'] if c['metric'] == 'aod_550nm']
            self.assertEqual(len(aods), 1)

    def test_merge_requires_existing_contract(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'bare.json'
            p.write_text(json.dumps({'opportunity_id': 'tw-999-P99'}), encoding='utf-8')
            with self.assertRaises(SystemExit):
                at.expand('sunset', 'tw-999-P99', p, None, Path(td) / 'o.json', None, False, merge=True)


if __name__ == '__main__':
    unittest.main()