<div align="center">

<img width="198" height="99" alt="Property 1=kenang logo - gradient" src="https://github.com/user-attachments/assets/e5ac66dc-48b6-4f10-bb1a-9f3342d371b9" />


# Kenang — AI Material Quality Sorting

**Automated visual quality control for Sima Arome, a natural-extracts manufacturer.**
Built for CyberHack 2026.

[Live Dashboard](https://cyber-hack-2026.vercel.app/qc-dashboard) · [API](https://cyberhack-2026-production.up.railway.app/)

</div>

> **Why "Kenang"?** From the Indonesian word for *memory / to remember* — because every piece of
> raw material deserves to be recorded, traced, and accounted for.

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

<!--
  📸 SCREENSHOT: replace the line below with a screenshot or GIF of the live dashboard.
  Easiest way: open the dashboard, take a screenshot, drag it into this file on GitHub's
  web editor — GitHub uploads it and inserts a markdown image link automatically.
-->
<!-- ![Kenang dashboard](public/dashboard-screenshot.png) -->

## Why it matters

- **Removes the manual-QC bottleneck** — grading no longer stalls when trained inspectors aren't on shift.
- **No double-counting** — ByteTrack assigns each item a stable ID, so one object is counted exactly once.
- **Single source of truth** — results live in one dashboard instead of scattered spreadsheets across shifts.
- **Auditable** — every detection is timestamped and stored, not lost in someone's notebook.
- **Scalable to new materials** — add a labelled dataset, retrain the model, redeploy — the pipeline stays the same.

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

> **On model accuracy:** the current model is an early-stage prototype trained on a limited
> dataset, so confidence scores are modest. The `CONFIDENCE_THRESHOLD` (0.45) is intentionally
> conservative to keep the pipeline responsive for the demo. Improving accuracy with a larger,
> better-labelled dataset is the top item on the roadmap — the architecture (capture → detect →
> track → store → visualize) stays exactly the same as the model improves.

## Tech stack

| Layer | Technology |
| ----- | ---------- |
| **AI / Vision** | Python, OpenCV, Ultralytics YOLOv8, ByteTrack |
| **Backend** | FastAPI, SQLAlchemy, SQLite |
| **Frontend** | Next.js (App Router), React, TypeScript, Mantine (BuildPad UI) |
| **Hosting** | Vercel (frontend) · Railway (backend) |

## Usage

The dashboard and backend are **already deployed** — you don't need to run them yourself.
You only run the **edge camera** to feed live detections.

### Demo (recommended) — uses the live deployment

1. Open the project in VS Code.
2. `Ctrl+Shift+P` → **Run Task** → **Run Edge Camera**.
   - The camera sends detections to the hosted backend automatically.
3. Open the live dashboard: **https://cyber-hack-2026.vercel.app/qc-dashboard**
4. Point the camera at the material — counts update live. Press **`q`** to stop.

> First run only: `pip install ultralytics opencv-python requests`

That's it — no backend, no `pnpm`, nothing else to start.

### Local development (only if you want to modify the code)

Needed only when changing the frontend or backend source. Requires Python 3.10+, Node 20+ with pnpm.

```bash
# Backend (terminal 1)
cd backend && pip install -r requirements.txt && python main.py   # http://localhost:8000

# Frontend (terminal 2)
pnpm install && pnpm run dev                                       # http://localhost:3000

# Edge camera (terminal 3) — point it at your local backend
set QC_BACKEND_URL=http://localhost:8000
python edge/edge_camera.py
```

Then open **http://localhost:3000/qc-dashboard**.

## API

Full contract in [`docs/API.md`](docs/API.md).

| Method | Path | Purpose |
| ------ | ---- | ------- |
| `POST` | `/api/qc/detections` | Camera submits a detection |
| `GET`  | `/api/inventory` | Counts, acceptance rate, detection list |
| `GET`  | `/api/inventory/stats` | Aggregated stats per class |

## Configuration

Key constants in `edge/edge_camera.py`:

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
