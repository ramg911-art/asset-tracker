"""Label generation schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LabelGenerateRequest(BaseModel):
    """Input for POST /labels/generate."""

    asset_ids: list[int]


class LabelBatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: Optional[str] = None
    file_path: Optional[str] = None
    asset_count: int
    created_by: Optional[int] = None
    created_at: datetime
