import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

/**
 * Auth layout — if user already has a session cookie, redirect to dashboard.
 */
export default async function AuthLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const cookieStore = await cookies();
    const allCookies = cookieStore.getAll();
    const hasSession = allCookies.some((c) => c.name.includes('-auth-token'));

    if (hasSession) {
        redirect('/dashboard');
    }

    return (
        <div
            className="min-h-screen flex items-center justify-center px-4"
            style={{ backgroundColor: '#0A1628' }}
        >
            <div className="w-full max-w-md">{children}</div>
        </div>
    );
}
