"""Asset document schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AssetDocumentCreate(BaseModel):
    asset_id: int
    title: str


class AssetDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    asset_id: int
    title: str
    file_path: str
    file_type: Optional[str] = None
    uploaded_at: datetime
    uploaded_by: Optional[int] = None
