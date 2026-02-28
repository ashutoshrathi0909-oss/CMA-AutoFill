'use client';

import { CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';
// Note: In a full implementation, we'd fetch validation results from the backend.
// For Phase 10 frontend shell, we use a mocked visual layout structure that will be hooked up later
// when the backend validation endpoint `GET /projects/{id}/validation` is available.

interface ValidationResultsProps {
    projectId: string;
}

export function ValidationResults({ projectId }: ValidationResultsProps) {
    // Mocked data for UI Phase 10
    const summary = {
        total_items: 56,
        auto_classified: 48,
        reviewed_by_ca: 8
    };

    const errors = [
        { message: 'Missing: Trade Creditors for FY 2023-24' }
    ];

    const warnings = [
        { message: 'Selling Expenses increased 350% YoY - please verify' }
    ];

    const passed = [
        { message: 'Balance Sheet is balanced across all years' },
        { message: 'P&L Arithmetic totals are correct' }
    ];

    return (
        <div className="rounded-xl border border-border/20 overflow-hidden text-sm" style={{ backgroundColor: 'var(--bg-card)' }}>
            <div className="p-4 border-b border-border/10">
                <h3 className="font-semibold text-foreground flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    Validation Results
                </h3>
            </div>

            <div className="p-4 sm:p-6 space-y-4">
                {/* Passed Checks */}
                <ul className="space-y-2">
                    {passed.map((item, idx) => (
                        <li key={idx} className="flex items-start gap-2.5 text-foreground">
                            <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 shrink-0" />
                            <span>{item.message}</span>
                        </li>
                    ))}
                </ul>

                {/* Warnings */}
                {warnings.length > 0 && (
                    <ul className="space-y-2 mt-4">
                        {warnings.map((warn, idx) => (
                            <li key={idx} className="flex items-start gap-2.5 text-amber-500 bg-amber-500/10 p-2.5 rounded border border-amber-500/20">
                                <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
                                <span>{warn.message}</span>
                            </li>
                        ))}
                    </ul>
                )}

                {/* Errors */}
                {errors.length > 0 && (
                    <ul className="space-y-2 mt-4">
                        {errors.map((err, idx) => (
                            <li key={idx} className="flex items-start gap-2.5 text-red-500 bg-red-500/10 p-2.5 rounded border border-red-500/20">
                                <XCircle className="h-4 w-4 mt-0.5 shrink-0" />
                                <span>{err.message}</span>
                            </li>
                        ))}
                    </ul>
                )}

                {/* Summary Section */}
                <div className="mt-6 p-4 bg-black/20 rounded-lg border border-border/10 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between text-muted-foreground">
                    <div className="flex items-center gap-2">
                        <Info className="h-4 w-4 opacity-70" />
                        <span className="font-medium text-foreground">Summary:</span>
                    </div>
                    <div className="flex flex-wrap gap-x-6 gap-y-2 text-xs">
                        <div className="flex flex-col">
                            <span className="text-foreground text-lg font-bold">{summary.total_items}</span>
                            <span>Items Classified</span>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-foreground text-lg font-bold">{summary.auto_classified}</span>
                            <span>Auto-Classified</span>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-foreground text-lg font-bold">{summary.reviewed_by_ca}</span>
                            <span>Reviewed by CA</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
