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

    def test_coverage_tw_full(self):
        tw_ids = {p['place_id'] for p in self.cat['places'] if p['place_id'].startswith('tw-')}
        self.assertEqual(len(tw_ids), 175, 'catalog tw count drifted — re-anchor this pin (CL-INT-135 merged tree: 116 AGLI-active tw + 59 CL-DATA-66 wave1-4 scoreless tw-125..183)')
        rec_ids = {r['place_id'] for r in self.full['records']}
        # CL-DATA-66 wave1 is SCORELESS (owner ruling 2026-11-11): no AGLI dual-board,
        # agli-final.json untouched — the 22 wave1 places (tw-125..146) stay out of this
        # full reconciliation until they are scored; every other tw place must be covered.
        scoreless = {f'tw-{n}' for n in range(125, 184)}
        self.assertEqual(rec_ids, tw_ids - scoreless)
        self.assertEqual(len(self.full['records']), 116)
        self.assertEqual(len(self.full['ranking']), 116)

    def test_unique_ids_and_monotonic_order(self):
        ids = [r['place_id'] for r in self.full['records']]
        self.assertEqual(len(ids), len(set(ids)))
        aglis = [r['agli'] for r in self.full['ranking']]
        self.assertEqual(aglis, sorted(aglis, reverse=True))

    def test_deterministic_weighted_synthesis(self):
        for r in self.full['records']:
            merged = r['merged']
            if r.get('gli_version') == '64-direct-v2':
                # CL-DATA-64: experience/cultural are low-confidence estimates and are
                # NOT SCORED in v2 — the 8-dim v1 synthesis does not apply; the v2
                # dual-board L/P live in agli-final.json (gate-kept by the 64 tests).
                self.assertEqual(sorted(k for k, v in merged.items() if v is None),
                                 ['cultural', 'experience'])
                continue
            expect = round(sum(merged[d] * WEIGHTS[d] for d in WEIGHTS) / 100.0, 1)
            self.assertEqual(expect, r['agli'],
                             f"{r['place_id']}: weighted synthesis {expect} != stored {r['agli']}")

    def test_dims_complete_and_in_range(self):
        for r in self.full['records']:
            self.assertEqual(set(r['merged']), set(WEIGHTS))
            for d, v in r['merged'].items():
                if r.get('gli_version') == '64-direct-v2':
                    # CL-DATA-64: experience/cultural honestly not scored (None)
                    self.assertIn(v, (None,) + tuple(range(101)), f"{r['place_id']} {d}={v}")
                else:
                    self.assertTrue(0 <= v <= 100, f"{r['place_id']} {d}={v}")

    def test_provenance_and_confidence_present(self):
        for r in self.full['records']:
            self.assertIn(r['confidence'], ('high', 'medium', 'low'))
            self.assertIn(r['source'], ('pilot-reuse', 'batch1', 'batch2', 're-eval-47', 'gap-fill-47', 'cl-data-51-direct', 'cl-data-64-direct'))
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
