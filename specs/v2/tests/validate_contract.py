import json
from pathlib import Path
from jsonschema import Draft202012Validator
p = Path(__file__).resolve().parents[1]
schema = json.loads((p/'schema/opportunity-v2.1.schema.json').read_text())
fixture = json.loads((p/'tests/fixtures/valid_aurora_draft.json').read_text())
Draft202012Validator.check_schema(schema)
Draft202012Validator(schema).validate(fixture)
print('PASS V2 canonical schema fixture')
