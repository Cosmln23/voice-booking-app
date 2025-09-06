export const API_CONFIG = {
  BASE_URL: process.env.EXPO_PUBLIC_API_URL || 'https://voice-booking-app-production.up.railway.app',
  WS_URL: process.env.EXPO_PUBLIC_WS_URL || 'wss://voice-booking-app-production.up.railway.app',
  TIMEOUT: 10000,
};

export const AUDIO_CONFIG = {
  SAMPLE_RATE: 24000,
  CHANNELS: 1,
  BIT_RATE: 384000,
  FORMAT: 'wav',
  CHUNK_SIZE: 1024,
  MAX_DURATION: 300000, // 5 minutes
};

export const COLORS = {
  primary: '#3B82F6',
  secondary: '#6B7280',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  background: '#FFFFFF',
  surface: '#F9FAFB',
  text: {
    primary: '#111827',
    secondary: '#6B7280',
    white: '#FFFFFF',
  },
  border: '#E5E7EB',
};

export const ROMANIAN_MESSAGES = {
  WELCOME: 'Bun venit! Spuneți ce programare doriți să faceți.',
  LISTENING: 'Vă ascult...',
  PROCESSING: 'Procesez cererea...',
  ERROR: 'A apărut o eroare. Încercați din nou.',
  NO_CONNECTION: 'Nu există conexiune la internet.',
  PERMISSION_DENIED: 'Pentru a folosi aplicația, acordați permisiunea pentru microfon.',
  RECORDING_STARTED: 'Înregistrarea a început',
  RECORDING_STOPPED: 'Înregistrarea s-a oprit',
};