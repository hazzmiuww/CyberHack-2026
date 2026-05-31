# 🚀 SIMA QC System - Quick Start Guide

## For Judges & Evaluators

This guide will help you run the entire SIMA Quality Control system with **one command**.

---

## 📋 Prerequisites

Before running the system, ensure you have:

1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
2. **Node.js 24 LTS** - [Download](https://nodejs.org/)
3. **Webcam** (or use the included sample video)

> **Note:** The startup script will automatically install `pnpm` and all dependencies.

---

## 🎯 One-Command Startup

### Windows Users

**Option 1: Double-click the batch file**
```
start-all.bat
```

**Option 2: Run from PowerShell**
```powershell
.\start-all.ps1
```

**Option 3: Run from Command Prompt**
```cmd
start-all.bat
```

### What Happens?

The script will:
1. ✅ Check prerequisites (Python, Node.js, pnpm)
2. ✅ Install Python dependencies (FastAPI, YOLO, etc.)
3. ✅ Install Node.js dependencies (Next.js, React, etc.)
4. ✅ Verify YOLO model exists (`best.pt`)
5. ✅ Start 3 services in separate windows:
   - **Backend API** (FastAPI on port 8000)
   - **Edge Camera** (YOLO detection with live feed)
   - **Dashboard** (Next.js on port 3000)

---

## 🌐 Access the System

After startup (wait ~10 seconds), open your browser:

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:3000/qc-dashboard | Main QC monitoring dashboard |
| **Network Access** | http://192.168.157.1:3000/qc-dashboard | Access from other devices |
| **Backend API** | http://localhost:8000 | REST API (for testing) |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |

---

## 📹 Camera Setup

### Using Webcam (Default)
The system will automatically use your webcam. Just allow camera access when prompted.

### Using Sample Video
If you don't have a webcam or want to use the demo video:

1. Open `edge_camera.py`
2. Change line 18:
   ```python
   VIDEO_PATH = 0  # Change this to:
   VIDEO_PATH = "sample_lemon.mp4"  # or "download (6).mp4"
   ```
3. Restart the system

---

## 🎮 Using the System

### Edge Camera Window
- Shows live detection with bounding boxes
- Displays total QC count and active tracks
- Shows live system logs (bottom-left)
- Press **'q'** to quit

### Dashboard (Browser)
- **Total Scanned**: Total items detected
- **Material Bagus**: Good quality items (green)
- **Material Rusak**: Bad quality items (red)
- **Acceptance Rate**: Percentage of good items
- **Recent Detections**: Live table of all detections
- Auto-refreshes every 4 seconds

---

## 🛑 Stopping the System

### Method 1: Close All Windows
Simply close the 3 terminal windows that opened.

### Method 2: Use the Script
Press any key in the main script window to stop all services.

### Method 3: Manual Kill
```cmd
taskkill /FI "WINDOWTITLE eq SIMA*" /F
```

---

## 🔧 Troubleshooting

### "Python not found"
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

### "Node.js not found"
- Install Node.js from https://nodejs.org/
- Restart your terminal after installation

### "best.pt not found"
- Ensure the YOLO model file `best.pt` is in the root directory
- This is the trained model for quality detection

### "Port already in use"
- Close any existing Python or Node.js processes
- Run: `taskkill /F /IM python.exe` and `taskkill /F /IM node.exe`

### Camera not working
- Check camera permissions in Windows Settings
- Try using the sample video instead (see Camera Setup above)

### Dashboard shows "Loading detections..."
- Wait 5-10 seconds for the backend to start
- Check that the Backend API window shows "Uvicorn running on http://0.0.0.0:8000"
- Refresh the browser page

---

## 📊 System Architecture

```
┌─────────────────┐
│  Edge Camera    │  ← YOLO detection + tracking
│  (Python)       │
└────────┬────────┘
         │ HTTP POST
         ↓
┌─────────────────┐
│  Backend API    │  ← FastAPI + SQLite
│  (Python)       │
└────────┬────────┘
         │ REST API
         ↓
┌─────────────────┐
│  Dashboard      │  ← Next.js + React
│  (Node.js)      │
└─────────────────┘
```

---

## 📝 Technical Details

### Backend API
- **Framework**: FastAPI
- **Database**: SQLite (`backend/sima_qc.db`)
- **Port**: 8000
- **Endpoints**:
  - `POST /api/qc/detections` - Receive detection from camera
  - `GET /api/inventory` - Get all detections with stats
  - `DELETE /api/qc/detections` - Reset database

### Edge Camera
- **Model**: YOLOv8 (`best.pt`)
- **Tracker**: ByteTrack (deduplication)
- **Confidence Threshold**: 0.45
- **Classes**: `material_bagus`, `material_rusak`

### Dashboard
- **Framework**: Next.js 16 + React 19
- **UI Library**: Mantine v8
- **Polling**: Auto-refresh every 4 seconds
- **Features**: Real-time metrics, live detection log, acceptance rate

---

## 🎓 For Development

If you want to run services individually:

```bash
# Backend only
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Edge Camera only
python edge_camera.py

# Dashboard only
pnpm install
pnpm run dev
```

---

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Ensure all prerequisites are installed
3. Check that ports 3000 and 8000 are not in use
4. Review the terminal output for error messages

---

## 🏆 Demo Tips for Judges

1. **Start the system** using `start-all.bat`
2. **Wait 10 seconds** for all services to initialize
3. **Open the dashboard** at http://localhost:3000/qc-dashboard
4. **Position items** in front of the camera (or play the sample video)
5. **Watch real-time detection** in both the camera window and dashboard
6. **Show the metrics** updating live (acceptance rate, counts, etc.)
7. **Demonstrate deduplication** - same item won't be counted twice

---

**Made with ❤️ for CyberHack 2026**
