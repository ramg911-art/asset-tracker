"""Asset category schemas."""
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AssetCategoryBase(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None


class AssetCategoryCreate(AssetCategoryBase):
    pass


class AssetCategoryUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None


class AssetCategoryResponse(AssetCategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
