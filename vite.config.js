import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // Build optimizations
  build: {
    // Enable rollup optimizations
    rollupOptions: {
      output: {
        // Manual chunking for better caching
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@headlessui/react', '@heroicons/react', 'framer-motion'],
          query: ['@tanstack/react-query', 'axios'],
          utils: ['zustand', 'react-hot-toast', 'react-markdown']
        }
      }
    },
    // Target modern browsers for smaller bundles
    target: 'es2020',
    // Minimize CSS
    cssMinify: true,
    // Reduce chunk size warnings threshold
    chunkSizeWarningLimit: 1000,
    // Source maps for production debugging (can be disabled for smaller builds)
    sourcemap: false
  },

  // Development server optimizations
  server: {
    // Enable pre-bundling for faster dev startup
    force: false,
    hmr: {
      overlay: false
    }
  },

  // Dependency pre-bundling optimizations
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      '@tanstack/react-query',
      'axios',
      'zustand',
      'framer-motion'
    ]
  },

  // Resolve configuration
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@api': resolve(__dirname, 'src/api'),
      '@gurus': resolve(__dirname, 'src/gurus')
    }
  },

  // CSS optimizations
  css: {
    devSourcemap: false
  }
})