import { NextRequest, NextResponse } from "next/server";

/**
 * Route protection.
 *
 * Reads the same non-httpOnly `opspilot_token` cookie that lib/auth.ts
 * writes on login. This only confirms a token is *present* — actual
 * validity (expiry, tampering) is enforced by the backend on every API
 * call, so a stale/invalid cookie just results in API 401s the
 * AuthProvider already handles, not a security hole.
 */
export function middleware(request: NextRequest) {
  const token = request.cookies.get("opspilot_token")?.value;
  const { pathname } = request.nextUrl;

  const isProtectedRoute = pathname.startsWith("/dashboard") || pathname.startsWith("/admin");
  const isAuthRoute = pathname === "/login" || pathname === "/signup";

  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/admin/:path*", "/login", "/signup"],
};
