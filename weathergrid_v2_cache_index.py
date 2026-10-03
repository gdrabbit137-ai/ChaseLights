"""Static regional cache index for WeatherGrid V2.

ChaseLights deploys as a static site, so the browser cannot execute native
JMA/GFS Python adapters on pan. This module defines a publishable cache index
that maps viewport cells to pre-generated JSON bundles.
"""
from __future__ import annotations
import json, math
from pathlib import Path

REGIONS={
 "tw":{"bbox":{"west":119.5,"south":21.5,"east":123.5,"north":26.5},"cell_deg":2.0},
 "jp":{"bbox":{"west":122.0,"south":24.0,"east":146.0,"north":46.0},"cell_deg":2.0},
 "us_west":{"bbox":{"west":-125.0,"south":31.0,"east":-102.0,"north":49.0},"cell_deg":4.0},
}
def cells_for_region(region):
    spec=REGIONS[region]; b=spec["bbox"]; d=spec["cell_deg"]; out=[]
    y=b["south"]
    while y < b["north"]-1e-9:
        x=b["west"]
        while x < b["east"]-1e-9:
            e=min(x+d,b["east"]); n=min(y+d,b["north"])
            cid=f"{region}_{x:g}_{y:g}_{e:g}_{n:g}".replace("-","m").replace(".","p")
            out.append({"id":cid,"bbox":{"west":x,"south":y,"east":e,"north":n}})
            x=e
        y=n
    return out
def _inside_jma_domain(bbox):
    domain={"west":120.0,"south":22.4,"east":150.0,"north":47.6}
    return (
        bbox["west"] >= domain["west"]
        and bbox["south"] >= domain["south"]
        and bbox["east"] <= domain["east"]
        and bbox["north"] <= domain["north"]
    )

def build_index():
    regions={}
    for name,spec in REGIONS.items():
        cells=cells_for_region(name)
        indexed=[]
        for c in cells:
            providers={"gfs":f"weathergrid/v2/gfs/{c['id']}.json"}
            if _inside_jma_domain(c["bbox"]):
                providers["jma"]=f"weathergrid/v2/jma/{c['id']}.json"
            indexed.append({**c,"providers":providers})
        regions[name]={**spec,"cells":indexed}
    return {"schema_version":1,"mode":"static_regional_cache","regions":regions}
def write_index(path):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(build_index(),ensure_ascii=False,separators=(",",":")),encoding="utf-8")
if __name__=="__main__":
    import argparse
    a=argparse.ArgumentParser();a.add_argument("--output",default="weathergrid/v2/index.json");ns=a.parse_args();write_index(ns.output)
