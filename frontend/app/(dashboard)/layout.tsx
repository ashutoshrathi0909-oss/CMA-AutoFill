import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { DashboardShell } from './dashboard-shell';

/**
 * Server-side auth guard for all dashboard routes.
 *
 * Checks for Supabase session cookies before rendering. This replaces
 * the Edge Runtime middleware approach which crashed on Vercel due to
 * __dirname not being available in Edge Runtime.
 *
 * Supabase stores auth tokens in cookies named `sb-<ref>-auth-token`.
 * We just check existence — JWT verification happens on the API server.
 */
export default async function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const cookieStore = await cookies();
    const allCookies = cookieStore.getAll();
    const hasSession = allCookies.some((c) => c.name.includes('-auth-token'));

    if (!hasSession) {
        redirect('/login');
    }

    return <DashboardShell>{children}</DashboardShell>;
}
