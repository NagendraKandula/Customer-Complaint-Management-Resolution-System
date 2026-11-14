import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// If VITE_API_BASE_URL is left empty in .env, requests go to /api/* on the
// Vite dev server and are proxied to the backend below (no CORS setup needed).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
});
