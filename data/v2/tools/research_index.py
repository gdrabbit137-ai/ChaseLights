"""Build/validate Task X from locked existing W2 Canonical, without network I/O.

The W1 #489 checkout is an explicit, byte-verified dependency, never copied into
W1 paths or assumed merged. CLI defaults to validation; build writes indexes only.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / 'data/v2'
INDEX = DATA / 'indexes/research'
LANGS = ('zh-TW', 'en', 'ja')
KINDS = ('place-index', 'date-query', 'topic-index', 'local-preferences',
         'browse-query', 'sort-capabilities')
W1_COMMIT = '38b234ba5f4df4a751eaea14dcc79036b45ed180'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()


def pointer(doc, path):
    value = doc
    for raw in path.lstrip('/').split('/'):
        key = raw.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def load_w1(w1_root, lock):
    root = Path(w1_root).resolve()
    if lock['w1']['commit_sha'] != W1_COMMIT:
        raise ValueError('Unreviewed W1 contract pin')
    for rel, pin in lock['w1']['files'].items():
        path = root / rel
        if not path.is_file() or sha256(path.read_bytes()) != pin['sha256'] or blob(path.read_bytes()) != pin['blob_sha']:
            raise ValueError(f'W1 dependency missing or bytes differ: {rel}; supply pinned #489 via --w1-root')
    # Verify module dependencies explicitly before importing the W1 reference gate.
    sys.path.insert(0, str(root / 'tests'))
    for name in ('validate_contract', 'validate_task_w_contracts'):
        spec = importlib.util.spec_from_file_location(name, root / 'tests' / f'{name}.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules['validate_task_w_contracts']


def verify_sources(lock, git_provenance=False):
    sources = {}
    for pin in lock['canonical_records'] + lock['supporting_sources']:
        path = ROOT / pin['path']
        raw = path.read_bytes()
        if sha256(raw) != pin['sha256'] or blob(raw) != pin['blob_sha']:
            raise ValueError('Pinned W2 source bytes differ: ' + pin['path'])
        if git_provenance:
            actual = subprocess.check_output(['git', 'show', f"{pin['commit_sha']}:{pin['path']}"], cwd=ROOT)
            if actual != raw:
                raise ValueError('Canonical/support commit:path mismatch: ' + pin['path'])
        sources[(pin['commit_sha'], pin['path'])] = raw
    actual = {p.stem for p in (DATA / 'opportunities').glob('*.json')}
    expected = {p['opportunity_id'] for p in lock['canonical_records']}
    if actual != expected or len(expected) != len(lock['canonical_records']):
        raise ValueError('Canonical ID coverage changed; explicit W2 source re-review required')
    return sources


def taxonomy_from_contract(w1_root):
    topics = {}
    text = (Path(w1_root) / 'TOPICS_FAVORITES_SORT_CONTRACT_V0_1.md').read_text()
    for line in text.splitlines():
        if not line.startswith('| `topic:'):
            continue
        _, key, labels, scope, _ = line.split('|')
        topic_id = key.strip().strip('`')
        names = labels.strip().split(' / ')
        if len(names) != 3:
            raise ValueError('W1 vocabulary table structure changed')
        topics[topic_id] = dict(name_i18n=dict(zip(LANGS, names)), scope_en=scope.strip())
    if len(topics) != 8:
        raise ValueError('W1 reviewed initial vocabulary changed')
    return topics


def assemble(w1_root, lock=None, curation=None):
    lock = lock if lock is not None else read(INDEX / 'source-lock.json')
    curation = curation if curation is not None else read(INDEX / 'curation.json')
    sources = verify_sources(lock)
    pins = {p['opportunity_id']: p for p in lock['canonical_records']}
    docs = {oid: read(ROOT / pin['path']) for oid, pin in pins.items()}
    place_ids = sorted({d['place_id'] for d in docs.values()})
    if set(curation['names']) != set(place_ids) or set(curation['classifications']) != set(docs):
        raise ValueError('Curation must exactly cover Canonical Places/Opportunities')
    provenance = dict(format_version='0.1.0',name_method=curation['name_method'],
                      human_review='PENDING',names={},opportunities={},topic_definitions={})
    supporting = {(p['commit_sha'], p['path']): p for p in lock['supporting_sources']}
    places = []
    for pid in place_ids:
        names = {}
        name_sources = {}
        for lang in LANGS:
            selection = curation['names'][pid][lang]
            if selection.get('direct_source'):
                # Direct byte-verified V1 source (weather JSON), per the no-review
                # admission gate: verbatim legacy-derived value, never a new translation.
                path = selection['source_path']
                match = [(c, p) for (c, p) in supporting if p == path]
                if len(match) != 1:
                    raise ValueError('Direct name source not uniquely pinned: ' + path)
                commit, _ = match[0]
                pin = supporting[(commit, path)]
                raw_doc = json.loads(sources[(commit, path)])
                doc = {s['spot_id']: s for s in raw_doc.get('spots', [])} \
                    if isinstance(raw_doc.get('spots'), list) else raw_doc
                if doc.get(selection['spot_id'], {}).get('name_i18n', {}).get(lang) is None:
                    raise ValueError(f'Direct V1 name missing: {pid}/{lang}')
                full = doc[selection['spot_id']]['name_i18n'][lang]
                if not isinstance(full, str) or not full:
                    raise ValueError('Direct V1 name is not a non-empty string')
                names[lang] = full
                name_sources[lang] = {**selection, 'value': names[lang],
                                     'source_commit_sha': commit,
                                     'source_blob_sha': pin['blob_sha']}
                continue
            oid = selection['opportunity_id']
            if docs[oid]['place_id'] != pid or selection['pointer'] != '/name_i18n/' + lang:
                raise ValueError('Name source is not the same canonical Place/locale')
            full = pointer(docs[oid], selection['pointer'])
            start, end = selection['start'], selection['end']
            if not isinstance(start, int) or not isinstance(end, int) or not (0 <= start < end <= len(full)):
                raise ValueError('Invalid name code-point range')
            names[lang] = full[start:end]
            name_sources[lang] = {**selection, 'value': names[lang],
                                 'source_commit_sha': pins[oid]['commit_sha'],
                                 'source_blob_sha': pins[oid]['blob_sha']}
        related = [d for d in docs.values() if d['place_id'] == pid]
        refs = sorted({r for d in related for c in d['evidence_claims']
                       if c['claim_type'] == 'existence' for r in c['evidence_refs']})
        places.append(dict(place_id=pid,name_i18n=names,
                           aliases_i18n={lang: [] for lang in LANGS},
                           metadata_status='PARTIAL' if pid == 'tw-034' or not refs else 'COMPLETE',
                           semantic_review='PENDING',country_codes=[],region_ids=[],
                           admin_status='UNKNOWN',evidence_refs=refs,
                           time_zone=dict(status='UNKNOWN',iana_id=None,evidence_ref=None)))
        provenance['names'][pid] = name_sources
    bindings = []
    topic_bindings = []
    for oid, pin in sorted(pins.items()):
        d = docs[oid]
        assignment = curation['classifications'][oid]
        claim = next(c for c in d['evidence_claims'] if c['claim_id'] == assignment['evidence_claim_id'])
        if claim['claim_type'] != 'existence' or not set(assignment['evidence_refs']) <= set(claim['evidence_refs']):
            raise ValueError('Topic assignment needs this Opportunity existence evidence')
        bindings.append(dict(opportunity_id=oid,place_id=d['place_id'],revision=d['revision'],
                             source_commit_sha=pin['commit_sha'],source_path=pin['path'],
                             source_blob_sha=pin['blob_sha'],publication='RESEARCH_ONLY',
                             publication_reason_codes=['CANONICAL_R1_EVIDENCE_REVIEW','HUMAN_RELEASE_APPROVAL_PENDING'],
                             publication_approval_ref=None))
        if assignment['topic_ids'] and assignment['evidence_refs']:
            # W1 topic-index schema requires non-empty topic_ids AND evidence_refs
            # resolving to pinned audit records. Opportunities without pinned
            # evidence stay unclassified (recorded below), never force-fitted.
            topic_bindings.append(dict(opportunity_id=oid,topic_ids=assignment['topic_ids'],
                                       evidence_refs=assignment['evidence_refs']))
        provenance['opportunities'][oid] = dict(
            classification_method='CURATED_CANONICAL_TARGET_AND_EXISTENCE_EVIDENCE',
            classification=assignment,
            classification_excerpts={ptr: pointer(d,ptr) for ptr in assignment['canonical_pointers']},
            description_ref=pin['path']+'#/description_i18n',
            access_advisory_refs=[pin['path']+f'#/camera_contexts/{i}/access_notes_i18n' for i in range(len(d['camera_contexts']))],
            safety_refs=[pin['path']+f'#/camera_contexts/{i}/safety_notes_i18n' for i in range(len(d['camera_contexts']))],
            navigation_ref=pin['path']+'#/navigation_targets')
    index = dict(schema_version='0.1.0',regions=[],places=places,opportunities=bindings)
    revision = 'sha256:' + sha256(encoded(index))
    index['index_revision'] = revision
    vocabulary = taxonomy_from_contract(w1_root)
    if set(curation['topic_definitions']) != set(vocabulary):
        raise ValueError('Topic definitions differ from reviewed W1 vocabulary')
    topics = []
    for tid, source in sorted(vocabulary.items()):
        definitions = dict(curation['topic_definitions'][tid],en=source['scope_en'])
        topics.append(dict(topic_id=tid,name_i18n=source['name_i18n'],definition_i18n=definitions,
                           status='ACTIVE',replaced_by=None))
        provenance['topic_definitions'][tid] = dict(
            source_commit_sha=lock['w1']['commit_sha'],
            source_path='specs/v2/TOPICS_FAVORITES_SORT_CONTRACT_V0_1.md',
            source_scope_en=source['scope_en'],
            name_method='EXACT_W1_THREE_LANGUAGE_LABELS',
            definition_method='W1_SCOPE_EN_WITH_SOURCE_DERIVED_ZH_TW_JA_TRANSLATION',
            human_semantic_review='PENDING',not_new_place_evidence=True)
    topic_index = dict(schema_version='0.1.0',index_revision=revision,
                       taxonomy_revision='sha256:'+sha256(encoded(topics)),
                       topics=topics,opportunity_topics=topic_bindings)
    gaps = {pid: ['VERIFIED_COUNTRY_ADMIN_CODES_ABSENT','PLACE_TIMEZONE_EVIDENCE_ABSENT',
                  'HUMAN_NAME_SEMANTIC_REVIEW_PENDING'] +
                  (['CHONGDE_PLACE_EXTENT_NAME_SCOPE_REVIEW'] if pid == 'tw-034' else []) for pid in place_ids}
    status = dict(format_version='0.1.0',mode='RESEARCH_ONLY',index_revision=revision,
                  taxonomy_revision=topic_index['taxonomy_revision'],
                  selected_date_recommendation_eligible=False,forecast_available=False,
                  evaluations=[],complete_region_picker_eligible=False,
                  region_registry_status='UNKNOWN_EXISTING_W2_SOURCES_INSUFFICIENT',
                  required_region_registry_counts={'TW':22,'JP':47,'US_STATES_AND_DC':51},
                  human_release_approval='PENDING',taxonomy_semantic_review='PENDING',
                  counts=dict(places=len(places),opportunities=len(bindings),topic_ids=len(topics),
                              opportunity_topic_links=sum(len(b['topic_ids']) for b in topic_bindings),
                              regions=0,verified_timezones=0,guide_eligible=0),
                  per_place_missing_fields=gaps,
                  unclassified_opportunity_ids=sorted(set(docs)-{b['opportunity_id'] for b in topic_bindings}))
    assets={'place-index.json':index,'topic-index.json':topic_index,
            'field-provenance.json':provenance,'index-status.json':status}
    manifest=dict(format_version='0.1.0',mode='RESEARCH_ONLY',index_revision=revision,
                  taxonomy_revision=topic_index['taxonomy_revision'],w1_contract_commit_sha=W1_COMMIT,
                  canonical_source_lock='source-lock.json',source_lock_sha256=sha256(encoded(lock)),
                  curation_sha256=sha256(encoded(curation)),
                  files={name:sha256(encoded(value)) for name,value in assets.items()})
    assets['manifest.json']=manifest
    return assets


def validate(w1_root, git_provenance=False):
    lock=read(INDEX/'source-lock.json')
    w1=load_w1(w1_root,lock)
    sources=verify_sources(lock,git_provenance)
    expected=assemble(w1_root,lock)
    errors=[]
    for name,value in expected.items():
        if (INDEX/name).read_bytes()!=encoded(value):
            errors.append('Generated projection/manifest drift: '+name)
    index=read(INDEX/'place-index.json');topics=read(INDEX/'topic-index.json')
    errors.extend(w1.validate_index(index,sources))
    errors.extend(w1.validate_topics(topics,index))
    for kind in ('date-query','local-preferences','browse-query','sort-capabilities'):
        doc=read(DATA/f'tests/fixtures/task-x/{kind}.json')
        errors.extend(w1.structural(kind,doc))
        if kind=='date-query':errors.extend(w1.validate_date_query(doc,index=index))
        if kind=='local-preferences':errors.extend(w1.validate_preferences(doc))
        if kind=='browse-query':errors.extend(w1.validate_browse(doc,index,topics))
        if kind=='sort-capabilities':errors.extend(w1.validate_capabilities(doc))
    # Existence claims must resolve to actual pinned W2 audit records, not URL-like strings.
    evidence={}
    for pin in lock['supporting_sources']:
        if '/audits/' in pin['path']:
            audit=read(ROOT/pin['path'])
            for row in audit.get('evidence',[])+audit.get('source_records',[]):
                if row['id'] in evidence:errors.append('Duplicate evidence ID')
                evidence[row['id']]=row
    for row in index['places']+topics['opportunity_topics']:
        for ref in row['evidence_refs']:
            if ref not in evidence or not evidence[ref].get('url','').startswith('https://'):
                errors.append('Unresolved pinned evidence: '+ref)
    for b in index['opportunities']:
        if b['publication']!='RESEARCH_ONLY' or b['publication_approval_ref'] is not None:
            errors.append('Research-only publication escalation')
    return sorted(set(errors))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['build','validate'],nargs='?',default='validate')
    parser.add_argument('--w1-root',type=Path,default=os.environ.get('CHASELIGHTS_W1_SPEC_ROOT'))
    parser.add_argument('--git-provenance',action='store_true')
    args=parser.parse_args()
    try:
        if args.w1_root is None:
            raise ValueError('Set CHASELIGHTS_W1_SPEC_ROOT or --w1-root to pinned #489 specs/v2 (not assumed merged)')
        lock=read(INDEX/'source-lock.json');load_w1(args.w1_root,lock)
        if args.action=='build':
            for name,value in assemble(args.w1_root,lock).items():
                (INDEX/name).write_bytes(encoded(value))
        errors=validate(args.w1_root,args.git_provenance)
        if errors:
            for e in errors:print('FAIL '+e)
            return 1
        print('PASS six W1 schemas; canonical/index/source/reference consistency')
        print('PASS exact source commit:path provenance' if args.git_provenance else 'PASS pinned source bytes (Git history gate not requested)')
        print(json.dumps(read(INDEX/'index-status.json')['counts'],sort_keys=True))
        return 0
    except (OSError,ValueError,KeyError,TypeError,subprocess.CalledProcessError) as exc:
        print('ERROR '+str(exc),file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
