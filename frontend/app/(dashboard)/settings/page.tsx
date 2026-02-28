import { Settings } from 'lucide-react';
import { EmptyState } from '@/components/ui/empty-state';

export default function SettingsPage() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-foreground">Settings</h1>
                <p className="text-sm text-muted-foreground mt-1">
                    Manage your account and preferences
                </p>
            </div>
            <EmptyState
                icon={Settings}
                title="Coming Soon"
                description="Settings and preferences management will be available in a future update."
            />
        </div>
    );
}
