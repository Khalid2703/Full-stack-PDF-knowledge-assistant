/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // REMOVED: output: 'standalone' - This breaks CSS in Vercel!
  // Vercel handles optimization automatically
  images: {
    domains: ['localhost', 'regnova-backend-bs3v.onrender.com'],
  },
  // Environment variables (fallback)
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
