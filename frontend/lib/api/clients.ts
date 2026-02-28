import { api, toQueryString } from './client';
import type { Client, ClientCreate, ClientUpdate, ClientListParams, ClientListResponse } from './types';

export async function getClients(params?: ClientListParams): Promise<ClientListResponse> {
    return api.get<ClientListResponse>(`/api/v1/clients${toQueryString(params as Record<string, unknown>)}`);
}

export async function getClient(id: string): Promise<Client> {
    return api.get<Client>(`/api/v1/clients/${id}`);
}

export async function createClient(data: ClientCreate): Promise<Client> {
    return api.post<Client>('/api/v1/clients', data);
}

export async function updateClient(id: string, data: ClientUpdate): Promise<Client> {
    return api.put<Client>(`/api/v1/clients/${id}`, data);
}

export async function deleteClient(id: string): Promise<void> {
    return api.delete<void>(`/api/v1/clients/${id}`);
}
