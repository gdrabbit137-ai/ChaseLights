"""Source-aware dynamic-access foundation for ChaseLights R4.2 B25.

This module intentionally separates *access logic* from *access data*. A
profile is not runtime-ready merely because an evaluator exists. It becomes
ready only after an authoritative provider/rule is connected for that profile.

Unknown or stale access data must never be interpreted as open.
"""

ACCESS_STATE_VERSION = "dynamic-access-foundation-r5-denali-mountain-vista-preview"

ACCESS_REQUIREMENTS = {
    "event_access_control": {
        "provider_family": "official_event_and_crowd_notice",
        "max_snapshot_age_seconds": 6 * 3600,
        "requires_live_notice": True,
        "requires_user_entitlement": False,
    },
    "public_space_live_notice": {
        "provider_family": "municipal_public_space_notice",
        "max_snapshot_age_seconds": 6 * 3600,
        "requires_live_notice": True,
        "requires_user_entitlement": False,
    },
    "trail_road_status": {
        "provider_family": "official_trail_and_road_status",
        "max_snapshot_age_seconds": 6 * 3600,
        "requires_live_notice": True,
        "requires_user_entitlement": False,
    },
    "managed_park_booking_notice": {
        "provider_family": "official_booking_and_closure_status",
        "max_snapshot_age_seconds": 6 * 3600,
        "requires_live_notice": True,
        "requires_user_entitlement": True,
    },
    "boardwalk_schedule_notice": {
        "provider_family": "official_schedule_and_closure_notice",
        "max_snapshot_age_seconds": 12 * 3600,
        "requires_live_notice": True,
        "requires_user_entitlement": False,
    },
    "private_property_permission": {
        "provider_family": "owner_permission",
        "max_snapshot_age_seconds": 24 * 3600,
        "requires_live_notice": False,
        "requires_user_entitlement": True,
    },
    "mountain_permit_trail_status": {
        "provider_family": "permit_plus_trail_closure_status",
        "max_snapshot_age_seconds": 6 * 3600,
        "requires_live_notice": True,
        "requires_user_entitlement": True,
    },
    "transport_facility_status": {
        "provider_family": "transport_and_facility_status",
        "max_snapshot_age_seconds": 6 * 3600,
        "requires_live_notice": True,
        "requires_user_entitlement": False,
    },
    "road_viewpoint_status": {
        "provider_family": "road_and_viewpoint_notice",
        "max_snapshot_age_seconds": 6 * 3600,
        "requires_live_notice": True,
        "requires_user_entitlement": False,
    },
    "public_attraction_notice": {
        "provider_family": "official_attraction_hours_and_notice",
        "max_snapshot_age_seconds": 12 * 3600,
        "requires_live_notice": True,
        "requires_user_entitlement": False,
    },
    "waterfall_trail_status": {
        "provider_family": "official_trail_and_waterfall_access_notice",
        "max_snapshot_age_seconds": 6 * 3600,
        "requires_live_notice": True,
        "requires_user_entitlement": False,
    },
    "tidal_path_notice": {
        "provider_family": "official_tidal_path_notice",
        "max_snapshot_age_seconds": 6 * 3600,
        "requires_live_notice": True,
        "requires_user_entitlement": False,
    },
    "facility_hours_notice": {
        "provider_family": "official_facility_hours_and_notice",
        "max_snapshot_age_seconds": 12 * 3600,
        "requires_live_notice": True,
        "requires_user_entitlement": False,
    },
    "managed_boat_operation": {
        "provider_family": "official_managed_boat_operation",
        "max_snapshot_age_seconds": 6 * 3600,
        "requires_live_notice": True,
        "requires_user_entitlement": True,
    },
}

_ACCESS_GROUPS = {
    "event_access_control": ("tw-002-P03", "jp-021-P02", "jp-022-P03"),
    "public_space_live_notice": ("tw-005-P01", "tw-005-P02"),
    "trail_road_status": (
        "tw-008-P01",
        "tw-032-P01", "tw-032-P02", "tw-032-P03",
        "tw-056-P01", "tw-056-P02", "tw-057-P02",
    ),
    "managed_park_booking_notice": ("tw-010-P01", "tw-010-P03", "us-003-P01", "us-003-P02", "us-031-P01"),
    "boardwalk_schedule_notice": ("tw-012-P02", "tw-015-P02"),
    "private_property_permission": (
        "tw-014-P01", "tw-014-P02",
        "tw-021-P01", "tw-021-P02",
    ),
    "mountain_permit_trail_status": (
        "tw-019-P01", "tw-019-P02", "tw-019-P05",
        "tw-040-P01", "tw-040-P05", "tw-040-P06",
        "tw-041-P02", "tw-041-P04",
        "tw-043-P04",
        "tw-045-P01", "tw-045-P03", "tw-045-P04",
        "tw-049-P02",
    ),
    "transport_facility_status": ("tw-024-P01", "tw-024-P05", "tw-037-P01", "jp-002-P01", "jp-004-P01", "jp-021-P01", "jp-022-P01", "jp-022-P02", "us-048-P02", "us-060-P02", "us-064-P01", "us-066-P01", "us-066-P02", "us-068-P01", "us-068-P02"),
    "road_viewpoint_status": ("tw-034-P01", "us-012-P01", "us-012-P02", "us-013-P02", "us-017-P01", "us-038-P01", "us-041-P01", "us-041-P02", "us-046-P01", "us-046-P02", "us-055-P01", "us-055-P02", "us-056-P01", "us-056-P02", "us-057-P01", "us-057-P02", "us-067-P01", "us-070-P01"),
    "public_attraction_notice": ("tw-038-P01", "tw-038-P02", "tw-081-P01", "jp-030-P01", "jp-034-P02", "us-010-P01", "us-027-P01", "us-029-P01", "us-047-P01", "us-059-P01", "us-059-P02"),
    "waterfall_trail_status": ("tw-055-P01",),
    "tidal_path_notice": ("tw-059-P01", "tw-078-P01"),
    "facility_hours_notice": ("tw-068-P01", "jp-033-P02", "us-024-P02", "us-050-P02"),
    "managed_boat_operation": ("jp-036-P03",),
}

ACCESS_PROFILE_CLASSIFICATION = {}
for _access_type, _profile_ids in _ACCESS_GROUPS.items():
    for _oid in _profile_ids:
        ACCESS_PROFILE_CLASSIFICATION[_oid] = {
            "access_type": _access_type,
            **ACCESS_REQUIREMENTS[_access_type],
        }

ACCESS_DEPENDENT_PROFILE_IDS = frozenset(ACCESS_PROFILE_CLASSIFICATION)

# Runtime-ready is explicit and profile-specific. us-017, us-041, jp-021 and
# jp-022 have authoritative fail-closed providers connected; all other
# access-dependent profiles remain blocked until their own provider is implemented.
ACCESS_RUNTIME_READY_PROFILES = frozenset({
    "us-017-P01",
    "us-041-P01",
    "us-041-P02",
    "jp-021-P01",
    "jp-021-P02",
    "jp-022-P01",
    "jp-022-P02",
    "jp-022-P03",
})

# These are provider-discovery hints, not proof that an Opportunity is open.
# They document official sources verified during B25 architecture work.
OFFICIAL_SOURCE_HINTS = {
    "jp-036": {
        "authority": "Takachiho Tourism Association",
        "source_kind": "takachiho_gorge_rental_boat_daily_operation",
        "url": "https://takachiho-kanko.info/boat/",
        "verified_on": "2026-10-02",
        "note": "The official operator publishes rental-boat operating state and notices. Weather alone must never imply the boat route is operating; provider integration remains pending and therefore fails closed.",
    },
    "us-070": {
        "authority": "Alaska Division of Parks and Outdoor Recreation",
        "source_kind": "independence_mine_hatcher_pass_current_road_trail_access",
        "url": "https://dnr.alaska.gov/parks/asp/curevnts.htm",
        "verified_on": "2026-09-27",
        "note": "Independence Mine pedestrian access and vehicle access differ by gate/season, while Hatcher Pass road, snow and avalanche conditions change dynamically. Favorable photography weather must not imply safe current access.",
    },
    "us-068": {
        "authority": "U.S. National Park Service",
        "source_kind": "noatak_remote_air_taxi_and_river_trip_access",
        "url": "https://home.nps.gov/noat/planyourvisit/floating.htm",
        "verified_on": "2026-09-27",
        "note": "Noatak River trips are remote and primarily accessed by air taxi, with no facilities or services once visitors depart. A representative weather coordinate must not be interpreted as an airstrip or guaranteed transport state.",
    },
    "us-067": {
        "authority": "Bureau of Land Management",
        "source_kind": "dalton_highway_yukon_crossing_current_road_access",
        "url": "https://www.blm.gov/office/central-yukon-field-office",
        "verified_on": "2026-09-27",
        "note": "Yukon Crossing is at Dalton Highway mile 56. Current road, ice, construction and remote-driving conditions remain independent of favorable visibility at the river.",
    },
    "us-066": {
        "authority": "U.S. National Park Service",
        "source_kind": "serpentine_hot_springs_remote_transport_access",
        "url": "https://www.nps.gov/bela/planyourvisit/shs_travel.htm",
        "verified_on": "2026-09-27",
        "note": "There are no roads into Bering Land Bridge. Serpentine is usually reached by air taxi or small plane, and the unmaintained airstrip plus weather/transport state must be checked independently of photography conditions.",
    },
    "us-064": {
        "authority": "Alyeska Resort",
        "source_kind": "alyeska_aerial_tram_current_operation",
        "url": "https://www.alyeskaresort.com/aerial-tram-summer/",
        "verified_on": "2026-09-27",
        "note": "Mountain Station photography depends on current Aerial Tram operation, maintenance and public observation-area access. Favorable visibility or a static seasonal schedule must not imply the upper Camera Zone is reachable.",
    },
    "us-060": {
        "authority": "U.S. National Park Service",
        "source_kind": "glacier_bay_day_tour_current_operation",
        "url": "https://www.nps.gov/glba/planyourvisit/tour.htm",
        "verified_on": "2026-09-27",
        "note": "NPS documents a summer day tour boat from Bartlett Cove to tidewater glaciers. Current operating day, departure, seat availability and weather cancellation state must not be inferred from the static seasonal description.",
    },
    "us-059": {
        "authority": "U.S. National Park Service",
        "source_kind": "brooks_falls_platform_current_access_and_bear_activity",
        "url": "https://www.nps.gov/places/brooks-falls-platform.htm",
        "verified_on": "2026-09-27",
        "note": "Brooks Falls viewing has capacity, seasonal nighttime closure, tripod and ranger-management rules. Bear presence also varies strongly by date. Static month tags must not imply platform access or an active bear subject.",
    },
    "us-057": {
        "authority": "Bureau of Land Management",
        "source_kind": "dalton_highway_arctic_circle_current_road_access",
        "url": "https://www.blm.gov/learn/interpretive-centers/arctic-interagency-visitor-center/frequently-asked-questions",
        "verified_on": "2026-09-27",
        "note": "The Dalton Highway is open through winter but conditions can become extremely challenging. Current Alaska 511 road conditions must remain independent of a favorable weather or aurora forecast.",
    },
    "us-056": {
        "authority": "Bureau of Land Management",
        "source_kind": "dalton_highway_atigun_pass_current_road_access",
        "url": "https://www.blm.gov/visit/atigun-pass",
        "verified_on": "2026-09-27",
        "note": "Atigun Pass is a remote Dalton Highway Camera Zone. Current road, construction, ice and blowing-snow conditions must be checked independently of visibility or aurora conditions.",
    },
    "us-055": {
        "authority": "U.S. National Park Service",
        "source_kind": "wrst_mccarthy_road_kennecott_root_glacier_current_access",
        "url": "https://www.nps.gov/wrst/planyourvisit/directions-mccarthy-rd-and-kennecott.htm",
        "verified_on": "2026-09-27",
        "note": "Kennecott requires remote McCarthy Road access plus walking/biking/shuttle beyond the Kennicott River bridge; Root Glacier access was rerouted in 2026 after a landslide hazard. Current road, transport, trail and closure state must be checked independently of favorable weather.",
    },
    "us-050": {
        "authority": "Goldbelt Tram",
        "source_kind": "goldbelt_tram_current_operating_status",
        "url": "https://www.goldbelttram.com/",
        "verified_on": "2026-09-27",
        "note": "The operator currently reports the tram temporarily closed while assessments continue. Static seasonal hours or favorable weather must not imply the upper panorama Camera Zone is reachable.",
    },
    "us-048": {
        "authority": "U.S. Forest Service",
        "source_kind": "portage_glacier_cruise_current_operation",
        "url": "https://www.fs.usda.gov/Internet/FSE_DOCUMENTS/fseprd1101873.pdf",
        "verified_on": "2026-09-27",
        "note": "The MV Ptarmigan is a managed seasonal transport-dependent way to view Portage Glacier. A published season or old timetable must not imply a current departure exists.",
    },
    "us-047": {
        "authority": "Alaska Division of Parks and Outdoor Recreation",
        "source_kind": "matanuska_glacier_srs_current_access",
        "url": "https://dnr.alaska.gov/parks/aspunits/matsu/matsuglsrs.htm",
        "verified_on": "2026-09-27",
        "note": "The public glacier-viewing recreation site remains distinct from private/guided glacier access and may close because of winter snow and ice. Favorable forecast weather must not override a closure.",
    },
    "us-046": {
        "authority": "Alaska Division of Parks and Outdoor Recreation",
        "source_kind": "hatcher_pass_summit_road_current_access",
        "url": "https://dnr.alaska.gov/parks/aspunits/matsu/hatcherpassema.htm",
        "verified_on": "2026-09-27",
        "note": "The summit road is seasonal and not maintained/open in winter; current road and public-parking access must be checked independently for both Summit Lake and winter aurora use.",
    },
    "us-041": {
        "authority": "U.S. National Park Service",
        "source_kind": "denali_current_park_road_conditions",
        "url": "https://www.nps.gov/dena/planyourvisit/conditions.htm",
        "verified_on": "2026-09-28",
        "note": "B91 connects the official Denali Current Conditions page as a fail-closed provider for Mountain Vista. Explicit current road-open language reaching/passing Mile 13 can prove short-lived access; an explicit closure at/before Park Headquarters blocks it. Closures farther west such as Mile 43 do not by themselves block the Mountain Vista Camera Zone. Favorable weather or aurora never proves access.",
    },
    "us-038": {
        "authority": "U.S. National Park Service",
        "source_kind": "newfound_gap_road_and_overlook_current_status",
        "url": "https://www.nps.gov/grsm/planyourvisit/temproadclose.htm",
        "verified_on": "2026-09-27",
        "note": "Newfound Gap Road / US 441 is normally year-round but weather permitting and may close for snow, ice, high wind or other hazards. Favorable forecast weather must not be treated as proof that Newfound Gap Overlook is currently reachable.",
    },
    "us-031": {
        "authority": "U.S. National Park Service",
        "source_kind": "rmnp_2026_timed_entry_plus_bear_lake_road",
        "url": "https://www.nps.gov/places/rmnp-timed-entry-%2B-bear-lake-road.htm",
        "verified_on": "2026-09-27",
        "note": "Sprague Lake is inside the Bear Lake Road Corridor. In 2026, Timed Entry + Bear Lake Road reservations are required 05:00–18:00 from May 22 through October 18. Reservation entitlement, current road/park status, and time window must not be inferred from favorable weather.",
    },
    "us-029": {
        "authority": "U.S. National Park Service",
        "source_kind": "white_sands_park_hours_and_missile_test_closure_status",
        "url": "https://www.nps.gov/whsa/planyourvisit/park-closures.htm",
        "verified_on": "2026-09-27",
        "note": "Dunes Drive can close for missile testing and other safety reasons, while ordinary park closing time varies with local sunset. Favorable weather, month, or a static hours table must not imply the dune Camera Zone is currently accessible.",
    },
    "us-027": {
        "authority": "USDA Forest Service / Recreation.gov",
        "source_kind": "redfish_lake_north_shore_day_use_opening_status",
        "url": "https://www.recreation.gov/camping/campgrounds/232076",
        "verified_on": "2026-09-27",
        "note": "North Shore is a public Redfish Lake day-use Camera Zone, but Recreation.gov states opening and closing dates are weather permitting. Do not infer access from calendar month or favorable forecast.",
    },
    "us-024": {
        "authority": "Space Needle official",
        "source_kind": "official_date_specific_ticketed_attraction_hours",
        "url": "https://www.spaceneedle.com/plan-your-visit",
        "verified_on": "2026-09-27",
        "note": "Observation-level access is ticketed and official hours vary by day/date. Exterior Seattle Center photography is a separate non-ticketed Opportunity; do not infer tower admission from favorable weather.",
    },
    "us-017": {
        "authority": "Washington State Department of Transportation / USDA Forest Service",
        "source_kind": "johnston_ridge_sr504_road_and_viewpoint_status",
        "url": "https://wsdot.wa.gov/construction-planning/search-projects/sr-504-south-coldwater-slide-spirit-lake-outlet-bridge-washout",
        "verified_on": "2026-09-28",
        "note": "B90 connects the current WSDOT SR 504 project page as a fail-closed provider. Explicit long-term closure can prove CLOSED across the forecast horizon; a future OPEN result requires fresh present-tense reopening language. Favorable weather never proves Johnston Ridge access.",
    },
    "us-012": {
        "authority": "U.S. National Park Service",
        "source_kind": "mount_rainier_seasonal_road_and_viewpoint_status",
        "url": "https://www.nps.gov/mora/planyourvisit/road-status.htm",
        "verified_on": "2026-09-27",
        "note": "Reflection Lakes / Tipsoo access depends on seasonal road and trail status. Do not infer access from calendar month alone.",
    },
    "us-013": {
        "authority": "U.S. National Park Service",
        "source_kind": "crater_lake_current_conditions_and_rim_drive_status",
        "url": "https://www.nps.gov/crla/planyourvisit/conditions.htm",
        "verified_on": "2026-09-27",
        "note": "Watchman Peak sunset access depends on current West Rim Drive and trail status; the park being open does not prove this specific Camera Zone is reachable.",
    },
    "us-010": {
        "authority": "U.S. National Park Service",
        "source_kind": "grand_prismatic_overlook_trail_and_road_status",
        "url": "https://www.nps.gov/thingstodo/yell-trail-grand-prismatic-overlook.htm",
        "notes": "Overlook access depends on current Yellowstone road/trail status; off-trail travel is prohibited.",
    },
    "us-003": {
        "authority": "Navajo Nation Parks & Recreation",
        "source_kind": "mandatory_guided_tour_and_authorized_operator_access",
        "url": "https://navajonationparks.org/guided-tour-operators/antelope-canyon-tour-operators/",
        "verified_on": "2026-09-27",
        "note": "All Antelope Canyon access requires a guided tour. Do not treat daylight or favorable weather as proof that a tour slot is available.",
    },
    "jp-002": {
        "authority": "Daisetsuzan Asahidake Ropeway",
        "source_kind": "official_ropeway_operation_and_mountain_condition_information",
        "url": "https://asahidake.hokkaido.jp/en/",
        "verified_on": "2026-09-24",
        "note": "Sugatami photography access for ordinary visitors depends on current ropeway operation and mountain conditions; do not infer access from a static annual timetable alone.",
    },
    "jp-004": {
        "authority": "Hakodate City / Travel Hakodate",
        "source_kind": "official_ropeway_road_and_summit_access_information",
        "url": "https://www.hakodate.travel/en/information/mt-hakodate/",
        "verified_on": "2026-09-24",
        "note": "Summit access is multi-modal. Ropeway hours, autumn maintenance, private-car evening restrictions, winter road closure, buses/taxis and hiking must not be collapsed into one static open/closed window.",
    },
    "jp-021": {
        "authority": "Shinhotaka Ropeway",
        "source_kind": "official_ropeway_operation_status_plus_annual_stargazing_schedule",
        "url": "https://shinhotaka-ropeway.jp/en/",
        "verified_on": "2026-09-25",
        "note": "Daytime summit access depends on actual ropeway operation. Night photography is not ordinary after-hours access: jp-021-P02 is valid only on the official annual Stargazing Service dates and while the special No.2 Ropeway service is operating.",
    },
    "jp-022": {
        "authority": "Niigata Prefecture Tourism / Yahiko Tourism Association / Yahikoyama Ropeway",
        "source_kind": "official_multi_route_summit_access_plus_annual_night_cruise_schedule",
        "url": "https://niigata-kankou.or.jp/spot/7462",
        "verified_on": "2026-09-25",
        "note": "Summit access is multi-modal: ropeway, seasonal Skyline road and walking routes have different constraints. 2026 night-view access is date-limited special ropeway service, so ordinary clear nights must not be inferred accessible.",
    },
    "jp-033": {
        "authority": "Karatsu Tourism Association",
        "source_kind": "official_castle_hours_and_facility_information",
        "url": "https://www.karatsu-kankou.jp/spots/detail/181/",
        "verified_on": "2026-09-27",
        "note": "Karatsu Castle keep is currently listed 09:00–17:00 with last admission 16:40 and may vary seasonally; Maizuru Park exterior access is a separate contract.",
    },
    "jp-034": {
        "authority": "Glover Garden official",
        "source_kind": "official_2026_opening_schedule_and_night_event_notice",
        "url": "https://glover-garden.jp/guide/",
        "verified_on": "2026-09-27",
        "note": "Glover Garden opening hours vary by 2026 date range and private-event/weather changes. Night photography must use current official schedule rather than a permanent generic night-open assumption.",
    },
    "jp-030": {
        "authority": "Naruto City Uzushio Tourism Association / Uzu-no-Michi",
        "source_kind": "official_tide_extremum_calendar_plus_attraction_hours_and_notice",
        "url": "https://www.naruto-kankou.jp/uzu/",
        "verified_on": "2026-09-27",
        "note": "Whirlpool strength is tied to official high/low-tide viewing windows and actual Uzu-no-Michi operation. Generic relative sea-level percentile must not substitute for local tidal-current extremum data.",
    },
    "tw-081": {
        "authority": "Matsu National Scenic Area Headquarters",
        "source_kind": "official_attraction_hours_plus_weather_control",
        "url": "https://www.matsu-nsa.gov.tw/zh-TW/attractions/1474",
        "verified_on": "2026-09-24",
        "note": "Iron Fort is currently listed 08:00–17:00 daily and may close during strong winds or long-period waves; night access must not be assumed.",
    },
    "tw-005": {
        "authority": "Taipei City Government",
        "source_kind": "municipal_event_and_traffic_notice",
        "url": "https://www.gov.taipei/News_Content.aspx?n=F0DDAF49B89E9413&s=5E6EB419E9EFF9AE",
        "verified_on": "2026-09-23",
        "note": "Dadaocheng access can be temporarily controlled for large events.",
    },
    "tw-037": {
        "authority": "Taitung County Government Tourism Department",
        "source_kind": "official_attraction_page_plus_closure_news",
        "url": "https://tour.taitung.gov.tw/zh-tw/tour/details/885",
        "verified_on": "2026-09-23",
        "note": "Static all-day listing is insufficient by itself because official closure notices also occur.",
    },
    "tw-078": {
        "authority": "Kinmen County Government Tourism Department",
        "source_kind": "official_tidal_path_schedule_and_live_camera",
        "url": "https://kinmen.travel/zh-tw/live-camera/1",
        "verified_on": "2026-09-24",
        "note": "Jiangong Islet causeway access follows official tide-specific recommended island windows; generic tide percentile must not substitute for the official access window.",
    },
    "tw-038": {
        "authority": "East Coast National Scenic Area Headquarters",
        "source_kind": "official_attraction_page_plus_construction_notice",
        "url": "https://www.eastcoast-nsa.gov.tw/zh-tw/attractions/detail/41/",
        "verified_on": "2026-09-23",
        "note": "Attraction page lists all-day opening while separately carrying bridge-construction closure information.",
    },
}

HARD_ACCESS_HOLDS = {
    "tw-052": {
        "reason": "construction_closure",
        "policy": "hold",
        "rule": "Do not auto-clear until an official reopening notice is verified.",
    }
}


def access_contract_for_opportunity(opportunity):
    return ACCESS_PROFILE_CLASSIFICATION.get(opportunity.get("opportunity_id"))


def supports_dynamic_access(opportunity):
    """Return True only after an authoritative provider/rule is connected."""
    return opportunity.get("opportunity_id") in ACCESS_RUNTIME_READY_PROFILES


def _snapshot_for_opportunity(opportunity, item_data):
    state = item_data.get("access_state")
    if not isinstance(state, dict):
        return None

    oid = opportunity.get("opportunity_id")
    spot_id = opportunity.get("spot_id") or (oid.split("-P")[0] if oid else None)

    # A direct snapshot is accepted when it itself carries a status.
    if state.get("status") is not None:
        return state
    if oid in state and isinstance(state[oid], dict):
        return state[oid]
    if spot_id in state and isinstance(state[spot_id], dict):
        return state[spot_id]
    return None


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def evaluate_dynamic_access(opportunity, item_data):
    """Evaluate an authoritative access snapshot without assuming unknown=open."""
    oid = opportunity.get("opportunity_id")
    contract = ACCESS_PROFILE_CLASSIFICATION.get(oid)
    if not contract:
        return {
            "module": "dynamic_access",
            "available": False,
            "eligible": False,
            "reason": "opportunity_access_classification_missing",
            "source_freshness_verified": False,
        }

    snapshot = _snapshot_for_opportunity(opportunity, item_data)
    if not snapshot:
        return {
            "module": "dynamic_access",
            "available": False,
            "eligible": False,
            "reason": "authoritative_access_snapshot_missing",
            "access_type": contract["access_type"],
            "provider_family": contract["provider_family"],
            "source_freshness_verified": False,
        }

    if snapshot.get("authoritative") is not True:
        return {
            "module": "dynamic_access",
            "available": False,
            "eligible": False,
            "reason": "access_source_not_authoritative",
            "access_type": contract["access_type"],
            "provider_family": contract["provider_family"],
            "source_freshness_verified": False,
        }

    if not snapshot.get("authority") or not snapshot.get("source_url"):
        return {
            "module": "dynamic_access",
            "available": False,
            "eligible": False,
            "reason": "access_source_identity_missing",
            "access_type": contract["access_type"],
            "provider_family": contract["provider_family"],
            "source_freshness_verified": False,
        }

    freshness_mode = str(snapshot.get("freshness_mode") or "live").lower()
    if freshness_mode not in {"live", "schedule"}:
        return {
            "module": "dynamic_access",
            "available": False,
            "eligible": False,
            "reason": "invalid_access_freshness_mode",
            "source_freshness_verified": False,
        }

    checked = _number(snapshot.get("checked_at_epoch"))
    valid_until = _number(snapshot.get("valid_until_epoch"))
    effective_from = _number(snapshot.get("effective_from_epoch"))
    effective_until = _number(snapshot.get("effective_until_epoch"))
    evaluation_time = _number(item_data.get("timestamp"))
    if evaluation_time is None:
        evaluation_time = checked

    if evaluation_time is None or (freshness_mode == "live" and checked is None):
        return {
            "module": "dynamic_access",
            "available": False,
            "eligible": False,
            "reason": "access_snapshot_time_missing",
            "access_type": contract["access_type"],
            "provider_family": contract["provider_family"],
            "source_freshness_verified": False,
        }

    age = None
    if freshness_mode == "live":
        age = evaluation_time - checked
        if age < -300:
            return {
                "module": "dynamic_access",
                "available": False,
                "eligible": False,
                "reason": "access_snapshot_from_future",
                "source_freshness_verified": False,
            }

        if age > float(contract["max_snapshot_age_seconds"]):
            return {
                "module": "dynamic_access",
                "available": False,
                "eligible": False,
                "reason": "access_snapshot_stale",
                "snapshot_age_seconds": round(age),
                "max_snapshot_age_seconds": contract["max_snapshot_age_seconds"],
                "source_freshness_verified": False,
            }

    if valid_until is not None and evaluation_time > valid_until:
        return {
            "module": "dynamic_access",
            "available": False,
            "eligible": False,
            "reason": "access_snapshot_expired",
            "source_freshness_verified": False,
        }
    if effective_from is not None and evaluation_time < effective_from:
        return {
            "module": "dynamic_access",
            "available": False,
            "eligible": False,
            "reason": "access_state_not_yet_effective",
            "source_freshness_verified": True,
        }
    if effective_until is not None and evaluation_time > effective_until:
        return {
            "module": "dynamic_access",
            "available": False,
            "eligible": False,
            "reason": "access_state_effective_window_expired",
            "source_freshness_verified": False,
        }

    status = str(snapshot.get("status") or "unknown").lower()
    if status not in {"open", "closed", "restricted", "unknown"}:
        return {
            "module": "dynamic_access",
            "available": False,
            "eligible": False,
            "reason": "invalid_access_status",
            "source_freshness_verified": True,
        }

    if status == "unknown":
        return {
            "module": "dynamic_access",
            "available": True,
            "eligible": False,
            "reason": "authoritative_source_status_unknown",
            "status": status,
            "freshness_mode": freshness_mode,
            "status_basis": snapshot.get("status_basis"),
            "source_freshness_verified": True,
        }

    # Static timetables / annual event calendars can authoritatively prove that
    # access is closed, but they must never be used as proof that a live-notice
    # facility is actually open.
    if freshness_mode == "schedule" and status == "open" and contract["requires_live_notice"]:
        return {
            "module": "dynamic_access",
            "available": True,
            "eligible": False,
            "reason": "live_access_confirmation_required",
            "status": status,
            "freshness_mode": freshness_mode,
            "status_basis": snapshot.get("status_basis"),
            "source_freshness_verified": True,
        }

    if contract["requires_user_entitlement"] and snapshot.get("entitlement_confirmed") is not True:
        return {
            "module": "dynamic_access",
            "available": True,
            "eligible": False,
            "reason": "permit_booking_or_permission_unconfirmed",
            "status": status,
            "source_freshness_verified": True,
            "requires_user_entitlement": True,
        }

    eligible = status == "open"
    return {
        "module": "dynamic_access",
        "available": True,
        "eligible": eligible,
        "reason": "authoritative_access_open" if eligible else "authoritative_access_not_open",
        "status": status,
        "access_type": contract["access_type"],
        "provider_family": contract["provider_family"],
        "authority": snapshot.get("authority"),
        "source_url": snapshot.get("source_url"),
        "source_kind": snapshot.get("source_kind"),
        "freshness_mode": freshness_mode,
        "status_basis": snapshot.get("status_basis"),
        "snapshot_age_seconds": round(age) if age is not None else None,
        "source_freshness_verified": True,
        "requires_live_notice": contract["requires_live_notice"],
        "requires_user_entitlement": contract["requires_user_entitlement"],
        "runtime_provider_connected": oid in ACCESS_RUNTIME_READY_PROFILES,
    }


def validate_access_registry():
    errors = []
    declared_profile_ids = [
        oid
        for profile_ids in _ACCESS_GROUPS.values()
        for oid in profile_ids
    ]
    if len(declared_profile_ids) != len(set(declared_profile_ids)):
        errors.append("duplicate Opportunity id across access classification groups")
    if set(declared_profile_ids) != set(ACCESS_DEPENDENT_PROFILE_IDS):
        errors.append("access classification build mismatch")
    if ACCESS_RUNTIME_READY_PROFILES - ACCESS_DEPENDENT_PROFILE_IDS:
        errors.append("runtime-ready access profile is not classified")
    for oid, contract in ACCESS_PROFILE_CLASSIFICATION.items():
        if not oid.startswith(("tw-", "jp-", "us-")):
            errors.append(f"{oid}: invalid Opportunity id")
        if contract["access_type"] not in ACCESS_REQUIREMENTS:
            errors.append(f"{oid}: unknown access type")
        if contract["max_snapshot_age_seconds"] <= 0:
            errors.append(f"{oid}: invalid freshness window")
    if HARD_ACCESS_HOLDS.get("tw-052", {}).get("policy") != "hold":
        errors.append("tw-052 hard access hold invariant missing")
    return errors


_ERRORS = validate_access_registry()
if _ERRORS:
    raise ValueError("Invalid dynamic-access registry: " + "; ".join(_ERRORS))
