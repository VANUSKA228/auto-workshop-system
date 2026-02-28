/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#2E75B6',
        'primary-dark': '#1F3864',
        'primary-light': '#EEF4FB',
        success: '#1B7A3B',
        danger: '#C0392B',
        warning: '#E67E22',
        neutral: '#6B7280',
      },
      fontFamily: {
        sans: ['Inter', 'Roboto', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '8px',
      },
    },
  },
  plugins: [],
}
