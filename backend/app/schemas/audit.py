"""Audit log schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    table_name: str
    record_id: int
    action: str
    user_id: Optional[int] = None
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    timestamp: datetime
