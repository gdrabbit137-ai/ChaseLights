"""V2-only NOAA/NCEP GFS global cloud acquisition/publish contract."""
from __future__ import annotations
from urllib.parse import urlencode
from weathergrid_v2_gfs_global import GFS_CLOUD_FIELDS

NOMADS_FILTER_URL="https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl"
GFS_GRIB_VARS={"cloud_cover":"TCDC","cloud_cover_low":"LCDC","cloud_cover_mid":"MCDC","cloud_cover_high":"HCDC"}
GFS_GRIB_LEVELS={"cloud_cover":"entire_atmosphere","cloud_cover_low":"low_cloud_layer","cloud_cover_mid":"middle_cloud_layer","cloud_cover_high":"high_cloud_layer"}

def build_cloud_url(*, filename,directory,bbox):
    w,s,e,n=(float(bbox[k]) for k in ("west","south","east","north"))
    if not (-180<=w<e<=180 and -90<=s<n<=90):
        raise ValueError("bbox must be a non-wrapping lon/lat segment; split antimeridian first")
    params={"file":filename,"subregion":"","leftlon":w,"rightlon":e,"bottomlat":s,"toplat":n,"dir":directory}
    for field in GFS_CLOUD_FIELDS:
        params["var_"+GFS_GRIB_VARS[field]]="on"
        params["lev_"+GFS_GRIB_LEVELS[field]]="on"
    return NOMADS_FILTER_URL+"?"+urlencode(params)

def build_publish_manifest(*, reference_time_utc, valid_time_utc, cell_results):
    complete=[]
    for item in cell_results:
        fields=set(item.get("published_fields",()))
        if set(GFS_CLOUD_FIELDS).issubset(fields) and item.get("tile_path"):
            complete.append(item["cell_id"])
    return {"schema_version":1,"provider":"gfs","model":"GFS_0p25","reference_time_utc":reference_time_utc,
      "valid_time_utc":valid_time_utc,"supported_fields":list(GFS_CLOUD_FIELDS),
      "published_cell_ids":sorted(set(complete)),"coverage_complete":False,
      "tile_url_template":"weathergrid/v2/gfs/current/{valid_time}/{cell_id}.json"}
