import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: path.resolve(__dirname, '../src/autoteam/web/dist'),
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        // 用 127.0.0.1 而非 localhost：Windows 上 localhost 优先解析为 IPv6 (::1)，
        // 而后端默认 host=0.0.0.0 只监听 IPv4，会得到 ECONNREFUSED ::1。
        target: 'http://127.0.0.1:8787',
        changeOrigin: true,
      },
    },
  },
})
