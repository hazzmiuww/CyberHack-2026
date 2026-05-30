"""
SIMA QC Camera - Quality Control Detection using YOLOv8
Loads a custom YOLO model (best.pt) and processes video_lemon.mp4,
printing mock JSON payloads for each detection.
"""

import json
import sys
from datetime import datetime

import cv2
from ultralytics import YOLO


def main():
    model_path = "best.pt"
    video_path = "Timelapse Lemon.mp4"

    # Load YOLO model
    try:
        model = YOLO(model_path)
    except Exception as e:
        print(f"[ERROR] Failed to load model '{model_path}': {e}", file=sys.stderr)
        sys.exit(1)

    # Open video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print(f"[ERROR] Failed to open video '{video_path}'. Check the file exists and is a valid video.", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Model loaded: {model_path}")
    print(f"[INFO] Video opened: {video_path}")
    print(f"[INFO] Press 'q' to quit.\n")

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[INFO] End of video or failed to read frame.")
            break

        frame_count += 1

        # Run inference
        results = model(frame, verbose=False)

        # Process detections
        for result in results:
            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                for box in boxes:
                    cls_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = model.names[cls_id]

                    payload = {
                        "timestamp": datetime.now().isoformat(),
                        "frame": frame_count,
                        "material": "Lemon",
                        "status": class_name,
                        "confidence": round(confidence, 4),
                    }
                    print(json.dumps(payload))

            # Draw annotated frame
            annotated_frame = result.plot()

        # Display the annotated frame
        if results:
            cv2.imshow("SIMA QC Camera", annotated_frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("[INFO] Quit signal received.")
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"[INFO] Processed {frame_count} frames total.")


if __name__ == "__main__":
    main()
