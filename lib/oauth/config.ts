/**
 * Minimal OAuth provider configuration module.
 *
 * The CLI-generated logout route imports `getProviderConfig` and
 * `buildLogoutUrl` from here to support external IdP Single Logout (SLO).
 * This project does NOT use external OAuth — authentication for the QC
 * dashboard goes through the FastAPI backend / Supabase email auth — so this
 * module provides safe no-op implementations that keep the build working.
 *
 * If you later add external OAuth (Azure AD, Okta, Auth0, etc.), replace this
 * file with the full implementation via:
 *   npx @buildpad/cli add external-oauth --overwrite
 */

export interface OAuthProviderConfig {
  provider: string;
  /** End-session endpoint, when the provider supports SLO. */
  logoutUrl?: string;
  /** Query param name used to pass the post-logout redirect URI. */
  logoutRedirectParam?: string;
}

/**
 * Resolve provider configuration by name.
 *
 * With no external OAuth configured we return a bare config. Returning an
 * object (rather than throwing) keeps the logout route's SLO branch harmless.
 */
export function getProviderConfig(provider: string): OAuthProviderConfig {
  return { provider };
}

/**
 * Build the IdP end-session (logout) URL.
 *
 * Returns `null` when the provider has no configured `logoutUrl`, which
 * signals the caller to skip SLO and simply fall back to `/login`.
 */
export function buildLogoutUrl(
  config: OAuthProviderConfig,
  postLogoutUri: string
): string | null {
  if (!config.logoutUrl) return null;

  const url = new URL(config.logoutUrl);
  const param = config.logoutRedirectParam ?? "post_logout_redirect_uri";
  url.searchParams.set(param, postLogoutUri);
  return url.toString();
}
