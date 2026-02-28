import { test, expect } from '@playwright/test';
import {
  mockSupabaseAuth,
  mockBackendAPI,
  mockProjectsAPI,
  mockCMAJourneyAPIs,
  API_BASE,
  MOCK_PROJECT,
} from './helpers';

test.describe('Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    await mockSupabaseAuth(page);
    await mockBackendAPI(page);
    await mockProjectsAPI(page);
    await mockCMAJourneyAPIs(page);
  });

  test('navigating to unknown page shows 404', async ({ page }) => {
    // With auth bypass, we can reach non-existent routes
    await page.goto('/this-does-not-exist-xyz');

    await expect(
      page.getByText(/not found|404|page.*not.*exist/i).first()
    ).toBeVisible({ timeout: 15_000 });
  });

  test('non-existent project shows error state', async ({ page }) => {
    await page.route(`${API_BASE}/api/v1/projects/nonexistent*`, async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({ data: null, error: { message: 'Project not found' } }),
        });
      } else {
        await route.continue();
      }
    });

    await page.route(`${API_BASE}/api/v1/pipeline/nonexistent/progress`, async (route) => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ data: null, error: { message: 'Not found' } }),
      });
    });

    await page.route(`${API_BASE}/api/v1/projects/nonexistent/files`, async (route) => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ data: null, error: { message: 'Not found' } }),
      });
    });

    await page.goto('/projects/nonexistent');
    await expect(
      page.getByText(/failed to load|error|not found/i).first()
    ).toBeVisible({ timeout: 15_000 });
  });

  test('process button disabled when no files uploaded', async ({ page }) => {
    await page.route(`${API_BASE}/api/v1/projects/*/files`, async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: [], error: null }),
        });
      } else {
        await route.continue();
      }
    });

    await page.goto(`/projects/${MOCK_PROJECT.id}`);
    await expect(page.getByText('Mehta Computers').first()).toBeVisible({ timeout: 15_000 });

    const processBtn = page.getByRole('button', { name: /process cma/i });
    await expect(processBtn).toBeVisible();
    await expect(processBtn).toBeDisabled();
  });

  test('API error on dashboard shows error state with retry', async ({ page }) => {
    await page.route(`${API_BASE}/api/v1/dashboard/stats`, async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ data: null, error: { message: 'Internal server error' } }),
      });
    });

    await page.goto('/dashboard');
    await expect(
      page.getByText(/failed to load|something went wrong/i).first()
    ).toBeVisible({ timeout: 15_000 });
    await expect(page.getByRole('button', { name: /try again|retry/i })).toBeVisible();
  });

  test('error project shows retry button', async ({ page }) => {
    await page.route(`${API_BASE}/api/v1/projects/proj-*`, async (route) => {
      const url = route.request().url();
      if (route.request().method() === 'GET' && /\/projects\/proj-[^/]+$/.test(url.split('?')[0])) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            data: {
              ...MOCK_PROJECT,
              status: 'error',
              error_message: 'Extraction failed: Invalid file format',
            },
            error: null,
          }),
        });
      } else {
        await route.continue();
      }
    });

    await page.route(`${API_BASE}/api/v1/pipeline/*/progress`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            project_id: 'proj-001',
            status: 'error',
            pipeline_progress: 20,
            error_message: 'Extraction failed',
            steps: [
              { name: 'extraction', status: 'failed', error: 'Invalid file format' },
              { name: 'classification', status: 'pending' },
              { name: 'validation', status: 'pending' },
              { name: 'generation', status: 'pending' },
            ],
          },
          error: null,
        }),
      });
    });

    await page.goto(`/projects/${MOCK_PROJECT.id}`);
    await expect(page.getByText('Mehta Computers').first()).toBeVisible({ timeout: 15_000 });
    await expect(page.getByRole('button', { name: /retry/i })).toBeVisible({ timeout: 10_000 });
  });
});
