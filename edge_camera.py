"""
SIMA QC Camera - Quality Control Detection with Object Tracking
Uses YOLOv8 + ByteTrack to deduplicate detections and prevent double-counting.
Sends payloads asynchronously via threading to avoid OpenCV frame drops.

Includes an on-screen dashboard overlay (total QC count, active tracks, live log panel)
for a presentable demo, while keeping the robust ByteTrack pipeline and the
confidence-gate-before-tracking architecture.
"""

import json
import os
import sys
import threading
from datetime import datetime, timezone

import cv2
import requests
from ultralytics import YOLO

# --- Configuration ---
MODEL_PATH = "best.pt"
VIDEO_PATH = 0   # set to 0 for a live webcam, or "sample_lemon.mp4" for the demo video
# Backend base URL.
# Default points at the deployed Railway backend so detections show up on the
# live Vercel dashboard out of the box. Override with env var QC_BACKEND_URL
# (e.g. set QC_BACKEND_URL=http://localhost:8000) to target a local backend.
API_BASE = os.getenv("QC_BACKEND_URL", "https://cyberhack-2026-production.up.railway.app")
API_ENDPOINT = f"{API_BASE}/api/qc/detections"
CAMERA_ID = "cam_01"
CONFIDENCE_THRESHOLD = 0.45

# --- Global deduplication state ---
processed_track_ids: set[int] = set()

# --- Live on-screen log (most recent dispatches) ---
recent_logs: list[str] = []
MAX_VISIBLE_LOGS = 5


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
        # Silently handle network errors to avoid disrupting the video stream
        pass


def draw_dashboard(frame, total_count: int, active_count: int):
    """Render the QC dashboard overlay (metrics + live log panel) onto a frame."""
    # --- Top metrics ---
    cv2.putText(
        frame, f"TOTAL QC: {total_count}", (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 3,
    )
    cv2.putText(
        frame, f"Aktif di Kamera: {active_count}", (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2,
    )

    # --- Live log panel (bottom-left) ---
    cv2.rectangle(frame, (15, 300), (450, 460), (20, 20, 20), -1)
    cv2.rectangle(frame, (15, 300), (450, 460), (100, 100, 100), 1)
    cv2.putText(
        frame, "SYSTEM LIVE LOGS (POST DATABASE)", (25, 320),
        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA,
    )
    for idx, log in enumerate(recent_logs):
        y_pos = 345 + (idx * 22)
        # newest log (index 0) bright green, older logs grey
        text_color = (0, 255, 0) if idx == 0 else (150, 150, 150)
        cv2.putText(
            frame, log, (25, y_pos),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, text_color, 1, cv2.LINE_AA,
        )


def main() -> None:
    # Load YOLO model
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"[ERROR] Failed to load model '{MODEL_PATH}': {e}", file=sys.stderr)
        sys.exit(1)

    # Open video capture
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(
            f"[ERROR] Failed to open video '{VIDEO_PATH}'. "
            "Check the file exists and is a valid video.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"[INFO] Model loaded: {MODEL_PATH}")
    print(f"[INFO] Video opened: {VIDEO_PATH}")
    print(f"[INFO] Tracker: ByteTrack | Camera: {CAMERA_ID}")
    print(f"[INFO] Sending detections to: {API_ENDPOINT}")

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

        # Run tracking inference (ByteTrack for consistent IDs across frames)
        results = model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)

        annotated_frame = frame  # fallback if no results
        active_count = 0          # tracks visible (above threshold) this frame

        for result in results:
            # Always render the annotated frame (with or without detections)
            annotated_frame = result.plot()

            boxes = result.boxes
            if boxes is None or len(boxes) == 0:
                continue

            for box in boxes:
                # Skip detections without a valid track ID
                if box.id is None:
                    continue

                track_id = int(box.id[0])
                confidence = float(box.conf[0])

                # CRITICAL: confidence gate BEFORE touching processed_track_ids.
                # A low-confidence detection must not consume/register a track_id,
                # so that if the same object reappears with higher confidence later
                # it can still be dispatched.
                if confidence < CONFIDENCE_THRESHOLD:
                    continue

                active_count += 1

                # Deduplicate: only process each track_id once
                if track_id in processed_track_ids:
                    continue

                processed_track_ids.add(track_id)

                cls_id = int(box.cls[0])
                class_name = model.names[cls_id]

                payload = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "item_class": class_name,
                    "confidence_score": round(confidence, 4),
                    "camera_id": CAMERA_ID,
                    "track_id": track_id,
                }

                # Dispatch async POST (non-blocking)
                thread = threading.Thread(
                    target=send_payload_async, args=(payload,), daemon=True
                )
                thread.start()

                # Terminal log only for NEW dispatches
                print(f"[DISPATCH] {json.dumps(payload)}")

                # On-screen live log (newest on top, capped)
                time_str = datetime.now().strftime("%H:%M:%S")
                recent_logs.insert(0, f"[{time_str}] ID {track_id}: {class_name} -> HTTP 200")
                if len(recent_logs) > MAX_VISIBLE_LOGS:
                    recent_logs.pop()

        # Draw dashboard overlay (total unique = size of dedup set)
        draw_dashboard(annotated_frame, len(processed_track_ids), active_count)

        # Display frame
        cv2.imshow("SIMA QC Camera", annotated_frame)

        # Quit on 'q' keypress (1ms wait keeps stream smooth)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("[INFO] Quit signal received.")
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[INFO] Processed {frame_count} frames.")
    print(f"[INFO] Unique objects tracked: {len(processed_track_ids)}")


if __name__ == "__main__":
    main()
