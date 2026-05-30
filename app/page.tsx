import { redirect } from "next/navigation";

/**
 * Root route → QC Command Center.
 * The dashboard is the primary entry point for this app.
 */
export default function HomePage() {
  redirect("/qc-dashboard");
}
