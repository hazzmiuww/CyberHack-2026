<div align="center">

<img width="198" height="99" alt="Property 1=kenang logo - gradient" src="https://github.com/user-attachments/assets/e5ac66dc-48b6-4f10-bb1a-9f3342d371b9" />


# Kenang — AI Material Quality Sorting

**Automated visual quality control for Sima Arome, a natural-extracts manufacturer.**
Built for CyberHack 2026.

[Live Dashboard](https://cyber-hack-2026.vercel.app/qc-dashboard) · [API](https://cyberhack-2026-production.up.railway.app/)

</div>

---

## What it does

Sima Arome grades incoming raw materials (e.g. fruit) by eye — slow, inconsistent, and a
bottleneck when trained staff aren't available. **Kenang** replaces that with an AI camera that
classifies each item as **good** (`material_bagus`) or **defective** (`material_rusak`) in real
time, and streams the results to a live web dashboard — one source of truth instead of notebooks
and spreadsheets.

This directly addresses CyberHack Focus Areas **01 (Integrated Operations)** and
**02 (AI for Raw-Material QC)**.

## Live demo

| Service | URL |
| ------- | --- |
| **Dashboard** (Command Center) | https://cyber-hack-2026.vercel.app/qc-dashboard |
| **Backend API** | https://cyberhack-2026-production.up.railway.app/ |

> The dashboard shows live data once the edge camera is running and streaming detections.

## How it works

```
┌─────────────────────┐   POST detections   ┌────────────────────┐   GET inventory   ┌─────────────────────┐
│  Edge Camera (AI)   │ ──────────────────> │   Backend API      │ <──────────────── │  Command Center      │
│  YOLOv8 + ByteTrack │                     │   FastAPI + SQLite │                   │  Next.js dashboard   │
└─────────────────────┘                     └────────────────────┘                   └─────────────────────┘
   runs on a device                            hosted on Railway                        hosted on Vercel
```

1. The AI camera runs a custom **YOLOv8** model (`best.pt`) on a camera/video feed.
2. **ByteTrack** assigns each item a stable ID so the same object is never counted twice.
3. A confidence gate (≥ 0.45) filters out weak detections before counting.
4. Each new item is sent asynchronously to the backend (no video lag).
5. The dashboard polls the backend and shows **Total**, **Good**, **Defective**, and
   **Acceptance Rate** with a live detection log.

## Tech stack

| Layer | Technology |
| ----- | ---------- |
| **AI / Vision** | Python, OpenCV, Ultralytics YOLOv8, ByteTrack |
| **Backend** | FastAPI, SQLAlchemy, SQLite |
| **Frontend** | Next.js (App Router), React, TypeScript, Mantine (BuildPad UI) |
| **Hosting** | Vercel (frontend) · Railway (backend) |

## Running locally

### Prerequisites

- Python 3.10+ with pip
- Node.js 20+ with pnpm
- A webcam, or use the bundled `sample_lemon.mp4`

### Easiest way (VS Code, one click)

1. Open the project in VS Code.
2. `Ctrl+Shift+P` → **Run Task** → **Run All Services** (starts the backend API + edge camera together).
3. In a terminal, start the dashboard:
   ```bash
   pnpm install
   pnpm run dev
   ```
4. Open **http://localhost:3000/qc-dashboard**.

### Manual (three terminals)

```bash
# 1 — Backend
cd backend && pip install -r requirements.txt && python main.py

# 2 — Edge camera
pip install ultralytics opencv-python requests
python edge_camera.py

# 3 — Dashboard
pnpm install && pnpm run dev
```

Press **`q`** in the camera window to stop it.

> By default the camera sends detections to the **hosted** backend so they appear on the live
> dashboard. To use a local backend instead, set `QC_BACKEND_URL=http://localhost:8000` before
> running `edge_camera.py`.

## API

Full contract in [`docs/API.md`](docs/API.md).

| Method | Path | Purpose |
| ------ | ---- | ------- |
| `POST` | `/api/qc/detections` | Camera submits a detection |
| `GET`  | `/api/inventory` | Counts, acceptance rate, detection list |
| `GET`  | `/api/inventory/stats` | Aggregated stats per class |

## Configuration

Key constants in `edge_camera.py`:

| Constant | Default | Description |
| -------- | ------- | ----------- |
| `MODEL_PATH` | `best.pt` | YOLOv8 model file |
| `VIDEO_PATH` | `0` | Webcam index, or a video path like `"sample_lemon.mp4"` |
| `CONFIDENCE_THRESHOLD` | `0.45` | Minimum confidence before an item is counted |
| `QC_BACKEND_URL` (env) | hosted Railway URL | Backend the camera sends detections to |

---

<div align="center">
Built for CyberHack 2026 · Sima Arome challenge
</div>
