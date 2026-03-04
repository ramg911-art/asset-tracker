"""Asset repair schemas."""
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AssetRepairBase(BaseModel):
    asset_id: int
    reported_date: date
    issue_description: Optional[str] = None
    service_type: Optional[str] = None
    vendor_id: Optional[int] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    expected_return_date: Optional[date] = None
    actual_return_date: Optional[date] = None
    cost: Optional[Decimal] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class AssetRepairCreate(AssetRepairBase):
    pass


class AssetRepairUpdate(BaseModel):
    reported_date: Optional[date] = None
    issue_description: Optional[str] = None
    service_type: Optional[str] = None
    vendor_id: Optional[int] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    expected_return_date: Optional[date] = None
    actual_return_date: Optional[date] = None
    cost: Optional[Decimal] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class AssetRepairResponse(AssetRepairBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_by: Optional[int] = None
