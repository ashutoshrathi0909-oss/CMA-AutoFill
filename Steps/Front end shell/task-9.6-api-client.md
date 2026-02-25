# Task 9.6: Typed API Client

> **Phase:** 09 - Frontend Shell
> **Depends on:** Tasks 9.1-9.5 (pages exist to wire up), Phase 03-08 (all API endpoints)
> **Time estimate:** 20 minutes

---

## Objective

Create a typed TypeScript API client that all frontend pages use to call the backend. Centralizes auth headers, error handling, and response typing.

---

## What to Do

### Create Files
- `frontend/lib/api/client.ts` — base HTTP client
- `frontend/lib/api/types.ts` — all TypeScript types matching API responses
- `frontend/lib/api/clients.ts` — client CRUD functions
- `frontend/lib/api/projects.ts` — project CRUD functions
- `frontend/lib/api/files.ts` — file upload/download functions
- `frontend/lib/api/extraction.ts` — extraction endpoints
- `frontend/lib/api/classification.ts` — classification endpoints
- `frontend/lib/api/review.ts` — review queue endpoints
- `frontend/lib/api/generation.ts` — validation + generation endpoints
- `frontend/lib/api/pipeline.ts` — pipeline process + progress
- `frontend/lib/api/dashboard.ts` — dashboard stats

### Base Client

```typescript
// frontend/lib/api/client.ts
import { createClient } from '@supabase/supabase-js'

const API_BASE = process.env.NEXT_PUBLIC_API_URL

async function apiRequest<T>(
  path: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  const session = await supabase.auth.getSession()
  const token = session.data.session?.access_token
  
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options?.headers,
    },
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new ApiError(response.status, error.error?.message || 'Unknown error')
  }
  
  return response.json()
}

export const api = {
  get: <T>(path: string) => apiRequest<T>(path),
  post: <T>(path: string, body?: any) => apiRequest<T>(path, { method: 'POST', body: JSON.stringify(body) }),
  put: <T>(path: string, body?: any) => apiRequest<T>(path, { method: 'PUT', body: JSON.stringify(body) }),
  delete: <T>(path: string) => apiRequest<T>(path, { method: 'DELETE' }),
  upload: <T>(path: string, formData: FormData) => apiRequest<T>(path, { method: 'POST', body: formData, headers: {} }),
}
```

### Types (matching backend responses)

```typescript
// frontend/lib/api/types.ts
interface ApiResponse<T> { data: T; error: null }
interface Client { id: string; name: string; entity_type: string; ... }
interface Project { id: string; client_id: string; status: string; pipeline_progress: number; ... }
interface ReviewItem { id: string; source_item_name: string; confidence: number; ... }
interface DashboardStats { total_clients: number; pending_reviews: number; ... }
interface PipelineProgress { status: string; pipeline_progress: number; steps: Step[]; ... }
// ... all types matching backend models
```

### React Query Hooks

Create custom hooks for each resource:

```typescript
// frontend/lib/hooks/use-clients.ts
export function useClients(params?: ClientListParams) {
  return useQuery({
    queryKey: ['clients', params],
    queryFn: () => api.get<ClientListResponse>(`/api/v1/clients?${toQueryString(params)}`),
  })
}

export function useCreateClient() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: ClientCreate) => api.post<Client>('/api/v1/clients', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['clients'] }),
  })
}
```

Create similar hooks for: projects, review queue, dashboard, pipeline progress.

### Wire Up All Pages

Go back through tasks 9.3-9.5 pages and replace any mock data with real API calls using these hooks.

---

## What NOT to Do

- Don't create separate axios/fetch calls in each component — use the central client
- Don't skip TypeScript types — they catch errors early
- Don't hardcode the API URL — use environment variable
- Don't handle auth tokens in individual components — centralized in client

---

## Verification

- [ ] `api.get('/api/v1/me')` → returns current user (auth header sent automatically)
- [ ] Dashboard page shows real data from API
- [ ] Client list shows real clients from API
- [ ] Project list shows real projects from API
- [ ] Create client via modal → appears in list (React Query invalidation)
- [ ] API error → error handled gracefully, not crash
- [ ] Token expired → user redirected to login
- [ ] All TypeScript types compile without errors

---

## Done → Move to task-9.7-error-states.md
