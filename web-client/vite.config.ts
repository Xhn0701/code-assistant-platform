import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    // 修复 sockjs-client 的 global 未定义问题
    global: 'globalThis',
  },
})
