from weathergrid_viewport_fetch import expand_bbox, plan_viewport_fetch

def test_jma_viewport_plan_expands_and_snaps():
    p=plan_viewport_fetch("jma",{"west":121,"south":23,"east":122,"north":24},.5)
    assert p["status"]=="ready"
    assert p["fetch_bbox"]["west"] <= 120.5
    assert p["fetch_bbox"]["east"] >= 122.5
    assert p["cache_key"]

def test_jma_plan_clips_native_domain():
    p=plan_viewport_fetch("jma",{"west":119.5,"south":22.0,"east":121,"north":23},.2)
    assert p["status"]=="ready"
    assert p["fetch_bbox"]["west"]==120.0
    assert p["fetch_bbox"]["south"]==22.4
    assert p["coverage_complete"] is False

def test_jma_outside_domain_is_explicit():
    p=plan_viewport_fetch("jma",{"west":100,"south":10,"east":101,"north":11})
    assert p["status"]=="outside_provider_domain"
    assert p["fetch_bbox"] is None

def test_cache_key_is_stable():
    b={"west":121,"south":23,"east":122,"north":24}
    assert plan_viewport_fetch("gfs",b)["cache_key"]==plan_viewport_fetch("gfs",b)["cache_key"]
