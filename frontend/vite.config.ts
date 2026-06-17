import path from "node:path";
import os from "node:os";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // Keep Vite's dep cache outside OneDrive to avoid EPERM/lock errors on Windows.
  cacheDir: path.join(os.tmpdir(), "vite-cache-assetflow"),
  server: {
    port: 5173,
    strictPort: true,
  },
});
