'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    getProjectProgress,
    processProject,
    retryProject,
    resumeProject,
} from '@/lib/api/pipeline';

const TERMINAL_STATUSES = ['completed', 'error', 'reviewing'] as const;

export function usePipelineProgress(projectId: string) {
    return useQuery({
        queryKey: ['pipeline-progress', projectId],
        queryFn: () => getProjectProgress(projectId),
        enabled: !!projectId,
        refetchInterval: (query) => {
            const status = query.state.data?.status;
            if (status && TERMINAL_STATUSES.includes(status as typeof TERMINAL_STATUSES[number])) {
                return false;
            }
            return 2000; // Poll every 2 seconds while processing
        },
        staleTime: 0,
    });
}

export function useStartProcessing() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (projectId: string) => processProject(projectId),
        onSuccess: (_, projectId) => {
            queryClient.invalidateQueries({ queryKey: ['pipeline-progress', projectId] });
            queryClient.invalidateQueries({ queryKey: ['project', projectId] });
            queryClient.invalidateQueries({ queryKey: ['projects'] });
        },
    });
}

export function useRetryProcessing() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (projectId: string) => retryProject(projectId),
        onSuccess: (_, projectId) => {
            queryClient.invalidateQueries({ queryKey: ['pipeline-progress', projectId] });
            queryClient.invalidateQueries({ queryKey: ['project', projectId] });
            queryClient.invalidateQueries({ queryKey: ['projects'] });
        },
    });
}

export function useResumeProcessing() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (projectId: string) => resumeProject(projectId),
        onSuccess: (_, projectId) => {
            queryClient.invalidateQueries({ queryKey: ['pipeline-progress', projectId] });
            queryClient.invalidateQueries({ queryKey: ['project', projectId] });
            queryClient.invalidateQueries({ queryKey: ['projects'] });
        },
    });
}
