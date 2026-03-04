"""Reports: summary and list endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Asset, AssetRepair, MaintenancePlan, AssetVerification
from app.schemas import AuditLogResponse, PaginatedResponse
from app.models import AuditLog
from app.utils.dependencies import CurrentUser, DBSession

router = APIRouter()


@router.get("/summary")
async def report_summary(
    db: DBSession,
    current_user: CurrentUser,
):
    """Basic counts for dashboard."""
    total_assets = (await db.execute(select(func.count()).select_from(Asset))).scalar() or 0
    active_assets = (await db.execute(select(func.count()).select_from(Asset).where(Asset.status == "active"))).scalar() or 0
    total_repairs = (await db.execute(select(func.count()).select_from(AssetRepair))).scalar() or 0
    total_plans = (await db.execute(select(func.count()).select_from(MaintenancePlan))).scalar() or 0
    total_verifications = (await db.execute(select(func.count()).select_from(AssetVerification))).scalar() or 0
    return {
        "total_assets": total_assets,
        "active_assets": active_assets,
        "total_repairs": total_repairs,
        "maintenance_plans": total_plans,
        "verification_scans": total_verifications,
    }


@router.get("/audit", response_model=PaginatedResponse[AuditLogResponse])
async def list_audit_logs(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    table_name: str | None = None,
    record_id: int | None = None,
):
    q = select(AuditLog)
    count_q = select(func.count()).select_from(AuditLog)
    if table_name:
        q = q.where(AuditLog.table_name == table_name)
        count_q = count_q.where(AuditLog.table_name == table_name)
    if record_id is not None:
        q = q.where(AuditLog.record_id == record_id)
        count_q = count_q.where(AuditLog.record_id == record_id)
    total = (await db.execute(count_q)).scalar() or 0
    q = q.offset((page - 1) * size).limit(size).order_by(AuditLog.timestamp.desc())
    result = await db.execute(q)
    items = result.scalars().all()
    pages = (total + size - 1) // size if total else 0
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)
