"""Asset categories CRUD."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import AssetCategory
from app.schemas import AssetCategoryCreate, AssetCategoryUpdate, AssetCategoryResponse, PaginatedResponse
from app.utils.dependencies import CurrentUser, DBSession

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AssetCategoryResponse])
async def list_categories(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    total = (await db.execute(select(func.count()).select_from(AssetCategory))).scalar() or 0
    q = select(AssetCategory).offset((page - 1) * size).limit(size).order_by(AssetCategory.name)
    result = await db.execute(q)
    items = result.scalars().all()
    pages = (total + size - 1) // size if total else 0
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/{category_id}", response_model=AssetCategoryResponse)
async def get_category(category_id: int, db: DBSession, current_user: CurrentUser):
    r = await db.execute(select(AssetCategory).where(AssetCategory.id == category_id))
    cat = r.scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "Category not found")
    return cat


@router.post("", response_model=AssetCategoryResponse, status_code=201)
async def create_category(
    data: AssetCategoryCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    cat = AssetCategory(**data.model_dump())
    db.add(cat)
    await db.flush()
    await db.refresh(cat)
    return cat


@router.patch("/{category_id}", response_model=AssetCategoryResponse)
async def update_category(
    category_id: int,
    data: AssetCategoryUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(AssetCategory).where(AssetCategory.id == category_id))
    cat = r.scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "Category not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(cat, k, v)
    await db.flush()
    await db.refresh(cat)
    return cat


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(AssetCategory).where(AssetCategory.id == category_id))
    cat = r.scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "Category not found")
    await db.delete(cat)
    return None
