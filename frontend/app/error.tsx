'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCcw } from 'lucide-react';

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        console.error('Unhandled error:', error);
    }, [error]);

    return (
        <div
            className="min-h-screen flex items-center justify-center px-4"
            style={{ backgroundColor: '#0A1628' }}
        >
            <div className="text-center space-y-6 max-w-md">
                <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-red-500/10">
                    <AlertTriangle className="h-8 w-8 text-red-400" />
                </div>
                <div className="space-y-2">
                    <h2 className="text-xl font-semibold text-white">Something went wrong</h2>
                    <p className="text-sm text-gray-400">
                        An unexpected error occurred. Please try again or contact support if the issue persists.
                    </p>
                </div>
                <Button
                    onClick={reset}
                    variant="outline"
                    className="border-gray-600 text-gray-200 hover:bg-gray-800"
                >
                    <RefreshCcw className="mr-2 h-4 w-4" />
                    Try again
                </Button>
            </div>
        </div>
    );
}
