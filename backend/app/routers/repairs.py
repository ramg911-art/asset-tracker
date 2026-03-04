"""Asset repairs CRUD."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import AssetRepair
from app.schemas import AssetRepairCreate, AssetRepairUpdate, AssetRepairResponse, PaginatedResponse
from app.utils.dependencies import CurrentUser, DBSession

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AssetRepairResponse])
async def list_repairs(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    asset_id: int | None = None,
):
    q = select(AssetRepair)
    count_q = select(func.count()).select_from(AssetRepair)
    if asset_id is not None:
        q = q.where(AssetRepair.asset_id == asset_id)
        count_q = count_q.where(AssetRepair.asset_id == asset_id)
    total = (await db.execute(count_q)).scalar() or 0
    q = q.offset((page - 1) * size).limit(size).order_by(AssetRepair.reported_date.desc())
    result = await db.execute(q)
    items = result.scalars().all()
    pages = (total + size - 1) // size if total else 0
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/{repair_id}", response_model=AssetRepairResponse)
async def get_repair(
    repair_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(AssetRepair).where(AssetRepair.id == repair_id))
    rep = r.scalar_one_or_none()
    if not rep:
        raise HTTPException(404, "Repair not found")
    return rep


@router.post("", response_model=AssetRepairResponse, status_code=201)
async def create_repair(
    data: AssetRepairCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    rep = AssetRepair(**data.model_dump(), created_by=current_user.id)
    db.add(rep)
    await db.flush()
    await db.refresh(rep)
    return rep


@router.patch("/{repair_id}", response_model=AssetRepairResponse)
async def update_repair(
    repair_id: int,
    data: AssetRepairUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(AssetRepair).where(AssetRepair.id == repair_id))
    rep = r.scalar_one_or_none()
    if not rep:
        raise HTTPException(404, "Repair not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(rep, k, v)
    await db.flush()
    await db.refresh(rep)
    return rep


@router.delete("/{repair_id}", status_code=204)
async def delete_repair(
    repair_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(AssetRepair).where(AssetRepair.id == repair_id))
    rep = r.scalar_one_or_none()
    if not rep:
        raise HTTPException(404, "Repair not found")
    await db.delete(rep)
    return None
