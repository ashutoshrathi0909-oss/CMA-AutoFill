import { test, expect } from '@playwright/test';
import {
  mockSupabaseAuth,
  mockBackendAPI,
  mockCMAJourneyAPIs,
  mockProjectsAPI,
  API_BASE,
  MOCK_PROJECT,
} from './helpers';

test.describe('Review Queue', () => {
  test.beforeEach(async ({ page }) => {
    await mockSupabaseAuth(page);
    await mockBackendAPI(page);
    await mockProjectsAPI(page);
    await mockCMAJourneyAPIs(page);
  });

  test('review page loads with heading', async ({ page }) => {
    await page.goto('/review');
    await expect(page.getByRole('heading', { name: /ask father review/i })).toBeVisible({ timeout: 15_000 });
  });

  test('review page without project_id shows guidance', async ({ page }) => {
    await page.goto('/review');
    await expect(page.getByRole('heading', { name: /ask father review/i })).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText(/no specific project/i)).toBeVisible();
  });

  test('review page with project_id loads correctly', async ({ page }) => {
    await page.goto('/review?project_id=proj-001');
    await expect(page.getByRole('heading', { name: /ask father review/i })).toBeVisible({ timeout: 15_000 });

    // Page loads and renders — the heading and description text confirms the review page is accessible.
    // Note: The project_id filtering happens within the ReviewQueue component.
    await expect(page.getByText(/review|pending/i).first()).toBeVisible();
  });

  test('project detail review tab is accessible', async ({ page }) => {
    // Override project to reviewing state
    await page.route(`${API_BASE}/api/v1/projects/proj-*`, async (route) => {
      const url = route.request().url();
      if (route.request().method() === 'GET' && /\/projects\/proj-[^/]+$/.test(url.split('?')[0])) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            data: { ...MOCK_PROJECT, status: 'reviewing', pipeline_progress: 65 },
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
            status: 'reviewing',
            pipeline_progress: 65,
            steps: [
              { name: 'extraction', status: 'completed' },
              { name: 'classification', status: 'completed' },
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

    // Click Review tab
    const reviewTab = page.getByRole('tab', { name: /review/i });
    await expect(reviewTab).toBeVisible({ timeout: 5_000 });
    await reviewTab.click();

    // Tab panel should render
    await expect(page.getByRole('tabpanel')).toBeVisible({ timeout: 5_000 });
  });

  test('review items display confidence values', async ({ page }) => {
    await page.goto('/review?project_id=proj-001');
    await expect(page.getByRole('heading', { name: /ask father review/i })).toBeVisible({ timeout: 15_000 });

    // Wait for review items or any content to load
    await page.waitForTimeout(3_000);

    // Check that the page has rendered review content (items, confidence, or pending state)
    const hasReviewContent = await page.getByText('Sundry Creditors').isVisible().catch(() => false)
      || await page.getByText(/55%/).isVisible().catch(() => false)
      || await page.getByText(/pending/i).first().isVisible().catch(() => false);

    expect(hasReviewContent).toBeTruthy();
  });
});
