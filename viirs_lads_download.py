"""Discover and download NASA LAADS VNP46A4 files using a bearer token."""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import re
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://ladsweb.modaps.eosdis.nasa.gov"
PRODUCT = "VNP46A4"
ARCHIVE_SET = "5200"
HDF5_MAGIC = b"\\x89HDF\\r\\n\\x1a\\n"
FILENAME_RE = re.compile(r"VNP46A4\.A(?P<year>\d{4})(?P<doy>\d{3})\.h\d{2}v\d{2}\.\d{3}\.[^.]+\.h5$")


def authorization_headers(token):
    if not token:
        raise ValueError("Earthdata/LAADS download token is required")
    return {
        "Authorization": f"Bearer {token}",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "ChaseLights-VIIRS/1.0",
    }


def search_url(year, bbox):
    left, bottom, right, top = [float(v) for v in bbox]
    params = {
        "products": PRODUCT,
        "archiveSets": ARCHIVE_SET,
        "temporalRanges": f"{int(year):04d}-001..{int(year):04d}-001",
        "regions": f"[BBOX]W{left:g} N{top:g} E{right:g} S{bottom:g}",
        "formats": "json",
    }
    return f"{BASE}/api/v2/content/details?{urllib.parse.urlencode(params)}"


def _walk_strings(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_strings(child)
    elif isinstance(value, str):
        yield value


def extract_filenames(payload):
    """Extract VNP46A4 HDF5 filenames without depending on one API JSON shape."""
    found = set()
    for value in _walk_strings(payload):
        name = value.rsplit("/", 1)[-1]
        if FILENAME_RE.fullmatch(name):
            found.add(name)
    return sorted(found)


def authenticated_opener():
    """Preserve LAADS/Earthdata cookies across EDL authentication redirects."""
    cookie_jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))


def discover_files(year, bbox, token, opener=None):
    opener = opener or authenticated_opener()
    request = urllib.request.Request(search_url(year, bbox), headers=authorization_headers(token))
    with opener.open(request, timeout=60) as response:
        payload = json.load(response)
    files = extract_filenames(payload)
    if not files:
        raise RuntimeError("LAADS search returned no VNP46A4 HDF5 files for bbox/year")
    return files


def archive_path(filename):
    match = FILENAME_RE.fullmatch(filename)
    if not match:
        raise ValueError("unexpected VNP46A4 filename")
    return (
        f"allData/{ARCHIVE_SET}/{PRODUCT}/"
        f"{match.group('year')}/{match.group('doy')}/{urllib.parse.quote(filename)}"
    )


def archive_url(filename):
    """Use the documented API-V2 archive download endpoint."""
    return f"{BASE}/api/v2/content/archives/{archive_path(filename)}"


def download_file(filename, token, destination, opener=None):
    """Download using NASA's documented curl EDL-token flow.

    curl -L follows Earthdata redirects and -b persists the LAADS/EDL session
    cookies required by the official scripted-download guidance.
    """
    authorization_headers(token)  # fail closed before spawning curl
    url = archive_url(filename)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    cookie_file = destination.parent / ".earthdata-session"
    subprocess.run(
        [
            "curl",
            "--fail",
            "--show-error",
            "--location",
            "--cookie",
            str(cookie_file),
            "--cookie-jar",
            str(cookie_file),
            "--header",
            f"Authorization: Bearer {token}",
            "--header",
            "X-Requested-With: XMLHttpRequest",
            "--output",
            str(destination),
            url,
        ],
        check=True,
    )
    with destination.open("rb") as stream:
        signature = stream.read(len(HDF5_MAGIC))
    if signature != HDF5_MAGIC:
        preview = destination.read_bytes()[:160].decode("utf-8", errors="replace").replace("\n", " ")
        destination.unlink(missing_ok=True)
        raise RuntimeError(
            "LAADS download did not return an HDF5 payload; "
            f"first bytes={signature!r}, preview={preview!r}"
        )
    return destination


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--bbox", default="119.5,21.5,122.5,25.5")
    parser.add_argument("--token-env", default="EARTHDATA_TOKEN")
    parser.add_argument("--output-dir", default=".cache/viirs")
    parser.add_argument("--list-only", action="store_true")
    args = parser.parse_args()
    bbox = tuple(float(v) for v in args.bbox.split(","))
    if len(bbox) != 4:
        raise SystemExit("--bbox requires left,bottom,right,top")
    token = os.environ.get(args.token_env)
    opener = authenticated_opener()
    files = discover_files(args.year, bbox, token, opener=opener)
    print(json.dumps({"year": args.year, "files": files}, indent=2))
    if args.list_only:
        return
    for filename in files:
        path = download_file(filename, token, Path(args.output_dir) / filename, opener=opener)
        print(path)


if __name__ == "__main__":
    main()
