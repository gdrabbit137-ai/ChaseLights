#!/usr/bin/env python3
"""Hydrate an R2 prefix into the working tree.

The heavy weather artefacts live in Cloudflare R2 and are no longer committed to
git (see ops/pages/r2-plan.md). CI and local dev still need them on disk because
the browser tests fetch ``./weather_details/<region>/<spot>.json`` from the same
origin as the page. This pulls exactly one prefix back down.

    python ops/pages/r2_pull.py --prefix weather_details/ --dest .

Credentials come from the same environment variables as r2_sync.py:
R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY / R2_BUCKET / R2_ENDPOINT.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def client():
    try:
        import boto3
        from botocore.config import Config
    except ImportError:  # pragma: no cover - operator feedback
        sys.exit("boto3 is required: python -m pip install boto3")

    missing = [k for k in ("R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_ENDPOINT") if not os.environ.get(k)]
    if missing:
        sys.exit("missing environment: " + ", ".join(missing))

    return boto3.client(
        "s3",
        endpoint_url=os.environ["R2_ENDPOINT"],
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
        config=Config(signature_version="s3v4", max_pool_connections=64, retries={"max_attempts": 5}),
    )


def list_keys(s3, bucket: str, prefix: str) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    token = None
    while True:
        kwargs = {"Bucket": bucket, "Prefix": prefix, "MaxKeys": 1000}
        if token:
            kwargs["ContinuationToken"] = token
        page = s3.list_objects_v2(**kwargs)
        for obj in page.get("Contents", []):
            out.append((obj["Key"], int(obj["Size"])))
        token = page.get("NextContinuationToken")
        if not page.get("IsTruncated"):
            return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", required=True, help="key prefix, e.g. weather_details/")
    ap.add_argument("--dest", default=".", help="destination root (keys are appended verbatim)")
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--force", action="store_true", help="re-download files that already exist")
    args = ap.parse_args()

    # A prefix ending in a filename is a request for exactly that key: appending
    # "/" turned weathergrid/gfs_tw_weather_browser.json into a directory prefix
    # that matches nothing.
    prefix = args.prefix
    if not prefix.endswith("/") and "." not in prefix.rsplit("/", 1)[-1]:
        prefix += "/"
    bucket = os.environ.get("R2_BUCKET", "chaselights-data")
    s3 = client()

    keys = list_keys(s3, bucket, prefix)
    if not keys:
        print(f"no objects under {prefix} in {bucket}", file=sys.stderr)
        return 1

    dest_root = Path(args.dest)
    todo: list[tuple[str, int]] = []
    for key, size in keys:
        target = dest_root / key
        if not args.force and target.exists() and target.stat().st_size == size:
            continue
        todo.append((key, size))

    total_mib = sum(s for _, s in todo) / 1048576
    print(f"{len(keys)} objects under {prefix}; {len(todo)} to fetch ({total_mib:.1f} MiB)")

    started = time.time()
    fetched = 0
    failed: list[str] = []

    def download(key: str, size: int) -> None:
        target = dest_root / key
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".part")
        s3.download_file(bucket, key, str(tmp))
        if tmp.stat().st_size != size:
            tmp.unlink(missing_ok=True)
            raise RuntimeError(f"size mismatch for {key}")
        tmp.replace(target)

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(download, k, s): k for k, s in todo}
        for fut in as_completed(futures):
            key = futures[fut]
            try:
                fut.result()
                fetched += 1
            except Exception as exc:  # noqa: BLE001 - report and keep going
                failed.append(f"{key}: {exc}")
            if fetched % 100 == 0 and fetched:
                print(f"  ...{fetched}/{len(todo)}", flush=True)

    dt = time.time() - started
    print(f"fetched={fetched} failed={len(failed)} in {dt:.1f}s")
    for line in failed[:5]:
        print("  FAIL " + line, file=sys.stderr)
    return 0 if not failed else 2


if __name__ == "__main__":
    sys.exit(main())
