import { defineConfig } from "vite";
import uni from "@dcloudio/vite-plugin-uni";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [uni()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:9000',
        changeOrigin: true,
        // 不需要 rewrite，因为后端路由就是 /api 开头
      }
    }
  },
  build: {
    // 确保打包文件名带有 hash，便于版本更新时强制刷新
    rollupOptions: {
      output: {
        // JS 入口文件名（带 hash）
        entryFileNames: 'assets/[name]-[hash].js',
        // JS chunk 文件名（带 hash）
        chunkFileNames: 'assets/[name]-[hash].js',
        // 静态资源文件名（带 hash）
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    // 生成 source map 便于调试（生产环境建议设为 false）
    sourcemap: false,
    // chunk 大小警告限制（单位：KB）
    chunkSizeWarningLimit: 1000,
    // 清空输出目录
    emptyOutDir: true
  }
});
