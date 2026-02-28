import { test, expect } from '@playwright/test';
import {
  mockSupabaseAuth,
  mockBackendAPI,
  mockClientsAPI,
  mockProjectsAPI,
  mockCMAJourneyAPIs,
  API_BASE,
  MOCK_PROJECT,
} from './helpers';

test.describe('Full CMA Journey (Happy Path)', () => {
  test.beforeEach(async ({ page }) => {
    await mockSupabaseAuth(page);
    await mockBackendAPI(page);
    await mockClientsAPI(page);
    await mockProjectsAPI(page);
    await mockCMAJourneyAPIs(page);
  });

  test('navigate to project detail and see file upload area', async ({ page }) => {
    await page.goto(`/projects/${MOCK_PROJECT.id}`);

    await expect(page.getByText('Mehta Computers').first()).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText('2024-25').first()).toBeVisible();
    await expect(page.getByRole('tab', { name: /files/i })).toBeVisible();
  });

  test('project detail shows pipeline stepper with step names', async ({ page }) => {
    await page.goto(`/projects/${MOCK_PROJECT.id}`);
    await expect(page.getByText('Mehta Computers').first()).toBeVisible({ timeout: 15_000 });

    // Pipeline stepper — look for step names (case-insensitive, may be in badges/labels)
    await expect(page.getByText(/extract/i).first()).toBeVisible({ timeout: 10_000 });
  });

  test('draft project shows Process CMA button', async ({ page }) => {
    await page.goto(`/projects/${MOCK_PROJECT.id}`);
    await expect(page.getByText('Mehta Computers').first()).toBeVisible({ timeout: 15_000 });

    await expect(page.getByRole('button', { name: /process cma/i })).toBeVisible();
  });

  test('clicking Process CMA triggers pipeline and shows progress', async ({ page }) => {
    await page.goto(`/projects/${MOCK_PROJECT.id}`);
    await expect(page.getByRole('button', { name: /process cma/i })).toBeVisible({ timeout: 15_000 });

    await page.getByRole('button', { name: /process cma/i }).click();
    await expect(page.getByRole('tab', { name: /progress/i })).toBeVisible();
  });

  test('completed project shows download section', async ({ page }) => {
    await page.route(`${API_BASE}/api/v1/projects/proj-*`, async (route) => {
      const url = route.request().url();
      if (route.request().method() === 'GET' && /\/projects\/proj-[^/]+$/.test(url.split('?')[0])) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            data: { ...MOCK_PROJECT, status: 'completed', pipeline_progress: 100 },
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
            status: 'completed',
            pipeline_progress: 100,
            steps: [
              { name: 'extraction', status: 'completed' },
              { name: 'classification', status: 'completed' },
              { name: 'validation', status: 'completed' },
              { name: 'generation', status: 'completed' },
            ],
          },
          error: null,
        }),
      });
    });

    await page.goto(`/projects/${MOCK_PROJECT.id}`);
    await expect(page.getByText('Mehta Computers').first()).toBeVisible({ timeout: 15_000 });

    await expect(
      page.getByText(/download/i).first().or(page.getByText(/CMA.*xlsx/i).first())
    ).toBeVisible({ timeout: 10_000 });
  });

  test('uploaded file appears in file list', async ({ page }) => {
    await page.goto(`/projects/${MOCK_PROJECT.id}`);
    await expect(page.getByText('Mehta Computers').first()).toBeVisible({ timeout: 15_000 });

    await page.getByRole('tab', { name: /files/i }).click();
    await expect(page.getByText('test_pl.xlsx')).toBeVisible({ timeout: 10_000 });
  });

  test('review tab accessible when project is in reviewing state', async ({ page }) => {
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

    // Review tab should be available
    const reviewTab = page.getByRole('tab', { name: /review/i });
    await expect(reviewTab).toBeVisible({ timeout: 5_000 });
    await reviewTab.click();

    // Review tab content should load (may show items or a loading state)
    await expect(page.getByRole('tabpanel')).toBeVisible({ timeout: 5_000 });
  });
});
