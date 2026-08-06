import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // Dev: forward relative /api calls to the FastAPI backend (no CORS needed).
    // In production the same relative paths are served from one origin.
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
