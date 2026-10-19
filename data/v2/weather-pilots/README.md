# W2 hourly-weather pilot binding

`tw-036-open-meteo.json` records the single Qixingtan study binding selected with W1 on 2026-10-19. It is a sourced research sidecar, not a new Canonical Place, CameraContext, NavigationTarget or a public browse-index update. Existing camera geometry, research maturity, access warnings and index timezone are retained exactly. See `specs/v2/HOURLY_WEATHER_PILOT_GATE_V0_1.md` for request/field/terms semantics and W3's bounded implementation task.

The individually reviewed timezone inference uses the named official Hualien place/address/coordinate, Taiwan's national standard-time statement and IANA's region mapping together. It does not infer a zone at runtime from a country code or an Open-Meteo auto value. Record the actual tzdb version when running a resolver. The tourism coordinate is a representative request point of unknown metre accuracy; provider-selected grid coordinates will be a different role and must be retained. Coastal wind, horizon and exact subject representativeness are not validated.

Source facts were read from the official URLs/locators in `evidence[]` using web retrieval. Full original page bytes were not archived; do not invent a page-body hash or call this a provider weather capture. No live Open-Meteo response was captured in this gate. Original weather response/hash/replay belongs in W3's next opt-in capture.

Usage is admitted only for the stated noncommercial public research purpose, with attribution, budget and no implicit commercial entitlement. No scheduled execution, merge or deployment is authorized. W1/W2 coding-agent review is distinct from external human approval, which remains PENDING. W5 must independently accept the new W1/W2 trees before source pins or public data can advance.
