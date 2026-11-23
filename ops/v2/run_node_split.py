#!/usr/bin/env python3
"""CL-CI-39: run the W4 node suite in two passes.

The CDP/Chromium test files each spawn their own headless browser. Node's test
runner executes files concurrently by default, so on a 2-core CI runner four
Chrome instances race for the same CPU and the slowest ones blow their 120s
per-test timeout (CL-UI-118b 5a/5b timed out in CI while passing standalone and
even with WebGL disabled).

So: unit files keep full parallelism, browser/CDP files run one at a time.
Both passes emit TAP; this wrapper strips their individual summaries and prints
exactly one merged `# tests / # pass / # fail / # skipped` block, because the
postmerge gate requires the counts to appear exactly once.

Classification is content-based, not a hard-coded list, so a new browser test
joins the serial pass automatically.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys

BROWSER_MARKERS = (
    "CHROMIUM_EXECUTABLE",
    "--remote-debugging-port",
    "playwright",
    "spawn(BROWSER",
)

SUMMARY_KEYS = ("tests", "suites", "pass", "fail", "cancelled", "skipped", "todo", "duration_ms")
SUMMARY_RE = re.compile(r"^#\s+(tests|suites|pass|fail|cancelled|skipped|todo|duration_ms)\s+(\d+)\s*$")


def classify(paths):
    browser, unit = [], []
    for path in paths:
        try:
            body = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            unit.append(path)
            continue
        (browser if any(m in body for m in BROWSER_MARKERS) else unit).append(path)
    return unit, browser


def run(node, files, extra):
    if not files:
        return 0, ""
    cmd = [node, "--test", "--test-isolation=none", "--test-timeout=120000",
           "--test-reporter=tap", *extra, *files]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout


def strip_and_count(stdout):
    counts = {k: 0 for k in SUMMARY_KEYS}
    kept = []
    for line in stdout.splitlines():
        match = SUMMARY_RE.match(line.strip())
        if match:
            counts[match.group(1)] += int(match.group(2))
            continue
        kept.append(line)
    return counts, kept


def main(argv):
    files = argv[1:]
    unit, browser = classify(files)
    # NODE_BIN lets a local Windows checkout point at the pinned node 26
    # build; CI uses the setup-node one on PATH.
    node = os.environ.get("NODE_BIN") or shutil.which("node") or "node"
    rc_unit, out_unit = run(node, unit, [])
    rc_browser, out_browser = run(node, browser, ["--test-concurrency=1"])

    total = {k: 0 for k in SUMMARY_KEYS}
    for out in (out_unit, out_browser):
        counts, kept = strip_and_count(out)
        for key, value in counts.items():
            total[key] += value
        print("\n".join(kept))
    # One merged summary, emitted exactly once for the gate.
    for key in ("tests", "suites", "pass", "fail", "cancelled", "skipped", "todo"):
        print(f"# {key} {total[key]}")
    return 0 if (rc_unit == 0 and rc_browser == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
