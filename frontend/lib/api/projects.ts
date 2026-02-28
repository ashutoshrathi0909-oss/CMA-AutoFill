import { api, toQueryString } from './client';
import type { Project, ProjectCreate, ProjectUpdate, ProjectListParams, ProjectListResponse } from './types';

export async function getProjects(params?: ProjectListParams): Promise<ProjectListResponse> {
    return api.get<ProjectListResponse>(`/api/v1/projects${toQueryString(params as Record<string, unknown>)}`);
}

export async function getProject(id: string): Promise<Project> {
    return api.get<Project>(`/api/v1/projects/${id}`);
}

export async function createProject(data: ProjectCreate): Promise<Project> {
    return api.post<Project>('/api/v1/projects', data);
}

export async function updateProject(id: string, data: ProjectUpdate): Promise<Project> {
    return api.put<Project>(`/api/v1/projects/${id}`, data);
}

export async function deleteProject(id: string): Promise<void> {
    return api.delete<void>(`/api/v1/projects/${id}`);
}
