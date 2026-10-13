# ChaseLights V2 M6b: NWS Raw Gridpoint Provenance Contract v0.1

Owner W1; research-stage proposal under Issue #467; W3 implementation follows in packages/core-v2/adapters. No changes to Legacy, V2 public Catalog, scores, navigation or research approvals.

## Official source and scope

The initial US test is Kerry Park / Seattle using a **representative regional sample**, NOT an independently surveyed photographer location. Obtain the raw gridpoint data via https://api.weather.gov/points/{lat},{lon}, read properties.forecastGridData, and then GET the returned https://api.weather.gov/gridpoints/{office}/{x},{y}. This is NOAA/NWS forecast data, NOT direct GFS initialization data. NWS documents the API as open data with rate limits, approximate grid size 2.5 km, and gridpoint validTime interval strings and data-layer uom. Sources:
- https://www.weather.gov/documentation/services-web-api
- https://github.com/weather-gov/api/blob/master/gridpoints.md

Official source updateTime is only data creation/refresh time, NOT the weather model run start. Provider-issued timestamp and run ID remain **null** until separately verified. Do not treat retrieved_at as provider issued_at.

## Required normalized record

Strict Draft-2020-12 schema: schema/weather-source-record-v0.1.schema.json.

A single record represents one numeric field and one exact interval, with:
- schema_version=0.1.0; provider=NOAA_NWS; source_kind=FORECAST
- source_url (official raw gridpoint endpoint), mapping_url (official /points lookup), source_sha256 (hash of original HTTP response bytes), source_update_time_utc, retrieved_at_utc
- grid office/x/y and representative sample latitude, longitude, coordinate_source, unknown coordinate_uncertainty_m, unknown native_resolution_m
- field and original uom; raw_value finite, NOT a boolean
- valid_from_utc and valid_until_utc with UTC half-open [start,end), preserving merged intervals (not assumed to be hourly)
- retrieval_mode = HTTPS_TLS or TEST_FIXTURE
- provider_issued_at_utc=null and provider_run_id=null
- data_state=RAW_ONLY, calibration_status=UNVALIDATED, recommendation_eligible=false, photography_verdict=NOT_EVALUABLE
- limitations_i18n has nonempty zh-TW, en, ja explaining this is a gridded raw forecast with no verified camera GPS or photographic prediction.

## W3 input-adapter acceptance

The importer MUST verify HTTPS host and no redirects, official /points URL-to-grid mapping, bounded body size and timeout, timestamp order and source update freshness, finite numeric field/unit, validTime ISO8601 start/duration and interval coverage, grid office/x/y consistency, raw byte hash and no ambiguity. Missing/null, unsupported duration, stale, malformed, wrong region/unit, unverifiable source or invalid timeframe all produce UNKNOWN, not zero/favorable.

A record passed to the API as an arbitrary dictionary is NOT thereby proven to come from NOAA. Fixture-only transport is marked TEST_FIXTURE and may exercise structural tests, never real provider authentication. Live HTTPS transport and source hash can establish transport provenance; no separate weather-model run ID is available in this pilot. Redistributed data retains public-service provenance and terms review.

Never infer the exact camera, subject or NavigationTarget coordinate from a point used for grid sampling. Access and closure warnings are independent non-scoring advisories. No unreviewed cloud thresholds, probabilities, weather-to-fog/sea-of-cloud inference, selected-date favorable scores, or test-only synthetic LIVE status.

WeatherGrid tiles, CWA humidity fog proxies and Himawari satellite imagery are separate products, not interchangeable with native NOAA NWS gridpoint forecast fields. Outside NWS coverage (e.g., Taiwan/Japan), return no data until an independently reviewed regional provider is available.

## Release gates

W1 tests must verify schema strictness and independent timestamp provenance; W3 unit tests use fixed JSON fixtures and negative cases. Opt-in real NWS probe may run separately, not as flaky mandatory CI. W5 must rotate exact W1/W3 pins after review and increase test counts without reducing existing 142 tests or bypassing W2 source/locale/access gates. The public V2 Research-only Preview remains unchanged.
