'use client';

import { Building2, CreditCard, Calendar, User, Hash, Banknote, Clock } from 'lucide-react';
import type { Project } from '@/lib/api/types';

interface CmaMetadataProps {
    project: Project;
    fileCount?: number;
    reviewCount?: number;
}

function formatLakhs(amount: number): string {
    // Format in Indian number system
    const formatted = amount.toLocaleString('en-IN');
    return `₹${formatted}`;
}

function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        timeZone: 'Asia/Kolkata',
    });
}

const entityTypeLabels: Record<string, string> = {
    partnership: 'Partnership',
    proprietorship: 'Proprietorship',
    company: 'Company',
    llp: 'LLP',
    trading: 'Trading',
};

export function CmaMetadata({ project, fileCount = 0, reviewCount = 0 }: CmaMetadataProps) {
    const items = [
        {
            icon: User,
            label: 'Client',
            value: project.client_name || '—',
        },
        {
            icon: Hash,
            label: 'Entity Type',
            value: entityTypeLabels[project.loan_type || ''] || '—',
        },
        {
            icon: Calendar,
            label: 'Financial Year',
            value: project.financial_year,
        },
        {
            icon: Building2,
            label: 'Bank',
            value: project.bank_name || '—',
        },
        {
            icon: CreditCard,
            label: 'Loan Type',
            value: project.loan_type || '—',
        },
        {
            icon: Banknote,
            label: 'Loan Amount',
            value: project.loan_amount ? formatLakhs(project.loan_amount) : '—',
        },
        {
            icon: Clock,
            label: 'Created',
            value: formatDate(project.created_at),
        },
        {
            icon: Clock,
            label: 'Updated',
            value: formatDate(project.updated_at),
        },
    ];

    return (
        <div
            className="rounded-xl border border-border/20 p-5"
            style={{ backgroundColor: 'var(--bg-card)' }}
        >
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4">
                Project Details
            </h3>
            <dl className="grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-4">
                {items.map(({ icon: Icon, label, value }) => (
                    <div key={label} className="min-w-0">
                        <dt className="flex items-center gap-1.5 text-xs text-muted-foreground mb-0.5">
                            <Icon className="h-3 w-3 flex-shrink-0" />
                            {label}
                        </dt>
                        <dd className="text-sm font-medium text-foreground truncate">{value}</dd>
                    </div>
                ))}
            </dl>
            {(fileCount > 0 || reviewCount > 0) && (
                <div className="mt-4 pt-4 border-t border-border/10 flex items-center gap-6">
                    {fileCount > 0 && (
                        <div className="text-sm">
                            <span className="font-semibold text-foreground">{fileCount}</span>
                            <span className="text-muted-foreground ml-1">file{fileCount !== 1 ? 's' : ''} uploaded</span>
                        </div>
                    )}
                    {reviewCount > 0 && (
                        <div className="text-sm">
                            <span className="font-semibold" style={{ color: 'var(--warning)' }}>{reviewCount}</span>
                            <span className="text-muted-foreground ml-1">item{reviewCount !== 1 ? 's' : ''} to review</span>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
