#!/usr/bin/env python3
"""ChaseLights V2 integration/legacy-isolation gate. No deployment or legacy edits."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

V2_PATH = "/apps/web-v2/"
PUBLIC_URL = "https://chaselights.app/apps/web-v2/"
REQUIRED_LEGACY = ("index.html", "CNAME", "RESEARCH_EVIDENCE_SPEC_R4_2.md", "NAVIGATION_SPEC_R4_2.md")


class PageRefs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = []
        self.links = []
        self.title_count = 0

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "title":
            self.title_count += 1
        if tag == "a" and data.get("href"):
            self.links.append(data)
        if tag in ("script", "img") and data.get("src"):
            self.assets.append(data["src"])
        if tag == "link" and "stylesheet" in data.get("rel", "").split() and data.get("href"):
            self.assets.append(data["href"])


def v2_link(anchor):
    path = urlparse(anchor.get("href", "")).path
    return path in ("apps/web-v2/", "./apps/web-v2/", "/apps/web-v2/")


def check_v2_assets(html, exists):
    parsed = PageRefs()
    parsed.feed(html)
    errors = []
    if not parsed.title_count:
        errors.append("V2 index has no HTML title")
    for ref in parsed.assets:
        u = urlparse(ref)
        if u.scheme or ref.startswith("//"):
            errors.append("V2 asset must be self-contained: " + ref)
            continue
        path = u.path
        if path.startswith("/") and not path.startswith(V2_PATH):
            errors.append("V2 asset escapes isolated path: " + ref)
        elif ".." in Path(path).parts:
            errors.append("V2 asset uses parent traversal: " + ref)
        elif not exists(path):
            errors.append("V2 asset missing: " + ref)
    return errors


def check_local(root):
    root = root.resolve()
    errors = ["Missing legacy file: " + p for p in REQUIRED_LEGACY if not (root / p).is_file()]
    legacy = root / "index.html"
    if not legacy.is_file():
        return errors, "legacy_missing", False
    parsed = PageRefs()
    parsed.feed(legacy.read_text(encoding="utf-8"))
    links = [a for a in parsed.links if v2_link(a)]
    v2_dir = root / "apps/web-v2"
    components = ("apps/web-v2", "data/v2", "packages/core-v2", "packages/models-v2")
    has_components = any((root / p).exists() for p in components)
    if has_components and not (root / "specs/v2/schema/opportunity-v2.1.schema.json").is_file():
        errors.append("V2 components require canonical specs/v2/schema/opportunity-v2.1.schema.json")
    if links and not (v2_dir / "index.html").is_file():
        errors.append("Legacy V2 link is forbidden until V2 page exists")
    if links:
        if len(links) != 1:
            errors.append("Legacy must expose exactly one V2 entry")
        if any(a.get("data-i18n") != "v2_link" for a in links):
            errors.append("Legacy V2 entry requires data-i18n=v2_link")
        app = root / "assets/app.js"
        if not app.is_file() or app.read_text(encoding="utf-8").count("v2_link:") < 3:
            errors.append("Legacy V2 entry lacks verified three-locale translation keys")
    if v2_dir.exists():
        page = v2_dir / "index.html"
        if not page.is_file():
            errors.append("V2 directory has no index.html")
        else:
            def exists(ref):
                p = (root / ref.lstrip("/")) if ref.startswith(V2_PATH) else (v2_dir / ref)
                p = p.resolve()
                return p.is_relative_to(v2_dir.resolve()) and p.is_file()
            errors.extend(check_v2_assets(page.read_text(encoding="utf-8"), exists))
    return errors, ("v2_present" if v2_dir.exists() else "v2_pending"), bool(links)


def check_public(url=PUBLIC_URL):
    u = urlparse(url)
    if (u.scheme, u.hostname, u.path.rstrip("/")) != ("https", "chaselights.app", "/apps/web-v2"):
        return ["Public smoke URL is not the canonical V2 path"]
    def get(target):
        with urlopen(Request(target, headers={"User-Agent": "ChaseLights-V2-Gate/1", "Cache-Control": "no-cache"}), timeout=20) as response:
            return response.status, response.headers.get_content_type(), response.read(3_000_000)
    try:
        status, mime, body = get(url)
        if status != 200 or mime != "text/html":
            return ["V2 public page HTTP/MIME mismatch: %s %s" % (status, mime)]
        html = body.decode("utf-8")
        if "ChaseLights" not in html:
            return ["Public page does not identify ChaseLights"]
        def exists(ref):
            target = urljoin(url, ref)
            parsed = urlparse(target)
            if parsed.hostname != "chaselights.app" or not parsed.path.startswith(V2_PATH):
                return False
            try:
                status, _, payload = get(target)
                return status == 200 and bool(payload)
            except Exception:
                return False
        return check_v2_assets(html, exists)
    except Exception as exc:
        return ["V2 public HTTP unavailable: %s: %s" % (type(exc).__name__, exc)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--public", action="store_true", help="Require real public HTTP and assets")
    args = parser.parse_args()
    errors, state, legacy_link = check_local(args.root)
    print("Local V2 integration state:", state)
    if legacy_link or args.public:
        errors.extend(check_public())
        print("Public HTTP smoke enforced:", "legacy link" if legacy_link else "explicit request")
    for error in errors:
        print("ERROR:", error)
    if errors:
        raise SystemExit(1)
    print("PASS: isolation contract; V2 pending is NOT deployment approval" if state == "v2_pending" else "PASS: local V2 integration contract")


if __name__ == "__main__":
    main()
