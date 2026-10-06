#!/usr/bin/env python3
"""Browser smoke for the deployed, isolated WeatherGrid V2 experiment."""
import argparse, json, re, time
from datetime import datetime, timezone
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

def lon_span(west,east):
    if abs(east-west) >= 359.999999:
        return 360.0
    return (east-west) % 360.0

def lon_segments(west,east):
    span=lon_span(west,east)
    if span >= 359.999999:
        return [(-180.0,180.0)]
    end=west+span
    if end <= 180.000001:
        return [(west,min(180.0,end))]
    return [(west,180.0),(-180.0,end-360.0)]

def viewport_center(text):
    west,south,east,north=bbox_values(text)
    lon=((west+lon_span(west,east)/2+180)%360)-180
    return (lon,(south+north)/2)

def coverage_contains(viewport_text, coverage_text):
    vw,vs,ve,vn=bbox_values(viewport_text)
    cw,cs,ce,cn=bbox_values(coverage_text)
    if cs > vs+1e-6 or cn < vn-1e-6:
        return False
    coverage_segments=lon_segments(cw,ce)
    return all(
        any(ow <= iw+1e-6 and oe >= ie-1e-6 for ow,oe in coverage_segments)
        for iw,ie in lon_segments(vw,ve)
    )

def sample_count(text):
    match=re.search(r"(\d+) samples", text or "")
    return int(match.group(1)) if match else 0

def settled(text):
    return "資料已就緒" in (text or "") or "資料不完整" in (text or "")

def coverage_present(text):
    return "loaded coverage" in (text or "") or "requested coverage" in (text or "")

def valid_time_age_seconds(text):
    raw=text.split(":",1)[1].strip()
    parsed=datetime.fromisoformat(raw.replace("Z","+00:00"))
    if parsed.tzinfo is None:
        parsed=parsed.replace(tzinfo=timezone.utc)
    return abs((datetime.now(timezone.utc)-parsed).total_seconds())

def run(url, screenshot):
    d=driver(); wait=WebDriverWait(d,60)
    try:
        d.get(url+("?smoke=" if "?" not in url else "&smoke=")+str(int(time.time())))
        try:
            wait.until(lambda x: settled(x.find_element(By.ID,"status").text))
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
          "time":d.find_element(By.ID,"time").text,
        }
        # Global-cloud P0 must use the same explicitly pinned GFS model even
        # when the initial viewport is Taiwan. Regional JMA ownership is only
        # exercised later through an explicit JMA selection.
        assert "NCEP GFS Global" in initial["source"], initial
        assert coverage_present(initial["coverage"]), initial
        assert coverage_contains(initial["viewport"], initial["coverage"]), initial
        if "資料已就緒" in initial["status"]:
            assert sample_count(initial["status"]) >= 200, initial
            assert valid_time_age_seconds(initial["time"]) <= 2 * 60 * 60, initial
        else:
            assert "rate-safe point fallback" in initial["source"], initial
            assert "外部 API 限流或請求預算已達上限" in initial["status"], initial

        # Japan must use the same pinned global GFS cloud baseline.
        jp_before=d.find_element(By.ID,"viewport").text
        d.find_element(By.CSS_SELECTOR,'[data-preset="jp"]').click()
        wait.until(lambda x: x.find_element(By.ID,"viewport").text != jp_before)
        wait.until(lambda x: (
            settled(x.find_element(By.ID,"status").text)
            and "NCEP GFS Global" in x.find_element(By.ID,"source").text
        ))
        jp={
          "status":d.find_element(By.ID,"status").text,
          "source":d.find_element(By.ID,"source").text,
          "viewport":d.find_element(By.ID,"viewport").text,
          "coverage":d.find_element(By.ID,"coverage").text,
          "region":d.execute_script("return window.__weatherGridV2Smoke.region()"),
        }
        assert jp["region"] == "jp", jp
        assert coverage_contains(jp["viewport"],jp["coverage"]), jp

        # Keep the cloud layer selected and move with the real U.S. preset.
        # The same pinned GFS global cloud model must remain active in CONUS.
        before=d.find_element(By.ID,"viewport").text
        d.find_element(By.CSS_SELECTOR,'[data-preset="us"]').click()
        wait.until(lambda x: x.find_element(By.ID,"viewport").text != before)
        try:
            wait.until(lambda x: (
                settled(x.find_element(By.ID,"status").text)
                and "NCEP GFS Global" in x.find_element(By.ID,"source").text
            ))
        except TimeoutException:
            screenshot.parent.mkdir(parents=True,exist_ok=True)
            d.save_screenshot(str(screenshot))
            diagnostic={
              "status":d.find_element(By.ID,"status").text,
              "source":d.find_element(By.ID,"source").text,
              "viewport":d.find_element(By.ID,"viewport").text,
              "coverage":d.find_element(By.ID,"coverage").text,
              "time":d.find_element(By.ID,"time").text,
              "browser_logs":d.get_log("browser")[-30:],
            }
            raise AssertionError("CONUS V2 handoff timed out: "+json.dumps(diagnostic,ensure_ascii=False))
        us={
          "status":d.find_element(By.ID,"status").text,
          "source":d.find_element(By.ID,"source").text,
          "viewport":d.find_element(By.ID,"viewport").text,
          "coverage":d.find_element(By.ID,"coverage").text,
        }
        assert "NCEP GFS Global" in us["source"], us
        assert initial["viewport"] != us["viewport"], (initial,us)
        assert coverage_contains(us["viewport"],us["coverage"]), us

        # Move again inside CONUS. A real drag must change the viewport and the
        # loader must refill/cover the new view instead of treating the preset
        # response as a fixed western-U.S. product.
        map_el=d.find_element(By.ID,"map")
        conus_before=d.find_element(By.ID,"viewport").text
        ActionChains(d).move_to_element(map_el).drag_and_drop_by_offset(map_el,-360,0).perform()
        wait.until(lambda x: x.find_element(By.ID,"viewport").text != conus_before)
        wait.until(lambda x: settled(x.find_element(By.ID,"status").text))
        conus_after={
          "status":d.find_element(By.ID,"status").text,
          "source":d.find_element(By.ID,"source").text,
          "viewport":d.find_element(By.ID,"viewport").text,
          "coverage":d.find_element(By.ID,"coverage").text,
        }
        assert "NCEP GFS Global" in conus_after["source"], conus_after
        assert conus_after["viewport"] != conus_before, conus_after
        # The prefetch ring may already cover the new viewport, so cache bounds
        # are allowed to remain unchanged. What matters is that the moved view
        # resolves successfully with usable samples and loaded coverage.
        assert "samples" in conus_after["status"], conus_after
        assert coverage_present(conus_after["coverage"]), conus_after

        # Return to a tighter Taiwan core viewport and explicitly select JMA
        # low cloud. Auto cloud stays pinned to GFS, while manual JMA still
        # proves the native regional tile path remains available and isolated.
        wait.until(lambda x: x.execute_script(
            "return !!window.__weatherGridV2Smoke"
        ))
        before_return=d.find_element(By.ID,"viewport").text
        d.execute_script(
            "window.__weatherGridV2Smoke.jumpTo(arguments[0], arguments[1], arguments[2])",
            121.75, 23.8, 10.0,
        )
        wait.until(lambda x: x.find_element(By.ID,"viewport").text != before_return)
        Select(d.find_element(By.ID,"layer")).select_by_value("cloud_cover_low")
        Select(d.find_element(By.ID,"provider")).select_by_value("jma")
        wait.until(lambda x: (
            settled(x.find_element(By.ID,"status").text)
            and "JMA MSM native tiles" in x.find_element(By.ID,"source").text
        ))
        tw_return={
          "status":d.find_element(By.ID,"status").text,
          "source":d.find_element(By.ID,"source").text,
          "viewport":d.find_element(By.ID,"viewport").text,
          "coverage":d.find_element(By.ID,"coverage").text,
        }
        assert coverage_contains(tw_return["viewport"],tw_return["coverage"]), tw_return

        # Unsupported native field must safely fall back instead of failing.
        Select(d.find_element(By.ID,"layer")).select_by_value("visibility")
        Select(d.find_element(By.ID,"provider")).select_by_value("auto")
        wait.until(lambda x: (
            settled(x.find_element(By.ID,"status").text)
            and "NCEP Best Match" in x.find_element(By.ID,"source").text
        ))
        visibility_source=d.find_element(By.ID,"source").text
        assert "NCEP Best Match" in visibility_source, visibility_source

        # Alaska has its own user-visible preset. Exercise the real control
        # instead of relying on the smoke-only jump hook, then verify that the
        # normal resolver identifies the resulting MapLibre viewport correctly.
        alaska_before=d.find_element(By.ID,"viewport").text
        d.find_element(By.CSS_SELECTOR,'[data-preset="us_alaska"]').click()
        wait.until(lambda x: x.find_element(By.ID,"viewport").text != alaska_before)
        wait.until(lambda x: x.execute_script(
            "return window.__weatherGridV2Smoke.region()"
        ) == "us_alaska")
        wait.until(lambda x: (
            settled(x.find_element(By.ID,"status").text)
            and coverage_present(x.find_element(By.ID,"coverage").text)
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
          "region":d.execute_script("return window.__weatherGridV2Smoke.region()"),
        }
        assert alaska["region"] == "us_alaska", alaska
        assert "NCEP Best Match" in alaska["source"], alaska
        alaska_lon,alaska_lat=viewport_center(alaska["viewport"])
        assert -170 <= alaska_lon <= -129 and 51 <= alaska_lat <= 72, alaska
        assert "samples" in alaska["status"], alaska
        # Published native GFS tiles are the high-resolution path. Until that
        # region is published, the browser point API is intentionally capped
        # to stay rate-safe and must identify itself as a degraded fallback.
        if "native tiles" in alaska["source"]:
            assert sample_count(alaska["status"]) >= 600, alaska
        else:
            assert "rate-safe point fallback" in alaska["source"], alaska
            if "資料已就緒" in alaska["status"]:
                assert sample_count(alaska["status"]) >= 200, alaska
            else:
                assert "外部 API 限流或請求預算已達上限" in alaska["status"], alaska
        assert coverage_contains(alaska["viewport"],alaska["coverage"]), alaska

        # An arbitrary non-preset global viewport must also resolve to the
        # pinned GFS cloud model, then refill after a real pan.
        Select(d.find_element(By.ID,"layer")).select_by_value("cloud_cover")
        global_before=d.find_element(By.ID,"viewport").text
        d.execute_script(
            "window.__weatherGridV2Smoke.jumpTo(arguments[0], arguments[1], arguments[2])",
            10.0, 50.0, 5.0,
        )
        wait.until(lambda x: x.find_element(By.ID,"viewport").text != global_before)
        wait.until(lambda x: (
            settled(x.find_element(By.ID,"status").text)
            and "NCEP GFS Global" in x.find_element(By.ID,"source").text
            and coverage_contains(
                x.find_element(By.ID,"viewport").text,
                x.find_element(By.ID,"coverage").text,
            )
        ))
        global_view={
          "status":d.find_element(By.ID,"status").text,
          "source":d.find_element(By.ID,"source").text,
          "viewport":d.find_element(By.ID,"viewport").text,
          "coverage":d.find_element(By.ID,"coverage").text,
          "region":d.execute_script("return window.__weatherGridV2Smoke.region()"),
        }
        assert global_view["region"] is None, global_view
        global_map=d.find_element(By.ID,"map")
        global_pan_before=global_view["viewport"]
        ActionChains(d).move_to_element(global_map).drag_and_drop_by_offset(global_map,-260,0).perform()
        wait.until(lambda x: x.find_element(By.ID,"viewport").text != global_pan_before)
        wait.until(lambda x: (
            settled(x.find_element(By.ID,"status").text)
            and "NCEP GFS Global" in x.find_element(By.ID,"source").text
            and coverage_contains(
                x.find_element(By.ID,"viewport").text,
                x.find_element(By.ID,"coverage").text,
            )
        ))
        global_after_pan={
          "status":d.find_element(By.ID,"status").text,
          "source":d.find_element(By.ID,"source").text,
          "viewport":d.find_element(By.ID,"viewport").text,
          "coverage":d.find_element(By.ID,"coverage").text,
        }

        # With renderWorldCopies disabled, MapLibre may clip the visible
        # viewport at ±180°.  The prefetch coverage is the geometry that must
        # wrap across the antimeridian while remaining a local request.
        dateline_before=d.find_element(By.ID,"viewport").text
        d.execute_script(
            "window.__weatherGridV2Smoke.jumpTo(arguments[0], arguments[1], arguments[2])",
            179.0, 10.0, 6.0,
        )
        wait.until(lambda x: x.find_element(By.ID,"viewport").text != dateline_before)
        wait.until(lambda x: (
            settled(x.find_element(By.ID,"status").text)
            and "NCEP GFS Global" in x.find_element(By.ID,"source").text
            and coverage_contains(
                x.find_element(By.ID,"viewport").text,
                x.find_element(By.ID,"coverage").text,
            )
        ))
        dateline={
          "status":d.find_element(By.ID,"status").text,
          "source":d.find_element(By.ID,"source").text,
          "viewport":d.find_element(By.ID,"viewport").text,
          "coverage":d.find_element(By.ID,"coverage").text,
          "region":d.execute_script("return window.__weatherGridV2Smoke.region()"),
        }
        dw,ds,de,dn=bbox_values(dateline["viewport"])
        cw,cs,ce,cn=bbox_values(dateline["coverage"])
        assert lon_span(dw,de) < 90, dateline
        assert cw > ce, dateline
        assert lon_span(cw,ce) < 90, dateline
        assert dateline["region"] is None, dateline

        dateline_map=d.find_element(By.ID,"map")
        dateline_pan_before=dateline["viewport"]
        ActionChains(d).move_to_element(dateline_map).drag_and_drop_by_offset(dateline_map,-300,0).perform()
        wait.until(lambda x: x.find_element(By.ID,"viewport").text != dateline_pan_before)
        wait.until(lambda x: (
            settled(x.find_element(By.ID,"status").text)
            and "NCEP GFS Global" in x.find_element(By.ID,"source").text
            and coverage_contains(
                x.find_element(By.ID,"viewport").text,
                x.find_element(By.ID,"coverage").text,
            )
        ))
        dateline_after_pan={
          "status":d.find_element(By.ID,"status").text,
          "source":d.find_element(By.ID,"source").text,
          "viewport":d.find_element(By.ID,"viewport").text,
          "coverage":d.find_element(By.ID,"coverage").text,
        }
        paw,pas,pae,pan=bbox_values(dateline_after_pan["viewport"])
        pcw,pcs,pce,pcn=bbox_values(dateline_after_pan["coverage"])
        assert lon_span(paw,pae) < 90, dateline_after_pan
        assert lon_span(pcw,pce) < 90, dateline_after_pan

        screenshot.parent.mkdir(parents=True,exist_ok=True)
        d.save_screenshot(str(screenshot))
        severe=[x for x in d.get_log("browser") if x.get("level")=="SEVERE"]
        return {"url":url,"initial":initial,"japan_global_cloud":jp,
                "visibility_source":visibility_source,
                "us_cloud_handoff":us,"conus_after_pan":conus_after,
                "tw_native_return":tw_return,"alaska_after_pan":alaska,
                "global_cloud":global_view,"global_after_pan":global_after_pan,
                "dateline_cloud":dateline,"dateline_after_pan":dateline_after_pan,
                "browser_severe_log_count":len(severe),"browser_severe_logs":severe[:10],
                "screenshot":str(screenshot)}
    finally:
        d.quit()

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--url",default="https://chaselights.app/weather-map-v2.html")
    p.add_argument("--screenshot",type=Path,default=Path("artifacts/weathergrid-v2-public-smoke.png"))
    a=p.parse_args(); print(json.dumps(run(a.url,a.screenshot),ensure_ascii=False,indent=2))
