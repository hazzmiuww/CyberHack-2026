# Sima Arome Integrated QC System

An end-to-end **AI Quality Control system** for Sima Arome, a natural extracts manufacturer.
Built for **CyberHack 2026**.

It replaces manual, eyeball-based QC and fragmented spreadsheets with an automated computer-vision
pipeline feeding a centralized **Command Center** — a single source of truth for material quality.

> **Problem addressed (CyberHack Focus Areas 01 + 02):** manual QC bottlenecks and fragmented
> systems. Incoming material is graded automatically by AI, and results flow into one dashboard
> instead of living in notebooks and spreadsheets.

---

## 🚀 Quick Start (For Judges & Evaluators)

**Want to run the entire system with one command?**

### Windows Users:
```cmd
start-all.bat
```

**That's it!** The script will:
- ✅ Check prerequisites
- ✅ Install all dependencies
- ✅ Start Backend API, Edge Camera, and Dashboard
- ✅ Open everything in separate windows

**Then open:** http://localhost:3000/qc-dashboard

📖 **Full guide:** See [QUICKSTART.md](QUICKSTART.md) for detailed instructions and troubleshooting.

---

## Architecture

Three nodes, one data flow:

```
┌────────────────────┐     POST /api/qc/detections     ┌────────────────────┐     GET /api/inventory     ┌────────────────────┐
│   NODE A: Edge      │ ──────────────────────────────> │   NODE B: Backend  │ <───────────────────────── │  NODE C: Command   │
│   (AI Vision)       │                                  │   (FastAPI + DB)   │                            │  Center (Next.js)  │
│  YOLOv8 + ByteTrack │                                  │   SQLite store     │                            │   Live dashboard   │
└────────────────────┘                                  └────────────────────┘                            └────────────────────┘
```

| Node | Role | Tech | Status |
| ---- | ---- | ---- | ------ |
| **A — Edge** | Detects & grades lemons from a video stream, sends results | Python, OpenCV, Ultralytics YOLOv8, ByteTrack | ✅ Done |
| **B — Backend** | Receives detections, stores them, serves metrics | FastAPI, SQLAlchemy, SQLite | ✅ Done |
| **C — Command Center** | Real-time QC dashboard (metric cards + log table) | Next.js, BuildPad | 🚧 In progress |

---

## Repository layout

```
edge_camera.py        # Node A — AI vision + tracking, dispatches detections
best.pt               # Custom-trained YOLOv8 model (material_bagus / material_rusak)
sample_lemon.mp4      # Demo input video
backend/
  ├── main.py         # Node B — FastAPI app (API)
  └── requirements.txt
docs/
  └── API.md          # Full API contract (read this for frontend integration)
```

---

## How it works

1. **Node A** runs the YOLOv8 model (`best.pt`) on a video stream, classifying each item as
   `material_bagus` (good) or `material_rusak` (defective).
2. **ByteTrack** assigns a stable `track_id` to each object so the same item isn't counted twice.
3. A confidence gate (`CONFIDENCE_THRESHOLD = 0.45`) filters out weak detections before tracking.
4. For every newly tracked object, Node A fires an **async** `POST` to Node B so the video stream
   never stalls (no frame drops).
5. **Node B** stores each detection and exposes aggregated metrics.
6. **Node C** polls the backend and renders a live dashboard: Total, Bagus, Rusak, and Acceptance Rate.

> Each detection run resets the backend first (`DELETE /api/qc/detections`), so the dashboard always
> reflects a single clean session — ideal for demos.

---

## Running locally

You need **two terminals**: one for the backend, one for the camera.

### 1. Backend (Node B)

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend starts on `http://localhost:8000`. Interactive API docs at `http://localhost:8000/docs`.
Leave this running.

### 2. Edge camera (Node A)

In a second terminal:

```bash
pip install ultralytics opencv-python requests
python edge_camera.py
```

A window opens playing `sample_lemon.mp4` with detection boxes. Press **`q`** to quit.
Detections stream into the backend automatically.

### 3. View the data

Open `http://localhost:8000/api/inventory` in a browser, or use the Swagger UI at `/docs`.

---

## API

See **[`docs/API.md`](docs/API.md)** for the complete request/response contract.

Key endpoints:

| Method | Path                   | Purpose                       |
| ------ | ---------------------- | ----------------------------- |
| `POST` | `/api/qc/detections`   | Edge Node submits a detection |
| `GET`  | `/api/inventory`       | Metrics + detection list      |
| `GET`  | `/api/inventory/stats` | Aggregated stats per class    |

---

## Edge Node configuration

Tunable constants at the top of `edge_camera.py`:

| Constant               | Default                                | Description                              |
| ---------------------- | -------------------------------------- | ---------------------------------------- |
| `MODEL_PATH`           | `best.pt`                              | YOLOv8 model file                        |
| `VIDEO_PATH`           | `sample_lemon.mp4`                     | Input video (swap for a camera index)    |
| `API_BASE`             | `http://localhost:8000`                | Backend base URL                         |
| `CONFIDENCE_THRESHOLD` | `0.45`                                 | Minimum confidence before tracking       |
| `CAMERA_ID`            | `cam_01`                               | Identifier tagged on each detection      |

---

## Team

Built for CyberHack 2026 · Sima Arome challenge.
