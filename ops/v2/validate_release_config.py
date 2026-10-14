#!/usr/bin/env python3
"""Static validation of the non-deploying W5 integration/build plan."""
import argparse
import json
from pathlib import Path
import re
import yaml


def validate(plan, workflow, events_required=None):
    if (plan.get('schema_version') != 1 or
            not re.fullmatch('[0-9a-f]{40}', plan.get('reviewed_main_sha', ''))):
        raise ValueError('Versioned plan and full reviewed SHA required')
    required = {'hosting': 'EXISTING_GITHUB_PAGES', 'domain': 'chaselights.app',
                'v2_source': 'apps/web-v2/', 'base_path': '/apps/web-v2/',
                'v2_url': 'https://chaselights.app/apps/web-v2/',
                'current_product': 'RESEARCH_ONLY_PREVIEW', 'approval': 'NOT_GRANTED',
                'deployment': 'NOT_PERFORMED'}
    if any(plan.get(k) != v for k, v in required.items()):
        raise ValueError('Deployment/source/isolation contract drift')
    for key in ('live_forecast_ready', 'deployment_enabled_by_this_plan', 'automatic_deployment_added'):
        if plan.get(key) is not False:
            raise ValueError('No release or deployment may be enabled: ' + key)
    if plan.get('new_secrets_required_for_static_build') != []:
        raise ValueError('Static build must require no production secret')
    if not isinstance(workflow, dict) or workflow.get('permissions') != {'contents': 'read'}:
        raise ValueError('Integration workflow must use contents:read only')
    events = workflow.get('on', {})
    if set(events) != (events_required or {'pull_request', 'push', 'workflow_dispatch'}):
        raise ValueError('Unexpected workflow trigger')
    if not workflow.get('jobs'):
        raise ValueError('Integration checks missing')
    for job in workflow['jobs'].values():
        if any(k in job for k in ('permissions', 'environment', 'continue-on-error')):
            raise ValueError('Job must not add permissions, approval assumptions or ignored failures')
        for step in job.get('steps', []):
            if any(k in step for k in ('continue-on-error', 'permissions')):
                raise ValueError('Step failure/permission override is forbidden')
            text = str(step.get('run', '')) + ' ' + str(step.get('uses', ''))
            if re.search(r'deploy-pages|upload-pages-artifact|git\s+push|gh\s+pr\s+merge|\|\|\s*true|set\s+\+e', text):
                raise ValueError('Integration workflow contains publish/merge or ignored failure')
    return {'status': 'PASS', 'deployment_allowed': False,
            'scope': 'W5 static configuration only; actual Hosting protections remain unverified'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    args = parser.parse_args()
    try:
        plan = json.loads((args.root / 'ops/v2/deployment_plan.json').read_text())
        # BaseLoader deliberately preserves the YAML key `on` as a string.
        workflow = yaml.load((args.root / '.github/workflows/v2-integration.yml').read_text(), Loader=yaml.BaseLoader)
        validate(plan, workflow)
        release_workflow = yaml.load((args.root / '.github/workflows/v2-release-readiness.yml').read_text(), Loader=yaml.BaseLoader)
        print(json.dumps(validate(plan, release_workflow, {'pull_request'})))
        return 0
    except Exception as exc:
        print(json.dumps({'status': 'FAIL', 'error': str(exc), 'deployment_allowed': False}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
