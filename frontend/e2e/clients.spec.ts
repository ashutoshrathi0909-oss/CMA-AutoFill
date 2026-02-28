import { test, expect } from '@playwright/test';
import {
  mockSupabaseAuth,
  mockBackendAPI,
  mockClientsAPI,
  API_BASE,
} from './helpers';

test.describe('Client Management', () => {
  test.beforeEach(async ({ page }) => {
    await mockSupabaseAuth(page);
    await mockBackendAPI(page);
    await mockClientsAPI(page);
  });

  test('clients page loads and shows client list', async ({ page }) => {
    await page.goto('/clients');

    // Use heading to avoid sidebar link match
    await expect(page.getByRole('heading', { name: 'Clients' })).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText('Mehta Computers')).toBeVisible();
    await expect(page.getByText('Sharma Textiles')).toBeVisible();
  });

  test('empty state shown when no clients match search', async ({ page }) => {
    await page.goto('/clients');
    await expect(page.getByRole('heading', { name: 'Clients' })).toBeVisible({ timeout: 15_000 });

    // Wait for initial data to load first
    await expect(page.getByText('Mehta Computers')).toBeVisible({ timeout: 10_000 });

    // Now type a non-matching search — the mock filters by name
    await page.getByPlaceholder('Search clients...').fill('zzzznonexistent');

    // Wait for "No clients found" empty state
    await expect(page.getByText(/no clients found/i)).toBeVisible({ timeout: 10_000 });
  });

  test('add client button opens form modal', async ({ page }) => {
    await page.goto('/clients');
    await expect(page.getByRole('heading', { name: 'Clients' })).toBeVisible({ timeout: 15_000 });

    await page.getByRole('button', { name: /add client/i }).click();

    // Modal should be visible (a dialog element)
    await expect(page.locator('[role="dialog"]')).toBeVisible({ timeout: 5_000 });
  });

  test('creating a new client opens and shows form fields', async ({ page }) => {
    await page.goto('/clients');
    await expect(page.getByRole('heading', { name: 'Clients' })).toBeVisible({ timeout: 15_000 });

    await page.getByRole('button', { name: /add client/i }).click();
    await expect(page.locator('[role="dialog"]')).toBeVisible({ timeout: 5_000 });

    // Verify dialog has form elements
    await expect(page.locator('[role="dialog"] input').first()).toBeVisible();
    await expect(page.locator('[role="dialog"] button[type="submit"]').or(
      page.locator('[role="dialog"]').getByRole('button', { name: /save|create|add|submit/i })
    )).toBeVisible();
  });

  test('client search filters the list', async ({ page }) => {
    await page.goto('/clients');
    await expect(page.getByText('Mehta Computers')).toBeVisible({ timeout: 15_000 });

    await page.getByPlaceholder('Search clients...').fill('Mehta');
    await expect(page.getByText('Mehta Computers')).toBeVisible();
  });

  test('edit client button exists for each client row', async ({ page }) => {
    await page.goto('/clients');
    await expect(page.getByText('Mehta Computers')).toBeVisible({ timeout: 15_000 });

    const editButtons = page.locator('button').filter({ has: page.locator('.lucide-pencil') });
    await expect(editButtons.first()).toBeVisible();
  });

  test('delete confirmation dialog appears', async ({ page }) => {
    await page.goto('/clients');
    await expect(page.getByText('Mehta Computers')).toBeVisible({ timeout: 15_000 });

    const deleteButtons = page.locator('button').filter({ has: page.locator('.lucide-trash-2') });
    await deleteButtons.first().click();

    await expect(page.getByText(/delete client/i)).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText(/cannot be undone/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /cancel/i })).toBeVisible();
  });
});
