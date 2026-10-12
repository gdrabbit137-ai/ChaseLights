# ChaseLights V2 — Non-scoring Access Advisory Policy

Status: V2 correction proposal (W1). Supersedes any V2 access-as-photo-blocker language. It does not edit Legacy rules.

## Separate concerns
Photography suitability evaluates researched environmental, astronomical, seasonal and subject-relevant conditions. Site/viewpoint/route/trail/road closures, opening hours, restricted access, construction, unsafe entry locations and unknown legal camera-area boundaries **are not photographic-condition inputs**. They SHALL NOT be REQUIRED, BLOCKER or QUALITY items in `ConditionContract`, nor drive its score, status, threshold, freshness or critical UNKNOWN/NOT_EVALUABLE propagation. Access closure may coexist with FAVORABLE meteorological conditions. Genuine weather hazards (e.g. lightning) and photographic impossibility from clouds or illumination remain independently valid environmental conditions.

Access state belongs to independently sourced and, when possible, time-stamped `AccessAdvisory` presentation, with the existing `CameraContext.access_notes_i18n`/`safety_notes_i18n`, evidence claims and reviewed provenance as the V2.1 nonbreaking transport. An advisory never asserts that another area is open; unknown lawful boundaries remain explicit. All user-visible content is semantically equivalent in zh-TW/en/ja.

## UI and navigation
Render a clearly labeled warning separate from suitability, without changing a favorable environmental result into an unfavorable result. Do not conceal closures merely because environmental conditions are favorable. Unknown or closed arrival routes, unverified navigation coordinates or unlawful areas MUST NOT generate verified Directions or encourage entry. This navigation safety gate is **independent of photographic suitability**.

## Migration and runtime compatibility
- W2: remove `ACCESS_SAFETY` conditions from the canonical `condition_contract.conditions` arrays, retaining sourced access notes and review/crosswalk evidence. Do not relabel a closure as a WEATHER blocker or fake a QUALITY factor.
- W3: ignore/segregate legacy `ACCESS_SAFETY` records for photographic evaluation, emit advisory traces separately and make them unable to block or promote; no access-only contract may produce a favorable result. Still require real weather/time/provider checks for live results.
- W4: show access-only items as warning text in a separate section, never under Required/Blocker/Quality photo-condition headings, including imports of older records. Unverified Directions remain disabled.
- W5: test weather favorable with closure warning, same weather score/status with open vs closed access, P01/P02/016 migration, three-locale parity, and main-based provenance.

No weather provider, numeric threshold or factual legal status can be fabricated to satisfy this policy. Keep existing evidence and human-signoff gates.
