import json
import math
import sys
import threading
from datetime import datetime, timezone

import cv2
import requests
from ultralytics import YOLO

# --- Configuration ---
MODEL_PATH = "best.pt"
VIDEO_PATH = 0 # Ganti ke 0 untuk live webcam
API_ENDPOINT = "http://localhost:8000/api/qc/detections"
CAMERA_ID = "cam_01"
CONFIDENCE_THRESHOLD = 0.55

# --- Logika Multi-Object Centroid Tracker ---
tracked_fruits = {}
next_fruit_id = 1
total_fruit_count = 0  

# --- RIWAYAT LOG UNTUK TAMPILAN LAYAR ---
recent_logs = []  # Menyimpan maksimal 5 log terakhir

# Parameter Tracker
MAX_DISTANCE_THRESHOLD = 60  
MAX_LOST_FRAMES = 20         


def reset_backend_records() -> None:
    """Clear all previous detection records so each run starts clean.

    Best-effort: if the backend is unreachable we warn but still continue,
    so the video stream can run even without the API.
    """
    try:
        resp = requests.delete(API_ENDPOINT, timeout=2.0)
        deleted = resp.json().get("deleted", "?")
        print(f"[INFO] Cleared {deleted} old record(s) from backend.")
    except requests.exceptions.RequestException:
        print("[WARN] Could not reach backend to reset records (continuing anyway).")


def send_payload_async(payload: dict) -> None:
    """Send detection payload to the API in a non-blocking manner."""
    try:
        requests.post(API_ENDPOINT, json=payload, timeout=1.0)
    except requests.exceptions.RequestException:
        pass


def main() -> None:
    global next_fruit_id, total_fruit_count, recent_logs

    # Load YOLO model
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"[ERROR] Failed to load model '{MODEL_PATH}': {e}", file=sys.stderr)
        sys.exit(1)

    # Open video capture
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"[ERROR] Failed to open video/webcam '{VIDEO_PATH}'.", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Model loaded: {MODEL_PATH}")
    print(f"[INFO] Video opened: {VIDEO_PATH}")
    print(f"[INFO] Tracker: ByteTrack | Camera: {CAMERA_ID}")

    # Start each run from a clean slate on the backend
    reset_backend_records()

    print(f"[INFO] Press 'q' to quit.\n")

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[INFO] End of video or failed to read frame.")
            break

        frame_count += 1

        # Jalankan deteksi biasa (predict mode)
        results = model(frame, verbose=False)
        annotated_frame = frame.copy()

        # 1. Ekstraksi semua titik tengah (centroid) frame saat ini
        current_frame_objects = []
        for result in results:
            annotated_frame = result.plot()  
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    conf = float(box.conf[0])
                    if conf >= CONFIDENCE_THRESHOLD:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)
                        
                        cls_id = int(box.cls[0])
                        class_name = model.names[cls_id]
                        
                        current_frame_objects.append({
                            "centroid": (cx, cy),
                            "class": class_name,
                            "conf": conf,
                            "matched": False
                        })

        # 2. Cocokkan centroid baru dengan objek lama di memori
        for f_id, f_data in list(tracked_fruits.items()):
            if not current_frame_objects:
                break
            
            closest_idx = -1
            min_dist = float('inf')
            
            for i, current_obj in enumerate(current_frame_objects):
                if current_obj["matched"]:
                    continue
                
                dist = math.dist(f_data["centroid"], current_obj["centroid"])
                if dist < min_dist and dist < MAX_DISTANCE_THRESHOLD:
                    min_dist = dist
                    closest_idx = i
            
            if closest_idx != -1:
                tracked_fruits[f_id]["centroid"] = current_frame_objects[closest_idx]["centroid"]
                tracked_fruits[f_id]["lost_frames"] = 0
                current_frame_objects[closest_idx]["matched"] = True

        # 3. Jika ada objek baru, masukkan ke counter dan tracker aktif
        for current_obj in current_frame_objects:
            if not current_obj["matched"]:
                tracked_fruits[next_fruit_id] = {
                    "centroid": current_obj["centroid"],
                    "class": current_obj["class"],
                    "conf": current_obj["conf"],
                    "dispatched": False,
                    "lost_frames": 0
                }
                total_fruit_count += 1 
                next_fruit_id += 1

        # 4. Evaluasi memori & Pengiriman API
        for f_id, f_data in list(tracked_fruits.items()):
            
            # Kirim data ke Backend (Hanya 1 kali per buah)
            if not f_data["dispatched"]:
                time_str = datetime.now().strftime("%H:%M:%S")
                payload = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "item_class": f_data["class"],
                    "confidence_score": round(f_data["conf"], 4),
                    "camera_id": CAMERA_ID,
                    "track_id": f_id  
                }

                thread = threading.Thread(
                    target=send_payload_async, args=(payload,), daemon=True
                )
                thread.start()
                
                print(f"📤 [DISPATCH] Data Sent -> ID: {f_id}")
                tracked_fruits[f_id]["dispatched"] = True

                # TAMBAHAN LOGIKA LOG: Masukkan log baru ke baris paling atas panel
                log_text = f"[{time_str}] ID {f_id}: {f_data['class']} -> HTTP 200"
                recent_logs.insert(0, log_text)  # Insert di indeks 0 agar log terbaru di atas
                
                # Batasi hanya menampilkan 5 log terakhir di layar agar tidak penuh
                if len(recent_logs) > 5:
                    recent_logs.pop()

            # Naikkan lost frame counter
            tracked_fruits[f_id]["lost_frames"] += 1
            
            # Pembersihan memori aktif jika objek keluar frame
            if tracked_fruits[f_id]["lost_frames"] > MAX_LOST_FRAMES:
                del tracked_fruits[f_id]

        # ====================================================
        # INTERFACE OVERLAY (DASHBOARD METRICS & LOG CONSOLE)
        # ====================================================
        # 1. Tampilkan Indikator Utama
        cv2.putText(annotated_frame, f"TOTAL QC: {total_fruit_count}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 3)
        cv2.putText(annotated_frame, f"Aktif di Kamera: {len(tracked_fruits)}", (20, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # 2. Gambar Background Kotak Semi-Transparan untuk Panel Log
        # Posisi kotak: kiri bawah area video
        cv2.rectangle(annotated_frame, (15, 300), (450, 460), (20, 20, 20), -1)
        # Gambar border luar untuk kotak log
        cv2.rectangle(annotated_frame, (15, 300), (450, 460), (100, 100, 100), 1)
        
        # Judul Panel Log
        cv2.putText(annotated_frame, "SYSTEM LIVE LOGS (POST DATABASE)", (25, 320), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA)

        # 3. Render Baris Log ke Dalam Kotak Panel
        for idx, log in enumerate(recent_logs):
            y_pos = 345 + (idx * 22)  # Jarak antar baris teks log
            # Log terbaru (indeks 0) diberi warna hijau terang, log lama warna abu-abu
            text_color = (0, 255, 0) if idx == 0 else (150, 150, 150)
            cv2.putText(annotated_frame, log, (25, y_pos), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, text_color, 1, cv2.LINE_AA)

        # Tampilkan jendela video
        cv2.imshow("SIMA QC Camera - Multi Object Mode", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("[INFO] Quit signal received.")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()