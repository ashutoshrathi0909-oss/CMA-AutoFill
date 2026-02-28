'use client';

import * as React from 'react';
import { Check, ChevronsUpDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
} from '@/components/ui/command';
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from '@/components/ui/popover';
import { CMA_CATEGORIES } from '@/lib/api/types';

interface CategorySelectorProps {
    value: string;
    onChange: (value: string, displayLabel?: string) => void;
    suggestedCategory?: string;
    disabled?: boolean;
}

export function CategorySelector({ value, onChange, suggestedCategory, disabled }: CategorySelectorProps) {
    const [open, setOpen] = React.useState(false);

    // Group categories for rendering
    const groupedCategories = CMA_CATEGORIES.reduce((acc, cat) => {
        if (!acc[cat.group]) acc[cat.group] = [];
        acc[cat.group].push(cat);
        return acc;
    }, {} as Record<string, typeof CMA_CATEGORIES[number][]>);

    // Find current display label
    const selectedItem = CMA_CATEGORIES.find(cat => cat.label === value || `Row ${cat.row} - ${cat.label}` === value);
    const displayValue = selectedItem ? `Row ${selectedItem.row} - ${selectedItem.label}` : value;

    return (
        <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
                <Button
                    variant="outline"
                    role="combobox"
                    aria-expanded={open}
                    disabled={disabled}
                    className="w-full justify-between bg-black/20 border-border/30 hover:bg-black/40 hover:text-foreground text-left font-normal"
                >
                    <span className="truncate">
                        {value ? displayValue : 'Select CMA Category...'}
                    </span>
                    <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                </Button>
            </PopoverTrigger>
            <PopoverContent className="w-[400px] p-0 shadow-xl border-border/20" style={{ backgroundColor: 'var(--bg-card)' }}>
                <Command className="bg-transparent">
                    <CommandInput placeholder="Search categories or rows..." className="border-none focus:ring-0" />
                    <CommandList className="max-h-[300px] overflow-y-auto custom-scrollbar">
                        <CommandEmpty>No category found.</CommandEmpty>

                        {Object.entries(groupedCategories).map(([group, items]) => (
                            <CommandGroup key={group} heading={group} className="text-muted-foreground">
                                {items.map((cat) => {
                                    const itemLabel = `Row ${cat.row} - ${cat.label}`;
                                    const isSuggested = suggestedCategory === cat.label || suggestedCategory === itemLabel;
                                    const isSelected = value === cat.label || value === itemLabel;

                                    return (
                                        <CommandItem
                                            key={cat.row}
                                            value={itemLabel}
                                            className={cn(
                                                "cursor-pointer my-0.5 rounded-md",
                                                isSuggested && "bg-[var(--gold)]/10 text-[var(--gold)] aria-selected:bg-[var(--gold)]/20 aria-selected:text-[var(--gold)]",
                                                isSelected && !isSuggested && "bg-white/10 text-foreground"
                                            )}
                                            onSelect={() => {
                                                onChange(cat.label, itemLabel);
                                                setOpen(false);
                                            }}
                                        >
                                            <Check
                                                className={cn(
                                                    "mr-2 h-4 w-4",
                                                    isSelected ? "opacity-100" : "opacity-0"
                                                )}
                                            />
                                            <span className="flex-1 truncate">{cat.label}</span>
                                            <span className={cn(
                                                "ml-2 text-xs font-mono tabular-nums px-1.5 py-0.5 rounded",
                                                isSuggested ? "bg-[var(--gold)]/20" : "bg-black/20 text-muted-foreground"
                                            )}>
                                                Row {cat.row}
                                            </span>
                                        </CommandItem>
                                    );
                                })}
                            </CommandGroup>
                        ))}
                    </CommandList>
                </Command>
            </PopoverContent>
        </Popover>
    );
}
