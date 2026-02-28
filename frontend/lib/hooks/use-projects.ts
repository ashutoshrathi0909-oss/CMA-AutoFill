'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getProjects, getProject, createProject, updateProject, deleteProject } from '@/lib/api/projects';
import { getProjectProgress } from '@/lib/api/pipeline';
import type { ProjectListParams, ProjectCreate, ProjectUpdate } from '@/lib/api/types';

export function useProjects(params?: ProjectListParams) {
    return useQuery({
        queryKey: ['projects', params],
        queryFn: () => getProjects(params),
    });
}

export function useProject(id: string) {
    return useQuery({
        queryKey: ['projects', id],
        queryFn: () => getProject(id),
        enabled: !!id,
    });
}

export function useCreateProject() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (data: ProjectCreate) => createProject(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard'] });
        },
    });
}

export function useUpdateProject() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: ProjectUpdate }) => updateProject(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects'] });
        },
    });
}

export function useDeleteProject() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id: string) => deleteProject(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard'] });
        },
    });
}

export function useProjectProgress(projectId: string, enabled = false) {
    return useQuery({
        queryKey: ['project-progress', projectId],
        queryFn: () => getProjectProgress(projectId),
        enabled,
        refetchInterval: 3000, // Poll every 3 seconds when enabled
    });
}
