"""
Road Health Intelligence (RHI) - Seed Data Generator
Initializes SQLite database with rich smart city defect records, road segments, work orders, verifications, and audit trails.
"""
import os
import sys
import datetime
from sqlalchemy.orm import Session

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

try:
    from backend.database import engine, Base, SessionLocal
    from backend.models import (
        User, RoadSegment, Defect, Observation, WorkOrder, Repair, Verification, WarrantyRecord, AuditEvent
    )
except ImportError:
    from database import engine, Base, SessionLocal
    from models import (
        User, RoadSegment, Defect, Observation, WorkOrder, Repair, Verification, WarrantyRecord, AuditEvent
    )

def init_db_and_seed():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(RoadSegment).count() > 0:
            print("[RHI SEED] Database already initialized.")
            return

        print("[RHI SEED] Seeding database with smart city initial data...")

        # 1. Seed Road Segments
        roads = [
            RoadSegment(
                code="RHI-2048",
                name="Ring Road Expressway - Sector 4",
                health_score=78,
                active_defects=12,
                critical_defects=2,
                last_inspection="Today",
                repair_status="4 In Progress",
                length_km=3.8
            ),
            RoadSegment(
                code="RHI-1042",
                name="Cyber Hub North Corridor",
                health_score=92,
                active_defects=3,
                critical_defects=0,
                last_inspection="Today",
                repair_status="Normal Operations",
                length_km=2.1
            ),
            RoadSegment(
                code="RHI-3091",
                name="Metro Outer Bypass - Zone B",
                health_score=64,
                active_defects=18,
                critical_defects=4,
                last_inspection="Today",
                repair_status="6 In Progress",
                length_km=5.4
            ),
            RoadSegment(
                code="RHI-5012",
                name="Airport Expressway Link",
                health_score=88,
                active_defects=5,
                critical_defects=1,
                last_inspection="Yesterday",
                repair_status="Normal Operations",
                length_km=4.2
            )
        ]
        db.add_all(roads)
        db.commit()

        # 2. Seed Primary Defect DEF-1024
        primary_defect = Defect(
            defect_code="DEF-1024",
            defect_type="Pothole",
            severity="CRITICAL",
            confidence=0.94,
            priority_score=87,
            factor_severity=82,
            factor_road_importance=91,
            factor_traffic=86,
            factor_risk=94,
            factor_recurrence=70,
            latitude=28.6139,
            longitude=77.2090,
            road_code="RHI-2048",
            road_name="Ring Road Expressway - Sector 4",
            road_segment_id=roads[0].id,
            image_url="/assets/sample_pothole_1.jpg",
            annotated_image_url="/assets/sample_pothole_1.jpg",
            status="ASSIGNED",
            observation_count=4,
            is_recurring=False
        )
        db.add(primary_defect)
        db.commit()

        # 3. Seed Observations for DEF-1024
        obs = [
            Observation(defect_id=primary_defect.id, observation_code="OBS-1024-01", latitude=28.6139, longitude=77.2090, confidence=0.94, source="Patrol Dashcam AI #14", image_url="/assets/sample_pothole_1.jpg"),
            Observation(defect_id=primary_defect.id, observation_code="OBS-1024-02", latitude=28.6140, longitude=77.2091, confidence=0.91, source="Citizen Upload App", image_url="/assets/sample_pothole_1.jpg"),
            Observation(defect_id=primary_defect.id, observation_code="OBS-1024-03", latitude=28.6138, longitude=77.2089, confidence=0.88, source="Municipal Fleet Unit 09", image_url="/assets/sample_pothole_1.jpg"),
            Observation(defect_id=primary_defect.id, observation_code="OBS-1024-04", latitude=28.6139, longitude=77.2092, confidence=0.95, source="Drone Survey Alpha", image_url="/assets/sample_pothole_1.jpg")
        ]
        db.add_all(obs)

        # 4. Additional Defects
        d2 = Defect(
            defect_code="DEF-1025",
            defect_type="Alligator Crack",
            severity="HIGH",
            confidence=0.89,
            priority_score=72,
            latitude=28.6250,
            longitude=77.2180,
            road_code="RHI-1042",
            road_name="Cyber Hub North Corridor",
            road_segment_id=roads[1].id,
            image_url="/assets/sample_crack_1.jpg",
            status="IN PROGRESS",
            observation_count=2
        )
        d3 = Defect(
            defect_code="DEF-1026",
            defect_type="Pothole",
            severity="CRITICAL",
            confidence=0.96,
            priority_score=91,
            latitude=28.6010,
            longitude=77.1950,
            road_code="RHI-3091",
            road_name="Metro Outer Bypass - Zone B",
            road_segment_id=roads[2].id,
            image_url="/assets/sample_pothole_2.jpg",
            status="REPAIR SUBMITTED",
            observation_count=3
        )
        d4 = Defect(
            defect_code="DEF-1027",
            defect_type="Longitudinal Crack",
            severity="MEDIUM",
            confidence=0.84,
            priority_score=54,
            latitude=28.6320,
            longitude=77.2050,
            road_code="RHI-5012",
            road_name="Airport Expressway Link",
            road_segment_id=roads[3].id,
            image_url="/assets/sample_crack_1.jpg",
            status="NEW",
            observation_count=1
        )
        db.add_all([d2, d3, d4])
        db.commit()

        # 5. Work Orders
        wo1 = WorkOrder(
            code="WO-2048",
            defect_id=primary_defect.id,
            priority="CRITICAL",
            assigned_dept="Central Arterial Division",
            contractor="Apex Infra Infrastructure Ltd",
            sla_hours=24,
            sla_deadline=datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            status="ASSIGNED",
            notes="Expedite repair due to high traffic volume on Ring Road."
        )
        wo2 = WorkOrder(
            code="WO-2049",
            defect_id=d3.id,
            priority="CRITICAL",
            assigned_dept="Metro Highway Authority",
            contractor="BuildTech Roadways",
            sla_hours=24,
            sla_deadline=datetime.datetime.utcnow() + datetime.timedelta(hours=6),
            status="REPAIR SUBMITTED",
            notes="Repair submitted by contractor. Pending AI Verification."
        )
        db.add_all([wo1, wo2])
        db.commit()

        # 6. Seed Verifications & Warranty
        verif = Verification(
            defect_id=primary_defect.id,
            before_image_url="/assets/sample_pothole_1.jpg",
            after_image_url="/assets/sample_repaired_1.jpg",
            is_verified=True,
            confidence=0.968,
            scan_result="REPAIR VERIFIED (100% COMPACTED)",
            defect_remaining_pct=0.0
        )
        db.add(verif)

        warranty = WarrantyRecord(
            defect_id=primary_defect.id,
            contractor="Apex Infra Infrastructure Ltd",
            warranty_months=12,
            start_date=datetime.datetime.utcnow(),
            end_date=datetime.datetime.utcnow() + datetime.timedelta(days=365),
            status="ACTIVE"
        )
        db.add(warranty)

        # 7. Seed Audit Events
        audits = [
            AuditEvent(defect_id=primary_defect.id, event_type="AI_DETECTION", stage="DETECT", title="AI Optical Sighting (YOLOv8n)", description="Patrol Dashcam unit #14 identified HIGH severity Pothole with 94.0% confidence."),
            AuditEvent(defect_id=primary_defect.id, event_type="GPS_CAPTURE", stage="DETECT", title="GPS Spatial Telemetry Calibrated", description="Coordinates 28.6139° N, 77.2090° E mapped to Segment RHI-2048."),
            AuditEvent(defect_id=primary_defect.id, event_type="CLUSTER_MERGE", stage="DETECT", title="Haversine Multi-Observation Clustering", description="4 independent fleet observations unified into parent record DEF-1024."),
            AuditEvent(defect_id=primary_defect.id, event_type="PRIORITY_CALCULATED", stage="PRIORITIZE", title="Priority Engine Calculation", description="Composite Risk Score computed: 87/100 (CRITICAL). SLA target: 24 Hours."),
            AuditEvent(defect_id=primary_defect.id, event_type="WORK_ORDER_DISPATCH", stage="REPAIR", title="Work Order WO-2048 Dispatched", description="Auto-assigned to contractor Apex Infra Infrastructure Ltd.")
        ]
        db.add_all(audits)
        db.commit()

        print("[RHI SEED] Database seeded successfully.")

    except Exception as e:
        db.rollback()
        print(f"[RHI SEED ERROR] Failed to seed database: {e}")
    finally:
        db.close()
