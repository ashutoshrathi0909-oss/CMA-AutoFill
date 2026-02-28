'use client';

import { Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Breadcrumb } from './breadcrumb';
import { Separator } from '@/components/ui/separator';

export function Header() {
    return (
        <header className="h-16 border-b border-border/10 flex items-center justify-between px-6 shrink-0" style={{ backgroundColor: 'var(--bg-sidebar)' }}>
            <div className="flex items-center gap-4">
                {/* Spacer for mobile hamburger */}
                <div className="w-8 lg:hidden" />
                <Breadcrumb />
            </div>
            <div className="flex items-center gap-3">
                <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground relative">
                    <Bell className="h-5 w-5" />
                    {/* Notification dot — placeholder for future */}
                    {/* <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-gold" /> */}
                </Button>
                <Separator orientation="vertical" className="h-6 bg-border/20" />
                <span className="text-xs text-muted-foreground hidden md:block">CMA AutoFill</span>
            </div>
        </header>
    );
}
