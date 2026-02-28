'use client';

import { Check, X, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { PipelineStep } from '@/lib/api/types';

const STEP_LABELS = ['Upload', 'Extract', 'Classify', 'Review', 'Generate'];

// Map pipeline step names returned from backend to our 5-step indices
function getStepIndex(stepName: string): number {
    const name = stepName.toLowerCase();
    if (name.includes('upload') || name.includes('file')) return 0;
    if (name.includes('extract')) return 1;
    if (name.includes('classif')) return 2;
    if (name.includes('review') || name.includes('validat')) return 3;
    if (name.includes('generat')) return 4;
    return -1;
}

interface PipelineStepperProps {
    steps: PipelineStep[];
    overallStatus: string;
}

type StepState = 'completed' | 'running' | 'failed' | 'skipped' | 'pending';

function deriveStepStates(steps: PipelineStep[], overallStatus: string): StepState[] {
    const states: StepState[] = ['pending', 'pending', 'pending', 'pending', 'pending'];

    // Mark upload as completed if there are any steps at all (files were uploaded)
    if (steps.length > 0 || overallStatus !== 'draft') {
        states[0] = 'completed';
    }

    // Process backend steps
    for (const step of steps) {
        const idx = getStepIndex(step.name);
        if (idx >= 0) {
            switch (step.status) {
                case 'completed': states[idx] = 'completed'; break;
                case 'running': states[idx] = 'running'; break;
                case 'failed': states[idx] = 'failed'; break;
                case 'skipped': states[idx] = 'skipped'; break;
            }
        }
    }

    // Heuristics from overall status
    if (overallStatus === 'extracting') states[1] = states[1] === 'pending' ? 'running' : states[1];
    if (overallStatus === 'classifying') {
        states[1] = states[1] === 'pending' ? 'completed' : states[1];
        states[2] = states[2] === 'pending' ? 'running' : states[2];
    }
    if (overallStatus === 'validating') {
        states[1] = 'completed'; states[2] = 'completed';
        states[3] = states[3] === 'pending' ? 'running' : states[3];
    }
    if (overallStatus === 'reviewing') {
        states[1] = 'completed'; states[2] = 'completed'; states[3] = 'running';
    }
    if (overallStatus === 'generating') {
        states[1] = 'completed'; states[2] = 'completed'; states[3] = 'completed';
        states[4] = states[4] === 'pending' ? 'running' : states[4];
    }
    if (overallStatus === 'completed') {
        states.fill('completed');
    }
    if (overallStatus === 'error') {
        // Find the running step and mark it failed
        const runningIdx = states.indexOf('running');
        if (runningIdx >= 0) states[runningIdx] = 'failed';
    }

    return states;
}

export function PipelineStepper({ steps, overallStatus }: PipelineStepperProps) {
    const stepStates = deriveStepStates(steps, overallStatus);

    return (
        <div
            className="rounded-xl border border-border/20 p-6"
            style={{ backgroundColor: 'var(--bg-card)' }}
        >
            <div className="flex items-center">
                {STEP_LABELS.map((label, idx) => {
                    const state = stepStates[idx];
                    const isLast = idx === STEP_LABELS.length - 1;

                    return (
                        <div key={label} className="flex items-center flex-1">
                            {/* Circle */}
                            <div className="flex flex-col items-center gap-2">
                                <div
                                    className={cn(
                                        'w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-500 relative',
                                        state === 'completed' && 'bg-green-500/20 border-green-500 text-green-400',
                                        state === 'running' && 'border-[var(--gold)] text-[var(--gold)] animate-pulse-soft',
                                        state === 'failed' && 'bg-red-500/20 border-red-500 text-red-400',
                                        state === 'skipped' && 'bg-gray-500/10 border-gray-600 text-gray-500',
                                        state === 'pending' && 'bg-background border-border/40 text-muted-foreground',
                                    )}
                                >
                                    {state === 'running' && (
                                        <div className="absolute inset-0 rounded-full border-2 border-[var(--gold)] opacity-40 animate-ping" />
                                    )}
                                    {state === 'completed' && <Check className="h-4 w-4" />}
                                    {state === 'running' && <span className="text-xs font-bold">{idx + 1}</span>}
                                    {state === 'failed' && <X className="h-4 w-4" />}
                                    {state === 'skipped' && <Minus className="h-4 w-4" />}
                                    {state === 'pending' && <span className="text-xs text-muted-foreground">{idx + 1}</span>}
                                </div>
                                <span
                                    className={cn(
                                        'text-xs font-medium whitespace-nowrap',
                                        state === 'completed' && 'text-green-400',
                                        state === 'running' && 'text-[var(--gold)]',
                                        state === 'failed' && 'text-red-400',
                                        state === 'pending' || state === 'skipped' ? 'text-muted-foreground' : '',
                                    )}
                                >
                                    {label}
                                </span>
                            </div>

                            {/* Connector line */}
                            {!isLast && (
                                <div className="flex-1 mx-2 mb-5">
                                    <div className="h-0.5 w-full rounded-full overflow-hidden bg-border/20">
                                        <div
                                            className="h-full transition-all duration-700"
                                            style={{
                                                width: stepStates[idx] === 'completed' ? '100%' : '0%',
                                                backgroundColor: '#22C55E',
                                            }}
                                        />
                                    </div>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
