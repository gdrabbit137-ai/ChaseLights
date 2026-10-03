"""Build native-provider WeatherGrid V2 requests from a map viewport.

This module is isolated from production WeatherGrid. It reuses the existing
JMA MSM AWS OM and GFS NOMADS adapters rather than the browser API prototype.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from weathergrid_viewport_fetch import plan_viewport_fetch

def adapter_bbox(plan):
    b=plan["fetch_bbox"]
    if not b: return None
    return {"leftlon":b["west"],"bottomlat":b["south"],"rightlon":b["east"],"toplat":b["north"]}

def build_native_request(provider, viewport, prefetch_fraction=.65, forecast_hour=0):
    plan=plan_viewport_fetch(provider,viewport,prefetch_fraction)
    out={"schema_version":1,"mode":"weathergrid_v2_native_viewport","plan":plan,"adapter_bbox":adapter_bbox(plan)}
    if plan["status"]!="ready": return out
    if provider=="jma":
        out["transport"]={"adapter":"jma_msm_aws_om.fetch_aws_snapshot","model":"JMA MSM","native_grid":True,"forecast_hours":max(1,int(forecast_hour)+1)}
    elif provider=="gfs":
        # Keep dry planning cycle-independent here; the existing
        # gfs_multilayer_poc downloader resolves candidate cycles at execution time.
        out["transport"]={"adapter":"gfs_multilayer_poc.download_multilayer_grib","model":"GFS","native_grid":True,"forecast_hour":int(forecast_hour),"bbox_query":adapter_bbox(plan)}
    return out

def execute_jma(request, forecast_hours=1):
    if request["plan"]["provider"]!="jma" or request["plan"]["status"]!="ready":
        raise ValueError("ready JMA request required")
    from jma_msm_aws_om import fetch_aws_snapshot
    return fetch_aws_snapshot(bbox=request["adapter_bbox"],forecast_hours=forecast_hours)

def parse_bbox(value):
    vals=[float(x) for x in value.split(",")]
    if len(vals)!=4: raise argparse.ArgumentTypeError("bbox must be west,south,east,north")
    return dict(zip(("west","south","east","north"),vals))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--provider",choices=("jma","gfs"),required=True)
    p.add_argument("--bbox",type=parse_bbox,required=True)
    p.add_argument("--prefetch-fraction",type=float,default=.65)
    p.add_argument("--forecast-hour",type=int,default=0)
    p.add_argument("--output")
    p.add_argument("--execute-jma",action="store_true")
    a=p.parse_args()
    request=build_native_request(a.provider,a.bbox,a.prefetch_fraction,a.forecast_hour)
    payload={"request":request}
    if a.execute_jma:
        payload["snapshot"]=execute_jma(request,max(1,a.forecast_hour+1))
    text=json.dumps(payload,ensure_ascii=False,indent=2)
    if a.output: Path(a.output).write_text(text,encoding="utf-8")
    print(text)
if __name__=="__main__": main()
