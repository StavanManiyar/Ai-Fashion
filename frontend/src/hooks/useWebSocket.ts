import { useState, useEffect, useRef } from 'react';

export interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export interface WebSocketOptions {
  onOpen?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
  onError?: (event: Event) => void;
  onMessage: (data: WebSocketMessage) => void;
}

export const useWebSocket = (url: string, options: WebSocketOptions) => {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = (event) => {
      setIsConnected(true);
      options.onOpen?.(event);
    };

    ws.onclose = (event) => {
      setIsConnected(false);
      options.onClose?.(event);
    };

    ws.onerror = (event) => {
      options.onError?.(event);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        options.onMessage(data);
      } catch (error) {
        console.error('WebSocket Message Parsing Error:', error);
      }
    };

    return () => {
      ws.close();
    };
  }, [url]);

  const sendMessage = (message: WebSocketMessage) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  return { isConnected, sendMessage };
};

