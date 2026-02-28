'use client';

import { usePathname } from 'next/navigation';
import { ChevronRight, Home } from 'lucide-react';
import Link from 'next/link';

const routeLabels: Record<string, string> = {
    dashboard: 'Dashboard',
    clients: 'Clients',
    projects: 'CMA Projects',
    review: 'Review Queue',
    precedents: 'Precedents',
    analytics: 'Analytics',
    settings: 'Settings',
};

export function Breadcrumb() {
    const pathname = usePathname();
    const segments = pathname.split('/').filter(Boolean);

    if (segments.length === 0) return null;

    return (
        <nav className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <Link href="/dashboard" className="hover:text-foreground transition-colors">
                <Home className="h-4 w-4" />
            </Link>
            {segments.map((segment, index) => {
                const href = '/' + segments.slice(0, index + 1).join('/');
                const isLast = index === segments.length - 1;
                const label = routeLabels[segment] || segment.charAt(0).toUpperCase() + segment.slice(1);

                return (
                    <span key={href} className="flex items-center gap-1.5">
                        <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/50" />
                        {isLast ? (
                            <span className="font-medium text-foreground">{label}</span>
                        ) : (
                            <Link href={href} className="hover:text-foreground transition-colors">
                                {label}
                            </Link>
                        )}
                    </span>
                );
            })}
        </nav>
    );
}
