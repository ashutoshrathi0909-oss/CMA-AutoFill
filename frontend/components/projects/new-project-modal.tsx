'use client';

import { useState, useEffect } from 'react';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Loader2 } from 'lucide-react';
import type { Client, ProjectCreate } from '@/lib/api/types';

const loanTypes = [
    { value: 'term_loan', label: 'Term Loan' },
    { value: 'working_capital', label: 'Working Capital' },
    { value: 'cc_od', label: 'CC/OD' },
    { value: 'other', label: 'Other' },
];

// Generate financial year options (current + 2 previous)
function getFinancialYears(): string[] {
    const now = new Date();
    const currentYear = now.getMonth() >= 3 ? now.getFullYear() : now.getFullYear() - 1;
    return Array.from({ length: 3 }, (_, i) => {
        const y = currentYear - i;
        return `${y}-${String(y + 1).slice(2)}`;
    });
}

interface NewProjectModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    clients: Client[];
    onSave: (data: ProjectCreate) => Promise<void>;
    isLoading?: boolean;
}

export function NewProjectModal({
    open,
    onOpenChange,
    clients,
    onSave,
    isLoading = false,
}: NewProjectModalProps) {
    const financialYears = getFinancialYears();
    const [formData, setFormData] = useState<ProjectCreate>({
        client_id: '',
        financial_year: financialYears[0],
        bank_name: '',
        loan_type: '',
        loan_amount: undefined,
    });
    const [errors, setErrors] = useState<Record<string, string>>({});

    useEffect(() => {
        if (open) {
            setFormData({
                client_id: '',
                financial_year: financialYears[0],
                bank_name: '',
                loan_type: '',
                loan_amount: undefined,
            });
            setErrors({});
        }
    }, [open]);

    const validate = (): boolean => {
        const newErrors: Record<string, string> = {};
        if (!formData.client_id) newErrors.client_id = 'Please select a client';
        if (!formData.financial_year) newErrors.financial_year = 'Financial year is required';
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!validate()) return;
        await onSave(formData);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-lg" style={{ backgroundColor: 'var(--bg-card)' }}>
                <DialogHeader>
                    <DialogTitle>Create New CMA Project</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4">
                    {/* Client */}
                    <div className="space-y-1.5">
                        <label className="text-sm font-medium text-foreground">
                            Client <span className="text-destructive">*</span>
                        </label>
                        <Select
                            value={formData.client_id}
                            onValueChange={(val) => {
                                setFormData((prev) => ({ ...prev, client_id: val }));
                                if (errors.client_id) setErrors((prev) => ({ ...prev, client_id: '' }));
                            }}
                        >
                            <SelectTrigger className="bg-background/50 border-border/30">
                                <SelectValue placeholder="Select a client" />
                            </SelectTrigger>
                            <SelectContent style={{ backgroundColor: 'var(--bg-card)' }}>
                                {clients.map((client) => (
                                    <SelectItem key={client.id} value={client.id}>{client.name}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        {errors.client_id && <p className="text-xs text-destructive">{errors.client_id}</p>}
                    </div>

                    {/* Financial Year */}
                    <div className="space-y-1.5">
                        <label className="text-sm font-medium text-foreground">
                            Financial Year <span className="text-destructive">*</span>
                        </label>
                        <Select
                            value={formData.financial_year}
                            onValueChange={(val) => setFormData((prev) => ({ ...prev, financial_year: val }))}
                        >
                            <SelectTrigger className="bg-background/50 border-border/30">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent style={{ backgroundColor: 'var(--bg-card)' }}>
                                {financialYears.map((fy) => (
                                    <SelectItem key={fy} value={fy}>FY {fy}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    {/* Bank & Loan */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                            <label className="text-sm font-medium text-foreground">Bank Name</label>
                            <Input
                                value={formData.bank_name || ''}
                                onChange={(e) => setFormData((prev) => ({ ...prev, bank_name: e.target.value }))}
                                placeholder="e.g., SBI"
                                className="bg-background/50 border-border/30"
                            />
                        </div>
                        <div className="space-y-1.5">
                            <label className="text-sm font-medium text-foreground">Loan Type</label>
                            <Select
                                value={formData.loan_type || ''}
                                onValueChange={(val) => setFormData((prev) => ({ ...prev, loan_type: val }))}
                            >
                                <SelectTrigger className="bg-background/50 border-border/30">
                                    <SelectValue placeholder="Select type" />
                                </SelectTrigger>
                                <SelectContent style={{ backgroundColor: 'var(--bg-card)' }}>
                                    {loanTypes.map((lt) => (
                                        <SelectItem key={lt.value} value={lt.value}>{lt.label}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    {/* Loan Amount */}
                    <div className="space-y-1.5">
                        <label className="text-sm font-medium text-foreground">Loan Amount (₹)</label>
                        <Input
                            type="number"
                            value={formData.loan_amount || ''}
                            onChange={(e) =>
                                setFormData((prev) => ({
                                    ...prev,
                                    loan_amount: e.target.value ? Number(e.target.value) : undefined,
                                }))
                            }
                            placeholder="e.g., 5000000"
                            className="bg-background/50 border-border/30"
                        />
                    </div>

                    <DialogFooter className="pt-2">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => onOpenChange(false)}
                            className="border-border/30"
                        >
                            Cancel
                        </Button>
                        <Button
                            type="submit"
                            className="bg-gold hover:bg-gold-hover text-primary-foreground font-semibold"
                            disabled={isLoading}
                        >
                            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Create Project
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
