/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        wa: {
          teal: '#008069',
          darkTeal: '#075e54',
          lightGreen: '#25d366',
          chatBg: '#efeae2',
          bubbleOut: '#d9fdd3',
          bubbleIn: '#ffffff',
          darkBg: '#0b141a',
          darkHeader: '#202c33',
          darkChatBg: '#0c1317',
          darkBubbleOut: '#005c4b',
          darkBubbleIn: '#202c33',
          muted: '#8696a0',
          border: '#e9edef',
          darkBorder: '#222d34'
        },
        brand: {
          50: '#f0f5ff',
          100: '#e0ecff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a8a'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
