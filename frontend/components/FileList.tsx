'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { fileAPI } from '../lib/api';
import { toast } from 'sonner';
import { FileText, Globe, Trash2, Eye, CheckCircle, Clock, AlertCircle, Loader2 } from 'lucide-react';
import { formatFileSize, formatDate } from '../lib/export';

interface FileListProps {
  refreshTrigger?: number;
}

export default function FileList({ refreshTrigger = 0 }: FileListProps) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<number | null>(null);

  useEffect(() => {
    loadFiles();
  }, [refreshTrigger]);

  // Auto-refresh if there are processing files
  useEffect(() => {
    const hasProcessingFiles = files.some((file: any) => file.is_processed === 1);
    
    if (!hasProcessingFiles) return;

    const refreshInterval = setInterval(() => {
      loadFiles();
    }, 3000); // Refresh every 3 seconds

    return () => clearInterval(refreshInterval);
  }, [files]);

  const loadFiles = async () => {
    try {
      const response = await fileAPI.listFiles();
      setFiles(response.data);
    } catch (error) {
      toast.error('Failed to load files');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (fileId: number) => {
    if (!confirm('Are you sure you want to delete this file?')) return;

    setDeleting(fileId);
    try {
      await fileAPI.deleteFile(fileId);
      toast.success('File deleted successfully');
      loadFiles();
    } catch (error) {
      toast.error('Failed to delete file');
    } finally {
      setDeleting(null);
    }
  };

  const getFileIcon = (fileType: string) => {
    if (fileType === 'pdf') return <FileText className="h-5 w-5 text-red-500" />;
    if (fileType === 'url') return <Globe className="h-5 w-5 text-blue-500" />;
    return <FileText className="h-5 w-5 text-gray-500" />;
  };

  const getStatusBadge = (status: number, processingError?: string) => {
    if (status === 2) {
      return (
        <div className="flex items-center space-x-1 text-green-600 bg-green-50 px-3 py-1.5 rounded-full text-xs font-medium">
          <CheckCircle className="h-3.5 w-3.5" />
          <span>Ready</span>
        </div>
      );
    }
    if (status === 1) {
      return (
        <div className="flex items-center space-x-1 text-blue-600 bg-blue-50 px-3 py-1.5 rounded-full text-xs font-medium">
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
          <span>Processing...</span>
        </div>
      );
    }
    if (status === 3) {
      return (
        <div 
          className="flex items-center space-x-1 text-red-600 bg-red-50 px-3 py-1.5 rounded-full text-xs font-medium cursor-help"
          title={processingError || 'Processing failed'}
        >
          <AlertCircle className="h-3.5 w-3.5" />
          <span>Failed</span>
        </div>
      );
    }
    return (
      <div className="flex items-center space-x-1 text-gray-600 bg-gray-50 px-3 py-1.5 rounded-full text-xs font-medium">
        <Clock className="h-3.5 w-3.5" />
        <span>Pending</span>
      </div>
    );
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="flex flex-col items-center justify-center space-y-2">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            <p className="text-sm text-gray-500">Loading files...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Your Files</CardTitle>
          {files.some((file: any) => file.is_processed === 1) && (
            <div className="flex items-center space-x-2 text-sm text-blue-600">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Auto-refreshing...</span>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {files.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>No files uploaded yet</p>
            <p className="text-sm mt-2">Upload a PDF to get started</p>
          </div>
        ) : (
          <div className="space-y-3">
            {files.map((file: any) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-4 flex-1 min-w-0">
                  {getFileIcon(file.file_type)}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{file.original_filename}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                      {file.file_size && (
                        <span>{formatFileSize(file.file_size)}</span>
                      )}
                      {file.page_count && (
                        <span>{file.page_count} pages</span>
                      )}
                      <span>{formatDate(file.uploaded_at)}</span>
                    </div>
                    {file.is_processed === 3 && file.processing_error && (
                      <p className="text-xs text-red-600 mt-1 truncate">
                        Error: {file.processing_error}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {getStatusBadge(file.is_processed, file.processing_error)}
                  
                  <div className="flex space-x-1">
                    {file.is_processed === 2 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {/* View metadata */}}
                        title="View details"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(file.id)}
                      disabled={deleting === file.id || file.is_processed === 1}
                      title={file.is_processed === 1 ? "Cannot delete while processing" : "Delete file"}
                    >
                      {deleting === file.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Trash2 className={`h-4 w-4 ${file.is_processed === 1 ? 'text-gray-400' : 'text-red-500'}`} />
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
