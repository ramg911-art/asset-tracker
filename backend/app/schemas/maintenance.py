"""Maintenance plan schemas."""
from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MaintenancePlanBase(BaseModel):
    asset_id: int
    maintenance_type: str
    interval_days: Optional[int] = None
    last_service_date: Optional[date] = None
    next_due_date: Optional[date] = None
    vendor_id: Optional[int] = None
    instructions: Optional[str] = None


class MaintenancePlanCreate(MaintenancePlanBase):
    pass


class MaintenancePlanUpdate(BaseModel):
    maintenance_type: Optional[str] = None
    interval_days: Optional[int] = None
    last_service_date: Optional[date] = None
    next_due_date: Optional[date] = None
    vendor_id: Optional[int] = None
    instructions: Optional[str] = None


class MaintenancePlanResponse(MaintenancePlanBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
