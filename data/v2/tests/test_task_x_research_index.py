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
        # CL-DATA-62: 6 Places retired (owner 2026-11-10) — their canonical
        # records remain byte-pinned archives in source-lock, but the generated
        # index/provenance projection excludes them (lifecycle_status retired).
        cls.docs={k:v for k,v in cls.docs.items() if k in cls.provenance['opportunities']}

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
        self.assertEqual((344,539),(len(actual),len(ids)))  # re-anchored CL-INT-134 (6-place retirement on the merged 350/552 tree)
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
        # CL-INT-134 merged re-anchor: full provenance commit whitelist of the
        # merged tree (CL-DATA-02..62 + CL-DATA-51..58 main waves + the 13
        # retired records re-pinned to the CL-INT-134 regen base commit).
        '0246bb4496f82b11678ec06550f51b29099c3e41',
        '0ab54271b600c0466dcca8dda2fc4a4a42c54680',
        '1bf8e398e20ebbc76be1157d98bd8dc188216746',
        '1edb5ced42e689cbf29dc523ebe6028d4a72f936',
        '21198c9cc91e00cdd3df8daea76aac46bf9fb45b',
        '23f1bb6c0a90964067d885c3783c99c87a902b86',
        '2af08fb9eec9994ab5862197c4a0d8a45587e440',
        '34cb70f39f8d959e9b68cfa3a6768a74cb29de99',
        '3dcf271879ea1ffde447f88d3870a68a09ef6d68',
        '3eb466432807185bc8b9271d006666b72d1fa406',
        '433d59401adf3727780b2af331426169bd81c40c',
        '4d56532ddf843a345f28560f8ad85a461d51dc4f',
        '4e51267ba7b7130d28efa41e50d2ef3d36de81a8',
        '69b832accfc8c0438a50e51689c4e7c40765e9f4',
        '6a420db5100bb184f655b4b765d29fdf3494588d',
        '7a77bea62a609a861b725288f53036e10b750ac9',
        '8024532fdfd00d32fb5d44335d2feb634d50a2de',
        '8393d5b3d4612c04b57d583a694094f77f78696c',
        '86cc3d9bdfaaac110f65361ac77df744cdd4cfa1',
        'a34cd15819a1b01702d6d38408524e444ca84906',
        'a38356bd36eacbd7f81fa962e251aa21fb48a6fa',
        'a4f803a7106816773ef5a2f659271c656b873bd7',
        'cc9e9d1a667134aeec9a5466f2436e9d82f70192',  # CL-DATA-66: 8 edited contracts re-pinned to the stage-1 data commit
        'affcdf391e49a43a606d7dd7e567aedf58e02f34',
        'b801dd4eba545a76879828b25e869f3c45df33ac',
        'c0c6114b0bfbae0afc28b1b5c0f128d3aa41b982',
        'c507251b3e3fb09d6a5bd16abe04a8beb2aee7ed',
        'c7b41c7c99e6a7cf73f1e90363a1fcfbe51fbed9',
        'c832d9112e8ba813b65c184a2fafb17a7f5b3643',
        'd3e019433a7516773f39c764ab09fe70810dec25',
        'd57d40f8966631783f1385908659bd8c1b82adbd',
        'd587d0d8c31dee9853e53207a00e9cbd7a1940e7',
        'db04b94f3a0a6e78bff000e3c97ffb80fee2daf5',
        'dda29699705dcdf9ced993bca06316e1085a15e9',
        'e261cc9817e720d852bd5aee9b1b555edd253d8c',
        'e6603751b8571025b9db78d405dbdd65c55476ea',
        'ef5b1042a5a86ea99e3bd6a477ed79ce5f62cf4e',
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
        self.assertEqual(1032,count)  # 344 places x 3 (re-anchored CL-INT-134: 6-place retirement on the merged tree)

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
        self.assertEqual(41,sum(len(b['topic_ids']) for b in self.topics['opportunity_topics']))  # CL-INT-134 merged re-anchor: topic links of the merged 539-opportunity index (retired links removed on top of the CL-DATA-53/54 wave links)
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
