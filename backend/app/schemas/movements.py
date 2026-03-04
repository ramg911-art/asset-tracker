"""Asset movement schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AssetMovementCreate(BaseModel):
    asset_id: int
    from_location_id: Optional[int] = None
    to_location_id: Optional[int] = None
    movement_type: str = "transfer"
    movement_date: Optional[datetime] = None
    remarks: Optional[str] = None


class AssetMovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    asset_id: int
    from_location_id: Optional[int] = None
    to_location_id: Optional[int] = None
    movement_type: str
    moved_by: Optional[int] = None
    movement_date: datetime
    remarks: Optional[str] = None
