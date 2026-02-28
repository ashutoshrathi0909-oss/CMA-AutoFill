'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    Users,
    FileSpreadsheet,
    ClipboardCheck,
    BookOpen,
    BarChart3,
    Settings,
    ChevronLeft,
    ChevronRight,
    Menu,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { BadgeCount } from '@/components/ui/badge-count';
import { UserMenu } from './user-menu';

interface NavItem {
    label: string;
    href: string;
    icon: React.ElementType;
    badge?: number;
}

const navItems: NavItem[] = [
    { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { label: 'Clients', href: '/clients', icon: Users },
    { label: 'CMA Projects', href: '/projects', icon: FileSpreadsheet },
    { label: 'Review Queue', href: '/review', icon: ClipboardCheck },
    { label: 'Precedents', href: '/precedents', icon: BookOpen },
    { label: 'Analytics', href: '/analytics', icon: BarChart3 },
];

const bottomNavItems: NavItem[] = [
    { label: 'Settings', href: '/settings', icon: Settings },
];

function SidebarContent({
    collapsed,
    onToggle,
    pendingReviewCount,
}: {
    collapsed: boolean;
    onToggle: () => void;
    pendingReviewCount: number;
}) {
    const pathname = usePathname();

    return (
        <div className="flex h-full flex-col" style={{ backgroundColor: 'var(--bg-sidebar)' }}>
            {/* Logo */}
            <div className="flex h-16 items-center justify-between px-4 border-b border-border/10">
                {!collapsed && (
                    <Link href="/dashboard" className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-lg bg-gold flex items-center justify-center">
                            <span className="text-sm font-bold text-primary-foreground">C</span>
                        </div>
                        <span className="text-lg font-semibold text-gold">CMA AutoFill</span>
                    </Link>
                )}
                {collapsed && (
                    <Link href="/dashboard" className="mx-auto">
                        <div className="h-8 w-8 rounded-lg bg-gold flex items-center justify-center">
                            <span className="text-sm font-bold text-primary-foreground">C</span>
                        </div>
                    </Link>
                )}
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={onToggle}
                    className="hidden lg:flex text-muted-foreground hover:text-foreground h-8 w-8"
                >
                    {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
                </Button>
            </div>

            {/* Main Navigation */}
            <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
                {navItems.map((item) => {
                    const isActive =
                        pathname === item.href || pathname.startsWith(`${item.href}/`);

                    const linkContent = (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
                                isActive
                                    ? 'bg-gold/15 text-gold border border-gold/20'
                                    : 'text-muted-foreground hover:bg-accent hover:text-foreground',
                                collapsed && 'justify-center px-2'
                            )}
                        >
                            <item.icon className={cn('h-5 w-5 shrink-0', isActive && 'text-gold')} />
                            {!collapsed && (
                                <>
                                    <span className="flex-1">{item.label}</span>
                                    {item.label === 'Review Queue' && pendingReviewCount > 0 && (
                                        <BadgeCount count={pendingReviewCount} />
                                    )}
                                </>
                            )}
                        </Link>
                    );

                    if (collapsed) {
                        return (
                            <Tooltip key={item.href} delayDuration={0}>
                                <TooltipTrigger asChild>{linkContent}</TooltipTrigger>
                                <TooltipContent side="right" className="flex items-center gap-2">
                                    {item.label}
                                    {item.label === 'Review Queue' && pendingReviewCount > 0 && (
                                        <BadgeCount count={pendingReviewCount} />
                                    )}
                                </TooltipContent>
                            </Tooltip>
                        );
                    }

                    return linkContent;
                })}
            </nav>

            {/* Bottom Navigation */}
            <div className="px-3 py-2 border-t border-border/10">
                {bottomNavItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
                                isActive
                                    ? 'bg-gold/15 text-gold'
                                    : 'text-muted-foreground hover:bg-accent hover:text-foreground',
                                collapsed && 'justify-center px-2'
                            )}
                        >
                            <item.icon className="h-5 w-5 shrink-0" />
                            {!collapsed && <span>{item.label}</span>}
                        </Link>
                    );
                })}
            </div>

            {/* User Menu */}
            <div className="p-3 border-t border-border/10">
                <UserMenu collapsed={collapsed} />
            </div>
        </div>
    );
}

export function Sidebar() {
    const [collapsed, setCollapsed] = useState(false);
    const [mobileOpen, setMobileOpen] = useState(false);
    const pendingReviewCount = 0; // Will be wired to API later

    // Restore collapsed state from localStorage
    useEffect(() => {
        const saved = localStorage.getItem('sidebar-collapsed');
        if (saved !== null) {
            setCollapsed(JSON.parse(saved));
        }
    }, []);

    const toggleCollapsed = () => {
        const next = !collapsed;
        setCollapsed(next);
        localStorage.setItem('sidebar-collapsed', JSON.stringify(next));
    };

    return (
        <>
            {/* Mobile hamburger trigger */}
            <Button
                variant="ghost"
                size="icon"
                className="fixed top-4 left-4 z-50 lg:hidden text-foreground"
                onClick={() => setMobileOpen(true)}
            >
                <Menu className="h-5 w-5" />
            </Button>

            {/* Mobile drawer */}
            <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
                <SheetTrigger asChild>
                    <span className="sr-only">Open menu</span>
                </SheetTrigger>
                <SheetContent side="left" className="p-0 w-72 border-r-0" style={{ backgroundColor: 'var(--bg-sidebar)' }}>
                    <SidebarContent
                        collapsed={false}
                        onToggle={() => setMobileOpen(false)}
                        pendingReviewCount={pendingReviewCount}
                    />
                </SheetContent>
            </Sheet>

            {/* Desktop sidebar */}
            <aside
                className={cn(
                    'hidden lg:flex flex-col border-r border-border/10 transition-all duration-300 ease-in-out shrink-0',
                    collapsed ? 'w-[68px]' : 'w-64'
                )}
                style={{ backgroundColor: 'var(--bg-sidebar)' }}
            >
                <SidebarContent
                    collapsed={collapsed}
                    onToggle={toggleCollapsed}
                    pendingReviewCount={pendingReviewCount}
                />
            </aside>
        </>
    );
}
