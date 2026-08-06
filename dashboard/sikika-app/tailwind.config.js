/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#0B2545',
          50: '#EEF2F7',
          100: '#D6E0EC',
          200: '#B6C6DA',
          300: '#8FA5C0',
          400: '#5A7398',
          600: '#132F52',
          700: '#0B2545',
          800: '#081B36',
          900: '#050F1E',
        },
        brand: {
          DEFAULT: '#EA580C',
          50: '#FFF4ED',
          100: '#FFE6D5',
          500: '#F2650F',
          600: '#EA580C',
          700: '#C2410C',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
