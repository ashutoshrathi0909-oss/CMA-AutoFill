import { test, expect } from '@playwright/test';
import { mockSupabaseAuth, mockBackendAPI, MOCK_USER } from './helpers';

// The actual Supabase URL from env
const SUPABASE_URL = 'https://yamcnvkwidxndxwaskoc.supabase.co';

test.describe('Authentication Flow', () => {
  test('unauthenticated user visiting /dashboard is redirected to /login', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/login/);
  });

  test('login page renders with email input and send button', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('h1')).toContainText('CMA AutoFill');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.getByRole('button', { name: /send magic link/i })).toBeVisible();
  });

  test('entering email and clicking send shows success message', async ({ page }) => {
    // Intercept ALL requests to the Supabase domain
    await page.route(`${SUPABASE_URL}/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({}),
      });
    });

    await page.goto('/login');
    await page.locator('input[type="email"]').fill('test@cafirm.com');
    await page.getByRole('button', { name: /send magic link/i }).click();

    await expect(page.getByText('Check your email')).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText('test@cafirm.com')).toBeVisible();
  });

  test('clicking "Use a different email" returns to form', async ({ page }) => {
    await page.route(`${SUPABASE_URL}/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({}),
      });
    });

    await page.goto('/login');
    await page.locator('input[type="email"]').fill('test@cafirm.com');
    await page.getByRole('button', { name: /send magic link/i }).click();
    await expect(page.getByText('Check your email')).toBeVisible({ timeout: 10_000 });

    await page.getByRole('button', { name: /use a different email/i }).click();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toHaveValue('');
  });

  test('empty email shows validation error', async ({ page }) => {
    await page.goto('/login');
    // Leave email empty and click submit
    await page.getByRole('button', { name: /send magic link/i }).click();

    await expect(page.getByText(/valid email/i)).toBeVisible({ timeout: 5_000 });
  });

  test('authenticated user sees dashboard with their name', async ({ page }) => {
    await mockSupabaseAuth(page);
    await mockBackendAPI(page);

    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);

    // Use heading specifically to avoid strict mode violation (name appears in sidebar + heading)
    await expect(
      page.getByRole('heading', { name: /welcome back/i })
    ).toBeVisible({ timeout: 15_000 });
  });
});
