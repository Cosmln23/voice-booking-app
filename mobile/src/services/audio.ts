import { Audio } from 'expo-av';
import { AUDIO_CONFIG } from '../constants/config';
import { AudioConfig } from '../types';

export class AudioService {
  private recording: Audio.Recording | null = null;
  private sound: Audio.Sound | null = null;
  private audioConfig: AudioConfig;
  private onAudioChunk?: (chunk: ArrayBuffer) => void;
  private recordingTimer?: NodeJS.Timeout;
  private isInitialized = false;

  constructor() {
    this.audioConfig = {
      sampleRate: AUDIO_CONFIG.SAMPLE_RATE,
      channels: AUDIO_CONFIG.CHANNELS,
      bitRate: AUDIO_CONFIG.BIT_RATE,
      format: AUDIO_CONFIG.FORMAT,
    };
  }

  async initialize() {
    if (this.isInitialized) return;

    try {
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false,
        staysActiveInBackground: false,
      });
      this.isInitialized = true;
    } catch (error) {
      console.error('Failed to initialize audio:', error);
      throw error;
    }
  }

  async startRecording(onAudioChunk?: (chunk: ArrayBuffer) => void): Promise<void> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      if (this.recording) {
        await this.stopRecording();
      }

      this.onAudioChunk = onAudioChunk;
      this.recording = new Audio.Recording();

      const recordingOptions = {
        android: {
          extension: `.${this.audioConfig.format}`,
          outputFormat: Audio.RECORDING_OPTION_ANDROID_OUTPUT_FORMAT_PCM_16BIT,
          audioEncoder: Audio.RECORDING_OPTION_ANDROID_AUDIO_ENCODER_PCM_16BIT,
          sampleRate: this.audioConfig.sampleRate,
          numberOfChannels: this.audioConfig.channels,
          bitRate: this.audioConfig.bitRate,
        },
        ios: {
          extension: `.${this.audioConfig.format}`,
          audioQuality: Audio.RECORDING_OPTION_IOS_AUDIO_QUALITY_HIGH,
          sampleRate: this.audioConfig.sampleRate,
          numberOfChannels: this.audioConfig.channels,
          bitRate: this.audioConfig.bitRate,
          linearPCMBitDepth: 16,
          linearPCMIsBigEndian: false,
          linearPCMIsFloat: false,
        },
      };

      await this.recording.prepareToRecordAsync(recordingOptions);
      await this.recording.startAsync();

      // Start streaming audio chunks if handler provided
      if (onAudioChunk) {
        this.startAudioStreaming();
      }

      // Auto-stop after max duration
      this.recordingTimer = setTimeout(() => {
        this.stopRecording();
      }, AUDIO_CONFIG.MAX_DURATION);

    } catch (error) {
      console.error('Failed to start recording:', error);
      throw error;
    }
  }

  private startAudioStreaming() {
    // In a real implementation, we would need to stream audio chunks
    // This is a simplified version - in production, you'd need native modules
    // or expo-av extensions to get real-time audio data
    
    const streamInterval = setInterval(async () => {
      if (!this.recording || !this.onAudioChunk) {
        clearInterval(streamInterval);
        return;
      }

      try {
        // This is a placeholder - actual implementation would need
        // to capture audio chunks in real-time
        const status = await this.recording.getStatusAsync();
        if (status.isRecording) {
          // In real implementation, get audio chunk here
          // const chunk = await this.getAudioChunk();
          // this.onAudioChunk(chunk);
        }
      } catch (error) {
        console.error('Error streaming audio:', error);
        clearInterval(streamInterval);
      }
    }, 100); // Send chunks every 100ms
  }

  async stopRecording(): Promise<string | null> {
    try {
      if (!this.recording) return null;

      if (this.recordingTimer) {
        clearTimeout(this.recordingTimer);
        this.recordingTimer = undefined;
      }

      await this.recording.stopAndUnloadAsync();
      const uri = this.recording.getURI();
      this.recording = null;
      this.onAudioChunk = undefined;

      return uri;
    } catch (error) {
      console.error('Failed to stop recording:', error);
      throw error;
    }
  }

  async playAudio(base64Audio: string): Promise<void> {
    try {
      if (this.sound) {
        await this.sound.unloadAsync();
      }

      // Convert base64 to audio URI
      const audioUri = `data:audio/wav;base64,${base64Audio}`;
      
      this.sound = new Audio.Sound();
      await this.sound.loadAsync({ uri: audioUri });
      await this.sound.playAsync();
    } catch (error) {
      console.error('Failed to play audio:', error);
      throw error;
    }
  }

  async getAudioLevel(): Promise<number> {
    if (this.recording) {
      try {
        const status = await this.recording.getStatusAsync();
        return status.isRecording && status.metering ? status.metering : 0;
      } catch (error) {
        console.error('Failed to get audio level:', error);
        return 0;
      }
    }
    return 0;
  }

  isRecording(): boolean {
    return this.recording !== null;
  }

  async cleanup(): Promise<void> {
    try {
      if (this.recording) {
        await this.stopRecording();
      }
      if (this.sound) {
        await this.sound.unloadAsync();
        this.sound = null;
      }
      if (this.recordingTimer) {
        clearTimeout(this.recordingTimer);
      }
    } catch (error) {
      console.error('Failed to cleanup audio service:', error);
    }
  }
}

export const audioService = new AudioService();