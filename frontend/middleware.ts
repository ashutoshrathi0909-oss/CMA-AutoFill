import { NextResponse, type NextRequest } from 'next/server';

/**
 * Lightweight auth middleware that checks for Supabase session cookies
 * WITHOUT importing @supabase/ssr (which pulls in Node.js dependencies
 * that crash Vercel's Edge Runtime with "__dirname is not defined").
 *
 * How it works:
 * - Supabase stores auth tokens in cookies named `sb-<ref>-auth-token`
 * - We just check if any such cookie exists — if so, the user is logged in
 * - We DON'T verify the JWT here — that's the API server's job
 * - This keeps the middleware bundle tiny and Edge-safe
 */

function hasSupabaseSession(request: NextRequest): boolean {
    const cookies = request.cookies.getAll();
    // Supabase auth cookies follow the pattern: sb-<project-ref>-auth-token
    // They may be chunked: sb-<ref>-auth-token.0, sb-<ref>-auth-token.1, etc.
    return cookies.some((cookie) => cookie.name.includes('-auth-token'));
}

export async function middleware(request: NextRequest) {
    const response = NextResponse.next({
        request: {
            headers: request.headers,
        },
    });

    // E2E test bypass — only in non-production environments
    if (
        process.env.NODE_ENV !== 'production' &&
        request.cookies.get('e2e-auth-bypass')?.value === 'true'
    ) {
        return response;
    }

    const hasSession = hasSupabaseSession(request);
    const { pathname } = request.nextUrl;

    // If user has no session and trying to access dashboard pages, redirect to login
    if (!hasSession && !pathname.startsWith('/login') && !pathname.startsWith('/auth')) {
        const url = request.nextUrl.clone();
        url.pathname = '/login';
        return NextResponse.redirect(url);
    }

    // If user has session and trying to access login page, redirect to dashboard
    if (hasSession && pathname.startsWith('/login')) {
        const url = request.nextUrl.clone();
        url.pathname = '/dashboard';
        return NextResponse.redirect(url);
    }

    return response;
}

export const config = {
    matcher: [
        /*
         * Match all request paths except for:
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico (favicon file)
         * - public files (images, etc.)
         */
        '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
    ],
};
