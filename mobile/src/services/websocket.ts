import { API_CONFIG } from '../constants/config';
import { VoiceStreamResponse } from '../types';

export class WebSocketService {
  private ws: WebSocket | null = null;
  private userId: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private messageHandlers: Map<string, (data: any) => void> = new Map();
  private connectionHandlers: {
    onOpen?: () => void;
    onClose?: () => void;
    onError?: (error: Event) => void;
  } = {};

  connect(userId: string, token: string): Promise<void> {
    this.userId = userId;
    
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `${API_CONFIG.WS_URL}/ws/voice/${userId}?token=${token}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          this.connectionHandlers.onOpen?.();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data: VoiceStreamResponse = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          this.connectionHandlers.onClose?.();
          this.handleReconnect(token);
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.connectionHandlers.onError?.(error);
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  private handleMessage(data: VoiceStreamResponse) {
    const handler = this.messageHandlers.get(data.action);
    if (handler) {
      handler(data);
    }

    // Handle global message types
    this.messageHandlers.forEach((handler, key) => {
      if (key === 'all') {
        handler(data);
      }
    });
  }

  private async handleReconnect(token: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.userId) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect(this.userId!, token).catch(console.error);
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  sendAudioChunk(audioData: ArrayBuffer) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(audioData);
    } else {
      console.warn('WebSocket not connected, cannot send audio chunk');
    }
  }

  sendMessage(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }

  onMessage(action: string, handler: (data: any) => void) {
    this.messageHandlers.set(action, handler);
  }

  onConnection(handlers: {
    onOpen?: () => void;
    onClose?: () => void;
    onError?: (error: Event) => void;
  }) {
    this.connectionHandlers = handlers;
  }

  removeMessageHandler(action: string) {
    this.messageHandlers.delete(action);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.messageHandlers.clear();
    this.userId = null;
    this.reconnectAttempts = 0;
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

export const wsService = new WebSocketService();