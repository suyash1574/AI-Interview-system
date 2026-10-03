/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: '#ffffff',
        'canvas-subtle': '#f8f9fa',
        'canvas-muted': '#f1f3f5',
        border: '#e5e7eb',
        'border-strong': '#d1d5db',
        ink: '#111827',
        'ink-secondary': '#374151',
        'ink-muted': '#6b7280',
        primary: {
          DEFAULT: '#1a56db',
          hover: '#1648c4',
          active: '#1340b0',
          subtle: '#eff3ff',
          ondark: '#6ea8ff'
        },
        dark: {
          base: '#0f1117',
          surface: '#181c27',
          border: 'rgba(255, 255, 255, 0.08)',
          ink: '#f1f3f5',
          muted: '#9ca3af'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      },
      animation: {
        'pulse-subtle': 'pulseSoft 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        pulseSoft: {
          '0%, 100%': { opacity: '0.7' },
          '50%': { opacity: '1' },
        }
      }
    },
  },
  plugins: [],
}
