"""CL-DATA-47 — AGLI TW full reconciliation gates.

Covers: 93/93 tw catalog places, deterministic weighted synthesis,
monotonic ranking, unique ids, L1 rankings present, source tags valid.
"""
import json
import os
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
FULL = os.path.join(REPO, 'data', 'v2', 'audits', 'agli', 'agli-tw-full.json')
CAT = os.path.join(REPO, 'apps', 'web-v2', 'catalog.v2.json')

WEIGHTS = {'grandeur': 20, 'uniqueness': 20, 'visual': 15, 'richness': 10,
           'photo': 15, 'season': 10, 'experience': 5, 'cultural': 5}


class TestCLData47AgliTwFull(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(FULL, encoding='utf-8') as f:
            cls.full = json.load(f)
        with open(CAT, encoding='utf-8') as f:
            cls.cat = json.load(f)

    def test_coverage_93_of_93(self):
        tw_ids = {p['place_id'] for p in self.cat['places'] if p['place_id'].startswith('tw-')}
        self.assertEqual(len(tw_ids), 93, 'catalog tw count drifted — re-anchor this pin')
        rec_ids = {r['place_id'] for r in self.full['records']}
        self.assertEqual(rec_ids, tw_ids)
        self.assertEqual(len(self.full['records']), 93)
        self.assertEqual(len(self.full['ranking']), 93)

    def test_unique_ids_and_monotonic_order(self):
        ids = [r['place_id'] for r in self.full['records']]
        self.assertEqual(len(ids), len(set(ids)))
        aglis = [r['agli'] for r in self.full['ranking']]
        self.assertEqual(aglis, sorted(aglis, reverse=True))

    def test_deterministic_weighted_synthesis(self):
        for r in self.full['records']:
            merged = r['merged']
            expect = round(sum(merged[d] * WEIGHTS[d] for d in WEIGHTS) / 100.0, 1)
            self.assertEqual(expect, r['agli'],
                             f"{r['place_id']}: weighted synthesis {expect} != stored {r['agli']}")

    def test_dims_complete_and_in_range(self):
        for r in self.full['records']:
            self.assertEqual(set(r['merged']), set(WEIGHTS))
            for d, v in r['merged'].items():
                self.assertTrue(0 <= v <= 100, f"{r['place_id']} {d}={v}")

    def test_provenance_and_confidence_present(self):
        for r in self.full['records']:
            self.assertIn(r['confidence'], ('high', 'medium', 'low'))
            self.assertIn(r['source'], ('pilot-reuse', 'batch1', 'batch2', 're-eval-47', 'gap-fill-47'))
            self.assertTrue(r['evidence_note'])
            self.assertIn(r['l1'], self.full['l1_region_rankings'])

    def test_l1_region_rankings_complete(self):
        for l1, rows in self.full['l1_region_rankings'].items():
            aglis = [x['agli'] for x in rows]
            self.assertEqual(aglis, sorted(aglis, reverse=True))

    def test_no_90_plus_inflation(self):
        self.assertEqual(self.full['summary']['n_90_plus'], 0,
                         '95+ requires a named global comparator per method §2')

    def test_summary_matches_records(self):
        s = self.full['summary']
        self.assertEqual(s['n'], len(self.full['records']))
        self.assertEqual(sum(s['anchor_bands'].values()), 93)
        self.assertEqual(sum(s['confidence'].values()), 93)


if __name__ == '__main__':
    unittest.main()
