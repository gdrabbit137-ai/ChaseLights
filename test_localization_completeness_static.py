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

    def test_weather_timeline_copy_uses_photographer_language_in_all_locales(self):
        for obsolete in (
            "[模型資料]",
            "[氣象預報]",
            "[model data]",
            "[forecast]",
            "[モデル]",
            "[予報]",
            "預測最佳出景窗口",
        ):
            self.assertNotIn(obsolete, APP)
            self.assertNotIn(obsolete, INDEX)

        for expected in (
            "逐時拍攝條件：過去 24 小時 + 未來 72 小時",
            "Hourly shooting conditions: past 24 hours + next 72 hours",
            "時間別の撮影条件：過去24時間＋未来72時間",
        ):
            self.assertIn(expected, APP)
        self.assertIn("所選日期中相對較佳的時段", APP)
        self.assertIn("a relatively better time on the selected date", APP)
        self.assertIn("選択日の中で相対的に条件が良い時間帯", APP)
        self.assertIn("逐時拍攝條件：過去 24 小時 + 未來 72 小時", INDEX)

    def test_no_recommendation_copy_hides_internal_research_state(self):
        for obsolete in (
            "此景點尚未完成逐點攝影研究，因此暫不顯示推測性的拍攝建議。",
            "攝影研究待補，暫不評分",
            "所選日期沒有合適的已研究拍攝機會",
            "This place has not yet completed place-specific photography research, so no speculative shooting guide is shown.",
            "Photography research pending · not scored yet",
            "No researched shooting opportunity is suitable for the selected date",
            "この場所は個別撮影調査が未完了のため、推測的な撮影案内は表示しません。",
            "撮影調査待ち・現在は採点しません",
            "選択日に適した調査済みの撮影機会はありません",
        ):
            with self.subTest(obsolete=obsolete):
                self.assertNotIn(obsolete, APP)

        for expected in (
            "目前沒有可提供的拍攝指南。",
            "所選日期目前無法提供可靠的拍攝建議",
            "所選日期目前沒有明確的拍攝建議",
            "No shooting guide is currently available for this place.",
            "A reliable shooting recommendation is not currently available for the selected date",
            "There is no clear shooting recommendation for the selected date",
            "この場所では現在、撮影ガイドを提供できません。",
            "選択日は信頼できる撮影提案を現在提供できません",
            "選択日には明確な撮影提案がありません",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, APP)


    def test_selected_date_verdicts_use_photographer_language_and_overall_state(self):
        for obsolete in (
            "為什麼適合？",
            "此拍攝題材的關鍵條件目前符合",
            "Key conditions for this opportunity currently match",
            "この撮影機会の主要条件が一致",
        ):
            self.assertNotIn(obsolete, APP)

        for expected in (
            "為什麼這樣判斷？",
            "⚠️ 不建議拍{subject}",
            "相對較佳時段",
            "Why this assessment?",
            "⚠️ Not recommended for {subject}",
            "Relatively better time",
            "なぜこの判定？",
            "⚠️ {subject}の撮影はおすすめしません",
            "比較的良い時間帯",
        ):
            self.assertIn(expected, APP)

        self.assertIn("if(metric.recommendation_state)return metric.recommendation_state;", APP)
        self.assertIn("if(state==='not_recommended')return {primary:fill(d().verdict_unfavorable)", APP)
        self.assertIn("metric.recommendation_state||OPPORTUNITY_POSITIVE_STATUS_KEYS.has", APP)

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
