"""Viewport-driven fetch planning for the isolated WeatherGrid V2 experiment.

Pure planning only: no network calls and no production WeatherGrid changes.
"""
from __future__ import annotations
import hashlib, json, math

DOMAINS={
 "jma":{"west":120.0,"south":22.4,"east":150.0,"north":47.6,"spacing":(0.0625,0.05)},
 "gfs":{"west":-180.0,"south":-90.0,"east":180.0,"north":90.0,"spacing":(0.25,0.25)},
}
def _finite(v):
    v=float(v)
    if not math.isfinite(v): raise ValueError("bbox coordinates must be finite")
    return v
def normalize_bbox(b):
    out={"west":_finite(b["west"]),"south":_finite(b["south"]),"east":_finite(b["east"]),"north":_finite(b["north"])}
    if not out["west"]<out["east"] or not out["south"]<out["north"]: raise ValueError("invalid bbox")
    if out["south"] < -90 or out["north"] > 90: raise ValueError("latitude outside world")
    return out
def expand_bbox(b,fraction=.65):
    b=normalize_bbox(b); fraction=max(0.0,float(fraction))
    dx=(b["east"]-b["west"])*fraction; dy=(b["north"]-b["south"])*fraction
    return {"west":max(-180,b["west"]-dx),"south":max(-90,b["south"]-dy),"east":min(180,b["east"]+dx),"north":min(90,b["north"]+dy)}
def _snap(v,step,up): return (math.ceil(v/step) if up else math.floor(v/step))*step
def plan_viewport_fetch(provider,viewport,prefetch_fraction=.65):
    if provider not in DOMAINS: raise ValueError(f"unsupported provider: {provider}")
    d=DOMAINS[provider]; requested=expand_bbox(viewport,prefetch_fraction)
    clipped={"west":max(requested["west"],d["west"]),"south":max(requested["south"],d["south"]),"east":min(requested["east"],d["east"]),"north":min(requested["north"],d["north"])}
    if clipped["west"]>=clipped["east"] or clipped["south"]>=clipped["north"]:
        return {"provider":provider,"status":"outside_provider_domain","viewport":normalize_bbox(viewport),"requested_bbox":requested,"fetch_bbox":None}
    sx,sy=d["spacing"]
    fetch={"west":max(d["west"],_snap(clipped["west"],sx,False)),"south":max(d["south"],_snap(clipped["south"],sy,False)),"east":min(d["east"],_snap(clipped["east"],sx,True)),"north":min(d["north"],_snap(clipped["north"],sy,True))}
    payload={"provider":provider,"bbox":{k:round(v,6) for k,v in fetch.items()}}
    cache_key=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()[:20]
    coverage_complete=(
        fetch["west"] <= requested["west"] + 1e-9
        and fetch["south"] <= requested["south"] + 1e-9
        and fetch["east"] >= requested["east"] - 1e-9
        and fetch["north"] >= requested["north"] - 1e-9
    )
    return {"provider":provider,"status":"ready","viewport":normalize_bbox(viewport),"requested_bbox":requested,"fetch_bbox":fetch,"coverage_complete":coverage_complete,"cache_key":cache_key}
