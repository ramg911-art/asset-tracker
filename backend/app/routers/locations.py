"""Locations CRUD."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Location
from app.schemas import LocationCreate, LocationUpdate, LocationResponse, PaginatedResponse
from app.utils.dependencies import CurrentUser, DBSession
from app.utils.audit import log_audit

router = APIRouter()


@router.get("", response_model=PaginatedResponse[LocationResponse])
async def list_locations(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    parent_id: int | None = None,
):
    q = select(Location)
    count_q = select(func.count()).select_from(Location)
    if parent_id is not None:
        q = q.where(Location.parent_id == parent_id)
        count_q = count_q.where(Location.parent_id == parent_id)
    total = (await db.execute(count_q)).scalar() or 0
    q = q.offset((page - 1) * size).limit(size).order_by(Location.name)
    result = await db.execute(q)
    items = result.scalars().all()
    pages = (total + size - 1) // size if total else 0
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(location_id: int, db: DBSession, current_user: CurrentUser):
    r = await db.execute(select(Location).where(Location.id == location_id))
    loc = r.scalar_one_or_none()
    if not loc:
        raise HTTPException(404, "Location not found")
    return loc


@router.post("", response_model=LocationResponse, status_code=201)
async def create_location(
    data: LocationCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    loc = Location(**data.model_dump())
    db.add(loc)
    await db.flush()
    await log_audit(db, "locations", loc.id, "INSERT", current_user.id, new_values=data.model_dump())
    await db.refresh(loc)
    return loc


@router.patch("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: int,
    data: LocationUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(Location).where(Location.id == location_id))
    loc = r.scalar_one_or_none()
    if not loc:
        raise HTTPException(404, "Location not found")
    old_vals = {k: getattr(loc, k) for k in data.model_dump(exclude_unset=True)}
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(loc, k, v)
    await db.flush()
    await log_audit(db, "locations", loc.id, "UPDATE", current_user.id, old_values=old_vals, new_values=data.model_dump(exclude_unset=True))
    await db.refresh(loc)
    return loc


@router.delete("/{location_id}", status_code=204)
async def delete_location(
    location_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(Location).where(Location.id == location_id))
    loc = r.scalar_one_or_none()
    if not loc:
        raise HTTPException(404, "Location not found")
    await log_audit(db, "locations", loc.id, "DELETE", current_user.id, old_values={"id": loc.id, "name": loc.name})
    await db.delete(loc)
    return None
