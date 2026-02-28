import { ReviewQueue } from '@/components/review/review-queue';

// Using a searchParams prop for Next.js App Router Page components
export default function ReviewPage({
    searchParams,
}: {
    searchParams: { [key: string]: string | string[] | undefined };
}) {
    // If a project_id comes in from the URL (e.g., ?project_id=123), extract it
    const projectIdParam = searchParams.project_id;
    const projectId = Array.isArray(projectIdParam) ? projectIdParam[0] : projectIdParam;

    return (
        <div className="space-y-6 animate-fade-in w-full max-w-[1200px] mx-auto">
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-foreground">Ask Father Review</h1>
                <p className="text-muted-foreground mt-2">
                    {projectId
                        ? 'Reviewing pending AI classifications for the selected project.'
                        : 'Review all pending items across your CMA pipeline waiting for CA approval.'}
                </p>
            </div>

            {projectId ? (
                <ReviewQueue projectId={projectId} />
            ) : (
                <div className="p-10 border border-border/20 border-dashed rounded-xl flex items-center justify-center text-center bg-black/20 text-muted-foreground">
                    <p>No specific project selected. Please navigate from a project details page or implement global review logic here.</p>
                </div>
            )}
        </div>
    );
}
