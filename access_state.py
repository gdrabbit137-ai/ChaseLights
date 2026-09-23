"""Source-aware dynamic-access foundation for ChaseLights R4.2 B25.

This module intentionally separates *access logic* from *access data*. A
profile is not runtime-ready merely because an evaluator exists. It becomes
ready only after an authoritative provider/rule is connected for that profile.

Unknown or stale access data must never be interpreted as open.
"""

ACCESS_STATE_VERSION = "dynamic-access-foundation-r1-preview"

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
}

_ACCESS_GROUPS = {
    "event_access_control": ("tw-002-P03",),
    "public_space_live_notice": ("tw-005-P01", "tw-005-P02"),
    "trail_road_status": (
        "tw-008-P01",
        "tw-032-P01", "tw-032-P02", "tw-032-P03",
        "tw-056-P01", "tw-056-P02", "tw-057-P02",
    ),
    "managed_park_booking_notice": ("tw-010-P01", "tw-010-P03"),
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
    "transport_facility_status": ("tw-024-P01", "tw-024-P05", "tw-037-P01"),
    "road_viewpoint_status": ("tw-034-P01",),
    "public_attraction_notice": ("tw-038-P01", "tw-038-P02"),
    "waterfall_trail_status": ("tw-055-P01",),
    "tidal_path_notice": ("tw-059-P01", "tw-078-P01", "tw-078-P02"),
    "facility_hours_notice": ("tw-068-P01",),
}

ACCESS_PROFILE_CLASSIFICATION = {}
for _access_type, _profile_ids in _ACCESS_GROUPS.items():
    for _oid in _profile_ids:
        ACCESS_PROFILE_CLASSIFICATION[_oid] = {
            "access_type": _access_type,
            **ACCESS_REQUIREMENTS[_access_type],
        }

ACCESS_DEPENDENT_PROFILE_IDS = frozenset(ACCESS_PROFILE_CLASSIFICATION)

# B25 is deliberately a foundation checkpoint: provider adapters are not yet
# connected, so no dynamic-access Opportunity is allowed to become contract-ready.
ACCESS_RUNTIME_READY_PROFILES = frozenset()

# These are provider-discovery hints, not proof that an Opportunity is open.
# They document official sources verified during B25 architecture work.
OFFICIAL_SOURCE_HINTS = {
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

    checked = _number(snapshot.get("checked_at_epoch"))
    valid_until = _number(snapshot.get("valid_until_epoch"))
    effective_from = _number(snapshot.get("effective_from_epoch"))
    effective_until = _number(snapshot.get("effective_until_epoch"))
    evaluation_time = _number(item_data.get("timestamp"))
    if evaluation_time is None:
        evaluation_time = checked

    if checked is None or evaluation_time is None:
        return {
            "module": "dynamic_access",
            "available": False,
            "eligible": False,
            "reason": "access_snapshot_time_missing",
            "access_type": contract["access_type"],
            "provider_family": contract["provider_family"],
            "source_freshness_verified": False,
        }

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
        "snapshot_age_seconds": round(age),
        "source_freshness_verified": True,
        "requires_live_notice": contract["requires_live_notice"],
        "requires_user_entitlement": contract["requires_user_entitlement"],
        "runtime_provider_connected": oid in ACCESS_RUNTIME_READY_PROFILES,
    }


def validate_access_registry():
    errors = []
    if len(ACCESS_DEPENDENT_PROFILE_IDS) != 42:
        errors.append(f"expected 42 dynamic-access profiles, got {len(ACCESS_DEPENDENT_PROFILE_IDS)}")
    if ACCESS_RUNTIME_READY_PROFILES - ACCESS_DEPENDENT_PROFILE_IDS:
        errors.append("runtime-ready access profile is not classified")
    for oid, contract in ACCESS_PROFILE_CLASSIFICATION.items():
        if not oid.startswith("tw-"):
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
