"""V2.1 Draft 2020-12 structural and intra-document reference validator.

This gate does not authenticate evidence sources, verify GPS or prove
translation semantic equivalence; those require separate review.
"""
import argparse
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load_schema():
    schema = json.loads((ROOT / "schema/opportunity-v2.1.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def validate_references(document):
    """Return dangling/duplicate reference errors after schema validation."""
    errors = []

    def ids(collection, field="id"):
        values = [item[field] for item in document[collection]]
        if len(values) != len(set(values)):
            errors.append(f"duplicate {collection} {field}")
        return set(values)

    cameras = ids("camera_contexts")
    targets = ids("targets")
    ids("observation_relations")
    ids("navigation_targets")
    claims = ids("evidence_claims", "claim_id")
    conditions = document["condition_contract"]["conditions"]
    condition_ids = [item["id"] for item in conditions]
    if len(condition_ids) != len(set(condition_ids)):
        errors.append("duplicate condition id")

    # Source IDs are declared by evidence claims, but their external validity
    # cannot be established without a separate evidence-source registry.
    declared_sources = {ref for claim in document["evidence_claims"]
                        for ref in claim["evidence_refs"]}
    for collection in ("camera_contexts", "targets", "observation_relations", "navigation_targets"):
        for item in document[collection]:
            for ref in item["evidence_refs"]:
                if ref not in declared_sources:
                    errors.append(f"{collection}/{item['id']}: undeclared evidence ref {ref}")

    for relation in document["observation_relations"]:
        if relation["camera_context_id"] not in cameras:
            errors.append(f"relation/{relation['id']}: missing camera {relation['camera_context_id']}")
        if relation["target_id"] not in targets:
            errors.append(f"relation/{relation['id']}: missing target {relation['target_id']}")

    for target in document["targets"]:
        for component in target.get("components", []):
            if component not in targets:
                errors.append(f"target/{target['id']}: missing component {component}")
            if component == target["id"]:
                errors.append(f"target/{target['id']}: self-reference")

    for condition in conditions:
        for claim in condition["claim_refs"]:
            if claim not in claims:
                errors.append(f"condition/{condition['id']}: missing claim {claim}")

    return sorted(errors)


def validate_record(document, schema=None):
    schema = schema if schema is not None else load_schema()
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [f"schema:{'/'.join(map(str, e.absolute_path)) or '$'}: {e.message}"
              for e in validator.iter_errors(document)]
    if errors:
        return sorted(errors)
    return validate_references(document)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", type=Path)
    args = parser.parse_args(argv)
    files = args.files or sorted((ROOT / "tests/fixtures").glob("valid_*.json"))
    if not files:
        print("FAIL: no valid fixtures found", file=sys.stderr)
        return 2
    schema = load_schema()
    failed = False
    for path in files:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            errors = validate_record(record, schema)
        except (OSError, ValueError) as exc:
            errors = [str(exc)]
        if errors:
            failed = True
            print(f"FAIL {path}: {'; '.join(errors)}")
        else:
            print(f"PASS {path}")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
