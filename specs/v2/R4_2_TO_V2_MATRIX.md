# ChaseLights R4.2 to V2 migration matrix

Status: Draft; Worker 1 owns this contract. The legacy specifications remain authoritative for the legacy website. V2 changes do not modify those files.

| R4.2 source | Preserved requirement | V2 representation | Verification |
| --- | --- | --- | --- |
| Research Evidence §§1–4 | Place-specific evidence proves the photography subject, not a weather forecast | Evidence claims, audit status, target and opportunity lifecycle | Claim provenance review |
| Research Evidence §4.1 | Narrow cloud-sea environmental exception; no inferred composition | Atmospheric target plus separately reviewed camera and relation | Unknown geometry remains unknown |
| Research Evidence §7 | Domain recommendation owns final conclusion, not UI score interpretation | Condition Contract and Evaluation Result | Unknown required inputs never pass |
| Research Evidence §12 | Approved canonical source ownership and controlled release | V2 canonical revision and approval status | Schema, crosswalk and evidence audit |
| Research Evidence §14 | Photo association is not camera/subject/navigation verification | Observation intake is separate from canonical geometry | EXIF/GPS unknown stays unknown |
| Navigation Spec | Camera Zone and Navigation Target are separate | Camera Context and Navigation Target | Verified arrival point requires evidence |
| Navigation Spec | Search text must not become navigation directions | map_query is metadata only | No keyword fallback |
| Localization policy | Full semantic parity across supported languages | zh-TW, en and ja fields | Automated presence checks plus semantic review |

## Migration gates

1. Inventory actual legacy records from current main rather than assuming historical counts.
2. Import only reviewed evidence; never infer exact coordinates, geometry or thresholds.
3. Require human-machine claim crosswalk and three-locale parity.
4. Validate schema and negative fixtures before production publication.
5. Keep V2 deployment independent; add Legacy-to-V2 link only after verified V2 URL.
6. Do not build automatic Legacy/V2 feature or forecast comparisons. The owner will sample manually.
