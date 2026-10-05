import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
APP = (ROOT / "assets" / "app.js").read_text(encoding="utf-8")
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
SUPPORTED_LOCALES = ("zh-TW", "en", "ja")


class LocalizationCompletenessStaticTests(unittest.TestCase):
    def test_runtime_translation_assets_cover_every_supported_locale(self):
        for region in ("tw", "jp", "us"):
            payload = json.loads((ROOT / f"{region}_weather.json").read_text(encoding="utf-8"))
            translations = payload.get("translations") or {}
            for section in ("messages", "factors"):
                entries = translations.get(section) or {}
                self.assertTrue(entries, f"{region}: missing translations.{section}")
                for key, values in entries.items():
                    self.assertIsInstance(values, dict, f"{region}:{section}.{key} must be a locale map")
                    for locale in SUPPORTED_LOCALES:
                        value = values.get(locale)
                        self.assertIsInstance(value, str, f"{region}:{section}.{key} missing {locale}")
                        self.assertTrue(value.strip(), f"{region}:{section}.{key} empty {locale}")

    def test_main_ui_semantic_copy_never_falls_back_to_another_locale(self):
        forbidden = (
            "t?.[currentLang]||t?.['zh-TW']",
            "notes[currentLang]||notes['zh-TW']",
            "spot.access_note_i18n?.[currentLang]||spot.access_note_i18n?.['zh-TW']",
            "metric.opportunity_name||themeLabel",
            "op.name_zh||themeLabel",
            "f.text||f.key",
            'aria-label="Favorite"',
            ">HIST<",
        )
        for fragment in forbidden:
            self.assertNotIn(fragment, APP)

        self.assertIn("const localeText=values=>", APP)
        self.assertIn("return localeText(t)||d().status_unavailable;", APP)
        self.assertIn("return currentLang==='zh-TW'?userFacingResearchValue(owner?.[key]):'';", APP)
        self.assertIn("return themeLabel(op?.legacy_theme||theme||'mountain_view');", APP)

    def test_place_name_is_the_only_explicit_local_name_fallback(self):
        self.assertIn(
            "const spotName=s=>s?.name_i18n?.[currentLang]||s?.name_local||",
            APP,
        )
        self.assertIn("spot.name_local!==spotName(spot)", APP)

    def test_document_and_accessibility_chrome_are_localized(self):
        for key in (
            "page_title",
            "country_aria",
            "temp_unit_aria",
            "weathergrid_title",
            "weathergrid_v2_title",
            "field_intake_title",
            "close_place",
            "close_weather",
        ):
            self.assertIn(key, APP)

        self.assertIn("document.documentElement.lang=currentLang;", APP)
        self.assertIn("document.title=d().page_title;", APP)
        self.assertIn("[data-i18n-title]", APP)
        self.assertIn("[data-i18n-aria-label]", APP)
        self.assertIn('data-i18n-aria-label="country_aria"', INDEX)
        self.assertIn('data-i18n-aria-label="temp_unit_aria"', INDEX)
        self.assertIn('data-i18n-title="weathergrid_title"', INDEX)
        self.assertIn('href="./weather-map-v2.html"', INDEX)
        self.assertIn('data-i18n-title="weathergrid_v2_title"', INDEX)
        self.assertIn('>🧪 WeatherGrid V2</a>', INDEX)
        self.assertIn('data-i18n-title="field_intake_title"', INDEX)

    def test_open_dynamic_surfaces_are_rerendered_on_language_switch(self):
        self.assertIn(
            "if(activePlaceSpot&&document.getElementById('place-modal-overlay').style.display==='flex')openPlaceModal(activePlaceSpot,activePlaceSummary);",
            APP,
        )
        self.assertIn(
            "if(activeModalSpot&&document.getElementById('modal-overlay').style.display==='flex')renderWeatherModal(activeModalSpot,activeModalSummary);",
            APP,
        )


if __name__ == "__main__":
    unittest.main()
