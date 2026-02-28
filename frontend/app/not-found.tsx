import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Home, SearchX } from 'lucide-react';

export default function NotFound() {
    return (
        <div
            className="min-h-screen flex items-center justify-center px-4"
            style={{ backgroundColor: '#0A1628' }}
        >
            <div className="text-center space-y-6 max-w-md">
                <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-gold/10">
                    <SearchX className="h-8 w-8 text-gold/60" />
                </div>
                <div className="space-y-2">
                    <h1 className="text-6xl font-bold text-gold">404</h1>
                    <h2 className="text-xl font-semibold text-white">Page not found</h2>
                    <p className="text-sm text-gray-400">
                        The page you&apos;re looking for doesn&apos;t exist or has been moved.
                    </p>
                </div>
                <Link href="/dashboard">
                    <Button className="bg-gold hover:bg-gold-hover text-primary-foreground font-semibold">
                        <Home className="mr-2 h-4 w-4" />
                        Back to Dashboard
                    </Button>
                </Link>
            </div>
        </div>
    );
}
