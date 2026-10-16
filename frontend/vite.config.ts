import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import type { ClientRequest } from "node:http";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on("proxyReq", (proxyRequest: ClientRequest) => {
            proxyRequest.setHeader("origin", "http://localhost:5173");
          });
        },
      },
    },
  },
});
