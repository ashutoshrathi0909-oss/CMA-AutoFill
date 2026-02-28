import { api } from './client';
import type { PipelineProgress } from './types';

export async function processProject(projectId: string): Promise<PipelineProgress> {
    return api.post<PipelineProgress>(`/api/v1/projects/${projectId}/process`);
}

export async function getProjectProgress(projectId: string): Promise<PipelineProgress> {
    return api.get<PipelineProgress>(`/api/v1/projects/${projectId}/progress`);
}

export async function retryProject(projectId: string): Promise<PipelineProgress> {
    return api.post<PipelineProgress>(`/api/v1/projects/${projectId}/retry`);
}

export async function resumeProject(projectId: string): Promise<PipelineProgress> {
    return api.post<PipelineProgress>(`/api/v1/projects/${projectId}/resume`);
}
