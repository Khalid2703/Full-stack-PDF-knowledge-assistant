'use client';

import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import Navbar from '@/components/Navbar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import FileUploader from '@/components/FileUploader';
import URLInput from '@/components/URLInput';
import FileList from '@/components/FileList';
import { FileText, Globe } from 'lucide-react';

export default function UploadPage() {
  useAuth();
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Upload Content</h1>
          <p className="text-gray-600 mt-2">
            Upload PDFs or scrape URLs to add to your knowledge base
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Upload Section */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Add New Content</CardTitle>
                <CardDescription>
                  Upload PDF files or provide URLs to scrape
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="pdf" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="pdf" className="flex items-center space-x-2">
                      <FileText className="h-4 w-4" />
                      <span>PDF Upload</span>
                    </TabsTrigger>
                    <TabsTrigger value="url" className="flex items-center space-x-2">
                      <Globe className="h-4 w-4" />
                      <span>URL Scrape</span>
                    </TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="pdf" className="mt-6">
                    <FileUploader onSuccess={handleUploadSuccess} />
                  </TabsContent>
                  
                  <TabsContent value="url" className="mt-6">
                    <URLInput onSuccess={handleUploadSuccess} />
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>

          {/* Tips Section */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>Upload Tips</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-semibold text-sm mb-2">📄 PDF Files</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Max size: 50MB</li>
                    <li>• Supports scanned PDFs (OCR)</li>
                    <li>• Extracts table of contents</li>
                    <li>• Identifies key entities</li>
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-semibold text-sm mb-2">🌐 Web URLs</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Extracts main content</li>
                    <li>• Removes ads and navigation</li>
                    <li>• Converts to clean text</li>
                    <li>• Works with most websites</li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-sm mb-2">⚡ Processing</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Automatic text extraction</li>
                    <li>• Vector embeddings generated</li>
                    <li>• Ready for AI search</li>
                    <li>• Usually takes 1-2 minutes</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* File List */}
        <div className="mt-8">
          <FileList refreshTrigger={refreshTrigger} />
        </div>
      </div>
    </div>
  );
}
