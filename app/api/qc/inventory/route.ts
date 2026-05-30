import { NextRequest, NextResponse } from "next/server";

/**
 * Server-side proxy to the FastAPI QC backend.
 *
 * The browser calls this Next.js route (same-origin, no CORS), and the server
 * forwards the request to the FastAPI backend. The backend base URL is
 * configurable via QC_BACKEND_URL so it can point at localhost in dev or a
 * deployed backend in production.
 */
const BACKEND_URL = process.env.QC_BACKEND_URL || "https://cyberhack-2026-production.up.railway.app";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);

  // Forward optional query params (min_confidence, limit) to the backend
  const qs = new URLSearchParams();
  const minConfidence = searchParams.get("min_confidence");
  const limit = searchParams.get("limit");
  if (minConfidence) qs.set("min_confidence", minConfidence);
  if (limit) qs.set("limit", limit);

  const url = `${BACKEND_URL}/api/inventory${qs.toString() ? `?${qs}` : ""}`;

  try {
    const res = await fetch(url, {
      // Always fetch fresh data — this is a live dashboard
      cache: "no-store",
      headers: { Accept: "application/json" },
    });

    if (!res.ok) {
      return NextResponse.json(
        { error: `Backend responded with ${res.status}` },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch {
    // Backend unreachable (not running, wrong URL, etc.)
    return NextResponse.json(
      {
        error: "Could not reach the QC backend.",
        hint: `Is the FastAPI server running at ${BACKEND_URL}?`,
      },
      { status: 502 }
    );
  }
}
