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

        auto_layers = Select(driver.find_element(By.ID, "layer-select"))
        auto_layer_values = [o.get_attribute("value") for o in auto_layers.options]
        assert "total_cloud_percent" in auto_layer_values, auto_layer_values
        auto_layers.select_by_value("total_cloud_percent")
        coverage_note = driver.find_element(By.ID, "provider-coverage-note")
        wait_for(
            lambda d: coverage_note.is_displayed()
            and "不代表晴朗" in coverage_note.text
            and "自動預報可能改用不同模型" in coverage_note.text,
            wait,
            "AUTO cloud provider coverage explanation",
        )
        desktop_coverage_note = coverage_note.text

        driver.set_window_size(390, 844)
        wait_for(
            lambda d: coverage_note.is_displayed(),
            wait,
            "mobile provider coverage explanation",
        )
        mobile_overflow = driver.execute_script(
            "return document.documentElement.scrollWidth - window.innerWidth"
        )
        assert mobile_overflow <= 1, mobile_overflow
        driver.set_window_size(1600, 1200)

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
        timeline_slider = driver.find_element(By.ID, "time-slider")
        timeline_max = int(timeline_slider.get_attribute("max") or "0")
        assert timeline_max >= 2, timeline_max
        assert "預報時間" in driver.find_element(By.ID, "time-label").text

        # JMA MSM is a separately scheduled provider. On UI-only deploys its
        # bundle may not exist yet; on JMA data publishes the option must be
        # enabled and the native total/low/mid/high cloud contract must work.
        jma_option = next(
            (o for o in model_select.options if o.get_attribute("value") == "jma"),
            None,
        )
        assert jma_option is not None, [o.text for o in model_select.options]
        jma_available = jma_option.get_attribute("disabled") is None
        jma_report = {"available": jma_available}
        if jma_available:
            model_select.select_by_value("jma")
            wait_for(
                lambda d: d.find_element(By.ID, "source-state").text
                == "LIVE · JMA MSM 5 km",
                wait,
                "JMA MSM live-provider selection",
            )
            jma_layers = Select(driver.find_element(By.ID, "layer-select"))
            jma_layer_values = [
                o.get_attribute("value") for o in jma_layers.options
            ]
            for required in (
                "total_cloud_percent",
                "low_cloud_percent",
                "mid_cloud_percent",
                "high_cloud_percent",
            ):
                assert required in jma_layer_values, (
                    required,
                    jma_layer_values,
                )
            wait_for(
                lambda d: (
                    d.execute_script(
                        "return window.__weatherGridCoverageDebug && "
                        "window.__weatherGridCoverageDebug.modelMode === 'jma' && "
                        "window.__weatherGridCoverageDebug.timelineModel === 'JMA_MSM'"
                    )
                ),
                wait,
                "JMA MSM model/timeline activation",
            )
            jma_timeline_max = int(
                driver.find_element(By.ID, "time-slider").get_attribute("max")
                or "0"
            )
            assert jma_timeline_max >= 3, jma_timeline_max
            assert "預報時間" in driver.find_element(By.ID, "time-label").text
            jma_report.update(
                {
                    "layers": jma_layer_values,
                    "timeline_steps": jma_timeline_max + 1,
                    "cycle": driver.find_element(By.ID, "cycle-label").text,
                }
            )
            # Return to CWA because the rest of this production smoke proves
            # the existing wind-vector and subject-aware coverage path.
            model_select.select_by_value("cwa")
            wait_for(
                lambda d: d.find_element(By.ID, "source-state").text
                == "LIVE · CWA WRF 3 km",
                wait,
                "return to CWA after JMA validation",
            )

        # Himawari-9 is an observation source, not a forecast model. The
        # selector must exist even when a current snapshot is temporarily
        # unavailable; when available, verify observation-only semantics.
        himawari_option = next(
            (
                o
                for o in model_select.options
                if o.get_attribute("value") == "himawari"
            ),
            None,
        )
        assert himawari_option is not None, [o.text for o in model_select.options]
        himawari_available = himawari_option.get_attribute("disabled") is None
        himawari_report = {"available": himawari_available}
        if himawari_available:
            model_select.select_by_value("himawari")
            wait_for(
                lambda d: d.find_element(By.ID, "source-state").text
                == "OBS · Himawari-9 2 km",
                wait,
                "Himawari-9 observation selection",
            )
            himawari_layers = Select(driver.find_element(By.ID, "layer-select"))
            himawari_layer_values = [
                o.get_attribute("value") for o in himawari_layers.options
            ]
            assert himawari_layer_values == [
                "observed_cloud_mask",
                "cloud_top_height_m",
            ], himawari_layer_values
            wait_for(
                lambda d: (
                    d.execute_script(
                        "return window.__weatherGridCoverageDebug && "
                        "window.__weatherGridCoverageDebug.modelMode === 'himawari' && "
                        "window.__weatherGridCoverageDebug.timelineModel === "
                        "'HIMAWARI9_AHI_OBS' && "
                        "window.__weatherGridCoverageDebug.sourceKind === 'observation'"
                    )
                ),
                wait,
                "Himawari-9 observation semantics",
            )
            assert (
                driver.find_element(By.ID, "time-slider").get_attribute("max")
                == "0"
            )
            assert "觀測時間" in driver.find_element(By.ID, "time-label").text
            assert "衛星觀測" in driver.find_element(By.ID, "cycle-label").text
            assert driver.find_element(By.ID, "time-play").get_attribute(
                "disabled"
            ) is not None
            himawari_report.update(
                {
                    "layers": himawari_layer_values,
                    "time": driver.find_element(By.ID, "time-label").text,
                    "observation": driver.find_element(By.ID, "cycle-label").text,
                }
            )
            model_select.select_by_value("cwa")
            wait_for(
                lambda d: d.find_element(By.ID, "source-state").text
                == "LIVE · CWA WRF 3 km",
                wait,
                "return to CWA after Himawari validation",
            )

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
                "coverage_note": desktop_coverage_note,
                "mobile_coverage_note_overflow_px": mobile_overflow,
                "map_rect": map_rect,
                "weather_rect": weather_rect,
                "selected": selected,
                "browser_severe_log_count": len(severe_logs),
                "browser_severe_logs": severe_logs[:10],
                "screenshot": str(screenshot),
                "wind_overview_screenshot": str(overview),
                "jma_msm": jma_report,
                "himawari9": himawari_report,
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
