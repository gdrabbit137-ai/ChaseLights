#!/usr/bin/env python3
"""Contract tests for ops/pages/build_dist.sh (Cloudflare Pages whitelist publish).

Run:  python ops/pages/test_build_dist.py
      (no third-party deps; works on Windows git-bash and the Linux runner)

What it pins:
  1. the whitelist manifest carries every file the static site fetches at runtime
  2. the manifest never carries an engineering path (workers/, packages/, ops/,
     specs/, .github/, AGENTS.md, SKILL.md, data/v2/staging/ ...)
  3. a real --light build produces those files on disk and still no leaks
  4. the per-file ceiling aborts (exit 3) instead of shipping a >25 MiB file
  5. the file-count ceiling aborts (exit 4) instead of shipping a >20k-file dist
  6. no emitted file sits at the Cloudflare 25 MiB ceiling
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SCRIPT = os.path.join("ops", "pages", "build_dist.sh")

# Files the published site actually reads (grep-verified fetch targets in
# assets/*.js + the shell documents' script tags).
REQUIRED = [
    "index.html",
    "404.html",
    "reminders.html",
    "weather-map.html",
    "genre-eval.html",
    "field-intake.html",
    "sources.html",
    "assets/app.js",
    "assets/reminders-page.js",
    "assets/weather-map.js",
    "locales",
    "data/v2/copy/fail_reason_overrides.json",
    "data/v2/copy/live_cam.json",
    "apps/web-v2/evaluations-latest.json",
    "apps/web-v2/catalog.v2.json",
    "apps/web-v2/browse-index.v2.json",
    "apps/web-v2/opportunity-contracts.json",
    "apps/web-v2/evaluations-details",
    "_headers",
]

FORBIDDEN = [
    "workers",
    "packages",
    "ops",
    "specs",
    ".github",
    ".ci",
    "AGENTS.md",
    "SKILL.md",
    "README.md",
    "data/v2/staging",
]

MAX_BYTES = 25 * 1024 * 1024


def bash() -> str:
    exe = shutil.which("bash")
    if not exe:
        raise SystemExit("bash not found on PATH")
    return exe


def run(args, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(
        [bash(), SCRIPT, *args],
        cwd=REPO, capture_output=True, text=True, env=e,
    )


def manifest() -> list[str]:
    r = run(["--dry-run"])
    assert r.returncode == 0, f"--dry-run failed ({r.returncode}): {r.stderr}"
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


def has(entries: list[str], want: str) -> bool:
    """True when the manifest carries `want` — either the file itself or a
    directory entry that contains it."""
    for e in entries:
        base = e.rstrip("/")
        if base == want or want.startswith(base + "/") or base.startswith(want + "/"):
            return True
    return False


RESULTS: list[tuple[bool, str, str]] = []


def test_script_is_lf_only():
    """The build runs on Linux: a CRLF shebang line makes bash die with
    `set: pipefail\\r: invalid option name` (measured on the first Cloudflare
    Pages build)."""
    for rel in ("ops/pages/build_dist.sh", "ops/pages/_headers"):
        raw = open(os.path.join(REPO, rel), "rb").read()
        assert b"\r" not in raw, f"{rel} must be LF-only (found CR)"


def check(name: str, fn):
    tmp = None
    try:
        fn()
        RESULTS.append((True, name, ""))
    except AssertionError as exc:
        RESULTS.append((False, name, str(exc)))
    finally:
        if tmp and os.path.isdir(tmp):
            shutil.rmtree(tmp, ignore_errors=True)


def git_index_has(rel: str) -> bool:
    """True when anything at or under `rel` is tracked, regardless of whether it
    is present in the worktree (a sparse checkout can hide it)."""
    r = subprocess.run(["git", "-C", REPO, "ls-files", "--", rel],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def test_manifest_has_runtime_surface():
    entries = manifest()
    missing = [w for w in REQUIRED if not has(entries, w)]
    # Distinguish "not whitelisted" from "whitelisted but hidden by a partial
    # checkout" — CI uses sparse-checkout and that is how 404.html slipped out
    # of the dist while the manifest silently looked fine.
    hidden = [w for w in missing if git_index_has(w.rstrip("/"))]
    assert not hidden, f"tracked but not checked out (sparse-checkout?): {hidden}"
    assert not missing, f"manifest is missing {missing}"


def test_full_mode_carries_the_data_plane():
    r = run(["--full", "--dry-run"])
    assert r.returncode == 0, r.stderr
    entries = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
    for want in ("weathergrid", "weather_details"):
        assert has(entries, want), f"--full manifest is missing {want}"


def test_manifest_has_no_engineering_paths():
    entries = manifest()
    leaks = [f for f in FORBIDDEN if has(entries, f)]
    assert not leaks, f"manifest leaks {leaks}"


def test_light_build_on_disk():
    out = tempfile.mkdtemp(prefix="cl-dist-")
    try:
        r = run(["--light", "--out", out])
        assert r.returncode == 0, f"build failed ({r.returncode}): {r.stderr}"
        assert "build_dist: OK" in r.stdout, r.stdout
        for rel in ["index.html", "reminders.html", "_headers",
                    os.path.join("assets", "app.js"),
                    os.path.join("assets", "reminders-page.js"),
                    os.path.join("data", "v2", "copy", "live_cam.json"),
                    os.path.join("apps", "web-v2", "evaluations-latest.json")]:
            assert os.path.isfile(os.path.join(out, rel)), f"missing {rel}"
        assert os.path.isdir(os.path.join(out, "apps", "web-v2", "evaluations-details"))
        for rel in FORBIDDEN + [".manifest.tmp"]:
            assert not os.path.exists(os.path.join(out, rel)), f"leaked {rel}"
        # 404 is served at any depth, so its asset URLs must be absolute.
        nf = os.path.join(out, "404.html")
        assert os.path.isfile(nf), "404.html missing from dist"
        html = open(nf, encoding="utf-8").read()
        assert 'href="/assets/app.css' in html, "404.html must use /assets/ (absolute), never ./assets/"
        # --light must not drag the heavy data dirs along
        for rel in ("weathergrid", "weather_details"):
            assert not os.path.exists(os.path.join(out, rel)), f"--light emitted {rel}"
        # nothing at the Cloudflare per-file ceiling
        for root, _dirs, files in os.walk(out):
            for fn in files:
                p = os.path.join(root, fn)
                size = os.path.getsize(p)
                assert size < MAX_BYTES, f"{os.path.relpath(p, out)} is {size} bytes"
    finally:
        shutil.rmtree(out, ignore_errors=True)


def test_per_file_ceiling_aborts():
    out = tempfile.mkdtemp(prefix="cl-dist-")
    try:
        r = run(["--light", "--out", out], env={"DIST_MAX_BYTES": "1000"})
        assert r.returncode == 3, f"expected exit 3, got {r.returncode}: {r.stdout} {r.stderr}"
        assert "25 MiB" in r.stderr or "ceiling" in r.stderr, r.stderr
    finally:
        shutil.rmtree(out, ignore_errors=True)


def test_file_count_ceiling_aborts():
    out = tempfile.mkdtemp(prefix="cl-dist-")
    try:
        r = run(["--light", "--out", out], env={"DIST_MAX_FILES": "5"})
        assert r.returncode == 4, f"expected exit 4, got {r.returncode}: {r.stdout} {r.stderr}"
    finally:
        shutil.rmtree(out, ignore_errors=True)


def main() -> int:
    check("script and headers are LF-only", test_script_is_lf_only)
    check("manifest carries the runtime surface", test_manifest_has_runtime_surface)
    check("--full manifest carries the data plane", test_full_mode_carries_the_data_plane)
    check("manifest carries no engineering paths", test_manifest_has_no_engineering_paths)
    check("--light build lands on disk without leaks", test_light_build_on_disk)
    check("per-file ceiling aborts with exit 3", test_per_file_ceiling_aborts)
    check("file-count ceiling aborts with exit 4", test_file_count_ceiling_aborts)
    failed = 0
    for i, (ok, name, err) in enumerate(RESULTS, 1):
        if ok:
            print(f"ok {i} - {name}")
        else:
            failed += 1
            print(f"not ok {i} - {name}\n  {err}")
    print(f"# pass {len(RESULTS) - failed}")
    print(f"# fail {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
