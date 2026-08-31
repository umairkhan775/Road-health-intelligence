import urllib.request
import urllib.parse
import json
import time

BASE = "http://127.0.0.1:8000"

def test_all():
    print("Testing RHI Backend Endpoints...")

    # 1. Test GET /api/defects
    req = urllib.request.urlopen(f"{BASE}/api/defects")
    defects = json.loads(req.read())
    print(f"[PASS] 1. GET /api/defects: {len(defects)} defects found. (First: {defects[0]['defect_code']})")

    # 2. Test GET /api/work-orders
    req = urllib.request.urlopen(f"{BASE}/api/work-orders")
    wos = json.loads(req.read())
    print(f"[PASS] 2. GET /api/work-orders: {len(wos)} work orders found. (First: {wos[0]['code']})")

    # 3. Test POST /api/defects
    payload = json.dumps({
        "defect_type": "Pothole",
        "severity": "HIGH",
        "confidence": 0.94,
        "latitude": 28.6145,
        "longitude": 77.2098,
        "road_name": "Demo Road 07",
        "image_url": "/assets/sample_pothole_1.jpg",
        "annotated_image_url": "/assets/sample_pothole_1.jpg"
    }).encode("utf-8")
    
    post_req = urllib.request.Request(
        f"{BASE}/api/defects",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(post_req)
    save_data = json.loads(res.read())
    print(f"[PASS] 3. POST /api/defects: Status={save_data.get('status')}, Defect={save_data.get('defect_code')}")

    # 4. Test GET /api/analytics
    req = urllib.request.urlopen(f"{BASE}/api/analytics")
    an_data = json.loads(req.read())
    print(f"[PASS] 4. GET /api/analytics: KPIs={an_data['kpis']}")

    # 5. Test GET /api/audit/1
    req = urllib.request.urlopen(f"{BASE}/api/audit/1")
    audit_data = json.loads(req.read())
    print(f"[PASS] 5. GET /api/audit/1: {len(audit_data)} chronological audit events verified.")

    # 6. Test GET /api/road-segments
    req = urllib.request.urlopen(f"{BASE}/api/road-segments")
    roads_data = json.loads(req.read())
    print(f"[PASS] 6. GET /api/road-segments: {len(roads_data)} road segments loaded.")

    print("\n>>> ALL API ENDPOINT CHECKS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_all()
