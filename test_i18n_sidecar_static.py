"""CL-I18N-01 static checks for the locale sidecar and translation pipeline.

Pure static verification: no weather evaluation, no recompute, no network.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOCALES = ["zh-TW", "en", "ja"]
FILES = ["ui.json", "taxonomy.json", "catalog.json"]


def test_locale_files_exist_and_parse():
    for lang in LOCALES:
        for name in FILES:
            p = ROOT / "locales" / lang / name
            assert p.exists(), f"missing {p}"
            json.loads(p.read_text(encoding="utf-8"))


def test_key_parity_across_locales():
    def keys(node, prefix=""):
        if isinstance(node, dict):
            for k, v in node.items():
                yield from keys(v, f"{prefix}/{k}")
        else:
            yield prefix

    for name in FILES:
        base = set(keys(json.loads((ROOT / "locales/zh-TW" / name).read_text(encoding="utf-8"))))
        for lang in LOCALES[1:]:
            other = set(keys(json.loads((ROOT / "locales" / lang / name).read_text(encoding="utf-8"))))
            assert base == other, f"{lang}/{name} key mismatch ({len(base ^ other)} keys)"


def test_qa_script_passes():
    out = subprocess.run([sys.executable, str(ROOT / "scripts/i18n_check.py")],
                         capture_output=True, text=True, cwd=str(ROOT))
    assert out.returncode == 0, out.stdout + out.stderr


def test_glossary_and_lock_present():
    g = json.loads((ROOT / "i18n/glossary.json").read_text(encoding="utf-8"))
    assert "霞池" in g["terms"]
    lock = json.loads((ROOT / "i18n/i18n_lock.json").read_text(encoding="utf-8"))
    assert "entries" in lock


def test_workflow_is_isolated_from_weather_pipeline():
    text = (ROOT / ".github/workflows/i18n-sync.yml").read_text(encoding="utf-8")
    for forbidden in ("update_weather", "evaluate_batch", "repin_canonical", "opportunity-evaluations"):
        assert forbidden not in text, f"i18n workflow must not invoke {forbidden}"
    for required in ("i18n_extract.py", "i18n_sync.py", "i18n_check.py"):
        assert required in text, f"workflow missing {required}"


def test_loader_fallback_merges_en():
    script = """
    import {loadLocaleSidecar} from './apps/web-v2/locale-loader.mjs';
    const files = {
      'en/ui.json': {a:'EN', b:'EN-B'},
      'en/taxonomy.json': {t:'EN-T'},
      'en/catalog.json': {c:'EN-C'},
      'ja/ui.json': {a:'JA'},
      'ja/taxonomy.json': {t:'JA-T'},
      'ja/catalog.json': {c:'JA-C'},
    };
    const fetchImpl = async (url) => {
      const key = url.split('/locales/')[1];
      const body = files[key];
      if (!body) return {ok:false, status:404, json:async()=>({})};
      return {ok:true, status:200, json:async()=>body};
    };
    const sc = await loadLocaleSidecar('ja', {fetchImpl, base:'./locales/'});
    console.log(JSON.stringify({ui:sc.ui, tax:sc.taxonomy, cat:sc.catalog}));
    """
    out = subprocess.run(["node", "--input-type=module", "-e", script],
                         capture_output=True, text=True, cwd=str(ROOT))
    assert out.returncode == 0, out.stderr
    data = json.loads(out.stdout.strip().splitlines()[-1])
    assert data["ui"]["a"] == "JA"
    assert data["ui"]["b"] == "EN-B", "missing key must fall back to en"
    assert data["tax"]["t"] == "JA-T"
    assert data["cat"]["c"] == "JA-C"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("PASS", name)
