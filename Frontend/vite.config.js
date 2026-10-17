import { fileURLToPath } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'


export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, fileURLToPath(new URL('.', import.meta.url)), '')
  const target = env.VITE_BACKEND_URL || 'http://localhost:8002'

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
    '/eaeu_hub': {
      target: 'http://app:8000',
      changeOrigin: true,
      secure: false,
    },
  },
    },
  }
})
