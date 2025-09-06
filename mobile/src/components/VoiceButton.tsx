import React from 'react';
import { View, TouchableOpacity, Text, StyleSheet, Animated } from 'react-native';
import { COLORS, ROMANIAN_MESSAGES } from '../constants/config';

interface VoiceButtonProps {
  isRecording: boolean;
  isConnected: boolean;
  audioLevel: number;
  onPress: () => void;
  disabled?: boolean;
}

export const VoiceButton: React.FC<VoiceButtonProps> = ({
  isRecording,
  isConnected,
  audioLevel,
  onPress,
  disabled = false,
}) => {
  const pulseAnimation = React.useRef(new Animated.Value(1)).current;
  const waveAnimation = React.useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    if (isRecording) {
      // Pulse animation
      const pulse = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnimation, {
            toValue: 1.2,
            duration: 1000,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnimation, {
            toValue: 1,
            duration: 1000,
            useNativeDriver: true,
          }),
        ])
      );

      // Audio wave animation
      const wave = Animated.loop(
        Animated.timing(waveAnimation, {
          toValue: audioLevel * 2,
          duration: 100,
          useNativeDriver: true,
        })
      );

      pulse.start();
      wave.start();

      return () => {
        pulse.stop();
        wave.stop();
      };
    } else {
      pulseAnimation.setValue(1);
      waveAnimation.setValue(0);
    }
  }, [isRecording, audioLevel]);

  const getButtonColor = () => {
    if (!isConnected) return COLORS.secondary;
    if (disabled) return COLORS.secondary;
    if (isRecording) return COLORS.error;
    return COLORS.primary;
  };

  const getButtonText = () => {
    if (!isConnected) return 'Reconectare...';
    if (isRecording) return 'Apăsați pentru a opri';
    return 'Apăsați și vorbiți';
  };

  return (
    <View style={styles.container}>
      {/* Audio level indicator */}
      {isRecording && (
        <View style={styles.audioLevelContainer}>
          {[...Array(5)].map((_, index) => (
            <Animated.View
              key={index}
              style={[
                styles.audioBar,
                {
                  height: Math.max(4, audioLevel * 30 * (index + 1)),
                  backgroundColor: audioLevel > index * 0.2 ? COLORS.primary : COLORS.border,
                },
              ]}
            />
          ))}
        </View>
      )}

      {/* Main voice button */}
      <Animated.View
        style={[
          styles.buttonContainer,
          {
            transform: [{ scale: pulseAnimation }],
          },
        ]}
      >
        <TouchableOpacity
          style={[
            styles.button,
            {
              backgroundColor: getButtonColor(),
              opacity: disabled ? 0.6 : 1,
            },
          ]}
          onPress={onPress}
          disabled={disabled}
          activeOpacity={0.8}
        >
          <View style={styles.buttonInner}>
            <View style={[styles.microphoneIcon, { backgroundColor: COLORS.text.white }]} />
            {isRecording && (
              <Animated.View
                style={[
                  styles.recordingIndicator,
                  {
                    transform: [{ scale: waveAnimation }],
                  },
                ]}
              />
            )}
          </View>
        </TouchableOpacity>
      </Animated.View>

      {/* Status text */}
      <Text style={styles.statusText}>{getButtonText()}</Text>
      
      {/* Connection indicator */}
      <View style={styles.connectionContainer}>
        <View
          style={[
            styles.connectionDot,
            {
              backgroundColor: isConnected ? COLORS.success : COLORS.error,
            },
          ]}
        />
        <Text style={styles.connectionText}>
          {isConnected ? 'Conectat' : 'Deconectat'}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    padding: 20,
  },
  audioLevelContainer: {
    flexDirection: 'row',
    alignItems: 'end',
    height: 40,
    marginBottom: 20,
    gap: 4,
  },
  audioBar: {
    width: 4,
    borderRadius: 2,
    minHeight: 4,
  },
  buttonContainer: {
    marginBottom: 16,
  },
  button: {
    width: 120,
    height: 120,
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  buttonInner: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  microphoneIcon: {
    width: 32,
    height: 48,
    borderRadius: 16,
    marginBottom: 8,
  },
  recordingIndicator: {
    position: 'absolute',
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
  },
  statusText: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text.primary,
    textAlign: 'center',
    marginBottom: 8,
  },
  connectionContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  connectionDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  connectionText: {
    fontSize: 12,
    color: COLORS.text.secondary,
  },
});