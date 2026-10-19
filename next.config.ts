import type { NextConfig } from "next";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8081";
// The API mounts its routes under an optional prefix (its `api_prefix` setting), e.g. "/interview".
const API_PREFIX = process.env.BACKEND_API_PREFIX ?? "";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  experimental: {
    // Transcription and feedback generation call LLMs and can take well over the 30s default.
    proxyTimeout: 180_000,
  },
  // The browser talks to /backend/*; Next forwards it to the interview API (no CORS setup needed).
  async rewrites() {
    return [{ source: "/backend/:path*", destination: `${BACKEND_URL}${API_PREFIX}/:path*` }];
  },
};

export default nextConfig;
