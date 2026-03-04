"""Audit logging helper."""
import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog


async def log_audit(
    db: AsyncSession,
    table_name: str,
    record_id: int,
    action: str,
    user_id: int | None = None,
    old_values: dict[str, Any] | None = None,
    new_values: dict[str, Any] | None = None,
) -> None:
    """Create an audit log entry. Call after commit for INSERT/UPDATE/DELETE."""
    def _serialize(obj):
        return json.dumps(obj, default=str) if obj is not None else None
    entry = AuditLog(
        table_name=table_name,
        record_id=record_id,
        action=action.upper(),
        user_id=user_id,
        old_values=_serialize(old_values),
        new_values=_serialize(new_values),
    )
    db.add(entry)
    await db.flush()
