import { BookOpen } from 'lucide-react';
import { EmptyState } from '@/components/ui/empty-state';

export default function PrecedentsPage() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-foreground">Precedents</h1>
                <p className="text-sm text-muted-foreground mt-1">
                    Manage classification precedents and learning rules
                </p>
            </div>
            <EmptyState
                icon={BookOpen}
                title="Coming in Phase 10"
                description="Precedent management with the learning loop will be built in the next phase."
            />
        </div>
    );
}
