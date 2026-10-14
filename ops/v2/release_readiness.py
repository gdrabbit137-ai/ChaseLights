#!/usr/bin/env python3
"""Fail-closed, offline evidence checklist. Advisory; cannot grant release permission."""
import argparse
import json
from pathlib import Path
import re

# Every item is necessary for a live V2 release. Preview build/CI is insufficient.
CHECKS = {
    'A.owner_integration': ('W5', 'local'),
    'A.pending_dependencies': ('W5', 'github_inventory'),
    'A.merge_rehearsal': ('W5', 'local'),
    'B.canonical_provenance': ('W2/W5', 'local'),
    'B.research_isolation': ('W2/W5', 'local'),
    'B.camera_subject_free_composition': ('W1/W2', 'review'),
    'B.navigation_separation': ('W2/W4', 'local'),
    'B.evidence_uncertainty_review': ('W2', 'review'),
    'B.trilingual_semantic_review': ('W2/W4', 'review'),
    'C.latest_w2_binding': ('W3/W5', 'local'),
    'C.real_weather_provider': ('W1/W3', 'provider'),
    'C.astronomy_source': ('W1/W3', 'local'),
    'C.approved_auto_thresholds': ('W1/W2/W3', 'review'),
    'C.unknown_no_false_score': ('W3', 'local'),
    'C.closure_warning_only': ('W3/W4', 'local'),
    'D.static_build': ('W4/W5', 'local'),
    'D.real_catalog_load': ('W4', 'browser'),
    'D.locale_device_browser': ('W4/W5', 'browser'),
    'D.empty_error_loading': ('W4', 'browser'),
    'D.live_ui_contract': ('W4', 'review'),
    'D.public_url_assets': ('W5', 'public'),
    'E.actual_commit_ci': ('W5', 'github'),
    'E.no_failed_or_skipped_tests': ('W5', 'github'),
    'E.fail_closed_missing_input': ('W5', 'local'),
    'E.hosting_protection': ('Owner/W5', 'review'),
    'E.approval_stage_defined': ('Owner/W5', 'review'),
    'E.health_rollback_plan': ('W5', 'review'),
}


def assess(snapshot, candidate_sha):
    if not re.fullmatch('[0-9a-f]{40}', candidate_sha):
        raise ValueError('Full candidate SHA required')
    if snapshot.get('candidate_sha') != candidate_sha:
        raise ValueError('Evidence belongs to a different candidate SHA')
    if not re.fullmatch('[0-9a-f]{40}', snapshot.get('reviewed_main_sha', '')):
        raise ValueError('Full reviewed main SHA required')
    rows = snapshot.get('checks', [])
    if not isinstance(rows, list):
        raise ValueError('checks must be an explicit list')
    supplied = {}
    for row in rows:
        if not isinstance(row, dict) or row.get('id') not in CHECKS or row['id'] in supplied:
            raise ValueError('Unknown or duplicate check')
        supplied[row['id']] = row
    results = []
    for identifier, (owner, domain) in CHECKS.items():
        row = supplied.get(identifier, {})
        state = row.get('status', 'UNVERIFIED')
        if state not in ('PASS', 'BLOCKED', 'FAIL', 'UNVERIFIED'):
            raise ValueError('SKIP/PENDING/unknown status is not an acceptance result: ' + identifier)
        reason = row.get('reason', 'Required evidence was not supplied')
        if state == 'PASS':
            if (row.get('candidate_sha') != candidate_sha or row.get('domain') != domain
                    or not isinstance(row.get('evidence'), list) or not row['evidence']
                    or not all(isinstance(x, str) and x.strip() for x in row['evidence'])):
                state, reason = 'UNVERIFIED', 'Missing exact-candidate evidence or wrong evidence domain'
            if domain == 'github' and state == 'PASS':
                ci = row.get('github', {})
                tested = ci.get('tested_checkout_sha', '')
                parents = ci.get('tested_parents', [])
                if (ci.get('head_sha') != candidate_sha or ci.get('conclusion') != 'success'
                        or not re.fullmatch('[0-9a-f]{40}', tested)
                        or not re.fullmatch(r'https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/[0-9]+', ci.get('url', ''))
                        or (tested != candidate_sha and candidate_sha not in parents)):
                    state, reason = 'UNVERIFIED', 'GitHub run/head/tested checkout linkage is missing'
                if identifier == 'E.no_failed_or_skipped_tests':
                    counts = ci.get('counts', {})
                    if (type(counts.get('tests')) is not int or counts.get('tests', 0) <= 0
                            or counts.get('pass') != counts.get('tests')
                            or any(counts.get(k) != 0 for k in ('fail', 'error', 'skip'))):
                        state, reason = 'FAIL', 'Actual test counts are absent, failed or skipped'
        results.append({'id': identifier, 'owner': owner, 'domain': domain,
                        'status': state, 'reason': reason, 'evidence': row.get('evidence', [])})
    states = [r['status'] for r in results]
    status = ('NOT READY' if any(s in ('BLOCKED', 'FAIL') for s in states) else
              'UNVERIFIED' if 'UNVERIFIED' in states else 'READY FOR APPROVAL')
    return {'schema_version': 1, 'candidate_sha': candidate_sha,
            'reviewed_main_sha': snapshot['reviewed_main_sha'], 'status': status,
            'checks': results, 'approval': 'NOT_GRANTED', 'deployment_allowed': False,
            'evidence_authenticity': 'EXTERNAL_REVIEW_REQUIRED',
            'scope': 'LIVE_V2_RELEASE',
            'limitations': 'Caller evidence is advisory, not authenticated GitHub or human approval.'}


def markdown(report):
    lines = ['# V2 Release Readiness Checklist', '',
             'Status: **' + report['status'] + '**. Deployment allowed: **false**.', '',
             'Candidate: `' + report['candidate_sha'] + '`; reviewed main: `' + report['reviewed_main_sha'] + '`.', '',
             'Evidence is advisory and requires independent review; this tool never authorizes deployment.', '',
             '| Check | Owner | Evidence domain | Status | Reason |', '|---|---|---|---|---|']
    for row in report['checks']:
        reason = str(row['reason']).replace('|', '\\|').replace('\n', ' ')
        lines.append(f"| {row['id']} | {row['owner']} | {row['domain']} | {row['status']} | {reason} |")
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--candidate-sha', required=True)
    parser.add_argument('--json-output', type=Path, required=True)
    parser.add_argument('--markdown-output', type=Path, required=True)
    args = parser.parse_args()
    try:
        report = assess(json.loads(args.snapshot.read_text()), args.candidate_sha)
        args.json_output.write_text(json.dumps(report, indent=2) + '\n')
        args.markdown_output.write_text(markdown(report))
        print(json.dumps({k: report[k] for k in ('status', 'candidate_sha', 'deployment_allowed')}))
        return int(report['status'] != 'READY FOR APPROVAL')
    except Exception as exc:
        print(json.dumps({'status': 'UNVERIFIED', 'error': str(exc), 'deployment_allowed': False}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
