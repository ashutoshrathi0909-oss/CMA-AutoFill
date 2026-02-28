'use client';

import { ArrowLeft, Calendar, Building2 } from 'lucide-react';
import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { Project, ProjectStatus } from '@/lib/api/types';

const statusConfig: Record<ProjectStatus, { label: string; className: string }> = {
    draft: { label: 'Draft', className: 'bg-gray-500/20 text-gray-300 border-gray-500/30' },
    extracting: { label: 'Extracting', className: 'bg-blue-500/20 text-blue-300 border-blue-500/30' },
    classifying: { label: 'Classifying', className: 'bg-blue-500/20 text-blue-300 border-blue-500/30' },
    validating: { label: 'Validating', className: 'bg-blue-500/20 text-blue-300 border-blue-500/30' },
    reviewing: { label: 'Reviewing', className: 'bg-amber-500/20 text-amber-300 border-amber-500/30' },
    generating: { label: 'Generating', className: 'bg-blue-500/20 text-blue-300 border-blue-500/30' },
    completed: { label: 'Completed', className: 'bg-green-500/20 text-green-300 border-green-500/30' },
    error: { label: 'Error', className: 'bg-red-500/20 text-red-300 border-red-500/30' },
};

const processingStatuses: ProjectStatus[] = ['extracting', 'classifying', 'validating', 'generating'];

interface CmaHeaderProps {
    project: Project;
}

export function CmaHeader({ project }: CmaHeaderProps) {
    const config = statusConfig[project.status];
    const isProcessing = processingStatuses.includes(project.status);
    const lastUpdated = new Date(project.updated_at).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
    });

    return (
        <div className="flex items-start justify-between gap-4 animate-fade-in">
            <div className="flex items-center gap-4">
                <Link
                    href="/projects"
                    className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors group"
                >
                    <ArrowLeft className="h-4 w-4 group-hover:-translate-x-0.5 transition-transform" />
                    Projects
                </Link>

                <div className="h-5 w-px bg-border/30" />

                <div>
                    <div className="flex items-center gap-3">
                        <h1 className="text-xl font-bold text-foreground">
                            CMA:{' '}
                            <span style={{ color: 'var(--gold)' }}>{project.client_name || 'Unknown Client'}</span>
                        </h1>
                        <Badge
                            variant="outline"
                            className={cn(
                                'text-[11px] border font-medium',
                                config.className,
                                isProcessing && 'animate-pulse-soft'
                            )}
                        >
                            {config.label}
                        </Badge>
                    </div>
                    <div className="flex items-center gap-3 mt-1">
                        <span className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Calendar className="h-3 w-3" />
                            FY {project.financial_year}
                        </span>
                        {project.bank_name && (
                            <span className="flex items-center gap-1 text-xs text-muted-foreground">
                                <Building2 className="h-3 w-3" />
                                {project.bank_name}
                            </span>
                        )}
                        <span className="text-xs text-muted-foreground">
                            Updated {lastUpdated}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}
