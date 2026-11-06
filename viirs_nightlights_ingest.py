"""Ingest NASA GIBS daily VIIRS DNB night-lights tiles into WeatherGrid JSON.

CL-CI-20: replaces the LAADS VNP46A4 pipeline (DEAD END - product lifecycle
termination). Source: NASA GIBS public WMTS rendered daily DNB tiles
(NOAA-20 primary). Radiance is recovered by inverting the published GIBS
colormap LUT, so values are colormap-bin-quantized approximations, not raw
HDF5 radiance. The daily product is CLOUD-AFFECTED - this is NOT a cloud-free
composite and no per-pixel quality flags exist in the rendered layer.
"""

from __future__ import annotations

import argparse
import json
import struct
import zlib
from pathlib import Path

from viirs_nightlights_weathergrid import build_bundle

# GIBS colormap v1.3 "Radiance" entries for VIIRS DayNightBand At-Sensor
# Radiance: (lo_nw_cm2_sr, hi_nw_cm2_sr, rgb). Verified against
# https://gibs.earthdata.nasa.gov/colormaps/v1.3/VIIRS_DayNightBand_At_Sensor_Radiance.xml
# on 2026-11-07. The saturated top bin is capped at its lower bound.
COLORMAP_ENTRIES = (
    (0, 0.1, (7,7,7)),
    (0.1, 0.2, (13,13,13)),
    (0.2, 0.3, (19,19,19)),
    (0.3, 0.4, (24,24,24)),
    (0.4, 0.5, (29,29,29)),
    (0.5, 0.6, (33,33,33)),
    (0.6, 0.7, (37,37,37)),
    (0.7, 0.8, (41,41,41)),
    (0.8, 0.9, (45,45,45)),
    (0.9, 1, (48,48,48)),
    (1, 1.1, (52,52,52)),
    (1.1, 1.2, (55,55,55)),
    (1.2, 1.3, (58,58,58)),
    (1.3, 1.4, (61,61,61)),
    (1.4, 1.5, (64,64,64)),
    (1.5, 1.6, (67,67,67)),
    (1.6, 1.7, (69,69,69)),
    (1.7, 1.8, (72,72,72)),
    (1.8, 1.9, (74,74,74)),
    (1.9, 2, (77,77,77)),
    (2, 2.1, (79,79,79)),
    (2.1, 2.2, (81,81,81)),
    (2.2, 2.3, (83,83,83)),
    (2.3, 2.4, (85,85,85)),
    (2.4, 2.5, (87,87,87)),
    (2.5, 2.6, (89,89,89)),
    (2.6, 2.7, (91,91,91)),
    (2.7, 2.8, (93,93,93)),
    (2.8, 2.9, (95,95,95)),
    (2.9, 3, (96,96,96)),
    (3, 3.1, (98,98,98)),
    (3.1, 3.2, (100,100,100)),
    (3.2, 3.3, (101,101,101)),
    (3.3, 3.4, (103,103,103)),
    (3.4, 3.5, (105,105,105)),
    (3.5, 3.6, (106,106,106)),
    (3.6, 3.7, (108,108,108)),
    (3.7, 3.8, (109,109,109)),
    (3.8, 3.9, (111,111,111)),
    (3.9, 4, (112,112,112)),
    (4, 4.1, (113,113,113)),
    (4.1, 4.2, (115,115,115)),
    (4.2, 4.3, (116,116,116)),
    (4.3, 4.4, (117,117,117)),
    (4.4, 4.5, (118,118,118)),
    (4.5, 4.6, (120,120,120)),
    (4.6, 4.7, (121,121,121)),
    (4.7, 4.8, (122,122,122)),
    (4.8, 4.9, (123,123,123)),
    (4.9, 5, (125,125,125)),
    (5, 5.1, (126,126,126)),
    (5.1, 5.2, (127,127,127)),
    (5.2, 5.3, (128,128,128)),
    (5.3, 5.4, (129,129,129)),
    (5.4, 5.5, (130,130,130)),
    (5.5, 5.6, (131,131,131)),
    (5.6, 5.7, (132,132,132)),
    (5.7, 5.8, (133,133,133)),
    (5.8, 5.9, (134,134,134)),
    (5.9, 6, (135,135,135)),
    (6, 6.1, (136,136,136)),
    (6.1, 6.2, (137,137,137)),
    (6.2, 6.3, (138,138,138)),
    (6.3, 6.4, (139,139,139)),
    (6.4, 6.5, (140,140,140)),
    (6.5, 6.6, (141,141,141)),
    (6.6, 6.7, (142,142,142)),
    (6.7, 6.8, (143,143,143)),
    (6.8, 7, (144,144,144)),
    (7, 7.1, (145,145,145)),
    (7.1, 7.2, (146,146,146)),
    (7.2, 7.3, (147,147,147)),
    (7.3, 7.4, (148,148,148)),
    (7.4, 7.6, (149,149,149)),
    (7.6, 7.7, (150,150,150)),
    (7.7, 7.8, (151,151,151)),
    (7.8, 7.9, (152,152,152)),
    (7.9, 8.1, (153,153,153)),
    (8.1, 8.2, (154,154,154)),
    (8.2, 8.3, (155,155,155)),
    (8.3, 8.5, (156,156,156)),
    (8.5, 8.6, (157,157,157)),
    (8.6, 8.8, (158,158,158)),
    (8.8, 8.9, (159,159,159)),
    (8.9, 9, (160,160,160)),
    (9, 9.2, (161,161,161)),
    (9.2, 9.3, (162,162,162)),
    (9.3, 9.5, (163,163,163)),
    (9.5, 9.6, (164,164,164)),
    (9.6, 9.8, (165,165,165)),
    (9.8, 100, (166,166,166)),
    (10, 10.1, (167,167,167)),
    (10.1, 10.3, (168,168,168)),
    (10.3, 10.4, (169,169,169)),
    (10.4, 10.6, (170,170,170)),
    (10.6, 10.8, (171,171,171)),
    (10.8, 11, (172,172,172)),
    (11, 11.1, (173,173,173)),
    (11.1, 11.3, (174,174,174)),
    (11.3, 11.5, (175,175,175)),
    (11.5, 11.7, (176,176,176)),
    (11.7, 11.8, (177,177,177)),
    (11.8, 12, (178,178,178)),
    (12, 12.2, (179,179,179)),
    (12.2, 12.4, (180,180,180)),
    (12.4, 12.6, (181,181,181)),
    (12.6, 12.8, (182,182,182)),
    (12.8, 13, (183,183,183)),
    (13, 13.2, (184,184,184)),
    (13.2, 13.4, (185,185,185)),
    (13.4, 13.6, (186,186,186)),
    (13.6, 13.9, (187,187,187)),
    (13.9, 14.1, (188,188,188)),
    (14.1, 14.3, (189,189,189)),
    (14.3, 14.5, (190,190,190)),
    (14.5, 14.7, (191,191,191)),
    (14.7, 15, (192,192,192)),
    (15, 15.2, (193,193,193)),
    (15.2, 15.4, (194,194,194)),
    (15.4, 15.7, (195,195,195)),
    (15.7, 15.9, (196,196,196)),
    (15.9, 16.2, (197,197,197)),
    (16.2, 16.4, (198,198,198)),
    (16.4, 16.7, (199,199,199)),
    (16.7, 16.9, (200,200,200)),
    (16.9, 17.2, (201,201,201)),
    (17.2, 17.5, (202,202,202)),
    (17.5, 17.7, (203,203,203)),
    (17.7, 18, (204,204,204)),
    (18, 18.3, (205,205,205)),
    (18.3, 18.6, (206,206,206)),
    (18.6, 18.8, (207,207,207)),
    (18.8, 19.1, (208,208,208)),
    (19.1, 19.4, (209,209,209)),
    (19.4, 19.7, (210,210,210)),
    (19.7, 20, (211,211,211)),
    (20, 20.3, (212,212,212)),
    (20.3, 20.7, (213,213,213)),
    (20.7, 21, (214,214,214)),
    (21, 21.3, (215,215,215)),
    (21.3, 21.6, (216,216,216)),
    (21.6, 21.9, (217,217,217)),
    (21.9, 22.3, (218,218,218)),
    (22.3, 22.6, (219,219,219)),
    (22.6, 23, (220,220,220)),
    (23, 23.3, (221,221,221)),
    (23.3, 23.7, (222,222,222)),
    (23.7, 24, (223,223,223)),
    (24, 24.4, (224,224,224)),
    (24.4, 24.8, (225,225,225)),
    (24.8, 25.1, (226,226,226)),
    (25.1, 25.5, (227,227,227)),
    (25.5, 25.9, (228,228,228)),
    (25.9, 26.3, (229,229,229)),
    (26.3, 26.7, (230,230,230)),
    (26.7, 27.1, (231,231,231)),
    (27.1, 27.5, (232,232,232)),
    (27.5, 27.9, (233,233,233)),
    (27.9, 28.3, (234,234,234)),
    (28.3, 28.8, (235,235,235)),
    (28.8, 29.2, (236,236,236)),
    (29.2, 29.6, (237,237,237)),
    (29.6, 30.1, (238,238,238)),
    (30.1, 30.5, (239,239,239)),
    (30.5, 31, (240,240,240)),
    (31, 31.5, (241,241,241)),
    (31.5, 31.9, (242,242,242)),
    (31.9, 32.4, (243,243,243)),
    (32.4, 32.9, (244,244,244)),
    (32.9, 33.4, (245,245,245)),
    (33.4, 33.9, (246,246,246)),
    (33.9, 34.4, (247,247,247)),
    (34.4, 34.9, (248,248,248)),
    (34.9, 35.5, (249,249,249)),
    (35.5, 36, (250,250,250)),
    (36, 36.5, (251,251,251)),
    (36.5, 37.1, (252,252,252)),
    (37.1, 37.6, (253,253,253)),
    (37.6, 38.2, (254,254,254)),
    (38.2, 38.2, (255,255,255)),
)

NODATA_RGB = (0, 0, 160)  # GIBS "No Data" colormap entry (transparent)


def _rgb(text):
    return tuple(int(v) for v in text.split(","))


def build_colormap_lut():
    """Return {rgb: radiance_bin_midpoint} for colormap inversion."""
    lut = {}
    for lo, hi, rgb in COLORMAP_ENTRIES:
        color = _rgb(rgb) if isinstance(rgb, str) else tuple(rgb)
        lut[color] = (float(lo) + float(hi)) / 2.0
    return lut


def decode_png_palette(path):
    """Decode an 8-bit palette PNG with pure stdlib. Returns (rows, palette, alpha)."""
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a PNG file: {path}")
    pos = 8
    idat = b""
    palette = None
    alpha = None
    header = None
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        if ctype == b"IHDR":
            header = struct.unpack(">IIBBBBB", body)
        elif ctype == b"PLTE":
            palette = body
        elif ctype == b"tRNS":
            alpha = body
        elif ctype == b"IDAT":
            idat += body
        pos += 12 + length
    if header is None or palette is None:
        raise ValueError(f"unsupported PNG structure (needs 8-bit palette): {path}")
    width, height, bit_depth, color_type = header[0], header[1], header[2], header[3]
    if bit_depth != 8 or color_type != 3:
        raise ValueError(f"unsupported PNG bit depth/color type: {bit_depth}/{color_type}")
    raw = zlib.decompress(idat)
    stride = width + 1
    rows = []
    previous = bytearray(width)
    offset = 0
    for _ in range(height):
        filt = raw[offset]
        line = bytearray(raw[offset + 1:offset + stride])
        offset += stride
        if filt == 1:
            for i in range(width):
                line[i] = (line[i] + (line[i - 1] if i else 0)) & 255
        elif filt == 2:
            for i in range(width):
                line[i] = (line[i] + previous[i]) & 255
        elif filt == 3:
            for i in range(width):
                left = line[i - 1] if i else 0
                line[i] = (line[i] + ((left + previous[i]) >> 1)) & 255
        elif filt == 4:
            for i in range(width):
                a = line[i - 1] if i else 0
                b = previous[i]
                c = previous[i - 1] if i else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                predictor = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + predictor) & 255
        elif filt != 0:
            raise ValueError(f"unsupported PNG filter {filt}")
        rows.append(bytes(line))
        previous = line
    palette_colors = [
        (palette[i * 3], palette[i * 3 + 1], palette[i * 3 + 2])
        for i in range(len(palette) // 3)
    ]
    return rows, palette_colors, alpha


def build_pixel_lut(palette_colors, alpha, colormap_lut):
    """Map palette indices -> radiance or None (nodata/transparent/unmapped)."""
    lut = []
    for index, color in enumerate(palette_colors):
        transparent = alpha is not None and index < len(alpha) and alpha[index] == 0
        if transparent or color == NODATA_RGB or color not in colormap_lut:
            lut.append(None)
        else:
            lut.append(colormap_lut[color])
    return lut


def read_tile(record, colormap_lut):
    """Decode one GIBS tile into (lats, lons, values) on its own pixel grid."""
    rows, palette_colors, alpha = decode_png_palette(record["path"])
    pixel_lut = build_pixel_lut(palette_colors, alpha, colormap_lut)
    height = len(rows)
    width = len(rows[0])
    left, bottom, right, top = (
        record["leftlon"],
        record["bottomlat"],
        record["rightlon"],
        record["toplat"],
    )
    lat_step = (top - bottom) / height
    lon_step = (right - left) / width
    lats = [top - (row + 0.5) * lat_step for row in range(height)]
    lons = [left + (col + 0.5) * lon_step for col in range(width)]
    values = []
    for row_pixels in rows:
        for index in row_pixels:
            values.append(pixel_lut[index])
    return lats, lons, values


def _coord(value):
    # Tile edges are deterministic in the WMTS grid; rounding guards against
    # harmless floating-point differences between adjacent tiles.
    return round(float(value), 10)


def mosaic_tiles(tiles, bbox):
    """Merge decoded tiles onto one regular lat/lon union grid, cropped to bbox."""
    left, bottom, right, top = [float(v) for v in bbox]
    cells = {}
    for lats, lons, values in tiles:
        if len(values) != len(lats) * len(lons):
            raise ValueError("decoded tile cell count does not match coordinates")
        for row, lat in enumerate(lats):
            if not bottom <= lat <= top:
                continue
            lat_key = _coord(lat)
            for col, lon in enumerate(lons):
                if not left <= lon <= right:
                    continue
                key = (lat_key, _coord(lon))
                if key in cells and cells[key] != values[row * len(lons) + col]:
                    raise ValueError(f"conflicting GIBS mosaic cell at {key}")
                cells[key] = values[row * len(lons) + col]
    if not cells:
        raise ValueError("no GIBS cells intersect requested bbox")

    out_lats = sorted({k[0] for k in cells}, reverse=True)
    out_lons = sorted({k[1] for k in cells})
    out_values = [cells.get((lat, lon)) for lat in out_lats for lon in out_lons]
    return out_lats, out_lons, out_values


def ingest(manifest_path, bbox, fail_on_missing=True):
    """Build a daily WeatherGrid bundle + QC from a GIBS tile manifest.

    Fail-closed: a fully-missing decode raises; partially missing cells add a
    QC flag that fails the workflow's semantic validation.
    """
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    colormap_lut = build_colormap_lut()
    decoded = [read_tile(record, colormap_lut) for record in manifest["tiles"]]
    lats, lons, values = mosaic_tiles(decoded, bbox)
    missing = sum(1 for v in values if v is None)
    if missing == len(values):
        raise ValueError("GIBS tiles decoded to zero valid radiance cells")

    bundle, qc = build_bundle(
        lats,
        lons,
        values,
        observation_date=manifest["observation_date"],
        source_layer=manifest["source_layer"],
        tile_level=manifest["level"],
    )
    bundle["provenance"]["source_tile_count"] = len(manifest["tiles"])
    qc["source_tile_count"] = len(manifest["tiles"])
    qc["missing_cells"] = missing
    if missing and fail_on_missing:
        qc["flags"].append("partial_missing_cells")
    return bundle, qc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tiles-manifest", required=True)
    parser.add_argument("--bbox", required=True, help="leftlon,bottomlat,rightlon,toplat")
    parser.add_argument("--output", default="weathergrid/viirs_nightlights_tw_browser.json")
    parser.add_argument("--qc-output", default="weathergrid/viirs_nightlights_tw_qc.json")
    args = parser.parse_args()
    bbox = tuple(float(v) for v in args.bbox.split(","))
    if len(bbox) != 4:
        raise SystemExit("--bbox requires four comma-separated numbers")

    bundle, qc = ingest(args.tiles_manifest, bbox)
    output = Path(args.output)
    qc_output = Path(args.qc_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    qc_output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    qc_output.write_text(json.dumps(qc, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(output),
                "qc_output": str(qc_output),
                "rows": bundle["grid"]["rows"],
                "cols": bundle["grid"]["cols"],
                "observation_date": bundle["frames"][0]["observation_date"],
                "source_layer": bundle["provenance"]["source_layer"],
                "missing_cells": qc["missing_cells"],
            }
        )
    )


if __name__ == "__main__":
    main()
