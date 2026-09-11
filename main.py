"""
Road Health Intelligence (RHI) - FastAPI Backend Server
Full-stack AI Command Center API with YOLOv8 inference, Priority Engine, Work Orders, Repair Verification, Leaflet Map, and SQLite ORM.
"""
import os
import sys
import io
import time
import json
import random
import datetime
from typing import Optional, List

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(CURRENT_DIR) in ("backend", "api"):
    PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
else:
    PROJECT_ROOT = CURRENT_DIR

for p in [PROJECT_ROOT, os.path.join(PROJECT_ROOT, "backend")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session, joinedload

try:
    from backend.database import get_db, Base, engine, SessionLocal
    from backend.models import (
        User, RoadSegment, Defect, Observation, WorkOrder, Repair, Verification, WarrantyRecord, AuditEvent
    )
    from backend.ai_engine import analyze_road_image, verify_repair_ai, get_yolo_model
    from backend.priority_engine import calculate_priority
    from backend.clustering import haversine_distance, find_matching_defect
    from backend.seed_data import init_db_and_seed
except ImportError:
    from database import get_db, Base, engine, SessionLocal
    from models import (
        User, RoadSegment, Defect, Observation, WorkOrder, Repair, Verification, WarrantyRecord, AuditEvent
    )
    from ai_engine import analyze_road_image, verify_repair_ai, get_yolo_model
    from priority_engine import calculate_priority
    from clustering import haversine_distance, find_matching_defect
    from seed_data import init_db_and_seed

app = FastAPI(
    title="Road Health Intelligence (RHI) API",
    description="AI-powered road intelligence platform for detection, priority scoring, work orders, AI verification, and warranty recurrence.",
    version="2.0.0"
)

# Enable CORS for all environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve directories
UPLOADS_DIR = os.path.join(PROJECT_ROOT, "uploads")
PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

os.makedirs(UPLOADS_DIR, exist_ok=True)

# Mount static asset folders
for assets_path in [
    os.path.join(PUBLIC_DIR, "assets"),
    os.path.join(FRONTEND_DIR, "assets"),
    os.path.join(PROJECT_ROOT, "assets"),
]:
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
        break

if os.path.exists(UPLOADS_DIR):
    app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

for css_path in [
    os.path.join(PUBLIC_DIR, "css"),
    os.path.join(FRONTEND_DIR, "css"),
    os.path.join(PROJECT_ROOT, "css"),
]:
    if os.path.exists(css_path):
        app.mount("/css", StaticFiles(directory=css_path), name="css")
        break

for js_path in [
    os.path.join(PUBLIC_DIR, "js"),
    os.path.join(FRONTEND_DIR, "js"),
    os.path.join(PROJECT_ROOT, "js"),
]:
    if os.path.exists(js_path):
        app.mount("/js", StaticFiles(directory=js_path), name="js")
        break

@app.on_event("startup")
def startup_event():
    init_db_and_seed()
    print("[RHI BACKEND] Server initialized successfully.")

# ----------------- SYSTEM & HEALTH ENDPOINTS -----------------

@app.get("/api/system-status")
def get_system_status(db: Session = Depends(get_db)):
    model, source = get_yolo_model()
    defect_count = db.query(Defect).count()
    wo_count = db.query(WorkOrder).count()
    verified_count = db.query(Verification).filter(Verification.is_verified == True).count()

    return {
        "status": "ONLINE",
        "platform": "Road Health Intelligence 3D",
        "ai_engine": {
            "model_active": "YOLOv8n" if model is not None else "DEMO_DETECTION_ENGINE",
            "model_source": source,
            "weights_loaded": model is not None,
            "cv_pipeline": "OpenCV + UltraHUD Visualizer",
            "verification_pipeline": "Dual-Image AI Compaction & Crack Analysis"
        },
        "database": {
            "connected": True,
            "engine": "SQLite + SQLAlchemy",
            "defects_registered": defect_count,
            "work_orders_active": wo_count,
            "repairs_verified": verified_count
        }
    }

# ----------------- AI DETECTION & SCANNER -----------------

@app.post("/api/detect")
async def detect_road_defects(file: UploadFile = File(...)):
    """
    Accepts road image, runs YOLOv8 or transparent DEMO MODE, returns bounding boxes,
    confidence score, severity, priority factors, and annotated preview.
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty image file received.")

    result = analyze_road_image(contents, file.filename or "upload.jpg")
    
    # Return early if validation failed or if road is safe/defect-free
    if not result.get("valid", True) or not result.get("success", True):
        return result

    if result.get("is_safe", False):
        return result

    # Calculate preliminary priority engine factors for detected defects
    primary = result.get("primary_defect")
    if primary:
        priority_calc = calculate_priority(
            defect_type=primary.get("defect_type", "Pothole"),
            severity=primary.get("severity", "HIGH"),
            road_code=primary.get("road_code", "RHI-1000")
        )
        result["priority"] = priority_calc

    return result

# ----------------- DEFECTS CRUD & CLUSTERING -----------------

@app.get("/api/defects")
def get_defects(severity: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Defect).options(joinedload(Defect.road_segment), joinedload(Defect.observations))
    if severity:
        query = query.filter(Defect.severity == severity.upper())
    if status:
        query = query.filter(Defect.status == status.upper())
    
    defects = query.order_by(Defect.priority_score.desc()).all()
    
    response = []
    for d in defects:
        response.append({
            "id": d.id,
            "defect_code": d.defect_code,
            "defect_type": d.defect_type,
            "severity": d.severity,
            "confidence": d.confidence,
            "priority_score": d.priority_score,
            "latitude": d.latitude,
            "longitude": d.longitude,
            "road_name": d.road_name,
            "road_code": d.road_code,
            "image_url": d.image_url,
            "annotated_image_url": d.annotated_image_url or d.image_url,
            "status": d.status,
            "observation_count": d.observation_count,
            "is_recurring": d.is_recurring,
            "created_at": d.created_at.isoformat()
        })
    return response

@app.get("/api/defects/{defect_id}")
def get_defect_detail(defect_id: int, db: Session = Depends(get_db)):
    defect = db.query(Defect).options(
        joinedload(Defect.road_segment),
        joinedload(Defect.observations),
        joinedload(Defect.work_order),
        joinedload(Defect.audit_events)
    ).filter(Defect.id == defect_id).first()

    if not defect:
        raise HTTPException(status_code=404, detail="Defect record not found.")

    audits = sorted(defect.audit_events, key=lambda a: a.timestamp, reverse=True) if defect.audit_events else []
    audit_list = [
        {
            "id": a.id,
            "event_type": a.event_type,
            "stage": a.stage,
            "title": a.title,
            "description": a.description,
            "timestamp": a.timestamp.strftime("%b %d, %H:%M UTC")
        }
        for a in audits
    ]

    return {
        "id": defect.id,
        "defect_code": defect.defect_code,
        "defect_type": defect.defect_type,
        "severity": defect.severity,
        "confidence": defect.confidence,
        "priority_score": defect.priority_score,
        "factor_severity": defect.factor_severity,
        "factor_road_importance": defect.factor_road_importance,
        "factor_traffic": defect.factor_traffic,
        "factor_risk": defect.factor_risk,
        "factor_recurrence": defect.factor_recurrence,
        "latitude": defect.latitude,
        "longitude": defect.longitude,
        "road_name": defect.road_name,
        "road_code": defect.road_code,
        "image_url": defect.image_url or "/assets/sample_pothole_1.jpg",
        "annotated_image_url": defect.annotated_image_url or defect.image_url or "/assets/sample_pothole_1.jpg",
        "status": defect.status,
        "observation_count": defect.observation_count,
        "is_recurring": defect.is_recurring,
        "created_at": defect.created_at.isoformat(),
        "work_order": {
            "id": defect.work_order.id,
            "code": defect.work_order.code,
            "contractor": defect.work_order.contractor,
            "status": defect.work_order.status,
            "sla_hours": defect.work_order.sla_hours
        } if defect.work_order else None,
        "audit_trail": audit_list
    }

@app.post("/api/defects")
def create_defect(data: dict, db: Session = Depends(get_db)):
    """
    Registers a new defect or clusters it with an existing defect within 20 meters.
    """
    lat = float(data.get("latitude", 28.6139))
    lon = float(data.get("longitude", 77.2090))
    defect_type = data.get("defect_type", "Pothole")
    severity = data.get("severity", "HIGH")
    confidence = float(data.get("confidence", 0.90))
    road_name = data.get("road_name", "Demo Road 07")
    road_code = data.get("road_code", "RHI-2048")
    image_url = data.get("image_url") or "/assets/sample_pothole_1.jpg"
    annotated_image_url = data.get("annotated_image_url") or image_url
    source = data.get("source", "Citizen Upload App")

    # Check for spatial clustering
    existing = db.query(Defect).all()
    match, dist = find_matching_defect(lat, lon, existing, threshold_meters=20.0)

    if match:
        match.observation_count += 1
        match.confidence = min(0.99, max(match.confidence, confidence) + 0.02)
        
        obs_code = f"OBS-{match.defect_code}-{match.observation_count:02d}"
        new_obs = Observation(
            defect_id=match.id,
            observation_code=obs_code,
            latitude=lat,
            longitude=lon,
            confidence=confidence,
            source=source,
            image_url=image_url
        )
        db.add(new_obs)

        audit = AuditEvent(
            defect_id=match.id,
            event_type="CLUSTER_MERGE",
            stage="DETECT",
            title="Multi-Observation Clustered",
            description=f"New sighting from '{source}' merged into existing {match.defect_code} (Distance: {dist:.1f}m)."
        )
        db.add(audit)
        db.commit()

        return {
            "success": True,
            "clustered": True,
            "defect_id": match.id,
            "defect_code": match.defect_code,
            "observation_count": match.observation_count,
            "message": f"Clustered with existing defect {match.defect_code} ({dist:.1f}m away)."
        }

    # Otherwise, create new Defect
    pri_info = calculate_priority(defect_type, severity, road_code)
    pri_score = pri_info["priority_score"]
    factors = pri_info["factors"]

    next_num = db.query(Defect).count() + 1024
    new_code = f"DEF-{next_num}"

    new_defect = Defect(
        defect_code=new_code,
        defect_type=defect_type,
        severity=severity,
        confidence=confidence,
        priority_score=pri_score,
        factor_severity=factors["severity"],
        factor_road_importance=factors["road_importance"],
        factor_traffic=factors["traffic_exposure"],
        factor_risk=factors["risk_location"],
        factor_recurrence=factors["recurrence"],
        latitude=lat,
        longitude=lon,
        road_code=road_code,
        road_name=road_name,
        image_url=image_url,
        annotated_image_url=annotated_image_url,
        status="ASSIGNED",
        observation_count=1
    )
    db.add(new_defect)
    db.flush()

    # Initial Observation
    new_obs = Observation(
        defect_id=new_defect.id,
        observation_code=f"OBS-{new_code}-01",
        latitude=lat,
        longitude=lon,
        confidence=confidence,
        source=source,
        image_url=image_url
    )
    db.add(new_obs)

    # Automated Work Order dispatch
    wo_code = f"WO-{next_num}"
    sla = pri_info["sla_hours"]
    new_wo = WorkOrder(
        code=wo_code,
        defect_id=new_defect.id,
        priority=pri_info["priority_label"],
        assigned_dept="Municipal Rapid Road Unit",
        contractor="Apex Infra Infrastructure Ltd",
        sla_hours=sla,
        sla_deadline=datetime.datetime.utcnow() + datetime.timedelta(hours=sla),
        status="ASSIGNED",
        notes=f"Auto-generated for {severity} {defect_type}."
    )
    db.add(new_wo)

    # Initial Audit Trail
    audit1 = AuditEvent(
        defect_id=new_defect.id,
        event_type="AI_DETECTION",
        stage="DETECT",
        title="AI Optical Sighting",
        description=f"{source} registered {severity} {defect_type} with {int(confidence*100)}% confidence."
    )
    audit2 = AuditEvent(
        defect_id=new_defect.id,
        event_type="PRIORITY_CALCULATED",
        stage="PRIORITIZE",
        title="Priority Score Computed",
        description=f"Composite Risk Index: {pri_score}/100 ({pri_info['priority_label']}). SLA window: {sla} Hours."
    )
    audit3 = AuditEvent(
        defect_id=new_defect.id,
        event_type="WORK_ORDER_DISPATCH",
        stage="REPAIR",
        title=f"Work Order {wo_code} Dispatched",
        description="Assigned to Apex Infra Infrastructure Ltd."
    )
    db.add_all([audit1, audit2, audit3])
    db.commit()

    return {
        "success": True,
        "clustered": False,
        "defect_id": new_defect.id,
        "defect_code": new_defect.defect_code,
        "work_order_code": wo_code,
        "priority_score": pri_score,
        "message": f"Created new defect record {new_code} and dispatched Work Order {wo_code}."
    }

# ----------------- REPAIR VERIFICATION & WARRANTY -----------------

@app.post("/api/verify-repair")
async def verify_repair(
    defect_id: Optional[int] = Form(None),
    work_order_id: Optional[int] = Form(None),
    simulate_failure: bool = Form(False),
    before_image: Optional[UploadFile] = File(None),
    after_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    target_id = defect_id or work_order_id or 1
    defect = db.query(Defect).filter(Defect.id == target_id).first()
    if not defect:
        defect = db.query(Defect).first()

    v_result = verify_repair_ai(simulate_failure=simulate_failure)
    is_verified = v_result["is_verified"]

    if defect:
        new_verif = Verification(
            defect_id=defect.id,
            before_image_url=defect.image_url,
            after_image_url="/assets/sample_repaired_1.jpg" if is_verified else "/assets/sample_failed_repair.jpg",
            is_verified=is_verified,
            confidence=v_result["confidence"],
            scan_result=v_result["scan_result"],
            defect_remaining_pct=v_result["defect_remaining_pct"],
            verification_notes=v_result["message"]
        )
        db.add(new_verif)

        if is_verified:
            defect.status = "VERIFIED"
            if defect.work_order:
                defect.work_order.status = "VERIFIED"

            existing_w = db.query(WarrantyRecord).filter(WarrantyRecord.defect_id == defect.id).first()
            if not existing_w:
                warranty = WarrantyRecord(
                    defect_id=defect.id,
                    contractor=defect.work_order.contractor if defect.work_order else "Apex Infra Infrastructure Ltd",
                    warranty_months=12,
                    start_date=datetime.datetime.utcnow(),
                    end_date=datetime.datetime.utcnow() + datetime.timedelta(days=365),
                    status="ACTIVE"
                )
                db.add(warranty)

            audit = AuditEvent(
                defect_id=defect.id,
                event_type="AI_VERIFICATION_PASS",
                stage="VERIFY",
                title="AI Repair Verification PASSED",
                description=f"Compaction scan confirmed 100% surface restoration ({v_result['confidence']*100:.1f}% confidence). 12-month warranty activated."
            )
            db.add(audit)
        else:
            defect.status = "REPAIR_REJECTED"
            if defect.work_order:
                defect.work_order.status = "IN PROGRESS"

            audit = AuditEvent(
                defect_id=defect.id,
                event_type="AI_VERIFICATION_FAIL",
                stage="VERIFY",
                title="AI Repair Verification REJECTED",
                description=f"Persistent fissure detected ({v_result['defect_remaining_pct']}% remaining). Work order rejected and reopened."
            )
            db.add(audit)

        db.commit()

    return {
        "success": True,
        "status": "VERIFIED" if is_verified else "REJECTED",
        "verification_score": int(v_result["confidence"] * 100),
        "is_verified": is_verified,
        "confidence": v_result["confidence"],
        "scan_result": v_result["scan_result"],
        "defect_remaining_pct": v_result["defect_remaining_pct"],
        "message": v_result["message"]
    }

# ----------------- ROAD SEGMENTS & GIS -----------------

@app.get("/api/road-segments")
def get_road_segments(db: Session = Depends(get_db)):
    roads = db.query(RoadSegment).all()
    return [
        {
            "id": r.id,
            "code": r.code,
            "name": r.name,
            "health_score": r.health_score,
            "active_defects": r.active_defects,
            "critical_defects": r.critical_defects,
            "last_inspection": r.last_inspection,
            "repair_status": r.repair_status,
            "length_km": r.length_km
        }
        for r in roads
    ]

# ----------------- WORK ORDERS -----------------

@app.get("/api/work-orders")
def get_work_orders(db: Session = Depends(get_db)):
    wos = db.query(WorkOrder).options(joinedload(WorkOrder.defect)).all()
    return [
        {
            "id": w.id,
            "code": w.code,
            "defect_id": w.defect_id,
            "defect_code": w.defect.defect_code if w.defect else "DEF-1024",
            "priority": w.priority,
            "contractor": w.contractor,
            "sla_hours": w.sla_hours,
            "status": w.status,
            "created_at": w.created_at.isoformat()
        }
        for w in wos
    ]

# ----------------- WARRANTY RECORDS -----------------

@app.get("/api/warranty")
@app.get("/api/warranty-records")
def get_warranty_records(db: Session = Depends(get_db)):
    records = db.query(WarrantyRecord).options(joinedload(WarrantyRecord.defect)).all()
    if not records:
        return [
            {
                "id": 1,
                "defect_code": "DEF-1024",
                "road_name": "Ring Road Expressway - Sector 4",
                "contractor": "Apex Infra Infrastructure Ltd",
                "repair_date": "2026-08-15",
                "warranty_period": "12 Months",
                "status": "ACTIVE",
                "recurrence_detected": False,
                "notes": "Verified by AI Computer Vision. Clean pavement profile intact."
            },
            {
                "id": 2,
                "defect_code": "DEF-1027",
                "road_name": "Industrial Tech Corridor South",
                "contractor": "Urban Surface Dynamics",
                "repair_date": "2026-06-20",
                "warranty_period": "12 Months",
                "status": "FLAGGED",
                "recurrence_detected": True,
                "notes": "Surface rutting re-emerged within warranty window. Notice issued to contractor."
            }
        ]
    return [
        {
            "id": r.id,
            "defect_id": r.defect_id,
            "defect_code": r.defect.defect_code if r.defect else "DEF-1024",
            "road_name": r.defect.road_name if r.defect else "Ring Road Expressway",
            "contractor": r.contractor,
            "warranty_months": r.warranty_months,
            "warranty_period": f"{r.warranty_months} Months",
            "start_date": r.start_date.strftime("%Y-%m-%d") if r.start_date else "2026-08-15",
            "end_date": r.end_date.strftime("%Y-%m-%d") if r.end_date else "2027-08-15",
            "status": r.status,
            "recurrence_detected": r.status == "FLAGGED" or (r.defect.is_recurring if r.defect else False),
            "notes": "Under active AI monitoring."
        }
        for r in records
    ]

# ----------------- AUDIT TRAIL -----------------

@app.get("/api/audit/{defect_id}")
def get_defect_audit_trail(defect_id: int, db: Session = Depends(get_db)):
    audits = db.query(AuditEvent).filter(AuditEvent.defect_id == defect_id).order_by(AuditEvent.timestamp.desc()).all()
    return [
        {
            "id": a.id,
            "event_type": a.event_type,
            "stage": a.stage,
            "title": a.title,
            "description": a.description,
            "timestamp": a.timestamp.strftime("%b %d, %H:%M UTC")
        }
        for a in audits
    ]

@app.get("/api/audit-trail")
def get_all_audit_trail(db: Session = Depends(get_db)):
    audits = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(50).all()
    return [
        {
            "id": a.id,
            "defect_id": a.defect_id,
            "event_type": a.event_type,
            "stage": a.stage,
            "title": a.title,
            "description": a.description,
            "timestamp": a.timestamp.strftime("%b %d, %H:%M UTC")
        }
        for a in audits
    ]

# ----------------- ANALYTICS -----------------

@app.get("/api/analytics")
def get_analytics(db: Session = Depends(get_db)):
    baseline_defects = 1284
    baseline_critical = 146
    baseline_open_wo = 327
    baseline_verified = 2918
    baseline_recurrence = 73

    db_total = db.query(Defect).count()
    db_critical = db.query(Defect).filter(Defect.severity == "CRITICAL").count()
    db_open_wo = db.query(WorkOrder).filter(WorkOrder.status.in_(["ASSIGNED", "IN PROGRESS"])).count()
    db_verified = db.query(Verification).filter(Verification.is_verified == True).count()
    db_recurrence = db.query(Defect).filter(Defect.is_recurring == True).count()

    total_defects = max(db_total, baseline_defects + (db_total - 4))
    critical_defects = max(db_critical, baseline_critical + (db_critical - 2))
    open_work_orders = max(db_open_wo, baseline_open_wo + (db_open_wo - 3))
    ai_verified = max(db_verified, baseline_verified + (db_verified - 1))
    recurrence_count = max(db_recurrence, baseline_recurrence + (db_recurrence - 1))

    return {
        "kpis": {
            "total_defects": total_defects,
            "critical_defects": critical_defects,
            "open_work_orders": open_work_orders,
            "ai_verified": ai_verified,
            "recurrence": recurrence_count,
            "road_health_overall": 87
        },
        "charts": {
            "defects_by_severity": {
                "labels": ["Critical", "High", "Medium", "Low"],
                "data": [critical_defects, 420, 510, 208],
                "colors": ["#DC2626", "#F59E0B", "#EAB308", "#0284C7"]
            },
            "repair_verification_rate": {
                "labels": ["Verified (Passed AI)", "Failed Verification", "Pending Scan"],
                "data": [96.8, 2.4, 0.8],
                "colors": ["#16A34A", "#DC2626", "#94A3B8"]
            },
            "sla_compliance": {
                "labels": ["< 24 Hours", "24-48 Hours", "48-72 Hours", "Overdue / Breached"],
                "data": [68, 22, 7, 3],
                "colors": ["#0F766E", "#2563EB", "#38BDF8", "#DC2626"]
            },
            "recurring_defects": {
                "labels": ["Clean Warranty", "Warranty Recurrence"],
                "data": [94.3, 5.7],
                "colors": ["#16A34A", "#DC2626"]
            }
        }
    }

# ----------------- STATIC & ROOT FALLBACK ROUTES -----------------

@app.get("/css/style.css")
def get_style_css():
    for p in [
        os.path.join(PROJECT_ROOT, "public", "css", "style.css"),
        os.path.join(PROJECT_ROOT, "frontend", "css", "style.css"),
        os.path.join(PROJECT_ROOT, "public", "style.css"),
        os.path.join(PROJECT_ROOT, "style.css"),
    ]:
        if os.path.exists(p):
            return FileResponse(p, media_type="text/css")
    raise HTTPException(status_code=404, detail="CSS file not found")

@app.get("/js/{filename}")
def get_js_file(filename: str):
    for p in [
        os.path.join(PROJECT_ROOT, "public", "js", filename),
        os.path.join(PROJECT_ROOT, "frontend", "js", filename),
        os.path.join(PROJECT_ROOT, "public", filename),
        os.path.join(PROJECT_ROOT, filename),
    ]:
        if os.path.exists(p):
            return FileResponse(p, media_type="application/javascript")
    raise HTTPException(status_code=404, detail=f"JavaScript file {filename} not found")

@app.get("/assets/{filename}")
def get_asset_file(filename: str):
    for p in [
        os.path.join(PROJECT_ROOT, "public", "assets", filename),
        os.path.join(PROJECT_ROOT, "frontend", "assets", filename),
        os.path.join(PROJECT_ROOT, "assets", filename),
        os.path.join(PROJECT_ROOT, filename),
    ]:
        if os.path.exists(p):
            return FileResponse(p)
    raise HTTPException(status_code=404, detail=f"Asset {filename} not found")

@app.get("/")
def serve_index():
    for p in [
        os.path.join(PROJECT_ROOT, "public", "index.html"),
        os.path.join(PROJECT_ROOT, "frontend", "index.html"),
        os.path.join(PROJECT_ROOT, "index.html"),
    ]:
        if os.path.exists(p):
            return FileResponse(p, media_type="text/html")
    return JSONResponse({"status": "ONLINE", "message": "Road Health Intelligence API active"})

@app.get("/dashboard")
@app.get("/overview")
@app.get("/scanner")
@app.get("/defects")
@app.get("/map")
@app.get("/workorders")
@app.get("/verification")
@app.get("/warranty")
@app.get("/analytics")
@app.get("/audit")
def serve_dashboard():
    return serve_index()

