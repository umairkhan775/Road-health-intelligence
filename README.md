# Road Health Intelligence (RHI) 🛣️🤖

> **AI-Powered 3D Road Infrastructure Intelligence & Command Platform**  
> *Detect. Prioritize. Repair. Verify. Monitor.*

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-2.0.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Three.js](https://img.shields.io/badge/Three.js-WebGL-black.svg)](https://threejs.org/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-green.svg)](https://leafletjs.com/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Computer%20Vision-red.svg)](https://ultralytics.com/)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel-000000.svg)](https://vercel.com/)

---

## 🌟 Core Concept

**Road Health Intelligence (RHI)** is a full-stack Smart City AI Command Center platform designed to manage the entire lifecycle of road defects:

$$\text{Road Photo} \longrightarrow \text{YOLOv8 AI Detection} \longrightarrow \text{GPS Telemetry} \longrightarrow \text{Haversine Clustering} \longrightarrow \text{Priority Engine} \longrightarrow \text{Work Order} \longrightarrow \text{Contractor Repair} \longrightarrow \text{AI Verification} \longrightarrow \text{Warranty Tracking}$$

---

## 📂 Project Architecture

```
road-health-intelligence/
├── backend/
│   ├── __init__.py            # Backend package initialization
│   ├── main.py                # FastAPI application, REST endpoints & static routes
│   ├── database.py            # SQLite database connection & session generator
│   ├── models.py              # SQLAlchemy ORM models (Defect, WorkOrder, Repair, Audit)
│   ├── ai_engine.py           # YOLOv8n inference pipeline & OpenCV UltraHUD visualizer
│   ├── priority_engine.py     # 0-100 multi-factor risk index & SLA calculator
│   ├── clustering.py          # Haversine spatial clustering algorithm (20m radius)
│   └── seed_data.py           # Initial Smart City road segments & defect database seed
│
├── frontend/
│   ├── index.html             # Single-Page Application (Hero + Command Center)
│   ├── css/
│   │   └── style.css          # Premium Smart City Design System stylesheet
│   ├── js/
│   │   ├── app.js             # Client application logic, Leaflet map, & AI Scanner
│   │   └── three_scene.js     # Three.js WebGL procedural 3D smart city road scene
│   └── assets/                # High-res demo sample road imagery
│       ├── sample_pothole_1.jpg
│       ├── sample_pothole_2.jpg
│       ├── sample_crack_1.jpg
│       ├── sample_repaired_1.jpg
│       └── sample_failed_repair.jpg
│
├── uploads/                   # Upload storage for AI scanner input & annotated HUD overlays
├── vercel.json                # Vercel deployment configuration
├── requirements.txt           # Python backend dependencies
├── .gitignore                 # Git ignore specifications
└── README.md                  # Project documentation & run guide
```

---

## 🚀 Local Setup & Installation Guide

### Prerequisites
* **Python 3.9+** installed on your system.
* A modern web browser (Google Chrome, Edge, Safari, Firefox).

---

### Step 1: Clone or Extract the Project
```bash
# If cloned via Git:
git clone https://github.com/<your-username>/road-health-intelligence.git
cd road-health-intelligence
```

---

### Step 2: Create a Virtual Environment (Recommended)

#### On Windows (PowerShell / Command Prompt):
```powershell
python -m venv venv
.\venv\Scripts\activate
```

#### On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

### Step 4: Run the Application Server
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### Step 5: Open in Your Browser
* **💻 Desktop / Laptop:** Open **[http://localhost:8000](http://localhost:8000)**
* **📱 Mobile / Android (Same Wi-Fi):** Open `http://<YOUR_LOCAL_IP>:8000` *(e.g., `http://192.168.1.8:8000`)*

---

## ☁️ Deploying to Vercel

The project includes a ready-to-deploy `vercel.json` configuration file supporting FastAPI serverless Python functions alongside static frontend hosting.

### Option A: Deploy via Vercel CLI
```bash
npm install -g vercel
vercel
```

### Option B: Deploy via GitHub Repository
1. Push this project to your GitHub account:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Road Health Intelligence"
   git branch -M main
   git remote add origin https://github.com/<your-username>/road-health-intelligence.git
   git push -u origin main
   ```
2. Go to [Vercel Dashboard](https://vercel.com/new).
3. Select **Import Git Repository** and choose your `road-health-intelligence` repository.
4. Click **Deploy**. Vercel will automatically detect `vercel.json` and deploy both the FastAPI backend and frontend.

---

## 🎯 Key Capabilities & Features

### 1. 🌐 3D Smart City Command Center (Three.js WebGL)
* Interactive WebGL 3D city scene with multi-lane asphalt highways, color-coded health edges (Green/Orange/Red), moving road rollers, AI CCTV towers, traffic cones, and floating GPS teardrop pins.
* Holographic floating intelligence cards displaying live network health metrics.

### 2. ◉ AI Road Scanner (YOLOv8 + OpenCV UltraHUD)
* Drag-and-drop road photo analysis or 1-click instant demo samples (*"Sample Pothole 01"*, *"Sample Critical 02"*, *"Sample Crack Pattern"*).
* UltraHUD visualizer drawing stylized corner brackets, severity badges, confidence ratings, and bounding boxes.
* Automated client-side fallback engine guaranteeing 0% failure rate during offline demos.

### 3. ◈ API-Key-Free Road Network Map (Leaflet + OpenStreetMap)
* 100% free OpenStreetMap standard tile integration with zero API key dependencies and zero watermarks.
* Color-coded road polylines:
  * **Green (`#16A34A`):** Healthy segments
  * **Orange (`#F59E0B`):** At-Risk segments
  * **Red (`#DC2626`):** Critical defect segments
* Interactive layer toggles for *Road Segments*, *Defect Locations (📍)*, *CCTV Cameras (📹)*, and *Work Zones (🚧)*.

### 4. ✓ AI Repair Verification Suite
* Independent dual-image computer vision scan comparing pre-repair defect imagery with post-repair asphalt compaction.
* Contractor self-reports cannot close work orders until AI validates compaction depth.
* Automatically triggers 12-month warranty tracking upon verified completion.

### 5. ▤ Immutable Defect Audit Trail
* Complete chronological ledger tracking every milestone from initial optical sighting to verified repair closure.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/system-status` | AI engine & database telemetry |
| `POST` | `/api/detect` | Multipart image upload for YOLOv8 defect detection |
| `GET` | `/api/defects` | List all registered road defects |
| `POST` | `/api/defects` | Create new defect or cluster into existing record |
| `GET` | `/api/work-orders` | Fetch active contractor work orders & SLA deadlines |
| `POST` | `/api/verify-repair` | Run dual-image AI repair verification scan |
| `GET` | `/api/road-segments` | Road network GIS segments & condition metrics |
| `GET` | `/api/analytics` | KPIs & chart analytics data |
| `GET` | `/api/audit/{id}` | Chronological defect audit trail |

---

## 📄 License

This project is open source and available under the **MIT License**.
