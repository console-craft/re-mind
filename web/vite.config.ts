import react from "@vitejs/plugin-react"
import { defineConfig } from "vite-plus"

// https://vite.dev/config/
export default defineConfig({
  clearScreen: false,
  fmt: { ignorePatterns: [".opencode/**"], printWidth: 120, semi: false },
  lint: {
    ignorePatterns: [".opencode/**", "dist"],
    options: { typeAware: true, typeCheck: true },
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": new URL("./src", import.meta.url).pathname,
    },
  },
})
