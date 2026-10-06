import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    const configuredBackendUrl = process.env.NEXT_PUBLIC_API_URL?.trim();

    if (!configuredBackendUrl) {
      throw new Error(
        "Set NEXT_PUBLIC_API_URL to the FastAPI backend URL.",
      );
    }

    const backendUrl = configuredBackendUrl.replace(/\/+$/, "");

    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
