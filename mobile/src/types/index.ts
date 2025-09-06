export interface Appointment {
  id: string;
  client_name: string;
  phone: string;
  service: string;
  date: string;
  time: string;
  duration: string;
  status: 'pending' | 'confirmed' | 'in-progress' | 'completed' | 'cancelled';
  notes?: string;
}

export interface VoiceStreamResponse {
  audio?: string; // Base64 encoded audio
  action: 'appointment_created' | 'appointment_updated' | 'appointment_cancelled' | 'availability_checked' | 'error';
  data?: any;
  message?: string;
}

export interface AudioConfig {
  sampleRate: number;
  channels: number;
  bitRate: number;
  format: string;
}

export interface User {
  id: string;
  business_name: string;
  phone: string;
  email?: string;
  calendar_enabled: boolean;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
}

export interface VoiceRecordingState {
  isRecording: boolean;
  isPlaying: boolean;
  isConnected: boolean;
  audioLevel: number;
  error?: string;
}