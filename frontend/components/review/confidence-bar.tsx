'use client';

import { Check, Info } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip';

interface ConfidenceBarProps {
    confidence: number;
    className?: string;
}

export function ConfidenceBar({ confidence, className }: ConfidenceBarProps) {
    // Backend sends confidence as 0.0 to 1.0, convert to percentage
    const percentage = Math.round(confidence * 100);

    // Determine level and color
    let level = 'LOW';
    let colorClass = 'bg-red-500';
    let textClass = 'text-red-500';
    let tooltipText = 'AI is uncertain. Please review carefully.';

    if (percentage >= 90) {
        level = 'HIGH';
        colorClass = 'bg-green-500';
        textClass = 'text-green-500';
        tooltipText = 'AI is very confident in this classification.';
    } else if (percentage >= 70) {
        level = 'MEDIUM';
        colorClass = 'bg-amber-500';
        textClass = 'text-amber-500';
        tooltipText = 'AI is moderately confident. Review is recommended.';
    }

    return (
        <div className={cn("flex items-center gap-3", className)}>
            <div className="w-32 sm:w-48 h-2.5 rounded-full bg-background/50 overflow-hidden outline outline-1 outline-border/20">
                <div
                    className={cn("h-full rounded-full transition-all duration-1000 ease-out", colorClass)}
                    style={{ width: `${percentage}%` }}
                />
            </div>

            <div className="flex items-center gap-1.5 min-w-[90px]">
                <span className={cn("text-sm font-bold tabular-nums", textClass)}>
                    {percentage}%
                </span>

                <TooltipProvider delayDuration={300}>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className={cn(
                                "flex items-center justify-center px-1.5 py-0.5 rounded text-[10px] font-bold cursor-help",
                                percentage >= 90 ? "bg-green-500/10 text-green-500 border border-green-500/20" :
                                    percentage >= 70 ? "bg-amber-500/10 text-amber-500 border border-amber-500/20" :
                                        "bg-red-500/10 text-red-500 border border-red-500/20"
                            )}>
                                {level}
                            </div>
                        </TooltipTrigger>
                        <TooltipContent side="top" className="text-xs max-w-xs" style={{ backgroundColor: 'var(--bg-card)' }}>
                            <div className="flex items-start gap-2">
                                <Info className="h-4 w-4 mt-0.5 text-muted-foreground" />
                                <p>{tooltipText}</p>
                            </div>
                        </TooltipContent>
                    </Tooltip>
                </TooltipProvider>
            </div>
        </div>
    );
}

export function SourceBadge({ source }: { source: 'ai' | 'rule' | 'precedent' }) {
    if (source === 'precedent') {
        return (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/20">
                <Check className="h-3 w-3" />
                Precedent
            </span>
        );
    }

    if (source === 'rule') {
        return (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
                Rule Engine
            </span>
        );
    }

    return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20">
            AI Extract
        </span>
    );
}
