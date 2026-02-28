import { api } from './client';
import type { ExtractionResult } from './types';

export async function extractProject(projectId: string): Promise<ExtractionResult> {
    return api.post<ExtractionResult>(`/api/v1/projects/${projectId}/extract`);
}
