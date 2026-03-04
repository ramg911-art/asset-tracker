"""Pydantic schemas for API request/response."""
from app.schemas.common import PaginatedResponse
from app.schemas.auth import Token, TokenData, UserCreate, UserResponse, UserLogin
from app.schemas.locations import LocationCreate, LocationUpdate, LocationResponse
from app.schemas.departments import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.schemas.categories import AssetCategoryCreate, AssetCategoryUpdate, AssetCategoryResponse
from app.schemas.vendors import VendorCreate, VendorUpdate, VendorResponse
from app.schemas.assets import AssetCreate, AssetUpdate, AssetResponse, AssetListResponse
from app.schemas.movements import AssetMovementCreate, AssetMovementResponse
from app.schemas.repairs import AssetRepairCreate, AssetRepairUpdate, AssetRepairResponse
from app.schemas.maintenance import MaintenancePlanCreate, MaintenancePlanUpdate, MaintenancePlanResponse
from app.schemas.verification import (
    VerificationCampaignCreate,
    VerificationCampaignResponse,
    ScanVerificationCreate,
    AssetVerificationResponse,
)
from app.schemas.documents import AssetDocumentCreate, AssetDocumentResponse
from app.schemas.labels import LabelGenerateRequest, LabelBatchResponse
from app.schemas.audit import AuditLogResponse

__all__ = [
    "PaginatedResponse",
    "Token",
    "TokenData",
    "UserCreate",
    "UserResponse",
    "UserLogin",
    "LocationCreate",
    "LocationUpdate",
    "LocationResponse",
    "DepartmentCreate",
    "DepartmentUpdate",
    "DepartmentResponse",
    "AssetCategoryCreate",
    "AssetCategoryUpdate",
    "AssetCategoryResponse",
    "VendorCreate",
    "VendorUpdate",
    "VendorResponse",
    "AssetCreate",
    "AssetUpdate",
    "AssetResponse",
    "AssetListResponse",
    "AssetMovementCreate",
    "AssetMovementResponse",
    "AssetRepairCreate",
    "AssetRepairUpdate",
    "AssetRepairResponse",
    "MaintenancePlanCreate",
    "MaintenancePlanUpdate",
    "MaintenancePlanResponse",
    "VerificationCampaignCreate",
    "VerificationCampaignResponse",
    "ScanVerificationCreate",
    "AssetVerificationResponse",
    "AssetDocumentCreate",
    "AssetDocumentResponse",
    "LabelGenerateRequest",
    "LabelBatchResponse",
    "AuditLogResponse",
]
