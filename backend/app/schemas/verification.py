"""Verification campaign and scan schemas."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class VerificationCampaignBase(BaseModel):
    name: str
    location_id: Optional[int] = None
    start_date: date
    end_date: date
    status: str = "draft"


class VerificationCampaignCreate(VerificationCampaignBase):
    pass


class VerificationCampaignResponse(VerificationCampaignBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_by: Optional[int] = None
    created_at: datetime


class ScanVerificationCreate(BaseModel):
    """Payload for POST /verification/scan."""

    asset_tag: str
    campaign_id: int
    lat: Optional[float] = None
    lon: Optional[float] = None
    accuracy: Optional[float] = None
    manual_location_id: Optional[int] = None


class AssetVerificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    campaign_id: int
    asset_id: int
    scan_lat: Optional[float] = None
    scan_lon: Optional[float] = None
    location_source: str
    detected_location_id: Optional[int] = None
    verified_by: Optional[int] = None
    scan_time: datetime
    photo_path: Optional[str] = None
    notes: Optional[str] = None
