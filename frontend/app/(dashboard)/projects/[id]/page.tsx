'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useProject } from '@/lib/hooks/use-projects';
import { usePipelineProgress, useStartProcessing, useRetryProcessing, useResumeProcessing } from '@/lib/hooks/use-pipeline';
import { useProjectFiles } from '@/lib/hooks/use-files';
import { useReviewQueue } from '@/lib/hooks/use-review';
import { PageSkeleton } from '@/components/ui/page-skeleton';
import { ErrorState } from '@/components/ui/error-state';
import { CmaHeader } from '@/components/cma/cma-header';
import { PipelineStepper } from '@/components/cma/pipeline-stepper';
import { CmaMetadata } from '@/components/cma/cma-metadata';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Play, Loader2, RotateCcw, Download, Eye, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

import { FileUploader } from '@/components/cma/file-uploader';
import { FileList } from '@/components/cma/file-list';
import { ProcessingProgress } from '@/components/cma/processing-progress';
import { ValidationResults } from '@/components/cma/validation-results';
import { DownloadSection } from '@/components/cma/download-section';
import { ReviewQueue } from '@/components/review/review-queue';

export default function ProjectDetailPage() {
    const params = useParams();
    const projectId = params.id as string;

    const [activeTab, setActiveTab] = useState('files');
    const [hasNavigated, setHasNavigated] = useState(false);

    // Data fetching
    const { data: project, isLoading, error, refetch } = useProject(projectId);
    const { data: progress } = usePipelineProgress(projectId);
    const { data: filesData } = useProjectFiles(projectId);
    const { data: reviewsData } = useReviewQueue({ project_id: projectId, status: 'pending' });

    // Mutations
    const startMutation = useStartProcessing();
    const retryMutation = useRetryProcessing();

    // Derived state
    const currentStatus = progress?.status || project?.status || 'draft';
    const pipelineSteps = progress?.steps || [];
    const files = filesData || [];
    const pendingReviewsCount = reviewsData?.total || 0;

    const isProcessing = ['extracting', 'classifying', 'validating', 'generating'].includes(currentStatus);

    // Auto-navigation logic based on status changes
    useEffect(() => {
        if (!hasNavigated && currentStatus !== 'draft') {
            // Initial load navigation
            if (isProcessing) setActiveTab('progress');
            else if (currentStatus === 'reviewing') setActiveTab('review');
            else if (currentStatus === 'completed' || currentStatus === 'error') setActiveTab('download');
            setHasNavigated(true);
        } else if (hasNavigated) {
            // Live status changes
            if (currentStatus === 'reviewing' && activeTab === 'progress') {
                setActiveTab('review');
                toast.warning(`Pipeline paused: ${pendingReviewsCount} items need review`);
            } else if (currentStatus === 'completed' && activeTab === 'progress') {
                setActiveTab('download');
                toast.success('CMA generation complete!');
            } else if (currentStatus === 'error' && activeTab === 'progress') {
                toast.error(progress?.error_message || 'Pipeline failed');
            }
        }
    }, [currentStatus, activeTab, isProcessing, pendingReviewsCount, progress?.error_message]); // Removed hasNavigated from dep array to avoid loops

    if (isLoading) return <PageSkeleton type="dashboard" />;
    if (error || !project) return <ErrorState message="Failed to load project details" onRetry={() => refetch()} />;

    const handleProcess = async () => {
        if (files.length === 0) {
            toast.error('Please upload standard CMA documents first');
            return;
        }
        try {
            await startMutation.mutateAsync(projectId);
            setActiveTab('progress');
            toast.success('Pipeline started');
        } catch {
            toast.error('Failed to start pipeline');
        }
    };

    const handleRetry = async () => {
        try {
            await retryMutation.mutateAsync(projectId);
            setActiveTab('progress');
            toast.success('Pipeline retrying');
        } catch {
            toast.error('Failed to retry pipeline');
        }
    };

    return (
        <div className="space-y-6 pb-10">
            {/* Header section */}
            <CmaHeader project={{ ...project, status: currentStatus as any }} />

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                {/* Main workspace */}
                <div className="xl:col-span-2 space-y-6">
                    <PipelineStepper steps={pipelineSteps} overallStatus={currentStatus} />

                    {/* Action Bar */}
                    <div className="flex items-center justify-between bg-[var(--bg-card)] border border-border/20 rounded-xl p-4">
                        <div className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                            {currentStatus === 'draft' && 'Upload files to begin'}
                            {isProcessing && (
                                <>
                                    <Loader2 className="h-4 w-4 animate-spin text-[var(--gold)]" />
                                    <span className="text-[var(--gold)]">AI is processing documents...</span>
                                </>
                            )}
                            {currentStatus === 'reviewing' && (
                                <>
                                    <AlertCircle className="h-4 w-4 text-amber-500" />
                                    <span className="text-amber-500">CA review required</span>
                                </>
                            )}
                            {currentStatus === 'completed' && 'CMA is ready for download'}
                            {currentStatus === 'error' && <span className="text-red-500">Pipeline encountered an error</span>}
                        </div>

                        <div>
                            {currentStatus === 'draft' && (
                                <Button
                                    onClick={handleProcess}
                                    disabled={files.length === 0 || startMutation.isPending}
                                    className="bg-gold hover:bg-gold-hover text-primary-foreground font-semibold"
                                >
                                    {startMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Play className="h-4 w-4 mr-2" />}
                                    Process CMA
                                </Button>
                            )}
                            {isProcessing && (
                                <Button disabled variant="outline" className="border-[var(--gold)]/50 text-[var(--gold)]">
                                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                    Processing...
                                </Button>
                            )}
                            {currentStatus === 'reviewing' && (
                                <Button onClick={() => setActiveTab('review')} className="bg-amber-600 hover:bg-amber-700 text-white">
                                    <Eye className="h-4 w-4 mr-2" />
                                    Review Items ({pendingReviewsCount})
                                </Button>
                            )}
                            {currentStatus === 'completed' && (
                                <Button onClick={() => setActiveTab('download')} className="bg-green-600 hover:bg-green-700 text-white">
                                    <Download className="h-4 w-4 mr-2" />
                                    View Downloads
                                </Button>
                            )}
                            {currentStatus === 'error' && (
                                <Button onClick={handleRetry} disabled={retryMutation.isPending} variant="destructive">
                                    {retryMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <RotateCcw className="h-4 w-4 mr-2" />}
                                    Retry
                                </Button>
                            )}
                        </div>
                    </div>

                    {/* Tabbed Interface */}
                    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                        <TabsList className="grid grid-cols-4 w-full bg-[var(--bg-card)] border border-border/20 p-1">
                            <TabsTrigger value="files" className="data-[state=active]:bg-background data-[state=active]:text-foreground">
                                Files ({files.length})
                            </TabsTrigger>
                            <TabsTrigger value="progress" className="data-[state=active]:bg-background data-[state=active]:text-foreground">
                                Progress
                            </TabsTrigger>
                            <TabsTrigger value="review" className="data-[state=active]:bg-background data-[state=active]:text-foreground relative">
                                Review
                                {pendingReviewsCount > 0 && currentStatus === 'reviewing' && (
                                    <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-amber-500 animate-pulse" />
                                )}
                            </TabsTrigger>
                            <TabsTrigger value="download" className="data-[state=active]:bg-background data-[state=active]:text-foreground">
                                Download
                            </TabsTrigger>
                        </TabsList>

                        <div className="mt-6">
                            <TabsContent value="files" className="m-0 focus-visible:outline-none focus-visible:ring-0">
                                <div className="space-y-6">
                                    <FileUploader projectId={projectId} disabled={currentStatus !== 'draft' && currentStatus !== 'error'} />
                                    <FileList projectId={projectId} files={files} disabled={currentStatus !== 'draft' && currentStatus !== 'error'} />
                                </div>
                            </TabsContent>

                            <TabsContent value="progress" className="m-0 focus-visible:outline-none focus-visible:ring-0">
                                <ProcessingProgress projectId={projectId} />
                            </TabsContent>

                            <TabsContent value="review" className="m-0 focus-visible:outline-none focus-visible:ring-0">
                                <ReviewQueue projectId={projectId} />
                            </TabsContent>

                            <TabsContent value="download" className="m-0 focus-visible:outline-none focus-visible:ring-0">
                                <div className="space-y-6">
                                    {currentStatus === 'completed' && <ValidationResults projectId={projectId} />}
                                    <DownloadSection projectId={projectId} />
                                </div>
                            </TabsContent>
                        </div>
                    </Tabs>
                </div>

                {/* Sidebar */}
                <div className="xl:col-span-1 space-y-6">
                    <CmaMetadata project={project} fileCount={files.length} reviewCount={pendingReviewsCount} />
                </div>
            </div>
        </div>
    );
}
