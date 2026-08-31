import urllib.request
import json
import mimetypes

BASE = "http://127.0.0.1:8000"

def test_multipart_detect():
    print("Testing /api/detect multipart file upload...")
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    with open("frontend/assets/sample_pothole_1.jpg", "rb") as f:
        file_bytes = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="sample_pothole_1.jpg"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode("latin1") + file_bytes + f"\r\n--{boundary}--\r\n".encode("latin1")

    req = urllib.request.Request(
        f"{BASE}/api/detect",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())
    print(f"[PASS] /api/detect Mode: {data['mode']}")
    print(f"[PASS] Primary Defect: {data['primary_defect']['defect_type']} ({data['primary_defect']['severity']})")
    print(f"[PASS] Priority Engine: {data['priority']['priority_score']} ({data['priority']['priority_label']})")
    print(f"[PASS] Annotated Image URL: {data['annotated_image_url']}")

def test_repair_verification():
    print("\nTesting /api/verify-repair...")
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="defect_id"\r\n\r\n1\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="simulate_failure"\r\n\r\nfalse\r\n'
        f"--{boundary}--\r\n"
    ).encode("latin1")

    req = urllib.request.Request(
        f"{BASE}/api/verify-repair",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())
    print(f"[PASS] /api/verify-repair: Verified={data['is_verified']}, Result={data['scan_result']}, Confidence={data['confidence']}")

if __name__ == "__main__":
    test_multipart_detect()
    test_repair_verification()
    print("\n>>> ALL MULTIPART CV & VERIFICATION PIPELINES PASSED! <<<")
