import { cn } from '@/lib/utils';

interface BadgeCountProps {
    count: number;
    className?: string;
}

export function BadgeCount({ count, className }: BadgeCountProps) {
    if (count <= 0) return null;

    const displayCount = count > 99 ? '99+' : String(count);

    return (
        <span
            className={cn(
                'inline-flex items-center justify-center rounded-full bg-gold px-1.5 py-0.5 text-[10px] font-bold leading-none text-primary-foreground min-w-[18px]',
                className
            )}
        >
            {displayCount}
        </span>
    );
}
