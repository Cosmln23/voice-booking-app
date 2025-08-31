import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      colors: {
        // Claude AI inspired theme
        background: '#1a1a1a',
        card: '#2d2d2d',
        'card-hover': '#404040',
        primary: '#ffffff',
        secondary: '#a0a0a0',
        accent: '#ff6b35',
        'accent-hover': '#ff8659',
        border: '#404040',
        'border-hover': '#606060',
        
        // Keep some grays for compatibility
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        },
        cyan: {
          50: '#ecfeff',
          100: '#cffafe',
          200: '#a5f3fc',
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#06b6d4',
          600: '#0891b2',
          700: '#0e7490',
          800: '#155e75',
          900: '#164e63',
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      spacing: {
        '4.5': '1.125rem',
        '18': '4.5rem',
      },
    },
  },
  plugins: [],
}

export default config