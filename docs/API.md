# Sima Arome QC — Backend API Reference

This is the contract between the **Backend (Node B)** and the **Frontend Command Center (Node C)**.
The frontend should rely only on the shapes documented here.

- **Base URL (local):** `http://localhost:8000`
- **Content-Type:** `application/json`
- **Auth:** none (MVP / hackathon scope)
- **CORS:** all origins allowed (frontend can call directly during local dev)

> All timestamps are ISO 8601 strings in UTC (e.g. `2026-05-30T17:12:16.043398+00:00`).

---

## Quick reference

| Method   | Path                    | Purpose                                   |
| -------- | ----------------------- | ----------------------------------------- |
| `GET`    | `/`                     | Health check                              |
| `POST`   | `/api/qc/detections`    | Create a detection (called by Edge Node)  |
| `DELETE` | `/api/qc/detections`    | Delete ALL detections (reset)             |
| `GET`    | `/api/inventory`        | Counts + acceptance rate + detection list |
| `GET`    | `/api/inventory/stats`  | Aggregated stats per class                |

The two endpoints the **frontend dashboard** needs are `GET /api/inventory` and `GET /api/inventory/stats`.

---

## GET /

Health check — use this to verify the backend is reachable.

**Response `200`**

```json
{ "status": "ok", "service": "SIMA Arome QC API", "version": "1.0.0" }
```

---

## POST /api/qc/detections

Creates a single detection record. **Called by the Edge Node (camera), not the frontend** — documented here for completeness.

**Request body**

```json
{
  "timestamp": "2026-05-30T17:12:16.043398+00:00",
  "item_class": "material_bagus",
  "confidence_score": 0.5138,
  "camera_id": "cam_01",
  "track_id": 47
}
```

| Field              | Type   | Notes                                    |
| ------------------ | ------ | ---------------------------------------- |
| `timestamp`        | string | ISO 8601 UTC                             |
| `item_class`       | string | `"material_bagus"` or `"material_rusak"` |
| `confidence_score` | float  | 0.0 – 1.0                                |
| `camera_id`        | string | e.g. `"cam_01"`                          |
| `track_id`         | int    | ByteTrack ID                             |

**Response `200`**

```json
{ "status": "ok", "id": 47 }
```

---

## DELETE /api/qc/detections

Deletes **all** detection records. The Edge Node calls this once at startup so each
detection run begins from a clean slate.

**Response `200`**

```json
{ "status": "ok", "deleted": 65 }
```

---

## GET /api/inventory

The **primary endpoint for the dashboard.** Returns the metric counts, acceptance
rate, and the list of detections (newest first).

**Query parameters (both optional)**

| Param            | Type  | Default | Description                                        |
| ---------------- | ----- | ------- | -------------------------------------------------- |
| `min_confidence` | float | `0.0`   | Only include detections with score >= this value   |
| `limit`          | int   | (none)  | Cap the number of detections in `detections[]`     |

> **Important:** `total`, the counts, and `acceptance_rate` are always computed over the
> FULL filtered set — `limit` only trims the returned `detections[]` array. So you can
> request `?limit=10` for a "recent logs" table while the metric cards stay accurate.

**Example:** `GET /api/inventory?limit=10`

**Response `200`**

```json
{
  "total": 10,
  "material_bagus_count": 5,
  "material_rusak_count": 5,
  "acceptance_rate": 50.0,
  "detections": [
    {
      "id": 10,
      "timestamp": "2026-05-30T17:12:16.043398+00:00",
      "item_class": "material_rusak",
      "confidence_score": 0.5059,
      "camera_id": "cam_01",
      "track_id": 47
    }
  ]
}
```

| Field                  | Type   | Description                                  |
| ---------------------- | ------ | -------------------------------------------- |
| `total`                | int    | Total detections in the filtered set         |
| `material_bagus_count` | int    | Count of `material_bagus`                    |
| `material_rusak_count` | int    | Count of `material_rusak`                    |
| `acceptance_rate`      | float  | `bagus / total * 100`, rounded to 2 dp       |
| `detections`           | array  | Detection objects, newest first              |

**Empty database:** `total` is `0`, counts are `0`, `acceptance_rate` is `0.0`,
and `detections` is `[]` — no error is thrown.

---

## GET /api/inventory/stats

Aggregated stats per class. Useful for charts / summary widgets.

**Response `200`**

```json
{
  "total": 10,
  "by_class": {
    "material_bagus": 5,
    "material_rusak": 5
  },
  "acceptance_rate": 50.0
}
```

| Field             | Type             | Description                              |
| ----------------- | ---------------- | ---------------------------------------- |
| `total`           | int              | Total detections                         |
| `by_class`        | object<str, int> | Count keyed by class name (dynamic keys) |
| `acceptance_rate` | float            | `material_bagus / total * 100`           |

> `by_class` keys are whatever class names exist in the data. Don't assume only two keys —
> render it by iterating the object.

---

## Frontend integration notes

- **Metric cards** (Total, Bagus, Rusak, Acceptance Rate): read directly from
  `GET /api/inventory` — all four values are in the top-level response.
- **Recent logs table:** use `GET /api/inventory?limit=25` and render `detections[]`.
- **Polling for "real-time" feel:** poll `GET /api/inventory` every few seconds. There is
  no websocket; simple interval polling is enough for the demo.
- **Confidence display:** `confidence_score` is 0–1; multiply by 100 for a percentage.
- **Class labels:** map `material_bagus` → "Bagus / Accepted", `material_rusak` →
  "Rusak / Rejected" for nicer UI text.

## Example fetch (frontend)

```ts
const res = await fetch("http://localhost:8000/api/inventory?limit=25");
const data = await res.json();
// data.total, data.material_bagus_count, data.material_rusak_count,
// data.acceptance_rate, data.detections[]
```
