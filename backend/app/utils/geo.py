"""Geometry helpers for location detection."""
import math
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Location


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance in meters between two WGS84 points."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


async def detect_location_by_coords(
    db: AsyncSession,
    lat: float,
    lon: float,
) -> Optional[int]:
    """
    Find a location whose (latitude, longitude, radius_meters) circle contains the point.
    Returns location id or None. If multiple match, returns first.
    """
    result = await db.execute(
        select(Location)
        .where(
            Location.latitude.isnot(None),
            Location.longitude.isnot(None),
            Location.radius_meters.isnot(None),
        )
    )
    for loc in result.scalars().all():
        if loc.latitude is None or loc.longitude is None or loc.radius_meters is None:
            continue
        if haversine_meters(lat, lon, loc.latitude, loc.longitude) <= loc.radius_meters:
            return loc.id
    return None
