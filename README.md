# Sima Arome Integrated QC System

An end-to-end **AI Quality Control system** for Sima Arome, a natural extracts manufacturer.
Built for **CyberHack 2026**.

It replaces manual, eyeball-based QC and fragmented spreadsheets with an automated computer-vision
pipeline feeding a centralized **Command Center** — a single source of truth for material quality.

> **Problem addressed (CyberHack Focus Areas 01 + 02):** manual QC bottlenecks and fragmented
> systems. Incoming material is graded automatically by AI, and results flow into one dashboard
> instead of living in notebooks and spreadsheets.

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
| **C — Command Center** | Real-time QC dashboard (metric cards + log table) | Next.js, BuildPad | ✅ Done |

---

## Repository layout

```
edge_camera.py        # Node A — AI vision + tracking, dispatches detections
best.pt               # Custom-trained YOLOv8 model (material_bagus / material_rusak)
sample_lemon.mp4      # Demo input video
backend/
  ├── main.py         # Node B — FastAPI app (API)
  └── requirements.txt
app/                  # Node C — Next.js pages & routes
components/           # React UI components
docs/
  └── API.md          # Full API contract (read this for frontend integration)
.vscode/
  └── tasks.json      # VS Code tasks to run services
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

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 24 LTS** with pnpm
- A webcam (or use the included `sample_lemon.mp4`)

### Quick Start (VS Code)

Open the project in VS Code, then:

1. Press `Ctrl+Shift+P` → **"Run Task"** → **"Run All Services"**
2. Two terminals open automatically:
   - **Backend API** — `python backend/main.py`
   - **Edge Camera** — `python edge_camera.py`
3. Open a third terminal and run: `pnpm run dev`
4. Open **http://localhost:3000/qc-dashboard** in your browser

### Manual Start (any terminal)

**Terminal 1 — Backend (Node B):**

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend starts on `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

**Terminal 2 — Edge Camera (Node A):**

```bash
pip install ultralytics opencv-python requests
python edge_camera.py
```

A window opens playing `sample_lemon.mp4` with detection boxes. Press **`q`** to quit.

**Terminal 3 — Dashboard (Node C):**

```bash
pnpm install
pnpm run dev
```

Dashboard at `http://localhost:3000/qc-dashboard`.

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
