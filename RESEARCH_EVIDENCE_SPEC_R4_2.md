# ChaseLights Research Evidence Specification R4.2

## 1. Core rule

Photography Opportunity existence is a **research claim about a Place**.

An Opportunity MAY be added to the production catalog only when there is Place-specific evidence that the subject, scene, event, or composition actually exists at that Place and is photographically meaningful.

Weather, terrain, elevation, hydrology, vegetation type, Scene tags, Theme tags, or generic destination categories may help discover a research lead or predict **when an already verified Opportunity may work**. They MUST NOT, by themselves, create or prove an Opportunity.

In short:

`Place-specific evidence proves WHAT can be photographed.`

`Forecast/runtime data estimates WHEN that verified subject may work.`

The two layers MUST NOT be reversed.

## 2. Evidence scope

Evidence must match the scope of the claim.

Examples:

- A lake being humid does not prove it has a worthwhile morning-mist photography Opportunity.
- A mountain being high does not prove a sea-of-clouds Opportunity.
- A west-facing coast does not prove a famous or usable sunset composition.
- Calm wind does not prove a reflection composition exists; the foreground/background geometry must be researched.
- Dark sky does not prove a Milky Way composition; access, horizon, orientation and subject geometry must be researched.
- Seasonal climate does not prove flowers, foliage, fireflies, birds or other subjects are present.
- Rainfall does not prove a waterfall is photographically usable from a legal Camera Zone.
- Broken cloud does not prove crepuscular rays are a repeatable Place-specific subject.

## 3. Evidence grades

### Grade A — authoritative Place-specific evidence
Examples:
- official scenic-area / park / forestry / municipality / tourism material,
- official trail, facility, event or habitat documentation,
- official image/caption explicitly showing or describing the subject at the Place,
- primary operator information for a recurring event or managed seasonal subject.

Grade A can establish Opportunity existence when the evidence actually supports the photographic claim.

### Grade B — reliable Place-specific observational evidence
Examples:
- established photography publication,
- reputable hiking/outdoor publication with identifiable Place-specific imagery or description,
- multiple independent dated photographs / field reports that consistently demonstrate the subject.

Grade B may establish Opportunity existence when the claim is concrete and independently reviewable. Prefer corroboration for rare or highly variable phenomena.

### Grade C — discovery-only evidence
Examples:
- generic travel blogs,
- social posts,
- unsourced photo captions,
- search snippets,
- map reviews,
- AI-generated summaries.

Grade C may create a research lead but MUST NOT alone promote an Opportunity to production.

## 4. High-risk subject rule

The following subjects require explicit Place-specific evidence and MUST NOT be inferred from terrain/weather alone:

- fog / mist / morning mist / haze as a photographic subject,
- sea of clouds,
- crepuscular rays / sunbeams / cloud-gap light,
- reflection compositions,
- Milky Way / star-field compositions,
- seasonal flowers and foliage,
- waterfalls where flow/visibility/access is part of the photographic claim,
- wildlife / birds / fireflies or other biological presence,
- recurring festivals, illuminations and events,
- snow/ice-specific compositions.

A high-risk Opportunity should record enough provenance to answer:
1. What evidence proves this subject exists here?
2. What geographic scope does that evidence support?
3. What part of the claim is forecastable?
4. What remains unforecastable or uncertain?

## 5. Camera Zone and evidence

Evidence for the subject does not automatically verify a Camera Zone.

A Camera Zone must be supported by location-specific evidence or explicitly marked representative/provisional.

Do not convert:
- an attraction center coordinate,
- a weather sampling coordinate,
- a map search result,
- a road point,
into an exact tripod point without separate evidence.

Navigation Target remains governed by `NAVIGATION_SPEC_R4_2.md` and is separate from Camera Zone evidence.

## 6. Runtime contract

Runtime modules evaluate an already-researched Opportunity.

They MAY:
- test visibility,
- wind,
- cloud layers,
- cloud base,
- precipitation,
- time window,
- sun/moon geometry,
- access state,
- tide/marine state,
- verified seasonal/event dates.

They MUST NOT:
- create a new subject because weather looks favorable,
- claim subject presence when presence is not forecastable,
- upgrade a generic Scene/Theme tag into a researched Opportunity,
- present terrain suitability as proof that a photographic phenomenon occurs there.

When subject presence is not forecastable, the model must expose that uncertainty and cap/qualify the recommendation as defined by the Opportunity contract.

## 7. Visible-copy rule

User-facing reasons must distinguish:
- observed/provider weather facts,
- runtime inference,
- researched Place facts,
- unknown subject presence.

Do not say a scene is present merely because its meteorological prerequisites are present.

Example:
- Allowed: "Low visibility and high humidity match the researched morning-mist window."
- Not allowed: "Morning mist is present" unless an observation source confirms it.

## 8. Admission checklist

Before adding a new Opportunity:

- [ ] Place-specific evidence found.
- [ ] Evidence grade recorded.
- [ ] Claim scope matches evidence scope.
- [ ] Camera Zone evidence reviewed separately.
- [ ] Forecastable vs non-forecastable parts identified.
- [ ] Required conditions / boosters / penalties are not being used as proof of subject existence.
- [ ] High-risk subject has explicit provenance.
- [ ] UI copy does not overstate uncertain presence.
- [ ] Tests cover the evidence/runtime boundary.

## 9. Audit policy

Existing production Opportunities are grandfathered for operation, not automatically certified under this specification.

The evidence audit classifies them into:
- `documented`: explicit Place-specific evidence metadata/reference is present,
- `review_required`: a high-risk subject exists but explicit evidence provenance is not machine-verifiable in the current runtime catalog,
- `lower_risk_legacy`: no high-risk semantic trigger; still subject to normal research requirements.

`review_required` is a research queue, not an assertion that the Opportunity is false.

## 10. Origin

This specification formalizes the existing B29 principles:
- every active Place requires Place-specific photography research,
- curated Opportunity data must not be synthesized from legacy Scene/Theme labels,
- visible scene claims such as forest mist / reflection require Place research plus corresponding model/data support.

B35 made the same boundary explicit for Liyu Lake morning mist. R4.2 now applies it project-wide.
## 11. Production admission gate

As of B41, the initial high-risk backlog has been fully classified and the evidence audit is an enforced CI admission gate.

For every pull request to `main` and relevant push to `main`:

- the audit runs with `--enforce`,
- any high-risk Opportunity left as `review_required` fails CI,
- `verified`, `narrow_scope`, `insufficient_evidence`, and `remove_or_rewrite` are explicit research outcomes and do not fail merely because they are conservative,
- a new high-risk Opportunity must therefore include Place-specific provenance or an explicit conservative classification before merge.

The gate protects the evidence boundary; it does not require promotion to `verified`.

