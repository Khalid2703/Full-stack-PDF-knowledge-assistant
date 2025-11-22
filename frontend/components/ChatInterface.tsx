'use client';

import { useState, useEffect, useRef } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { chatAPI, fileAPI } from '../lib/api';
import { useChatStore } from '../lib/store';
import { toast } from 'sonner';
import { Send, Loader2, FileText, Download, Sparkles, AlertCircle } from 'lucide-react';
import { exportChatToPDF, exportToJSON } from '../lib/export';

export default function ChatInterface() {
  const [message, setMessage] = useState('');
  const { messages, addMessage, isLoading, setLoading } = useChatStore();
  const [sessionId] = useState(() => `session-${Date.now()}`);
  const [error, setError] = useState<string | null>(null);
  const [files, setFiles] = useState<any[]>([]);
  const [selectedFileIds, setSelectedFileIds] = useState<number[]>([]);
  const [filesOpen, setFilesOpen] = useState(false);
  const filesDropdownRef = useRef<HTMLDivElement | null>(null);
  const [fileSearch, setFileSearch] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load user files for selection
    const loadFiles = async () => {
      try {
        const res = await fileAPI.listFiles();
        setFiles(res.data || []);
      } catch (err) {
        // ignore silently
      }
    };

    loadFiles();
  }, []);

  // Load persisted selection from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem('selectedFileIds');
      if (stored) {
        const parsed = JSON.parse(stored) as number[];
        setSelectedFileIds(parsed || []);
      }
    } catch (e) {
      // ignore
    }
  }, []);

  // Persist selection
  useEffect(() => {
    try {
      localStorage.setItem('selectedFileIds', JSON.stringify(selectedFileIds));
    } catch (e) {
      // ignore
    }
  }, [selectedFileIds]);

  useEffect(() => {
    // Close dropdown when clicking outside
    function handleClickOutside(event: MouseEvent) {
      if (filesDropdownRef.current && !filesDropdownRef.current.contains(event.target as Node)) {
        setFilesOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [filesDropdownRef]);

  const handleSend = async () => {
    if (!message.trim() || isLoading) return;

    const userMessage = { 
      role: 'user' as const, 
      content: message, 
      timestamp: new Date().toISOString() 
    };
    
    addMessage(userMessage);
    setMessage('');
    setLoading(true);
    setError(null);

    try {
      const payload: any = {
        session_id: sessionId,
        message: message,
        use_rag: true,
        rag_mode: 'accurate',
        stream: false,
        include_citations: true,
        check_safety: true
      };

      if (selectedFileIds && selectedFileIds.length > 0) {
        payload.file_ids = selectedFileIds;
      }

      const response = await chatAPI.sendMessageV2(payload);

      console.log('API Response:', response.data);

      if (response.data && response.data.message) {
        addMessage({
          role: 'assistant',
          content: response.data.message,
          sources: response.data.sources || [],
          timestamp: new Date().toISOString(),
        });
      } else {
        throw new Error('Invalid response format from server');
      }
    } catch (error: any) {
      console.error('Chat Error:', error);
      
      const errorMessage = error.response?.data?.detail || 
                          error.message || 
                          'Failed to send message';
      
      setError(errorMessage);
      toast.error(errorMessage);
      
      addMessage({
        role: 'assistant',
        content: `Sorry, I encountered an error: ${errorMessage}. Please make sure you have uploaded documents and try again.`,
        timestamp: new Date().toISOString(),
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExportJSON = () => {
    exportToJSON(messages, `chat-export-${Date.now()}`);
    toast.success('Chat exported as JSON');
  };

  const handleExportPDF = () => {
    exportChatToPDF(messages, `chat-export-${Date.now()}`);
    toast.success('Chat exported as PDF');
  };

  return (
    <div className="flex flex-col h-full">
      <div className="border-b p-4 flex items-center justify-between bg-white">
        <div className="flex items-center space-x-2">
          <Sparkles className="h-5 w-5 text-blue-500" />
          <h3 className="font-semibold">AI Assistant</h3>
          <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
            Online
          </span>
        </div>
        <div className="flex-1 px-4">
          {/* Selected file chips */}
          <div className="flex flex-wrap gap-2">
            {selectedFileIds.slice(0, 5).map((id) => {
              const f = files.find((x) => x.id === id);
              if (!f) return null;
              return (
                <div key={id} className="inline-flex items-center bg-gray-100 text-xs px-2 py-1 rounded-full border">
                  <span className="mr-2">{f.title || f.filename}</span>
                  <button
                    onClick={() => setSelectedFileIds((s) => s.filter((x) => x !== id))}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ×
                  </button>
                </div>
              );
            })}
            {selectedFileIds.length > 5 && (
              <div className="inline-flex items-center text-xs text-gray-600">+{selectedFileIds.length - 5} more</div>
            )}
          </div>
        </div>
        <div className="flex space-x-2">
            <div className="relative">
              <button
                onClick={() => setFilesOpen(!filesOpen)}
                className="text-sm px-3 py-1 border rounded bg-white"
              >
                {selectedFileIds.length === 0 ? 'All Files' : `${selectedFileIds.length} file(s)`}
              </button>

              {filesOpen && (
                <div ref={filesDropdownRef} className="absolute right-0 mt-2 w-96 bg-white border rounded shadow-lg z-40 p-3">
                  <div className="flex items-center justify-between mb-2">
                    <strong className="text-sm">Select files</strong>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => setSelectedFileIds(files.map((f) => f.id))}
                        className="text-xs px-2 py-1 border rounded"
                      >
                        All
                      </button>
                      <button
                        onClick={() => setSelectedFileIds([])}
                        className="text-xs px-2 py-1 border rounded"
                      >
                        Clear
                      </button>
                    </div>
                  </div>

                  <div className="mb-2">
                    <input
                      value={fileSearch}
                      onChange={(e) => setFileSearch(e.target.value)}
                      placeholder="Search files..."
                      className="w-full text-sm border rounded px-2 py-1"
                    />
                  </div>

                  <div className="max-h-56 overflow-y-auto">
                    {files.length === 0 && (
                      <p className="text-xs text-gray-500">No files found</p>
                    )}
                    {files
                      .filter((f) =>
                        fileSearch.trim() === ''
                          ? true
                          : (f.title || f.filename || '').toLowerCase().includes(fileSearch.toLowerCase())
                      )
                      .map((f) => (
                        <label key={f.id} className="flex items-start justify-between space-x-2 py-1">
                          <div className="flex items-start space-x-2">
                            <input
                              type="checkbox"
                              checked={selectedFileIds.includes(f.id)}
                              onChange={(e) => {
                                if (e.target.checked) setSelectedFileIds((s) => [...s, f.id]);
                                else setSelectedFileIds((s) => s.filter((id) => id !== f.id));
                              }}
                              className="mt-1"
                            />
                            <div className="text-xs">
                              <div className="font-medium">{f.title || f.filename}</div>
                              <div className="text-gray-500">{f.page_count || '?'} pages</div>
                            </div>
                          </div>
                          <div className="text-xs text-gray-500 ml-4">
                            {f.is_processed === 1 && <span className="text-yellow-600">Processing</span>}
                            {f.is_processed === 2 && <span className="text-green-600">Ready</span>}
                            {f.is_processed === 3 && <span className="text-red-600">Failed</span>}
                          </div>
                        </label>
                      ))}
                  </div>
                </div>
              )}
            </div>
            
            {messages.length > 0 && (
              <>
                <Button variant="outline" size="sm" onClick={handleExportJSON}>
                  <Download className="h-4 w-4 mr-2" />
                  JSON
                </Button>
                <Button variant="outline" size="sm" onClick={handleExportPDF}>
                  <Download className="h-4 w-4 mr-2" />
                  PDF
                </Button>
              </>
            )}
          </div>
        
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-3 flex items-center">
          <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
          <p className="text-sm text-red-700">{error}</p>
          <button 
            onClick={() => setError(null)}
            className="ml-auto text-red-500 hover:text-red-700"
          >
            ×
          </button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Sparkles className="h-16 w-16 text-blue-500 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Start a conversation
            </h3>
            <p className="text-gray-500 max-w-md">
              Ask questions about your uploaded documents and get AI-powered answers with sources.
            </p>
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl">
              <button
                onClick={() => setMessage("What are the main topics in my documents?")}
                className="text-left p-4 border rounded-lg hover:bg-white hover:shadow-sm transition-all"
              >
                <p className="text-sm font-medium text-gray-900">Main topics?</p>
                <p className="text-xs text-gray-500 mt-1">Get document overview</p>
              </button>
              <button
                onClick={() => setMessage("Summarize the key findings")}
                className="text-left p-4 border rounded-lg hover:bg-white hover:shadow-sm transition-all"
              >
                <p className="text-sm font-medium text-gray-900">Key findings</p>
                <p className="text-xs text-gray-500 mt-1">Get concise summary</p>
              </button>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[75%] rounded-lg p-4 shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-white text-gray-900 border'
                  }`}
                >
                  <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                  
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-gray-200">
                      <p className="text-xs font-semibold mb-2 flex items-center text-gray-700">
                        <FileText className="h-3 w-3 mr-1" />
                        Sources ({msg.sources.length})
                      </p>
                      <div className="space-y-2">
                        {msg.sources.slice(0, 5).map((source: any, idx: number) => (
                          <div key={idx} className="text-xs bg-gray-50 p-3 rounded border">
                            <p className="font-medium text-gray-900">{source.filename || 'Document'}</p>
                            {source.page_number && (
                              <p className="text-gray-600 mt-1">Page {source.page_number}</p>
                            )}
                            {source.relevance_score && (
                              <div className="mt-2">
                                <div className="w-full bg-gray-200 rounded-full h-1.5">
                                  <div 
                                    className="bg-blue-500 h-1.5 rounded-full" 
                                    style={{ width: `${source.relevance_score * 100}%` }}
                                  />
                                </div>
                                <p className="text-gray-500 text-xs mt-1">
                                  Relevance: {(source.relevance_score * 100).toFixed(0)}%
                                </p>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {msg.timestamp && (
                    <p className={`text-xs mt-2 ${msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                      {new Date(msg.timestamp).toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </p>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white rounded-lg p-4 border shadow-sm">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
                    <span className="text-sm text-gray-600">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <div className="border-t p-4 bg-white">
        <div className="flex space-x-2">
          <Input
            placeholder="Ask a question about your documents..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            disabled={isLoading}
            className="flex-1"
          />
          <Button 
            onClick={handleSend} 
            disabled={isLoading || !message.trim()}
            size="lg"
            className="px-6"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Press Enter to send • Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
