#!/usr/bin/env python3
import argparse
import base64
import json
import tempfile
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait


JPEG_1PX = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////"
    "2wBDAf//////////////////////////////////////////////////////////////////////////////////////"
    "wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAf/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/"
    "9oADAMBAAIQAxAAAAF//8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABBQJ//8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/"
    "aAAgBAwEBPwF//8QAFBEBAAAAAAAAAAAAAAAAAAAAAAP/aAAgBAgEBPwF//8QAFBABAAAAAAAAAAAAAAAAAAAAAP/"
    "aAAgBAQAGPwJ//8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPyF//9oADAMBAAIAAwAAABD/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/"
    "9oACAEDAQE/EB//xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oACAECAQE/EB//xAAUEAEAAAAAAAAAAAAAAAAAAAAA/"
    "9oACAEBAAE/EB//2Q=="
)


def build_driver(width=1440, height=1100):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--window-size={width},{height}")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    return webdriver.Chrome(options=options)


def wait_for(wait, predicate, label):
    try:
        return wait.until(predicate)
    except Exception as exc:
        raise AssertionError(f"Timed out waiting for {label}") from exc


def state(driver):
    return driver.execute_script("return ChaseLightsFieldIntake.getStateSummary()")


def run(url: str, screenshot: Path) -> dict:
    driver = build_driver()
    wait = WebDriverWait(driver, 45)
    report = {"url": url}

    try:
        nonce = int(time.time())
        join = "&" if "?" in url else "?"
        driver.get(f"{url}{join}smoke={nonce}")

        wait_for(
            wait,
            lambda d: d.execute_script(
                "return !!window.ChaseLightsFieldIntake && "
                "ChaseLightsFieldIntake.getStateSummary().catalogLoaded"
            ),
            "Field Intake catalog readiness",
        )

        body_text = driver.find_element(By.TAG_NAME, "body").text
        for forbidden in (
            "B120",
            "ground truth",
            "observation JSON",
            "field-observation-draft-r4.2-1",
            "FV-",
        ):
            assert forbidden not in body_text, (forbidden, body_text[:1200])

        with tempfile.TemporaryDirectory() as tmp:
            photo = Path(tmp) / "no-exif.jpg"
            photo.write_bytes(base64.b64decode(JPEG_1PX))
            driver.find_element(By.ID, "photo-input").send_keys(str(photo))
            wait_for(
                wait,
                lambda d: len(d.find_elements(By.CSS_SELECTOR, ".observation-card")) == 1,
                "parsed observation card",
            )

        initial = state(driver)
        assert initial["rows"][0]["selected_spot_id"] is None, initial
        assert initial["rows"][0]["association_method"] == "unmatched", initial
        assert driver.find_element(By.CSS_SELECTOR, ".selected-place.unmatched")
        assert not driver.find_elements(By.CSS_SELECTOR, "select.place-select")

        search = driver.find_element(By.CSS_SELECTOR, ".place-search-input")
        search.send_keys("tw-")
        first_option = wait_for(
            wait,
            lambda d: d.find_element(By.CSS_SELECTOR, ".place-option[data-spot-id]"),
            "search result",
        )
        target_id = first_option.get_attribute("data-spot-id")
        assert target_id and target_id.startswith("tw-"), target_id
        assert driver.find_elements(By.CSS_SELECTOR, '[data-action="close-results"]')
        search.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
        wait_for(
            wait,
            lambda d: state(d)["rows"][0]["selected_spot_id"] == target_id,
            "desktop keyboard Place selection",
        )
        assert state(driver)["rows"][0]["association_method"] == "manual_search_selection"

        driver.find_element(By.CSS_SELECTOR, ".clear-btn").click()
        wait_for(
            wait,
            lambda d: state(d)["rows"][0]["selected_spot_id"] is None,
            "clear to unmatched",
        )

        suggestion = driver.execute_script(
            """
            return ChaseLightsFieldIntake.buildObservationDraft({
              id:'production-synthetic',
              file:{name:'synthetic.jpg',type:'image/jpeg',size:1,lastModified:0},
              capture_time:{captured_at:null,local_clock:null,utc_offset:null,source_tag:null,timezone_status:'missing'},
              user_capture_time:'',
              camera:{},
              location:null,
              auto_match:{spot_id:arguments[0],canonical_name:'candidate',distance_km:0.25,viewpoint_id:'vp-test'},
              selected_spot_id:null,
              selection_source:null,
              selected_opportunity_id:null,
              outcome:'',
              failure_reason:'',
              note:''
            }, {includeGps:false,modelValidation:false}).place_match;
            """,
            target_id,
        )
        assert suggestion["method"] == "unmatched", suggestion
        assert suggestion["confirmed_by_user"] is False, suggestion
        assert suggestion["gps_suggestion"]["spot_id"] == target_id, suggestion

        Select(driver.find_element(By.ID, "language-select")).select_by_value("en")
        wait_for(wait, lambda d: state(d)["lang"] == "en", "English locale")
        assert "Search place" in driver.find_element(
            By.CSS_SELECTOR, ".place-search-input"
        ).get_attribute("placeholder")
        assert "Unmatched" in driver.find_element(
            By.CSS_SELECTOR, ".selected-place-title"
        ).text

        driver.set_window_size(390, 844)
        search = driver.find_element(By.CSS_SELECTOR, ".place-search-input")
        search.send_keys(target_id)
        wait_for(
            wait,
            lambda d: d.find_element(
                By.CSS_SELECTOR, f'.place-option[data-spot-id="{target_id}"]'
            ),
            "mobile search result",
        )
        close_button = driver.find_element(
            By.CSS_SELECTOR, '[data-action="close-results"]'
        )
        driver.execute_script("arguments[0].click()", close_button)
        wait_for(
            wait,
            lambda d: d.find_element(By.CSS_SELECTOR, ".place-results").get_attribute(
                "hidden"
            )
            is not None,
            "mobile explicit close",
        )

        search = driver.find_element(By.CSS_SELECTOR, ".place-search-input")
        search.send_keys(Keys.CONTROL, "a")
        search.send_keys(target_id)
        option = wait_for(
            wait,
            lambda d: d.find_element(
                By.CSS_SELECTOR, f'.place-option[data-spot-id="{target_id}"]'
            ),
            "mobile reopened result",
        )
        driver.execute_script("arguments[0].click()", option)
        wait_for(
            wait,
            lambda d: state(d)["rows"][0]["selected_spot_id"] == target_id,
            "mobile touch Place selection",
        )

        overflow = driver.execute_script(
            "return document.documentElement.scrollWidth - window.innerWidth"
        )
        assert overflow <= 1, overflow

        Select(driver.find_element(By.ID, "language-select")).select_by_value("ja")
        wait_for(wait, lambda d: state(d)["lang"] == "ja", "Japanese locale")
        assert "実写検証" in driver.find_element(By.TAG_NAME, "h1").text

        screenshot.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(screenshot))

        severe_logs = [
            item for item in driver.get_log("browser") if item.get("level") == "SEVERE"
        ]
        report.update(
            {
                "desktop_keyboard_match": True,
                "explicit_unmatched": True,
                "gps_suggestion_not_confirmation": True,
                "localization": ["zh-TW", "en", "ja"],
                "mobile_width": driver.execute_script("return window.innerWidth"),
                "mobile_overflow_px": overflow,
                "selected_spot_id": target_id,
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
        description="Smoke-test the deployed ChaseLights Field Intake experience."
    )
    parser.add_argument(
        "--url",
        default="https://chaselights.app/field-intake.html",
    )
    parser.add_argument(
        "--screenshot",
        type=Path,
        default=Path("artifacts/field-intake-production-smoke.png"),
    )
    args = parser.parse_args()
    print(json.dumps(run(args.url, args.screenshot), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
