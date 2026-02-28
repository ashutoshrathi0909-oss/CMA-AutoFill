import { api } from './client';
import { supabase } from '@/lib/supabase';
import type { UploadedFile, GeneratedFile } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function uploadFiles(projectId: string, files: File[]): Promise<UploadedFile[]> {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    return api.upload<UploadedFile[]>(`/api/v1/projects/${projectId}/files`, formData);
}

export async function getProjectFiles(projectId: string): Promise<UploadedFile[]> {
    return api.get<UploadedFile[]>(`/api/v1/projects/${projectId}/files`);
}

export async function getGeneratedFiles(projectId: string): Promise<GeneratedFile[]> {
    return api.get<GeneratedFile[]>(`/api/v1/projects/${projectId}/generated-files`);
}

export async function deleteFile(fileId: string): Promise<void> {
    return api.delete<void>(`/api/v1/files/${fileId}`);
}

export async function downloadCMA(projectId: string): Promise<Blob> {
    const { data: { session } } = await supabase.auth.getSession();
    const token = session?.access_token;
    if (!token) throw new Error('Not authenticated');

    const response = await fetch(`${API_BASE}/api/v1/projects/${projectId}/download`, {
        headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
    }

    return response.blob();
}
