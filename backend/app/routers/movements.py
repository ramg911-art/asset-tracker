"""Asset movements. POST /movements auto-updates asset.current_location_id."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Asset, AssetMovement
from app.schemas import AssetMovementCreate, AssetMovementResponse, PaginatedResponse
from app.utils.dependencies import CurrentUser, DBSession

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AssetMovementResponse])
async def list_movements(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    asset_id: int | None = None,
):
    q = select(AssetMovement)
    count_q = select(func.count()).select_from(AssetMovement)
    if asset_id is not None:
        q = q.where(AssetMovement.asset_id == asset_id)
        count_q = count_q.where(AssetMovement.asset_id == asset_id)
    total = (await db.execute(count_q)).scalar() or 0
    q = q.offset((page - 1) * size).limit(size).order_by(AssetMovement.movement_date.desc())
    result = await db.execute(q)
    items = result.scalars().all()
    pages = (total + size - 1) // size if total else 0
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/{movement_id}", response_model=AssetMovementResponse)
async def get_movement(
    movement_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(AssetMovement).where(AssetMovement.id == movement_id))
    m = r.scalar_one_or_none()
    if not m:
        raise HTTPException(404, "Movement not found")
    return m


@router.post("", response_model=AssetMovementResponse, status_code=201)
async def create_movement(
    data: AssetMovementCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(Asset).where(Asset.id == data.asset_id))
    asset = r.scalar_one_or_none()
    if not asset:
        raise HTTPException(404, "Asset not found")
    movement_date = data.movement_date or datetime.now(timezone.utc)
    movement = AssetMovement(
        asset_id=data.asset_id,
        from_location_id=data.from_location_id,
        to_location_id=data.to_location_id,
        movement_type=data.movement_type,
        moved_by=current_user.id,
        movement_date=movement_date,
        remarks=data.remarks,
    )
    db.add(movement)
    await db.flush()
    # Auto-update asset current location
    asset.current_location_id = data.to_location_id
    asset.updated_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(movement)
    return movement


@router.delete("/{movement_id}", status_code=204)
async def delete_movement(
    movement_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(AssetMovement).where(AssetMovement.id == movement_id))
    m = r.scalar_one_or_none()
    if not m:
        raise HTTPException(404, "Movement not found")
    await db.delete(m)
    return None
