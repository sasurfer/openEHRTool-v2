import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
	plugins: [vue()],
	server: {
		port: 8180
	},
	base: '/',
	resolve: {
		alias: {
			'@': path.resolve(__dirname, 'src'), // <--- critical
		},
	},
})
