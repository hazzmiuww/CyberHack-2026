# 📦 Files Created - All-in-One Startup System

## Summary

I've created a complete **one-command startup system** for your SIMA QC project. Judges and users can now run the entire system (Backend + Camera + Dashboard) with a single command!

---

## 🆕 New Files Created

### 1. **start-all.bat** ⭐ (Main Startup Script)
**Location:** Root directory  
**Purpose:** All-in-one startup script for Windows  
**Usage:** Double-click or run `start-all.bat` from command prompt

**What it does:**
- ✅ Checks prerequisites (Python, Node.js, pnpm)
- ✅ Installs Python dependencies (FastAPI, YOLO, etc.)
- ✅ Installs Node.js dependencies (Next.js, React, etc.)
- ✅ Verifies YOLO model exists (`best.pt`)
- ✅ Starts 3 services in separate windows:
  - Backend API (port 8000)
  - Edge Camera (YOLO detection)
  - Dashboard (port 3000)
- ✅ Shows all URLs for easy access
- ✅ Allows stopping all services with one keypress

### 2. **start-all.ps1** (PowerShell Version)
**Location:** Root directory  
**Purpose:** PowerShell version with better error handling  
**Usage:** `.\start-all.ps1` from PowerShell

**Features:**
- Same functionality as .bat version
- Better error messages
- Color-coded output
- More robust process management

### 3. **QUICKSTART.md** 📖 (Complete Guide)
**Location:** Root directory  
**Purpose:** Comprehensive guide for judges and evaluators

**Contents:**
- Prerequisites checklist
- One-command startup instructions
- System URLs and access points
- Camera setup (webcam vs sample video)
- Troubleshooting guide
- System architecture diagram
- Technical details for each component
- Demo tips for judges

### 4. **reset-database.bat** (Database Reset)
**Location:** Root directory  
**Purpose:** Quick database reset for fresh demos  
**Usage:** `reset-database.bat`

**What it does:**
- Deletes `backend/sima_qc.db`
- Prompts for confirmation
- Allows starting fresh for each demo

### 5. **scripts/dev.js** (Custom Dev Server)
**Location:** `scripts/dev.js`  
**Purpose:** Custom Next.js dev server with better URL display

**Features:**
- Shows custom URLs on startup
- Displays: `http://localhost:3000/qc-dashboard` (direct to dashboard)
- Displays: `http://192.168.157.1:3000` (network access)
- Auto-detects network IP

### 6. **Updated README.md**
**Location:** Root directory  
**Changes:** Added Quick Start section at the top

**New section:**
```markdown
## 🚀 Quick Start (For Judges & Evaluators)
Windows Users: start-all.bat
Then open: http://localhost:3000/qc-dashboard
```

---

## 📁 File Structure

```
CyberHack-2026/
├── start-all.bat          ⭐ Main startup script (Windows)
├── start-all.ps1          ⭐ PowerShell version
├── QUICKSTART.md          📖 Complete guide for judges
├── reset-database.bat     🔄 Database reset utility
├── README.md              📝 Updated with Quick Start
├── FILES-CREATED.md       📦 This file
├── scripts/
│   └── dev.js             🔧 Custom dev server
├── backend/
│   ├── main.py            (existing)
│   ├── requirements.txt   (existing)
│   └── sima_qc.db         (created at runtime)
├── edge_camera.py         (existing)
├── best.pt                (existing - YOLO model)
└── ... (other existing files)
```

---

## 🎯 How Judges Will Use It

### Step 1: Download Repository
```bash
git clone <your-repo-url>
cd CyberHack-2026
```

### Step 2: Run One Command
```cmd
start-all.bat
```

### Step 3: Wait 10 Seconds
The script will:
- Install all dependencies automatically
- Start all 3 services
- Show URLs

### Step 4: Open Dashboard
```
http://localhost:3000/qc-dashboard
```

### Step 5: Watch Live Detection
- Camera window shows YOLO detection
- Dashboard updates every 4 seconds
- Metrics update in real-time

---

## 🔧 Configuration Files Updated

### 1. **package.json**
**Changes:**
- Added `dev:next` script (internal use)
- Modified `dev` script to use custom `scripts/dev.js`

**Before:**
```json
"dev": "next dev --turbopack --hostname 0.0.0.0"
```

**After:**
```json
"dev": "node scripts/dev.js",
"dev:next": "next dev --turbopack --hostname 0.0.0.0"
```

### 2. **next.config.js**
**Changes:**
- Added `allowedDevOrigins` for network access

```javascript
allowedDevOrigins: ['192.168.157.1']
```

### 3. **.env.local**
**Changes:**
- Added `HOSTNAME=0.0.0.0` for network binding
- Added `QC_BACKEND_URL=http://127.0.0.1:8000`

### 4. **proxy.ts** (renamed from middleware.ts)
**Changes:**
- Renamed file to follow Next.js 16 convention
- Changed to default export

---

## ✅ Testing Checklist

Before submitting to judges, test:

- [ ] `start-all.bat` runs without errors
- [ ] All 3 windows open (Backend, Camera, Dashboard)
- [ ] Backend shows "Uvicorn running on http://0.0.0.0:8000"
- [ ] Camera window shows video with detection boxes
- [ ] Dashboard loads at http://localhost:3000/qc-dashboard
- [ ] Dashboard shows live data (Total, Bagus, Rusak)
- [ ] Recent Detections table updates
- [ ] Acceptance Rate calculates correctly
- [ ] Pressing 'q' in camera window stops detection
- [ ] Closing windows stops all services

---

## 🎓 For Development

If you want to run services individually (not for judges):

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

## 📝 Notes for Judges

### What They'll See:

1. **3 Terminal Windows:**
   - "SIMA Backend API" - FastAPI server logs
   - "SIMA Edge Camera" - YOLO detection with live video
   - "SIMA Dashboard" - Next.js dev server

2. **Camera Window:**
   - Live video with bounding boxes
   - Total QC count (top-left)
   - Active tracks count
   - Live system logs (bottom-left)

3. **Dashboard (Browser):**
   - Total Scanned metric
   - Material Bagus (green card)
   - Material Rusak (red card)
   - Acceptance Rate
   - Recent Detections table (50 entries)
   - Auto-refresh every 4 seconds

### Demo Flow:

1. Run `start-all.bat`
2. Wait for all services to start (~10 seconds)
3. Open dashboard in browser
4. Show camera window with live detection
5. Point to metrics updating in real-time
6. Show detection table growing
7. Explain deduplication (same item not counted twice)
8. Show acceptance rate calculation

---

## 🐛 Common Issues & Solutions

### Issue: "Python not found"
**Solution:** Install Python 3.8+ from https://www.python.org/downloads/

### Issue: "Node.js not found"
**Solution:** Install Node.js 24 LTS from https://nodejs.org/

### Issue: "best.pt not found"
**Solution:** Ensure YOLO model is in root directory

### Issue: "Port 8000 already in use"
**Solution:** 
```cmd
taskkill /F /IM python.exe
```

### Issue: "Port 3000 already in use"
**Solution:**
```cmd
taskkill /F /IM node.exe
```

### Issue: Dashboard shows "Loading detections..."
**Solution:** Wait 5-10 seconds for backend to fully start

---

## 🎉 Success Criteria

The system is working correctly when:

✅ All 3 terminal windows open without errors  
✅ Backend shows "Application startup complete"  
✅ Camera window displays video with detection boxes  
✅ Dashboard loads and shows metrics  
✅ Detection count increases as items are detected  
✅ Recent Detections table populates  
✅ Acceptance Rate updates correctly  
✅ No CORS errors in browser console  
✅ No "Backend unavailable" alerts  

---

## 📞 Support

If judges encounter issues:
1. Check QUICKSTART.md troubleshooting section
2. Verify all prerequisites are installed
3. Ensure ports 3000 and 8000 are free
4. Try `reset-database.bat` and restart

---

**Created for CyberHack 2026 - SIMA QC System**  
**All-in-One Startup System v1.0**
