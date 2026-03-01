'use client';

import { useState, useMemo, useCallback } from 'react';
import { useClients, useCreateClient, useUpdateClient, useDeleteClient } from '@/lib/hooks/use-clients';
import { PageSkeleton } from '@/components/ui/page-skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { ErrorState } from '@/components/ui/error-state';
import { ClientFormModal } from '@/components/clients/client-form-modal';
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
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Plus, Search, Pencil, Trash2, Users } from 'lucide-react';
import { toast } from 'sonner';
import type { Client, ClientCreate, EntityType } from '@/lib/api/types';

const entityTypeLabels: Record<EntityType, string> = {
    partnership: 'Partnership',
    proprietorship: 'Proprietorship',
    company: 'Company',
    llp: 'LLP',
    trading: 'Trading',
};

const entityTypeBadgeColors: Record<EntityType, string> = {
    partnership: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    proprietorship: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    company: 'bg-green-500/20 text-green-300 border-green-500/30',
    llp: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    trading: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
};

export default function ClientsPage() {
    const [search, setSearch] = useState('');
    const [entityTypeFilter, setEntityTypeFilter] = useState<string>('all');
    const [page, setPage] = useState(1);
    const [modalOpen, setModalOpen] = useState(false);
    const [editingClient, setEditingClient] = useState<Client | null>(null);
    const [deleteTarget, setDeleteTarget] = useState<Client | null>(null);

    const { data, isLoading, error, refetch } = useClients({
        search: search || undefined,
        entity_type: entityTypeFilter !== 'all' ? (entityTypeFilter as EntityType) : undefined,
        page,
        per_page: 10,
    });

    const createMutation = useCreateClient();
    const updateMutation = useUpdateClient();
    const deleteMutation = useDeleteClient();

    const handleSave = useCallback(async (formData: ClientCreate) => {
        try {
            if (editingClient) {
                await updateMutation.mutateAsync({ id: editingClient.id, data: formData });
                toast.success('Client updated successfully');
            } else {
                await createMutation.mutateAsync(formData);
                toast.success('Client created successfully');
            }
            setModalOpen(false);
            setEditingClient(null);
        } catch (err) {
            toast.error(editingClient ? 'Failed to update client' : 'Failed to create client');
        }
    }, [editingClient, createMutation, updateMutation]);

    const handleDelete = useCallback(async () => {
        if (!deleteTarget) return;
        try {
            await deleteMutation.mutateAsync(deleteTarget.id);
            toast.success('Client deleted successfully');
            setDeleteTarget(null);
        } catch {
            toast.error('Failed to delete client');
        }
    }, [deleteTarget, deleteMutation]);

    const handleEdit = useCallback((client: Client) => {
        setEditingClient(client);
        setModalOpen(true);
    }, []);

    const handleAddNew = useCallback(() => {
        setEditingClient(null);
        setModalOpen(true);
    }, []);

    if (isLoading) return <PageSkeleton type="list" />;

    if (error) {
        return <ErrorState message="Failed to load clients" onRetry={() => refetch()} />;
    }

    const clients = data?.items || [];
    const total = data?.total || 0;
    const totalPages = Math.ceil(total / 10);

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-foreground">Clients</h1>
                    <p className="text-sm text-muted-foreground mt-1">
                        Manage your clients and their CMA projects
                    </p>
                </div>
                <Button
                    onClick={handleAddNew}
                    className="bg-gold hover:bg-gold-hover text-primary-foreground font-semibold"
                >
                    <Plus className="mr-2 h-4 w-4" />
                    Add Client
                </Button>
            </div>

            {/* Search & Filter */}
            <div className="flex items-center gap-4">
                <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Search clients..."
                        value={search}
                        onChange={(e) => {
                            setSearch(e.target.value);
                            setPage(1);
                        }}
                        className="pl-10 bg-background/50 border-border/30"
                    />
                </div>
                <Select
                    value={entityTypeFilter}
                    onValueChange={(val) => {
                        setEntityTypeFilter(val);
                        setPage(1);
                    }}
                >
                    <SelectTrigger className="w-44 bg-background/50 border-border/30">
                        <SelectValue placeholder="Entity Type" />
                    </SelectTrigger>
                    <SelectContent style={{ backgroundColor: 'var(--bg-card)' }}>
                        <SelectItem value="all">All Types</SelectItem>
                        {Object.entries(entityTypeLabels).map(([value, label]) => (
                            <SelectItem key={value} value={value}>{label}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            {/* Table */}
            {clients.length === 0 ? (
                <EmptyState
                    icon={Users}
                    title={search || entityTypeFilter !== 'all' ? 'No clients found' : 'No clients yet'}
                    description={
                        search || entityTypeFilter !== 'all'
                            ? 'Try adjusting your search or filter'
                            : 'Add your first client to start creating CMAs'
                    }
                    actionLabel={!search && entityTypeFilter === 'all' ? 'Add Client' : undefined}
                    onAction={handleAddNew}
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
                                    <TableHead className="text-muted-foreground font-semibold text-xs uppercase tracking-wider">Name</TableHead>
                                    <TableHead className="text-muted-foreground font-semibold text-xs uppercase tracking-wider">Entity Type</TableHead>
                                    <TableHead className="text-muted-foreground font-semibold text-xs uppercase tracking-wider">Contact</TableHead>
                                    <TableHead className="text-muted-foreground font-semibold text-xs uppercase tracking-wider">Projects</TableHead>
                                    <TableHead className="text-muted-foreground font-semibold text-xs uppercase tracking-wider">Added</TableHead>
                                    <TableHead className="text-muted-foreground font-semibold text-xs uppercase tracking-wider w-20">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {clients.map((client) => (
                                    <TableRow
                                        key={client.id}
                                        className="border-border/10 hover:bg-accent/30 transition-colors cursor-pointer"
                                    >
                                        <TableCell>
                                            <div>
                                                <p className="font-medium text-foreground">{client.name}</p>
                                                {client.pan && (
                                                    <p className="text-xs text-muted-foreground">PAN: {client.pan}</p>
                                                )}
                                            </div>
                                        </TableCell>
                                        <TableCell>
                                            <Badge
                                                variant="outline"
                                                className={entityTypeBadgeColors[client.entity_type]}
                                            >
                                                {entityTypeLabels[client.entity_type]}
                                            </Badge>
                                        </TableCell>
                                        <TableCell>
                                            <div className="text-sm">
                                                {client.contact_person && (
                                                    <p className="text-foreground">{client.contact_person}</p>
                                                )}
                                                {client.email && (
                                                    <p className="text-xs text-muted-foreground">{client.email}</p>
                                                )}
                                            </div>
                                        </TableCell>
                                        <TableCell>
                                            <span className="text-sm text-foreground">{client.projects_count || 0}</span>
                                        </TableCell>
                                        <TableCell>
                                            <span className="text-sm text-muted-foreground">
                                                {new Date(client.created_at).toLocaleDateString('en-IN', {
                                                    month: 'short',
                                                    year: 'numeric',
                                                })}
                                            </span>
                                        </TableCell>
                                        <TableCell>
                                            <div className="flex items-center gap-1">
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-8 w-8 text-muted-foreground hover:text-foreground"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleEdit(client);
                                                    }}
                                                >
                                                    <Pencil className="h-3.5 w-3.5" />
                                                </Button>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-8 w-8 text-muted-foreground hover:text-destructive"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setDeleteTarget(client);
                                                    }}
                                                >
                                                    <Trash2 className="h-3.5 w-3.5" />
                                                </Button>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ))}
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

            {/* Add/Edit Modal */}
            <ClientFormModal
                open={modalOpen}
                onOpenChange={(open) => {
                    setModalOpen(open);
                    if (!open) setEditingClient(null);
                }}
                client={editingClient}
                onSave={handleSave}
                isLoading={createMutation.isPending || updateMutation.isPending}
            />

            {/* Delete Confirmation */}
            <AlertDialog
                open={!!deleteTarget}
                onOpenChange={(open) => !open && setDeleteTarget(null)}
            >
                <AlertDialogContent style={{ backgroundColor: 'var(--bg-card)' }}>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Delete Client</AlertDialogTitle>
                        <AlertDialogDescription>
                            Are you sure you want to delete &quot;{deleteTarget?.name}&quot;? This action cannot be undone.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel className="border-border/30">Cancel</AlertDialogCancel>
                        <AlertDialogAction
                            onClick={handleDelete}
                            className="bg-destructive hover:bg-destructive/90"
                        >
                            Delete
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
}
