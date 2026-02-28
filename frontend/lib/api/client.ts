// ============================================================================
// Base API Client — Centralizes auth headers, error handling, response typing
// ============================================================================

import { supabase } from '@/lib/supabase';
import type { ApiResponse } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/** Custom API error with status code and message */
export class ApiError extends Error {
    constructor(
        public status: number,
        public serverMessage: string,
        public code?: string
    ) {
        super(serverMessage);
        this.name = 'ApiError';
    }
}

/** Internal request helper — attaches Supabase auth token automatically */
async function apiRequest<T>(
    path: string,
    options?: RequestInit & { skipContentType?: boolean }
): Promise<T> {
    const {
        data: { session },
    } = await supabase.auth.getSession();
    const token = session?.access_token;

    if (!token) {
        throw new ApiError(401, 'Not authenticated. Please sign in.');
    }

    const headers: Record<string, string> = {
        Authorization: `Bearer ${token}`,
        ...((options?.headers as Record<string, string>) || {}),
    };

    // Only set Content-Type if not uploading files
    if (!options?.skipContentType) {
        headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        let errorMessage = 'Something went wrong';
        let errorCode: string | undefined;

        try {
            const errorBody = await response.json();
            errorMessage =
                errorBody?.error?.message ||
                errorBody?.detail ||
                errorBody?.message ||
                errorMessage;
            errorCode = errorBody?.error?.code;
        } catch {
            // Response body is not JSON
            errorMessage = response.statusText || errorMessage;
        }

        throw new ApiError(response.status, errorMessage, errorCode);
    }

    // Handle 204 No Content
    if (response.status === 204) {
        return {} as T;
    }

    const json = (await response.json()) as ApiResponse<T>;
    return json.data;
}

/** Build query string from params object, filtering out undefined values */
export function toQueryString(params?: Record<string, unknown>): string {
    if (!params) return '';
    const searchParams = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null && value !== '') {
            searchParams.set(key, String(value));
        }
    }
    const qs = searchParams.toString();
    return qs ? `?${qs}` : '';
}

/** Typed API client with convenience methods */
export const api = {
    get: <T>(path: string) => apiRequest<T>(path),

    post: <T>(path: string, body?: unknown) =>
        apiRequest<T>(path, {
            method: 'POST',
            body: body ? JSON.stringify(body) : undefined,
        }),

    put: <T>(path: string, body?: unknown) =>
        apiRequest<T>(path, {
            method: 'PUT',
            body: body ? JSON.stringify(body) : undefined,
        }),

    delete: <T>(path: string) =>
        apiRequest<T>(path, { method: 'DELETE' }),

    upload: <T>(path: string, formData: FormData) =>
        apiRequest<T>(path, {
            method: 'POST',
            body: formData,
            skipContentType: true,
            headers: {},
        }),
};
