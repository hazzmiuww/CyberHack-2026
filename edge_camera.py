"""
SIMA QC Camera - Quality Control Detection with Object Tracking
Uses YOLOv8 + ByteTrack to deduplicate detections and prevent double-counting.
Sends payloads asynchronously via threading to avoid OpenCV frame drops.
"""

import json
import sys
import threading
from datetime import datetime, timezone

import cv2
import requests
from ultralytics import YOLO

# --- Configuration ---
MODEL_PATH = "best.pt"
VIDEO_PATH = "Timelapse Lemon.mp4"
API_ENDPOINT = "http://localhost:8000/api/qc/detections"
CAMERA_ID = "cam_01"
CONFIDENCE_THRESHOLD = 0.45

# --- Global deduplication state ---
processed_track_ids: set[int] = set()


def send_payload_async(payload: dict) -> None:
    """Send detection payload to the API in a non-blocking manner."""
    try:
        requests.post(API_ENDPOINT, json=payload, timeout=1.0)
    except requests.exceptions.RequestException:
        # Silently handle network errors to avoid disrupting the video stream
        pass


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
