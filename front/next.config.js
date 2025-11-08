/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  webpack: (config) => {
    config.resolve.alias.canvas = false
    config.resolve.alias.encoding = false
    return config
  },
  // Rewrites только для разработки, в продакшне используем переменную окружения
  async rewrites() {
    // Используем rewrites только если не указан NEXT_PUBLIC_API_URL
    const apiUrl = process.env.NEXT_PUBLIC_API_URL
    if (!apiUrl || apiUrl.includes('localhost')) {
      return [
        {
          source: '/api/:path*',
          destination: 'http://localhost:5000/:path*',
        },
      ]
    }
    return []
  },
}

module.exports = nextConfig

