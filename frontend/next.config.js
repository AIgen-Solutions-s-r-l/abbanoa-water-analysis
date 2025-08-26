/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output for Docker deployment
  output: 'standalone',
  
  // Server external packages (moved from experimental)
  serverExternalPackages: [],
  
  // Environment variables that should be available on the client side
  env: {
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8000',
  },
  
  // API routes configuration
  // Commented out because we're using a custom API route handler
  // async rewrites() {
  //   return [
  //     {
  //       source: '/api/proxy/:path*',
  //       destination: `${process.env.BACKEND_URL || 'http://localhost:8000'}/:path*`,
  //     },
  //   ];
  // },
  
  // Security headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },
  
  // Optimize images
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
      },
    ],
  },
  
  // Build optimization (swcMinify is now default and deprecated)
  poweredByHeader: false,
  
  // Disable ESLint during production builds
  eslint: {
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig; 