'use client';

import { useState, useCallback } from 'react';
import { useProjects, useCreateProject } from '@/lib/hooks/use-projects';
import { useClients } from '@/lib/hooks/use-clients';
import { PageSkeleton } from '@/components/ui/page-skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { ErrorState } from '@/components/ui/error-state';
import { NewProjectModal } from '@/components/projects/new-project-modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { Plus, Search, FileSpreadsheet, Eye, Download, RotateCcw, Play, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import type { ProjectStatus, ProjectCreate } from '@/lib/api/types';

const statusConfig: Record<ProjectStatus, { label: string; className: string; processing?: boolean }> = {
    draft: { label: 'Draft', className: 'bg-gray-500/20 text-gray-300 border-gray-500/30' },
    extracting: { label: 'Extracting', className: 'bg-blue-500/20 text-blue-300 border-blue-500/30', processing: true },
    classifying: { label: 'Classifying', className: 'bg-blue-500/20 text-blue-300 border-blue-500/30', processing: true },
    validating: { label: 'Validating', className: 'bg-blue-500/20 text-blue-300 border-blue-500/30', processing: true },
    reviewing: { label: 'Reviewing', className: 'bg-amber-500/20 text-amber-300 border-amber-500/30' },
    generating: { label: 'Generating', className: 'bg-blue-500/20 text-blue-300 border-blue-500/30', processing: true },
    completed: { label: 'Completed', className: 'bg-green-500/20 text-green-300 border-green-500/30' },
    error: { label: 'Error', className: 'bg-red-500/20 text-red-300 border-red-500/30' },
};

export default function ProjectsPage() {
    const [search, setSearch] = useState('');
    const [statusFilter, setStatusFilter] = useState<string>('all');
    const [clientFilter, setClientFilter] = useState<string>('all');
    const [page, setPage] = useState(1);
    const [modalOpen, setModalOpen] = useState(false);
    const router = useRouter();

    const { data, isLoading, error, refetch } = useProjects({
        search: search || undefined,
        status: statusFilter !== 'all' ? (statusFilter as ProjectStatus) : undefined,
        client_id: clientFilter !== 'all' ? clientFilter : undefined,
        page,
        per_page: 10,
    });

    const { data: clientsData } = useClients({ per_page: 100 });
    const createMutation = useCreateProject();

    const handleCreate = useCallback(async (formData: ProjectCreate) => {
        try {
            await createMutation.mutateAsync(formData);
            toast.success('CMA project created successfully');
            setModalOpen(false);
        } catch {
            toast.error('Failed to create project');
        }
    }, [createMutation]);

    if (isLoading) return <PageSkeleton type="list" />;

    if (error) {
        return <ErrorState message="Failed to load projects" onRetry={() => refetch()} />;
    }

    const projects = data?.projects || [];
    const total = data?.total || 0;
    const totalPages = Math.ceil(total / 10);
    const clients = clientsData?.clients || [];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-foreground">CMA Projects</h1>
                    <p className="text-sm text-muted-foreground mt-1">
                        Manage your Credit Monitoring Arrangement projects
                    </p>
                </div>
                <Button
                    onClick={() => setModalOpen(true)}
                    className="bg-gold hover:bg-gold-hover text-primary-foreground font-semibold"
                >
                    <Plus className="mr-2 h-4 w-4" />
                    New CMA Project
                </Button>
            </div>

            {/* Search & Filters */}
            <div className="flex items-center gap-4 flex-wrap">
                <div className="relative flex-1 min-w-[200px] max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Search projects..."
                        value={search}
                        onChange={(e) => {
                            setSearch(e.target.value);
                            setPage(1);
                        }}
                        className="pl-10 bg-background/50 border-border/30"
                    />
                </div>
                <Select
                    value={statusFilter}
                    onValueChange={(val) => {
                        setStatusFilter(val);
                        setPage(1);
                    }}
                >
                    <SelectTrigger className="w-40 bg-background/50 border-border/30">
                        <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent style={{ backgroundColor: 'var(--bg-card)' }}>
                        <SelectItem value="all">All Statuses</SelectItem>
                        {Object.entries(statusConfig).map(([value, config]) => (
                            <SelectItem key={value} value={value}>{config.label}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
                <Select
                    value={clientFilter}
                    onValueChange={(val) => {
                        setClientFilter(val);
                        setPage(1);
                    }}
                >
                    <SelectTrigger className="w-44 bg-background/50 border-border/30">
                        <SelectValue placeholder="Client" />
                    </SelectTrigger>
                    <SelectContent style={{ backgroundColor: 'var(--bg-card)' }}>
                        <SelectItem value="all">All Clients</SelectItem>
                        {clients.map((c) => (
                            <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            {/* Table */}
            {projects.length === 0 ? (
                <EmptyState
                    icon={FileSpreadsheet}
                    title={search || statusFilter !== 'all' || clientFilter !== 'all' ? 'No projects found' : 'No CMA projects yet'}
                    description={
                        search || statusFilter !== 'all' || clientFilter !== 'all'
                            ? 'Try adjusting your filters'
                            : 'Create your first CMA project to get started'
                    }
                    actionLabel={!search && statusFilter === 'all' && clientFilter === 'all' ? 'New CMA Project' : undefined}
                    onAction={() => setModalOpen(true)}
                />
            ) : (
                <>
                    <div
                        className="rounded-xl border border-border/20 overflow-hidden"
                        style={{ backgroundColor: 'var(--bg-card)' }}
                    >
                        <Table>
                            <TableHeader>
                                <TableRow className="border-border/10 hover:bg-transparent">
                                    <TableHead className="text-muted-foreground font-semibold text-xs uppercase tracking-wider">Client</TableHead>
                                    <TableHead className="text-muted-foreground font-semibold text-xs uppercase tracking-wider">Financial Year</TableHead>
                                    <TableHead className="text-muted-foreground font-semibold text-xs uppercase tracking-wider">Status</TableHead>
                                    <TableHead className="text-muted-foreground font-semibold text-xs uppercase tracking-wider">Progress</TableHead>
                                    <TableHead className="text-muted-foreground font-semibold text-xs uppercase tracking-wider">Updated</TableHead>
                                    <TableHead className="text-muted-foreground font-semibold text-xs uppercase tracking-wider w-20">Action</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {projects.map((project) => {
                                    const config = statusConfig[project.status];
                                    return (
                                        <TableRow
                                            key={project.id}
                                            className="border-border/10 hover:bg-accent/30 transition-colors cursor-pointer"
                                            onClick={() => router.push(`/projects/${project.id}`)}
                                        >
                                            <TableCell>
                                                <div>
                                                    <p className="font-medium text-foreground">{project.client_name || 'Unknown'}</p>
                                                    {project.bank_name && (
                                                        <p className="text-xs text-muted-foreground">{project.bank_name}</p>
                                                    )}
                                                </div>
                                            </TableCell>
                                            <TableCell className="text-sm text-foreground">
                                                {project.financial_year}
                                            </TableCell>
                                            <TableCell>
                                                <Badge
                                                    variant="outline"
                                                    className={cn(
                                                        'text-[11px] border',
                                                        config.className,
                                                        config.processing && 'animate-pulse-soft'
                                                    )}
                                                >
                                                    {config.label}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>
                                                <div className="flex items-center gap-2">
                                                    <div className="w-20 h-1.5 rounded-full bg-background/50 overflow-hidden">
                                                        <div
                                                            className="h-full rounded-full transition-all duration-500"
                                                            style={{
                                                                width: `${project.pipeline_progress}%`,
                                                                backgroundColor:
                                                                    project.status === 'error'
                                                                        ? '#EF4444'
                                                                        : project.status === 'completed'
                                                                            ? '#22C55E'
                                                                            : '#3B82F6',
                                                            }}
                                                        />
                                                    </div>
                                                    <span className="text-xs text-muted-foreground w-9 text-right">
                                                        {project.pipeline_progress}%
                                                    </span>
                                                </div>
                                            </TableCell>
                                            <TableCell className="text-sm text-muted-foreground">
                                                {new Date(project.updated_at).toLocaleDateString('en-IN', {
                                                    day: 'numeric',
                                                    month: 'short',
                                                })}
                                            </TableCell>
                                            <TableCell onClick={(e) => e.stopPropagation()}>
                                                {project.status === 'draft' && (
                                                    <Button
                                                        variant="ghost"
                                                        size="icon"
                                                        className="h-8 w-8 text-gold hover:text-gold-hover"
                                                        onClick={() => router.push(`/projects/${project.id}`)}
                                                    >
                                                        <Play className="h-4 w-4" />
                                                    </Button>
                                                )}
                                                {config.processing && (
                                                    <Loader2 className="h-4 w-4 text-blue-400 animate-spin mx-auto" />
                                                )}
                                                {project.status === 'reviewing' && (
                                                    <Button
                                                        variant="ghost"
                                                        size="icon"
                                                        className="h-8 w-8 text-amber-400 hover:text-amber-300"
                                                        onClick={() => router.push(`/projects/${project.id}`)}
                                                    >
                                                        <Eye className="h-4 w-4" />
                                                    </Button>
                                                )}
                                                {project.status === 'completed' && (
                                                    <Button
                                                        variant="ghost"
                                                        size="icon"
                                                        className="h-8 w-8 text-green-400 hover:text-green-300"
                                                        onClick={() => router.push(`/projects/${project.id}`)}
                                                    >
                                                        <Download className="h-4 w-4" />
                                                    </Button>
                                                )}
                                                {project.status === 'error' && (
                                                    <Button
                                                        variant="ghost"
                                                        size="icon"
                                                        className="h-8 w-8 text-red-400 hover:text-red-300"
                                                        onClick={() => router.push(`/projects/${project.id}`)}
                                                    >
                                                        <RotateCcw className="h-4 w-4" />
                                                    </Button>
                                                )}
                                            </TableCell>
                                        </TableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                    </div>

                    {/* Pagination */}
                    {totalPages > 1 && (
                        <div className="flex items-center justify-between">
                            <p className="text-sm text-muted-foreground">
                                Showing {(page - 1) * 10 + 1}–{Math.min(page * 10, total)} of {total}
                            </p>
                            <div className="flex items-center gap-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                                    disabled={page === 1}
                                    className="border-border/30"
                                >
                                    Previous
                                </Button>
                                {Array.from({ length: totalPages }, (_, i) => i + 1).slice(
                                    Math.max(0, page - 3),
                                    Math.min(totalPages, page + 2)
                                ).map((p) => (
                                    <Button
                                        key={p}
                                        variant={p === page ? 'default' : 'outline'}
                                        size="sm"
                                        onClick={() => setPage(p)}
                                        className={p === page ? 'bg-gold hover:bg-gold-hover text-primary-foreground' : 'border-border/30'}
                                    >
                                        {p}
                                    </Button>
                                ))}
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                                    disabled={page === totalPages}
                                    className="border-border/30"
                                >
                                    Next
                                </Button>
                            </div>
                        </div>
                    )}
                </>
            )}

            {/* New Project Modal */}
            <NewProjectModal
                open={modalOpen}
                onOpenChange={setModalOpen}
                clients={clients}
                onSave={handleCreate}
                isLoading={createMutation.isPending}
            />
        </div>
    );
}
