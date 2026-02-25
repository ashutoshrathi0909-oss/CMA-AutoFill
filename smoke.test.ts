import { test, expect } from '@playwright/test';

const BASE_URL = process.env.APP_URL || 'http://localhost:3000';

test.describe('CMA AutoFill Smoke Tests', () => {

    test('Homepage loads successfully', async ({ page }) => {
        const response = await page.goto(BASE_URL);
        expect(response?.status()).toBeLessThan(400);
        await expect(page).toHaveTitle(/CMA/i);
    });

    test('Login page is accessible', async ({ page }) => {
        await page.goto(`${BASE_URL}/login`);
        // Check for email input (magic link login)
        await expect(page.locator('input[type="email"]')).toBeVisible();
    });

    test('API health check responds 200', async ({ request }) => {
        // Replace with your actual backend URL when deployed
        const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
        const response = await request.get(`${BACKEND_URL}/health`);
        expect(response.status()).toBe(200);
    });

    test('No console errors on homepage', async ({ page }) => {
        const errors: string[] = [];
        page.on('console', msg => {
            if (msg.type() === 'error') errors.push(msg.text());
        });
        await page.goto(BASE_URL);
        // Allow minor third-party errors but fail on critical ones
        const criticalErrors = errors.filter(e => !e.includes('favicon'));
        expect(criticalErrors).toHaveLength(0);
    });

});
