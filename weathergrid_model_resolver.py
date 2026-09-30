"""Cloud-model selection rules for ChaseLights WeatherGrid.

ICON Global is the preferred global cloud model while a matching forecast frame
exists. GFS remains the fallback and extends the long-range horizon.

This module is intentionally network-free so provider selection can be tested
without contacting DWD or NOAA.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

ICON_CYCLES = (0, 6, 12, 18)
ICON_HORIZON_HOURS = {0: 180, 6: 120, 12: 180, 18: 120}
ICON_HOURLY_THROUGH = 78
GFS_HORIZON_HOURS = 384


@dataclass(frozen=True)
class CloudModelRun:
    provider: str
    model: str
    cycle_time_utc: datetime
    forecast_hour: int
    native_resolution_km: float
    native_grid: str

    @property
    def valid_time_utc(self) -> datetime:
        return self.cycle_time_utc + timedelta(hours=self.forecast_hour)

    @property
    def cycle(self) -> str:
        return f"{self.cycle_time_utc:%H}"

    @property
    def date(self) -> str:
        return f"{self.cycle_time_utc:%Y%m%d}"


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _floor_cycle(value: datetime, cadence_hours: int = 6) -> datetime:
    value = _as_utc(value)
    hour = (value.hour // cadence_hours) * cadence_hours
    return value.replace(hour=hour, minute=0, second=0, microsecond=0)


def icon_horizon_hours(cycle_hour: int) -> int:
    hour = int(cycle_hour)
    if hour not in ICON_HORIZON_HOURS:
        raise ValueError(f"ICON cycle must be one of 00/06/12/18, got {hour:02d}")
    return ICON_HORIZON_HOURS[hour]


def icon_forecast_hour_is_published(forecast_hour: int) -> bool:
    """Return whether the standard ICON global schedule has this lead time."""
    fh = int(forecast_hour)
    if fh < 0:
        return False
    if fh <= ICON_HOURLY_THROUGH:
        return True
    return fh % 3 == 0


def candidate_icon_cycles(
    now: datetime | None = None,
    *,
    publication_lag_hours: int = 4,
    count: int = 8,
) -> list[datetime]:
    """Return recent likely-published ICON cycles, newest first."""
    if now is None:
        now = datetime.now(timezone.utc)
    probe = _as_utc(now) - timedelta(hours=publication_lag_hours)
    cycle = _floor_cycle(probe)
    return [cycle - timedelta(hours=6 * i) for i in range(int(count))]


def select_icon_run(
    valid_time_utc: datetime,
    *,
    now: datetime | None = None,
    publication_lag_hours: int = 4,
    count: int = 8,
) -> CloudModelRun | None:
    """Choose the newest likely-published ICON cycle covering the valid time."""
    valid = _as_utc(valid_time_utc)
    for cycle in candidate_icon_cycles(
        now,
        publication_lag_hours=publication_lag_hours,
        count=count,
    ):
        delta = valid - cycle
        seconds = delta.total_seconds()
        if seconds < 0 or seconds % 3600:
            continue
        fh = int(seconds // 3600)
        if fh > icon_horizon_hours(cycle.hour):
            continue
        if not icon_forecast_hour_is_published(fh):
            continue
        return CloudModelRun(
            provider="DWD Open Data",
            model="ICON_GLOBAL",
            cycle_time_utc=cycle,
            forecast_hour=fh,
            native_resolution_km=13.0,
            native_grid="icosahedral",
        )
    return None


def candidate_gfs_cycles(
    now: datetime | None = None,
    *,
    publication_lag_hours: int = 4,
    count: int = 8,
) -> list[datetime]:
    if now is None:
        now = datetime.now(timezone.utc)
    probe = _as_utc(now) - timedelta(hours=publication_lag_hours)
    cycle = _floor_cycle(probe)
    return [cycle - timedelta(hours=6 * i) for i in range(int(count))]


def select_gfs_run(
    valid_time_utc: datetime,
    *,
    now: datetime | None = None,
    publication_lag_hours: int = 4,
    count: int = 8,
) -> CloudModelRun | None:
    """Choose a recent GFS cycle covering the valid time."""
    valid = _as_utc(valid_time_utc)
    for cycle in candidate_gfs_cycles(
        now,
        publication_lag_hours=publication_lag_hours,
        count=count,
    ):
        delta = valid - cycle
        seconds = delta.total_seconds()
        if seconds < 0 or seconds % 3600:
            continue
        fh = int(seconds // 3600)
        if fh > GFS_HORIZON_HOURS or fh % 3:
            continue
        return CloudModelRun(
            provider="NOAA/NCEP NOMADS",
            model="GFS",
            cycle_time_utc=cycle,
            forecast_hour=fh,
            native_resolution_km=27.8,
            native_grid="regular_latlon_0p25",
        )
    return None


def resolve_cloud_run(
    valid_time_utc: datetime,
    *,
    now: datetime | None = None,
    icon_available: bool = True,
    gfs_available: bool = True,
) -> CloudModelRun | None:
    """Resolve ICON first, then GFS."""
    if icon_available:
        icon = select_icon_run(valid_time_utc, now=now)
        if icon is not None:
            return icon
    if gfs_available:
        return select_gfs_run(valid_time_utc, now=now)
    return None
