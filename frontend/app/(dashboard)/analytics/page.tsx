import { BarChart3 } from 'lucide-react';
import { EmptyState } from '@/components/ui/empty-state';

export default function AnalyticsPage() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-foreground">Analytics</h1>
                <p className="text-sm text-muted-foreground mt-1">
                    View classification accuracy and learning metrics
                </p>
            </div>
            <EmptyState
                icon={BarChart3}
                title="Coming in Phase 10"
                description="Analytics dashboard with learning metrics will be built in the next phase."
            />
        </div>
    );
}
