"""
SIMA Arome QC Backend - FastAPI + SQLite
Receives detection payloads from camera scripts and serves inventory data.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, desc
from sqlalchemy.orm import declarative_base, sessionmaker

import uvicorn

# --- Database Setup ---
DATABASE_URL = "sqlite:///./sima_qc.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# --- Model ---
class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(String, nullable=False)
    item_class = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    camera_id = Column(String, nullable=False)
    track_id = Column(Integer, nullable=False)


# Create tables
Base.metadata.create_all(bind=engine)


# --- Pydantic Schemas ---
class DetectionPayload(BaseModel):
    timestamp: str
    item_class: str
    confidence_score: float
    camera_id: str
    track_id: int


class DetectionResponse(BaseModel):
    id: int
    timestamp: str
    item_class: str
    confidence_score: float
    camera_id: str
    track_id: int


# --- FastAPI App ---
app = FastAPI(title="SIMA Arome QC API", version="1.0.0")

# CORS - allow all origins for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Endpoints ---


@app.get("/")
def health_check():
    """Simple health check so the frontend can verify the API is reachable."""
    return {"status": "ok", "service": "SIMA Arome QC API", "version": "1.0.0"}


@app.post("/api/qc/detections")
def create_detection(payload: DetectionPayload):
    """Receive a detection payload from the camera script and store it."""
    db = SessionLocal()
    try:
        detection = Detection(
            timestamp=payload.timestamp,
            item_class=payload.item_class,
            confidence_score=payload.confidence_score,
            camera_id=payload.camera_id,
            track_id=payload.track_id,
        )
        db.add(detection)
        db.commit()
        db.refresh(detection)
        return {"status": "ok", "id": detection.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.delete("/api/qc/detections")
def reset_detections():
    """Delete ALL detection records.

    Called by the edge camera once at startup so each detection run begins
    from a clean slate (prevents duplicate track_ids accumulating across runs).
    """
    db = SessionLocal()
    try:
        deleted = db.query(Detection).delete()
        db.commit()
        return {"status": "ok", "deleted": deleted}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/api/inventory")
def get_inventory(min_confidence: float = 0.0, limit: int | None = None):
    """Return detections ordered by timestamp DESC with counts.

    Query params:
    - min_confidence: only return detections with confidence_score >= this value
    - limit: cap the number of detections returned (useful for "recent logs")

    Note: counts and acceptance_rate are always computed over the FULL filtered
    set, not the limited slice, so the metric cards stay accurate.
    """
    db = SessionLocal()
    try:
        query = (
            db.query(Detection)
            .filter(Detection.confidence_score >= min_confidence)
            .order_by(desc(Detection.timestamp))
        )

        # Counts are computed over the full filtered set first
        detections = query.all()

        total = len(detections)
        material_bagus_count = sum(1 for d in detections if d.item_class == "material_bagus")
        material_rusak_count = sum(1 for d in detections if d.item_class == "material_rusak")

        # Guard against ZeroDivisionError when no detections match
        acceptance_rate = (
            round((material_bagus_count / total) * 100, 2) if total > 0 else 0.0
        )

        # Apply limit only to the returned list, not to the counts
        returned = detections[:limit] if limit is not None else detections

        return {
            "total": total,
            "material_bagus_count": material_bagus_count,
            "material_rusak_count": material_rusak_count,
            "acceptance_rate": acceptance_rate,
            "detections": [
                {
                    "id": d.id,
                    "timestamp": d.timestamp,
                    "item_class": d.item_class,
                    "confidence_score": d.confidence_score,
                    "camera_id": d.camera_id,
                    "track_id": d.track_id,
                }
                for d in returned
            ],
        }
    finally:
        db.close()


@app.get("/api/inventory/stats")
def get_stats():
    """Return summary statistics per class."""
    db = SessionLocal()
    try:
        detections = db.query(Detection).all()
        total = len(detections)

        by_class: dict[str, int] = {}
        for d in detections:
            by_class[d.item_class] = by_class.get(d.item_class, 0) + 1

        material_bagus_count = by_class.get("material_bagus", 0)
        # Guard against ZeroDivisionError when the database is empty
        acceptance_rate = (
            round((material_bagus_count / total) * 100, 2) if total > 0 else 0.0
        )

        return {
            "total": total,
            "by_class": by_class,
            "acceptance_rate": acceptance_rate,
        }
    finally:
        db.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
