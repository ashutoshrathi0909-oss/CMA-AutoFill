'use client';

import { useDeleteFile } from '@/lib/hooks/use-files';
import { Trash2, FileSpreadsheet, FileText, Image as ImageIcon, File } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import type { UploadedFile } from '@/lib/api/types';

interface FileListProps {
    projectId: string;
    files: UploadedFile[];
    disabled?: boolean;
}

function formatBytes(bytes: number, decimals = 2) {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

function getFileIcon(filename: string, fileType: string) {
    const ext = filename.split('.').pop()?.toLowerCase() || '';
    if (ext === 'xlsx' || ext === 'xls' || fileType.includes('spreadsheet')) {
        return <FileSpreadsheet className="h-4 w-4 text-green-500" />;
    }
    if (ext === 'pdf' || fileType.includes('pdf')) {
        return <FileText className="h-4 w-4 text-red-400" />;
    }
    if (['jpg', 'jpeg', 'png', 'tiff'].includes(ext) || fileType.includes('image')) {
        return <ImageIcon className="h-4 w-4 text-blue-400" />;
    }
    return <File className="h-4 w-4 text-muted-foreground" />;
}

export function FileList({ projectId, files, disabled }: FileListProps) {
    const deleteMutation = useDeleteFile();

    if (!files || files.length === 0) {
        return null; // Don't show the table if no files are uploaded
    }

    const handleDelete = async (fileId: string) => {
        try {
            await deleteMutation.mutateAsync({ fileId, projectId });
            toast.success('File removed successfully');
        } catch {
            toast.error('Failed to remove file');
        }
    };

    return (
        <div className="rounded-xl border border-border/20 overflow-hidden" style={{ backgroundColor: 'var(--bg-card)' }}>
            <Table>
                <TableHeader>
                    <TableRow className="border-border/10 hover:bg-transparent">
                        <TableHead className="w-12 text-center">Type</TableHead>
                        <TableHead>Filename</TableHead>
                        <TableHead>Size</TableHead>
                        <TableHead className="w-24 text-right">Actions</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {files.map((file) => (
                        <TableRow key={file.id} className="border-border/10 hover:bg-white/5 transition-colors">
                            <TableCell className="text-center">
                                <div className="flex justify-center p-2 rounded-md bg-background/50 w-8 h-8 mx-auto items-center">
                                    {getFileIcon(file.filename, file.file_type)}
                                </div>
                            </TableCell>
                            <TableCell>
                                <p className="font-medium text-sm text-foreground truncate max-w-[300px] sm:max-w-md">
                                    {file.filename}
                                </p>
                            </TableCell>
                            <TableCell className="text-muted-foreground text-sm">
                                {formatBytes(file.file_size)}
                            </TableCell>
                            <TableCell className="text-right">
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => handleDelete(file.id)}
                                    disabled={disabled || deleteMutation.isPending}
                                    className="text-muted-foreground hover:text-red-400 hover:bg-red-400/10 h-8 w-8"
                                >
                                    <Trash2 className="h-4 w-4" />
                                </Button>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}
