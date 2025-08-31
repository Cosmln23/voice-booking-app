# Voice Booking Frontend

Dashboard pentru aplicația de programări cu interfață vocală.

## 🚀 Instalare

```bash
# Instalează dependințele
npm install

# Pornește serverul de dezvoltare
npm run dev

# Build pentru producție
npm run build

# Verificare tipuri TypeScript
npm run type-check

# Lint cod
npm run lint
```

## 🎯 Funcționalități Implementate

- ✅ **Layout complet** - Sidebar, Header, MobileDrawer
- ✅ **KPI Cards** cu Chart.js - metrici în timp real
- ✅ **Timeline Agenda** - programări zilnice interactive
- ✅ **Voice Monitor** - activitate agent vocal live
- ✅ **Status Alerts** - monitorizare servicii
- ✅ **Theme System** - dark/light mode cu localStorage
- ✅ **Responsive design** - mobile-first cu drawer navigation
- ✅ **TypeScript** - type safety complet
- ✅ **Tailwind CSS** - design system consistent

## 📱 Testare

1. **Desktop**: Verifică sidebar, KPI cards, timeline
2. **Mobile**: Testează drawer navigation și responsive layout
3. **Theme Toggle**: Switch între dark/light mode
4. **Interactive Elements**: Hover effects, buttons, navigation

## 🏗️ Structura

```
src/
├── app/                 # Next.js App Router
├── components/
│   ├── dashboard/      # KPI, Timeline, Voice Monitor
│   ├── layout/         # Sidebar, Header, Mobile Drawer  
│   ├── providers/      # Theme Provider
│   └── ui/             # Badge, Button, Theme Toggle
├── hooks/              # useTheme
├── lib/                # Utils
└── styles/             # Globals CSS
```

## 🎨 Design System

- **Colors**: Gray scale + Cyan accents
- **Typography**: Inter font family
- **Components**: Surface cards cu hover effects
- **Responsive**: Mobile-first breakpoints
- **Accessibility**: ARIA labels, keyboard navigation