'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

interface UseSSEOptions {
  onMessage?: (data: any) => void;
  onError?: (error: any) => void;
  onComplete?: () => void;
}

export function useSSE() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const startStream = useCallback(
    (url: string, options: UseSSEOptions = {}) => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      setIsStreaming(true);
      setError(null);

      const token = localStorage.getItem('token');
      const urlWithToken = `${url}${url.includes('?') ? '&' : '?'}token=${token}`;

      const eventSource = new EventSource(urlWithToken);
      eventSourceRef.current = eventSource;

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          options.onMessage?.(data);
        } catch (err) {
          console.error('Error parsing SSE message:', err);
        }
      };

      eventSource.onerror = (err) => {
        console.error('SSE Error:', err);
        setError('Streaming connection error');
        options.onError?.(err);
        stopStream();
      };

      eventSource.addEventListener('complete', () => {
        options.onComplete?.();
        stopStream();
      });
    },
    []
  );

  const stopStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  useEffect(() => {
    return () => {
      stopStream();
    };
  }, [stopStream]);

  return { isStreaming, error, startStream, stopStream };
}
