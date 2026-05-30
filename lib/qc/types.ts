/**
 * Types matching the FastAPI QC backend contract (see docs/API.md).
 */

export type ItemClass = "material_bagus" | "material_rusak";

export interface Detection {
  id: number;
  timestamp: string; // ISO 8601 UTC
  item_class: ItemClass | string;
  confidence_score: number; // 0..1
  camera_id: string;
  track_id: number;
}

export interface InventoryResponse {
  total: number;
  material_bagus_count: number;
  material_rusak_count: number;
  acceptance_rate: number; // 0..100
  detections: Detection[];
}

export interface InventoryError {
  error: string;
  hint?: string;
}
