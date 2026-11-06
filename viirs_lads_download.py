"""NASA LAADS VNP46A4 download — DEAD END (do not use).

DEAD END documented per CL-CI-20 (owner ruling + LAADS evidence, 2026-11):
- Suomi NPP data supply was TERMINATED 2026-11-01;
- VNP46A4 is an Suomi NPP (SNPP) product, so the annual cloud-free composite
  can no longer be sourced: the product lifecycle has ended;
- the LAADS scripted-download auth chain additionally required a product
  EULA/license that was never reliably obtainable (CL-CI-19 evidence).

Replacement pipeline: NASA GIBS public WMTS daily VIIRS DNB tiles
(NOAA-20 primary) — see viirs_gibs_download.py + viirs_nightlights_ingest.py.

This module is kept only so that stale callers fail CLOSED with an explicit
error instead of silently producing fabricated data.
"""

DEAD_END_REASON = (
    "LAADS VNP46A4 is a dead end: SNPP data supply terminated 2026-11-01 and "
    "VNP46A4 is an SNPP product (product lifecycle end-of-life). Use the "
    "NASA GIBS daily VIIRS DNB pipeline (viirs_gibs_download.py) instead."
)


def fail_dead_end():
    raise SystemExit(DEAD_END_REASON)


def main():
    fail_dead_end()


if __name__ == "__main__":
    main()
