"""Assets CRUD."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Asset
from app.schemas import AssetCreate, AssetUpdate, AssetResponse, AssetListResponse, PaginatedResponse
from app.utils.dependencies import CurrentUser, DBSession
from app.utils.audit import log_audit

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AssetResponse])
async def list_assets(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    status: str | None = None,
    category_id: int | None = None,
    location_id: int | None = None,
):
    q = select(Asset)
    count_q = select(func.count()).select_from(Asset)
    if search:
        term = f"%{search}%"
        q = q.where(
            or_(
                Asset.asset_tag.ilike(term),
                Asset.name.ilike(term),
                Asset.serial_number.ilike(term),
            )
        )
        count_q = count_q.where(
            or_(
                Asset.asset_tag.ilike(term),
                Asset.name.ilike(term),
                Asset.serial_number.ilike(term),
            )
        )
    if status:
        q = q.where(Asset.status == status)
        count_q = count_q.where(Asset.status == status)
    if category_id is not None:
        q = q.where(Asset.category_id == category_id)
        count_q = count_q.where(Asset.category_id == category_id)
    if location_id is not None:
        q = q.where(Asset.current_location_id == location_id)
        count_q = count_q.where(Asset.current_location_id == location_id)
    total = (await db.execute(count_q)).scalar() or 0
    q = q.offset((page - 1) * size).limit(size).order_by(Asset.asset_tag)
    result = await db.execute(q)
    items = result.scalars().all()
    pages = (total + size - 1) // size if total else 0
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: int, db: DBSession, current_user: CurrentUser):
    r = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = r.scalar_one_or_none()
    if not asset:
        raise HTTPException(404, "Asset not found")
    return asset


@router.post("", response_model=AssetResponse, status_code=201)
async def create_asset(
    data: AssetCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(Asset).where(Asset.asset_tag == data.asset_tag))
    if r.scalar_one_or_none():
        raise HTTPException(400, "Asset tag already exists")
    asset = Asset(**data.model_dump())
    db.add(asset)
    await db.flush()
    await log_audit(db, "assets", asset.id, "INSERT", current_user.id, new_values=data.model_dump())
    await db.refresh(asset)
    return asset


@router.patch("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    data: AssetUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = r.scalar_one_or_none()
    if not asset:
        raise HTTPException(404, "Asset not found")
    old_vals = {k: getattr(asset, k) for k in data.model_dump(exclude_unset=True)}
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(asset, k, v)
    await db.flush()
    await log_audit(db, "assets", asset.id, "UPDATE", current_user.id, old_values=old_vals, new_values=data.model_dump(exclude_unset=True))
    await db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(
    asset_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = r.scalar_one_or_none()
    if not asset:
        raise HTTPException(404, "Asset not found")
    await log_audit(db, "assets", asset.id, "DELETE", current_user.id, old_values={"id": asset.id, "asset_tag": asset.asset_tag})
    await db.delete(asset)
    return None
