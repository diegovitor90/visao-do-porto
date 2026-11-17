import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    server: {
      host: '127.0.0.1',
      strictPort: true,
      proxy: {
        '/api/v1/vision': { target: env.VISION_API_TARGET || 'http://127.0.0.1:8000', changeOrigin: true },
      },
    },
  }
})
