import { api } from './client';
import type { ClassificationResult } from './types';

export async function classifyProject(projectId: string): Promise<ClassificationResult> {
    return api.post<ClassificationResult>(`/api/v1/projects/${projectId}/classify`);
}
