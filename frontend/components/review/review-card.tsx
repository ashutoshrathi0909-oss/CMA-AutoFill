'use client';

import { useState } from 'react';
import { useResolveReview } from '@/lib/hooks/use-review';
import { ConfidenceBar, SourceBadge } from './confidence-bar';
import { CategorySelector } from './category-selector';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Loader2, CheckCircle2, ChevronRight, FileText } from 'lucide-react';
import { toast } from 'sonner';
import type { ReviewItem } from '@/lib/api/types';

interface ReviewCardProps {
    item: ReviewItem;
    isSelected: boolean;
    onSelect: (checked: boolean) => void;
}

export function ReviewCard({ item, isSelected, onSelect }: ReviewCardProps) {
    const resolveMutation = useResolveReview();
    const [selectedCategory, setSelectedCategory] = useState(item.suggested_category);
    const [reasoning, setReasoning] = useState('');
    const [savePrecedent, setSavePrecedent] = useState(true);

    const isHighConfidence = item.confidence >= 0.9;
    const isAiSuggestionSelected = selectedCategory === item.suggested_category || selectedCategory.includes(item.suggested_category);

    const handleResolve = async (categoryToUse = selectedCategory) => {
        try {
            // Strip row prefix if present
            const cleanCategory = categoryToUse.includes(' - ') ? categoryToUse.split(' - ')[1] : categoryToUse;

            await resolveMutation.mutateAsync({
                id: item.id,
                data: {
                    resolved_category: cleanCategory,
                    resolved_subcategory: reasoning, // Using subcategory field for reasoning for now
                    // Backend handles saving precedent automatically in Phase 07 logic
                }
            });
            toast.success('Classification resolved');
        } catch {
            toast.error('Failed to resolve item');
        }
    };

    if (item.status !== 'pending') return null;

    return (
        <div
            className="rounded-xl border border-border/20 p-5 sm:p-6 transition-colors"
            style={{
                backgroundColor: 'var(--bg-card)',
                borderColor: isSelected ? 'var(--gold)' : undefined
            }}
        >
            <div className="flex items-start gap-4">
                <Checkbox
                    checked={isSelected}
                    onCheckedChange={(checked: boolean | 'indeterminate') => onSelect(checked === true)}
                    className="mt-1 border-border/50 data-[state=checked]:bg-[var(--gold)] data-[state=checked]:border-[var(--gold)]"
                />

                <div className="flex-1 min-w-0">
                    {/* Header Row */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                        <div>
                            <h3 className="text-xl font-bold text-foreground leading-tight">{item.source_item_name}</h3>
                            <div className="flex items-center gap-2 mt-1.5 text-xs text-muted-foreground">
                                <FileText className="h-3 w-3" />
                                <span>Source: CMA Extraction</span>
                            </div>
                        </div>
                    </div>

                    <div className="h-px w-full bg-border/20 my-4" />

                    {/* AI Suggestion Area */}
                    <div className="flex flex-col sm:flex-row gap-6 sm:items-center justify-between mb-6">
                        <div className="space-y-3">
                            <div>
                                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1 block">AI Suggestion</span>
                                <div className="flex items-center gap-2">
                                    <span className="text-[var(--gold)] font-medium text-base">
                                        {item.suggested_category}
                                    </span>
                                    {item.suggested_subcategory && (
                                        <span className="text-muted-foreground text-sm flex items-center gap-1">
                                            <ChevronRight className="h-3 w-3" />
                                            {item.suggested_subcategory}
                                        </span>
                                    )}
                                </div>
                            </div>

                            <div className="flex items-center gap-4">
                                <ConfidenceBar confidence={item.confidence} />
                                <SourceBadge source={item.classification_source} />
                            </div>
                        </div>

                        {/* Fast Tracking for High Confidence */}
                        {isHighConfidence && (
                            <div className="sm:self-end">
                                <Button
                                    onClick={() => handleResolve(item.suggested_category)}
                                    disabled={resolveMutation.isPending}
                                    className="bg-green-600 hover:bg-green-700 text-white w-full sm:w-auto h-11 px-6 shadow-lg shadow-green-900/20"
                                >
                                    {resolveMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <CheckCircle2 className="h-4 w-4 mr-2" />}
                                    Accept AI Forecast ✓
                                </Button>
                            </div>
                        )}
                    </div>

                    {/* Manual Decision Area */}
                    <div className="rounded-lg bg-black/20 border border-border/10 p-4">
                        <h4 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
                            <span>Your Decision</span>
                            {!isHighConfidence && <span className="text-[10px] uppercase bg-amber-500/10 text-amber-500 px-1.5 py-0.5 rounded border border-amber-500/20 font-bold">Review Required</span>}
                        </h4>

                        <div className="grid grid-cols-1 sm:grid-cols-12 gap-4">
                            <div className="sm:col-span-5 relative z-10">
                                <label className="text-xs text-muted-foreground block mb-1.5">CMA Category</label>
                                <CategorySelector
                                    value={selectedCategory}
                                    onChange={(val) => setSelectedCategory(val)}
                                    suggestedCategory={item.suggested_category}
                                    disabled={resolveMutation.isPending}
                                />
                            </div>

                            <div className="sm:col-span-5">
                                <label className="text-xs text-muted-foreground block mb-1.5">Reasoning (Optional)</label>
                                <Input
                                    value={reasoning}
                                    onChange={(e) => setReasoning(e.target.value)}
                                    placeholder="Why this category?"
                                    disabled={resolveMutation.isPending}
                                    className="bg-black/20 border-border/30 h-10"
                                />
                            </div>

                            <div className="sm:col-span-2 flex items-end">
                                <Button
                                    onClick={() => handleResolve()}
                                    disabled={resolveMutation.isPending || !selectedCategory}
                                    className="w-full h-10 bg-white/10 hover:bg-white/20 text-foreground border border-border/40"
                                >
                                    {resolveMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> :
                                        isAiSuggestionSelected ? 'Accept ▶' : 'Override ▶'}
                                </Button>
                            </div>
                        </div>

                        <div className="flex items-center gap-2 mt-4 ml-1">
                            <Checkbox
                                id={`precedent-${item.id}`}
                                checked={savePrecedent}
                                onCheckedChange={(checked: boolean | 'indeterminate') => setSavePrecedent(checked === true)}
                                disabled={resolveMutation.isPending}
                                className="border-border/50 data-[state=checked]:bg-[var(--gold)] data-[state=checked]:border-[var(--gold)]"
                            />
                            <label
                                htmlFor={`precedent-${item.id}`}
                                className="text-xs text-muted-foreground font-medium cursor-pointer"
                            >
                                Save rule for future "{item.source_item_name}" classifications across firm
                            </label>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
