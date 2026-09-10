"""
Road Health Intelligence (RHI) - Observation Clustering Engine
Clusters multiple geo-located observations into unified defect records using Haversine distance.
"""
import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two points in meters."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def find_matching_defect(lat: float, lon: float, existing_defects, threshold_meters: float = 20.0):
    """
    Finds if an observation matches an existing defect within threshold_meters.
    """
    closest_defect = None
    min_dist = float("inf")

    for defect in existing_defects:
        dist = haversine_distance(lat, lon, defect.latitude, defect.longitude)
        if dist < threshold_meters and dist < min_dist:
            min_dist = dist
            closest_defect = defect

    return closest_defect, min_dist
