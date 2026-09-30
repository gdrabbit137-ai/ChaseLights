#!/usr/bin/env python3
import argparse
import json
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait


def build_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1600,1200")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    return webdriver.Chrome(options=options)


def wait_for(predicate, wait, label):
    try:
        return wait.until(predicate)
    except Exception as exc:
        raise AssertionError(f"Timed out waiting for {label}") from exc


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
                "return window.__weatherGridPreviewReady === true"
            ),
            wait,
            "WeatherGrid preview readiness",
        )

        wait_for(
            lambda d: "ready"
            in d.find_element(By.ID, "basemap-status").get_attribute("class"),
            wait,
            "MapLibre/OpenFreeMap basemap readiness",
        )

        source_text = driver.find_element(By.ID, "source-state").text
        basemap_text = driver.find_element(By.ID, "basemap-status").text
        opacity = driver.find_element(By.ID, "opacity-slider").get_attribute("value")
        map_canvas = driver.find_element(By.CSS_SELECTOR, "#weather-basemap .maplibregl-canvas")
        weather_canvas = driver.find_element(By.ID, "weather-canvas")

        assert source_text in {"AUTO · GFS", "AUTO · ICON Global"}, source_text
        assert "MapLibre" in basemap_text and "OpenFreeMap" in basemap_text, basemap_text
        assert opacity == "62", opacity

        model_select = Select(driver.find_element(By.ID, "model-select"))
        cwa_option = next(
            (o for o in model_select.options if o.get_attribute("value") == "cwa"),
            None,
        )
        assert cwa_option is not None, [o.text for o in model_select.options]
        assert cwa_option.get_attribute("disabled") is None, (
            "CWA selector is disabled; live CWA browser bundle was not loaded"
        )
        model_select.select_by_value("cwa")
        wait_for(
            lambda d: d.find_element(By.ID, "source-state").text
            == "LIVE · CWA WRF 3 km",
            wait,
            "CWA live-provider selection",
        )
        cwa_layers = Select(driver.find_element(By.ID, "layer-select"))
        cwa_layer_values = [o.get_attribute("value") for o in cwa_layers.options]
        for required in (
            "temperature_2m_c",
            "relative_humidity_2m_percent",
            "shortwave_flux_w_m2",
            "wind_speed_10m_m_s",
            "wind_direction_10m_deg",
        ):
            assert required in cwa_layer_values, (required, cwa_layer_values)
        wait_for(
            lambda d: (
                d.execute_script(
                    "return window.__weatherGridCoverageDebug && "
                    "window.__weatherGridCoverageDebug.modelMode === 'cwa' && "
                    "window.__weatherGridCoverageDebug.timelineModel === 'CWA_WRF_3KM'"
                )
            ),
            wait,
            "CWA model/timeline activation",
        )
        timeline_buttons = driver.find_elements(By.CSS_SELECTOR, "#timeline button")
        assert len(timeline_buttons) >= 3, len(timeline_buttons)

        map_rect = driver.execute_script(
            "const r=arguments[0].getBoundingClientRect();"
            "return {width:r.width,height:r.height};",
            map_canvas,
        )
        weather_rect = driver.execute_script(
            "const r=arguments[0].getBoundingClientRect();"
            "return {width:r.width,height:r.height};",
            weather_canvas,
        )
        assert map_rect["width"] > 300 and map_rect["height"] > 200, map_rect
        assert weather_rect["width"] > 300 and weather_rect["height"] > 200, weather_rect

        layer_select = Select(driver.find_element(By.ID, "layer-select"))
        layer_select.select_by_value("wind_speed_10m_m_s")
        wait_for(
            lambda d: d.execute_script(
                "return window.__weatherGridCoverageDebug && "
                "window.__weatherGridCoverageDebug.windVectors === true && "
                "window.__weatherGridCoverageDebug.windVectorCount > 0"
            ),
            wait,
            "automatic wind-vector enablement and rendered vectors",
        )
        assert driver.find_element(By.ID, "wind-vector-toggle").is_selected()

        overview = screenshot.with_name(
            screenshot.stem + "-wind-overview" + screenshot.suffix
        )
        overview.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(overview))

        spot_select = Select(driver.find_element(By.ID, "spot-select"))
        spot_values = [o.get_attribute("value") for o in spot_select.options]
        assert "tw-073" in spot_values, spot_values[:10]
        spot_select.select_by_value("tw-073")

        wait_for(
            lambda d: d.execute_script(
                "return window.__weatherGridCoverageDebug && "
                "window.__weatherGridCoverageDebug.spotId === 'tw-073'"
            ),
            wait,
            "tw-073 Place selection",
        )

        opportunity = Select(driver.find_element(By.ID, "opportunity-select"))
        nonempty = [o.get_attribute("value") for o in opportunity.options if o.get_attribute("value")]
        assert nonempty, [o.text for o in opportunity.options]
        opportunity.select_by_value(nonempty[0])

        wait_for(
            lambda d: d.execute_script(
                "return window.__weatherGridCoverageDebug && "
                "window.__weatherGridCoverageDebug.opportunityId !== ''"
            ),
            wait,
            "Opportunity coverage selection",
        )

        selected = driver.execute_script(
            """
            return {
              source: document.getElementById('source-state').textContent,
              basemap: document.getElementById('basemap-status').textContent,
              opacity: document.getElementById('opacity-slider').value,
              layer: document.getElementById('layer-select').value,
              spot: document.getElementById('spot-select').value,
              opportunity: document.getElementById('opportunity-select').value,
              coverage: document.getElementById('coverage-status').textContent,
              debug: window.__weatherGridCoverageDebug,
              cycle: document.getElementById('cycle-label').textContent
            };
            """
        )
        assert selected["layer"] == "wind_speed_10m_m_s", selected
        assert selected["spot"] == "tw-073", selected
        assert selected["opportunity"], selected
        assert selected["debug"]["windVectors"] is True, selected
        assert "viewport" in selected["coverage"], selected["coverage"]
        assert selected["debug"]["coverageSource"] == "live", selected

        screenshot.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(screenshot))

        severe_logs = [
            item
            for item in driver.get_log("browser")
            if item.get("level") == "SEVERE"
        ]
        report.update(
            {
                "source": source_text,
                "basemap": basemap_text,
                "opacity_percent": int(opacity),
                "map_rect": map_rect,
                "weather_rect": weather_rect,
                "selected": selected,
                "browser_severe_log_count": len(severe_logs),
                "browser_severe_logs": severe_logs[:10],
                "screenshot": str(screenshot),
                "wind_overview_screenshot": str(overview),
            }
        )
        return report
    finally:
        driver.quit()


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test the deployed ChaseLights WeatherGrid basemap."
    )
    parser.add_argument(
        "--url",
        default="https://chaselights.app/weather-map.html",
    )
    parser.add_argument(
        "--screenshot",
        type=Path,
        default=Path("artifacts/weathergrid-production-smoke.png"),
    )
    args = parser.parse_args()
    report = run(args.url, args.screenshot)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
