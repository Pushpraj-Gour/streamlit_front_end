import type { NextConfig } from "next";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8081";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // The browser talks to /backend/*; Next forwards it to the interview API (no CORS setup needed).
  async rewrites() {
    return [{ source: "/backend/:path*", destination: `${BACKEND_URL}/:path*` }];
  },
};

export default nextConfig;
