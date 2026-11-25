#!/usr/bin/env python3
"""Upload the heavy data plane (weathergrid/ + weather_details/) to Cloudflare R2.

The site keeps HTML/JS/CSS on Cloudflare Pages and reads the big JSON from R2.
This script is the only writer: it mirrors the repo layout into the bucket so
the front end just needs a base-URL prefix.

Usage:
    python ops/pages/r2_sync.py --dry-run          # what would go where (no creds needed)
    python ops/pages/r2_sync.py --apply            # upload (needs S3 creds)
    python ops/pages/r2_sync.py --apply --only weather_details
    python ops/pages/r2_sync.py --apply --prune    # delete bucket keys with no local file

Credentials (S3 API, NOT the Cloudflare API token):
    R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY  — created in the R2 dashboard
    R2_ENDPOINT   default https://<account_id>.r2.cloudflarestorage.com
    R2_BUCKET     default chaselights-data

Cache-Control (matches ops/pages/_headers):
    */manifest.json                      public, max-age=60
    weathergrid/v2/*, weathergrid/png/*  public, max-age=31536000, immutable
    weathergrid/*                        public, max-age=600
    weather_details/*                    public, max-age=300, stale-while-revalidate=60
"""
from __future__ import annotations

import argparse
import mimetypes
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREFIXES = ("weathergrid", "weather_details")
DEFAULT_BUCKET = "chaselights-data"
DEFAULT_ACCOUNT = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "218303e56b40f3bc72f70bcc975fda64")

CACHE_IMMUTABLE = "public, max-age=31536000, immutable"
CACHE_MANIFEST = "public, max-age=60"
CACHE_GRID = "public, max-age=600"
CACHE_DETAILS = "public, max-age=300, stale-while-revalidate=60"


def cache_control(key: str) -> str:
    if key.endswith("/manifest.json") or key == "manifest.json":
        return CACHE_MANIFEST
    if key.startswith("weathergrid/v2/") or key.startswith("weathergrid/png/"):
        return CACHE_IMMUTABLE
    if key.startswith("weather_details/"):
        return CACHE_DETAILS
    if key.startswith("weathergrid/"):
        return CACHE_GRID
    return CACHE_DETAILS


def content_type(key: str) -> str:
    guess, _ = mimetypes.guess_type(key)
    if guess:
        return guess
    if key.endswith(".json"):
        return "application/json"
    return "application/octet-stream"


def iter_files(only: tuple[str, ...] = PREFIXES):
    """Tracked files only, resolved against the git index (never the working
    tree): generated leftovers must not reach the bucket."""
    import subprocess

    for prefix in only:
        r = subprocess.run(["git", "-C", REPO, "ls-files", "-z", "--", prefix],
                           capture_output=True)
        if r.returncode != 0:
            raise SystemExit(f"git ls-files failed for {prefix}")
        for raw in r.stdout.split(b"\0"):
            if not raw:
                continue
            rel = raw.decode("utf-8")
            path = os.path.join(REPO, rel)
            if not os.path.isfile(path):
                # tracked but not checked out (sparse) — skip, do not lie
                continue
            yield rel, path


def plan(only: tuple[str, ...]):
    rows = []
    for rel, path in iter_files(only):
        rows.append({
            "key": rel,
            "path": path,
            "size": os.path.getsize(path),
            "content_type": content_type(rel),
            "cache_control": cache_control(rel),
        })
    return rows


def client(endpoint: str, bucket: str):
    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        raise SystemExit("boto3 is required for --apply (pip install boto3)")
    ak = os.environ.get("R2_ACCESS_KEY_ID")
    sk = os.environ.get("R2_SECRET_ACCESS_KEY")
    if not ak or not sk:
        raise SystemExit("R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY are not set "
                         "(create an R2 S3 API token in the dashboard)")
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=ak,
        aws_secret_access_key=sk,
        region_name="auto",
        config=Config(signature_version="s3v4", max_pool_connections=16),
    )


def upload(s3, bucket: str, rows, workers: int = 8):
    done = failed = 0
    total = len(rows)

    def one(row):
        with open(row["path"], "rb") as fh:
            s3.put_object(
                Bucket=bucket,
                Key=row["key"],
                Body=fh,
                ContentType=row["content_type"],
                CacheControl=row["cache_control"],
            )

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(one, r): r for r in rows}
        for fut in as_completed(futures):
            row = futures[fut]
            try:
                fut.result()
                done += 1
            except Exception as exc:  # noqa: BLE001 - report, keep going
                failed += 1
                print(f"  FAIL {row['key']}: {exc}", file=sys.stderr)
            if (done + failed) % 100 == 0:
                print(f"  {done + failed}/{total} ...", flush=True)
    return done, failed


def prune(s3, bucket: str, rows):
    keep = {r["key"] for r in rows}
    removed = 0
    token = None
    while True:
        kwargs = {"Bucket": bucket, "MaxKeys": 1000}
        if token:
            kwargs["ContinuationToken"] = token
        page = s3.list_objects_v2(**kwargs)
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key not in keep:
                s3.delete_object(Bucket=bucket, Key=key)
                removed += 1
        if not page.get("IsTruncated"):
            break
        token = page.get("NextContinuationToken")
    return removed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="actually upload")
    ap.add_argument("--dry-run", action="store_true", help="list only (default)")
    ap.add_argument("--prune", action="store_true", help="delete bucket keys with no local file")
    ap.add_argument("--only", choices=PREFIXES, action="append", default=None)
    ap.add_argument("--files-from", default=None,
                    help="newline-separated repo-relative paths to sync (default: all tracked)")
    ap.add_argument("--bucket", default=os.environ.get("R2_BUCKET", DEFAULT_BUCKET))
    ap.add_argument("--endpoint", default=os.environ.get(
        "R2_ENDPOINT", f"https://{DEFAULT_ACCOUNT}.r2.cloudflarestorage.com"))
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--show", type=int, default=5, help="sample rows in dry-run")
    args = ap.parse_args()

    only = tuple(args.only) if args.only else PREFIXES
    if args.files_from:
        wanted = [ln.strip() for ln in open(args.files_from, encoding="utf-8") if ln.strip()]
        # CL-PAGES-05: hard isolation. Each writer repo owns one prefix; a path
        # outside the --only scope is a configuration bug, not something to skip
        # quietly (a silent drop would leave stale objects in the other tree).
        outside = [w for w in wanted if not w.startswith(only)]
        if outside:
            raise SystemExit(
                f"refusing {len(outside)} path(s) outside --only scope {only}: "
                + ", ".join(outside[:3])
            )
        wanted = [w for w in wanted if w.startswith(only)]
        present = {rel: path for rel, path in iter_files(only)}
        rows = [{"key": w, "path": present[w], "size": os.path.getsize(present[w]),
                 "content_type": content_type(w), "cache_control": cache_control(w)}
                for w in wanted if w in present]
    else:
        rows = plan(only)
    total_bytes = sum(r["size"] for r in rows)

    by_cache: dict[str, int] = {}
    for r in rows:
        by_cache[r["cache_control"]] = by_cache.get(r["cache_control"], 0) + 1

    print(f"bucket={args.bucket} endpoint={args.endpoint}")
    print(f"files={len(rows)} size={total_bytes / 1048576:.1f} MiB")
    for cc, n in sorted(by_cache.items(), key=lambda kv: -kv[1]):
        print(f"  {n:5d}  {cc}")
    for r in rows[: args.show]:
        print(f"  -> {r['key']}  {r['size'] / 1024:.0f} KiB  {r['content_type']}  {r['cache_control']}")

    if not args.apply:
        print("dry-run: nothing uploaded (pass --apply with R2 credentials)")
        return 0

    s3 = client(args.endpoint, args.bucket)
    done, failed = upload(s3, args.bucket, rows, workers=args.workers)
    print(f"uploaded={done} failed={failed}")
    if args.prune:
        print(f"pruned={prune(s3, args.bucket, rows)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
