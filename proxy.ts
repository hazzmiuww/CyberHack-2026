/**
 * @buildpad-origin @buildpad/cli/supabase-auth/proxy
 * @buildpad-version 1.0.0
 *
 * This file was copied from Buildpad UI Packages.
 * To update, run: npx @buildpad/cli add supabase-auth/proxy --overwrite
 *
 * Docs: https://buildpad.dev/components/supabase-auth/proxy
 */

/**
 * Next.js Proxy (formerly Middleware)
 * 
 * Root proxy file that handles auth session refresh.
 * This file is copied to your project by the Buildpad CLI.
 * 
 * @buildpad/origin: proxy
 * @buildpad/version: 1.0.0
 */

import { type NextRequest } from 'next/server';
import { updateSession } from '@/lib/supabase/middleware';

// Default export is required for Next.js proxy
export default async function proxy(request: NextRequest) {
  return await updateSession(request);
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
