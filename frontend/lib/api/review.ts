import { api, toQueryString } from './client';
import type { ReviewItem, ReviewListParams, ReviewListResponse, ReviewResolvePayload, BulkResolvePayload } from './types';

export async function getReviewQueue(params?: ReviewListParams): Promise<ReviewListResponse> {
    return api.get<ReviewListResponse>(`/api/v1/review-queue${toQueryString(params as Record<string, unknown>)}`);
}

export async function resolveReviewItem(id: string, data: ReviewResolvePayload): Promise<ReviewItem> {
    return api.post<ReviewItem>(`/api/v1/review-queue/${id}/resolve`, data);
}

export async function bulkResolveReviews(data: BulkResolvePayload): Promise<{ resolved_count: number }> {
    return api.post<{ resolved_count: number }>('/api/v1/review-queue/bulk-resolve', data);
}

export async function approveAllReviews(): Promise<{ approved_count: number }> {
    return api.post<{ approved_count: number }>('/api/v1/review-queue/approve-all');
}
