'use client';

import Link from 'next/link';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Eye, Download, RotateCcw } from 'lucide-react';
import type { Project, ProjectStatus } from '@/lib/api/types';

const statusStyles: Record<ProjectStatus, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline'; className: string }> = {
    draft: { label: 'Draft', variant: 'secondary', className: 'bg-gray-500/20 text-gray-300 border-gray-500/30' },
    extracting: { label: 'Extracting', variant: 'default', className: 'bg-blue-500/20 text-blue-300 border-blue-500/30 animate-pulse-soft' },
    classifying: { label: 'Classifying', variant: 'default', className: 'bg-blue-500/20 text-blue-300 border-blue-500/30 animate-pulse-soft' },
    validating: { label: 'Validating', variant: 'default', className: 'bg-blue-500/20 text-blue-300 border-blue-500/30 animate-pulse-soft' },
    reviewing: { label: 'Reviewing', variant: 'default', className: 'bg-amber-500/20 text-amber-300 border-amber-500/30' },
    generating: { label: 'Generating', variant: 'default', className: 'bg-blue-500/20 text-blue-300 border-blue-500/30 animate-pulse-soft' },
    completed: { label: 'Completed', variant: 'default', className: 'bg-green-500/20 text-green-300 border-green-500/30' },
    error: { label: 'Error', variant: 'destructive', className: 'bg-red-500/20 text-red-300 border-red-500/30' },
};

function formatTimeAgo(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}

interface RecentProjectsProps {
    projects: Project[];
    className?: string;
}

export function RecentProjects({ projects, className }: RecentProjectsProps) {
    if (projects.length === 0) {
        return null;
    }

    return (
        <div
            className={cn('rounded-xl border border-border/20 overflow-hidden', className)}
            style={{ backgroundColor: 'var(--bg-card)' }}
        >
            <div className="px-6 py-4 border-b border-border/10">
                <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-foreground">Recent Projects</h3>
                    <Link href="/projects" className="text-xs text-gold hover:text-gold-hover transition-colors">
                        View all →
                    </Link>
                </div>
            </div>

            <div className="divide-y divide-border/10">
                {projects.slice(0, 5).map((project) => {
                    const style = statusStyles[project.status];
                    return (
                        <div
                            key={project.id}
                            className="px-6 py-4 flex items-center justify-between hover:bg-accent/30 transition-colors"
                        >
                            <div className="flex items-center gap-4 min-w-0 flex-1">
                                <div className="min-w-0">
                                    <p className="text-sm font-medium text-foreground truncate">
                                        {project.client_name || 'Unknown Client'}
                                    </p>
                                    <p className="text-xs text-muted-foreground">
                                        FY {project.financial_year} · Updated {formatTimeAgo(project.updated_at)}
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <Badge variant={style.variant} className={cn('text-[11px] border', style.className)}>
                                    {style.label}
                                </Badge>
                                {/* Progress bar */}
                                <div className="hidden sm:flex w-20 h-1.5 rounded-full bg-background/50 overflow-hidden">
                                    <div
                                        className="h-full rounded-full transition-all duration-500"
                                        style={{
                                            width: `${project.pipeline_progress}%`,
                                            backgroundColor: project.status === 'error' ? '#EF4444' : project.status === 'completed' ? '#22C55E' : '#3B82F6',
                                        }}
                                    />
                                </div>
                                {/* Action buttons */}
                                <div className="flex items-center gap-1">
                                    {project.status === 'completed' && (
                                        <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground">
                                            <Download className="h-4 w-4" />
                                        </Button>
                                    )}
                                    {project.status === 'reviewing' && (
                                        <Link href={`/review?project_id=${project.id}`}>
                                            <Button variant="ghost" size="icon" className="h-8 w-8 text-amber-400 hover:text-amber-300">
                                                <Eye className="h-4 w-4" />
                                            </Button>
                                        </Link>
                                    )}
                                    {project.status === 'error' && (
                                        <Button variant="ghost" size="icon" className="h-8 w-8 text-red-400 hover:text-red-300">
                                            <RotateCcw className="h-4 w-4" />
                                        </Button>
                                    )}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
