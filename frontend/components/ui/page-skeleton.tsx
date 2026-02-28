import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';

interface PageSkeletonProps {
    type?: 'dashboard' | 'list' | 'detail';
    className?: string;
}

export function PageSkeleton({ type = 'list', className }: PageSkeletonProps) {
    if (type === 'dashboard') {
        return (
            <div className={cn('space-y-6', className)}>
                {/* Header skeleton */}
                <div className="flex items-center justify-between">
                    <div className="space-y-2">
                        <Skeleton className="h-8 w-64 bg-muted/50" />
                        <Skeleton className="h-4 w-48 bg-muted/50" />
                    </div>
                    <Skeleton className="h-10 w-32 bg-muted/50" />
                </div>

                {/* Stat cards skeleton */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {Array.from({ length: 4 }).map((_, i) => (
                        <div
                            key={i}
                            className="rounded-xl border border-border/20 p-6"
                            style={{ backgroundColor: 'var(--bg-card)' }}
                        >
                            <div className="flex items-start justify-between">
                                <div className="space-y-3">
                                    <Skeleton className="h-4 w-24 bg-muted/50" />
                                    <Skeleton className="h-9 w-16 bg-muted/50" />
                                </div>
                                <Skeleton className="h-10 w-10 rounded-lg bg-muted/50" />
                            </div>
                        </div>
                    ))}
                </div>

                {/* Status bar skeleton */}
                <div
                    className="rounded-xl border border-border/20 p-6"
                    style={{ backgroundColor: 'var(--bg-card)' }}
                >
                    <Skeleton className="h-4 w-32 bg-muted/50 mb-4" />
                    <Skeleton className="h-3 w-full rounded-full bg-muted/50 mb-4" />
                    <div className="flex gap-4">
                        {Array.from({ length: 4 }).map((_, i) => (
                            <Skeleton key={i} className="h-3 w-20 bg-muted/50" />
                        ))}
                    </div>
                </div>

                {/* Table skeleton */}
                <div
                    className="rounded-xl border border-border/20 overflow-hidden"
                    style={{ backgroundColor: 'var(--bg-card)' }}
                >
                    <div className="px-6 py-4 border-b border-border/10">
                        <Skeleton className="h-4 w-32 bg-muted/50" />
                    </div>
                    {Array.from({ length: 5 }).map((_, i) => (
                        <div
                            key={i}
                            className="px-6 py-4 flex items-center justify-between border-b border-border/10 last:border-b-0"
                        >
                            <div className="space-y-2">
                                <Skeleton className="h-4 w-40 bg-muted/50" />
                                <Skeleton className="h-3 w-28 bg-muted/50" />
                            </div>
                            <div className="flex items-center gap-3">
                                <Skeleton className="h-5 w-20 rounded-full bg-muted/50" />
                                <Skeleton className="h-1.5 w-20 rounded-full bg-muted/50" />
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    // List type
    return (
        <div className={cn('space-y-6', className)}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <Skeleton className="h-8 w-32 bg-muted/50" />
                <Skeleton className="h-10 w-32 bg-muted/50" />
            </div>

            {/* Search/filter bar */}
            <div className="flex items-center gap-4">
                <Skeleton className="h-10 flex-1 bg-muted/50" />
                <Skeleton className="h-10 w-40 bg-muted/50" />
            </div>

            {/* Table */}
            <div
                className="rounded-xl border border-border/20 overflow-hidden"
                style={{ backgroundColor: 'var(--bg-card)' }}
            >
                {/* Table header */}
                <div className="px-6 py-3 border-b border-border/10 flex items-center gap-4">
                    {Array.from({ length: 5 }).map((_, i) => (
                        <Skeleton key={i} className="h-3 w-24 bg-muted/50" />
                    ))}
                </div>
                {/* Table rows */}
                {Array.from({ length: 8 }).map((_, i) => (
                    <div
                        key={i}
                        className="px-6 py-4 flex items-center gap-4 border-b border-border/10 last:border-b-0"
                    >
                        {Array.from({ length: 5 }).map((_, j) => (
                            <Skeleton key={j} className="h-4 w-24 bg-muted/50" />
                        ))}
                    </div>
                ))}
            </div>
        </div>
    );
}
