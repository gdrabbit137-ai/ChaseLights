"""Task X real-source consistency + fail-closed regressions, no network/research.

Use CHASELIGHTS_W1_SPEC_ROOT=<pinned #489 checkout>/specs/v2. Missing dependency
is an ERROR, never SKIP or validation against the old main schema by accident.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[3]
MODULE=ROOT/'data/v2/tools/research_index.py'
spec=importlib.util.spec_from_file_location('task_x_index',MODULE)
x=importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)


class ResearchIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value=os.environ.get('CHASELIGHTS_W1_SPEC_ROOT')
        if not value:
            raise RuntimeError('Required pinned W1 #489: set CHASELIGHTS_W1_SPEC_ROOT; no SKIP/fallback')
        cls.w1_root=Path(value)
        cls.lock=x.read(x.INDEX/'source-lock.json')
        cls.w1=x.load_w1(cls.w1_root,cls.lock)
        cls.sources=x.verify_sources(cls.lock)
        cls.index=x.read(x.INDEX/'place-index.json')
        cls.topics=x.read(x.INDEX/'topic-index.json')
        cls.provenance=x.read(x.INDEX/'field-provenance.json')
        cls.status=x.read(x.INDEX/'index-status.json')
        cls.docs={p['opportunity_id']:x.read(ROOT/p['path']) for p in cls.lock['canonical_records']}

    def test_pinned_w1_six_schemas_and_semantic_bundle(self):
        self.assertEqual([],x.validate(self.w1_root))
        for kind in x.KINDS:
            doc=(self.index if kind=='place-index' else self.topics if kind=='topic-index'
                 else x.read(x.DATA/f'tests/fixtures/task-x/{kind}.json'))
            with self.subTest(kind=kind):self.assertEqual([],self.w1.structural(kind,doc))

    def test_exact_unique_complete_place_and_opportunity_sets(self):
        expected_places={d['place_id'] for d in self.docs.values()}
        actual=[p['place_id'] for p in self.index['places']]
        ids=[b['opportunity_id'] for b in self.index['opportunities']]
        self.assertEqual(expected_places,set(actual));self.assertEqual(len(actual),len(set(actual)))
        self.assertEqual(set(self.docs),set(ids));self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual((232,420),(len(actual),len(ids)))  # re-anchored CL-DATA-32 (14 southern-Japan additions)
        self.assertEqual(3,sum(b['place_id']=='tw-026' for b in self.index['opportunities']))

    def test_real_canonical_blob_sha256_identity_and_revision(self):
        self.assertEqual([],self.w1.validate_index(self.index,self.sources))
        for pin in self.lock['canonical_records']:
            raw=(ROOT/pin['path']).read_bytes();d=json.loads(raw)
            self.assertEqual(pin['blob_sha'],x.blob(raw))
            self.assertEqual(pin['sha256'],hashlib.sha256(raw).hexdigest())
            self.assertEqual((pin['opportunity_id'],d['place_id'],d['revision']),
                             (d['opportunity_id'],d['place_id'],d['revision']))
        self.assertEqual({
            # CL-DATA-02 owner ruling 2026-11-02: the six review-gated records
            # re-pinned to the ruling data commit 76e926d16 (rollback pointer
            # for the original human-review contracts: 34cb70f39 and earlier).
            '34cb70f39f8d959e9b68cfa3a6768a74cb29de99',
            '06b51d046fd391ab44708535464e7478cfc13ee4',
            '3eb466432807185bc8b9271d006666b72d1fa406',
            # CL-INT-83: the 8 CL-DATA-18 AI-verified fill records
            # (tw-034-P02/tw-036-P01/tw-082-P01/jp-010-P01/us-071-P01/
            # tw-026-P01/tw-026-P02/us-057-P01) anchored to the provenance
            # commit 2af08fb9e — merged checkout bytes verified byte-identical
            # to the branch fills (union with CL-INT-82/85/86 main).
            '2af08fb9eec9994ab5862197c4a0d8a45587e440',
            # CL-DATA-04: three new owner-defined records pinned to the
            # owner-definition data commit. (tw-086-P02 — the last holder of
            # cebb9689 — was byte-changed and re-pinned by CL-DATA-16, so the
            # cebb9689 pin left the set.)
            # CL-UI-20 round-2: 63 high-exposure subject records re-pinned to
            # the task-branch commit carrying verified en/ja subject names
            # (tw-036-P01 / tw-082-P01 keep their review-gated round-1 pins).
            'b97f7bb87a46db4a3e21922d7f6058b8b64a6385',
            # CL-UI-25: 22 city_night contracts re-pinned to the task-branch
            # commit adding the contract-level city_night_window condition
            # (mirrors the CL-UI-23 evaluation-layer gate semantics).
            '6a420db5100bb184f655b4b765d29fdf3494588d',
            # CL-DATA-09: tw-027-P02 re-pinned to the task-branch commit adding
            # the contract-level city_night_window condition (civil darkness
            # <= -6 deg; TIME_SPECIALIZATION §3 misplacement, owner ruling
            # 2026-11-05, CL-UI-25 same-source definition). CL-DATA-12 later
            # re-pinned those records (batch e moon-triple removal, civil
            # twilight only) to d57d40f89 — see below.
            # CL-UI-36: rationale_i18n review-note strip re-pinned the affected
            # canonical records to the task-branch commit holding the new bytes.
            # (dce2f6ed0812... retired by CL-DATA-19: its last six records
            # jp-007-P01/tw-045-P02/tw-054-P01/tw-056-P02/tw-082-P02/us-069-P01
            # gained the civil light_window and were re-pinned to e261cc9817e.)
            '4e51267ba7b7130d28efa41e50d2ef3d36de81a8',
            # CL-DATA-12: wave-1 semantic corrections (batches A–O) re-pinned
            # the touched records to the contract commits, and the three
            # migration-skeleton tidal records were restored to their
            # reviewed-main bytes (commit 86cc3d9bd).
            'd57d40f8966631783f1385908659bd8c1b82adbd',
            '86cc3d9bdfaaac110f65361ac77df744cdd4cfa1',
            # CL-DATA-13: the touched records' bytes changed (view_azimuth
            # backfill + light_direction pilot contracts) and their blob pins
            # were re-anchored below, but the W2 provenance commit_sha of each
            # record is preserved (bytes live at the recorded provenance
            # commits' successors; the blob pins carry the new state).
            # CL-DATA-14 merge (3682e14ec): 10 records byte-changed by the
            # CL-PHOTO-02 audit corrections (seasonal_state unions etc.) and
            # 37 stale commit_sha provenance pointers (CL-CI-14 latent)
            # re-pointed to the merge commit carrying the verified bytes.
            '3682e14ec5ed7eb4b78d2b7a47d0b43c1b836c98',
            # CL-CI-22 merged-tree re-anchor: per-record pins from the merged
            # CL-DATA-24/25/26 branches (69b832acc dusk-phase repin,
            # 64685ff7d tw-017-P03 blue-hour note, 2cd38d860 CL-INT-89 pin
            # restore). CL-DATA-32 later re-pinned tw-010-P01 (008ab85ff) when
            # the golden-window upgrade gave way to sunrise_time_window MAIN.
            '69b832accfc8c0438a50e51689c4e7c40765e9f4',
            '64685ff7df762f588bd1f276a56f7c007c07b8c2',
            '008ab85ff19794c3aa2ffc1173afa30212aa426e',
            '2cd38d860868d63b7a214434d74f2db6ad153506',
            'b801dd4eba545a76879828b25e869f3c45df33ac',
            # CL-DATA-15 (merged side): owner-verified elevation corrections
            # (Paiyun Lodge 3,402 m / Datun 1,092 m / Zhushan 2,451 m;
            # Hehuan 3,417 m confirmed) — tw-001-P02/tw-019-P04/tw-024-P02/
            # tw-040-P04 byte-changed on main after CL-DATA-16 forked and
            # remain re-pinned to the task-branch commit carrying those
            # corrections (union merge, CL-INT-81).
            'c90f56712550ae46824e30684442bbc44855c9b5',
            # CL-DATA-20: 18 tailored contracts + 3 byte-changed records
            # (tw-059-P01/tw-078-P01 tidal genre, tw-016-P01 summit geometry)
            # pinned to the data commit.
            'a4f803a7106816773ef5a2f659271c656b873bd7',
            # CL-DATA-19: 126 mid-latitude all-day contracts gained a civil
            # light_window (REQUIRED/MAIN, sun elevation > -6 deg, CL-DATA-11
            # same-source definition); canonical records re-pinned to the
            # contract commit holding the new bytes.
            'e261cc9817e720d852bd5aee9b1b555edd253d8c',
            # CL-INT-78 merge (7a290aa08 -> re-pointed at the CL-INT-86
            # re-merge db04b94f3): the CL-DATA-17 US coordinate/elevation
            # records re-pointed to the merge commit carrying the merged
            # verified bytes (union with CL-DATA-19 re-pins).
            'db04b94f3a0a6e78bff000e3c97ffb80fee2daf5',
            # CL-DATA-25: 37 admitted discovery contracts (25 places) pinned
            # to the admission commit carrying the evidence-ref + renumber bytes.
            'a34cd15819a1b01702d6d38408524e444ca84906',
            # CL-DATA-25R: tw-098 渭水之丘／櫻花陵園 (rubric v2 3.8) admitted;
            # its two canonical records pinned to the 25R stage-1 data commit.
            'd587d0d8c31dee9853e53207a00e9cbd7a1940e7',
            # CL-DATA-28: subject-name vs qualifying-hours fixes — tw-008-P01
            # (city_night_window -> blue_hour_window phase=dusk, Mt. Guanyin/
            # Bitan precedent) and tw-010-P02 (golden_hour_window -> REQUIRED/
            # MAIN dawn/dusk window, tw-010-P01 CL-DATA-26 precedent) re-pinned
            # to the contract commit carrying the new bytes.
            '2d9af4d86856301e22df74153d9ff67d1500bc42',
            # CL-DATA-32: 14 southern-Japan admitted discovery contracts
            # (jp-051..jp-064, PM-judgment admission) pinned to the admission
            # commit carrying the evidence-ref + revision-2 bytes.
            'dda29699705dcdf9ced993bca06316e1085a15e9',
            # CL-INT-103 union: tw-034-P02 re-pinned to the CL-DATA-33 light_window
            # revision commit (git-show verifiable at the merged tree HEAD).
            '1edb5ced42e689cbf29dc523ebe6028d4a72f936',
            # CL-DATA-36: 60 batch2 access-verified records re-pinned to the
            # stage-1 commit carrying the e-d36 evidence-ref + revision-2 bytes.
            '21198c9cc91e00cdd3df8daea76aac46bf9fb45b',
        }, {p['commit_sha'] for p in self.lock['canonical_records']})
        p01=next(p for p in self.lock['canonical_records'] if p['opportunity_id']=='tw-026-P01')
        # CL-INT-83: tw-026-P01 anchored to the provenance commit carrying
        # the CL-DATA-18 AI-verified fill bytes (union with CL-INT-82/85).
        self.assertEqual('2af08fb9eec9994ab5862197c4a0d8a45587e440',p01['commit_sha'])
        # CL-DATA-18: bytes = the AI-verified geometry/light-window fill state
        self.assertEqual('87d380a1025bb6ec710bed8f2f95a93871dda477',p01['blob_sha'])

    def test_all_place_names_exact_source_spans_without_new_translation(self):
        count=0
        for p in self.index['places']:
            for lang in x.LANGS:
                source=self.provenance['names'][p['place_id']][lang]
                self.assertEqual('/name_i18n/'+lang,source['pointer'])
                self.assertTrue(p['name_i18n'][lang].strip());count+=1
                if source.get('direct_source'):
                    data=json.loads((ROOT/source['source_path']).read_text(encoding='utf-8'))
                    spot=next(s for s in data['spots'] if s['spot_id']==source['spot_id'])
                    self.assertEqual(p['name_i18n'][lang],spot['name_i18n'][lang])
                    self.assertEqual(source['value'],p['name_i18n'][lang])
                else:
                    doc=self.docs[source['opportunity_id']]
                    self.assertEqual(doc['place_id'],p['place_id'])
                    original=x.pointer(doc,source['pointer'])
                    self.assertEqual(p['name_i18n'][lang],original[source['start']:source['end']])
                    self.assertEqual(source['value'],p['name_i18n'][lang])
            self.assertEqual('PENDING',p['semantic_review'])
        self.assertEqual(696,count)  # 232 places x 3 (re-anchored CL-DATA-32: 14 southern-Japan additions)

    def test_missing_name_locale_and_foreign_place_source_fail(self):
        bad=copy.deepcopy(self.index);bad['places'][0]['name_i18n'].pop('ja')
        self.assertTrue(self.w1.validate_index(bad,self.sources))
        curation=x.read(x.INDEX/'curation.json')
        curation['names']['jp-010']['en']['opportunity_id']='us-071-P01'
        with self.assertRaisesRegex(ValueError,'same canonical Place'):
            x.assemble(self.w1_root,curation=curation)
        curation=x.read(x.INDEX/'curation.json')
        curation['names']['jp-010']['en']['end']=10000
        with self.assertRaisesRegex(ValueError,'range'):
            x.assemble(self.w1_root,curation=curation)

    def test_no_country_from_prefix_and_no_guessed_admin_registry(self):
        self.assertEqual([],self.index['regions'])
        self.assertFalse(self.status['complete_region_picker_eligible'])
        self.assertEqual({'TW':22,'JP':47,'US_STATES_AND_DC':51},self.status['required_region_registry_counts'])
        for p in self.index['places']:
            self.assertEqual([],p['country_codes']);self.assertEqual([],p['region_ids'])
            self.assertEqual('UNKNOWN',p['admin_status'])
            self.assertIn('VERIFIED_COUNTRY_ADMIN_CODES_ABSENT',self.status['per_place_missing_fields'][p['place_id']])

    def test_multivalue_admin_schema_semantics_test_only_not_real_data(self):
        # Synthetic registry exercises representation only, not claimed geography.
        sample=copy.deepcopy(self.index)
        def region(code,level):
            country=code[:2]
            return dict(region_id=('country:' if level=='COUNTRY' else 'admin1:')+code,
                        country_code=country,level=level,code_standard='ISO_3166_1' if level=='COUNTRY' else 'ISO_3166_2',
                        code=code,name_i18n={lang:'SYNTHETIC '+code for lang in x.LANGS})
        sample['regions']=[region('TW','COUNTRY'),region('US','COUNTRY'),region('TW-TNN','ADMIN1'),region('TW-HUA','ADMIN1'),region('US-WA','ADMIN1')]
        p=sample['places'][0]
        p.update(admin_status='COMPLETE',metadata_status='COMPLETE',evidence_refs=['synthetic-ref'],
                 country_codes=['TW','US'],region_ids=[r['region_id'] for r in sample['regions']])
        self.assertEqual([],self.w1.validate_index(sample,self.sources))
        p['region_ids'].append('admin1:NOT-DECLARED')
        self.assertTrue(self.w1.validate_index(sample,self.sources))
        self.assertEqual([],self.index['regions'])  # no synthetic row reaches shipped data

    def test_unknown_timezones_make_all_place_dates_not_evaluable(self):
        q=x.read(x.DATA/'tests/fixtures/task-x/date-query.json')
        for p in self.index['places']:
            self.assertEqual(dict(status='UNKNOWN',iana_id=None,evidence_ref=None),p['time_zone'])
            query=copy.deepcopy(q);query['place_id']=p['place_id']
            self.assertEqual([],self.w1.validate_date_query(query,index=self.index))
            self.assertEqual('NOT_EVALUABLE',query['state'])
            self.assertIsNone(query['local_day']);self.assertIsNone(query['artifact'])
            query['time_zone']=dict(status='VERIFIED',iana_id='Asia/Taipei',evidence_ref='invented-country-default')
            self.assertTrue(self.w1.validate_date_query(query,index=self.index))
        bad=copy.deepcopy(q);bad['state']='READY';bad['device_time_zone']='Asia/Taipei'
        self.assertTrue(self.w1.validate_date_query(bad,index=self.index))

    def test_topic_vocabulary_exact_w1_labels_and_scopes(self):
        vocabulary=x.taxonomy_from_contract(self.w1_root)
        self.assertEqual(set(vocabulary),{t['topic_id'] for t in self.topics['topics']})
        for t in self.topics['topics']:
            self.assertEqual(vocabulary[t['topic_id']]['name_i18n'],t['name_i18n'])
            self.assertEqual(vocabulary[t['topic_id']]['scope_en'],t['definition_i18n']['en'])
            self.assertEqual(set(x.LANGS),set(t['definition_i18n']))
            self.assertTrue(all(v.strip() for v in t['definition_i18n'].values()))
            self.assertEqual('PENDING',self.provenance['topic_definitions'][t['topic_id']]['human_semantic_review'])

    def test_topic_associations_only_existing_existence_evidence(self):
        self.assertEqual([],self.w1.validate_topics(self.topics,self.index))
        classified={b['opportunity_id'] for b in self.topics['opportunity_topics']}
        self.assertTrue(classified <= set(self.docs))
        # Unevidenced opportunities stay honestly unclassified (recorded), never force-fitted.
        self.assertEqual(sorted(set(self.docs)-classified),self.status['unclassified_opportunity_ids'])
        self.assertEqual(23,sum(len(b['topic_ids']) for b in self.topics['opportunity_topics']))
        self.assertEqual(len(self.docs)-len(classified),len(self.status['unclassified_opportunity_ids']))
        by_id={b['opportunity_id']:set(b['topic_ids']) for b in self.topics['opportunity_topics']}
        self.assertEqual({'topic:mountain-landscape','topic:flowers'},by_id['jp-010-P01'])
        self.assertEqual({'topic:sunrise','topic:coastal-landscape'},by_id['tw-036-P01'])
        self.assertEqual({'topic:sunset'},by_id['tw-026-P01'])
        self.assertEqual({'topic:colorful-clouds'},by_id['tw-026-P02'])
        for b in self.topics['opportunity_topics']:
            existence=next(c for c in self.docs[b['opportunity_id']]['evidence_claims'] if c['claim_type']=='existence')
            self.assertTrue(set(b['evidence_refs'])<=set(existence['evidence_refs']))
            entry=self.provenance['opportunities'][b['opportunity_id']]
            for ptr,value in entry['classification_excerpts'].items():
                self.assertEqual(x.pointer(self.docs[b['opportunity_id']],ptr),value)

    def test_missing_classification_fails_instead_of_silently_dropping(self):
        curation=x.read(x.INDEX/'curation.json');del curation['classifications']['tw-026-P02']
        with self.assertRaisesRegex(ValueError,'exactly cover'):
            x.assemble(self.w1_root,curation=curation)
        topics=copy.deepcopy(self.topics);topics['opportunity_topics'][0]['topic_ids']=[]
        self.assertTrue(self.w1.validate_topics(topics,self.index))

    def test_duplicate_ids_dangling_topics_and_wrong_canonical_revision(self):
        bad=copy.deepcopy(self.index);bad['places'].append(bad['places'][0])
        self.assertTrue(self.w1.validate_index(bad,self.sources))
        bad=copy.deepcopy(self.index);bad['opportunities'][0]['revision']=999
        self.assertTrue(self.w1.validate_index(bad,self.sources))
        topics=copy.deepcopy(self.topics);topics['opportunity_topics'][0]['topic_ids']=['topic:unsupported']
        self.assertTrue(self.w1.validate_topics(topics,self.index))
        topics=copy.deepcopy(self.topics);topics['opportunity_topics'][0]['opportunity_id']='missing-opportunity'
        self.assertTrue(self.w1.validate_topics(topics,self.index))

    def test_research_only_cannot_forge_publication_or_coordinates(self):
        for b in self.index['opportunities']:
            self.assertEqual('RESEARCH_ONLY',b['publication']);self.assertIsNone(b['publication_approval_ref'])
        bad=copy.deepcopy(self.index);bad['opportunities'][0].update(publication='GUIDE_ELIGIBLE',publication_approval_ref='made-up-human-approval')
        self.assertTrue(self.w1.validate_index(bad,self.sources))
        bad=copy.deepcopy(self.index);bad['places'][0]['lat']=0
        self.assertTrue(self.w1.validate_index(bad,self.sources))
        self.assertFalse(self.status['forecast_available'])
        self.assertFalse(self.status['selected_date_recommendation_eligible'])
        self.assertEqual([],self.status['evaluations'])

    def test_all_original_descriptions_access_and_safety_preserved_by_reference(self):
        for oid,doc in self.docs.items():
            entry=self.provenance['opportunities'][oid]
            for ref in [entry['description_ref'],*entry['access_advisory_refs'],*entry['safety_refs']]:
                path,ptr=ref.split('#')
                value=x.pointer(x.read(ROOT/path),ptr)
                self.assertEqual(set(x.LANGS),set(value))
                self.assertTrue(all(v.strip() for v in value.values()))
            self.assertFalse(any(c['domain']=='ACCESS_SAFETY' for c in doc['condition_contract']['conditions']))
            self.assertNotEqual('verified',doc['navigation_targets'][0]['status'])
        salt=self.docs['tw-026-P01']['camera_contexts'][0]['access_notes_i18n']
        self.assertIn('2026-11-30',salt['zh-TW']);self.assertIn('2026-11-30',salt['en'])

    def test_deterministic_regeneration_and_manifest_checksums(self):
        assets=x.assemble(self.w1_root)
        self.assertEqual(assets,x.assemble(self.w1_root))
        for name,value in assets.items():self.assertEqual((x.INDEX/name).read_bytes(),x.encoded(value))
        for name,digest in assets['manifest.json']['files'].items():
            self.assertEqual(digest,x.sha256((x.INDEX/name).read_bytes()))
        tampered=copy.deepcopy(self.index);tampered['places'][0]['name_i18n']['en']='invented'
        self.assertNotEqual(assets['manifest.json']['files']['place-index.json'],x.sha256(x.encoded(tampered)))

    def test_source_whitespace_tamper_is_not_trusted_json_equivalence(self):
        pin=self.lock['canonical_records'][0]
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/pin['path'];dest.parent.mkdir(parents=True)
            dest.write_bytes((ROOT/pin['path']).read_bytes()+b'\n')
            with patch.object(x,'ROOT',Path(tmp)):
                with self.assertRaisesRegex(ValueError,'source bytes differ'):x.verify_sources(self.lock)

    def test_old_main_contract_dependency_cannot_silently_replace_w1_pin(self):
        # Independent of whether a later integration checkout already has W1.
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'W1 dependency missing or bytes differ'):
                x.load_w1(Path(tmp),self.lock)
        bad=copy.deepcopy(self.lock);bad['w1']['commit_sha']='0'*40
        with self.assertRaisesRegex(ValueError,'Unreviewed W1'):x.load_w1(self.w1_root,bad)

    def test_query_preferences_capabilities_are_test_only_and_no_favorable(self):
        manifest=x.read(x.INDEX/'manifest.json')
        self.assertEqual({'place-index.json','topic-index.json','field-provenance.json','index-status.json'},set(manifest['files']))
        q=x.read(x.DATA/'tests/fixtures/task-x/date-query.json')
        self.assertFalse(q['recommendation_eligible'])
        caps=x.read(x.DATA/'tests/fixtures/task-x/sort-capabilities.json')
        self.assertFalse(caps['SCORE']['enabled']);self.assertFalse(caps['DISTANCE']['enabled'])
        browse=x.read(x.DATA/'tests/fixtures/task-x/browse-query.json')
        browse['sort']='SCORE'
        self.assertTrue(self.w1.validate_browse(browse,self.index,self.topics,caps))
        browse.update(sort='REGION',region_ids=['country:TW'])
        self.assertTrue(self.w1.validate_browse(browse,self.index,self.topics,caps))


if __name__=='__main__':unittest.main()
