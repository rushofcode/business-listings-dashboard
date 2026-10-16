import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Port 5173 must match CORS_ORIGINS in backend/.env
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, strictPort: true },
});
