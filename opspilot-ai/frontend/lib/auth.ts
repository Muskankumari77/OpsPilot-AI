/**
 * Token storage.
 *
 * The JWT is kept in a plain (non-httpOnly) cookie so that:
 *   1. `middleware.ts` can read it server-side to gate /dashboard routes
 *   2. client code can attach it to the Authorization header on API calls
 *
 * This is a deliberate lean-build simplification — a production version
 * would use an httpOnly cookie plus a server-side session or refresh-token
 * exchange so the token is never exposed to JS. Documented in
 * ARCHITECTURE.md as a future improvement.
 */
const TOKEN_COOKIE = "opspilot_token";
const ORG_COOKIE = "opspilot_org_id";

function setCookie(name: string, value: string, days = 7) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function deleteCookie(name: string) {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
}

export function setToken(token: string) {
  setCookie(TOKEN_COOKIE, token);
}

export function getToken(): string | null {
  if (typeof document === "undefined") return null;
  return getCookie(TOKEN_COOKIE);
}

export function clearToken() {
  deleteCookie(TOKEN_COOKIE);
  deleteCookie(ORG_COOKIE);
}

export function setActiveOrgId(orgId: number) {
  setCookie(ORG_COOKIE, String(orgId));
}

export function getActiveOrgId(): number | null {
  if (typeof document === "undefined") return null;
  const value = getCookie(ORG_COOKIE);
  return value ? Number(value) : null;
}
