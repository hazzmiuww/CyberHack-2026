"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { InventoryResponse } from "./types";

interface UseInventoryOptions {
  /** Poll interval in ms. Set to 0 to disable polling. */
  pollMs?: number;
  /** Max detections to fetch for the log table. */
  limit?: number;
}

interface UseInventoryState {
  data: InventoryResponse | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

/**
 * Fetches QC inventory from the Next.js proxy (/api/qc/inventory) with optional
 * polling for a near-real-time dashboard feel.
 */
export function useInventory(options: UseInventoryOptions = {}): UseInventoryState {
  const { pollMs = 4000, limit = 50 } = options;

  const [data, setData] = useState<InventoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const isMounted = useRef(true);

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(`/api/qc/inventory?limit=${limit}`, {
        cache: "no-store",
      });
      const json = await res.json();

      if (!isMounted.current) return;

      if (!res.ok) {
        setError(json?.hint || json?.error || "Failed to load inventory.");
      } else {
        setData(json);
        setError(null);
      }
    } catch {
      if (isMounted.current) setError("Network error while loading inventory.");
    } finally {
      if (isMounted.current) setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    isMounted.current = true;
    fetchData();

    if (pollMs > 0) {
      const id = setInterval(fetchData, pollMs);
      return () => {
        isMounted.current = false;
        clearInterval(id);
      };
    }
    return () => {
      isMounted.current = false;
    };
  }, [fetchData, pollMs]);

  return { data, loading, error, refresh: fetchData };
}
