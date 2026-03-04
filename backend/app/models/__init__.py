"""SQLAlchemy models for Enterprise Asset Management."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# --- Enums ---
class AssetStatusEnum(str):
    ACTIVE = "active"
    UNDER_REPAIR = "under_repair"
    OUT_OF_SERVICE = "out_of_service"
    DISPOSED = "disposed"
    LOST = "lost"


class MovementTypeEnum(str):
    TRANSFER = "transfer"
    RETURN = "return"
    ISSUE = "issue"
    OTHER = "other"


class LocationSourceEnum(str):
    GPS = "gps"
    MANUAL = "manual"
    DEVICE_LAST_LOCATION = "device_last_location"


class CampaignStatusEnum(str):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# --- Users & Auth ---
class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    user_roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    user_roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")


class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="user_roles")
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles")


# --- Locations (hierarchical) ---
class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    location_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    radius_meters: Mapped[Optional[float]] = mapped_column(nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    parent: Mapped[Optional["Location"]] = relationship("Location", remote_side=[id], back_populates="children")
    children: Mapped[list["Location"]] = relationship("Location", back_populates="parent")


# --- Departments ---
class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    assets: Mapped[list["Asset"]] = relationship("Asset", back_populates="department")


# --- Asset Categories ---
class AssetCategory(Base):
    __tablename__ = "asset_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    assets: Mapped[list["Asset"]] = relationship("Asset", back_populates="category")


# --- Vendors ---
class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_person: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    assets: Mapped[list["Asset"]] = relationship("Asset", back_populates="vendor")
    repairs: Mapped[list["AssetRepair"]] = relationship("AssetRepair", back_populates="vendor")
    maintenance_plans: Mapped[list["MaintenancePlan"]] = relationship("MaintenancePlan", back_populates="vendor")


# --- Assets ---
class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_tag: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("asset_categories.id", ondelete="RESTRICT"), nullable=False)
    serial_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    purchase_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    purchase_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    current_location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    warranty_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    warranty_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    amc_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    amc_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    vendor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True)
    criticality: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()", onupdate="now()")

    category: Mapped["AssetCategory"] = relationship("AssetCategory", back_populates="assets")
    current_location: Mapped[Optional["Location"]] = relationship("Location", foreign_keys=[current_location_id])
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="assets")
    vendor: Mapped[Optional["Vendor"]] = relationship("Vendor", back_populates="assets")
    movements: Mapped[list["AssetMovement"]] = relationship("AssetMovement", back_populates="asset", foreign_keys="AssetMovement.asset_id")
    repairs: Mapped[list["AssetRepair"]] = relationship("AssetRepair", back_populates="asset")
    documents: Mapped[list["AssetDocument"]] = relationship("AssetDocument", back_populates="asset", cascade="all, delete-orphan")
    photos: Mapped[list["AssetPhoto"]] = relationship("AssetPhoto", back_populates="asset", cascade="all, delete-orphan")
    assignments: Mapped[list["AssetAssignment"]] = relationship("AssetAssignment", back_populates="asset")
    maintenance_plans: Mapped[list["MaintenancePlan"]] = relationship("MaintenancePlan", back_populates="asset")
    maintenance_records: Mapped[list["MaintenanceRecord"]] = relationship("MaintenanceRecord", back_populates="asset")
    verifications: Mapped[list["AssetVerification"]] = relationship("AssetVerification", back_populates="asset")
    events: Mapped[list["AssetEvent"]] = relationship("AssetEvent", back_populates="asset")
    disposals: Mapped[list["AssetDisposal"]] = relationship("AssetDisposal", back_populates="asset")


# --- Asset Documents & Photos ---
class AssetDocument(Base):
    __tablename__ = "asset_documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")
    uploaded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="documents")


class AssetPhoto(Base):
    __tablename__ = "asset_photos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    caption: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    taken_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    uploaded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="photos")


# --- Asset Movements ---
class AssetMovement(Base):
    __tablename__ = "asset_movements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    from_location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    to_location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    movement_type: Mapped[str] = mapped_column(String(32), nullable=False)
    moved_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    movement_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="movements", foreign_keys=[asset_id])


# --- Asset Assignments ---
class AssetAssignment(Base):
    __tablename__ = "asset_assignments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    assigned_to: Mapped[str] = mapped_column(String(255), nullable=False)  # user id or employee id
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")
    returned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="assignments")


# --- Asset Repairs ---
class AssetRepair(Base):
    __tablename__ = "asset_repairs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    reported_date: Mapped[date] = mapped_column(Date, nullable=False)
    issue_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    service_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    vendor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True)
    contact_person: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    expected_return_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_return_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="repairs")
    vendor: Mapped[Optional["Vendor"]] = relationship("Vendor", back_populates="repairs")


# --- Maintenance ---
class MaintenancePlan(Base):
    __tablename__ = "maintenance_plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    maintenance_type: Mapped[str] = mapped_column(String(128), nullable=False)
    interval_days: Mapped[Optional[int]] = mapped_column(nullable=True)
    last_service_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    next_due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    vendor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True)
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="maintenance_plans")
    vendor: Mapped[Optional["Vendor"]] = relationship("Vendor", back_populates="maintenance_plans")


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    plan_id: Mapped[Optional[int]] = mapped_column(ForeignKey("maintenance_plans.id", ondelete="SET NULL"), nullable=True)
    performed_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    performed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="maintenance_records")


# --- Verification ---
class VerificationCampaign(Base):
    __tablename__ = "verification_campaigns"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    verifications: Mapped[list["AssetVerification"]] = relationship("AssetVerification", back_populates="campaign")


class AssetVerification(Base):
    __tablename__ = "asset_verifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("verification_campaigns.id", ondelete="CASCADE"), nullable=False)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_lat: Mapped[Optional[float]] = mapped_column(nullable=True)
    scan_lon: Mapped[Optional[float]] = mapped_column(nullable=True)
    location_source: Mapped[str] = mapped_column(String(32), nullable=False)
    detected_location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    verified_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    scan_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    photo_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    campaign: Mapped["VerificationCampaign"] = relationship("VerificationCampaign", back_populates="verifications")
    asset: Mapped["Asset"] = relationship("Asset", back_populates="verifications")


# --- Asset Events (timeline) ---
class AssetEvent(Base):
    __tablename__ = "asset_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reference_id: Mapped[Optional[int]] = mapped_column(nullable=True)  # generic FK to movement, repair, etc.
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    asset: Mapped["Asset"] = relationship("Asset", back_populates="events")


# --- Asset Disposals ---
class AssetDisposal(Base):
    __tablename__ = "asset_disposals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    disposal_date: Mapped[date] = mapped_column(Date, nullable=False)
    disposal_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    asset: Mapped["Asset"] = relationship("Asset", back_populates="disposals")


# --- Label Batches ---
class LabelBatch(Base):
    __tablename__ = "label_batches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    asset_count: Mapped[int] = mapped_column(nullable=False, default=0)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")


# --- Audit Log ---
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    table_name: Mapped[str] = mapped_column(String(128), nullable=False)
    record_id: Mapped[int] = mapped_column(nullable=False)
    action: Mapped[str] = mapped_column(String(16), nullable=False)  # INSERT, UPDATE, DELETE
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    old_values: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    new_values: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")


# --- System Settings ---
class SystemSetting(Base):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()", onupdate="now()")


