# CL-WG-16: Python-side cross-language pin tests for the WeatherGrid PNG
# prerender pipeline.
#
# The generator (scripts/weathergrid_png_prerender.mjs) is Node so it can import
# the EXACT palette module the browser draws with (the honest single-source
# rule). These tests execute it from Python and verify the artifacts with an
# INDEPENDENT Python reimplementation of the palette math, so any drift in the
# shared palette or the generator's color conversion is caught here too.
#
# Run: python -m unittest test_weathergrid_png_prerender -v
import base64
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

REPO = os.path.dirname(os.path.abspath(__file__))
GENERATOR = os.path.join(REPO, "scripts", "weathergrid_png_prerender.mjs")


# ---- independent CSS hsl() -> 8-bit RGB (no imports from the JS side) ----
def hsl_to_rgb(h, s, l):
    s /= 100.0
    l /= 100.0

    def k(n):
        return (n + h / 30.0) % 12

    a = s * min(l, 1 - l)

    def f(n):
        kn = k(n)
        return l - a * max(-1.0, min(kn - 3.0, min(9.0 - kn, 1.0)))

    return tuple(round(255 * x) for x in (f(0), f(8), f(4)))


# ---- independent cloud opacity stops (interpolateStops on CLOUD_OPACITY_STOPS) ----
CLOUD_OPACITY_STOPS = [(0, .02), (20, .12), (40, .32), (50, .55), (70, .72), (85, .88), (100, 1)]


def cloud_opacity(value):
    v = max(0.0, min(100.0, float(value)))
    if v <= CLOUD_OPACITY_STOPS[0][0]:
        return CLOUD_OPACITY_STOPS[0][1]
    for i in range(1, len(CLOUD_OPACITY_STOPS)):
        x1, y1 = CLOUD_OPACITY_STOPS[i]
        x0, y0 = CLOUD_OPACITY_STOPS[i - 1]
        if v <= x1:
            return y0 + (y1 - y0) * (v - x0) / (x1 - x0)
    return CLOUD_OPACITY_STOPS[-1][1]


# ---- independent visibility opacity (domain 0..30, .08+.92*(1-t)^.8) ----
def visibility_opacity(value):
    t = max(0.0, min(1.0, float(value) / 30.0))
    return .08 + .92 * (1 - t) ** .8


# CL-WG-21: Windy-style monotonic lightness ramp (deep blue -> gray-white -> white).
CLOUD_BANDS = [
    (0, 20, "hsl(214 78% 44%)"),
    (20, 40, "hsl(211 66% 58%)"),
    (40, 50, "hsl(209 44% 71%)"),
    (50, 70, "hsl(208 28% 82%)"),
    (70, 85, "hsl(207 16% 91%)"),
    (85, 100, "hsl(206 8% 97%)"),
]

# CL-WG-21: low cloud keeps the same ladder with a slate gray-blue base tone.
LOW_CLOUD_BANDS = [
    (0, 20, "hsl(205 62% 48%)"),
    (20, 40, "hsl(204 50% 60%)"),
    (40, 50, "hsl(203 34% 70%)"),
    (50, 70, "hsl(202 24% 79%)"),
    (70, 85, "hsl(201 16% 87%)"),
    (85, 100, "hsl(200 12% 92%)"),
]


def cloud_color(value, bands=None):
    v = max(0.0, min(100.0, float(value)))
    table = bands if bands is not None else CLOUD_BANDS
    for _lo, hi, css in table:
        if v < hi:
            return css
    return table[-1][2]


def parse_hsl(css):
    parts = css.replace("hsl(", "").replace(")", "").replace("%", "").split()
    return float(parts[0]), float(parts[1]), float(parts[2])


def decode_png_rgba(path):
    with open(path, "rb") as fh:
        buf = fh.read()
    assert buf[:8] == b"\x89PNG\r\n\x1a\n"
    off = 8
    width = height = None
    idat = b""
    while off < len(buf):
        (length,) = struct.unpack(">I", buf[off:off + 4])
        ctype = buf[off + 4:off + 8].decode("ascii")
        data = buf[off + 8:off + 8 + length]
        if ctype == "IHDR":
            width, height = struct.unpack(">II", data[:8])
            assert data[8] == 8 and data[9] == 6, "expect 8-bit RGBA"
        elif ctype == "IDAT":
            idat += data
        off += 12 + length
    raw = zlib.decompress(idat)
    stride = width * 4
    rgba = bytearray(width * height * 4)
    for y in range(height):
        assert raw[y * (stride + 1)] == 0, "filter none expected"
        rgba[y * stride:(y + 1) * stride] = raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)]
    return width, height, bytes(rgba)


def pixel(rgba, width, x, y):
    o = (y * width + x) * 4
    return tuple(rgba[o:o + 4])


class PalettePinTest(unittest.TestCase):
    """Pin the JS palette formulas against the independent Python math."""

    @classmethod
    def setUpClass(cls):
        node = shutil.which("node")
        assert node, "node is required for these tests"
        cls.node = node
        # Dump a grid of pinned palette outputs from the shared module.
        script = (
            "const p = require('./assets/weather-map-palette.js');"
            "const cloud = p.LAYER_RENDER_CONFIG.total_cloud_percent;"
            "const low = p.LAYER_RENDER_CONFIG.low_cloud_percent;"
            "const vis = p.LAYER_RENDER_CONFIG.visibility_km;"
            "const out = [];"
            "for (const v of [0, 5, 19.9, 20, 30, 45, 50, 55, 70, 80, 99, 100]) {"
            "  out.push({layer:'cloud', value:v, color:p.colorFor(v, cloud), alpha:p.cellOpacityFor(v, cloud)});"
            "  out.push({layer:'cloudLow', value:v, color:p.colorFor(v, low), alpha:p.cellOpacityFor(v, low)});"
            "}"
            "for (const v of [0, 3, 10, 15, 22, 30]) {"
            "  out.push({layer:'visibility', value:v, color:p.colorFor(v, vis), alpha:p.cellOpacityFor(v, vis)});"
            "}"
            "console.log(JSON.stringify({version:p.PALETTE_VERSION, samples:out}));"
        )
        res = subprocess.run(
            [cls.node, "-e", script], cwd=REPO, capture_output=True, text=True, check=True
        )
        cls.dump = json.loads(res.stdout)

    def test_palette_version_is_declared(self):
        self.assertTrue(self.dump["version"])
        # Manifests must carry the same version string.
        manifest = os.path.join(REPO, "weathergrid", "png", "tw", "manifest.json")
        with open(manifest, encoding="utf-8") as fh:
            self.assertEqual(json.load(fh)["palette_version"], self.dump["version"])

    def test_cloud_colors_match_independent_hsl_math(self):
        for s in self.dump["samples"]:
            if s["layer"] != "cloud":
                continue
            expected_css = cloud_color(s["value"])
            self.assertEqual(s["color"], expected_css,
                             f"cloud color drift at value {s['value']}")
            rgb = hsl_to_rgb(*parse_hsl(s["color"]))
            # Pinned canonical RGB values (computed once, hand-verified):
            pins = {
                "hsl(214 78% 44%)": (25, 101, 200),
                "hsl(211 66% 58%)": (77, 146, 219),
                "hsl(209 44% 71%)": (149, 182, 214),
                "hsl(208 28% 82%)": (196, 210, 222),
                "hsl(207 16% 91%)": (228, 232, 236),
                "hsl(206 8% 97%)": (247, 247, 248),
            }
            self.assertEqual(rgb, pins[s["color"]], f"RGB pin failed for {s['color']}")

    def test_low_cloud_colors_match_independent_hsl_math(self):
        for s in self.dump["samples"]:
            if s["layer"] != "cloudLow":
                continue
            expected_css = cloud_color(s["value"], LOW_CLOUD_BANDS)
            self.assertEqual(s["color"], expected_css,
                             f"low cloud color drift at value {s['value']}")
            rgb = hsl_to_rgb(*parse_hsl(s["color"]))
            pins = {
                "hsl(205 62% 48%)": (47, 135, 198),
                "hsl(204 50% 60%)": (102, 163, 204),
                "hsl(203 34% 70%)": (152, 185, 205),
                "hsl(202 24% 79%)": (189, 205, 214),
                "hsl(201 16% 87%)": (217, 223, 227),
                "hsl(200 12% 92%)": (232, 235, 237),
            }
            self.assertEqual(rgb, pins[s["color"]], f"RGB pin failed for {s['color']}")

    def test_cloud_opacities_match_independent_stops(self):
        for s in self.dump["samples"]:
            if s["layer"] != "cloud":
                continue
            expected = round(cloud_opacity(s["value"]) * 255)
            self.assertEqual(round(s["alpha"] * 255), expected,
                             f"cloud alpha drift at value {s['value']}")

    def test_visibility_color_and_opacity_match_independent_math(self):
        for s in self.dump["samples"]:
            if s["layer"] != "visibility":
                continue
            t = max(0.0, min(1.0, s["value"] / 30.0))
            hue = 5 + t * 145
            light = 36 + t * 28
            # Exact string form: JS builds `hsl(${hue} 72% ${light}%)` — the
            # hue/light may be floats; compare parsed numbers instead of raw
            # strings.
            self.assertEqual(parse_hsl(s["color"])[1], 72.0)
            self.assertAlmostEqual(parse_hsl(s["color"])[2], light, places=9)
            self.assertAlmostEqual(parse_hsl(s["color"])[0], hue, places=9)
            rgb = hsl_to_rgb(*parse_hsl(s["color"]))
            self.assertEqual(rgb, hsl_to_rgb(hue, 72, light))
            expected_alpha = round(visibility_opacity(s["value"]) * 255)
            self.assertEqual(round(s["alpha"] * 255), expected_alpha,
                             f"visibility alpha drift at value {s['value']}")


class GeneratedBundlePinTest(unittest.TestCase):
    """Run the real generator on a real tw GFS bundle slice and pin pixels."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="wg16py-")
        node = shutil.which("node")
        assert node, "node is required"
        bundle_path = os.path.join(REPO, "weathergrid", "gfs_tw_weather_browser.json")
        with open(bundle_path, encoding="utf-8") as fh:
            bundle = json.load(fh)
        # Keep the full grid (row-flip verification needs real geometry) but
        # only the first frame for speed.
        bundle["frames"] = bundle["frames"][:1]
        cls.bundle = bundle
        cls.bundle_path = os.path.join(cls.tmp, "gfs_slice.json")
        with open(cls.bundle_path, "w", encoding="utf-8") as fh:
            json.dump(bundle, fh)
        subprocess.run(
            [node, GENERATOR, "--out", os.path.join(cls.tmp, "png"),
             f"region=tw,source=gfs,bundle={cls.bundle_path}"],
            cwd=REPO, check=True, capture_output=True, text=True,
        )
        with open(os.path.join(cls.tmp, "png", "tw", "manifest.json"), encoding="utf-8") as fh:
            cls.manifest = json.load(fh)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_manifest_structure(self):
        m = self.manifest
        self.assertEqual(m["schema_version"], 1)
        self.assertEqual(m["region"], "tw")
        self.assertTrue(m["palette_version"])
        src = m["sources"]["gfs"]
        self.assertEqual(src["grid"]["rows"], self.bundle["grid"]["rows"])
        self.assertEqual(src["grid"]["cols"], self.bundle["grid"]["cols"])
        for key in ("total_cloud_percent", "low_cloud_percent", "visibility_km"):
            layer = src["layers"].get(key)
            self.assertIsNotNone(layer, f"{key} missing from manifest")
            self.assertTrue(layer["covered"])
            self.assertEqual(len(layer["frames"]), len(self.bundle["frames"]))
            for f in layer["frames"]:
                self.assertTrue(f["valid_time_utc"])
                self.assertGreater(f["bytes"], 0)

    def test_first_frame_pixels_match_independent_palette(self):
        layer = self.manifest["sources"]["gfs"]["layers"]["total_cloud_percent"]
        frame = layer["frames"][0]
        png_path = os.path.join(self.tmp, "png", "tw", frame["file"])
        width, height, rgba = decode_png_rgba(png_path)
        rows = self.bundle["grid"]["rows"]
        cols = self.bundle["grid"]["cols"]
        self.assertEqual((width, height), (cols, rows))
        values = self.bundle["frames"][0]["values"]["total_cloud_percent"]
        meta = self.bundle["fields"]["total_cloud_percent"]
        scale = meta.get("scale", 1) or 1
        wrap = meta.get("wrap")
        # Verify a deterministic sample: corners + center of the grid.
        spots = [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1),
                 (rows // 2, cols // 2)]
        for (r, c) in spots:
            v = values[r * cols + c]
            # PNG rows run north->south; bundle latitudes ascend (row 0 = south).
            py = rows - 1 - r
            got = pixel(rgba, width, c, py)
            if v is None:
                self.assertEqual(got, (0, 0, 0, 0), f"cell ({r},{c}) should be transparent")
                continue
            # decodeValue semantics: encoded * scale, optional wrap.
            v = v * scale
            if wrap:
                v = ((v % wrap) + wrap) % wrap
            css = cloud_color(v)
            expected_rgb = hsl_to_rgb(*parse_hsl(css))
            expected_a = round(cloud_opacity(v) * 255)
            self.assertEqual(got[:3], expected_rgb,
                             f"cell ({r},{c}) value {v}: {got[:3]} != {expected_rgb}")
            self.assertEqual(got[3], expected_a,
                             f"cell ({r},{c}) alpha {got[3]} != {expected_a}")

    def test_visibility_first_frame_corners(self):
        layer = self.manifest["sources"]["gfs"]["layers"]["visibility_km"]
        frame = layer["frames"][0]
        width, height, rgba = decode_png_rgba(os.path.join(self.tmp, "png", "tw", frame["file"]))
        values = self.bundle["frames"][0]["values"]["visibility_km"]
        meta = self.bundle["fields"]["visibility_km"]
        scale = meta.get("scale", 1) or 1
        rows, cols = self.bundle["grid"]["rows"], self.bundle["grid"]["cols"]
        for (r, c) in [(0, 0), (rows - 1, cols - 1)]:
            v = values[r * cols + c]
            py = rows - 1 - r
            got = pixel(rgba, width, c, py)
            if v is None:
                self.assertEqual(got, (0, 0, 0, 0))
                continue
            v = v * scale
            t = max(0.0, min(1.0, v / 30.0))
            expected_rgb = hsl_to_rgb(5 + t * 145, 72, 36 + t * 28)
            expected_a = round(visibility_opacity(v) * 255)
            self.assertEqual(got[:3], expected_rgb)
            self.assertEqual(got[3], expected_a)


class GeneratorDeterminismTest(unittest.TestCase):
    def test_same_input_produces_byte_identical_png(self):
        tmp = tempfile.mkdtemp(prefix="wg16det-")
        try:
            bundle = {
                "schema_version": 1, "model": "DET",
                "bbox": {"leftlon": 105, "rightlon": 106, "bottomlat": 5, "toplat": 6},
                "grid": {"rows": 3, "cols": 3, "latitudes": [5, 5.5, 6],
                         "longitudes": [105, 105.5, 106]},
                "fields": {"total_cloud_percent": {"scale": 1}},
                "frames": [{"forecast_hour": 0,
                            "valid_time_utc": "2026-11-03T12:00:00+00:00",
                            "values": {"total_cloud_percent": [0, 30, 55, 70, 85, 100, 20, 45, None]}}],
            }
            bp = os.path.join(tmp, "b.json")
            with open(bp, "w", encoding="utf-8") as fh:
                json.dump(bundle, fh)
            outs = []
            node = shutil.which("node")
            assert node, "node is required"
            for i in range(2):
                out = os.path.join(tmp, f"out{i}")
                subprocess.run([node, GENERATOR, "--out", out,
                                f"region=tw,source=d,bundle={bp}"],
                               cwd=REPO, check=True, capture_output=True)
                with open(os.path.join(out, "tw", "d", "total_cloud_percent", "f000.png"), "rb") as fh:
                    outs.append(fh.read())
            self.assertEqual(outs[0], outs[1])
            # And the 3x3 grid pins every cloud band + the transparent hole.
            width, height, rgba = decode_png_rgba(os.path.join(tmp, "out0", "tw", "d", "total_cloud_percent", "f000.png"))
            vals = bundle["frames"][0]["values"]["total_cloud_percent"]
            for idx, v in enumerate(vals):
                r, c = divmod(idx, 3)
                py = 2 - r  # north-up flip
                got = pixel(rgba, width, c, py)
                if v is None:
                    self.assertEqual(got, (0, 0, 0, 0))
                else:
                    self.assertEqual(got, hsl_to_rgb(*parse_hsl(cloud_color(v))) + (round(cloud_opacity(v) * 255),))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()