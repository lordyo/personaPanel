/**
 * Tailwind CSS configuration for PersonaPanel
 */
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
    './public/index.html',
  ],
  theme: {
    extend: {
      colors: {
        // Base dark theme colors
        'gray': {
          750: '#303848',
          800: '#1e2533',
          850: '#1a1f2c',
          900: '#141824',
          950: '#0f111a',
        },
        // Blue accent colors
        'blue': {
          300: '#90caf9',
          400: '#6ba8e5',
          500: '#4880d0',
          600: '#2962bc',
          700: '#1e45a0',
        },
        // Purple accent colors
        'purple': {
          300: '#c5a8ff',
          400: '#a985f3',
          500: '#8c68e3',
          600: '#7049cc',
          700: '#5530b5',
        },
        // Additional useful colors
        'green': {
          400: '#66bb6a',
          500: '#48a54e',
        },
        'red': {
          400: '#f06292',
          500: '#e64a6c',
        },
        'yellow': {
          400: '#ffeb3b',
          500: '#ffc107',
        },
      },
      fontFamily: {
        'sans': ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
        'mono': ['Fira Code', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '4px',
        'md': '6px',
        'lg': '8px',
      },
      boxShadow: {
        'card': '0 4px 6px -1px rgba(10, 10, 25, 0.1), 0 2px 4px -1px rgba(10, 10, 25, 0.06)',
      },
    },
  },
  plugins: [],
}; 