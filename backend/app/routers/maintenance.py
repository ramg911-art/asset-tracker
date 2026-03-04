"""Maintenance plans CRUD."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import MaintenancePlan
from app.schemas import MaintenancePlanCreate, MaintenancePlanUpdate, MaintenancePlanResponse, PaginatedResponse
from app.utils.dependencies import CurrentUser, DBSession

router = APIRouter()


@router.get("", response_model=PaginatedResponse[MaintenancePlanResponse])
async def list_plans(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    asset_id: int | None = None,
):
    q = select(MaintenancePlan)
    count_q = select(func.count()).select_from(MaintenancePlan)
    if asset_id is not None:
        q = q.where(MaintenancePlan.asset_id == asset_id)
        count_q = count_q.where(MaintenancePlan.asset_id == asset_id)
    total = (await db.execute(count_q)).scalar() or 0
    q = q.offset((page - 1) * size).limit(size).order_by(MaintenancePlan.next_due_date.asc().nullslast())
    result = await db.execute(q)
    items = result.scalars().all()
    pages = (total + size - 1) // size if total else 0
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/{plan_id}", response_model=MaintenancePlanResponse)
async def get_plan(
    plan_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(MaintenancePlan).where(MaintenancePlan.id == plan_id))
    plan = r.scalar_one_or_none()
    if not plan:
        raise HTTPException(404, "Maintenance plan not found")
    return plan


@router.post("", response_model=MaintenancePlanResponse, status_code=201)
async def create_plan(
    data: MaintenancePlanCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    plan = MaintenancePlan(**data.model_dump())
    db.add(plan)
    await db.flush()
    await db.refresh(plan)
    return plan


@router.patch("/{plan_id}", response_model=MaintenancePlanResponse)
async def update_plan(
    plan_id: int,
    data: MaintenancePlanUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(MaintenancePlan).where(MaintenancePlan.id == plan_id))
    plan = r.scalar_one_or_none()
    if not plan:
        raise HTTPException(404, "Maintenance plan not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(plan, k, v)
    await db.flush()
    await db.refresh(plan)
    return plan


@router.delete("/{plan_id}", status_code=204)
async def delete_plan(
    plan_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(MaintenancePlan).where(MaintenancePlan.id == plan_id))
    plan = r.scalar_one_or_none()
    if not plan:
        raise HTTPException(404, "Maintenance plan not found")
    await db.delete(plan)
    return None
