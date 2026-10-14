# W2 Task X research index

This is a **Research-only** projection of the existing W2 Canonical Database: **7 Places / 8 Opportunities / 8 topic IDs / 10 Opportunity-topic links**. It does not add Places, re-research evidence, reconstruct the Database, publish a Catalog or create a date-specific photography result.

## Read paths and contracts for W4

Start at `data/v2/indexes/research/manifest.json`, then resolve its relative files inside this directory:

| File | Purpose / W1 contract |
| --- | --- |
| `place-index.json` | Place identity/name/membership and eight exact Canonical bindings; W1 `place-index-v0.1.schema.json`. |
| `topic-index.json` | Eight W1 stable topic IDs and ten evidenced links; W1 `topic-index-v0.1.schema.json`. Join through Opportunity ID to Place; do not infer tags from names. |
| `field-provenance.json` | Name code-point ranges into exact canonical text, per-topic definition origins, classification source excerpts/claims, and pointers to original descriptions/access/safety/navigation. W2 audit sidecar, not an altered W1 transport schema. |
| `index-status.json` | Research-only safety flags, actual counts, per-Place gaps and incomplete-region-picker state. W2 readiness sidecar; W4 must not silently equate schema validity with complete metadata. |
| `source-lock.json` | Exact reviewed main, W1 dependency and every Canonical/supporting commit/path/blob/SHA256. Runtime manifest pins its SHA256. |
| `curation.json` | Explicit source-span selections and audited topic assignments. No runtime name-based classifier, geocoder or timezone guesser. Its SHA256 is in the manifest. |

W1 dependency is Draft #489 **`38b234ba5f4df4a751eaea14dcc79036b45ed180`**, not assumed merged. Six v0.1 shapes are consumed unchanged. `place-index` and `topic-index` are real research artifacts; the other four formats are exercised only by clearly separated `data/v2/tests/fixtures/task-x/` documents, never exported as runtime forecasts/preferences/capabilities.

Use the accepted W2 commit/tree as the trusted distribution source, verify the manifest and declared file SHA256, validate the pinned W1 schemas and revision equality, then join by exact stable IDs. The `source_commit_sha`/`source_path`/`source_blob_sha`/`revision` of each Opportunity must resolve to matching canonical bytes; do not read a mutable latest file and relabel it with the pinned revision. Source commits are **`2177bd8c8b6c18e0a4b284e50b55d0ff12697ddd`** (three Batch03 records) and **`509a7c206413a4f8d13350ddb50c2a7ad075ca4a`** (five Batch04 records). Their bytes equal reviewed main. P01 original source provenance remains distinct; its current accepted blob is `001a3380231e3d073e900bf2b415aac7dcc5fd79`.

This PR changes no Canonical file or current public W4 Catalog. W4/W5 must deliberately package and read these paths after accepting the dependencies; no claim is made that they are already served by the website.

## Data limits and missing fields

- All **21 Place-name values** are exact Unicode code-point slices of existing canonical `name_i18n`; no new proper-name translation. W1 COMPLETE here means all three sourced name fields are present, not human approval. `semantic_review=PENDING` throughout. The short Chongde label uses PARTIAL because official full Place extent/identity naming needs review. Aliases are empty rather than invented.
- There is **no verified ISO country/admin membership registry in these W2 sources**. `regions=[]`; all seven Places have `country_codes=[]`, `region_ids=[]`, `admin_status=UNKNOWN`. We do not map ID prefixes, source domains, a publisher's jurisdiction or common geographic knowledge into a verified membership. `complete_region_picker_eligible=false`. W1's TW22/JP47/US51 picker requirement is **not satisfied** and has not been relaxed; a sourced registry/membership handoff remains required. No fake Place is created for an unrepresented region.
- All seven `time_zone` envelopes are UNKNOWN with null IANA ID/evidence. Existing sources contain no verified Place-scope timezone assignment. No country/device/coordinate fallback. Time-dependent date queries remain NOT_EVALUABLE; no forecast or score is invented.
- Topic names copy W1's eight three-language labels. English definitions copy the exact W1 scope; zh-TW/ja definitions are conservative translations of that same scope, marked **human semantic review PENDING**. They are operational vocabulary, not additional Place facts or new research. Assignment uses existing canonical target/descriptions + existence evidence, never generic weather/terrain. ACTIVE means available in this research vocabulary, not human publication approval.
- All eight bindings are RESEARCH_ONLY with null approval reference. No GUIDE_ELIGIBLE, verified Directions, numeric score, threshold or live recommendation. Human evidence/semantic/geometry/permission decisions remain pending. No complete metadata or provider capability is implied by the index counts.
- Canonical descriptions, source caveats, closures and safety notices remain verbatim in their original documents. Follow `field-provenance` pointers and preserve all three languages; this index does not replace them with summaries. Access warnings stay non-scoring and navigation stays separately guarded.

A missing/changed pinned file, unknown join, partial translation or stale revision is a validation error, not an empty success. Currently every Opportunity has a sourced classification (`unclassified_opportunity_ids=[]`); if future data has none, it must be explicitly reviewed/recorded as unclassified under the W1 policy instead of guessing or silently extending this fixed-source task. Missing names remain null under W1 when a future reviewed input cannot supply a source; this task's reviewed seven all have source-backed labels. Unreviewed new input is rejected by the source lock.

## Reproduce without network

Provide a byte-identical checkout of the pinned W1 `specs/v2/` directory (external worktree, or deliberately integrated source), rather than copying W1 code into this W2 PR:

```sh
export CHASELIGHTS_W1_SPEC_ROOT=/path/to/pinned-w1/specs/v2
python data/v2/tools/research_index.py validate --git-provenance
python -m unittest discover -s data/v2/tests -p 'test_*.py' -v
```

`build` replaces only the five generated index artifacts and must reproduce identical bytes from `source-lock.json` + `curation.json` + pinned Canonical/W1. Validation is the default action. `--git-provenance` independently checks declared commit:path bytes and needs those Git objects present; it performs no fetch or credential handling. Missing W1/source dependencies fail with a clear error; no SKIP or old-main fallback.

[Owner handoffs and human checklist](../../reviews/TASK_X_HANDOFF.md) · [Actual test results/raw logs](../../tests/logs/task-x/RESULTS.md).
