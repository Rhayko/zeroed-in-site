import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  cacheDir: ".vite-preview",
  base: "/zeroed-in-site/",
  plugins: [react()],
});
