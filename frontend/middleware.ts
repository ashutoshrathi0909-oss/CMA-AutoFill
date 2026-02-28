// Polyfill __dirname BEFORE any other code runs.
// @next/env's ncc-compiled bundle uses __dirname for base-path resolution
// but Edge Runtime doesn't provide it, causing ReferenceError.
// This MUST be the very first statement in the file.
if (typeof globalThis.__dirname === 'undefined') {
    (globalThis as Record<string, unknown>).__dirname = '/';
}
if (typeof globalThis.__filename === 'undefined') {
    (globalThis as Record<string, unknown>).__filename = '/index.js';
}

import { NextResponse, type NextRequest } from 'next/server';

function hasSupabaseSession(request: NextRequest): boolean {
    const cookies = request.cookies.getAll();
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

    if (!hasSession && !pathname.startsWith('/login') && !pathname.startsWith('/auth')) {
        const url = request.nextUrl.clone();
        url.pathname = '/login';
        return NextResponse.redirect(url);
    }

    if (hasSession && pathname.startsWith('/login')) {
        const url = request.nextUrl.clone();
        url.pathname = '/dashboard';
        return NextResponse.redirect(url);
    }

    return response;
}

export const config = {
    matcher: [
        '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
    ],
};
