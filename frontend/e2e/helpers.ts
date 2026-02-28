import { Page, BrowserContext } from '@playwright/test';

// ---------------------------------------------------------------------------
// Mock user & firm data shared across all test suites
// ---------------------------------------------------------------------------

export const MOCK_USER = {
  id: 'user-001',
  email: 'test@cafirm.com',
  user_metadata: { full_name: 'Ashutosh Test' },
  aud: 'authenticated',
  role: 'authenticated',
  created_at: '2025-01-01T00:00:00Z',
};

export const MOCK_SESSION = {
  access_token: 'mock-jwt-token-for-tests',
  token_type: 'bearer',
  expires_in: 3600,
  refresh_token: 'mock-refresh-token',
  user: MOCK_USER,
  expires_at: Math.floor(Date.now() / 1000) + 3600,
};

export const MOCK_FIRM_ID = 'firm-001';
export const API_BASE = 'http://localhost:8000';

// Supabase project ref extracted from the NEXT_PUBLIC_SUPABASE_URL
const SUPABASE_PROJECT_REF = 'yamcnvkwidxndxwaskoc';
const SUPABASE_STORAGE_KEY = `sb-${SUPABASE_PROJECT_REF}-auth-token`;

// ---------------------------------------------------------------------------
// Set E2E auth bypass cookie (bypasses Next.js server-side middleware)
// ---------------------------------------------------------------------------

export async function setAuthBypassCookie(context: BrowserContext) {
  await context.addCookies([
    {
      name: 'e2e-auth-bypass',
      value: 'true',
      domain: 'localhost',
      path: '/',
    },
  ]);
}

// ---------------------------------------------------------------------------
// Mock Supabase auth at the network level (client-side requests)
// ---------------------------------------------------------------------------

export async function mockSupabaseAuth(page: Page) {
  // Set bypass cookie for server-side middleware
  await setAuthBypassCookie(page.context());

  // Inject Supabase session into localStorage BEFORE page loads.
  // The Supabase JS client reads from localStorage on init via getSession().
  await page.addInitScript(
    ({ storageKey, session }) => {
      window.localStorage.setItem(storageKey, JSON.stringify(session));
    },
    { storageKey: SUPABASE_STORAGE_KEY, session: MOCK_SESSION }
  );

  // Intercept ALL requests to the Supabase domain (auth refreshes, getUser, etc.)
  const SUPABASE_URL = `https://${SUPABASE_PROJECT_REF}.supabase.co`;
  await page.route(`${SUPABASE_URL}/**`, async (route) => {
    const url = route.request().url();
    if (url.includes('/auth/v1/user')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_USER),
      });
    } else if (url.includes('/auth/v1/token')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_SESSION),
      });
    } else if (url.includes('/auth/v1/logout')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({}),
      });
    } else {
      // Default: return empty success for any other Supabase call
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({}),
      });
    }
  });
}

// ---------------------------------------------------------------------------
// Mock the backend API with sensible defaults for an authenticated user
// ---------------------------------------------------------------------------

export async function mockBackendAPI(page: Page) {
  // GET /api/v1/auth/me
  await page.route(`${API_BASE}/api/v1/auth/me`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: {
          id: MOCK_USER.id,
          email: MOCK_USER.email,
          full_name: 'Ashutosh Test',
          role: 'admin',
          firm_id: MOCK_FIRM_ID,
          firm_name: 'Test CA Firm',
        },
        error: null,
      }),
    });
  });

  // GET /api/v1/dashboard/stats
  await page.route(`${API_BASE}/api/v1/dashboard/stats`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: {
          total_clients: 3,
          active_projects: 2,
          pending_reviews: 1,
          completed_this_month: 1,
          total_cost_this_month: 45,
          projects_by_status: {
            draft: 1,
            completed: 1,
            reviewing: 0,
            extracting: 0,
            classifying: 0,
            validating: 0,
            generating: 0,
            error: 0,
          },
          recent_projects: [
            {
              id: 'proj-001',
              client_name: 'Mehta Computers',
              financial_year: '2024-25',
              status: 'completed',
              pipeline_progress: 100,
              updated_at: '2026-02-20T10:00:00Z',
              created_at: '2026-02-15T08:00:00Z',
            },
          ],
        },
        error: null,
      }),
    });
  });
}

// ---------------------------------------------------------------------------
// Mock clients API
// ---------------------------------------------------------------------------

const MOCK_CLIENTS = [
  {
    id: 'client-001',
    firm_id: MOCK_FIRM_ID,
    name: 'Mehta Computers',
    entity_type: 'trading',
    pan: 'AABCM1234A',
    contact_person: 'Rajesh Mehta',
    email: 'rajesh@mehta.com',
    projects_count: 1,
    created_at: '2026-01-10T00:00:00Z',
    updated_at: '2026-01-10T00:00:00Z',
  },
  {
    id: 'client-002',
    firm_id: MOCK_FIRM_ID,
    name: 'Sharma Textiles',
    entity_type: 'company',
    contact_person: 'Priya Sharma',
    email: 'priya@sharma.com',
    projects_count: 0,
    created_at: '2026-02-01T00:00:00Z',
    updated_at: '2026-02-01T00:00:00Z',
  },
];

export async function mockClientsAPI(page: Page) {
  // GET /api/v1/clients
  await page.route(`${API_BASE}/api/v1/clients*`, async (route) => {
    if (route.request().method() === 'GET') {
      const url = new URL(route.request().url());
      const search = url.searchParams.get('search') || '';
      const filtered = search
        ? MOCK_CLIENTS.filter((c) => c.name.toLowerCase().includes(search.toLowerCase()))
        : MOCK_CLIENTS;

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: { clients: filtered, total: filtered.length, page: 1, per_page: 10 },
          error: null,
        }),
      });
    } else if (route.request().method() === 'POST') {
      const body = route.request().postDataJSON();
      const newClient = {
        id: 'client-new',
        firm_id: MOCK_FIRM_ID,
        ...body,
        projects_count: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ data: newClient, error: null }),
      });
    } else {
      await route.continue();
    }
  });

  // PUT/DELETE /api/v1/clients/:id
  await page.route(`${API_BASE}/api/v1/clients/client-*`, async (route) => {
    if (route.request().method() === 'PUT') {
      const body = route.request().postDataJSON();
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: { ...MOCK_CLIENTS[0], ...body },
          error: null,
        }),
      });
    } else if (route.request().method() === 'DELETE') {
      await route.fulfill({ status: 204 });
    } else {
      await route.continue();
    }
  });
}

// ---------------------------------------------------------------------------
// Mock projects API
// ---------------------------------------------------------------------------

export const MOCK_PROJECT = {
  id: 'proj-001',
  firm_id: MOCK_FIRM_ID,
  client_id: 'client-001',
  client_name: 'Mehta Computers',
  financial_year: '2024-25',
  bank_name: 'SBI',
  loan_type: 'Term Loan',
  loan_amount: 2500000,
  status: 'draft',
  pipeline_progress: 0,
  current_step: null,
  created_at: '2026-02-15T08:00:00Z',
  updated_at: '2026-02-15T08:00:00Z',
};

export async function mockProjectsAPI(page: Page) {
  // GET /api/v1/projects
  await page.route(`${API_BASE}/api/v1/projects?*`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: { projects: [MOCK_PROJECT], total: 1, page: 1, per_page: 10 },
        error: null,
      }),
    });
  });

  // GET /api/v1/projects/:id (single project)
  await page.route(`${API_BASE}/api/v1/projects/proj-*`, async (route) => {
    if (route.request().method() !== 'GET') {
      await route.continue();
      return;
    }
    const url = route.request().url();
    // Don't match sub-resources like /files, /progress
    if (/\/projects\/proj-[^/]+$/.test(url.split('?')[0])) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ data: MOCK_PROJECT, error: null }),
      });
    } else {
      await route.continue();
    }
  });

  // POST /api/v1/projects
  await page.route(`${API_BASE}/api/v1/projects`, async (route) => {
    if (route.request().method() !== 'POST') {
      await route.continue();
      return;
    }
    const body = route.request().postDataJSON();
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: {
          ...MOCK_PROJECT,
          id: 'proj-new',
          ...body,
          status: 'draft',
        },
        error: null,
      }),
    });
  });
}

// ---------------------------------------------------------------------------
// Mock pipeline + files + review APIs for the CMA journey
// ---------------------------------------------------------------------------

export async function mockCMAJourneyAPIs(page: Page) {
  // Files — GET uploaded files
  await page.route(`${API_BASE}/api/v1/projects/*/files`, async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: [
            {
              id: 'file-001',
              project_id: 'proj-001',
              filename: 'test_pl.xlsx',
              file_type: 'xlsx',
              file_size: 45000,
              storage_path: 'firm-001/proj-001/test_pl.xlsx',
              created_at: '2026-02-15T09:00:00Z',
            },
          ],
          error: null,
        }),
      });
    } else if (route.request().method() === 'POST') {
      // File upload
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: [
            {
              id: 'file-002',
              project_id: 'proj-001',
              filename: 'uploaded_file.xlsx',
              file_type: 'xlsx',
              file_size: 50000,
              storage_path: 'firm-001/proj-001/uploaded_file.xlsx',
              created_at: new Date().toISOString(),
            },
          ],
          error: null,
        }),
      });
    } else {
      await route.continue();
    }
  });

  // Pipeline — process
  await page.route(`${API_BASE}/api/v1/pipeline/*/process`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: { message: 'Pipeline started', project_id: 'proj-001' },
        error: null,
      }),
    });
  });

  // Pipeline — progress (simulates completion)
  let progressCallCount = 0;
  await page.route(`${API_BASE}/api/v1/pipeline/*/progress`, async (route) => {
    progressCallCount++;
    const isComplete = progressCallCount > 3;
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: {
          project_id: 'proj-001',
          status: isComplete ? 'completed' : 'extracting',
          pipeline_progress: isComplete ? 100 : 40,
          current_step: isComplete ? null : 'extraction',
          steps: [
            { name: 'extraction', status: isComplete ? 'completed' : 'running' },
            { name: 'classification', status: isComplete ? 'completed' : 'pending' },
            { name: 'validation', status: isComplete ? 'completed' : 'pending' },
            { name: 'generation', status: isComplete ? 'completed' : 'pending' },
          ],
        },
        error: null,
      }),
    });
  });

  // Pipeline — retry
  await page.route(`${API_BASE}/api/v1/pipeline/*/retry`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: { message: 'Pipeline retrying', project_id: 'proj-001' },
        error: null,
      }),
    });
  });

  // Generated files
  await page.route(`${API_BASE}/api/v1/projects/*/generated`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          {
            id: 'gen-001',
            project_id: 'proj-001',
            filename: 'CMA_Mehta_Computers_2024-25.xlsx',
            file_type: 'xlsx',
            storage_path: 'firm-001/proj-001/generated/CMA.xlsx',
            created_at: '2026-02-20T10:00:00Z',
          },
        ],
        error: null,
      }),
    });
  });

  // File download (generated)
  await page.route(`${API_BASE}/api/v1/generated/*/download`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/octet-stream',
      headers: {
        'Content-Disposition': 'attachment; filename="CMA_Mehta_Computers_2024-25.xlsx"',
      },
      body: Buffer.from('mock-excel-content'),
    });
  });

  // Review queue
  await page.route(`${API_BASE}/api/v1/review-queue*`, async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            items: [
              {
                id: 'review-001',
                project_id: 'proj-001',
                firm_id: MOCK_FIRM_ID,
                source_item_name: 'Sundry Creditors',
                suggested_category: 'Trade Payables / Creditors',
                confidence: 0.55,
                classification_source: 'ai',
                status: 'pending',
                created_at: '2026-02-18T10:00:00Z',
              },
              {
                id: 'review-002',
                project_id: 'proj-001',
                firm_id: MOCK_FIRM_ID,
                source_item_name: 'Depreciation on Plant',
                suggested_category: 'Depreciation & Amortisation',
                confidence: 0.62,
                classification_source: 'rule',
                status: 'pending',
                created_at: '2026-02-18T10:01:00Z',
              },
              {
                id: 'review-003',
                project_id: 'proj-001',
                firm_id: MOCK_FIRM_ID,
                source_item_name: 'Misc Income',
                suggested_category: 'Other Income',
                confidence: 0.48,
                classification_source: 'ai',
                status: 'pending',
                created_at: '2026-02-18T10:02:00Z',
              },
            ],
            total: 3,
            page: 1,
            per_page: 10,
          },
          error: null,
        }),
      });
    } else {
      await route.continue();
    }
  });

  // Resolve review item
  await page.route(`${API_BASE}/api/v1/review-queue/*/resolve`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: { message: 'Review item resolved' },
        error: null,
      }),
    });
  });

  // Bulk resolve / approve-all
  await page.route(`${API_BASE}/api/v1/review-queue/bulk-resolve`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: { message: 'Bulk resolved' },
        error: null,
      }),
    });
  });

  await page.route(`${API_BASE}/api/v1/review-queue/approve-all*`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: { message: 'All approved' },
        error: null,
      }),
    });
  });

  // CMA row config
  await page.route(`${API_BASE}/api/v1/review-queue/config/cma-rows`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { group: 'Income', row: 1, label: 'Net Sales / Revenue from Operations' },
          { group: 'Expenses', row: 15, label: 'Depreciation & Amortisation' },
          { group: 'Liabilities', row: 55, label: 'Trade Payables / Creditors' },
          { group: 'Income', row: 2, label: 'Other Income' },
        ],
        error: null,
      }),
    });
  });

  // Validation endpoint
  await page.route(`${API_BASE}/api/v1/generation/*/validate`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: { is_valid: true, errors: [], warnings: [] },
        error: null,
      }),
    });
  });
}
