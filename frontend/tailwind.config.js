/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Figtree', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      colors: {
        navy: { 950: '#080f1f', 900: '#0c1730', 800: '#13213f', 700: '#1c2f57', 600: '#2a4170' },
        brand: { 50: '#eef4ff', 100: '#dbe7ff', 500: '#3b6df0', 600: '#2a58d8', 700: '#2347b3' },
      },
      boxShadow: {
        card: '0 1px 2px rgba(15,23,42,.05), 0 1px 3px rgba(15,23,42,.04)',
        pop: '0 10px 30px -8px rgba(15,23,42,.25)',
      },
    },
  },
  plugins: [],
};
