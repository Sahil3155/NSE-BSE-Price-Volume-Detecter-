/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B111E',
        surface: '#151F32',
        surfaceHover: '#1E2C44',
        border: '#23324E',
        accent: '#2563EB',
        bullGreen: '#10B981',
        bearRed: '#EF4444',
        warningOrange: '#F59E0B',
      },
    },
  },
  plugins: [],
}
