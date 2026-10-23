import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  // Enable React strict mode for better development experience
  reactStrictMode: true,

  // Pin the workspace root to frontend/ (avoids picking up stray lockfiles in parent folders)
  turbopack: {
    root: path.resolve(__dirname),
  },

  // Optimize images
  images: {
    formats: ['image/avif', 'image/webp'],
  },

  // Experimental optimizations for faster compilation
  experimental: {
    optimizePackageImports: ['recharts', 'lucide-react', 'framer-motion'],
    // Use the OS certificate store when fetching Google Fonts (needed behind HTTPS-scanning antivirus/proxies)
    turbopackUseSystemTlsCerts: true,
  },
};

export default nextConfig;
