import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { fileURLToPath } from 'node:url';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  esbuild: {
    // Ensure proper JSX handling
    jsxDev: false,
  },
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  resolve: {
    alias: {
      '@': path.resolve(path.dirname(fileURLToPath(import.meta.url)), './src'),
    },
  },
  server: {
    host: '127.0.0.1',
    port: 3001,
    hmr: {
      port: process.env.VITE_HMR_PORT ? parseInt(process.env.VITE_HMR_PORT) : 3004,
      host: '127.0.0.1',
      clientPort: process.env.VITE_HMR_PORT ? parseInt(process.env.VITE_HMR_PORT) : 3004,
      overlay: false
    },
    strictPort: false,
    open: true,
    cors: true,
    watch: {
      usePolling: true,
      interval: 100
    }
  },
  preview: {
    host: 'localhost',
    port: 3001,
  },
  define: {
    global: 'globalThis',
  },
  build: {
    commonjsOptions: {
      include: [/node_modules/],
    },
    rollupOptions: {
      onwarn(warning, warn) {
        // Suppress specific warnings
        if (warning.code === 'MODULE_LEVEL_DIRECTIVE') return;
        warn(warning);
      },
    },
  },
});
