"""Task W contract regressions; all invented data below is TEST ONLY.

The filter oracle is an executable acceptance truth table, not W4 application code.
No external requests, storage implementation or live forecast is exercised.
"""
import copy
import hashlib
import json
import unittest
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from validate_task_w_contracts import (
    KINDS, structural, validate_index, validate_date_query, validate_topics,
    validate_preferences, validate_browse, validate_capabilities)

FIXTURES = Path(__file__).parent / 'fixtures/task-w'


def load(kind):
    return json.loads((FIXTURES / f'{kind}.json').read_text())


def i18n(text):
    return {'zh-TW': '測試 ' + text, 'en': 'Test ' + text, 'ja': 'テスト ' + text}


def regional_index():
    index = load('place-index')
    for country, admin in [('TW', 'TW-TNN'), ('US', 'US-WA'), ('JP', 'JP-19')]:
        index['regions'] += [
            dict(region_id='country:' + country, country_code=country, level='COUNTRY',
                 code_standard='ISO_3166_1', code=country, name_i18n=i18n(country)),
            dict(region_id='admin1:' + admin, country_code=country, level='ADMIN1',
                 code_standard='ISO_3166_2', code=admin, name_i18n=i18n(admin))]
    # Synthetic test memberships, deliberately not a W2 geographic claim.
    for place, (country, admin) in zip(index['places'], [('TW', 'TW-TNN'), ('US', 'US-WA'), ('JP', 'JP-19')]):
        place.update(name_i18n=i18n(place['place_id']), metadata_status='COMPLETE',
                     country_codes=[country], region_ids=['country:' + country, 'admin1:' + admin],
                     admin_status='COMPLETE', evidence_refs=['SYNTHETIC_TEST_SOURCE'])
    return index


def resolved_query(zone_name='Asia/Taipei', day='2026-10-14'):
    q = load('date-query')
    zone = ZoneInfo(zone_name)
    d = datetime.fromisoformat(day)
    start = d.replace(tzinfo=zone)
    end = (d + timedelta(days=1)).replace(tzinfo=zone)
    q.update(time_zone=dict(status='VERIFIED', iana_id=zone_name, evidence_ref='TEST_ONLY_NOT_PLACE_EVIDENCE'),
             selected_date=day, place_local_date=day, state='EMPTY', reason_code='NO_MATCHING_DATA',
             local_day=dict(start_utc=start.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z'),
                            end_utc=end.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z'),
                            start_offset_seconds=int(start.utcoffset().total_seconds()),
                            end_offset_seconds=int(end.utcoffset().total_seconds()),
                            tzdb_version='test:host-zoneinfo-not-release-metadata'))
    return q


def ready_query():
    q = resolved_query()
    q.update(state='READY', reason_code=None,
             artifact=dict(kind='WINDOW', artifact_ref='test-only:window', artifact_sha256='a' * 64,
                           data_revision='test-data-1', opportunity_id='tw-026-P01',
                           opportunity_revision=1, contract_revision=1))
    return q


def normalize(text):
    return ' '.join(unicodedata.normalize('NFKC', text).casefold().split())


def filter_oracle(index, topics, query, favorites=()):
    """Small reference predicate for W4/W5 acceptance; returns eligible IDs."""
    if query['surface'] == 'RECOMMENDATIONS':
        return {}  # This fixture provides no genuine evaluated recommendation.
    memberships = {p['place_id']: p for p in index['places']}
    tags = {b['opportunity_id']: set(b['topic_ids']) for b in topics['opportunity_topics']}
    result = {}
    for binding in index['opportunities']:
        publication = binding['publication']
        if publication == 'WITHHELD' or (query['surface'] == 'GUIDE' and publication != 'GUIDE_ELIGIBLE'):
            continue
        pid, oid = binding['place_id'], binding['opportunity_id']
        p = memberships[pid]
        if query['region_ids'] and not set(query['region_ids']) & set(p['region_ids']):
            continue
        if query['topic_ids'] and not set(query['topic_ids']) & tags.get(oid, set()):
            continue
        if query['favorites_only'] and ('PLACE', pid) not in favorites and ('OPPORTUNITY', oid) not in favorites:
            continue
        names = [v for v in p['name_i18n'].values() if v is not None]
        aliases = [v for values in p['aliases_i18n'].values() for v in values]
        region_labels = [v for r in index['regions'] if r['region_id'] in p['region_ids']
                         for v in [r['region_id'], r['code'], *r['name_i18n'].values()]]
        if not any(normalize(query['search']) in normalize(v) for v in [pid, *names, *aliases, *region_labels]):
            continue
        result.setdefault(pid, []).append(oid)
    return result


class PlaceIndexContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {}
        for b in load('place-index')['opportunities']:
            # Contract fixtures pin historical canonical bytes. Current W2 may
            # legitimately correct a record without rewriting this test claim.
            current = (Path(__file__).resolve().parents[3] / b['source_path']).read_bytes()
            blob = lambda raw: hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
            raw = current if blob(current) == b['source_blob_sha'] else (
                FIXTURES / 'canonical' / (b['opportunity_id'] + '.json')).read_bytes()
            if blob(raw) != b['source_blob_sha']:
                raise AssertionError('Historical contract fixture byte pin mismatch: ' + b['opportunity_id'])
            cls.sources[(b['source_commit_sha'], b['source_path'])] = raw

    def test_all_six_schemas_and_fixture_shapes(self):
        for kind in KINDS:
            with self.subTest(kind=kind):
                self.assertEqual([], structural(kind, load(kind)))

    def test_pinned_canonical_four_records_three_places_two_opportunities(self):
        index = load('place-index')
        self.assertEqual([], validate_index(index, self.sources))
        self.assertEqual(3, len(index['places']))
        self.assertEqual(2, sum(b['place_id'] == 'tw-026' for b in index['opportunities']))

    def test_multi_admin_and_multi_country_is_one_stable_place(self):
        index = regional_index()
        p = index['places'][0]
        p['country_codes'].append('US')
        p['region_ids'] += ['country:US', 'admin1:US-WA']
        index['regions'].append(dict(region_id='admin1:TW-HUA', country_code='TW', level='ADMIN1', code_standard='ISO_3166_2', code='TW-HUA', name_i18n=i18n('Second synthetic region')))
        p['region_ids'].append('admin1:TW-HUA')
        self.assertEqual([], validate_index(index, self.sources))
        self.assertEqual('tw-026', p['place_id'])

    def test_registry_country_admin_complete_and_reference_errors(self):
        for change in ('country', 'standard', 'dangling', 'missing-admin'):
            index = regional_index()
            if change == 'country': index['places'][0]['country_codes'] = ['JP']
            if change == 'standard': index['regions'][1]['code_standard'] = 'ISO_3166_1'
            if change == 'dangling': index['places'][0]['region_ids'].append('admin1:MISSING')
            if change == 'missing-admin': index['places'][0]['region_ids'] = ['country:TW']
            with self.subTest(change=change):
                self.assertTrue(validate_index(index, self.sources))

    def test_duplicate_ids_and_dangling_canonical_join_fail(self):
        for collection in ('regions', 'places', 'opportunities'):
            index = regional_index()
            index[collection].append(copy.deepcopy(index[collection][0]))
            self.assertTrue(validate_index(index, self.sources))
        index = load('place-index')
        index['opportunities'][0]['place_id'] = 'missing'
        self.assertTrue(validate_index(index, self.sources))

    def test_canonical_revision_path_hash_and_missing_bytes_fail(self):
        for key, value in [('revision', 999), ('source_path', 'data/v2/opportunities/wrong.json'), ('source_blob_sha', 'f' * 40)]:
            index = load('place-index')
            index['opportunities'][0][key] = value
            self.assertTrue(validate_index(index, self.sources), key)
        self.assertTrue(validate_index(load('place-index'), {}))

    def test_partial_names_valid_but_complete_or_missing_locale_not(self):
        index = load('place-index')
        p = index['places'][0]
        p.update(metadata_status='PARTIAL', name_i18n={'zh-TW': '測試', 'en': None, 'ja': None})
        self.assertEqual([], validate_index(index, self.sources))
        p['metadata_status'] = 'COMPLETE'
        self.assertTrue(validate_index(index, self.sources))
        p['name_i18n'] = i18n('all')
        self.assertTrue(validate_index(index, self.sources))  # no metadata evidence
        del p['name_i18n']['ja']
        self.assertTrue(validate_index(index, self.sources))

    def test_research_never_promoted_by_schema_or_r1(self):
        index = regional_index()
        index['opportunities'][0]['publication'] = 'GUIDE_ELIGIBLE'
        index['opportunities'][0]['publication_approval_ref'] = 'invented-human-approval'
        self.assertTrue(validate_index(index, self.sources))
        index['opportunities'][0]['publication'] = 'RESEARCH_ONLY'
        self.assertTrue(validate_index(index, self.sources))  # residual approval forbidden


class DateQueryContractTests(unittest.TestCase):
    def test_unknown_zone_has_no_device_fallback_or_artifact(self):
        q = load('date-query')
        self.assertEqual([], validate_date_query(q))
        for field, value in [('state', 'READY'), ('place_local_date', q['selected_date']), ('local_day', resolved_query()['local_day'])]:
            changed = copy.deepcopy(q)
            changed[field] = value
            self.assertTrue(validate_date_query(changed))
        q['device_time_zone'] = 'Asia/Taipei'
        self.assertTrue(validate_date_query(q))

    def test_taipei_tokyo_and_date_line_local_day(self):
        for zone in ('Asia/Taipei', 'Asia/Tokyo', 'Pacific/Kiritimati'):
            with self.subTest(zone=zone):
                q = resolved_query(zone)
                self.assertEqual([], validate_date_query(q))
                self.assertTrue(q['local_day']['start_utc'].startswith('2026-10-13'))

    def test_seattle_and_anchorage_dst_23_and_25_hours(self):
        for zone in ('America/Los_Angeles', 'America/Anchorage'):
            for date, hours in [('2026-03-08', 23), ('2026-11-01', 25)]:
                with self.subTest(zone=zone, date=date):
                    q = resolved_query(zone, date)
                    self.assertEqual([], validate_date_query(q))
                    day = q['local_day']
                    duration = datetime.fromisoformat(day['end_utc']) - datetime.fromisoformat(day['start_utc'])
                    self.assertEqual(hours * 3600, duration.total_seconds())
                    self.assertNotEqual(day['start_offset_seconds'], day['end_offset_seconds'])
                    bad = copy.deepcopy(q)
                    start = datetime.fromisoformat(day['start_utc'])
                    bad['local_day']['end_utc'] = (start + timedelta(hours=24)).isoformat().replace('+00:00', 'Z')
                    self.assertTrue(validate_date_query(bad))

    def test_relative_dates_per_place_and_shuffled_daily_date_keys(self):
        # Frozen UTC: tomorrow is already a different civil day in TW and US.
        now = datetime(2026, 10, 14, 2, tzinfo=timezone.utc)
        expected = {'Asia/Taipei': '2026-10-15', 'America/Los_Angeles': '2026-10-14'}
        for zone_name, wanted in expected.items():
            today = now.astimezone(ZoneInfo(zone_name)).date()
            tomorrow = today + timedelta(days=1)
            self.assertEqual(wanted, tomorrow.isoformat())
            self.assertEqual([], validate_date_query(resolved_query(zone_name, wanted)))
            # Find by date, not position; second item is deliberately yesterday.
            daily = [{'date': wanted}, {'date': (today - timedelta(days=1)).isoformat()},
                     {'date': today.isoformat()}]
            self.assertNotEqual(wanted, daily[1]['date'])
            self.assertEqual(wanted, next(d for d in daily if d['date'] == wanted)['date'])
            self.assertIsNone(next((d for d in daily if d['date'] == '2027-01-01'), None))

    def test_invalid_date_zone_offset_and_boundary_rejected(self):
        for change in ('date', 'zone', 'offset', 'boundary', 'local-date'):
            q = resolved_query()
            if change == 'date': q['selected_date'] = '2026-02-30'
            if change == 'zone': q['time_zone']['iana_id'] = 'Not/A_Zone'
            if change == 'offset': q['local_day']['end_offset_seconds'] = 0
            if change == 'boundary': q['local_day']['start_utc'] = q['local_day']['end_utc']
            if change == 'local-date': q['place_local_date'] = '2026-10-15'
            self.assertTrue(validate_date_query(q), change)

    def test_skipped_apia_date_no_fake_interval(self):
        q = load('date-query')
        q.update(selected_date='2011-12-30', reason_code='NONEXISTENT_LOCAL_DATE',
                 time_zone=dict(status='VERIFIED', iana_id='Pacific/Apia', evidence_ref='TEST_ONLY'))
        self.assertEqual([], validate_date_query(q))
        zone = ZoneInfo('Pacific/Apia')
        start = datetime(2011, 12, 29, tzinfo=timezone.utc)
        self.assertNotIn('2011-12-30', {(start + timedelta(hours=h)).astimezone(zone).date().isoformat() for h in range(96)})
        bad = resolved_query('Pacific/Apia', '2011-12-30')
        self.assertTrue(validate_date_query(bad))

    def test_cross_midnight_and_fold_instant_order(self):
        zone = ZoneInfo('America/Los_Angeles')
        start = datetime(2026, 10, 31, 23, 30, tzinfo=zone)
        end = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=1)
        self.assertEqual('2026-10-31', start.date().isoformat())
        self.assertEqual('2026-11-01', end.date().isoformat())
        self.assertEqual(timedelta(hours=3), end.astimezone(timezone.utc) - start.astimezone(timezone.utc))
        first = end.replace(fold=0)
        self.assertEqual(timedelta(hours=1), end.astimezone(timezone.utc) - first.astimezone(timezone.utc))

    def test_ready_reference_and_generation_date_revision_identity(self):
        q = ready_query()
        self.assertEqual([], validate_date_query(q, copy.deepcopy(q)))
        for field, value in [('query_id', 'late'), ('generation', 2), ('place_id', 'us-071'), ('selected_date', '2026-10-15'), ('index_revision', 'new-index')]:
            expected = copy.deepcopy(q)
            expected[field] = value
            self.assertTrue(validate_date_query(q, expected), field)
        expected = copy.deepcopy(q)
        expected['artifact']['data_revision'] = 'new-data'
        self.assertTrue(validate_date_query(q, expected))

    def test_query_must_use_index_place_timezone_and_canonical_revision(self):
        index = load('place-index')
        q = load('date-query')
        self.assertEqual([], validate_date_query(q, index=index))
        self.assertTrue(validate_date_query(ready_query(), index=index))
        index['places'][0]['time_zone'] = ready_query()['time_zone']
        self.assertEqual([], validate_date_query(ready_query(), index=index))
        q = ready_query()
        q['artifact']['opportunity_revision'] = 2
        self.assertTrue(validate_date_query(q, index=index))
        q = load('date-query')
        q['place_id'] = 'missing'
        self.assertTrue(validate_date_query(q, index=index))

    def test_loading_error_empty_stale_clear_previous_artifact(self):
        for state in ('IDLE', 'LOADING', 'EMPTY', 'ERROR', 'STALE', 'NOT_EVALUABLE'):
            q = ready_query()
            q.update(state=state, reason_code='TEST_REASON', artifact=None)
            self.assertEqual([], validate_date_query(q))
            q['artifact'] = ready_query()['artifact']
            self.assertTrue(validate_date_query(q), state)

    def test_query_never_carries_forecast_or_recommendation(self):
        q = ready_query()
        for field, value in [('recommendation_eligible', True), ('score', 90), ('photography_verdict', 'FAVORABLE'), ('provider_run_id', 'invented')]:
            changed = copy.deepcopy(q)
            changed[field] = value
            self.assertTrue(validate_date_query(changed), field)


class TopicsPreferencesSortTests(unittest.TestCase):
    def test_topics_and_shared_browse_valid(self):
        index = load('place-index')
        topics = load('topic-index')
        self.assertEqual([], validate_topics(topics, index))
        self.assertEqual([], validate_browse(load('browse-query'), index, topics))

    def test_topic_missing_locale_and_dangling_or_duplicate_join_fail(self):
        for change in ('locale', 'duplicate', 'opportunity', 'topic', 'revision'):
            topics = load('topic-index')
            if change == 'locale': del topics['topics'][0]['definition_i18n']['ja']
            if change == 'duplicate': topics['opportunity_topics'].append(topics['opportunity_topics'][0])
            if change == 'opportunity': topics['opportunity_topics'][0]['opportunity_id'] = 'missing'
            if change == 'topic': topics['opportunity_topics'][0]['topic_ids'] = ['topic:missing']
            if change == 'revision': topics['index_revision'] = 'missing'
            self.assertTrue(validate_topics(topics, load('place-index')), change)

    def test_deprecated_topic_replacement_is_explicit_and_acyclic(self):
        topics = load('topic-index')
        topics['topics'][0].update(status='DEPRECATED', replaced_by='topic:contract-b')
        self.assertEqual([], validate_topics(topics, load('place-index')))
        topics['topics'][1].update(status='DEPRECATED', replaced_by='topic:contract-a')
        self.assertTrue(validate_topics(topics, load('place-index')))
        topics['topics'][0]['replaced_by'] = 'topic:missing'
        self.assertTrue(validate_topics(topics, load('place-index')))

    def test_favorites_unknown_retained_and_typed_keys_unique(self):
        prefs = load('local-preferences')
        self.assertEqual([], validate_preferences(prefs))
        entry = copy.deepcopy(prefs['favorites'][0])
        entry['entity_type'] = 'OPPORTUNITY'
        prefs['favorites'].append(entry)
        self.assertEqual([], validate_preferences(prefs))
        entry2 = copy.deepcopy(entry)
        entry2['added_at_utc'] = '2026-10-15T00:00:00Z'
        prefs['favorites'].append(entry2)
        self.assertTrue(validate_preferences(prefs))

    def test_favorites_version_corruption_and_sensitive_extra_fields_rejected(self):
        for key, value in [('schema_version', '9.0.0'), ('storage_revision', -1), ('user_location', [0, 0]), ('favorites', 'broken')]:
            prefs = load('local-preferences')
            prefs[key] = value
            self.assertTrue(validate_preferences(prefs), key)

    def test_sort_unavailable_requires_translated_explanation_and_null_key(self):
        caps = load('sort-capabilities')
        self.assertEqual([], validate_capabilities(caps))
        for change in ('locale', 'key', 'reason'):
            bad = copy.deepcopy(caps)
            if change == 'locale': del bad['DISTANCE']['explanation_i18n']['ja']
            if change == 'key': bad['SCORE']['comparison_key'] = 'fake-score'
            if change == 'reason': bad['SCORE']['reason_code'] = None
            self.assertTrue(validate_capabilities(bad), change)

    def test_score_and_distance_cannot_self_enable(self):
        for field in ('SCORE', 'DISTANCE'):
            caps = load('sort-capabilities')
            caps[field].update(enabled=True, reason_code=None, explanation_i18n=None, comparison_key='invented')
            self.assertTrue(validate_capabilities(caps))
            # Test-only injected trust exercises the interface, not a live source.
            self.assertEqual([], validate_capabilities(caps, {field: 'invented'}))

    def test_unknown_filters_and_unavailable_sort_rejected(self):
        for field, value in [('region_ids', ['missing']), ('topic_ids', ['topic:missing']), ('taxonomy_revision', 'missing'), ('sort', 'SCORE'), ('sort', 'DISTANCE')]:
            q = load('browse-query')
            q[field] = value
            self.assertTrue(validate_browse(q, load('place-index'), load('topic-index'), load('sort-capabilities')), field)

    def test_region_topic_or_with_and_and_place_dedup_truth_table(self):
        index, topics, q = regional_index(), load('topic-index'), load('browse-query')
        q.update(region_ids=['country:TW', 'country:US'], topic_ids=['topic:contract-a', 'topic:contract-b'])
        self.assertEqual({'tw-026': ['tw-026-P01', 'tw-026-P02'], 'us-071': ['us-071-P01']}, filter_oracle(index, topics, q))
        q['topic_ids'] = ['topic:contract-a']
        self.assertEqual({'tw-026': ['tw-026-P01'], 'us-071': ['us-071-P01']}, filter_oracle(index, topics, q))
        q['region_ids'] = ['country:JP']
        self.assertEqual({}, filter_oracle(index, topics, q))

    def test_sourced_admin_search_and_same_name_stable_identity(self):
        index, topics, q = regional_index(), load('topic-index'), load('browse-query')
        index['places'][0]['name_i18n'] = i18n('Same name')
        index['places'][1]['name_i18n'] = i18n('Same name')
        q['search'] = 'Same name'
        self.assertEqual({'tw-026', 'us-071'}, set(filter_oracle(index, topics, q)))
        q['search'] = 'US-WA'
        self.assertEqual({'us-071': ['us-071-P01']}, filter_oracle(index, topics, q))
        q['search'] = 'テスト TW-TNN'
        q['locale'] = 'en'  # All available sourced language labels are searchable.
        self.assertEqual({'tw-026': ['tw-026-P01', 'tw-026-P02']}, filter_oracle(index, topics, q))
        q.update(search='', region_ids=['country:JP'])
        self.assertEqual({'jp-010': ['jp-010-P01']}, filter_oracle(index, topics, q))

    def test_favorites_do_not_promote_research_or_duplicate_place(self):
        index, topics, q = load('place-index'), load('topic-index'), load('browse-query')
        q['favorites_only'] = True
        saved = [('PLACE', 'tw-026'), ('OPPORTUNITY', 'tw-026-P01')]
        self.assertEqual({'tw-026': ['tw-026-P01', 'tw-026-P02']}, filter_oracle(index, topics, q, saved))
        self.assertEqual({'tw-026': ['tw-026-P01']}, filter_oracle(index, topics, q, [('OPPORTUNITY', 'tw-026-P01')]))
        for surface in ('GUIDE', 'RECOMMENDATIONS'):
            q['surface'] = surface
            self.assertEqual({}, filter_oracle(index, topics, q, saved))
        q['surface'] = 'RESEARCH'
        index['opportunities'][0]['publication'] = 'WITHHELD'
        self.assertEqual({'tw-026': ['tw-026-P02']}, filter_oracle(index, topics, q, saved))

    def test_cross_locale_alias_normalization_null_names_and_empty_search(self):
        index, topics, q = load('place-index'), load('topic-index'), load('browse-query')
        index['places'][0]['aliases_i18n']['ja'] = ['Ｔｅｓｔ  alias']
        q['search'] = '  TEST   ALIAS '
        for locale in ('zh-TW', 'en', 'ja'):
            q['locale'] = locale
            self.assertEqual({'tw-026': ['tw-026-P01', 'tw-026-P02']}, filter_oracle(index, topics, q))
        q['search'] = 'jp-010'
        self.assertEqual({'jp-010': ['jp-010-P01']}, filter_oracle(index, topics, q))
        q['search'] = ''
        self.assertEqual(3, len(filter_oracle(index, topics, q)))
        q['search'] = 'absent'
        self.assertEqual({}, filter_oracle(index, topics, q))


if __name__ == '__main__':
    unittest.main()
