"""Location schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LocationBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    location_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_meters: Optional[float] = None
    address: Optional[str] = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    location_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_meters: Optional[float] = None
    address: Optional[str] = None


class LocationResponse(LocationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
