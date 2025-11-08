/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Убираем standalone для Netlify, так как это вызывает проблемы с зависимостями
  // output: 'standalone',
  env: {
    API_URL: process.env.API_URL || 'https://dmed.gubkin.uz',
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://dmed.gubkin.uz',
  },
  // Игнорируем системные файлы Windows при отслеживании изменений
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.watchOptions = {
        ...config.watchOptions,
        ignored: [
          '**/node_modules/**',
          '**/.git/**',
          '**/.next/**',
          '**/pagefile.sys',
          '**/hiberfil.sys',
          '**/swapfile.sys',
        ],
      }
    }
    return config
  },
}

module.exports = nextConfig

