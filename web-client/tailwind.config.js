/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Neo-Brutalism Design Tokens
      colors: {
        // 主色调
        'brut-white': '#FFFFFF',
        'brut-black': '#000000',
        'brut-yellow': '#FFD700',
        'brut-blue': '#0066FF',
        'brut-red': '#FF0000',
        'brut-green': '#00FF00',
        'brut-pink': '#FF69B4',
        'brut-gray': {
          50: '#F9FAFB',
          100: '#F3F4F6',
          200: '#E5E7EB',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280',
          600: '#4B5563',
          700: '#374151',
          800: '#1F2937',
          900: '#111827',
        },
      },
      // 硬阴影
      boxShadow: {
        'brut-sm': '2px 2px 0px 0px #000000',
        'brut-md': '4px 4px 0px 0px #000000',
        'brut-lg': '6px 6px 0px 0px #000000',
        'brut-xl': '8px 8px 0px 0px #000000',
        'brut-2xl': '12px 12px 0px 0px #000000',
      },
      // 边框
      borderWidth: {
        'brut': '2px',
        'brut-thick': '3px',
      },
      // 字体
      fontFamily: {
        'mono': ['Courier New', 'monospace'],
        'sans': ['Arial', 'Helvetica', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
