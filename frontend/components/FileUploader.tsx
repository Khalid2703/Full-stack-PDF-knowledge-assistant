'use client';

import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from './ui/button';
import { fileAPI } from '../lib/api';
import { toast } from 'sonner';
import { Upload, FileText, X, CheckCircle, Loader2, AlertCircle } from 'lucide-react';

interface FileUploaderProps {
  onSuccess?: () => void;
}

export default function FileUploader({ onSuccess }: FileUploaderProps) {
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'processing' | 'success' | 'error'>('idle');
  const [uploadedFileId, setUploadedFileId] = useState<number | null>(null);
  const [processingMessage, setProcessingMessage] = useState('Processing document...');

  // Poll for processing status
  useEffect(() => {
    if (uploadStatus !== 'processing' || !uploadedFileId) return;

    const pollInterval = setInterval(async () => {
      try {
        const response = await fileAPI.getFileStatus(uploadedFileId);
        const status = response.data.is_processed;

        if (status === 2) {
          // Completed
          clearInterval(pollInterval);
          setUploadStatus('success');
          setProcessingMessage('Processing complete!');
          toast.success('PDF processed successfully!');
          
          setTimeout(() => {
            setSelectedFile(null);
            setUploadProgress(0);
            setUploadStatus('idle');
            setUploadedFileId(null);
            onSuccess?.();
          }, 2000);
        } else if (status === 3) {
          // Failed
          clearInterval(pollInterval);
          setUploadStatus('error');
          const error = response.data.processing_error || 'Unknown error';
          setProcessingMessage(`Processing failed: ${error}`);
          toast.error('PDF processing failed');
        } else if (status === 1) {
          // Still processing - update message
          setProcessingMessage('Processing document... This may take a minute');
        }
      } catch (error) {
        console.error('Error polling status:', error);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [uploadStatus, uploadedFileId, onSuccess]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      // Validate file type
      if (!file.name.endsWith('.pdf')) {
        toast.error('Please upload a PDF file');
        return;
      }

      // Validate file size (50MB)
      if (file.size > 50 * 1024 * 1024) {
        toast.error('File size must be less than 50MB');
        return;
      }

      setSelectedFile(file);
      setUploadStatus('idle');
      setUploadedFileId(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    multiple: false,
  });

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadStatus('uploading');
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await fileAPI.uploadPDF(formData);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Save file ID and start polling for processing status
      setUploadedFileId(response.data.file_id);
      setUploadStatus('processing');
      setProcessingMessage('Upload complete! Processing document...');
      toast.success('File uploaded! Processing started...');

    } catch (error: any) {
      setUploadStatus('error');
      setProcessingMessage(error.response?.data?.detail || 'Upload failed');
      toast.error(error.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleRemove = () => {
    setSelectedFile(null);
    setUploadProgress(0);
    setUploadStatus('idle');
    setUploadedFileId(null);
  };

  return (
    <div className="space-y-4">
      {/* Dropzone */}
      {!selectedFile && uploadStatus === 'idle' && (
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
            transition-colors
            ${isDragActive 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-300 hover:border-gray-400'
            }
          `}
        >
          <input {...getInputProps()} />
          <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          {isDragActive ? (
            <p className="text-blue-600 font-medium">Drop the PDF here...</p>
          ) : (
            <>
              <p className="text-gray-600 mb-2">
                Drag and drop a PDF file here, or click to select
              </p>
              <p className="text-sm text-gray-500">
                Max file size: 50MB
              </p>
            </>
          )}
        </div>
      )}

      {/* Selected File */}
      {selectedFile && (
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <FileText className="h-8 w-8 text-red-500" />
              <div>
                <p className="font-medium">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            {uploadStatus === 'idle' && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRemove}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>

          {/* Upload Progress */}
          {uploadStatus === 'uploading' && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Uploading...</span>
                <span className="font-medium">{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Processing Status */}
          {uploadStatus === 'processing' && (
            <div className="space-y-3">
              <div className="flex items-center space-x-2 text-blue-600">
                <Loader2 className="h-5 w-5 animate-spin" />
                <span className="font-medium">{processingMessage}</span>
              </div>
              <div className="text-sm text-gray-500">
                Extracting text, generating embeddings, and indexing...
              </div>
            </div>
          )}

          {/* Success Message */}
          {uploadStatus === 'success' && (
            <div className="flex items-center space-x-2 text-green-600">
              <CheckCircle className="h-5 w-5" />
              <span className="font-medium">Processing complete! Ready to chat.</span>
            </div>
          )}

          {/* Error Message */}
          {uploadStatus === 'error' && (
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-red-600">
                <AlertCircle className="h-5 w-5" />
                <span className="font-medium">Processing failed</span>
              </div>
              <p className="text-sm text-gray-600">{processingMessage}</p>
              <Button
                onClick={handleRemove}
                variant="outline"
                size="sm"
                className="mt-2"
              >
                Try Another File
              </Button>
            </div>
          )}

          {/* Upload Button */}
          {uploadStatus === 'idle' && (
            <Button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full"
            >
              {uploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                'Upload PDF'
              )}
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
