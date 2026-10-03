"""WeatherGrid V2 static-cache capacity budget.

Estimates payload pressure before publishing generated regional cells into Git.
Use measured_bytes when available; otherwise estimates raw float payload and a
conservative compact-JSON multiplier.
"""
from __future__ import annotations
import math

MIB=1024*1024
PROVIDERS={
 "jma":{"dx":0.0625,"dy":0.05,"fields":4,"frames":40},
 "gfs":{"dx":0.25,"dy":0.25,"fields":7,"frames":5},
}
# Guardrail, not a GitHub hard limit. Keeps the experiment comfortably below
# the scale where generated weather data dominates the static site/repository.
DEFAULT_REFRESH_BUDGET_MIB=150.0

def estimate_cell(provider,bbox,json_multiplier=2.5):
    p=PROVIDERS[provider]
    cols=math.floor((bbox["east"]-bbox["west"])/p["dx"]+1e-9)+1
    rows=math.floor((bbox["north"]-bbox["south"])/p["dy"]+1e-9)+1
    values=rows*cols*p["fields"]*p["frames"]
    raw=values*4
    return {"provider":provider,"rows":rows,"cols":cols,"fields":p["fields"],"frames":p["frames"],
            "values":values,"raw_float32_bytes":raw,"estimated_compact_json_bytes":math.ceil(raw*json_multiplier)}

def estimate_region(provider,cells,measured_bytes=None):
    estimates=[estimate_cell(provider,c["bbox"]) for c in cells]
    total=sum(x["estimated_compact_json_bytes"] for x in estimates)
    if measured_bytes is not None: total=sum(measured_bytes.get(c["id"],e["estimated_compact_json_bytes"]) for c,e in zip(cells,estimates))
    return {"provider":provider,"cell_count":len(cells),"estimated_refresh_bytes":total,
            "estimated_refresh_mib":round(total/MIB,2),"within_default_budget":total<=DEFAULT_REFRESH_BUDGET_MIB*MIB}

def recommend_storage(region_estimates):
    total=sum(x["estimated_refresh_bytes"] for x in region_estimates)
    # Generated forecast cells are ephemeral. Even below the experiment
    # guardrail, object/deployment storage is preferred over Git history.
    return {"estimated_refresh_mib":round(total/MIB,2),
            "publish_generated_cells_to_git":False,
            "preferred":"deployment/object storage",
            "reason":"ephemeral generated forecast grids should not accumulate in Git history"}
