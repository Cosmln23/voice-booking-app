import { useState, useCallback, useRef, useEffect } from 'react';
import { audioService } from '../services/audio';
import { wsService } from '../services/websocket';
import { VoiceRecordingState, VoiceStreamResponse } from '../types';
import { ROMANIAN_MESSAGES } from '../constants/config';

interface UseVoiceProps {
  userId: string;
  token: string;
  onResponse?: (response: VoiceStreamResponse) => void;
  onError?: (error: string) => void;
}

export const useVoice = ({ userId, token, onResponse, onError }: UseVoiceProps) => {
  const [state, setState] = useState<VoiceRecordingState>({
    isRecording: false,
    isPlaying: false,
    isConnected: false,
    audioLevel: 0,
  });

  const audioLevelInterval = useRef<NodeJS.Timeout>();
  const isInitialized = useRef(false);

  // Initialize services
  useEffect(() => {
    if (isInitialized.current) return;
    
    const initialize = async () => {
      try {
        await audioService.initialize();
        
        // Connect WebSocket
        await wsService.connect(userId, token);
        
        // Set up WebSocket handlers
        wsService.onConnection({
          onOpen: () => {
            setState(prev => ({ ...prev, isConnected: true, error: undefined }));
          },
          onClose: () => {
            setState(prev => ({ ...prev, isConnected: false }));
          },
          onError: (error) => {
            const errorMsg = ROMANIAN_MESSAGES.ERROR;
            setState(prev => ({ ...prev, error: errorMsg }));
            onError?.(errorMsg);
          },
        });

        // Handle voice responses
        wsService.onMessage('all', (data: VoiceStreamResponse) => {
          if (data.audio) {
            playResponseAudio(data.audio);
          }
          onResponse?.(data);
        });

        isInitialized.current = true;
      } catch (error) {
        console.error('Failed to initialize voice services:', error);
        const errorMsg = error instanceof Error ? error.message : ROMANIAN_MESSAGES.ERROR;
        setState(prev => ({ ...prev, error: errorMsg }));
        onError?.(errorMsg);
      }
    };

    initialize();

    // Cleanup on unmount
    return () => {
      cleanup();
    };
  }, [userId, token]);

  // Start/stop recording
  const toggleRecording = useCallback(async () => {
    if (!state.isConnected) {
      onError?.(ROMANIAN_MESSAGES.NO_CONNECTION);
      return;
    }

    try {
      if (state.isRecording) {
        await stopRecording();
      } else {
        await startRecording();
      }
    } catch (error) {
      console.error('Recording error:', error);
      const errorMsg = error instanceof Error ? error.message : ROMANIAN_MESSAGES.ERROR;
      setState(prev => ({ ...prev, error: errorMsg }));
      onError?.(errorMsg);
    }
  }, [state.isRecording, state.isConnected]);

  const startRecording = useCallback(async () => {
    setState(prev => ({ ...prev, isRecording: true, error: undefined }));
    
    // Start audio level monitoring
    audioLevelInterval.current = setInterval(async () => {
      const level = await audioService.getAudioLevel();
      setState(prev => ({ ...prev, audioLevel: level }));
    }, 100);

    await audioService.startRecording((audioChunk) => {
      // Stream audio chunks to backend
      wsService.sendAudioChunk(audioChunk);
    });
  }, []);

  const stopRecording = useCallback(async () => {
    setState(prev => ({ ...prev, isRecording: false, audioLevel: 0 }));
    
    if (audioLevelInterval.current) {
      clearInterval(audioLevelInterval.current);
    }

    await audioService.stopRecording();
  }, []);

  const playResponseAudio = useCallback(async (base64Audio: string) => {
    try {
      setState(prev => ({ ...prev, isPlaying: true }));
      await audioService.playAudio(base64Audio);
      setState(prev => ({ ...prev, isPlaying: false }));
    } catch (error) {
      console.error('Failed to play response audio:', error);
      setState(prev => ({ ...prev, isPlaying: false }));
    }
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (state.isConnected) {
      wsService.sendMessage(message);
    }
  }, [state.isConnected]);

  const cleanup = useCallback(async () => {
    if (audioLevelInterval.current) {
      clearInterval(audioLevelInterval.current);
    }
    await audioService.cleanup();
    wsService.disconnect();
    isInitialized.current = false;
  }, []);

  return {
    ...state,
    toggleRecording,
    sendMessage,
    cleanup,
  };
};