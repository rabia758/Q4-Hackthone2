/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    turbo: {
      enabled: false // Disable Turbopack to ensure Tailwind CSS works properly
    }
  },
}

module.exports = nextConfig