import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCcw, WifiOff, ShieldX } from 'lucide-react';
import Link from 'next/link';

interface ErrorStateProps {
    message?: string;
    type?: 'error' | 'not-found' | 'network' | 'unauthorized';
    onRetry?: () => void;
    className?: string;
}

const errorConfig = {
    error: {
        icon: AlertTriangle,
        title: 'Something went wrong',
        defaultMessage: 'An error occurred while loading this page. Please try again.',
        iconColor: 'text-destructive',
        bgColor: 'bg-destructive/10',
    },
    'not-found': {
        icon: ShieldX,
        title: 'Page not found',
        defaultMessage: "The page you're looking for doesn't exist or has been moved.",
        iconColor: 'text-muted-foreground',
        bgColor: 'bg-muted/50',
    },
    network: {
        icon: WifiOff,
        title: "Can't connect to server",
        defaultMessage: 'Please check your internet connection and try again.',
        iconColor: 'text-warning',
        bgColor: 'bg-warning/10',
    },
    unauthorized: {
        icon: ShieldX,
        title: 'Access denied',
        defaultMessage: 'You do not have permission to view this page.',
        iconColor: 'text-destructive',
        bgColor: 'bg-destructive/10',
    },
};

export function ErrorState({ message, type = 'error', onRetry, className }: ErrorStateProps) {
    const config = errorConfig[type];
    const Icon = config.icon;

    return (
        <div
            className={cn(
                'flex flex-col items-center justify-center py-16 px-6 text-center rounded-xl border border-border/20',
                className
            )}
            style={{ backgroundColor: 'var(--bg-card)' }}
        >
            <div className={cn('rounded-2xl p-4 mb-4', config.bgColor)}>
                <Icon className={cn('h-8 w-8', config.iconColor)} />
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">{config.title}</h3>
            <p className="text-sm text-muted-foreground max-w-sm mb-6">
                {message || config.defaultMessage}
            </p>
            <div className="flex items-center gap-3">
                {onRetry && (
                    <Button
                        onClick={onRetry}
                        variant="outline"
                        className="border-border/30 hover:border-gold/30"
                    >
                        <RefreshCcw className="mr-2 h-4 w-4" />
                        Try again
                    </Button>
                )}
                {type === 'not-found' && (
                    <Link href="/dashboard">
                        <Button className="bg-gold hover:bg-gold-hover text-primary-foreground">
                            Go to Dashboard
                        </Button>
                    </Link>
                )}
            </div>
        </div>
    );
}
