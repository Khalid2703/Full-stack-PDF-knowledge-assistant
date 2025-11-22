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

  const getStatusBadge = (status: number) => {
    if (status === 2) {
      return (
        <div className="flex items-center space-x-1 text-green-600 bg-green-50 px-2 py-1 rounded text-xs">
          <CheckCircle className="h-3 w-3" />
          <span>Ready</span>
        </div>
      );
    }
    if (status === 1) {
      return (
        <div className="flex items-center space-x-1 text-yellow-600 bg-yellow-50 px-2 py-1 rounded text-xs">
          <Clock className="h-3 w-3" />
          <span>Processing</span>
        </div>
      );
    }
    return (
      <div className="flex items-center space-x-1 text-red-600 bg-red-50 px-2 py-1 rounded text-xs">
        <AlertCircle className="h-3 w-3" />
        <span>Failed</span>
      </div>
    );
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="flex items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Your Files</CardTitle>
      </CardHeader>
      <CardContent>
        {files.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>No files uploaded yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {files.map((file: any) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-4 flex-1">
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
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {getStatusBadge(file.is_processed)}
                  
                  <div className="flex space-x-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {/* View metadata */}}
                      title="View details"
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(file.id)}
                      disabled={deleting === file.id}
                      title="Delete file"
                    >
                      {deleting === file.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Trash2 className="h-4 w-4 text-red-500" />
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
