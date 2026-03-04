"""Asset schemas."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AssetBase(BaseModel):
    asset_tag: str
    name: str
    category_id: int
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_cost: Optional[Decimal] = None
    current_location_id: Optional[int] = None
    department_id: Optional[int] = None
    status: str = "active"
    warranty_start: Optional[date] = None
    warranty_end: Optional[date] = None
    amc_start: Optional[date] = None
    amc_end: Optional[date] = None
    vendor_id: Optional[int] = None
    criticality: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    asset_tag: Optional[str] = None
    name: Optional[str] = None
    category_id: Optional[int] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_cost: Optional[Decimal] = None
    current_location_id: Optional[int] = None
    department_id: Optional[int] = None
    status: Optional[str] = None
    warranty_start: Optional[date] = None
    warranty_end: Optional[date] = None
    amc_start: Optional[date] = None
    amc_end: Optional[date] = None
    vendor_id: Optional[int] = None
    criticality: Optional[str] = None


class AssetResponse(AssetBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class AssetListResponse(BaseModel):
    """Minimal asset for list views."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    asset_tag: str
    name: str
    category_id: int
    status: str
    current_location_id: Optional[int] = None
