#!/usr/bin/env python3
"""Browser smoke for the deployed, isolated WeatherGrid V2 experiment."""
import argparse, json, time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import TimeoutException

def driver():
    o=webdriver.ChromeOptions()
    o.add_argument("--headless=new"); o.add_argument("--no-sandbox")
    o.add_argument("--disable-dev-shm-usage"); o.add_argument("--window-size=1440,1000")
    o.set_capability("goog:loggingPrefs", {"browser":"ALL"})
    return webdriver.Chrome(options=o)

def bbox_values(text):
    return [float(v.strip()) for v in text.split(":",1)[1].split(",")]

def viewport_center(text):
    west,south,east,north=bbox_values(text)
    return ((west+east)/2,(south+north)/2)

def coverage_contains(viewport_text, coverage_text):
    vw,vs,ve,vn=bbox_values(viewport_text)
    cw,cs,ce,cn=bbox_values(coverage_text)
    return cw <= vw and cs <= vs and ce >= ve and cn >= vn

def run(url, screenshot):
    d=driver(); wait=WebDriverWait(d,60)
    try:
        d.get(url+("?smoke=" if "?" not in url else "&smoke=")+str(int(time.time())))
        try:
            wait.until(lambda x: "資料已就緒" in x.find_element(By.ID,"status").text)
        except TimeoutException:
            screenshot.parent.mkdir(parents=True,exist_ok=True)
            d.save_screenshot(str(screenshot))
            diagnostic={
              "status":d.find_element(By.ID,"status").text,
              "source":d.find_element(By.ID,"source").text,
              "viewport":d.find_element(By.ID,"viewport").text,
              "coverage":d.find_element(By.ID,"coverage").text,
              "resolved_provider":d.find_element(By.ID,"resolved-provider").text,
              "time":d.find_element(By.ID,"time").text,
              "browser_logs":d.get_log("browser")[-30:],
            }
            raise AssertionError("Initial V2 load timed out: "+json.dumps(diagnostic,ensure_ascii=False))
        initial={
          "status":d.find_element(By.ID,"status").text,
          "source":d.find_element(By.ID,"source").text,
          "viewport":d.find_element(By.ID,"viewport").text,
          "coverage":d.find_element(By.ID,"coverage").text,
        }
        assert "JMA MSM native tiles" in initial["source"], initial
        assert "loaded coverage" in initial["coverage"], initial
        # Unsupported native field must safely fall back instead of failing.
        Select(d.find_element(By.ID,"layer")).select_by_value("visibility")
        wait.until(lambda x: "資料已就緒" in x.find_element(By.ID,"status").text)
        visibility_source=d.find_element(By.ID,"source").text
        assert "NCEP Best Match" in visibility_source, visibility_source
        # Pan via the U.S. preset. The viewport and provider must change and refill.
        before=d.find_element(By.ID,"viewport").text
        d.find_element(By.CSS_SELECTOR,'[data-preset="us"]').click()
        wait.until(lambda x: x.find_element(By.ID,"viewport").text != before)
        wait.until(lambda x: "資料已就緒" in x.find_element(By.ID,"status").text)
        us={
          "status":d.find_element(By.ID,"status").text,
          "source":d.find_element(By.ID,"source").text,
          "viewport":d.find_element(By.ID,"viewport").text,
          "coverage":d.find_element(By.ID,"coverage").text,
        }
        assert "NCEP Best Match" in us["source"], us
        assert initial["viewport"] != us["viewport"], (initial,us)

        # Move again inside CONUS. A real drag must change the viewport and the
        # loader must refill/cover the new view instead of treating the preset
        # response as a fixed western-U.S. product.
        map_el=d.find_element(By.ID,"map")
        conus_before=d.find_element(By.ID,"viewport").text
        ActionChains(d).move_to_element(map_el).drag_and_drop_by_offset(map_el,-360,0).perform()
        wait.until(lambda x: x.find_element(By.ID,"viewport").text != conus_before)
        wait.until(lambda x: "資料已就緒" in x.find_element(By.ID,"status").text)
        conus_after={
          "status":d.find_element(By.ID,"status").text,
          "source":d.find_element(By.ID,"source").text,
          "viewport":d.find_element(By.ID,"viewport").text,
          "coverage":d.find_element(By.ID,"coverage").text,
        }
        assert "NCEP Best Match" in conus_after["source"], conus_after
        assert conus_after["viewport"] != conus_before, conus_after
        # The prefetch ring may already cover the new viewport, so cache bounds
        # are allowed to remain unchanged. What matters is that the moved view
        # resolves successfully with usable samples and loaded coverage.
        assert "samples" in conus_after["status"], conus_after
        assert "loaded coverage" in conus_after["coverage"], conus_after

        # Alaska has its own geographic resolver. Move there with real map
        # drags, but decide each next drag from the viewport that MapLibre
        # actually produced. This avoids assuming one pixel offset always lands
        # in Alaska across browser/rendering differences.
        for _ in range(8):
            current=d.find_element(By.ID,"viewport").text
            lon,lat=viewport_center(current)
            if -170 <= lon <= -129 and 51 <= lat <= 72:
                break
            dx=360 if lon > -129 else (-240 if lon < -170 else 0)
            dy=140 if lat < 51 else (-120 if lat > 72 else 0)
            assert dx or dy, {"viewport":current,"center":[lon,lat]}
            ActionChains(d).move_to_element(map_el).drag_and_drop_by_offset(map_el,dx,dy).perform()
            wait.until(lambda x, previous=current: x.find_element(By.ID,"viewport").text != previous)

        wait.until(lambda x: (
            "資料已就緒" in x.find_element(By.ID,"status").text
            and "loaded coverage" in x.find_element(By.ID,"coverage").text
            and coverage_contains(
                x.find_element(By.ID,"viewport").text,
                x.find_element(By.ID,"coverage").text,
            )
        ))
        alaska={
          "status":d.find_element(By.ID,"status").text,
          "source":d.find_element(By.ID,"source").text,
          "viewport":d.find_element(By.ID,"viewport").text,
          "coverage":d.find_element(By.ID,"coverage").text,
        }
        assert "NCEP Best Match" in alaska["source"], alaska
        alaska_lon,alaska_lat=viewport_center(alaska["viewport"])
        assert -170 <= alaska_lon <= -129 and 51 <= alaska_lat <= 72, alaska
        assert "samples" in alaska["status"], alaska
        assert coverage_contains(alaska["viewport"],alaska["coverage"]), alaska

        screenshot.parent.mkdir(parents=True,exist_ok=True)
        d.save_screenshot(str(screenshot))
        severe=[x for x in d.get_log("browser") if x.get("level")=="SEVERE"]
        return {"url":url,"initial":initial,"visibility_source":visibility_source,"us":us,
                "conus_after_pan":conus_after,"alaska_after_pan":alaska,
                "browser_severe_log_count":len(severe),"browser_severe_logs":severe[:10],
                "screenshot":str(screenshot)}
    finally:
        d.quit()

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--url",default="https://chaselights.app/weather-map-v2.html")
    p.add_argument("--screenshot",type=Path,default=Path("artifacts/weathergrid-v2-public-smoke.png"))
    a=p.parse_args(); print(json.dumps(run(a.url,a.screenshot),ensure_ascii=False,indent=2))
