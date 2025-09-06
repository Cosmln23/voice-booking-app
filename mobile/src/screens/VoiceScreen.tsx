import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  Alert,
} from 'react-native';
import { VoiceButton } from '../components/VoiceButton';
import { useVoice } from '../hooks/useVoice';
import { COLORS, ROMANIAN_MESSAGES } from '../constants/config';
import { VoiceStreamResponse, Appointment } from '../types';

interface VoiceScreenProps {
  userId: string;
  token: string;
  businessName: string;
}

export const VoiceScreen: React.FC<VoiceScreenProps> = ({
  userId,
  token,
  businessName,
}) => {
  const [messages, setMessages] = useState<string[]>([ROMANIAN_MESSAGES.WELCOME]);
  const [lastAppointment, setLastAppointment] = useState<Appointment | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleVoiceResponse = (response: VoiceStreamResponse) => {
    console.log('Voice response:', response);
    
    setIsProcessing(false);

    switch (response.action) {
      case 'appointment_created':
        if (response.data) {
          setLastAppointment(response.data);
          setMessages(prev => [...prev, 'Programare creată cu succes!']);
          Alert.alert(
            'Programare Confirmată',
            `Programarea dumneavoastră pentru ${response.data.service} în data de ${response.data.date} la ora ${response.data.time} a fost confirmată.`,
            [{ text: 'OK' }]
          );
        }
        break;
      
      case 'availability_checked':
        if (response.message) {
          setMessages(prev => [...prev, response.message]);
        }
        break;
      
      case 'error':
        setMessages(prev => [...prev, response.message || 'A apărut o eroare']);
        Alert.alert('Eroare', response.message || ROMANIAN_MESSAGES.ERROR);
        break;
      
      default:
        if (response.message) {
          setMessages(prev => [...prev, response.message]);
        }
    }
  };

  const handleError = (error: string) => {
    console.error('Voice error:', error);
    setIsProcessing(false);
    setMessages(prev => [...prev, error]);
  };

  const {
    isRecording,
    isPlaying,
    isConnected,
    audioLevel,
    toggleRecording,
  } = useVoice({
    userId,
    token,
    onResponse: handleVoiceResponse,
    onError: handleError,
  });

  const handleVoiceButtonPress = () => {
    if (!isRecording) {
      setMessages(prev => [...prev, ROMANIAN_MESSAGES.LISTENING]);
      setIsProcessing(true);
    }
    toggleRecording();
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Programări Vocale</Text>
        <Text style={styles.businessName}>{businessName}</Text>
      </View>

      {/* Messages Area */}
      <ScrollView
        style={styles.messagesContainer}
        contentContainerStyle={styles.messagesContent}
      >
        {messages.map((message, index) => (
          <View key={index} style={styles.messageItem}>
            <Text style={styles.messageText}>{message}</Text>
          </View>
        ))}
        
        {isProcessing && (
          <View style={[styles.messageItem, styles.processingMessage]}>
            <Text style={styles.processingText}>{ROMANIAN_MESSAGES.PROCESSING}</Text>
          </View>
        )}
      </ScrollView>

      {/* Last Appointment */}
      {lastAppointment && (
        <View style={styles.appointmentCard}>
          <Text style={styles.appointmentTitle}>Ultima programare</Text>
          <Text style={styles.appointmentDetails}>
            {lastAppointment.service} • {lastAppointment.date} • {lastAppointment.time}
          </Text>
          <Text style={styles.appointmentClient}>
            Client: {lastAppointment.client_name}
          </Text>
        </View>
      )}

      {/* Voice Button */}
      <View style={styles.voiceButtonContainer}>
        <VoiceButton
          isRecording={isRecording}
          isConnected={isConnected}
          audioLevel={audioLevel}
          onPress={handleVoiceButtonPress}
          disabled={isPlaying || isProcessing}
        />
      </View>

      {/* Instructions */}
      <Text style={styles.instructions}>
        Apăsați butonul și spuneți ce programare doriți să faceți. 
        De exemplu: "Vreau să fac o programare pentru tunsoare mâine la 10"
      </Text>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  header: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
    backgroundColor: COLORS.surface,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.text.primary,
    textAlign: 'center',
  },
  businessName: {
    fontSize: 16,
    color: COLORS.text.secondary,
    textAlign: 'center',
    marginTop: 4,
  },
  messagesContainer: {
    flex: 1,
    padding: 20,
  },
  messagesContent: {
    gap: 12,
  },
  messageItem: {
    backgroundColor: COLORS.surface,
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.primary,
  },
  messageText: {
    fontSize: 16,
    color: COLORS.text.primary,
    lineHeight: 22,
  },
  processingMessage: {
    borderLeftColor: COLORS.warning,
    backgroundColor: '#FEF3C7',
  },
  processingText: {
    fontSize: 16,
    color: COLORS.warning,
    fontStyle: 'italic',
  },
  appointmentCard: {
    margin: 20,
    padding: 16,
    backgroundColor: COLORS.success,
    borderRadius: 12,
  },
  appointmentTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.text.white,
    marginBottom: 8,
  },
  appointmentDetails: {
    fontSize: 14,
    color: COLORS.text.white,
    marginBottom: 4,
  },
  appointmentClient: {
    fontSize: 14,
    color: COLORS.text.white,
    opacity: 0.9,
  },
  voiceButtonContainer: {
    paddingVertical: 20,
  },
  instructions: {
    fontSize: 14,
    color: COLORS.text.secondary,
    textAlign: 'center',
    paddingHorizontal: 30,
    paddingBottom: 20,
    lineHeight: 20,
  },
});