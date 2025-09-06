import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { VoiceScreen } from './src/screens/VoiceScreen';
import { COLORS } from './src/constants/config';

interface UserData {
  id: string;
  token: string;
  business_name: string;
}

export default function App() {
  const [user, setUser] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      const userData = await AsyncStorage.getItem('user_data');
      if (userData) {
        setUser(JSON.parse(userData));
      } else {
        // For demo purposes, set default user
        const defaultUser: UserData = {
          id: 'demo-user-1',
          token: 'demo-token',
          business_name: 'Salon Demo',
        };
        setUser(defaultUser);
        await AsyncStorage.setItem('user_data', JSON.stringify(defaultUser));
      }
    } catch (error) {
      console.error('Failed to load user data:', error);
      Alert.alert('Eroare', 'Nu s-au putut încărca datele utilizatorului');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Se încarcă...</Text>
        <StatusBar style="auto" />
      </View>
    );
  }

  if (!user) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Eroare la încărcarea aplicației</Text>
        <StatusBar style="auto" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <VoiceScreen
        userId={user.id}
        token={user.token}
        businessName={user.business_name}
      />
      <StatusBar style="dark" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: COLORS.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    fontSize: 18,
    color: COLORS.text.primary,
  },
  errorContainer: {
    flex: 1,
    backgroundColor: COLORS.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
  errorText: {
    fontSize: 18,
    color: COLORS.error,
    textAlign: 'center',
  },
});
