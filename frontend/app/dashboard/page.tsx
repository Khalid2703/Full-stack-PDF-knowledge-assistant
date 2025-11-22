'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { fileAPI, chatAPI } from '@/lib/api';
import { 
  FileText, 
  MessageSquare, 
  Upload, 
  Globe, 
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';

export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState({
    totalFiles: 0,
    processedFiles: 0,
    pendingFiles: 0,
    totalChats: 0,
  });
  const [recentFiles, setRecentFiles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [filesRes, sessionsRes] = await Promise.all([
        fileAPI.listFiles(),
        chatAPI.listSessions(),
      ]);

      const files = filesRes.data;
      setRecentFiles(files.slice(0, 5));

      setStats({
        totalFiles: files.length,
        processedFiles: files.filter((f: any) => f.is_processed === 2).length,
        pendingFiles: files.filter((f: any) => f.is_processed === 1).length,
        totalChats: sessionsRes.data.sessions.length,
      });
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getFileIcon = (fileType: string) => {
    if (fileType === 'pdf') return <FileText className="h-5 w-5 text-red-500" />;
    if (fileType === 'url') return <Globe className="h-5 w-5 text-blue-500" />;
    return <FileText className="h-5 w-5 text-gray-500" />;
  };

  const getStatusIcon = (status: number) => {
    if (status === 2) return <CheckCircle className="h-4 w-4 text-green-500" />;
    if (status === 1) return <Clock className="h-4 w-4 text-yellow-500" />;
    return <AlertCircle className="h-4 w-4 text-red-500" />;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.name}!
          </h1>
          <p className="text-gray-600 mt-2">
            Here's what's happening with your knowledge base
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Files</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalFiles}</div>
              <p className="text-xs text-muted-foreground">
                PDFs and URLs uploaded
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Processed</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.processedFiles}</div>
              <p className="text-xs text-muted-foreground">
                Ready for search
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Processing</CardTitle>
              <Clock className="h-4 w-4 text-yellow-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.pendingFiles}</div>
              <p className="text-xs text-muted-foreground">
                Currently processing
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Chat Sessions</CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalChats}</div>
              <p className="text-xs text-muted-foreground">
                Conversations started
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => router.push('/upload')}>
            <CardHeader>
              <Upload className="h-8 w-8 text-blue-500 mb-2" />
              <CardTitle>Upload Files</CardTitle>
              <CardDescription>Upload PDFs or scrape URLs</CardDescription>
            </CardHeader>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => router.push('/chat')}>
            <CardHeader>
              <MessageSquare className="h-8 w-8 text-green-500 mb-2" />
              <CardTitle>Start Chat</CardTitle>
              <CardDescription>Ask questions about your documents</CardDescription>
            </CardHeader>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => router.push('/analytics')}>
            <CardHeader>
              <TrendingUp className="h-8 w-8 text-purple-500 mb-2" />
              <CardTitle>View Analytics</CardTitle>
              <CardDescription>Track your usage and insights</CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* Recent Files */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Files</CardTitle>
            <CardDescription>Your latest uploads and scraped content</CardDescription>
          </CardHeader>
          <CardContent>
            {recentFiles.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>No files yet. Start by uploading a PDF or scraping a URL!</p>
                <Link href="/upload">
                  <Button className="mt-4">Upload Your First File</Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {recentFiles.map((file: any) => (
                  <div
                    key={file.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex items-center space-x-4">
                      {getFileIcon(file.file_type)}
                      <div>
                        <p className="font-medium">{file.original_filename}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(file.uploaded_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(file.is_processed)}
                      <span className="text-sm text-gray-500">
                        {file.is_processed === 2 ? 'Ready' : file.is_processed === 1 ? 'Processing' : 'Failed'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
