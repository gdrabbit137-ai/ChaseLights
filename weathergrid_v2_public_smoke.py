#!/usr/bin/env python3
"""Browser smoke for the deployed, isolated WeatherGrid V2 experiment."""
import argparse, json, time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait

def driver():
    o=webdriver.ChromeOptions()
    o.add_argument("--headless=new"); o.add_argument("--no-sandbox")
    o.add_argument("--disable-dev-shm-usage"); o.add_argument("--window-size=1440,1000")
    o.set_capability("goog:loggingPrefs", {"browser":"ALL"})
    return webdriver.Chrome(options=o)

def run(url, screenshot):
    d=driver(); wait=WebDriverWait(d,60)
    try:
        d.get(url+("?smoke=" if "?" not in url else "&smoke=")+str(int(time.time())))
        wait.until(lambda x: "資料已就緒" in x.find_element(By.ID,"status").text)
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
        screenshot.parent.mkdir(parents=True,exist_ok=True)
        d.save_screenshot(str(screenshot))
        severe=[x for x in d.get_log("browser") if x.get("level")=="SEVERE"]
        return {"url":url,"initial":initial,"visibility_source":visibility_source,"us":us,
                "browser_severe_log_count":len(severe),"browser_severe_logs":severe[:10],
                "screenshot":str(screenshot)}
    finally:
        d.quit()

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--url",default="https://chaselights.app/weather-map-v2.html")
    p.add_argument("--screenshot",type=Path,default=Path("artifacts/weathergrid-v2-public-smoke.png"))
    a=p.parse_args(); print(json.dumps(run(a.url,a.screenshot),ensure_ascii=False,indent=2))
