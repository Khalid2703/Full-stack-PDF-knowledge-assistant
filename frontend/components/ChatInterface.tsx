'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { chatAPI, fileAPI } from '../lib/api';
import { useChatStore } from '../lib/store';
import { toast } from 'sonner';
import { Send, Loader2, FileText, Download, Sparkles, AlertCircle, Plus, RefreshCw } from 'lucide-react';
import { exportChatToPDF, exportToJSON } from '../lib/export';
import ReactMarkdown from 'react-markdown';

export default function ChatInterface() {
  const [message, setMessage] = useState('');
  const { messages, addMessage, isLoading, setLoading, clearMessages } = useChatStore();
  const [sessionId, setSessionId] = useState(() => `session-${Date.now()}`);
  const [error, setError] = useState<string | null>(null);
  const [files, setFiles] = useState<any[]>([]);
  const [selectedFileIds, setSelectedFileIds] = useState<number[]>([]);
  const [filesOpen, setFilesOpen] = useState(false);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const filesDropdownRef = useRef<HTMLDivElement | null>(null);
  const [fileSearch, setFileSearch] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // ✅ PROPER FIX: Load files and validate selections
  const loadFiles = useCallback(async () => {
    setLoadingFiles(true);
    try {
      const res = await fileAPI.listFiles();
      const filesList = res.data || [];
      setFiles(filesList);
      
      // Validate selected files - use setSelectedFileIds callback to get current value
      setSelectedFileIds(currentSelectedIds => {
        if (filesList.length === 0) {
          // No files exist, clear everything
          localStorage.removeItem('selectedFileIds');
          return [];
        }
        
        // Get valid file IDs from the fetched list
        const validFileIds = filesList.map((f: any) => f.id);
        
        // Filter out any selected IDs that no longer exist
        const validSelectedIds = currentSelectedIds.filter(id => validFileIds.includes(id));
        
        // Update localStorage
        if (validSelectedIds.length === 0) {
          localStorage.removeItem('selectedFileIds');
        } else {
          localStorage.setItem('selectedFileIds', JSON.stringify(validSelectedIds));
        }
        
        // Only update state if something changed
        if (validSelectedIds.length !== currentSelectedIds.length) {
          console.log(`Cleaned up selections: ${currentSelectedIds.length} → ${validSelectedIds.length}`);
          if (validSelectedIds.length < currentSelectedIds.length) {
            toast.info(`Removed ${currentSelectedIds.length - validSelectedIds.length} deleted file(s) from selection`);
          }
        }
        
        return validSelectedIds;
      });
    } catch (err) {
      console.error('Failed to load files:', err);
      toast.error('Failed to load files');
    } finally {
      setLoadingFiles(false);
    }
  }, []); // No dependencies needed since we use callback form of setState

  // Load files on mount
  useEffect(() => {
    loadFiles();
  }, [loadFiles]);

  // Load files when window regains focus
  useEffect(() => {
    const handleFocus = () => {
      loadFiles();
    };
    
    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [loadFiles]);

  // Reload files every 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      loadFiles();
    }, 10000);
    
    return () => clearInterval(interval);
  }, [loadFiles]);

  // Load selected file IDs from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem('selectedFileIds');
      if (stored) {
        const parsed = JSON.parse(stored) as number[];
        setSelectedFileIds(parsed || []);
      }
    } catch (e) {
      console.error('Failed to load selected files:', e);
      localStorage.removeItem('selectedFileIds');
    }
  }, []);

  // Save selected file IDs to localStorage whenever they change
  useEffect(() => {
    try {
      if (selectedFileIds.length === 0) {
        localStorage.removeItem('selectedFileIds');
      } else {
        localStorage.setItem('selectedFileIds', JSON.stringify(selectedFileIds));
      }
    } catch (e) {
      console.error('Failed to save selected files:', e);
    }
  }, [selectedFileIds]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (filesDropdownRef.current && !filesDropdownRef.current.contains(event.target as Node)) {
        setFilesOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [filesDropdownRef]);

  const handleNewChat = () => {
    if (messages.length > 0) {
      const confirmNew = window.confirm('Start a new chat? Current conversation will be cleared.');
      if (!confirmNew) return;
    }
    clearMessages();
    setSessionId(`session-${Date.now()}`);
    setError(null);
    toast.success('New chat started');
  };

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
      };

      if (selectedFileIds.length > 0) {
        payload.file_ids = selectedFileIds;
      }

      const response = await chatAPI.sendMessageV2(payload);

      if (response.data) {
        const assistantMessage = {
          role: 'assistant' as const,
          content: response.data.answer || response.data.response || 'No response',
          sources: response.data.sources || [],
          timestamp: new Date().toISOString(),
        };
        addMessage(assistantMessage);
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to send message';
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const toggleFileSelection = (fileId: number) => {
    setSelectedFileIds((prev) =>
      prev.includes(fileId) ? prev.filter((id) => id !== fileId) : [...prev, fileId]
    );
  };

  const filteredFiles = files.filter((f) =>
    f.original_filename?.toLowerCase().includes(fileSearch.toLowerCase())
  );

  const handleExportPDF = async () => {
    try {
      exportChatToPDF(messages, `chat-${sessionId}`);
      toast.success('Chat exported to PDF');
    } catch (err) {
      toast.error('Failed to export PDF');
    }
  };

  const handleExportJSON = () => {
    try {
      exportToJSON(messages, `chat-${sessionId}.json`);
      toast.success('Chat exported to JSON');
    } catch (err) {
      toast.error('Failed to export JSON');
    }
  };

  return (
    <div className="flex flex-col h-full max-h-screen bg-white">
      <div className="border-b p-3 bg-white flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-blue-500" />
          <h2 className="font-semibold text-gray-900">AI Chat Assistant</h2>
          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
            Powered by OpenAI
          </span>
        </div>
        
        <div className="flex gap-2">
          {messages.length > 0 && (
            <>
              <Button variant="outline" size="sm" onClick={handleExportJSON} title="Export as JSON">
                <Download className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={handleExportPDF} title="Export as PDF">
                <FileText className="h-4 w-4" />
              </Button>
            </>
          )}
          <Button variant="outline" size="sm" onClick={handleNewChat} title="Start new chat" className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            New Chat
          </Button>
        </div>
      </div>

      <div className="border-b p-3 bg-gray-50">
        <div className="relative" ref={filesDropdownRef}>
          <button onClick={() => setFilesOpen(!filesOpen)} className="w-full text-left px-3 py-2 border rounded-lg bg-white hover:bg-gray-50 flex items-center justify-between">
            <span className="text-sm text-gray-700">
              {selectedFileIds.length > 0 ? `${selectedFileIds.length} file(s) selected` : 'Select files for context'}
            </span>
            <div className="flex items-center gap-2">
              {loadingFiles && <Loader2 className="h-3 w-3 animate-spin text-gray-400" />}
              <FileText className="h-4 w-4 text-gray-400" />
            </div>
          </button>

          {filesOpen && (
            <div className="absolute top-full mt-1 w-full bg-white border rounded-lg shadow-lg z-10 max-h-64 overflow-y-auto">
              <div className="p-2 border-b flex items-center gap-2">
                <Input placeholder="Search files..." value={fileSearch} onChange={(e) => setFileSearch(e.target.value)} className="text-sm flex-1" />
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => loadFiles()} 
                  disabled={loadingFiles}
                  title="Refresh files list"
                >
                  <RefreshCw className={`h-4 w-4 ${loadingFiles ? 'animate-spin' : ''}`} />
                </Button>
              </div>
              <div className="p-2 space-y-1">
                {filteredFiles.length === 0 ? (
                  <p className="text-sm text-gray-500 text-center py-2">No files uploaded</p>
                ) : (
                  filteredFiles.map((file) => (
                    <label key={file.id} className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer">
                      <input type="checkbox" checked={selectedFileIds.includes(file.id)} onChange={() => toggleFileSelection(file.id)} className="rounded" />
                      <span className="text-sm text-gray-700 truncate flex-1">{file.original_filename}</span>
                      <span className="text-xs text-gray-500">{file.is_processed === 2 ? '✓' : '...'}</span>
                    </label>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-3 flex items-center">
          <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
          <p className="text-sm text-red-700">{error}</p>
          <button onClick={() => setError(null)} className="ml-auto text-red-500 hover:text-red-700">×</button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-3 space-y-2 bg-gray-50">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Sparkles className="h-16 w-16 text-blue-500 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Start a conversation</h3>
            <p className="text-gray-500 max-w-md mb-4">Ask questions about your uploaded documents and get AI-powered answers with sources.</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl">
              <button onClick={() => setMessage("What are the main topics in my documents?")} className="text-left p-3 border rounded-lg hover:bg-white hover:shadow-sm transition-all">
                <p className="text-sm font-medium text-gray-900">Main topics?</p>
                <p className="text-xs text-gray-500 mt-1">Get document overview</p>
              </button>
              <button onClick={() => setMessage("Summarize the key findings")} className="text-left p-3 border rounded-lg hover:bg-white hover:shadow-sm transition-all">
                <p className="text-sm font-medium text-gray-900">Key findings</p>
                <p className="text-xs text-gray-500 mt-1">Get concise summary</p>
              </button>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-lg p-3 shadow-sm ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-white text-gray-900 border'}`}>
                  {msg.role === 'assistant' ? (
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown
                        components={{
                          h2: ({node, ...props}) => <h2 className="text-lg font-bold mt-3 mb-2" {...props} />,
                          h3: ({node, ...props}) => <h3 className="text-base font-semibold mt-2 mb-1" {...props} />,
                          p: ({node, ...props}) => <p className="mb-2 leading-relaxed" {...props} />,
                          ul: ({node, ...props}) => <ul className="list-disc ml-4 mb-2 space-y-1" {...props} />,
                          ol: ({node, ...props}) => <ol className="list-decimal ml-4 mb-2 space-y-1" {...props} />,
                          li: ({node, ...props}) => <li className="leading-relaxed" {...props} />,
                          strong: ({node, ...props}) => <strong className="font-bold text-gray-900" {...props} />,
                          code: ({node, inline, ...props}: any) => 
                            inline ? <code className="bg-gray-100 px-1 py-0.5 rounded text-sm" {...props} /> : <code className="block bg-gray-100 p-2 rounded text-sm overflow-x-auto" {...props} />,
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="leading-relaxed">{msg.content}</p>
                  )}
                  
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-xs font-semibold mb-2 flex items-center text-gray-700">
                        <FileText className="h-3 w-3 mr-1" />Sources ({msg.sources.length})
                      </p>
                      <div className="space-y-2">
                        {msg.sources.slice(0, 3).map((source: any, idx: number) => (
                          <div key={idx} className="text-xs bg-gray-50 p-2 rounded border">
                            <p className="font-medium text-gray-900">{source.filename || 'Document'}</p>
                            {source.page_number && <p className="text-gray-600 mt-1">Page {source.page_number}</p>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {msg.timestamp && (
                    <p className={`text-xs mt-2 ${msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                      {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white rounded-lg p-3 border shadow-sm">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                    <span className="text-sm text-gray-600">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <div className="border-t p-3 bg-white">
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
          <Button onClick={handleSend} disabled={isLoading || !message.trim()} size="lg" className="px-6">
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </Button>
        </div>
        <p className="text-xs text-gray-500 mt-2">Press Enter to send • Shift+Enter for new line</p>
      </div>
    </div>
  );
}
