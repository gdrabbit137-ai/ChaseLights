#!/usr/bin/env python3
import argparse
import json
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def build_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=390,844")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": True},
    )
    return driver


def wait_for(predicate, wait, label):
    try:
        return wait.until(predicate)
    except Exception as exc:
        raise AssertionError(f"Timed out waiting for {label}") from exc


def contains_han(text: str) -> bool:
    return any("\u3400" <= ch <= "\u9fff" for ch in str(text or ""))


def semantic_locale_snapshot(driver) -> list[str]:
    return driver.execute_script(
        """
        const selectors = [
          '#discovery-title', '#filter-result-summary', '#sub-nav', '#admin-filter',
          '.spot-region-heading', '.theme-winner', '.best-window-row',
          '.recommendation-reasons', '.forecast-status-row',
          '.card-footer-tools', '.access-note'
        ];
        return selectors.flatMap(selector =>
          [...document.querySelectorAll(selector)].map(node => node.textContent || '')
        );
        """
    )


def run(url: str, screenshot: Path) -> dict:
    driver = build_driver()
    wait = WebDriverWait(driver, 45)
    report = {"url": url}

    try:
        cache_bust = int(time.time())
        join = "&" if "?" in url else "?"
        driver.get(f"{url}{join}smoke={cache_bust}")

        wait_for(
            lambda d: d.execute_script(
                "return typeof currentData !== 'undefined' && currentData && "
                "typeof currentSpots !== 'undefined' && currentSpots.length > 0"
            ),
            wait,
            "homepage forecast data",
        )
        wait_for(
            lambda d: d.execute_script(
                "return window.innerWidth <= 640 && typeof isMobileAdminPicker === 'function' && isMobileAdminPicker()"
            ),
            wait,
            "mobile admin-picker breakpoint",
        )

        driver.execute_script("if (currentRegion !== 'tw') switchRegion('tw');")
        wait_for(
            lambda d: d.execute_script(
                "return currentRegion === 'tw' && currentSpots && currentSpots.length > 0"
            ),
            wait,
            "Taiwan region",
        )
        driver.execute_script(
            """
            currentAdminAreas.clear();
            persistAdminAreas();
            filterAndRender();
            window.scrollTo(0, 320);
            """
        )

        # Production localization smoke. Place/local-name nodes are deliberately
        # excluded: the product may show a translated Place name together with
        # its local/original name. Decision-facing semantic copy must follow the
        # selected locale on both phone and desktop surfaces.
        driver.execute_script("switchLanguage('en')")
        wait_for(
            lambda d: d.execute_script(
                "return currentLang === 'en' && document.documentElement.lang === 'en' "
                "&& document.title.includes('Photography Weather Forecast')"
            ),
            wait,
            "English locale",
        )
        mobile_english = semantic_locale_snapshot(driver)
        assert not [text for text in mobile_english if contains_han(text)], mobile_english

        first_card = driver.find_element(By.CSS_SELECTOR, "#spots-container .card")
        driver.execute_script("arguments[0].click()", first_card)
        wait_for(
            lambda d: d.find_element(By.ID, "place-modal-overlay").value_of_css_property("display") == "flex",
            wait,
            "English Place guide",
        )
        english_guide = driver.find_element(By.ID, "place-modal-body").text
        assert not contains_han(english_guide), english_guide
        driver.execute_script("closePlaceModal()")

        driver.execute_cdp_cmd(
            "Emulation.setDeviceMetricsOverride",
            {"width": 1440, "height": 1000, "deviceScaleFactor": 1, "mobile": False},
        )
        wait_for(lambda d: d.execute_script("return window.innerWidth > 640"), wait, "desktop viewport")
        desktop_english = semantic_locale_snapshot(driver)
        assert not [text for text in desktop_english if contains_han(text)], desktop_english

        driver.execute_script("switchLanguage('ja')")
        wait_for(
            lambda d: d.execute_script(
                "return currentLang === 'ja' && document.documentElement.lang === 'ja' "
                "&& document.title.includes('撮影向け気象予報')"
            ),
            wait,
            "Japanese locale",
        )
        japanese_semantic = " ".join(semantic_locale_snapshot(driver))
        for leaked in (
            "Where should I shoot",
            "Best shooting time",
            "Status details are temporarily unavailable",
            "View details",
        ):
            assert leaked not in japanese_semantic, (leaked, japanese_semantic)

        driver.execute_cdp_cmd(
            "Emulation.setDeviceMetricsOverride",
            {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": True},
        )
        wait_for(lambda d: d.execute_script("return window.innerWidth <= 640"), wait, "restored mobile viewport")
        driver.execute_script("switchLanguage('zh-TW')")
        wait_for(
            lambda d: d.execute_script(
                "return currentLang === 'zh-TW' && document.documentElement.lang === 'zh-TW'"
            ),
            wait,
            "Traditional Chinese locale",
        )
        driver.execute_script("window.scrollTo(0, 320)")

        before_scroll = driver.execute_script("return window.scrollY")
        trigger = driver.find_element(By.CSS_SELECTOR, "#admin-filter .admin-filter > summary")
        driver.execute_script("arguments[0].click()", trigger)

        wait_for(
            lambda d: d.execute_script(
                "return document.body.classList.contains('admin-picker-open') && "
                "document.querySelector('#admin-filter .admin-filter')?.open"
            ),
            wait,
            "mobile admin picker open state",
        )

        opened = driver.execute_script(
            """
            const details=document.querySelector('#admin-filter .admin-filter');
            const menu=document.querySelector('#admin-filter .admin-filter-menu');
            const backdrop=document.querySelector('#admin-filter [data-admin-backdrop]');
            return {
              innerWidth: window.innerWidth,
              innerHeight: window.innerHeight,
              open: details.open,
              locked: document.body.classList.contains('admin-picker-open'),
              bodyPosition: getComputedStyle(document.body).position,
              role: menu.getAttribute('role'),
              ariaModal: menu.getAttribute('aria-modal'),
              sheetHeight: menu.getBoundingClientRect().height,
              backdropDisplay: getComputedStyle(backdrop).display,
              hasSearch: !!document.querySelector('#admin-filter [data-admin-search]'),
              hasDone: !!document.querySelector('#admin-filter [data-admin-done]'),
              hasClose: !!document.querySelector('#admin-filter [data-admin-close]')
            };
            """
        )
        assert opened["innerWidth"] == 390, opened
        assert opened["open"] is True and opened["locked"] is True, opened
        assert opened["bodyPosition"] == "fixed", opened
        assert opened["role"] == "dialog" and opened["ariaModal"] == "true", opened
        assert opened["backdropDisplay"] != "none", opened
        assert opened["sheetHeight"] < opened["innerHeight"] * 0.84, opened
        assert opened["hasSearch"] and opened["hasDone"] and opened["hasClose"], opened

        hualien = driver.find_element(By.CSS_SELECTOR, '[data-admin-area="花蓮縣"]')
        driver.execute_script("arguments[0].click()", hualien)
        wait_for(
            lambda d: d.execute_script("return currentAdminAreas.has('花蓮縣')"),
            wait,
            "Hualien area selection",
        )
        selected = driver.execute_script(
            """
            return {
              open: document.querySelector('#admin-filter .admin-filter')?.open,
              locked: document.body.classList.contains('admin-picker-open'),
              selected: [...currentAdminAreas],
              pressed: document.querySelector('[data-admin-area="花蓮縣"]')?.getAttribute('aria-pressed'),
              cardCount: document.querySelectorAll('#spots-container .card').length
            };
            """
        )
        assert selected["open"] is True and selected["locked"] is True, selected
        assert selected["pressed"] == "true", selected
        assert selected["selected"] == ["花蓮縣"], selected
        assert selected["cardCount"] > 0, selected

        driver.find_element(By.CSS_SELECTOR, "#admin-filter [data-admin-done]").click()
        wait_for(
            lambda d: d.execute_script(
                "return !document.body.classList.contains('admin-picker-open') && "
                "!document.querySelector('#admin-filter .admin-filter')?.open"
            ),
            wait,
            "mobile admin picker close state",
        )

        after = driver.execute_script(
            """
            return {
              locked: document.body.classList.contains('admin-picker-open'),
              scrollY: window.scrollY,
              bodyPosition: getComputedStyle(document.body).position
            };
            """
        )
        assert after["locked"] is False, after
        assert after["bodyPosition"] != "fixed", after
        assert abs(after["scrollY"] - before_scroll) <= 2, (before_scroll, after)

        screenshot.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(screenshot))
        severe_logs = [
            item for item in driver.get_log("browser") if item.get("level") == "SEVERE"
        ]

        report.update(
            {
                "opened": opened,
                "selected": selected,
                "after": after,
                "scroll_before": before_scroll,
                "localization": {
                    "mobile_english_fragments": len(mobile_english),
                    "desktop_english_fragments": len(desktop_english),
                    "english_place_guide_no_han": True,
                    "japanese_semantic_rerendered": True,
                },
                "browser_severe_log_count": len(severe_logs),
                "browser_severe_logs": severe_logs[:10],
                "screenshot": str(screenshot),
            }
        )
        return report
    finally:
        driver.quit()


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test the deployed ChaseLights mobile administrative-area picker."
    )
    parser.add_argument("--url", default="https://chaselights.app/index.html")
    parser.add_argument(
        "--screenshot",
        type=Path,
        default=Path("artifacts/mobile-admin-production-smoke.png"),
    )
    args = parser.parse_args()
    report = run(args.url, args.screenshot)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
