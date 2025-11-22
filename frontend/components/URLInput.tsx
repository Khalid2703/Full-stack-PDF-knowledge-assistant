'use client';

import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { scrapeAPI } from '../lib/api';
import { toast } from 'sonner';
import { Globe, Loader2, CheckCircle } from 'lucide-react';

interface URLInputProps {
  onSuccess?: () => void;
}

export default function URLInput({ onSuccess }: URLInputProps) {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success'>('idle');

  const isValidURL = (string: string) => {
    try {
      new URL(string);
      return true;
    } catch {
      return false;
    }
  };

  const handleScrape = async () => {
    if (!url.trim()) {
      toast.error('Please enter a URL');
      return;
    }

    if (!isValidURL(url)) {
      toast.error('Please enter a valid URL');
      return;
    }

    setLoading(true);
    try {
      await scrapeAPI.scrapeURL({
        url: url,
        extract_metadata: true,
      });

      setStatus('success');
      toast.success('URL scraped successfully!');
      
      setTimeout(() => {
        setUrl('');
        setStatus('idle');
        onSuccess?.();
      }, 2000);

    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to scrape URL');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !loading) {
      handleScrape();
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col space-y-4">
        <div>
          <label className="text-sm font-medium mb-2 block">
            Enter URL to Scrape
          </label>
          <div className="flex space-x-2">
            <div className="relative flex-1">
              <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="url"
                placeholder="https://example.com/article"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyPress={handleKeyPress}
                className="pl-10"
                disabled={loading}
              />
            </div>
            <Button
              onClick={handleScrape}
              disabled={loading || !url.trim()}
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Scraping...
                </>
              ) : (
                'Scrape URL'
              )}
            </Button>
          </div>
        </div>

        {status === 'success' && (
          <div className="flex items-center space-x-2 text-green-600 bg-green-50 p-3 rounded-lg">
            <CheckCircle className="h-5 w-5" />
            <span className="font-medium">URL scraped successfully!</span>
          </div>
        )}
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-sm text-blue-900 mb-2">How it works</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Extracts main content from the webpage</li>
          <li>• Removes ads, navigation, and clutter</li>
          <li>• Converts to clean, searchable text</li>
          <li>• Generates embeddings for AI search</li>
        </ul>
      </div>

      <div className="space-y-2">
        <h4 className="font-semibold text-sm">Example URLs:</h4>
        <div className="flex flex-wrap gap-2">
          {[
            'https://en.wikipedia.org/wiki/Artificial_intelligence',
            'https://blog.example.com/article',
            'https://docs.example.com/guide'
          ].map((exampleUrl) => (
            <button
              key={exampleUrl}
              onClick={() => setUrl(exampleUrl)}
              className="text-xs text-blue-600 hover:text-blue-800 underline"
              disabled={loading}
            >
              {exampleUrl}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
