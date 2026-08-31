"""
Road Health Intelligence (RHI) - SQLAlchemy Models
Database tables for full lifecycle: Photo -> AI Detection -> GPS -> Defect -> Priority -> Work Order -> Repair -> AI Verification -> Warranty Recurrence -> Audit
"""
import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(String, default="Inspector")  # Inspector, Engineer, Contractor, Admin
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class RoadSegment(Base):
    __tablename__ = "road_segments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)  # e.g., RHI-2048
    name = Column(String)                           # e.g., Ring Road Expressway - Sector 4
    health_score = Column(Integer, default=85)      # 0 - 100
    active_defects = Column(Integer, default=0)
    critical_defects = Column(Integer, default=0)
    last_inspection = Column(String, default="Today")
    repair_status = Column(String, default="Normal Operations")
    length_km = Column(Float, default=2.4)
    coordinates_json = Column(Text, nullable=True)  # GeoJSON / polyline

    defects = relationship("Defect", back_populates="road_segment")

class Defect(Base):
    __tablename__ = "defects"

    id = Column(Integer, primary_key=True, index=True)
    defect_code = Column(String, unique=True, index=True) # e.g. DEF-1024
    defect_type = Column(String, default="Pothole")       # Pothole, Alligator Crack, Longitudinal Crack, Rutting
    severity = Column(String, default="HIGH")             # CRITICAL, HIGH, MEDIUM, LOW
    confidence = Column(Float, default=0.92)              # AI confidence (0.0 to 1.0)
    priority_score = Column(Integer, default=85)          # 0 - 100 calculated by Priority Engine
    
    # Priority Factors
    factor_severity = Column(Integer, default=82)
    factor_road_importance = Column(Integer, default=90)
    factor_traffic = Column(Integer, default=85)
    factor_risk = Column(Integer, default=92)
    factor_recurrence = Column(Integer, default=70)

    # Location & Road
    latitude = Column(Float, default=28.6139)
    longitude = Column(Float, default=77.2090)
    road_code = Column(String, default="RHI-2048")
    road_name = Column(String, default="Demo Road 07")
    road_segment_id = Column(Integer, ForeignKey("road_segments.id"), nullable=True)

    # Imagery
    image_url = Column(String)
    annotated_image_url = Column(String, nullable=True)
    bbox_json = Column(Text, nullable=True)

    # Status Flow
    # NEW -> ASSIGNED -> IN PROGRESS -> REPAIR SUBMITTED -> AI VERIFICATION -> VERIFIED -> RECURRING
    status = Column(String, default="NEW")
    observation_count = Column(Integer, default=1)
    
    is_recurring = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    road_segment = relationship("RoadSegment", back_populates="defects")
    observations = relationship("Observation", back_populates="defect", cascade="all, delete-orphan")
    work_order = relationship("WorkOrder", back_populates="defect", uselist=False)
    repairs = relationship("Repair", back_populates="defect")
    verifications = relationship("Verification", back_populates="defect")
    warranty_records = relationship("WarrantyRecord", back_populates="defect")
    audit_events = relationship("AuditEvent", back_populates="defect", cascade="all, delete-orphan")

class Observation(Base):
    """Multiple sightings from different vehicles/cameras that cluster into 1 Defect."""
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    defect_id = Column(Integer, ForeignKey("defects.id"))
    observation_code = Column(String)  # e.g., OBS-01
    latitude = Column(Float)
    longitude = Column(Float)
    confidence = Column(Float, default=0.90)
    source = Column(String, default="Patrol Dashcam AI")  # Patrol Dashcam, Citizen App, Drone Scan, Municipal Fleet
    image_url = Column(String, nullable=True)
    captured_at = Column(DateTime, default=datetime.datetime.utcnow)

    defect = relationship("Defect", back_populates="observations")

class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)  # e.g., WO-2048
    defect_id = Column(Integer, ForeignKey("defects.id"), unique=True)
    priority = Column(String, default="CRITICAL")   # CRITICAL, HIGH, MEDIUM, LOW
    assigned_dept = Column(String, default="Road Maintenance Division")
    contractor = Column(String, default="Apex Infra Infrastructure Ltd")
    sla_hours = Column(Integer, default=24)         # 24, 48, 72
    sla_deadline = Column(DateTime, nullable=True)
    
    # Status: ASSIGNED -> IN PROGRESS -> REPAIR SUBMITTED -> AI VERIFICATION -> VERIFIED
    status = Column(String, default="ASSIGNED")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    defect = relationship("Defect", back_populates="work_order")
    repairs = relationship("Repair", back_populates="work_order")

class Repair(Base):
    __tablename__ = "repairs"

    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"))
    defect_id = Column(Integer, ForeignKey("defects.id"))
    contractor_name = Column(String, default="Apex Infra")
    repair_image_url = Column(String)
    material_used = Column(String, default="Cold Mix Bitumen & Polymer Asphalt")
    notes = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)

    work_order = relationship("WorkOrder", back_populates="repairs")
    defect = relationship("Defect", back_populates="repairs")
    verifications = relationship("Verification", back_populates="repair")

class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=True)
    defect_id = Column(Integer, ForeignKey("defects.id"))
    before_image_url = Column(String)
    after_image_url = Column(String)
    is_verified = Column(Boolean, default=False)
    confidence = Column(Float, default=0.968)
    scan_result = Column(String, default="REPAIR VERIFIED") # REPAIR VERIFIED / VERIFICATION FAILED
    defect_remaining_pct = Column(Float, default=0.0)
    ai_engine = Column(String, default="YOLOv8n Verification Pipeline")
    verification_notes = Column(Text, nullable=True)
    verified_at = Column(DateTime, default=datetime.datetime.utcnow)

    repair = relationship("Repair", back_populates="verifications")
    defect = relationship("Defect", back_populates="verifications")

class WarrantyRecord(Base):
    __tablename__ = "warranty_records"

    id = Column(Integer, primary_key=True, index=True)
    defect_id = Column(Integer, ForeignKey("defects.id"))
    contractor = Column(String, default="Apex Infra")
    warranty_months = Column(Integer, default=12)
    start_date = Column(DateTime, default=datetime.datetime.utcnow)
    end_date = Column(DateTime)
    is_recurring = Column(Boolean, default=False)
    recurrence_date = Column(DateTime, nullable=True)
    recurrence_defect_id = Column(String, nullable=True)
    status = Column(String, default="ACTIVE") # ACTIVE, EXPIRED, BREACHED_RECURRENCE

    defect = relationship("Defect", back_populates="warranty_records")

class AuditEvent(Base):
    """Immutable audit trail for complete defect accountability."""
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    defect_id = Column(Integer, ForeignKey("defects.id"))
    event_type = Column(String) # AI_DETECTION, GPS_CAPTURE, DEFECT_CREATED, PRIORITY_ASSIGNED, WORK_ORDER_ISSUED, REPAIR_SUBMITTED, AI_VERIFICATION, WARRANTY_ACTIVE, RECURRENCE_TRIGGERED
    stage = Column(String)      # DETECT, PRIORITIZE, REPAIR, VERIFY, WARRANTY
    title = Column(String)
    description = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    metadata_json = Column(Text, nullable=True)

    defect = relationship("Defect", back_populates="audit_events")
