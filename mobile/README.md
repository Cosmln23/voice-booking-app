# 📱 Voice Booking Mobile App

## 🎯 Overview

Aplicația mobilă nativă React Native pentru sistemul de rezervări vocale în limba română. Oferă o experiență superioară față de sistemul telefonic prin:

- **Audio HD**: Calitate audio 24kHz vs 8kHz PSTN
- **Interface vizuală**: Voice + Calendar + Notifications
- **Fiabilitate**: 99.9% uptime vs 85-90% telefonic
- **Costuri reduse**: Fix vs per-minute

## 🏗️ Arhitectura Tehnică

```
📱 React Native App (iOS + Android)
    ↓ WebSocket Real-time
🚀 Railway Backend API
    ↓ Voice Processing  
🤖 OpenAI Realtime API (Romanian)
    ↓ Business Logic
📅 Google Calendar Integration
```

## 🔧 Stack Tehnologic

### Frontend Mobile
- **React Native 0.79.6** - Cross-platform development
- **Expo 53** - Development platform
- **TypeScript** - Type safety
- **expo-av** - Audio recording and playback
- **WebSocket** - Real-time communication

### Backend Integration
- **FastAPI WebSocket** - Real-time voice streaming
- **OpenAI Realtime API** - Romanian voice processing
- **Google Calendar API** - Appointment sync
- **Railway** - Cloud hosting

## 📦 Instalare și Setup

### Prerequisite
```bash
npm install -g expo-cli @expo/cli
```

### Instalare Dependențe
```bash
cd mobile
npm install
```

### Configurare Environment
```bash
cp .env.example .env
```

Editează `.env`:
```env
EXPO_PUBLIC_API_URL=https://voice-booking-app-production.up.railway.app
EXPO_PUBLIC_WS_URL=wss://voice-booking-app-production.up.railway.app
```

### Rulare Dezvoltare
```bash
# Start Expo development server
npm start

# Run on Android
npm run android

# Run on iOS  
npm run ios

# Run on web (for testing)
npm run web
```

## 📱 Structura Aplicației

```
src/
├── components/           # UI Components
│   └── VoiceButton.tsx   # Main voice interaction button
├── screens/             # App screens
│   └── VoiceScreen.tsx  # Main voice interface
├── services/            # External services
│   ├── websocket.ts     # WebSocket communication
│   └── audio.ts         # Audio recording/playback
├── hooks/               # Custom React hooks
│   └── useVoice.ts      # Voice interaction logic
├── types/               # TypeScript definitions
│   └── index.ts         # App interfaces
├── constants/           # App constants
│   └── config.ts        # Configuration values
└── utils/               # Utility functions
```

## 🎤 Funcționalități Voice

### Înregistrare Audio
- **Format**: WAV, 24kHz, 16-bit, Mono
- **Streaming**: Real-time chunks via WebSocket
- **Durată maximă**: 5 minute
- **Indicatori vizuali**: Audio level, waveform

### Procesare Vocală
- **Limbă**: Română nativă
- **Engine**: OpenAI Realtime API
- **Comenzi suportate**:
  - "Vreau să fac o programare pentru tunsoare"
  - "Am nevoie de o programare mâine la 10"
  - "Modific programarea de joi la ora 14"

### Răspunsuri Audio
- **Playback**: Base64 audio din backend
- **Feedback vizual**: Status programării
- **Notificări**: Push notifications pentru confirmare

## 📡 WebSocket Communication

### Connection Endpoint
```
wss://voice-booking-app-production.up.railway.app/ws/voice/{user_id}?token={auth_token}
```

### Message Types

**Outgoing (Mobile → Backend)**:
```typescript
// Start recording
{ type: "start_recording" }

// Audio chunk (binary)
ArrayBuffer // Raw audio data

// Stop recording  
{ type: "stop_recording" }

// Ping
{ type: "ping" }
```

**Incoming (Backend → Mobile)**:
```typescript
// Voice response with appointment
{
  action: "appointment_created",
  audio: "base64_audio_response",
  message: "Programarea a fost creată!",
  data: {
    id: "apt_123",
    service: "Tunsoare", 
    date: "2024-09-07",
    time: "10:00"
  }
}

// Connection ready
{
  type: "mobile_voice_ready",
  capabilities: ["audio_streaming", "real_time_voice"]
}
```

## 📋 User Experience Flow

### 1. Prima utilizare
```
📱 Deschide app
🎤 Acordă permisiuni microfon
🔔 Activează notificări
🏢 Selectează salon (auto-detect)
👋 Tutorial vocal introductiv
```

### 2. Crearea unei programări
```
📱 Apasă butonul voice (120px, albastru)
🎤 "Aș vrea să fac o programare pentru tunsoare mâine la 10"
⚡ Streaming real-time la backend (100ms chunks)
🤖 Procesare OpenAI în română
📅 Verificare disponibilitate calendar
✅ Confirmare vizuală + audio
🔔 Push notification
📧 Opțional: Email confirmation
```

### 3. Gestionarea programărilor
```
📅 Vedere calendar integrată
🎤 "Vreau să modific programarea de mâine"
📝 Detalii programare cu opțiuni edit
🔄 Sincronizare automată cu Google Calendar
🔔 Notificări pentru modificări
```

## 🔒 Securitate și Autentificare

### Authentication
- **JWT Tokens**: Pentru API access
- **User ID**: Identificare unică utilizator
- **Business Isolation**: Separare date per salon
- **Token Refresh**: Auto-refresh pentru sesiuni lungi

### Permissions
- **Microphone**: Obligatoriu pentru voice
- **Notifications**: Pentru confirmări și reminder-e
- **Storage**: Pentru cache local appointments

### Privacy
- **Audio local**: Procesare pe device când posibil
- **Data encryption**: TLS pentru toate comunicațiile
- **No persistent audio**: Audio-ul nu se stochează

## 📊 Performanță și Optimizări

### Audio Performance
- **Latency**: <500ms end-to-end
- **Battery**: <5% drain per 10min conversation
- **Network**: Adaptive bitrate pentru conexiuni slabe
- **Offline**: Cache pentru appointment viewing

### UI Performance
- **Launch time**: <2 secunde
- **Smooth animations**: 60fps pentru interacțiuni
- **Memory**: <100MB RAM usage
- **Storage**: <50MB app size

### Network Optimizations
- **Compression**: Audio compression pentru mobile data
- **Reconnection**: Auto-reconnect cu exponential backoff
- **Caching**: Appointment data local caching
- **Background**: Audio processing în background

## 🚀 Deployment și Distribution

### Build Process
```bash
# Production build pentru Android
expo build:android --type=app-bundle

# Production build pentru iOS
expo build:ios --type=archive

# Web build (PWA fallback)
expo build:web
```

### App Store Deployment
- **iOS**: Apple App Store via TestFlight
- **Android**: Google Play Store via Play Console
- **PWA**: Progressive Web App pentru backup

### Store Optimization
- **Keywords**: "programari salon", "rezervari", "voice booking"
- **Screenshots**: Voice interface + calendar views
- **Description**: Română cu focus pe voice booking
- **Reviews**: Target >4.5/5 rating

## 📈 Analytics și Monitoring

### Business Metrics
- **User Adoption**: Download to active conversion >60%
- **Engagement**: 2+ appointments per user/month
- **Retention**: 70% users active after 30 days
- **Success Rate**: >90% successful voice bookings

### Technical Metrics
- **Voice Recognition**: >90% accuracy în română
- **Response Time**: <500ms average
- **Uptime**: 99.9% availability
- **Crash Rate**: <1% sessions

### Monitoring Tools
- **Crash Reporting**: Sentry for error tracking
- **Analytics**: Mixpanel for user behavior
- **Performance**: Custom metrics for voice quality
- **A/B Testing**: Optimize voice interaction flows

## 🛠️ Development Workflow

### Local Development
```bash
# Start backend local
cd ../backend && python -m uvicorn app.main:app --reload

# Start mobile app
npm start

# Test voice functionality
# 1. Connect via Expo Go
# 2. Test WebSocket connection
# 3. Test audio recording
# 4. Verify backend integration
```

### Testing Strategy
- **Unit Tests**: Jest pentru logic components
- **Integration**: Test WebSocket communication
- **E2E**: Detox pentru complete user flows
- **Voice Testing**: Manual testing cu diverse accente române

### Code Quality
- **TypeScript**: Strict mode pentru type safety
- **ESLint**: Code style enforcement
- **Prettier**: Auto-formatting
- **Husky**: Pre-commit hooks pentru quality gates

## 🔄 Migration din Phone System

### Phase 1: Parallel Operation
- Backend suportă atât Twilio cât și Mobile WebSocket
- Testare limitată cu saloane selecte
- Feedback collection și iterație rapidă

### Phase 2: Gradual Transition  
- QR codes în saloane pentru download app
- Training pentru salon staff
- Incentive pentru early adopters

### Phase 3: Complete Migration
- Dezactivare treptată Twilio endpoints
- Focus complet pe mobile experience
- Analytics și optimizare continuă

## 📞 Support și Feedback

### User Support
- **In-app Help**: Tutorial vocal și FAQ
- **Email Support**: support@voice-booking.app
- **Phone Support**: Pentru saloanele partenere
- **Documentation**: Ghiduri video pentru utilizare

### Developer Support
- **Technical Docs**: Detailed API documentation
- **Slack Channel**: #voice-booking-mobile
- **Issue Tracking**: GitHub Issues pentru bug reports
- **Feature Requests**: Roadmap public pentru features

---

## 🎉 Ready to Build the Future of Salon Bookings! 

Aplicația mobilă transformă un sistem simplu de rezervări telefonice într-o soluție digitală comprehensivă pe care clienții și saloanele o vor adora! 📱✨

### Quick Start:
```bash
cd mobile
npm install
npm start
# Scan QR code cu Expo Go
# Test voice booking functionality
```