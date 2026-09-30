# B155 — Himawari-9 observed-cloud POC

## Goal

Add a no-subscription proof of concept for **observed** cloud data from JMA
Himawari-9, distributed freely through NOAA's Open Data Dissemination (NODD)
bucket on AWS.

This batch is deliberately observation-only. It must not present satellite
retrievals as forecast low/mid/high cloud cover and it does not change
Photography Opportunity scoring.

## Source

- observing platform: JMA Himawari-9 / Advanced Himawari Imager (AHI)
- distribution: NOAA NODD / AWS Open Data
- bucket: `s3://noaa-himawari9`, region `us-east-1`
- product family: `AHI-L2-FLDK-Clouds`
- nominal full-disk cadence: 10 minutes
- nominal native resolution: 2 km at nadir
- AWS account/API key: not required
- requested attribution: JMA + NOAA NODD

The relevant Level-2 products are:

- `AHI-CMSK_...` — cloud mask
- `AHI-CHGT_...` — cloud-top height/pressure/temperature

## Why this comes before LFM

JMA LFM is operationally attractive (1 km since 2026-03), but as of B155 it
is not present in Open-Meteo's public model list/Open Data mirror. Real-time
JMBSC LFM distribution has an ongoing fee. ChaseLights therefore keeps LFM
behind a source/cost gate and advances the free Himawari path first.

## Semantic guardrails

Himawari is an **observation** source.

Cloud-top height is not equivalent to a model's vertically integrated
low/mid/high cloud-cover diagnostics. In particular, a top-height product
cannot prove that a lower cloud deck is absent beneath a higher layer.

B155 therefore exposes only source/schema facts. Any later UI may show:

- observed cloud mask
- observed cloud-top height / pressure / temperature
- an explicitly labelled cloud-top category if useful

It must not label a cloud-top category as forecast "low cloud / mid cloud /
high cloud" coverage.

## POC validation

The B155 live smoke:

1. anonymously lists recent 10-minute Himawari-9 cloud-product prefixes;
2. requires a same-slot CMSK + CHGT pair;
3. opens the remote NetCDF/HDF5 objects through anonymous S3 range reads;
4. verifies a cloud-mask dataset is present;
5. verifies `CldTopHght` or an equivalent Cloud Top Height dataset is present;
6. records grid shape, time coverage, satellite, resolution, projection and
   geolocation-variable metadata without publishing the full disk.

No browser artifact is published in B155. A later batch may crop/reproject a
Taiwan observation product after the live schema is proven.


## Live result

Validated in GitHub Actions against a current same-slot Himawari-9 cloud pair.

- Full Disk product grid: **5500 × 5500**
- source product resolution: **2 km at nadir**
- source cadence: **10 minutes**
- HDF5 tile/chunk size for the selected AWIPS fields: **200 × 200**, gzip
- Taiwan QC window: rows **1343:1630**, columns **1626:1964**
- Taiwan QC window size: **287 × 338 = 97,006 pixels**
- fraction of the 30,250,000-pixel Full Disk: **~0.32%**
- geolocation checked from the file itself:
  - latitude span about **21.15°–27.42°N**
  - longitude span about **116.46°–125.08°E**
- cloud mask field: `CloudMaskBinaryAWIPS`
- cloud-top-height field: `CldTopHghtAWIPS`
- cloud-top-height product also provides parallax-corrected
  `Latitude_Pc` / `Longitude_Pc`

This proves a production path does **not** need to download either whole
Full-Disk file. The next batch should publish a compact Taiwan observation
bundle from this fixed-grid range-read and keep it explicitly separate from
forecast-model timelines.
