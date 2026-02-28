'use client';

import { usePipelineProgress, useRetryProcessing } from '@/lib/hooks/use-pipeline';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { CheckCircle2, Circle, Loader2, XCircle, FileSearch, HelpCircle, FileCheck, BrainCircuit, Activity, RotateCcw } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { PipelineStep } from '@/lib/api/types';

interface ProcessingProgressProps {
    projectId: string;
}

const STEP_ICONS: Record<string, React.ElementType> = {
    'upload': FileSearch,
    'extract': FileSearch,
    'classif': BrainCircuit,
    'validat': Activity,
    'review': HelpCircle,
    'generat': FileCheck,
};

function getStepIcon(stepName: string) {
    const name = stepName.toLowerCase();
    for (const [key, Icon] of Object.entries(STEP_ICONS)) {
        if (name.includes(key)) return Icon;
    }
    return Circle;
}

function formatDuration(startAt?: string, endAt?: string) {
    if (!startAt) return '';
    const start = new Date(startAt).getTime();
    const end = endAt ? new Date(endAt).getTime() : Date.now();
    const diff = Math.max(0, end - start) / 1000;

    if (diff < 60) return `${diff.toFixed(1)}s`;
    return `${Math.floor(diff / 60)}m ${(diff % 60).toFixed(0)}s`;
}

export function ProcessingProgress({ projectId }: ProcessingProgressProps) {
    const { data: progress, isLoading, error } = usePipelineProgress(projectId);
    const retryMutation = useRetryProcessing();

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center py-20 bg-[var(--bg-card)] rounded-xl border border-border/20">
                <Loader2 className="h-8 w-8 animate-spin text-[var(--gold)] mb-4" />
                <p className="text-muted-foreground">Loading pipeline status...</p>
            </div>
        );
    }

    if (error || !progress) {
        return (
            <div className="flex flex-col items-center justify-center py-20 bg-[var(--bg-card)] rounded-xl border border-red-500/20 text-red-500">
                <XCircle className="h-8 w-8 mb-4" />
                <p>Failed to load pipeline progress.</p>
                <Button
                    variant="outline"
                    className="mt-4 border-red-500/30 text-red-400 hover:bg-red-500/10"
                    onClick={() => retryMutation.mutate(projectId)}
                >
                    Retry Loading
                </Button>
            </div>
        );
    }

    const { status, pipeline_progress: percentage, steps, current_step, error_message } = progress;
    const isError = status === 'error';
    const isComplete = status === 'completed';

    return (
        <div className="rounded-xl border border-border/20 overflow-hidden" style={{ backgroundColor: 'var(--bg-card)' }}>
            <div className="p-6 border-b border-border/10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h3 className="text-lg font-semibold text-foreground">Pipeline Progress</h3>
                    <p className="text-sm text-muted-foreground mt-1">
                        {isError
                            ? 'Pipeline encountered an error'
                            : isComplete
                                ? 'Processing complete'
                                : `Currently: ${current_step || 'Initializing...'}`}
                    </p>
                </div>
                {isError && (
                    <Button
                        onClick={() => retryMutation.mutate(projectId)}
                        disabled={retryMutation.isPending}
                        variant="destructive"
                        size="sm"
                    >
                        {retryMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <RotateCcw className="h-4 w-4 mr-2" />}
                        Retry Failed Step
                    </Button>
                )}
            </div>

            <div className="p-6 bg-black/20">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-muted-foreground">Overall Completion</span>
                    <span className={cn(
                        "text-sm font-bold",
                        isError ? "text-red-400" : isComplete ? "text-green-400" : "text-[var(--gold)]"
                    )}>
                        {percentage}%
                    </span>
                </div>
                <Progress
                    value={percentage}
                    className="h-2.5 bg-background/50"
                />
            </div>

            <div className="p-2 sm:p-6">
                <div className="space-y-1">
                    {steps.length === 0 ? (
                        <div className="p-4 text-center text-muted-foreground text-sm">Waiting for pipeline to start...</div>
                    ) : (
                        steps.map((step, idx) => (
                            <StepRow key={idx} step={step} />
                        ))
                    )}
                </div>

                {isError && error_message && (
                    <div className="mt-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm font-mono whitespace-pre-wrap overflow-auto max-h-40">
                        {error_message}
                    </div>
                )}
            </div>
        </div>
    );
}

function StepRow({ step }: { step: PipelineStep }) {
    const Icon = getStepIcon(step.name);

    return (
        <div className={cn(
            "flex items-center justify-between p-3 sm:p-4 rounded-lg transition-colors",
            step.status === 'running' ? "bg-white/5 border border-white/10" : "hover:bg-white/5 border border-transparent"
        )}>
            <div className="flex items-center gap-4">
                <div className={cn(
                    "flex-shrink-0 flex items-center justify-center rounded-full p-2 h-10 w-10",
                    step.status === 'completed' ? "bg-green-500/20 text-green-400" :
                        step.status === 'failed' ? "bg-red-500/20 text-red-500" :
                            step.status === 'running' ? "bg-[var(--gold)]/20 text-[var(--gold)]" :
                                step.status === 'skipped' ? "bg-gray-500/20 text-gray-500" :
                                    "bg-background text-muted-foreground"
                )}>
                    {step.status === 'completed' ? <CheckCircle2 className="h-5 w-5" /> :
                        step.status === 'failed' ? <XCircle className="h-5 w-5" /> :
                            step.status === 'running' ? <Icon className="h-5 w-5 animate-pulse" /> :
                                <Icon className="h-5 w-5 opacity-50" />}
                </div>

                <div className="min-w-0">
                    <p className={cn(
                        "text-sm font-medium truncate",
                        step.status === 'running' ? "text-foreground" :
                            step.status === 'completed' ? "text-foreground" : "text-muted-foreground"
                    )}>
                        {step.name}
                    </p>
                    {step.error ? (
                        <p className="text-xs text-red-400 truncate mt-0.5 max-w-[200px] sm:max-w-md" title={step.error}>
                            {step.error}
                        </p>
                    ) : (
                        <p className="text-xs text-muted-foreground capitalize mt-0.5 flex items-center gap-2">
                            {step.status}
                            {step.status === 'running' && (
                                <span className="flex gap-0.5">
                                    <span className="h-1 w-1 bg-[var(--gold)] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                    <span className="h-1 w-1 bg-[var(--gold)] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                    <span className="h-1 w-1 bg-[var(--gold)] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                </span>
                            )}
                        </p>
                    )}
                </div>
            </div>

            <div className="text-xs font-mono text-muted-foreground text-right tabular-nums">
                {step.status !== 'pending' && <>{formatDuration(step.started_at, step.completed_at)}</>}
            </div>
        </div>
    );
}
