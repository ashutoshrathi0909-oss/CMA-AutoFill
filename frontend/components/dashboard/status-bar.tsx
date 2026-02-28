import { cn } from '@/lib/utils';
import type { ProjectStatus } from '@/lib/api/types';

const statusConfig: Record<string, { label: string; color: string }> = {
    draft: { label: 'Draft', color: '#6B7280' },
    extracting: { label: 'Extracting', color: '#3B82F6' },
    classifying: { label: 'Classifying', color: '#3B82F6' },
    validating: { label: 'Validating', color: '#3B82F6' },
    reviewing: { label: 'Reviewing', color: '#F59E0B' },
    generating: { label: 'Generating', color: '#3B82F6' },
    completed: { label: 'Completed', color: '#22C55E' },
    error: { label: 'Error', color: '#EF4444' },
};

interface StatusBarProps {
    projectsByStatus: Record<string, number>;
    className?: string;
}

export function StatusBar({ projectsByStatus, className }: StatusBarProps) {
    const total = Object.values(projectsByStatus).reduce((sum, count) => sum + count, 0);

    if (total === 0) {
        return (
            <div className={cn('rounded-xl border border-border/20 p-6', className)} style={{ backgroundColor: 'var(--bg-card)' }}>
                <p className="text-sm font-medium text-muted-foreground mb-3">Projects by Status</p>
                <p className="text-sm text-muted-foreground">No projects yet</p>
            </div>
        );
    }

    return (
        <div className={cn('rounded-xl border border-border/20 p-6', className)} style={{ backgroundColor: 'var(--bg-card)' }}>
            <p className="text-sm font-medium text-muted-foreground mb-4">Projects by Status</p>

            {/* Bar */}
            <div className="flex h-3 rounded-full overflow-hidden bg-background/50 mb-4">
                {Object.entries(projectsByStatus).map(([status, count]) => {
                    if (count === 0) return null;
                    const config = statusConfig[status];
                    const percentage = (count / total) * 100;
                    return (
                        <div
                            key={status}
                            className="transition-all duration-500"
                            style={{
                                width: `${percentage}%`,
                                backgroundColor: config?.color || '#6B7280',
                            }}
                            title={`${config?.label}: ${count}`}
                        />
                    );
                })}
            </div>

            {/* Legend */}
            <div className="flex flex-wrap gap-x-4 gap-y-2">
                {Object.entries(projectsByStatus).map(([status, count]) => {
                    if (count === 0) return null;
                    const config = statusConfig[status];
                    return (
                        <div key={status} className="flex items-center gap-1.5 text-xs">
                            <span
                                className="h-2.5 w-2.5 rounded-full"
                                style={{ backgroundColor: config?.color || '#6B7280' }}
                            />
                            <span className="text-muted-foreground">
                                {config?.label}: <span className="font-medium text-foreground">{count}</span>
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
