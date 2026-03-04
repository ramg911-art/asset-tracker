"""Asset documents with file upload (local storage)."""
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models import Asset, AssetDocument
from app.schemas import AssetDocumentResponse, PaginatedResponse
from app.utils.dependencies import CurrentUser, DBSession

router = APIRouter()
settings = get_settings()
ALLOWED = set(settings.allowed_document_extensions.lower().split(","))


def allowed_file(filename: str) -> bool:
    ext = Path(filename).suffix.lstrip(".").lower()
    return ext in ALLOWED


@router.get("", response_model=PaginatedResponse[AssetDocumentResponse])
async def list_documents(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    asset_id: int | None = None,
):
    q = select(AssetDocument)
    count_q = select(func.count()).select_from(AssetDocument)
    if asset_id is not None:
        q = q.where(AssetDocument.asset_id == asset_id)
        count_q = count_q.where(AssetDocument.asset_id == asset_id)
    total = (await db.execute(count_q)).scalar() or 0
    q = q.offset((page - 1) * size).limit(size).order_by(AssetDocument.uploaded_at.desc())
    result = await db.execute(q)
    items = result.scalars().all()
    pages = (total + size - 1) // size if total else 0
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/{doc_id}", response_model=AssetDocumentResponse)
async def get_document(
    doc_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(AssetDocument).where(AssetDocument.id == doc_id))
    doc = r.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


@router.post("", response_model=AssetDocumentResponse, status_code=201)
async def upload_document(
    db: DBSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    asset_id: int = Form(...),
    title: str = Form(None),
):
    if not title:
        title = file.filename or "Document"
    if not allowed_file(file.filename or ""):
        raise HTTPException(400, f"Allowed extensions: {settings.allowed_document_extensions}")
    r = await db.execute(select(Asset).where(Asset.id == asset_id))
    if not r.scalar_one_or_none():
        raise HTTPException(404, "Asset not found")
    upload_path = Path(settings.upload_dir) / "documents"
    upload_path.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename or "bin").suffix
    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_path / safe_name
    content = await file.read()
    file_path.write_bytes(content)
    relative_path = str(Path("documents") / safe_name)
    doc = AssetDocument(
        asset_id=asset_id,
        title=title,
        file_path=relative_path,
        file_type=ext.lstrip("."),
        uploaded_by=current_user.id,
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return doc


@router.delete("/{doc_id}", status_code=204)
async def delete_document(
    doc_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(AssetDocument).where(AssetDocument.id == doc_id))
    doc = r.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Document not found")
    full_path = Path(settings.upload_dir) / doc.file_path
    if full_path.exists():
        full_path.unlink(missing_ok=True)
    await db.delete(doc)
    return None
