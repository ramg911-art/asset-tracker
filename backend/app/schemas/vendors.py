"""Vendor schemas."""
from typing import Optional

from pydantic import BaseModel, ConfigDict


class VendorBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class VendorResponse(VendorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
