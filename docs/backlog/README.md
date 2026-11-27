# Backlog — third wave (deferred, not blocking the current release)

These are the items the 2026-11-26 four-reviewer audit surfaced that we
deliberately did **not** fix in waves 1–2. Each file states the observed
defect, the numbers behind it, the proposed approach and the acceptance
criteria, so a future ticket can be written without re-running the audit.

| Item | Why it is deferred | Owner-visible impact |
|---|---|---|
| [CL-DATA-85 — valley + summit dual-grid cloud sea](cl-data-85-valley-cloud-sea.md) | needs a second grid column per spot (new provider pull + contract work) | 雲海 days mostly read 資料不足 above the summit |
| [Photographer decision inputs](photographer-decision-inputs.md) | new data sources (moon phase, galactic centre bearing, drive time) | 「今晚去哪拍」 still needs outside tools |
| [Cross-region shortlist / compare](cross-region-shortlist.md) | new UI surface, needs design | comparing 3 spots means opening 3 modals and remembering |
| [Hourly plane ↔ bundle sync](hourly-plane-bundle-sync.md) | data-pipeline change (single fetch per run) | hourly detail can be up to 16 h older than the verdict |

## Owner-spec items (added 2026-11-27)

| Item | Why it is not in the current wave | Owner-visible impact |
|---|---|---|
| [CL-UI-115 — experience and visual unification](cl-ui-115-experience-and-visual-unification.md) | changes the card state machine (two triggers, two panels) and needs a new icon library; must wait for CL-UI-46 to merge first because both edit `assets/app.js` | metric icons differ between desktop and phone; card weather row shows the day's representative hour instead of *now*; card body and subject button open the same panel |

## Where the evidence lives

- Audit findings jsonl: `D:/tmp/audit/findings.jsonl` (27 rows, P0/P1/P2, per reviewer)
- Physics scan scripts: `D:/tmp/audit-physics/analyze{1..6}.py`
- Visual screenshots: `D:/tmp/audit-visual/` (45 images)
- Chaos report: `D:/tmp/audit-chaos/report.md`
- Photographer notes: `D:/tmp/audit-photog/notes.md`
