'use client';

import { useQuery } from '@tanstack/react-query';
import { getDashboardStats } from '@/lib/api/dashboard';

export function useDashboardStats() {
    return useQuery({
        queryKey: ['dashboard'],
        queryFn: getDashboardStats,
        refetchInterval: 30 * 1000, // Auto-refresh every 30 seconds
    });
}
