'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    getProjectFiles,
    uploadFiles,
    deleteFile,
    getGeneratedFiles,
} from '@/lib/api/files';

export function useProjectFiles(projectId: string) {
    return useQuery({
        queryKey: ['project-files', projectId],
        queryFn: () => getProjectFiles(projectId),
        enabled: !!projectId,
    });
}

export function useUploadFiles() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ projectId, files }: { projectId: string; files: File[] }) =>
            uploadFiles(projectId, files),
        onSuccess: (_, { projectId }) => {
            queryClient.invalidateQueries({ queryKey: ['project-files', projectId] });
            queryClient.invalidateQueries({ queryKey: ['project', projectId] });
        },
    });
}

export function useDeleteFile() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ fileId, projectId }: { fileId: string; projectId: string }) =>
            deleteFile(fileId),
        onSuccess: (_, { projectId }) => {
            queryClient.invalidateQueries({ queryKey: ['project-files', projectId] });
        },
    });
}

export function useGeneratedFiles(projectId: string) {
    return useQuery({
        queryKey: ['generated-files', projectId],
        queryFn: () => getGeneratedFiles(projectId),
        enabled: !!projectId,
    });
}
