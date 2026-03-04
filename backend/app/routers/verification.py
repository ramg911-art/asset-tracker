"""Verification campaigns and QR scan. POST /verification/scan with location detection."""
import uuid
from pathlib import Path
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models import Asset, AssetVerification, VerificationCampaign
from app.schemas import (
    VerificationCampaignCreate,
    VerificationCampaignResponse,
    ScanVerificationCreate,
    AssetVerificationResponse,
    PaginatedResponse,
)
from app.utils.dependencies import CurrentUser, DBSession
from app.utils.geo import detect_location_by_coords

router = APIRouter()
settings = get_settings()
ALLOWED_PHOTO = set(settings.allowed_image_extensions.lower().split(","))

LOCATION_SOURCE_GPS = "gps"
LOCATION_SOURCE_MANUAL = "manual"
LOCATION_SOURCE_DEVICE = "device_last_location"


@router.get("/campaigns", response_model=PaginatedResponse[VerificationCampaignResponse])
async def list_campaigns(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    total = (await db.execute(select(func.count()).select_from(VerificationCampaign))).scalar() or 0
    q = select(VerificationCampaign).offset((page - 1) * size).limit(size).order_by(VerificationCampaign.created_at.desc())
    result = await db.execute(q)
    items = result.scalars().all()
    pages = (total + size - 1) // size if total else 0
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/campaigns/{campaign_id}", response_model=VerificationCampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    r = await db.execute(select(VerificationCampaign).where(VerificationCampaign.id == campaign_id))
    c = r.scalar_one_or_none()
    if not c:
        raise HTTPException(404, "Campaign not found")
    return c


@router.post("/campaigns", response_model=VerificationCampaignResponse, status_code=201)
async def create_campaign(
    data: VerificationCampaignCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    c = VerificationCampaign(**data.model_dump(), created_by=current_user.id)
    db.add(c)
    await db.flush()
    await db.refresh(c)
    return c


@router.post("/scan", response_model=AssetVerificationResponse, status_code=201)
async def scan_verification(
    data: ScanVerificationCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Record a QR scan. If lat/lon available, detect location by radius; else use manual_location_id.
    location_source: gps | manual | device_last_location.
    """
    r = await db.execute(select(Asset).where(Asset.asset_tag == data.asset_tag))
    asset = r.scalar_one_or_none()
    if not asset:
        raise HTTPException(404, "Asset not found")
    r = await db.execute(select(VerificationCampaign).where(VerificationCampaign.id == data.campaign_id))
    campaign = r.scalar_one_or_none()
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    scan_time = datetime.now(timezone.utc)
    location_source = LOCATION_SOURCE_MANUAL
    detected_location_id: int | None = None
    if data.lat is not None and data.lon is not None:
        loc_id = await detect_location_by_coords(db, data.lat, data.lon)
        if loc_id is not None:
            location_source = LOCATION_SOURCE_GPS
            detected_location_id = loc_id
        else:
            location_source = LOCATION_SOURCE_DEVICE if data.manual_location_id is None else LOCATION_SOURCE_MANUAL
    if detected_location_id is None and data.manual_location_id is not None:
        location_source = LOCATION_SOURCE_MANUAL
        detected_location_id = data.manual_location_id
    verification = AssetVerification(
        campaign_id=data.campaign_id,
        asset_id=asset.id,
        scan_lat=data.lat,
        scan_lon=data.lon,
        location_source=location_source,
        detected_location_id=detected_location_id,
        verified_by=current_user.id,
        scan_time=scan_time,
        notes=None,
    )
    db.add(verification)
    await db.flush()
    await db.refresh(verification)
    return verification


@router.get("/scans", response_model=PaginatedResponse[AssetVerificationResponse])
async def list_scans(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    campaign_id: int | None = None,
    asset_id: int | None = None,
):
    q = select(AssetVerification)
    count_q = select(func.count()).select_from(AssetVerification)
    if campaign_id is not None:
        q = q.where(AssetVerification.campaign_id == campaign_id)
        count_q = count_q.where(AssetVerification.campaign_id == campaign_id)
    if asset_id is not None:
        q = q.where(AssetVerification.asset_id == asset_id)
        count_q = count_q.where(AssetVerification.asset_id == asset_id)
    total = (await db.execute(count_q)).scalar() or 0
    q = q.offset((page - 1) * size).limit(size).order_by(AssetVerification.scan_time.desc())
    result = await db.execute(q)
    items = result.scalars().all()
    pages = (total + size - 1) // size if total else 0
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/scans/{verification_id}/photo")
async def upload_verification_photo(
    verification_id: int,
    current_user: CurrentUser,
    db: DBSession,
    file: UploadFile = File(...),
):
    """Upload photo for a verification scan."""
    ext = (Path(file.filename or "").suffix or ".jpg").lstrip(".").lower()
    if ext not in ALLOWED_PHOTO:
        raise HTTPException(400, f"Allowed: {settings.allowed_image_extensions}")
    r = await db.execute(select(AssetVerification).where(AssetVerification.id == verification_id))
    verification = r.scalar_one_or_none()
    if not verification:
        raise HTTPException(404, "Verification record not found")
    upload_path = Path(settings.upload_dir) / "verification"
    upload_path.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    file_path = upload_path / safe_name
    content = await file.read()
    file_path.write_bytes(content)
    verification.photo_path = str(Path("verification") / safe_name)
    await db.flush()
    await db.refresh(verification)
    return {"photo_path": verification.photo_path, "id": verification.id}
