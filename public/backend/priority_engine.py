"""
Road Health Intelligence (RHI) - 3D Priority Engine
Computes multi-factor road risk index and SLA deadlines.
"""

def calculate_priority(
    defect_type: str,
    severity: str,
    road_code: str = "RHI-2048",
    is_recurring: bool = False,
    traffic_density: str = "HIGH"
):
    """
    Computes 0-100 composite priority score and granular factor breakdown:
    - Severity factor (30%)
    - Road Importance factor (25%)
    - Traffic Exposure factor (20%)
    - Risk Location factor (15%)
    - Recurrence factor (10%)
    """
    severity_map = {
        "CRITICAL": 95,
        "HIGH": 82,
        "MEDIUM": 55,
        "LOW": 30
    }
    sev_val = severity_map.get(severity.upper(), 70)

    # Road importance heuristic based on arterial / expressway status
    if "2048" in road_code or "EXPRESS" in road_code.upper():
        road_importance = 91
    elif "RING" in road_code.upper() or "MAIN" in road_code.upper():
        road_importance = 85
    else:
        road_importance = 68

    # Traffic factor
    traffic_map = {"HIGH": 86, "MEDIUM": 60, "LOW": 35}
    traffic_val = traffic_map.get(traffic_density.upper(), 80)

    # Risk location (e.g. intersections, school zones, high-speed curves)
    risk_val = 94 if sev_val > 75 else 65

    # Recurrence factor
    recurrence_val = 90 if is_recurring else (40 if defect_type.lower() == "pothole" else 30)

    # Weighted calculation
    score = int(
        (0.30 * sev_val) +
        (0.25 * road_importance) +
        (0.20 * traffic_val) +
        (0.15 * risk_val) +
        (0.10 * recurrence_val)
    )
    score = max(10, min(99, score))

    if score >= 80:
        priority_label = "CRITICAL"
        sla_hours = 24
    elif score >= 60:
        priority_label = "HIGH"
        sla_hours = 48
    elif score >= 40:
        priority_label = "MEDIUM"
        sla_hours = 72
    else:
        priority_label = "LOW"
        sla_hours = 120

    return {
        "priority_score": score,
        "priority_label": priority_label,
        "sla_hours": sla_hours,
        "factors": {
            "severity": sev_val,
            "road_importance": road_importance,
            "traffic_exposure": traffic_val,
            "risk_location": risk_val,
            "recurrence": recurrence_val
        }
    }
