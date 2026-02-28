'use client';

import { useDashboardStats } from '@/lib/hooks/use-dashboard';
import { useAuth } from '@/lib/auth-context';
import { StatCard } from '@/components/dashboard/stat-card';
import { StatusBar } from '@/components/dashboard/status-bar';
import { RecentProjects } from '@/components/dashboard/recent-projects';
import { PageSkeleton } from '@/components/ui/page-skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { ErrorState } from '@/components/ui/error-state';
import { Button } from '@/components/ui/button';
import { Users, ClipboardCheck, FileCheck, IndianRupee, Plus, FileSpreadsheet } from 'lucide-react';
import Link from 'next/link';

function formatLakhs(amount: number): string {
    if (amount >= 100000) {
        return `₹${(amount / 100000).toFixed(2)}L`;
    }
    return `₹${amount.toLocaleString('en-IN')}`;
}

export default function DashboardPage() {
    const { user } = useAuth();
    const { data: stats, isLoading, error, refetch } = useDashboardStats();

    const displayName = user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'User';

    if (isLoading) {
        return <PageSkeleton type="dashboard" />;
    }

    if (error) {
        return <ErrorState message="Failed to load dashboard data" onRetry={() => refetch()} />;
    }

    if (!stats) {
        return (
            <EmptyState
                icon={FileSpreadsheet}
                title="Welcome to CMA AutoFill"
                description="Start by adding your first client, then create a CMA project."
                actionLabel="Add Client"
                actionHref="/clients"
            />
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-foreground">
                        Welcome back, {displayName}
                    </h1>
                    <p className="text-sm text-muted-foreground mt-1">
                        Here&apos;s what&apos;s happening with your CMA projects
                    </p>
                </div>
                <Link href="/projects">
                    <Button className="bg-gold hover:bg-gold-hover text-primary-foreground font-semibold">
                        <Plus className="mr-2 h-4 w-4" />
                        New CMA
                    </Button>
                </Link>
            </div>

            {/* Stat Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    title="Active Clients"
                    value={stats.total_clients}
                    icon={Users}
                    href="/clients"
                />
                <StatCard
                    title="Pending Reviews"
                    value={stats.pending_reviews}
                    icon={ClipboardCheck}
                    href="/review"
                />
                <StatCard
                    title="Completed CMAs"
                    value={stats.completed_this_month}
                    icon={FileCheck}
                />
                <StatCard
                    title="This Month"
                    value={stats.total_cost_this_month ? formatLakhs(stats.total_cost_this_month) : '₹0'}
                    icon={IndianRupee}
                />
            </div>

            {/* Status Bar */}
            {stats.projects_by_status && (
                <StatusBar projectsByStatus={stats.projects_by_status} />
            )}

            {/* Recent Projects */}
            {stats.recent_projects && stats.recent_projects.length > 0 ? (
                <RecentProjects projects={stats.recent_projects} />
            ) : (
                <EmptyState
                    icon={FileSpreadsheet}
                    title="No projects yet"
                    description="Create your first CMA project to get started!"
                    actionLabel="New CMA Project"
                    actionHref="/projects"
                />
            )}
        </div>
    );
}
