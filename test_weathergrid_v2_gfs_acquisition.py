import tempfile
import unittest
from pathlib import Path

from gfs_raw_poc import GFSRun
from weathergrid_v2_gfs_acquisition import (
    GFS_GRIB_VARS,
    aws_grib_url,
    fetch_cloud_subset,
    parse_gfs_idx,
    select_cloud_records,
)


IDX_FIXTURE = """1:0:d=2026100518:TMP:2 m above ground:anl:
2:100:d=2026100518:TCDC:entire atmosphere:anl:
3:200:d=2026100518:LCDC:low cloud layer:anl:
4:300:d=2026100518:MCDC:middle cloud layer:anl:
5:400:d=2026100518:HCDC:high cloud layer:anl:
6:500:d=2026100518:VIS:surface:anl:
"""


class FakeResponse:
    def __init__(self, *, text="", content=b"", status=200, headers=None):
        self.text = text
        self.content = content
        self.status_code = status
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self):
        self.gets = []
        self.heads = []

    def get(self, url, headers=None, timeout=None):
        self.gets.append((url, headers, timeout))
        if url.endswith(".idx"):
            return FakeResponse(text=IDX_FIXTURE)
        assert headers and headers["Range"].startswith("bytes=")
        return FakeResponse(content=b"GRIB" + b"x" * 96, status=206)

    def head(self, url, timeout=None):
        self.heads.append((url, timeout))
        return FakeResponse(headers={"Content-Length": "600"})


class GfsAwsAcquisitionTests(unittest.TestCase):
    def test_four_cloud_grib_variables(self):
        self.assertEqual(
            GFS_GRIB_VARS,
            {
                "cloud_cover": "TCDC",
                "cloud_cover_low": "LCDC",
                "cloud_cover_mid": "MCDC",
                "cloud_cover_high": "HCDC",
            },
        )

    def test_aws_url_uses_operational_025_path(self):
        run = GFSRun("20261005", "18", 3)
        self.assertEqual(
            aws_grib_url(run),
            "https://noaa-gfs-bdp-pds.s3.amazonaws.com/"
            "gfs.20261005/18/atmos/gfs.t18z.pgrb2.0p25.f003",
        )

    def test_idx_ranges_and_cloud_selection(self):
        records = parse_gfs_idx(IDX_FIXTURE)
        selected = select_cloud_records(records)
        self.assertEqual(selected["cloud_cover"].range_header, "bytes=100-199")
        self.assertEqual(selected["cloud_cover_low"].range_header, "bytes=200-299")
        self.assertEqual(selected["cloud_cover_mid"].range_header, "bytes=300-399")
        self.assertEqual(selected["cloud_cover_high"].range_header, "bytes=400-499")

    def test_missing_cloud_field_fails_closed(self):
        records = parse_gfs_idx(IDX_FIXTURE.replace(
            "5:400:d=2026100518:HCDC:high cloud layer:anl:\n", ""
        ))
        with self.assertRaises(KeyError):
            select_cloud_records(records)

    def test_fetch_uses_four_byte_ranges_not_tile_requests(self):
        run = GFSRun("20261005", "18", 0)
        session = FakeSession()
        with tempfile.TemporaryDirectory() as tmp:
            result = fetch_cloud_subset(
                run,
                Path(tmp) / "clouds.grib2",
                session=session,
            )
            self.assertEqual(result["fields"], [
                "cloud_cover",
                "cloud_cover_low",
                "cloud_cover_mid",
                "cloud_cover_high",
            ])
            self.assertEqual(len(result["messages"]), 4)
            self.assertEqual(len(session.gets), 5)  # one idx + four ranges
            self.assertFalse(session.heads)
            self.assertTrue((Path(tmp) / "clouds.grib2").read_bytes().startswith(b"GRIB"))
            self.assertEqual((Path(tmp) / "clouds.grib2").read_bytes().count(b"GRIB"), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
