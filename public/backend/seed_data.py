"""
Road Health Intelligence (RHI) - Seed Data Generator
Initializes SQLite database with rich smart city defect records, road segments, work orders, verifications, and audit trails.
"""
import datetime
from sqlalchemy.orm import Session
from backend.database import engine, Base, SessionLocal
from backend.models import (
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
                repair_status="1 In Progress",
                length_km=4.2
            ),
            RoadSegment(
                code="RHI-4120",
                name="Industrial Tech Corridor South",
                health_score=54,
                active_defects=24,
                critical_defects=7,
                last_inspection="2 days ago",
                repair_status="8 In Progress",
                length_km=6.0
            )
        ]
        db.add_all(roads)
        db.commit()

        # Refresh roads to get IDs
        for r in roads:
            db.refresh(r)

        # 2. Seed Primary Defect DEF-1024 (Central Featured Defect)
        def1024 = Defect(
            defect_code="DEF-1024",
            defect_type="Pothole",
            severity="HIGH",
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
            road_name="Demo Road 07",
            road_segment_id=roads[0].id,
            image_url="/assets/sample_pothole_1.jpg",
            annotated_image_url="/assets/sample_pothole_1.jpg",
            status="IN PROGRESS",
            observation_count=4,
            is_recurring=False,
            created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=6)
        )
        db.add(def1024)
        db.commit()
        db.refresh(def1024)

        # 3. Seed Observations for DEF-1024 (Demonstrating Clustering Requirement #17)
        obs_list = [
            Observation(
                defect_id=def1024.id,
                observation_code="OBS-01",
                latitude=28.61391,
                longitude=77.20902,
                confidence=0.94,
                source="Patrol Dashcam AI",
                captured_at=datetime.datetime.utcnow() - datetime.timedelta(hours=6, minutes=12)
            ),
            Observation(
                defect_id=def1024.id,
                observation_code="OBS-02",
                latitude=28.61389,
                longitude=77.20898,
                confidence=0.92,
                source="Citizen Mobile App",
                captured_at=datetime.datetime.utcnow() - datetime.timedelta(hours=5, minutes=45)
            ),
            Observation(
                defect_id=def1024.id,
                observation_code="OBS-03",
                latitude=28.61392,
                longitude=77.20904,
                confidence=0.96,
                source="Municipal Fleet AI",
                captured_at=datetime.datetime.utcnow() - datetime.timedelta(hours=4, minutes=30)
            ),
            Observation(
                defect_id=def1024.id,
                observation_code="OBS-04",
                latitude=28.61388,
                longitude=77.20901,
                confidence=0.95,
                source="Drone Infrastructure Scan",
                captured_at=datetime.datetime.utcnow() - datetime.timedelta(hours=3, minutes=10)
            )
        ]
        db.add_all(obs_list)

        # 4. Seed Work Order for DEF-1024
        wo2048 = WorkOrder(
            code="WO-2048",
            defect_id=def1024.id,
            priority="CRITICAL",
            assigned_dept="Road Maintenance Division",
            contractor="Apex Infra Infrastructure Ltd",
            sla_hours=24,
            sla_deadline=datetime.datetime.utcnow() + datetime.timedelta(hours=18),
            status="IN PROGRESS",
            notes="Dispatched emergency mobile asphalt patch team with polymer cold mix."
        )
        db.add(wo2048)

        # 5. Seed Additional Defects (DEF-1025 to DEF-1029)
        def1025 = Defect(
            defect_code="DEF-1025",
            defect_type="Alligator Crack",
            severity="MEDIUM",
            confidence=0.89,
            priority_score=68,
            factor_severity=65,
            factor_road_importance=78,
            factor_traffic=62,
            factor_risk=70,
            factor_recurrence=45,
            latitude=28.6240,
            longitude=77.2185,
            road_code="RHI-1042",
            road_name="Cyber Hub North Corridor",
            road_segment_id=roads[1].id,
            image_url="/assets/sample_crack_1.jpg",
            annotated_image_url="/assets/sample_crack_1.jpg",
            status="REPAIR SUBMITTED",
            observation_count=2,
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
        )

        def1026 = Defect(
            defect_code="DEF-1026",
            defect_type="Pothole",
            severity="CRITICAL",
            confidence=0.96,
            priority_score=92,
            factor_severity=95,
            factor_road_importance=92,
            factor_traffic=89,
            factor_risk=96,
            factor_recurrence=80,
            latitude=28.6350,
            longitude=77.2250,
            road_code="RHI-3091",
            road_name="Metro Outer Bypass - Zone B",
            road_segment_id=roads[2].id,
            image_url="/assets/sample_pothole_2.jpg",
            annotated_image_url="/assets/sample_pothole_2.jpg",
            status="VERIFIED",
            observation_count=3,
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=3)
        )

        def1027 = Defect(
            defect_code="DEF-1027",
            defect_type="Surface Rutting",
            severity="CRITICAL",
            confidence=0.95,
            priority_score=91,
            factor_severity=92,
            factor_road_importance=94,
            factor_traffic=90,
            factor_risk=93,
            factor_recurrence=95,
            latitude=28.6050,
            longitude=77.2340,
            road_code="RHI-4120",
            road_name="Industrial Tech Corridor South",
            road_segment_id=roads[4].id,
            image_url="/assets/sample_pothole_1.jpg",
            annotated_image_url="/assets/sample_pothole_1.jpg",
            status="RECURRING",
            observation_count=5,
            is_recurring=True,
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=7)
        )

        db.add_all([def1025, def1026, def1027])
        db.commit()
        db.refresh(def1025)
        db.refresh(def1026)
        db.refresh(def1027)

        # Work orders for other defects
        wo2049 = WorkOrder(
            code="WO-2049",
            defect_id=def1025.id,
            priority="HIGH",
            assigned_dept="Urban Civil Works",
            contractor="Metro Pavement Corp",
            sla_hours=48,
            status="REPAIR SUBMITTED",
            notes="Surface slurry seal applied. Awaiting AI re-scan."
        )

        wo2050 = WorkOrder(
            code="WO-2050",
            defect_id=def1026.id,
            priority="CRITICAL",
            assigned_dept="Highway Division",
            contractor="Apex Infra Infrastructure Ltd",
            sla_hours=24,
            status="VERIFIED",
            notes="Milling and hot-mix overlay completed. Verified by AI."
        )

        wo2051 = WorkOrder(
            code="WO-2051",
            defect_id=def1027.id,
            priority="CRITICAL",
            assigned_dept="Emergency Response",
            contractor="BuildTech Global",
            sla_hours=24,
            status="RECURRING",
            notes="Defect reappeared 45 days after repair during 12-month warranty period."
        )
        db.add_all([wo2049, wo2050, wo2051])
        db.commit()

        # 6. Seed Verification & Repair Records
        rep1026 = Repair(
            work_order_id=wo2050.id,
            defect_id=def1026.id,
            contractor_name="Apex Infra",
            repair_image_url="/assets/sample_repaired_1.jpg",
            material_used="Superpave Bituminous Concrete (Grade 2)",
            notes="Compaction tests passed, thermal imaging verified even seal."
        )
        db.add(rep1026)
        db.commit()
        db.refresh(rep1026)

        ver1026 = Verification(
            repair_id=rep1026.id,
            defect_id=def1026.id,
            before_image_url="/assets/sample_pothole_2.jpg",
            after_image_url="/assets/sample_repaired_1.jpg",
            is_verified=True,
            confidence=0.968,
            scan_result="REPAIR VERIFIED",
            defect_remaining_pct=0.0,
            ai_engine="YOLOv8n Verification Pipeline",
            verification_notes="AI scan verifies 100% surface restoration without structural cracks."
        )
        db.add(ver1026)

        # 7. Seed Warranty & Recurrence Record for DEF-1027
        warr1027 = WarrantyRecord(
            defect_id=def1027.id,
            contractor="BuildTech Global",
            warranty_months=12,
            start_date=datetime.datetime.utcnow() - datetime.timedelta(days=60),
            end_date=datetime.datetime.utcnow() + datetime.timedelta(days=305),
            is_recurring=True,
            recurrence_date=datetime.datetime.utcnow() - datetime.timedelta(days=2),
            recurrence_defect_id="DEF-1027-REC",
            status="BREACHED_RECURRENCE"
        )
        db.add(warr1027)

        # 8. Seed Immutable Audit Trail for DEF-1024
        audit_events_1024 = [
            AuditEvent(
                defect_id=def1024.id,
                event_type="AI_DETECTION",
                stage="DETECT",
                title="AI Detection Complete",
                description="YOLOv8n model identified HIGH severity Pothole with 94.0% confidence.",
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=6, minutes=12)
            ),
            AuditEvent(
                defect_id=def1024.id,
                event_type="GPS_CAPTURE",
                stage="DETECT",
                title="GPS Telemetry Locked",
                description="Coordinates 28.61390° N, 77.20900° E mapped to Road Segment RHI-2048.",
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=6, minutes=10)
            ),
            AuditEvent(
                defect_id=def1024.id,
                event_type="OBSERVATION_CLUSTERED",
                stage="DETECT",
                title="Observation Clustering",
                description="Spatial Haversine clustering merged 4 separate sightings into parent DEF-1024.",
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=5, minutes=50)
            ),
            AuditEvent(
                defect_id=def1024.id,
                event_type="DEFECT_CREATED",
                stage="DETECT",
                title="Defect Record Generated",
                description="System created official defect entity DEF-1024 on Demo Road 07.",
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=5, minutes=45)
            ),
            AuditEvent(
                defect_id=def1024.id,
                event_type="PRIORITY_ASSIGNED",
                stage="PRIORITIZE",
                title="Priority Engine Calculation",
                description="Priority score computed: 87/100 (CRITICAL). SLA window set to 24 Hours.",
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=5, minutes=40)
            ),
            AuditEvent(
                defect_id=def1024.id,
                event_type="WORK_ORDER_ISSUED",
                stage="REPAIR",
                title="Work Order Dispatched",
                description="Work Order WO-2048 auto-assigned to contractor Apex Infra Infrastructure Ltd.",
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=5, minutes=30)
            ),
            AuditEvent(
                defect_id=def1024.id,
                event_type="REPAIR_IN_PROGRESS",
                stage="REPAIR",
                title="Repair In Progress",
                description="Contractor field unit checked in at location. Cold-mix patch deployed.",
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=2, minutes=15)
            )
        ]
        db.add_all(audit_events_1024)
        db.commit()

        print("[RHI SEED] Database initialization and seeding successful!")
    except Exception as e:
        db.rollback()
        print(f"[RHI SEED] Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db_and_seed()
