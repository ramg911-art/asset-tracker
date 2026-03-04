"""Departments CRUD."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Department
from app.schemas import DepartmentCreate, DepartmentUpdate, DepartmentResponse, PaginatedResponse
from app.utils.dependencies import CurrentUser, DBSession

router = APIRouter()


@router.get("", response_model=PaginatedResponse[DepartmentResponse])
async def list_departments(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    total = (await db.execute(select(func.count()).select_from(Department))).scalar() or 0
    q = select(Department).offset((page - 1) * size).limit(size).order_by(Department.name)
    result = await db.execute(q)
    items = result.scalars().all()
    pages = (total + size - 1) // size if total else 0
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(department_id: int, db: DBSession, current_user: CurrentUser):
    r = await db.execute(select(Department).where(Department.id == department_id))
    dep = r.scalar_one_or_none()
    if not dep:
        raise HTTPException(404, "Department not found")
    return dep


@router.post("", response_model=DepartmentResponse, status_code=201)
async def create_department(
    data: DepartmentCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    dep = Department(**data.model_dump())
    db.add(dep)
    await db.flush()
    await db.refresh(dep)
    return dep


@router.patch("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    data: DepartmentUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(Department).where(Department.id == department_id))
    dep = r.scalar_one_or_none()
    if not dep:
        raise HTTPException(404, "Department not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(dep, k, v)
    await db.flush()
    await db.refresh(dep)
    return dep


@router.delete("/{department_id}", status_code=204)
async def delete_department(
    department_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(Department).where(Department.id == department_id))
    dep = r.scalar_one_or_none()
    if not dep:
        raise HTTPException(404, "Department not found")
    await db.delete(dep)
    return None
