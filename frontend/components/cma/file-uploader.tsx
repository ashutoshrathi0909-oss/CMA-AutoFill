'use client';

import { useState, useRef } from 'react';
import { useUploadFiles } from '@/lib/hooks/use-files';
import { UploadCloud, FileSpreadsheet, FileText, Image as ImageIcon, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface FileUploaderProps {
    projectId: string;
    disabled?: boolean;
}

const ACCEPTED_TYPES = {
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    'application/vnd.ms-excel': ['.xls'],
    'application/pdf': ['.pdf'],
    'image/png': ['.png'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/tiff': ['.tiff'],
};

const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25MB
const MAX_FILES = 10;

export function FileUploader({ projectId, disabled }: FileUploaderProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const uploadMutation = useUploadFiles();

    const handleDragEnter = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (!disabled) setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (!disabled && e.dataTransfer) {
            e.dataTransfer.dropEffect = 'copy';
        }
    };

    const processFiles = async (fileList: FileList | File[]) => {
        if (disabled) return;

        const files = Array.from(fileList);
        if (files.length === 0) return;

        if (files.length > MAX_FILES) {
            toast.error(`Maximum ${MAX_FILES} files allowed per project`);
            return;
        }

        const validFiles = files.filter(file => {
            if (file.size > MAX_FILE_SIZE) {
                toast.error(`File ${file.name} exceeds 25MB limit`);
                return false;
            }
            return true;
        });

        if (validFiles.length === 0) return;

        setIsUploading(true);
        try {
            await uploadMutation.mutateAsync({ projectId, files: validFiles });
            toast.success(`Successfully uploaded ${validFiles.length} file(s)`);
        } catch (error) {
            toast.error('Failed to upload files. Please try again.');
        } finally {
            setIsUploading(false);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        if (disabled) return;

        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            await processFiles(e.dataTransfer.files);
        }
    };

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            await processFiles(e.target.files);
        }
    };

    return (
        <div className="w-full">
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
                multiple
                accept={Object.values(ACCEPTED_TYPES).flat().join(',')}
                disabled={disabled || isUploading}
            />

            <div
                className={cn(
                    'relative w-full rounded-xl border-2 border-dashed transition-all duration-200 flex flex-col items-center justify-center p-10',
                    disabled ? 'opacity-50 cursor-not-allowed border-border/20 bg-[var(--bg-card)]'
                        : isDragging ? 'border-[var(--gold)] bg-[var(--gold)]/5 scale-[1.02]'
                            : 'border-border/40 hover:border-border/80 hover:bg-white/5 bg-[var(--bg-card)] cursor-pointer'
                )}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                onClick={() => !disabled && !isUploading && fileInputRef.current?.click()}
            >
                {isUploading ? (
                    <div className="flex flex-col items-center text-[var(--gold)]">
                        <Loader2 className="h-10 w-10 animate-spin mb-4" />
                        <h3 className="text-lg font-semibold">Uploading Files...</h3>
                        <p className="text-sm text-muted-foreground mt-2">Please wait while your files are securely uploaded.</p>
                    </div>
                ) : (
                    <div className="flex flex-col items-center text-center">
                        <div className={cn("p-4 rounded-full mb-4", isDragging ? 'bg-[var(--gold)]/20 text-[var(--gold)]' : 'bg-background/80 text-muted-foreground')}>
                            <UploadCloud className="h-8 w-8" />
                        </div>
                        <h3 className="text-lg font-semibold text-foreground">
                            Drag & drop files here
                        </h3>
                        <p className="text-sm text-muted-foreground mt-1 mb-6">
                            or click to browse from your computer
                        </p>

                        <div className="flex items-center gap-6 text-xs text-muted-foreground">
                            <div className="flex items-center gap-1.5 flex-col">
                                <FileSpreadsheet className="h-5 w-5 opacity-70" />
                                <span>Excel (.xlsx, .xls)</span>
                            </div>
                            <div className="flex items-center gap-1.5 flex-col">
                                <FileText className="h-5 w-5 opacity-70" />
                                <span>PDF (.pdf)</span>
                            </div>
                            <div className="flex items-center gap-1.5 flex-col">
                                <ImageIcon className="h-5 w-5 opacity-70" />
                                <span>Images (.jpg, .png)</span>
                            </div>
                        </div>

                        <div className="mt-6 text-[11px] text-muted-foreground/60 border-t border-border/10 pt-4 w-full max-w-xs">
                            Maximum 10 files per project. Up to 25MB each.
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
