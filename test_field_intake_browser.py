from pathlib import Path
import base64
import tempfile

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select


URL = "http://127.0.0.1:8000/field-intake.html"
JPEG_1PX = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////"
    "2wBDAf//////////////////////////////////////////////////////////////////////////////////////"
    "wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAf/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/"
    "9oADAMBAAIQAxAAAAF//8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABBQJ//8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/"
    "aAAgBAwEBPwF//8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAgBAgEBPwF//8QAFBABAAAAAAAAAAAAAAAAAAAAAP/"
    "aAAgBAQAGPwJ//8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPyF//9oADAMBAAIAAwAAABD/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/"
    "9oACAEDAQE/EB//xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oACAECAQE/EB//xAAUEAEAAAAAAAAAAAAAAAAAAAAA/"
    "9oACAEBAAE/EB//2Q=="
)


def wait_state(driver, wait):
    wait.until(lambda d: d.execute_script(
        "return !!window.ChaseLightsFieldIntake && ChaseLightsFieldIntake.getStateSummary().catalogLoaded"
    ))


def state(driver):
    return driver.execute_script("return ChaseLightsFieldIntake.getStateSummary()")


def main():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1440,1100")
    driver = webdriver.Chrome(options=opts)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get(URL)
        wait_state(driver, wait)

        with tempfile.TemporaryDirectory() as tmp:
            photo = Path(tmp) / "no-exif.jpg"
            photo.write_bytes(base64.b64decode(JPEG_1PX))
            driver.find_element(By.ID, "photo-input").send_keys(str(photo))
            wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, ".observation-card")) == 1)

        initial = state(driver)
        assert initial["rows"][0]["selected_spot_id"] is None, initial
        assert driver.find_element(By.CSS_SELECTOR, ".selected-place.unmatched")
        assert not driver.find_elements(By.CSS_SELECTOR, "select.place-select")

        search = driver.find_element(By.CSS_SELECTOR, ".place-search-input")
        search.send_keys("tw-")
        first_option = wait.until(lambda d: d.find_element(By.CSS_SELECTOR, '.place-option[data-spot-id]'))
        target_id = first_option.get_attribute("data-spot-id")
        assert target_id and target_id.startswith("tw-"), target_id
        assert driver.find_elements(By.CSS_SELECTOR, '[data-action="close-results"]')
        search.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
        wait.until(lambda d: state(d)["rows"][0]["selected_spot_id"] == target_id)
        assert state(driver)["rows"][0]["association_method"] == "manual_search_selection"

        driver.find_element(By.CSS_SELECTOR, ".clear-btn").click()
        wait.until(lambda d: state(d)["rows"][0]["selected_spot_id"] is None)

        association = driver.execute_script("""
          return ChaseLightsFieldIntake.buildObservationDraft({
            id:'synthetic',
            file:{name:'synthetic.jpg',type:'image/jpeg',size:1,lastModified:0},
            capture_time:{captured_at:null,local_clock:null,utc_offset:null,source_tag:null,timezone_status:'missing'},
            user_capture_time:'',
            camera:{},
            location:null,
            auto_match:{spot_id:arguments[0],canonical_name:'candidate',distance_km:0.25,viewpoint_id:'vp-test'},
            selected_spot_id:null,
            selected_opportunity_id:null,
            outcome:'',
            failure_reason:'',
            note:''
          }, {includeGps:false,modelValidation:false}).place_match;
        """, target_id)
        assert association["method"] == "unmatched", association
        assert association["confirmed_by_user"] is False, association
        assert association["gps_suggestion"]["spot_id"] == target_id, association
        suggestion_confirmed = driver.execute_script(
            "return ChaseLightsFieldIntake.associationMethod({selected_spot_id:'tw-003',selection_source:'gps_suggestion_confirmation'});"
        )
        searched_same = driver.execute_script(
            "return ChaseLightsFieldIntake.associationMethod({selected_spot_id:'tw-003',selection_source:'manual_search_selection'});"
        )
        overridden = driver.execute_script(
            "return ChaseLightsFieldIntake.associationMethod({selected_spot_id:'tw-004',selection_source:'manual_override'});"
        )
        assert suggestion_confirmed == "user_confirmed_gps_suggestion"
        assert searched_same == "manual_search_selection"
        assert overridden == "user_override"

        Select(driver.find_element(By.ID, "language-select")).select_by_value("en")
        wait.until(lambda d: state(d)["lang"] == "en")
        assert "Search place" in driver.find_element(By.CSS_SELECTOR, ".place-search-input").get_attribute("placeholder")
        assert "Unmatched" in driver.find_element(By.CSS_SELECTOR, ".selected-place-title").text

        driver.set_window_size(390, 844)
        search = driver.find_element(By.CSS_SELECTOR, ".place-search-input")
        search.send_keys(target_id)
        wait.until(lambda d: d.find_element(By.CSS_SELECTOR, '.place-option[data-spot-id="' + target_id + '"]'))
        close_button = driver.find_element(By.CSS_SELECTOR, '[data-action="close-results"]')
        driver.execute_script("arguments[0].click()", close_button)
        wait.until(lambda d: d.find_element(By.CSS_SELECTOR, ".place-results").get_attribute("hidden") is not None)
        search = driver.find_element(By.CSS_SELECTOR, ".place-search-input")
        search.send_keys(Keys.CONTROL, "a")
        search.send_keys(target_id)
        option = wait.until(lambda d: d.find_element(By.CSS_SELECTOR, '.place-option[data-spot-id="' + target_id + '"]'))
        driver.execute_script("arguments[0].click()", option)
        wait.until(lambda d: state(d)["rows"][0]["selected_spot_id"] == target_id)
        overflow = driver.execute_script("return document.documentElement.scrollWidth - window.innerWidth")
        assert overflow <= 1, overflow
        driver.find_element(By.CSS_SELECTOR, ".clear-btn").click()
        wait.until(lambda d: state(d)["rows"][0]["selected_spot_id"] is None)

        Select(driver.find_element(By.ID, "language-select")).select_by_value("ja")
        wait.until(lambda d: state(d)["lang"] == "ja")
        assert "実写検証" in driver.find_element(By.TAG_NAME, "h1").text

        print({
            "desktop_keyboard_match": True,
            "explicit_unmatched": True,
            "gps_suggestion_not_confirmation": True,
            "localization": ["zh-TW", "en", "ja"],
            "mobile_width": driver.execute_script("return window.innerWidth"),
            "mobile_overflow_px": overflow,
        })
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
