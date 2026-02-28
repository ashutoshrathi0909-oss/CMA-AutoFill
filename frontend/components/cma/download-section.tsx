'use client';

import { useState } from 'react';
import { useGeneratedFiles } from '@/lib/hooks/use-files';
import { useStartProcessing } from '@/lib/hooks/use-pipeline';
import { downloadCMA } from '@/lib/api/files';
import { Button } from '@/components/ui/button';
import { Download, FileSpreadsheet, RotateCcw, Loader2, PartyPopper } from 'lucide-react';
import { toast } from 'sonner';

interface DownloadSectionProps {
    projectId: string;
}

function formatBytes(bytes: number, decimals = 2) {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

export function DownloadSection({ projectId }: DownloadSectionProps) {
    const { data: files, isLoading } = useGeneratedFiles(projectId);
    const startMutation = useStartProcessing();
    const [isDownloading, setIsDownloading] = useState(false);

    if (isLoading) {
        return (
            <div className="p-10 border border-border/20 rounded-xl flex items-center justify-center bg-[var(--bg-card)]">
                <Loader2 className="h-6 w-6 animate-spin text-[var(--gold)]" />
            </div>
        );
    }

    const latestFile = files && files.length > 0 ? files[0] : null;
    const previousVersions = files && files.length > 1 ? files.slice(1) : [];

    const handleDownload = async () => {
        setIsDownloading(true);
        try {
            const blob = await downloadCMA(projectId);

            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = latestFile?.filename || 'CMA_Report.xlsx';
            document.body.appendChild(a);
            a.click();

            // Cleanup
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            toast.success('Download started');
        } catch {
            toast.error('Failed to download file');
        } finally {
            setIsDownloading(false);
        }
    };

    const handleRegenerate = async () => {
        try {
            await startMutation.mutateAsync(projectId);
            toast.success('Regeneration triggered');
        } catch {
            toast.error('Failed to trigger regeneration');
        }
    };

    if (!latestFile) {
        return (
            <div className="p-10 border border-border/20 border-dashed rounded-xl flex flex-col items-center justify-center text-center bg-[var(--bg-card)] text-muted-foreground">
                <FileSpreadsheet className="h-10 w-10 mb-4 opacity-50" />
                <p>No generated files found.</p>
                <p className="text-xs mt-1">Files will appear here once the pipeline finishes processing.</p>
            </div>
        );
    }

    const generatedDate = new Date(latestFile.created_at).toLocaleString('en-IN', {
        day: 'numeric', month: 'short', year: 'numeric',
        hour: 'numeric', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata'
    });

    return (
        <div className="rounded-xl border border-[var(--gold)]/30 overflow-hidden" style={{ backgroundColor: 'var(--bg-card)' }}>
            <div className="p-4 sm:p-6 bg-gradient-to-r from-[var(--gold)]/10 to-transparent border-b border-border/10 flex items-center gap-3">
                <PartyPopper className="h-5 w-5 text-[var(--gold)]" />
                <h3 className="font-semibold text-foreground text-lg">CMA Ready for Download</h3>
            </div>

            <div className="p-4 sm:p-6 space-y-6">
                {/* Main Download Card */}
                <div className="rounded-lg border border-[var(--gold)]/20 bg-black/20 p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                    <div className="flex items-start gap-4 flex-1">
                        <div className="bg-green-500/10 p-3 rounded-lg text-green-500 border border-green-500/20 shrink-0">
                            <FileSpreadsheet className="h-8 w-8" />
                        </div>
                        <div>
                            <p className="font-semibold text-foreground text-base truncate pr-4">{latestFile.filename}</p>
                            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1 text-sm text-muted-foreground">
                                <span>Generated: {generatedDate}</span>
                                <span>Size: {formatBytes((latestFile as any).file_size || 250000)}</span>
                            </div>
                        </div>
                    </div>

                    <div className="flex flex-col sm:flex-row items-center gap-3 shrink-0">
                        <Button
                            variant="outline"
                            onClick={handleRegenerate}
                            disabled={startMutation.isPending}
                            className="w-full sm:w-auto border-border/30 hover:bg-white/5"
                        >
                            {startMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <RotateCcw className="h-4 w-4 mr-2 text-muted-foreground" />}
                            Regenerate
                        </Button>
                        <Button
                            onClick={handleDownload}
                            disabled={isDownloading}
                            className="w-full sm:w-auto bg-green-600 hover:bg-green-700 text-white shadow-lg shadow-green-900/20"
                        >
                            {isDownloading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Download className="h-4 w-4 mr-2" />}
                            Download Excel
                        </Button>
                    </div>
                </div>

                {/* Version History */}
                {previousVersions.length > 0 && (
                    <div className="mt-8">
                        <h4 className="text-xs font-semibold uppercase text-muted-foreground tracking-wider mb-4 border-b border-border/10 pb-2">
                            Version History
                        </h4>
                        <div className="space-y-3">
                            <div className="flex items-center text-sm">
                                <span className="w-16 text-foreground font-medium">v{previousVersions.length + 1}</span>
                                <span className="text-muted-foreground">Current Version ({generatedDate})</span>
                            </div>
                            {previousVersions.map((v, i) => (
                                <div key={v.id} className="flex items-center text-sm">
                                    <span className="w-16 text-muted-foreground">v{previousVersions.length - i}</span>
                                    <span className="text-muted-foreground/70">
                                        {new Date(v.created_at).toLocaleString('en-IN', {
                                            day: 'numeric', month: 'short', year: 'numeric',
                                            hour: 'numeric', minute: '2-digit', hour12: true
                                        })}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
