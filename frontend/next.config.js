/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  async rewrites() {
    return [];
  },
  async headers() {
    return [];
  },
};

module.exports = nextConfig; 