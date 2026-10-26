#!/usr/bin/env python3
"""Genre template registry validator + expansion tool.

Registry: data/v2/templates/<template_id>.json (+ metric-vocabulary.json).

Subcommands:
  validate                       validate every template in the registry
  expand --template cloud_sea --opportunity-id tw-001-P02 \
         --skeleton data/v2/migration/skeletons/tw-001-P02.json \
         --params params.json [--out data/v2/staging/contracts/tw-001-P02.json]
                                 materialize a template onto a spot skeleton
                                 (staging only; canonical dirs are coverage-locked)
  binding-lint                    lint model_binding strings in data/v2/opportunities

Binding grammar (model_binding string; the template registry stores the
structured object and expansion serializes it):
    dataset:<id>|field:<name>[+<name>...]|role:<ROLE>[|level:<fixed|dynamic:param>][|sector:<id>]
Rules: pipe-separated key:value segments, each key at most once, `dataset`
and `field` required, `role` must be one of the five tiering roles
(SHORT_HQ/MID/LONG/AEROSOL/OBS). `+` inside `field` lists the fields a
derived metric consumes. Unknown keys or duplicate segments fail closed.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TEMPLATES = REPO / 'data/v2/templates'
VOCAB = TEMPLATES / 'metric-vocabulary.json'

ROLES = {'SHORT_HQ', 'MID', 'LONG', 'AEROSOL', 'OBS'}
BIND_KEYS = {'dataset', 'field', 'level', 'role', 'sector'}
OPERATORS = {'gte', 'lte', 'gt', 'lt', 'between', 'none'}


def _load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_vocabulary():
    return _load_json(VOCAB)


def _fail(msg: str):
    raise SystemExit(f'ERROR {msg}')


def lint_binding_string(value: str) -> dict:
    """Parse a model_binding string into a dict; fail closed on any violation."""
    if not isinstance(value, str) or not value.strip():
        _fail('binding must be a non-empty string')
    seen = {}
    for segment in value.split('|'):
        if ':' not in segment:
            _fail(f'binding segment missing colon: {segment!r}')
        key, val = segment.split(':', 1)
        key = key.strip()
        if key not in BIND_KEYS:
            _fail(f'unknown binding key {key!r} in {value!r}')
        if key in seen:
            _fail(f'duplicate binding key {key!r} in {value!r}')
        if not val.strip():
            _fail(f'empty value for binding key {key!r} in {value!r}')
        seen[key] = val.strip()
    for required in ('dataset', 'field'):
        if required not in seen:
            _fail(f'binding missing required key {required!r}: {value!r}')
    if 'role' in seen and seen['role'] not in ROLES:
        _fail(f"binding role {seen['role']!r} not in {sorted(ROLES)}")
    if 'level' in seen and seen['level'].startswith('dynamic:'):
        if len(seen['level']) <= len('dynamic:'):
            _fail(f'empty dynamic level in {value!r}')
    return seen


def lint_binding_object(obj) -> dict:
    if obj is None:
        return None
    if not isinstance(obj, dict):
        _fail(f'binding must be an object or null, got {type(obj).__name__}')
    unknown = set(obj) - BIND_KEYS - {'note'}
    if unknown:
        _fail(f'unknown binding keys {sorted(unknown)}')
    for required in ('dataset', 'field', 'role'):
        if required not in obj or not str(obj[required]).strip():
            _fail(f'binding missing required key {required!r}')
    if obj['role'] not in ROLES:
        _fail(f"binding role {obj['role']!r} not in {sorted(ROLES)}")
    return obj


def serialize_binding(obj) -> str:
    parts = [f"dataset:{obj['dataset']}", f"field:{obj['field']}", f"role:{obj['role']}"]
    if obj.get('level'):
        parts.append(f"level:{obj['level']}")
    if obj.get('sector'):
        parts.append(f"sector:{obj['sector']}")
    return '|'.join(parts)


def _eval_expr(expr: str, params: dict):
    """Safe arithmetic evaluator: numbers, declared params, + - * / ( )."""
    ALLOWED_BIN = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
                   ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b}

    def _ev(node):
        if isinstance(node, ast.Expression):
            return _ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            if node.id not in params:
                _fail(f'expression references undeclared param {node.id!r}')
            return params[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_BIN:
            return ALLOWED_BIN[type(node.op)](_ev(node.left), _ev(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -_ev(node.operand)
        _fail(f'disallowed syntax in threshold expression: {ast.dump(node)[:80]}')

    try:
        tree = ast.parse(expr, mode='eval')
    except SyntaxError as exc:
        _fail(f'bad threshold expression {expr!r}: {exc}')
    value = _ev(tree)
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return value


def validate_template(path: Path, vocab: dict):
    t = _load_json(path)
    tid = t.get('template_id')
    if tid != path.stem:
        _fail(f'{path.name}: template_id {tid!r} != filename stem')
    if t.get('status') not in {'defined', 'scaffold', 'draft'}:
        _fail(f'{tid}: status must be defined|scaffold|draft, got {t.get("status")!r}')
    refs = [c.get('template_ref') for c in t.get('conditions', [])]
    if len(refs) != len(set(refs)):
        _fail(f'{tid}: duplicate template_ref values')
    declared = {p['name'] for p in t.get('params', [])}
    for c in t.get('conditions', []):
        metric = c.get('metric')
        if metric not in vocab['metrics']:
            _fail(f'{tid}/{c.get("template_ref")}: metric {metric!r} not in metric-vocabulary.json')
        if c.get('operator') not in OPERATORS:
            _fail(f'{tid}/{c.get("template_ref")}: operator {c.get("operator")!r} not allowed')
        thr = c.get('threshold')
        if c['operator'] == 'none' and thr is not None:
            _fail(f'{tid}/{c["template_ref"]}: operator none requires threshold null')
        if c['operator'] == 'between':
            if not (isinstance(thr, list) and len(thr) == 2):
                _fail(f'{tid}/{c["template_ref"]}: between requires a 2-element threshold')
        if isinstance(thr, dict):
            if 'expr' not in thr:
                _fail(f'{tid}/{c["template_ref"]}: object threshold must carry expr')
            if c.get('threshold_source') != 'computed':
                _fail(f'{tid}/{c["template_ref"]}: expr thresholds require threshold_source computed')
            for p in c.get('threshold_params', []):
                if p not in declared:
                    _fail(f'{tid}/{c["template_ref"]}: threshold param {p!r} not declared in params')
        if c['status_expected'] if False else False:
            pass
        lint_binding_object(c.get('binding'))
        if t['status'] == 'defined':
            for lang in ('zh-TW', 'en', 'ja'):
                if not (c.get('rationale_i18n') or {}).get(lang, '').strip():
                    _fail(f'{tid}/{c["template_ref"]}: rationale_i18n missing {lang!r}')
            if c.get('binding') is None and vocab['metrics'][metric].get('kind') not in (None, 'computed', 'observation'):
                _fail(f'{tid}/{c["template_ref"]}: metric {metric!r} needs a binding')
        if c.get('activate_when'):
            aw = c['activate_when']
            if aw.get('template_ref') not in refs:
                _fail(f'{tid}/{c["template_ref"]}: activate_when references unknown template_ref')
            if aw.get('mode') not in {'when_not_met', 'when_met'}:
                _fail(f'{tid}/{c["template_ref"]}: activate_when mode must be when_not_met|when_met')
        scope = c.get('genre_scope')
        if scope is not None and not re.fullmatch(r'[a-z][a-z_]*', scope):
            _fail(f'{tid}/{c["template_ref"]}: genre_scope must be a lowercase identifier')
        fetch = c.get('fetch')
        if fetch is not None:
            if not isinstance(fetch, dict) or fetch.get('strategy') not in {'nearest_gridpoint', 'height_bound'}:
                _fail(f'{tid}/{c["template_ref"]}: fetch.strategy must be nearest_gridpoint|height_bound')
            unknown = set(fetch) - {'strategy', 'gridpoint_selector', 'candidate_levels_hpa', 'target_height_expression'}
            if unknown:
                _fail(f'{tid}/{c["template_ref"]}: unknown fetch keys {sorted(unknown)}')
    return t


def validate_registry() -> list:
    vocab = load_vocabulary()
    out = []
    for path in sorted(TEMPLATES.glob('*.json')):
        if path.name == 'metric-vocabulary.json':
            continue
        out.append(validate_template(path, vocab))
    return out


def _scope_sig(cond):
    """Spatial scope signature: fetch binding dict, else point sampling."""
    b = cond.get('binding')
    if isinstance(b, dict):
        return json.dumps(b, sort_keys=True)
    return 'point'


def _merge_conditions(existing, additions, template_id, template_version):
    """Fail-closed merge: refuse metric overlaps that are not cleanly scoped."""
    out = list(existing)
    by_metric = {}
    for c in existing:
        by_metric.setdefault(c['metric'], []).append(c)
    skipped = 0
    for c in additions:
        clashes = by_metric.get(c['metric'], [])
        sig = _scope_sig(c)
        conflict = False
        for e in clashes:
            esig = _scope_sig(e)
            if esig == sig:
                same = (e['operator'] == c['operator'] and e['threshold'] == c['threshold'])
                if same:
                    conflict = 'duplicate'
                else:
                    conflict = 'conflict'
                break
            if esig == 'point' or sig == 'point':
                conflict = 'conflict'   # point vs sector sampling of the same metric
                break
        if conflict == 'duplicate':
            skipped += 1
            continue
        if conflict:
            _fail(f"merge conflict on metric {c['metric']!r} ({conflict}): identical sampling scope "
                  f"with different operator/threshold between existing contract and template "
                  f"{template_id!r}; resolve in the template or via a spot-level override")
        c = dict(c)
        c['genre_template'] = template_id          # schema-tolerant provenance keys
        c['template_version'] = template_version
        out.append(c)
    return out, skipped


def expand(template_id: str, opportunity_id: str, skeleton_path: Path,
           params_path: Path | None, out_path: Path | None, claim_ref: str | None = None,
           print_only: bool = False, merge: bool = False):
    vocab = load_vocabulary()
    tpath = TEMPLATES / f'{template_id}.json'
    if not tpath.exists():
        _fail(f'template {template_id!r} not found in registry')
    t = validate_template(tpath, vocab)
    if t['status'] != 'defined':
        _fail(f"template {template_id!r} is {t['status']}; owner must approve it (status=defined) before expansion")
    params = _load_json(params_path) if params_path else {}
    declared = {p['name'] for p in t['params']}
    unknown = set(params) - declared
    if unknown:
        _fail(f'undeclared params supplied: {sorted(unknown)}')
    skeleton = _load_json(skeleton_path)
    if skeleton.get('opportunity_id') != opportunity_id:
        _fail(f"skeleton opportunity_id {skeleton.get('opportunity_id')!r} != {opportunity_id!r}")
    conditions = []
    ref_to_id = {}
    for i, c in enumerate(t['conditions'], 1):
        ref_to_id[c['template_ref']] = f'C-{opportunity_id}-{i:02d}'
    for i, c in enumerate(t['conditions'], 1):
        thr = c['threshold']
        if isinstance(thr, dict):
            thr = _eval_expr(thr['expr'], params)
        cond = {
            'id': f'C-{opportunity_id}-{i:02d}',
            'role': c['role'], 'domain': c['domain'],
            'evaluation_mode': c['evaluation_mode'], 'capability': c['capability'],
            'metric': c['metric'], 'operator': c['operator'], 'threshold': thr,
            'unit': c['unit'], 'unknown_policy': c['unknown_policy'],
            'claim_refs': [claim_ref or f'{opportunity_id}-claim-01'],
            'model_binding': serialize_binding(c['binding']) if c.get('binding') else None,
            'validation_status': 'provisional',
            'condition_tier': c['condition_tier'],
            'threshold_source': c['threshold_source'],
            'calibration_status': c['calibration_status'],
            'rationale_i18n': c['rationale_i18n'],
        }
        if c.get('fetch'):
            cond['binding'] = c['fetch']
        if c.get('genre_scope'):
            cond['genre_scope'] = c['genre_scope']
        if c.get('activate_when'):
            cond['modifier_activation'] = {
                'when_condition': ref_to_id[c['activate_when']['template_ref']],
                'mode': c['activate_when']['mode'],
            }
        conditions.append(cond)
    contract_version = f"{template_id}-v{t['version']}"
    if merge:
        existing_cc = skeleton.get('condition_contract')
        if not existing_cc or not existing_cc.get('conditions'):
            _fail('--merge requires a skeleton that already carries a condition_contract')
        # ids continue after the existing numbering
        n = len(existing_cc['conditions'])
        renum = {}
        for i, c in enumerate(conditions, n + 1):
            renum[c['id']] = f'C-{opportunity_id}-{i:02d}'
            c['id'] = f'C-{opportunity_id}-{i:02d}'
        for c in conditions:
            ma = c.get('modifier_activation')
            if ma:
                ma['when_condition'] = renum.get(ma['when_condition'], ma['when_condition'])
        merged, skipped = _merge_conditions(existing_cc['conditions'], conditions,
                                            template_id, contract_version)
        existing_cc['conditions'] = merged
        out = skeleton
        note = f'merged {template_id}-v{t["version"]} -> {len(conditions)} offered, {skipped} duplicate skipped, {len(merged)} total'
    else:
        skeleton['condition_contract'] = {
            'contract_id': f'CC-{opportunity_id}-v1',
            'status': 'draft',
            'genre_template': template_id,
            'template_version': contract_version,
            'recommendation_policy_version': None,
            'conditions': conditions,
        }
        out = skeleton
        note = f'expanded {template_id}-v{t["version"]} -> {len(conditions)} conditions'
    if print_only:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return out
    if out_path is None:
        out_path = REPO / f'data/v2/staging/contracts/{opportunity_id}.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{note} -> {out_path}')
    return out


def binding_lint():
    bad = 0
    for path in sorted((REPO / 'data/v2/opportunities').glob('*.json')):
        doc = _load_json(path)
        for c in (doc.get('condition_contract') or {}).get('conditions', []):
            mb = c.get('model_binding')
            if mb is None:
                continue
            try:
                lint_binding_string(mb)
            except SystemExit as exc:
                bad += 1
                print(f'{path.name}/{c["id"]}: {exc}')
    print(f'binding-lint: {bad} violations across data/v2/opportunities')
    return bad


def main(argv=None):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('validate')
    ex = sub.add_parser('expand')
    ex.add_argument('--template', required=True)
    ex.add_argument('--opportunity-id', required=True)
    ex.add_argument('--skeleton', required=True)
    ex.add_argument('--params')
    ex.add_argument('--out')
    ex.add_argument('--claim-ref', help='claim id every condition cites (default <opportunity-id>-claim-01)')
    ex.add_argument('--merge', action='store_true',
                    help='append conditions to an existing contract (fail-closed conflict check)')
    ex.add_argument('--print', action='store_true')
    sub.add_parser('binding-lint')
    args = ap.parse_args(argv)
    if args.cmd == 'validate':
        templates = validate_registry()
        defined = [t['template_id'] for t in templates if t['status'] == 'defined']
        draft = [t['template_id'] for t in templates if t['status'] == 'draft']
        scaffold = [t['template_id'] for t in templates if t['status'] == 'scaffold']
        print(f"PASS registry: {len(defined)} defined ({', '.join(defined)}), "
              f"{len(draft)} draft ({', '.join(draft)}), {len(scaffold)} scaffold ({', '.join(scaffold)})")
    elif args.cmd == 'expand':
        expand(args.template, args.opportunity_id, Path(args.skeleton),
               Path(args.params) if args.params else None,
               Path(args.out) if args.out else None, args.claim_ref, args.print,
               merge=bool(args.merge))
    else:
        sys.exit(1 if binding_lint() else 0)


if __name__ == '__main__':
    main()
