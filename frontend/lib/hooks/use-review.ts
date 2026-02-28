'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getReviewQueue, resolveReviewItem, bulkResolveReviews, approveAllReviews } from '@/lib/api/review';
import type { ReviewListParams, ReviewResolvePayload, BulkResolvePayload } from '@/lib/api/types';

export function useReviewQueue(params?: ReviewListParams) {
    return useQuery({
        queryKey: ['review-queue', params],
        queryFn: () => getReviewQueue(params),
    });
}

export function useResolveReview() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: ReviewResolvePayload }) =>
            resolveReviewItem(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['review-queue'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard'] });
        },
    });
}

export function useBulkResolveReviews() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (data: BulkResolvePayload) => bulkResolveReviews(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['review-queue'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard'] });
        },
    });
}

export function useApproveAllReviews() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: approveAllReviews,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['review-queue'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard'] });
        },
    });
}
