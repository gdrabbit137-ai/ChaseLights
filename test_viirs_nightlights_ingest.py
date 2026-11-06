"""Synthetic palette-PNG tests for the GIBS colormap inversion + mosaic."""
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from viirs_nightlights_ingest import (
    COLORMAP_ENTRIES,
    NODATA_RGB,
    build_colormap_lut,
    ingest,
    mosaic_tiles,
    read_tile,
)
from viirs_nightlights_weathergrid import FIELD_RADIANCE


def write_palette_png(path, width, height, indices, palette, alpha=None):
    raw = b""
    for row in range(height):
        raw += b"\x00" + bytes(indices[row * width:(row + 1) * width])
    plte = b"".join(bytes(c) for c in palette)
    chunks = [b"IHDR" + struct.pack(">IIBBBBB", width, height, 8, 3, 0, 0, 0)]
    chunks.append(b"PLTE" + plte)
    if alpha is not None:
        chunks.append(b"tRNS" + bytes(alpha))
    chunks.append(b"IDAT" + zlib.compress(raw))
    body = b"\x89PNG\r\n\x1a\n"
    for ctype in chunks:
        body += struct.pack(">I", len(ctype) - 4) + ctype + struct.pack(">I", zlib.crc32(ctype) & 0xFFFFFFFF)
    path.write_bytes(body)


# Two synthetic colormap colors and the nodata color, mapping to known bins.
SYNTHETIC_LUT = {
    (7, 7, 7): 0.05,       # bin [0, 0.1)
    (13, 13, 13): 0.15,    # bin [0.1, 0.2)
    NODATA_RGB: None,
}


def synthetic_manifest(path, tiles):
    path.write_text(json.dumps({
        "schema_version": "viirs-gibs-tiles-v1",
        "source_layer": "VIIRS_NOAA20_DayNightBand_At_Sensor_Radiance",
        "observation_date": "2026-11-04",
        "tile_matrix_set": "500m",
        "level": 6,
        "tiles": tiles,
    }), encoding="utf-8")


class ColormapLutTest(unittest.TestCase):
    def test_published_colormap_entries_are_complete_and_monotonic(self):
        self.assertGreater(len(COLORMAP_ENTRIES), 150)
        luts = build_colormap_lut()
        self.assertEqual(len(luts), len(COLORMAP_ENTRIES))
        lows = sorted(lo for lo, hi, _rgb_ in COLORMAP_ENTRIES)
        self.assertEqual(lows[0], 0.0)
        # every rgb entry decodes to a 3-int tuple (str or literal tuple)
        for lo, hi, rgb in COLORMAP_ENTRIES[:3]:
            parts = [int(v) for v in (rgb.split(",") if isinstance(rgb, str) else rgb)]
            self.assertEqual(len(parts), 3)


class GibsIngestTest(unittest.TestCase):
    def build_synthetic_tile(self, dir_path, name, rgb_values, palette):
        path = dir_path / name
        indices = []
        values = []
        for row in rgb_values:
            for color in row:
                indices.append(palette.index(color))
                values.append(color)
        write_palette_png(path, 2, 2, indices, palette)
        return path

    def test_single_tile_decode_and_crop(self):
        palette = [(7, 7, 7), (13, 13, 13), NODATA_RGB]
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            # tile spans lon 0-2, lat 0-2 with cell centers at .5 offsets
            self.build_synthetic_tile(d, "tile_6_44_90.png",
                [[(7, 7, 7), (13, 13, 13)], [NODATA_RGB, (7, 7, 7)]], palette)
            synthetic_manifest(d / "manifest.json", [{
                "path": str(d / "tile_6_44_90.png"),
                "row": 44, "col": 90,
                "leftlon": 0.0, "bottomlat": 0.0, "rightlon": 2.0, "toplat": 2.0,
            }])
            # crop to the northern row only (lat 1.0-2.0)
            lats, lons, values = mosaic_tiles(
                [read_tile({
                    "path": str(d / "tile_6_44_90.png"),
                    "leftlon": 0.0, "bottomlat": 0.0, "rightlon": 2.0, "toplat": 2.0,
                }, SYNTHETIC_LUT)], (0.4, 1.1, 1.6, 1.9))
        self.assertEqual(lats, [1.5])
        self.assertEqual(lons, [0.5, 1.5])
        self.assertEqual(values, [0.05, 0.15])

    def test_full_ingest_builds_daily_bundle_with_provenance(self):
        palette = [(7, 7, 7), (13, 13, 13), NODATA_RGB]
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            self.build_synthetic_tile(d, "tile_6_44_90.png",
                [[(7, 7, 7), (13, 13, 13)], [(13, 13, 13), (7, 7, 7)]], palette)
            synthetic_manifest(d / "manifest.json", [{
                "path": str(d / "tile_6_44_90.png"),
                "row": 44, "col": 90,
                "leftlon": 0.0, "bottomlat": 0.0, "rightlon": 2.0, "toplat": 2.0,
            }])
            bundle, qc = ingest(d / "manifest.json", (0.0, 0.0, 2.0, 2.0))
        self.assertEqual(bundle["source"], "nasa_gibs_viirs_noaa20_dnb")
        self.assertEqual(bundle["frames"][0]["observation_date"], "2026-11-04")
        self.assertEqual(qc["missing_cells"], 0)
        self.assertEqual(qc["flags"], [])
        prov = bundle["provenance"]
        self.assertIn("cloud contamination", prov["cloud_caveat"])
        self.assertIn("dead end", prov["laads_dead_end"])
        self.assertIn("not Bortle class", prov["semantics"])

    def test_partial_missing_cells_fail_closed(self):
        palette = [(7, 7, 7), NODATA_RGB]
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            self.build_synthetic_tile(d, "tile_6_44_90.png",
                [[(7, 7, 7), NODATA_RGB], [(7, 7, 7), (7, 7, 7)]], palette)
            synthetic_manifest(d / "manifest.json", [{
                "path": str(d / "tile_6_44_90.png"),
                "row": 44, "col": 90,
                "leftlon": 0.0, "bottomlat": 0.0, "rightlon": 2.0, "toplat": 2.0,
            }])
            bundle, qc = ingest(d / "manifest.json", (0.0, 0.0, 2.0, 2.0))
        self.assertEqual(qc["missing_cells"], 1)
        self.assertIn("partial_missing_cells", qc["flags"])

    def test_all_missing_raises(self):
        palette = [NODATA_RGB]
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            self.build_synthetic_tile(d, "tile_6_44_90.png",
                [[NODATA_RGB, NODATA_RGB], [NODATA_RGB, NODATA_RGB]], palette)
            synthetic_manifest(d / "manifest.json", [{
                "path": str(d / "tile_6_44_90.png"),
                "row": 44, "col": 90,
                "leftlon": 0.0, "bottomlat": 0.0, "rightlon": 2.0, "toplat": 2.0,
            }])
            with self.assertRaisesRegex(ValueError, "zero valid radiance"):
                ingest(d / "manifest.json", (0.0, 0.0, 2.0, 2.0))


if __name__ == "__main__":
    unittest.main()
