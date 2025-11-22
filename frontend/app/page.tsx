'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '../components/ui/button';
import { ArrowRight, FileText, Globe, MessageSquare, Sparkles } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      router.push('/dashboard');
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-20">
        <div className="text-center space-y-8">
          <div className="inline-block">
            <span className="bg-blue-100 text-blue-800 text-sm font-semibold px-4 py-2 rounded-full">
              Powered by Google Gemini AI
            </span>
          </div>
          
          <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Regnova
          </h1>
          
          <p className="text-2xl text-gray-600 max-w-2xl mx-auto">
            Your Universal PDF + Web Knowledge Assistant
          </p>
          
          <p className="text-lg text-gray-500 max-w-xl mx-auto">
            Upload documents, scrape websites, and get AI-powered answers with source citations
          </p>

          <div className="flex gap-4 justify-center pt-4">
            <Button
              size="lg"
              onClick={() => router.push('/auth/register')}
              className="text-lg px-8"
            >
              Get Started <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              onClick={() => router.push('/auth/login')}
              className="text-lg px-8"
            >
              Sign In
            </Button>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-4 gap-6 mt-20">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <FileText className="h-12 w-12 text-blue-500 mb-4" />
            <h3 className="font-semibold text-lg mb-2">PDF Processing</h3>
            <p className="text-gray-600 text-sm">
              Upload PDFs with OCR support for scanned documents
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <Globe className="h-12 w-12 text-green-500 mb-4" />
            <h3 className="font-semibold text-lg mb-2">Web Scraping</h3>
            <p className="text-gray-600 text-sm">
              Extract content from any URL for analysis
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <MessageSquare className="h-12 w-12 text-purple-500 mb-4" />
            <h3 className="font-semibold text-lg mb-2">AI Chat</h3>
            <p className="text-gray-600 text-sm">
              Ask questions with real-time streaming responses
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <Sparkles className="h-12 w-12 text-orange-500 mb-4" />
            <h3 className="font-semibold text-lg mb-2">RAG Powered</h3>
            <p className="text-gray-600 text-sm">
              Source-grounded answers with dual RAG modes
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
