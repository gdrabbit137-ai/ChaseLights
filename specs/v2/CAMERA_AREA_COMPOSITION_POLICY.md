# V2 photography composition and optional viewpoint policy

Status: W1 integration proposal, pending PR review and merge. Owner W1. This is the worker acceptance and optional viewpoint companion to `FREE_COMPOSITION_SPEC.md`, which owns the detailed composition dependency and R4.2 cloud-sea exception. Both documents preserve the same unknown, access and navigation gates.

## Default user experience and data contract
Photographers **normally choose their own compositions** at a place. An Opportunity describes a place-specific photographic subject and when its relevant weather, astronomical, seasonal, and environmental conditions may be suitable. A fixed tripod location, verified camera GPS, single azimuth/distance, or specific camera-to-subject alignment is **not required** to research, store, or evaluate ordinary Opportunities. CameraContext may represent an area, route, point, or mobile platform under the existing V2.1 schema. Do not classify every ordinary Opportunity as requiring a fixed viewpoint.

A recommended viewpoint is **optional supplementary guidance**, not a prerequisite for the Opportunity's existence, research completion, readiness or ordinary condition evaluation. W2 may find or calculate candidate viewpoints when evidence and geometry allow, but must distinguish observed/verified locations from inferred candidates and preserve provenance, assumptions, precision and access uncertainty. An inferred viewpoint is never presented as verified, uniquely optimal, or a navigation target. Do not invent point coordinates or area polygons. Lack of a recommended viewpoint must not block R1 research-only delivery or valid area-wide evaluation.

## Condition evaluation and the narrow geometry exception
Evaluate each ordinary photographic condition against its actual prerequisites: place-specific subject evidence; valid weather/astronomy/season/time provider coverage and representativeness; scientifically justified thresholds; relevant access/safety; and honest uncertainty. No valid provider, calibration, threshold or required access evidence means UNKNOWN/NOT_EVALUABLE, never favorable. A regionally suitable sunset/cloud window is not proof of a particular composition or reflective pool.

**Only when a condition explicitly claims a precise composition** (e.g. sun between specific buildings, sun aligned with a named peak, reflection from a defined camera position) is that condition dependent on verified geometry. If geometry is missing, keep *that specific composition claim* UNKNOWN/NOT_EVALUABLE or omit it from general recommendations; do not block other independently evaluable ordinary conditions at the same Place. No geometry-dependent promise may be inferred from weather alone.

## Camera, subject, and navigation
Keep CameraContext, PhotographyTarget, ObservationRelation, NavigationTarget independent. Camera area/route is a potential place to compose, not an assertion that all land is publicly accessible. Never equate a scenic-area center or target coordinate with a camera position or arrival point. Only separately verified lawful arrival points may yield Directions; missing recommended viewpoints do not prevent a verified general arrival point from being offered. Respect current closures, access rules, and safety restrictions.

## Research and UI acceptance
- W1: document this default in the canonical V2 spec and tests; reuse current schema's area/route support, avoid introducing a required viewpoint enum or new breaking fields.
- W2: research place, photographic subjects, conditions, evidence and provenance first. Optional viewpoint discovery/calculation is a **nonblocking enrichment step** with clear confidence/provenance. No repetitive searching for a unique camera point. Keep research-only vs live status distinct and zh-TW/en/ja semantics equivalent.
- W3: evaluate valid regional weather/astronomy/season conditions without requiring camera-point geometry; keep precise alignment claims separately fail-closed and never promote unknown to favorable.
- W4: default wording lets users select their own compositions; optionally show supported recommended viewpoints with evidence/confidence labels, access caveats and separate verified arrival Directions. Do not render speculative points as factual pins.
- W5: include tests that (a) ordinary Opportunity without viewpoint can pass its otherwise-valid condition evaluation, (b) exact alignment without geometry fails closed, (c) unverified candidate viewpoints never produce Directions, (d) research-only cannot be shown as live favorable, and (e) three-language semantic parity and Legacy isolation hold.

## Example: Jingzaijiao salt fields
General salt-field sunset photography is an ordinary Opportunity. Evaluate applicable sunset time, cloud, visibility, wind and reflection-relevant environment independently when data and thresholds are valid. Photographers choose their framing within actually permitted areas. A suggested photo spot is optional extra information; exact solar alignment or reflection geometry is a separate optional composition-specific claim. Closures and verified arrival navigation remain independently gated.

## Source precedence
Apply alongside latest main AGENTS.md, RESEARCH_EVIDENCE_SPEC_R4_2.md, NAVIGATION_SPEC_R4_2.md and specs/v2/README.md. No Legacy changes, invented evidence, unsafe navigation, or automatic Legacy/V2 comparisons. This proposal becomes binding only when merged into main under normal review/CI gates. Structural EvaluationResult validation alone cannot authenticate a provider or approve a canonical AUTO threshold/model binding; W5 must retain the semantic fail-closed gate.
