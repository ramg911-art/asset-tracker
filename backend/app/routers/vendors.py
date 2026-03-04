"""Vendors CRUD."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Vendor
from app.schemas import VendorCreate, VendorUpdate, VendorResponse, PaginatedResponse
from app.utils.dependencies import CurrentUser, DBSession

router = APIRouter()


@router.get("", response_model=PaginatedResponse[VendorResponse])
async def list_vendors(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    total = (await db.execute(select(func.count()).select_from(Vendor))).scalar() or 0
    q = select(Vendor).offset((page - 1) * size).limit(size).order_by(Vendor.name)
    result = await db.execute(q)
    items = result.scalars().all()
    pages = (total + size - 1) // size if total else 0
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: int, db: DBSession, current_user: CurrentUser):
    r = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    v = r.scalar_one_or_none()
    if not v:
        raise HTTPException(404, "Vendor not found")
    return v


@router.post("", response_model=VendorResponse, status_code=201)
async def create_vendor(
    data: VendorCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    v = Vendor(**data.model_dump())
    db.add(v)
    await db.flush()
    await db.refresh(v)
    return v


@router.patch("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: int,
    data: VendorUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    v = r.scalar_one_or_none()
    if not v:
        raise HTTPException(404, "Vendor not found")
    for k, val in data.model_dump(exclude_unset=True).items():
        setattr(v, k, val)
    await db.flush()
    await db.refresh(v)
    return v


@router.delete("/{vendor_id}", status_code=204)
async def delete_vendor(
    vendor_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    v = r.scalar_one_or_none()
    if not v:
        raise HTTPException(404, "Vendor not found")
    await db.delete(v)
    return None
