/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: '#07090e',
        'canvas-subtle': '#0d111c',
        'canvas-muted': '#151b2b',
        border: 'rgba(255, 255, 255, 0.08)',
        'border-strong': 'rgba(255, 255, 255, 0.16)',
        ink: '#f8fafc',
        'ink-secondary': '#94a3b8',
        'ink-muted': '#64748b',
        primary: {
          DEFAULT: '#6366f1',
          hover: '#4f46e5',
          active: '#4338ca',
          subtle: 'rgba(99, 102, 241, 0.12)',
          ondark: '#a5b4fc'
        },
        accent: {
          cyan: '#06b6d4',
          violet: '#8b5cf6',
          emerald: '#10b981',
          amber: '#f59e0b',
          rose: '#f43f5e'
        },
        dark: {
          base: '#07090e',
          surface: '#0f1422',
          card: '#131929',
          border: 'rgba(255, 255, 255, 0.08)',
          ink: '#f8fafc',
          muted: '#94a3b8'
        }
      },
      boxShadow: {
        'glow-primary': '0 0 30px -5px rgba(99, 102, 241, 0.35)',
        'glow-cyan': '0 0 30px -5px rgba(6, 182, 212, 0.35)',
        'glow-emerald': '0 0 30px -5px rgba(16, 185, 129, 0.35)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      },
      animation: {
        'pulse-subtle': 'pulseSoft 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 12s linear infinite',
        'float': 'float 6s ease-in-out infinite',
        'ripple': 'ripple 3s cubic-bezier(0, 0.2, 0.8, 1) infinite',
        'shimmer': 'shimmer 2.5s linear infinite'
      },
      keyframes: {
        pulseSoft: {
          '0%, 100%': { opacity: '0.7' },
          '50%': { opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        ripple: {
          '0%': { transform: 'scale(0.8)', opacity: '0.8' },
          '100%': { transform: 'scale(2.2)', opacity: '0' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        }
      }
    },
  },
  plugins: [],
}
