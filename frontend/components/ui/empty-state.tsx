import { cn } from '@/lib/utils';
import type { LucideIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

interface EmptyStateProps {
    icon?: LucideIcon;
    title: string;
    description: string;
    actionLabel?: string;
    actionHref?: string;
    onAction?: () => void;
    className?: string;
}

export function EmptyState({
    icon: Icon,
    title,
    description,
    actionLabel,
    actionHref,
    onAction,
    className,
}: EmptyStateProps) {
    return (
        <div
            className={cn(
                'flex flex-col items-center justify-center py-16 px-6 text-center rounded-xl border border-border/20',
                className
            )}
            style={{ backgroundColor: 'var(--bg-card)' }}
        >
            {Icon && (
                <div className="rounded-2xl bg-gold/10 p-4 mb-4">
                    <Icon className="h-8 w-8 text-gold/60" />
                </div>
            )}
            <h3 className="text-lg font-semibold text-foreground mb-2">{title}</h3>
            <p className="text-sm text-muted-foreground max-w-sm mb-6">{description}</p>
            {actionLabel && (
                actionHref ? (
                    <Link href={actionHref}>
                        <Button className="bg-gold hover:bg-gold-hover text-primary-foreground font-semibold">
                            {actionLabel}
                        </Button>
                    </Link>
                ) : (
                    <Button
                        onClick={onAction}
                        className="bg-gold hover:bg-gold-hover text-primary-foreground font-semibold"
                    >
                        {actionLabel}
                    </Button>
                )
            )}
        </div>
    );
}
