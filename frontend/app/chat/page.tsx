'use client';

import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import Navbar from '@/components/Navbar';
import ChatInterface from '@/components/ChatInterface';
import { Card } from '@/components/ui/card';
import { Sparkles } from 'lucide-react';

export default function ChatPage() {
  useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
            <Sparkles className="h-8 w-8 text-blue-500" />
            <span>AI Chat</span>
          </h1>
          <p className="text-gray-600 mt-2">
            Ask questions about your uploaded documents and get AI-powered answers
          </p>
        </div>

        <Card className="h-[calc(100vh-250px)]">
          <ChatInterface />
        </Card>
      </div>
    </div>
  );
}
