import { cn } from '@/lib/utils';
import type { LucideIcon } from 'lucide-react';
import Link from 'next/link';

interface StatCardProps {
    title: string;
    value: string | number;
    icon: LucideIcon;
    href?: string;
    trend?: {
        value: number;
        label: string;
    };
    className?: string;
}

export function StatCard({ title, value, icon: Icon, href, trend, className }: StatCardProps) {
    const content = (
        <div
            className={cn(
                'rounded-xl border border-border/20 p-6 card-hover-glow transition-all duration-200',
                className
            )}
            style={{ backgroundColor: 'var(--bg-card)' }}
        >
            <div className="flex items-start justify-between">
                <div className="space-y-2">
                    <p className="text-sm font-medium text-muted-foreground">{title}</p>
                    <p className="text-3xl font-bold text-foreground tracking-tight">{value}</p>
                    {trend && (
                        <p
                            className={cn(
                                'text-xs font-medium',
                                trend.value >= 0 ? 'text-success' : 'text-destructive'
                            )}
                        >
                            {trend.value >= 0 ? '↑' : '↓'} {Math.abs(trend.value)}% {trend.label}
                        </p>
                    )}
                </div>
                <div className="rounded-lg p-2.5 bg-gold/10">
                    <Icon className="h-5 w-5 text-gold" />
                </div>
            </div>
        </div>
    );

    if (href) {
        return (
            <Link href={href} className="block">
                {content}
            </Link>
        );
    }

    return content;
}
