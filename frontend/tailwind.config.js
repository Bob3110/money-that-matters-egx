/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // EXACT SINGLE ACCENT COLOR: Baby Blue (#38BDF8 / sky-400)
        accent: {
          DEFAULT: '#38BDF8',
          light: '#7DD3FC',
          dark: '#0284C7',
          subtle: '#F0F9FF'
        },
        // Semantic Bullish / Bearish
        bullish: {
          DEFAULT: '#10B981',
          bg: '#ECFDF5',
          text: '#065F46'
        },
        bearish: {
          DEFAULT: '#F43F5E',
          bg: '#FFF1F2',
          text: '#9F1239'
        }
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Fira Code"', '"Roboto Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif']
      },
      minHeight: {
        'tap': '44px'
      },
      minWidth: {
        'tap': '44px'
      }
    },
  },
  plugins: [],
}
