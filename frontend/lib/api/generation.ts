import { api } from './client';
import type { GenerationResult } from './types';

export async function generateProject(projectId: string): Promise<GenerationResult> {
    return api.post<GenerationResult>(`/api/v1/projects/${projectId}/generate`);
}
