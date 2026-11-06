import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import { existsSync, readdirSync, rmSync } from 'node:fs'
import { basename, join } from 'node:path'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [uni(), {
    name: 'exclude-static-readmes',
    writeBundle: {
      order: 'post',
      sequential: true,
      handler({ dir }) {
        const staticDir = join(dir, 'static')
        if (!existsSync(staticDir)) return

        // uni-app 整体复制 static，发布包只需要运行资源。
        for (const file of readdirSync(staticDir, { recursive: true })) {
          if (basename(file) === 'README.md') rmSync(join(staticDir, file))
        }
      },
    },
  }],
  build: { minify: process.env.NODE_ENV === 'production' ? 'esbuild' : false },
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) }
  }
})
